import json
import os
from django.conf import settings
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView
from plan_visual_django.forms import PlanForm, VisualFormForAdd, VisualFormForEdit, VisualActivityFormForEdit, \
    ReUploadPlanForm
from plan_visual_django.models import Plan, PlanVisual, PlanField, PlanActivity, SwimlaneForVisual, VisualActivity, \
    PlotableStyle
from django.contrib import messages
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.services.general.user_services import get_current_user
from plan_visual_django.services.plan_file_utilities.plan_updater import update_plan_data
from plan_visual_django.services.plan_to_visual.plan_to_visual import VisualManager
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings, SwimlaneSettings
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration


# Create your views here.

@transaction.atomic  # Ensure that if there is an error either on uploading the plan or parsing the plan no records saved
def add_plan(request):
    if request.method == "POST":
        plan_form = PlanForm(data=request.POST, files=request.FILES)
        if plan_form.is_valid():
            current_user = get_current_user(request, default_if_logged_out=True)

            # Save fields from form but don't commit so can modify other fields before committing.
            plan = plan_form.save(commit=False)

            # Check that user hasn't already added a file with this name. Count should be zero
            count = Plan.objects.filter(user=current_user, original_file_name=plan.file.name).count()
            if count > 0:
                messages.error(request, f"Already uploaded a file called {plan.file.name}.  Record not added")
            else:
                # Uploaded file will be given a unique name - so need to store the name of the file the user chose.
                plan.original_file_name = plan.file.name

                # Add user to record (currently hard-coded)
                plan.user = current_user

                # Now can save the record
                plan.save()

                # Have saved the record, now parse the plan and store activities.
                # Only store fields which are part of the plan for the given file type.

                mapping_type = plan.file_type.plan_field_mapping_type

                plan_file = plan.file.path

                file_reader = ExcelXLSFileReader()
                raw_data = file_reader.read(plan_file)
                parsed_data = file_reader.parse(raw_data, plan_field_mapping=mapping_type)

                for activity in parsed_data:
                    # Note that the duration field isn't stored, but used to work out whether the activity is a
                    # milestone.
                    if activity['duration'] == 0:
                        milestone_flag = True
                    else:
                        milestone_flag = False

                    record = PlanActivity(
                        plan=plan,
                        unique_sticky_activity_id=activity['unique_sticky_activity_id'],
                        activity_name=activity['activity_name'],
                        milestone_flag=milestone_flag,
                        start_date=activity['start_date'],
                        end_date=activity['end_date'],
                        level=activity['level'] if 'level' in activity else 1,
                    )
                    record.save()

                messages.success(request, "New plan saved successfully")
        else:
            messages.error(request, "Failed validation")

        return HttpResponseRedirect(reverse('manage_plans'))
    elif request.method == "GET":
        form = PlanForm()
        return render(request=request, template_name="plan_visual_django/pv_add_plan.html", context={'form': form})
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")\


@transaction.atomic  # Ensure that if there is an error either on uploading the plan or parsing the plan no records saved
def re_upload_plan(request, pk):
    """
    Re uploads an existing plan to reflect changes made to the plan.  This is useful if the user has made changes to
    the plan in Excel and wants to see the changes reflected in the visual.

    The processing required is:
    - Read in each line of the plan and check if the unique_sticky_activity_id exists in the database.
    - If it does then update the record with the new values.
    - If it doesn't then add a new record.
    - If the unique_sticky_activity_id exists in the database but not in the plan then delete the record.

    :param pk:
    :param request:
    :return:
    """
    plan_record = Plan.objects.get(id=pk)
    if request.method == "POST":
        plan_form = ReUploadPlanForm(data=request.POST, files=request.FILES, instance=plan_record)
        if plan_form.is_valid():
            current_user = get_current_user(request, default_if_logged_out=True)
            # The user may have uploaded a file with a different name from the original file, which is fine, as long
            # as the file is for the same plan.

            # Save fields from form but don't commit so can modify other fields before committing.
            plan = plan_form.save(commit=False)

            # Uploaded file will be given a unique name - so need to store the name of the file the user chose, which
            # may be different from the name when the file was last uploaded for this plan.
            plan.original_file_name = plan.file.name

            # Add user to record (currently hard-coded)
            # ToDo: Replace hard-coded user with actual user.
            plan.user = current_user

            # Now can save the record
            plan.save()

            # Have saved the record, now parse the plan and store activities.
            # Only store fields which are part of the plan for the given file type.

            mapping_type = plan.file_type.plan_field_mapping_type

            plan_file = plan.file.path

            file_reader = ExcelXLSFileReader()
            raw_data = file_reader.read(plan_file)
            parsed_data = file_reader.parse(raw_data, plan_field_mapping=mapping_type)
            new_activities, updated_activities, deleted_sticky_ids = update_plan_data(parsed_data, plan)
            for activity in new_activities:
                record = PlanActivity(
                    plan=plan,
                    unique_sticky_activity_id=activity['unique_sticky_activity_id'],
                    activity_name=activity['activity_name'],
                    duration=activity['duration'],
                    start_date=activity['start_date'],
                    end_date=activity['end_date'],
                    level=activity['level'] if 'level' in activity else 1,
                )
                record.save()
            for activity in updated_activities:
                record = PlanActivity.objects.get(plan=plan, unique_sticky_activity_id=activity['unique_sticky_activity_id'])
                record.activity_name = activity['activity_name']
                record.duration = activity['duration']
                record.start_date = activity['start_date']
                record.end_date = activity['end_date']
                record.level = activity['level'] if 'level' in activity else 1
                record.save()
            for deleted_sticky_id in deleted_sticky_ids:
                # Need to remove from the plan and from any visuals

                # Remove from plan
                record = PlanActivity.objects.get(plan=plan, unique_sticky_activity_id=deleted_sticky_id)
                record.delete()

                # Remove from visuals
                visuals = PlanVisual.objects.filter(plan=plan)
                for visual in visuals:
                    visual_activities = VisualActivity.objects.filter(visual=visual, unique_id_from_plan=deleted_sticky_id)
                    for visual_activity in visual_activities:
                        visual_activity.delete()

            messages.success(request, "New version of plan saved successfully")
        else:
            messages.error(request, "New version of plan upload failed validation")

        return HttpResponseRedirect(reverse('manage_plans'))
    elif request.method == "GET":
        form = ReUploadPlanForm(instance=plan_record)
        return render(request=request, template_name="plan_visual_django/pv_add_plan.html", context={'form': form})
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


def add_visual(request, plan_id):
    if request.method == "POST":
        visual_form = VisualFormForAdd(data=request.POST, files=request.FILES)
        if visual_form.is_valid():
            # Save fields from form but don't commit so can modify other fields before comitting.
            visual_record = visual_form.save(commit=False)

            # Add plan to record
            plan = Plan.objects.get(id=plan_id)
            visual_record.plan = plan

            # Now can save the record
            visual_record.save()
            messages.success(request, "New visual for plan saved successfully")

            # Now create default versions of objects which are required as part of any visual activity
            # This logic assumes that there will be certain default records in the database such as Color
            # and PlotableFormat records.

            # First create default swimlane
            default_plotable_style = PlotableStyle.objects.get(style_name="(default)")
            swimlane = SwimlaneForVisual(
                plan_visual=visual_record,
                swim_lane_name="(default)",
                plotable_style=default_plotable_style,
                sequence_number=1
            ).save()

        return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))
    elif request.method == "GET":
        form = VisualFormForAdd()
        context = {
            'add_or_edit': 'Add',
            'form': form
        }
        return render(request=request, template_name="plan_visual_django/pv_add_edit_visual.html", context=context)
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


def edit_visual(request, visual_id):
    instance = PlanVisual.objects.get(id=visual_id)
    plan_id = instance.plan.id
    if request.method == "POST":
        visual_form = VisualFormForEdit(data=request.POST, files=request.FILES, instance=instance)
        if visual_form.is_valid():
            # Save fields from form but don't commit so can modify other fields before comitting.
            visual_record = visual_form.save()
            messages.success(request, "Visual updated successfully")

        return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))
    elif request.method == "GET":
        form = VisualFormForEdit(instance=instance)
        context = {
            'add_or_edit': 'Edit',
            'form': form
        }
        return render(request=request, template_name="plan_visual_django/pv_add_edit_visual.html", context=context)
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


def manage_plans(request):
    user = get_current_user(request, default_if_logged_out=True)
    plan_files = Plan.objects.filter(user=user)

    context = {
        'user': user,
        'plan_files': plan_files
    }
    return render(request, "plan_visual_django/pv_manage_plans.html", context)


def delete_plan(request, pk):
    plan_record = Plan.objects.get(id=pk)

    # Before deleting record from database delete the file which was uploaded
    plan_file_path = os.path.join(settings.MEDIA_ROOT, plan_record.file.path)
    try:
        os.remove(plan_file_path)
    except OSError as e:
        messages.error(request, f"Error deleting file {plan_record.original_file_name}")

    try:
        plan_record.delete()
    except Exception:
        messages.error(request, f"Error deleting plan record for {plan_record.original_file_name}")
    else:
        messages.success(request, f"Record deleted for {plan_record.original_file_name}")

    return HttpResponseRedirect(reverse('manage_plans'))


def delete_visual(request, pk):
    visual_record = PlanVisual.objects.get(id=pk)
    # We need to know which plan this visual was attached to so that we can return to the manage visuals page after
    # deleting the visual.
    plan_id = visual_record.plan.id

    try:
        visual_record.delete()
    except Exception:
        messages.error(request,
                       f"Error deleting visual record {visual_record.name} for {visual_record.plan.original_file_name}")
    else:
        messages.success(request, f"Record deleted for {visual_record.name}")

    return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))


def manage_visuals(request, plan_id):
    """
    View for managing the visuals associated with a given uploaded plan, for the current user.

    :param request:
    :param plan_id:
    :return:
    """
    # ToDo decide what user validation is required here
    # Get plan record for the plan whose visuals we are managing.
    plan_record = Plan.objects.get(id=plan_id)

    # Get all visuals associated with this plan
    plan_visuals = plan_record.planvisual_set.all()

    context = {
        'plan': plan_record,
        'visuals': plan_visuals
    }
    return render(request, "plan_visual_django/pv_manage_visuals.html", context)


def configure_visual_activities(request, visual_id):
    """
    Gets all the plan activities related to the plan for which this visual was added and displays in tabular form to
    allow user to select which activities are to appear on the visual.  For every record which is selected, a visual
    activity record will be added.

    When a visual is first added there will be no visual activities.  As activities are added to the visual, new
    records will be added.  If the user deselects an activity which was previously selected, instead of deleting
    the plan activity record, the record will be flagged is disabled.  If the user subsequently reselects it,
    the visual activity will be re-enabled, and previous formatting and layout information will be retained.

    NOTE: Visual activities use the unique sticky id from the plan to identify which record on the plan a visual
    activity relates to, as that is the only field which will be consistent across multiple versions of a plan
    being uploaded.

    :param request:
    :param visual_id:
    :return:
    """
    visual = PlanVisual.objects.get(id=visual_id)  # get() returns exactly one result or raises an exception
    plan = visual.plan
    plan_activities = plan.planactivity_set.all()

    # Create list of fields for each activity and a flag to say whether the activity
    # is already in the plan or not.
    # But extract the unique_sticky_id as this is needed for the id of the <tr> element
    # for each activity (used in sending API request later)
    plan_activities_list = []
    for activity in plan_activities:
        activity_data = {
            "unique_sticky_id": activity.unique_sticky_activity_id,
            "field_list": [],
        }
        for field_name in PlanField.plan_headings():
            if field_name != "unique_sticky_activity_id":  # Already included this
                activity_data['field_list'].append((field_name, getattr(activity, field_name)))

        # Now add the flag to say whether this activity is in or out of the visual.
        # If the record doesn't exist then the activity has never been added so is absent.
        # If the record does exist then check the enabled flag as may have been added and then disabled.
        try:
            # Get record for this activity if it exists.  There will be one or no records.
            visual_activity = visual.visualactivity_set.get(unique_id_from_plan=activity.unique_sticky_activity_id)
        except VisualActivity.DoesNotExist:
            # No record so activity not currently in visual
            enabled = False
        else:
            enabled = visual_activity.enabled

        activity_data['field_list'].append(("enabled", enabled))
        plan_activities_list.append(activity_data)

    context = {
        'visual_id': visual.id,
        'headings': PlanField.plan_headings(),
        'plan_activities': plan_activities_list
    }

    return render(request, "plan_visual_django/pv_configure_visual_activities.html", context)


def layout_visual(request, visual_id):
    """
    Used to specify layout and formatting attributes for each of the activities selected to be in the visual.  Only the
    activities which have been selected will be shown (activities can be added or removed from the visual using the
    configure activities from visual screen).

    Note this uses a skeleton template as the html will be built by Javascript.

    :param request:
    :param visual_id:
    :return:
    """
    VisualActivityFormSet = inlineformset_factory(
        PlanVisual,
        VisualActivity,

        # These are the fields that can be edited.  There will be other fields which need to be displayed but aren't
        # part of the form. (e.g. Activity name)
        fields=(
            "swimlane",
            "vertical_positioning_type",
            "vertical_positioning_value",
            "height_in_tracks",
            "text_vertical_alignment",
            "text_flow",
            "plotable_shape",
            "plotable_style"
        ),
        extra=0,
        can_delete=False,
        form=VisualActivityFormForEdit
    )
    visual = PlanVisual.objects.get(pk=visual_id)
    if request.method == 'GET':
        formset = VisualActivityFormSet(instance=visual, queryset=visual.visualactivity_set.filter(enabled=True))
        # Add value of activity field for each form as won't be provided by visual
        context = {
            'formset': formset
        }
        return render(request, "plan_visual_django/pv_layout_visual.html", context)

    if request.method == 'POST':
        formset = VisualActivityFormSet(request.POST, instance=visual)
        if formset.is_valid():
            formset.save()
            return redirect(f'/pv/layout-visual/{visual_id}')
        else:
            raise Exception(f"Fatal error saving layout, {formset.errors}")


class PlotVisualView(DetailView):
    model = PlanVisual

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        plan_visual: PlanVisual = self.get_object()  # Retrieve DB instance which is being viewed.
        visual_settings = VisualSettings(width=1200, height=600)
        visual_orchestrator = VisualOrchestration(plan_visual, visual_settings)

        canvas_renderer = CanvasRenderer()
        canvas_data = canvas_renderer.plot_visual(visual_orchestrator.visual_collection)

        context['activity_data'] = canvas_data

        return context
