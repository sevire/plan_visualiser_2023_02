import json
import os
from typing import List, Dict, Any

import markdown
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import ProtectedError
from django.forms import inlineformset_factory, modelformset_factory, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from plan_visual_django.exceptions import DuplicateSwimlaneException, PlanParseError, ExcelPlanSheetNotFound, \
    AddPlanError
from plan_visual_django.forms import PlanForm, VisualFormForAdd, VisualFormForEdit, VisualActivityFormForEdit, \
    ReUploadPlanForm, VisualSwimlaneFormForEdit, VisualTimelineFormForEdit, ColorForm, PlotableStyleForm, \
    SwimlaneDropdownForm
from plan_visual_django.models import Plan, PlanVisual, PlanField, PlanActivity, SwimlaneForVisual, VisualActivity, \
    PlotableStyle, TimelineForVisual, Color, StaticContent, FileType, PlanMappedField
from django.contrib import messages
from plan_visual_django.services.general.color_utilities import ColorLib
from plan_visual_django.services.plan_file_utilities.plan_parsing import read_and_parse_plan
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.services.general.user_services import get_current_user, can_access_plan, can_access_visual
from plan_visual_django.services.visual.auto_layout import VisualAutoLayoutManager
from plan_visual_django.services.visual.visual_settings import VisualSettings
import logging

logger = logging.getLogger(__name__)

@login_required
@transaction.atomic
def add_plan(request):
    """
    Uploads an impoarts a new plan file and adds it and all the activities to the database.

    :param request:
    :return:
    """
    if request.method == "POST":
        logger.debug(f"Uploading new plan...")

        plan_form = PlanForm(data=request.POST, files=request.FILES)
        if plan_form.is_valid():
            # Save fields from form but don't commit so can modify other fields before committing.
            plan = plan_form.save(commit=False)

            current_user = get_current_user(request, default_if_logged_out=True)
            logger.debug(f"Uploading new plan for user {current_user.username}, plan is {plan.plan_name}")

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
                logger.info(f"Plan record added for user {current_user}, name = {plan.file.name}")
                logger.info(f"About to parse new plan for user {current_user}, name = {plan.file.name}")

                # Have saved the record, now parse the plan and store activities.
                # Only store fields which are part of the plan for the given file type.

                mapping_type = plan.file_type.plan_field_mapping_type
                file_reader = ExcelXLSFileReader()

                # Attempt to read and parse the plan, if an error occurs log it to messages and then abort transaction
                # to ensure there is no plan record saved without correct activities.
                try:
                    read_and_parse_plan(plan, mapping_type, file_reader)
                except PlanParseError as e:
                    messages.error(request, f"Plan parse error parsing {plan.file.path}, {e}")
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
    # plan_record needed either as instance to be updated (POST) or instance to populate form from (GET)
    plan_record = Plan.objects.get(id=pk)

    if request.method == "POST":
        logger.debug(f"Re-uploading plan id for user {request.user.username}, plan id is {pk}")

        # Upload the plan in an empty form (not pre-populated) to avoid displaying generated unique filename
        # then apply new file to existing plan record.
        plan_form = ReUploadPlanForm(data=request.POST, files=request.FILES)
        if plan_form.is_valid():
            # Note we aren't going to use this form to update the record.  We just needed the new version
            # of the file.  We will use this to modify the existing plan record.
            # Not sure if this is best practice but should work!

            plan_record.file = plan_form.cleaned_data['file']
            plan_record.file_name = plan_form.cleaned_data['file'].name
            plan_record.save()

            current_user = get_current_user(request, default_if_logged_out=True)
            logger.debug(f"File uploaded for user {current_user.username}, plan {plan_record.plan_name}")
            logger.debug(f"Re-importing plan for user {current_user.username}, plan is {plan_record.plan_name}")

            # Have saved the record, now parse the plan and store activities.
            # Only store fields which are part of the plan for the given file type.

            mapping_type = plan_record.file_type.plan_field_mapping_type
            file_reader = ExcelXLSFileReader()

            try:
                read_and_parse_plan(plan_record, mapping_type, file_reader, update_flag=True)
            except PlanParseError as e:
                messages.error(request, f"Plan parse error parsing {plan_record.file.path}, {e}")
                transaction.set_rollback(True)
            except ExcelPlanSheetNotFound as e:
                messages.error(request, f"{e}")
                transaction.set_rollback(True)
            else:
                messages.success(request, "Updated plan saved successfully")

        else:
            messages.error(request, "Re-uploaded version of plan upload failed validation")

        return HttpResponseRedirect(reverse('manage-plans'))
    elif request.method == "GET":
        if not can_access_plan(request.user, pk):
            messages.error(request, "Plan does not exist or you do not have access")
            return HttpResponseRedirect(reverse('manage-plans'))
        else:
            # Populate form with current plan details
            form = ReUploadPlanForm()
            context = {
                'form': form,
                'primary_heading': 'Re-upload File For Existing Plan',
                'secondary_heading': plan_record.file_name
            }
            return render(request=request, template_name="plan_visual_django/pv_add_plan.html", context=context)
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
            plan = Plan.objects.get(id=plan_id)

            form = VisualFormForAdd(plan=plan)
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

        return HttpResponseRedirect(reverse('manage-plans'))


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
            'primary_heading': f"Manage Visuals For Plan: { plan_record.plan_name }",
            'secondary_heading': f"File: { plan_record.file_name }",
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
    shared_data_user = User.objects.get(username=shared_data_user_name)
    PlotableStyleFormset = inlineformset_factory(
        User,
        PlotableStyle,
        fields="__all__",
        extra=1,
        can_delete=True,
        form=PlotableStyleForm
    )
    form_kwargs = {'users': [user, shared_data_user]}
    if request.method == 'GET':
        formset = PlotableStyleFormset(instance=user,  form_kwargs=form_kwargs)
        context = {
            'primary_heading': "Manage Styles",
            'secondary_heading': "",
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
def plot_visual(request, visual_id):
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

    plan_name = visual.plan.plan_name
    visual_name = visual.name

    context = {
        'primary_heading': f"Plan <small class='fst-italic text-body-secondary'>{plan_name}</small>",
        'secondary_heading': f"Visual <small class='fst-italic text-body-secondary'>{visual_name}</small>",
        'visual': visual,
    }
    return render(request, "plan_visual_django/planvisual_detail.html", context)


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
        context = {
            'primary_heading': "Manage Colours",
            'secondary_heading': "",
            'formset': formset
        }
        return render(request, 'plan_visual_django/manage_colors.html', context=context)


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


class FileTypeListView(ListView):
    template_name = "plan_visual_django/pv_list_file_types.html"
    model = FileType

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['primary_heading'] = "Support File Types and Field Mappings"

        mapped_fields_for_file_types = [(file_type, PlanMappedField.objects.filter(plan_field_mapping_type=file_type.plan_field_mapping_type).order_by('mapped_field__sort_index')) for file_type in context['object_list']]
        context['ordered_mapped_fields'] = mapped_fields_for_file_types

        return context


class StaticPageView(DetailView):
    model = StaticContent
    template_name = "plan_visual_django/static_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['primary_heading'] = self.object.title
        context['markdown_text'] = markdown.markdown(self.object.content, extensions=['nl2br'])
        return context

