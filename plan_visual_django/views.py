import json
import os
from typing import List, Dict, Any
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import ProtectedError
from django.forms import inlineformset_factory, modelformset_factory, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from plan_visual_django.exceptions import DuplicateSwimlaneException, PlanParseError, ExcelPlanSheetNotFound, \
    AddPlanError
from plan_visual_django.forms import PlanForm, VisualFormForAdd, VisualFormForEdit, VisualActivityFormForEdit, \
    ReUploadPlanForm, VisualSwimlaneFormForEdit, VisualTimelineFormForEdit, ColorForm, PlotableStyleForm, \
    SwimlaneDropdownForm
from plan_visual_django.models import Plan, PlanVisual, PlanField, PlanActivity, SwimlaneForVisual, VisualActivity, \
    PlotableStyle, TimelineForVisual, Color
from django.contrib import messages
from plan_visual_django.services.general.color_utilities import ColorLib
from plan_visual_django.services.general.string_utilities import indent
from plan_visual_django.services.plan_file_utilities.plan_parsing import read_and_parse_plan
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.services.general.user_services import get_current_user, can_access_plan, can_access_visual
from plan_visual_django.services.plan_file_utilities.plan_updater import update_plan_data
from plan_visual_django.services.visual.auto_layout import VisualAutoLayoutManager
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration
import logging

logger = logging.getLogger(__name__)

@login_required
@transaction.atomic
def add_plan(request):
    logger.debug("Adding plan...")
    if request.method == "POST":
        plan_form = PlanForm(data=request.POST, files=request.FILES)
        if plan_form.is_valid():
            current_user = get_current_user(request, default_if_logged_out=True)

            # Save fields from form but don't commit so can modify other fields before committing.
            plan = plan_form.save(commit=False)

            # Check that user hasn't already added a file with this name. Count should be zero
            count = Plan.objects.filter(user=current_user, file_name=plan.file.name).count()
            if count > 0:
                messages.error(request, f"Already uploaded a file called {plan.file.name}.  Record not added")
            else:
                # Uploaded file will be given a unique name - so need to store the name of the file the user chose.
                plan.file_name = plan.file.name
                plan.user = current_user

                # Now can save the record
                plan.save()
                logger.info(f"Plan added for user {current_user}, name = {plan.file.name}")

                # Have saved the record, now parse the plan and store activities.
                # Only store fields which are part of the plan for the given file type.

                mapping_type = plan.file_type.plan_field_mapping_type
                plan_file = plan.file.path
                file_reader = ExcelXLSFileReader()

                # Attempt to read and parse the plan, if an error occurs log it to messages and then abort transaction
                # to ensure there is no plan record saved without correct activities.
                try:
                    read_and_parse_plan(plan, mapping_type, file_reader)
                except PlanParseError as e:
                    messages.error(request, f"Plan parse error parsing {plan_file}, {e}")
                    transaction.set_rollback(True)
                except ExcelPlanSheetNotFound as e:
                    messages.error(request, f"{e}")
                    transaction.set_rollback(True)
                else:
                    messages.success(request, "New plan saved successfully")
        else:
            messages.error(request, "Failed validation")

        return HttpResponseRedirect(reverse('manage-plans'))
    elif request.method == "GET":
        form = PlanForm()
        return render(request=request, template_name="plan_visual_django/pv_add_plan.html", context={'form': form})
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")\


@login_required
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
            plan.file_name = plan.file.name

            # Add user to record (currently hard-coded)
            # ToDo: Replace hard-coded user with actual user.
            plan.user = current_user

            # Now can save the record
            plan.save()

            # Have saved the record, now parse the plan and store activities.
            # Only store fields which are part of the plan for the given file type.

            mapping_type = plan.file_type.plan_field_mapping_type

            file_reader = ExcelXLSFileReader()
            raw_data, headers = file_reader.read(plan)
            parsed_data = file_reader.parse(raw_data, headers, plan_field_mapping=mapping_type)
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

        return HttpResponseRedirect(reverse('manage-plans'))
    elif request.method == "GET":
        if not can_access_plan(request.user, pk):
            messages.error(request, "Plan does not exist or you do not have access")
            return HttpResponseRedirect(reverse('manage-plans'))
        else:
            form = ReUploadPlanForm(instance=plan_record)
            return render(request=request, template_name="plan_visual_django/pv_add_plan.html", context={'form': form})
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


@login_required
def add_visual(request, plan_id):
    if request.method == "POST":
        visual_form = VisualFormForAdd(data=request.POST, files=request.FILES)
        if visual_form.is_valid():
            # Before attempting to save, check whether the name of this visual already exists for this plan
            if PlanVisual.objects.filter(plan_id=plan_id, name=visual_form.cleaned_data["name"]).exists():
                messages.error(request, f"Name for new visual {visual_form.cleaned_data['name']} already exists - choose another one.")
                form = VisualFormForAdd()
                context = {
                    'add_or_edit': 'Add',
                    'form': visual_form
                }
                return render(request=request, template_name="plan_visual_django/pv_add_edit_visual.html", context=context)

            # Save fields from form but don't commit so can modify other fields before comitting.
            visual_record = visual_form.save(commit=False)

            # Add plan to record
            plan = Plan.objects.get(id=plan_id)
            visual_record.plan = plan

            # Now can save and commit the record
            visual_record.save()
            messages.success(request, "New visual for plan saved successfully")

            # Now create default versions of objects which are required as part of any visual activity
            # This logic assumes that there will be certain default records in the database such as Color
            # and PlotableFormat records.

            style_for_swimlane = visual_record.default_swimlane_plotable_style

            # First create default swimlane
            default_swimlane = SwimlaneForVisual.objects.create(
                plan_visual=visual_record,
                swim_lane_name="(default)",
                plotable_style=style_for_swimlane,
                sequence_number=1,
            )

        return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))
    elif request.method == "GET":
        if not can_access_plan(request.user, plan_id):
            messages.error(request, "Plan does not exist or you do not have access")
            return HttpResponseRedirect(reverse('manage-plans'))
        else:
            form = VisualFormForAdd()
            context = {
                'add_or_edit': 'Add',
                'form': form
            }
            return render(request=request, template_name="plan_visual_django/pv_add_edit_visual.html", context=context)
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


@login_required
def edit_visual(request, visual_id):
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
    else:
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
                'visual': instance,
                'add_or_edit': 'Edit',
                'form': form
            }
            return render(request=request, template_name="plan_visual_django/pv_add_edit_visual.html", context=context)
        else:
            raise Exception("Unrecognised METHOD {request['METHOD']}")


@login_required
def manage_plans(request):
    user = get_current_user(request)
    if user is None:
        messages.error(request, "No user logged in")
        return HttpResponseRedirect('/accounts/login')

    plan_files = Plan.objects.filter(user=user)
    context = {
        'primary_heading': "Manage Plans",
        'secondary_heading': "",
        'user': user,
        'plan_files': plan_files
    }
    return render(request, "plan_visual_django/pv_manage_plans.html", context)


@login_required
def delete_plan(request, pk):
    # ToDo: refactor to be consistent in naming of pk and plan_id (and other examples)
    if not can_access_plan(request.user, pk):
        messages.error(request, "Plan does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
    else:
        plan_record = Plan.objects.get(id=pk)

        # Before deleting record from database delete the file which was uploaded
        plan_file_path = os.path.join(settings.MEDIA_ROOT, plan_record.file.path)
        try:
            os.remove(plan_file_path)
        except OSError as e:
            messages.warning(request, f"Error deleting file {plan_record.file_name}")

        try:
            plan_record.delete()
        except Exception:
            messages.error(request, f"Error deleting plan record for {plan_record.file_name}")
        else:
            messages.success(request, f"Record deleted for {plan_record.file_name}")

        return HttpResponseRedirect(reverse('manage_plans'))


@login_required
def delete_visual(request, pk):
    if not can_access_visual(request.user, pk):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
    else:
        visual_record = PlanVisual.objects.get(id=pk)
        # We need to know which plan this visual was attached to so that we can return to the manage visuals page after
        # deleting the visual.
        plan_id = visual_record.plan.id

        try:
            visual_record.delete()
        except Exception:
            messages.error(request,
                           f"Error deleting visual record {visual_record.name} for {visual_record.plan.file_name}")
        else:
            messages.success(request, f"Record deleted for {visual_record.name}")

        return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))


@login_required
def manage_visuals(request, plan_id):
    """
    View for managing the visuals associated with a given uploaded plan, for the current user.

    If plan doesn't exist or if user doesn't have permission to access the plan then a page not found error will
    be displayed.

    :param request:
    :param plan_id:
    :return:
    """
    if not can_access_plan(request.user, plan_id):
        messages.error(request, "Plan does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
    else:
        plan_record = Plan.objects.get(id=plan_id)
        visuals = plan_record.planvisual_set.all()
        plan_summary_data = plan_record.get_plan_summary_data()

        plan_summary_data_display = [(name, value) for name, value in plan_summary_data.values()]

        context = {
            'primary_heading': "Manage Visuals",
            'secondary_heading': "",
            'plan': plan_record,
            'visuals': visuals,
            'plan_summary_data_display': plan_summary_data_display
        }
        return render(request, "plan_visual_django/pv_manage_visuals.html", context)


@login_required
def manage_swimlanes_for_visual(request, visual_id):
    """
    Displays swimlanes for this visual and allows user to edit details of any swimlane, or add a new one.

    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    VisualSwimlaneFormSet = inlineformset_factory(
        PlanVisual,
        SwimlaneForVisual,

        fields=(
            "sequence_number",
            "swim_lane_name",
            "plotable_style",
        ),
        extra=1,
        can_delete=True,
        form=VisualSwimlaneFormForEdit
    )
    visual = PlanVisual.objects.get(pk=visual_id)
    if request.method == 'GET':
        formset = VisualSwimlaneFormSet(instance=visual)
        context = {
            'visual': visual,
            'formset': formset
        }
        return render(request, "plan_visual_django/pv_manage_swimlanes.html", context)

    if request.method == 'POST':
        formset = VisualSwimlaneFormSet(request.POST, instance=visual)
        if formset.is_valid():
            formset.save()
            return redirect(f'/pv/manage-swimlanes-for-visual/{visual_id}')
        else:
            raise Exception(f"Fatal error saving layout, {formset.errors}")


@login_required
def manage_timelines_for_visual(request, visual_id):
    """
    Displays swimlanes for this visual and allows user to edit details of any swimlane, or add a new one.

    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    VisualTimelineFormSet = inlineformset_factory(
        PlanVisual,
        TimelineForVisual,

        fields=(
            "timeline_type",
            "timeline_name",
            "timeline_height",
            "plotable_style",
            "sequence_number",
        ),
        extra=1,
        can_delete=True,
        form=VisualTimelineFormForEdit
    )
    visual = PlanVisual.objects.get(pk=visual_id)
    if request.method == 'GET':
        formset = VisualTimelineFormSet(instance=visual)
        context = {
            'visual': visual,
            'formset': formset
        }
        return render(request, "plan_visual_django/pv_manage_timelines.html", context)

    if request.method == 'POST':
        formset = VisualTimelineFormSet(request.POST, instance=visual)
        if formset.is_valid():
            formset.save()
            return redirect(f'/pv/manage-timelines-for-visual/{visual_id}')
        else:
            raise Exception(f"Fatal error saving layout, {formset.errors}")


@login_required()
def manage_plotable_styles(request):
    """
    Displays plotable styles for this user and allows user to edit details of any plotable style, or add a new one.

    Get current logged in user and manage plotable styles for that user.

    :param request:
    :return:
    """
    user = get_current_user(request)
    shared_data_user_name = settings.SHARED_DATA_USER_NAME
    shared_data_user = User.objects.get()
    PlotableStyleFormset = inlineformset_factory(
        User,
        PlotableStyle,
        fields="__all__",
        extra=1,
        can_delete=True,
        form=PlotableStyleForm
    )
    form_kwargs = {'users': [request.user, shared_data_user]}
    if request.method == 'GET':
        formset = PlotableStyleFormset(instance=user,  form_kwargs=form_kwargs)
        context = {
            'formset': formset
        }
        return render(request, "plan_visual_django/pv_manage_plotable_styles.html", context)

    if request.method == 'POST':
        formset = PlotableStyleFormset(request.POST, instance=user, form_kwargs=form_kwargs)
        if formset.is_valid():
            formset.save()
            return redirect(f'/pv/manage-plotable-styles')
        else:
            messages.error(request, "Error saving plotable styles")
            return HttpResponseRedirect(reverse('manage-styles'))


@login_required
def create_milestone_swimlane(request, visual_id):
    """
    Applies logic to visual to lay out milestone visuals in a swimlane.  This is a one-off operation and once
    done the user can edit the visual to change the layout.

    After applying the changes the view will move to the visual rendering.

    :param visual_settings:
    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
    visual = PlanVisual.objects.get(id=visual_id)
    visual_settings = VisualSettings(visual_id=visual.id)
    auto_layout_manager = VisualAutoLayoutManager(visual_id_for_plan=visual_id)

    swimlane_plotable_style = visual_settings.default_swimlane_plotable_style
    milestone_plotable_style = visual_settings.default_milestone_plotable_style
    milestone_plotable_shape = visual_settings.default_milestone_shape

    try:
        auto_layout_manager.create_milestone_swimlane(
            swimlane_plotable_style=swimlane_plotable_style,
            milestone_plotable_style=milestone_plotable_style,
            milestone_plotable_shape=milestone_plotable_shape
        )
    except DuplicateSwimlaneException as e:
        messages.error(request, "Milestone swimlane already exists")
    return HttpResponseRedirect(reverse('plot-visual', args=[visual_id]))


@login_required
def select_visual_activities(request, visual_id):
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
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))
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
            "field_list": {},
        }
        # Need to extract level early as needed to calculate indent
        level = activity.level
        for field_name in PlanField.plan_headings():
            if field_name != "unique_sticky_activity_id":  # Already included this
                if field_name == "activity_name":
                    activity_data['field_list'][field_name] = indent(getattr(activity, field_name), level-1, ch='&nbsp;', multiple=3)
                else:
                    activity_data['field_list'][field_name] = getattr(activity, field_name)

        # Now add the flag to say whether this activity is in or out of the visual.
        # If the record doesn't exist then the activity has never been added so is absent.
        # If the record does exist then check the enabled flag as may have been added and then disabled.
        try:
            # Get record for this activity within the visual, if it exists.  There will be one or no records.
            visual_activity = visual.visualactivity_set.get()
        except VisualActivity.DoesNotExist:
            # No record so activity not currently in visual
            enabled = False
        else:
            enabled = visual_activity.enabled

        activity_data['field_list']['enabled'] = enabled
        plan_activities_list.append(activity_data)

    context = {
        'visual': visual,
        'headings': PlanField.plan_headings(),
        'plan_activities': plan_activities_list
    }

    return render(request, "plan_visual_django/pv_configure_visual_activities.html", context)


@login_required
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
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    VisualActivityFormSet = inlineformset_factory(
        PlanVisual,
        VisualActivity,

        # These are the fields that can be edited.  There will be other fields which need to be displayed but aren't
        # part of the form. (e.g. Activity name)
        fields=(
            "swimlane",
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
        queryset = visual.visualactivity_set.filter(enabled=True)
        formset = VisualActivityFormSet(instance=visual, queryset=queryset)
        swimlane_form = SwimlaneDropdownForm(instance=visual)

        # Add value of activity field for each form as won't be provided by visual
        context = {
            'visual': visual,
            'formset': formset,
            'swimlane_dropdown_form': swimlane_form
        }
        return render(request, "plan_visual_django/pv_layout_visual.html", context)

    if request.method == 'POST':
        formset = VisualActivityFormSet(request.POST, instance=visual)
        if formset.is_valid():
            formset.save()
            return redirect(f'/pv/layout-visual/{visual_id}')
        else:
            raise Exception(f"Fatal error saving layout, {formset.errors}")


@login_required
def plot_visual(request, visual_id):
    """
    This view is used to plot the visual.  It will be called by the browser when the page is loaded and will return
    the data required to plot the visual.

    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    visual = PlanVisual.objects.get(id=visual_id)

    if visual.activity_count() == 0:
        messages.error(request, "No activities selected for visual")
        return HttpResponseRedirect(f'/pv/configure-visual-activities/{visual_id}')
    else:
        visual_settings = VisualSettings(visual_id)
        visual_orchestrator = VisualOrchestration(visual, visual_settings)
        canvas_renderer = CanvasRenderer()
        canvas_data = canvas_renderer.plot_visual(visual_orchestrator.visual_collection)
        swimlane_form = SwimlaneDropdownForm(instance=visual)
        context = {
            'activity_data': canvas_data,
            'visual': visual,
            'swimlane_dropdown_form': swimlane_form
        }
        return render(request, "plan_visual_django/planvisual_detail.html", context)


@login_required
def plot_visual_02(request, visual_id):
    """
    This view is used to plot the visual.  It will be called by the browser when the page is loaded and will return
    the data required to plot the visual.

    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    visual = PlanVisual.objects.get(id=visual_id)

    if visual.activity_count() == 0:
        messages.error(request, "No activities selected for visual")
        return HttpResponseRedirect(f'/pv/configure-visual-activities/{visual_id}')
    else:
        # visual_settings = VisualSettings(visual_id)
        # visual_orchestrator = VisualOrchestration(visual, visual_settings)
        # canvas_renderer = CanvasRenderer()
        # canvas_data = canvas_renderer.plot_visual(visual_orchestrator.visual_collection)
        # swimlane_form = SwimlaneDropdownForm(instance=visual)
        context = {
            # 'activity_data': canvas_data,
            'visual': visual,
            # 'swimlane_dropdown_form': swimlane_form
        }
        return render(request, "plan_visual_django/planvisual_detail_02.html", context)
@login_required
def plot_visual_03(request, visual_id):
    """
    Screen for full dynamic editing of a visual for a given plan.

    :param request:
    :param visual_id:
    :return:
    """
    if not can_access_visual(request.user, visual_id):
        messages.error(request, "Visual does not exist or you do not have access")
        return HttpResponseRedirect(reverse('manage-plans'))

    visual = PlanVisual.objects.get(id=visual_id)

    context = {
        'visual': visual,
    }
    return render(request, "plan_visual_django/planvisual_detail_03.html", context)

@login_required
def manage_colors(request):
    """
    This view is used to define the colors used in the visual for a user.

    :param request:
    :param visual_id:
    :return:
    """
    extra_rows_on_form = 1
    ColorFormset = formset_factory(ColorForm, extra=extra_rows_on_form, can_delete=True)

    colors_for_user = Color.objects.filter(user=request.user)

    # Set initial data which is used on form to show existing values and when processing the form to detect changed
    # rows. Note that as the color widget on the ColorForm has an initial value of #000000, the form will always
    # be flagged as changed unless the initial values are set to include that value.

    initial_for_extra: list[dict[str, Any]] = [
        {
            'hex_color': '#000000'
        } for i in range(extra_rows_on_form)
    ]

    if colors_for_user.count() == 0:
        initial = []
    else:
        initial: list[dict[str, Any]] = [
            {
                "id": record.id,
                "name": record.name,
                "hex_color": ColorLib.from_rgb_255(record.red, record.green, record.blue).to_hex6()
            }
            for record in colors_for_user
        ]

    if request.method == "POST":
        # ToDo: Look for better way of doing this, not sure I am detecting new, changed and deleted record correctly
        formset = ColorFormset(request.POST, initial=initial)
        if formset.is_valid():
            # First process deleted records
            for form in formset.deleted_forms:
                id = form.cleaned_data.get('id')
                name = form.cleaned_data.get('name')
                if id:
                    try:
                        object_to_delete = Color.objects.get(id=id)
                        object_to_delete.delete()
                    except ProtectedError:
                        messages.error(request, f"Cannot delete color {name} as it is in use")
                    else:
                        messages.info(request, f"Deleted color {name}")
            for form in formset:
                if len(form.changed_data) > 0 and form not in formset.deleted_forms:
                    id = form.cleaned_data.get('id')
                    name = form.cleaned_data.get('name')
                    hex_color = form.cleaned_data.get('hex_color')
                    color = ColorLib.from_hex6(hex_color)
                    red, green, blue = color.to_rgb_255()
                    if name and hex_color:
                        Color.objects.update_or_create(
                            id=id,
                            user=request.user,
                            defaults={
                                "name": name,
                                "red": red,
                                "green": green,
                                "blue": blue
                            }
                        )
            return HttpResponseRedirect(reverse('manage-colors'))
        else:
            raise Exception(f"Fatal error saving colors, {formset.errors}")
    else:
        formset = ColorFormset(
            initial=initial
        )
        return render(request, 'plan_visual_django/manage_colors.html', context={"formset": formset})


def swimlane_actions(request, visual_id):
    """
    Processes various different types of actions for a specific swimlane, such as add activities, sort swimlane etc.
    :param request:
    :param visual_id:
    :return:
    """
    if request.method == "POST":
        visual = PlanVisual.objects.get(id=visual_id)
        swimlane_form = SwimlaneDropdownForm(data=request.POST, instance=visual)
        if swimlane_form.is_valid():
            swimlane = swimlane_form.cleaned_data['swimlane']
        else:
            raise ValueError(f"Unable to read swimlane from form")
        auto_layout_manager = VisualAutoLayoutManager(visual_id)

        # Extract level from POST
        level_post_entry = [entry for entry in request.POST if
                            entry.startswith("Add") or
                            entry.startswith("Remove") or
                            entry.startswith("Compress") or
                            entry.startswith("Sort")]

        # Check exactly one match
        if len(level_post_entry) == 0:
            raise ValueError(f"Unexpected missing entry for level in POST {request.POST}")
        elif len(level_post_entry) > 1:
            raise ValueError(f"Unexpectedly more than one entry for level in POST {request.POST}")
        else:
            # Extract action and level from form element name.
            action, arg1, arg2 = tuple(level_post_entry[0].split(" "))
            action = action.lower()

        if action == "add" or action == "remove":
            if arg2 == "ALL": arg2 = "0"
            level = int(arg2)

            if action == "add":
                auto_layout_manager.add_delete_activities(level, swimlane, delete_flag=False)
            elif action == 'remove':
                auto_layout_manager.add_delete_activities(level, swimlane, delete_flag=True)
            else:
                raise ValueError(f"Unknown action {action} during level based action")
        elif action == "sort":
            auto_layout_manager.sort_swimlane(swimlane)
        elif action == "compress":
            auto_layout_manager.compress_swimlane(swimlane)

    return HttpResponseRedirect(reverse('plot-visual', args=[visual_id]))
