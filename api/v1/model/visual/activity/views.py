from django.db import transaction
from django.views import View
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services.error_message_handling import MessagesToHeaderMixin
from api.v1.model.visual.activity.serializer import ModelVisualActivityListSerialiser, ModelVisualActivitySerialiser, \
    ModelVisualActivitySerialiserForUpdate
from plan_visual_django.models import (PlanVisual, VisualActivity,
                                       DEFAULT_HEIGHT_IN_TRACKS, DEFAULT_TEXT_VERTICAL_ALIGNMENT, DEFAULT_TEXT_FLOW, \
    DEFAULT_TEXT_HORIZONTAL_ALIGNMENT)
from plan_visual_django.services.service_utilities.service_response import ServiceStatusCode
from plan_visual_django.services.visual.model.auto_layout import VisualLayoutManager
from plan_visual_django.services.visual.model.layout import adjust_visual_activity_track
from django.contrib import messages


class VisualActivityViewDispatcher(View):
    @staticmethod
    def get(request, *args, **kwargs):
        view = ModelVisualActivityListAPI.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def patch(request, *args, **kwargs):
        view = ModelVisualActivityUpdateAPI.as_view()
        return view(request, *args, **kwargs)


class ModelVisualActivitySwimlaneDispatcher(APIView):
    """
    Dispatcher for adding activity to visual in given swimlane or moving activity to new simwlane.
    Can be a bit confusing as the swimlane for moving an activity is a sequence number, but for adding an
    activity is a swimlane_id.  I think this is logically right, but it means a similar url has a different
    meaning, which isn't as clean as I'd like.

    ToDo: Re-visit use of sequence number vs swimlane_id for swimlane for moving/adding activity.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.method == "PUT":
            return ModelVisualActivityAPI.as_view()(request, *args, **kwargs)
        elif request.method == "PATCH":
            return ModelVisualActivityChangeSwimlaneAPI.as_view()(request, *args, **kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)


class ModelVisualActivitySwimlaneSubActivities(MessagesToHeaderMixin, APIView):
    @staticmethod
    def put(request, visual_id, activity_unique_id, swimlane, *args, **kwargs):
        """
        Adds all sub-activities for a given activity to the visual at the swimlane sequence number specified
        :param request:
        :param activity_unique_id:
        :param swimlane:
        :param args:
        :param kwargs:
        :return:
        """
        manager = VisualLayoutManager(visual_id)
        service_status = manager.add_subactivities(activity_unique_id, swimlane)
        if service_status.status == ServiceStatusCode.SUCCESS:
            messages.add_message(request, messages.INFO, service_status.message)
            return Response(status=status.HTTP_201_CREATED)
        else:
            messages.add_message(request, messages.INFO, service_status.message)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelVisualActivityListAPI(ListAPIView):
    def get(self, request, visual_id=None, enabled=False, **kwargs):
        if enabled is True:
            visual_activities_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.filter(enabled=True)
        else:
            visual_activities_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.all()
        serializer = ModelVisualActivityListSerialiser(instance=visual_activities_queryset, many=True)

        response = serializer.data

        return Response(response)


class ModelVisualActivityUpdateAPI(APIView):
    @staticmethod
    def patch(request, visual_id=None, **kwargs):
        """
        For patching or updating the activity from the API I am not expecting to update related records so
        I don't need to set the depth to anything.  Specifically, for the use case where we are just updating the
        swimlane (a common use case) I only want to update the foreign key.  So I have created a different serializer
        no depth defined for updating.

        It's possible that I will encounter further use cases where I need to be more sophisticated with
        what I need to do for foreign key relationships when updating.

        :param request:
        :param visual_id:
        :param kwargs:
        :return:
        """
        visual_activity_data = request.data

        with transaction.atomic():
            for activity_data in visual_activity_data:
                try:
                    instance = VisualActivity.objects.get(id=activity_data['id'])

                    if instance.visual_id != visual_id:
                        return Response({"error": f"Supplied activity id {activity_data['id']} does not belong to supplied visual"},
                                        status=status.HTTP_409_CONFLICT)
                    serializer_for_current_record = ModelVisualActivitySerialiserForUpdate(instance, data=activity_data, partial=True)
                    if serializer_for_current_record.is_valid(raise_exception=True):
                        serializer_for_current_record.save()
                except VisualActivity.DoesNotExist:
                    return Response({"error": f"Object with id={activity_data['id']} not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)


class ModelVisualActivityAddSubActivitiesAPI(APIView):
    @staticmethod
    def put(request, visual_id, activity_unique_id:str, swimlane, **kwargs):
        # ToDo: Complete the coding for the add sub-activities functionality
        pass # Coding in progress


class ModelVisualActivityAPI(MessagesToHeaderMixin, APIView):
    @staticmethod
    def get(request, visual_id, activity_unique_id):
        visual_activity_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.get(unique_id_from_plan=activity_unique_id)
        serializer = ModelVisualActivitySerialiser(instance=visual_activity_queryset)

        response = serializer.data

        return Response(response)

    @staticmethod
    def put(request, visual_id, activity_unique_id, swimlane=1):
        """
        Adds activity to visual in given swimlane.  Note the swimlane number is a sequence number,
        not a swimlane id.

        :param request:
        :param visual_id:
        :param activity_unique_id:
        :return:
        """
        # ToDo: Revisit use of PUT with no data to check this is good practice.

        visual_manager = VisualLayoutManager(visual_id)
        service_status = visual_manager.add_activity_to_swimlane(activity_unique_id, swimlane)
        if service_status.status == ServiceStatusCode.SUCCESS:
            messages.add_message(request, messages.INFO, service_status.message)
            return Response(status=status.HTTP_201_CREATED)
        else:
            messages.add_message(request, messages.INFO, service_status.message)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete(request, visual_id, activity_unique_id):
        try:
            visual = PlanVisual.objects.get(id=visual_id)
        except PlanVisual.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # We have found the visual so now check whether the activity already exists for the visual.
        visual_activity = visual.visualactivity_set.get(unique_id_from_plan=activity_unique_id)

        # We just disable this activity - no need to physically delete it.
        visual_activity.enabled = False
        visual_activity.save()

        return Response(status=status.HTTP_202_ACCEPTED)

class ModelVisualActivityChangeSwimlaneAPI(MessagesToHeaderMixin, APIView):
    @staticmethod
    def patch(request, visual_id, activity_unique_id, swimlane):
        """
        We are updating the swimlane and adjusting the track to position the activity at the bottom of the new swimlane.

        :param request:
        :param visual_id:
        :param activity_unique_id:
        :param new_swimlane_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)
        visual_activity = VisualActivity.objects.get(visual=visual, unique_id_from_plan=activity_unique_id)

        adjust_visual_activity_track(visual_activity, swimlane)

        with transaction.atomic():  # Not sure we need this!
            visual_activity.save()

        messages.add_message(request, messages.INFO, "Activity moved to new swimlane")
        return Response(status=status.HTTP_202_ACCEPTED)