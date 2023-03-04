import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from plan_visual_django.forms import PlanForm, VisualFormForAdd, VisualFormForEdit
from plan_visual_django.models import Plan, PlanVisual, PlanField
from django.contrib import messages
from plan_visual_django.services.plan_reader import ExcelXLSFileReader
from plan_visual_django.services.user_services import get_current_user


# Create your views here.

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
                messages.success(request, "New plan saved successfully")
        else:
            messages.error(request, "Failed validation")

        return HttpResponseRedirect(reverse('manage_plans'))
    elif request.method == "GET":
        form = PlanForm()
        return render(request=request, template_name="plan_visualiser_django/pv_add_plan.html", context={'form': form})
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

        return HttpResponseRedirect(reverse('manage_visuals', args=[plan_id]))
    elif request.method == "GET":
        form = VisualFormForAdd()
        context = {
            'add_or_edit': 'Add',
            'form': form
        }
        return render(request=request, template_name="plan_visualiser_django/pv_add_edit_visual.html", context=context)
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
        return render(request=request, template_name="plan_visualiser_django/pv_add_edit_visual.html", context=context)
    else:
        raise Exception("Unrecognised METHOD {request['METHOD']}")


def manage_plans(request):
    user = get_current_user(request, default_if_logged_out=True)
    plan_files = Plan.objects.filter(user=user)

    context = {
        'user': user,
        'plan_files': plan_files
    }
    return render(request, "plan_visualiser_django/pv_manage_plans.html", context)


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
        messages.error(request, f"Error deleting visual record {visual_record.name} for {visual_record.plan.original_file_name}")
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
    return render(request, "plan_visualiser_django/pv_manage_visuals.html", context)


def format_and_layout_visual(request, visual_id):
    visual = PlanVisual.objects.get(id=visual_id)  # get() returns exactly one result or raises an exception
    plan = visual.plan
    mapping_type = plan.file_type.plan_field_mapping_type

    plan_file = plan.file.path
    file_reader = ExcelXLSFileReader()
    raw_data = file_reader.read(plan_file)
    parsed_data = file_reader.parse(raw_data, plan_field_mapping=mapping_type)

    context = {
        'headings': PlanField.plan_headings(),
        'plan_activities': parsed_data
    }

    return render(request, "plan_visualiser_django/pv_format_and_layout_visual.html", context)
