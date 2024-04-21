import json

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.visual.serializer import VisualActivityListSerialiser
from plan_visual_django.models import DEFAULT_HEIGHT_IN_TRACKS, \
    SwimlaneForVisual, DEFAULT_SWIMLANE_NAME, VisualActivity, PlanVisual, \
    DEFAULT_VERTICAL_POSITIONING_TYPE, DEFAULT_TEXT_HORIZONTAL_ALIGNMENT, DEFAULT_TEXT_VERTICAL_ALIGNMENT, \
    DEFAULT_TEXT_FLOW
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration





class VisualActivityListAPI(APIView):
    def get(self, request, visual_id):
        visual = PlanVisual.objects.get(id=visual_id)
        visual_activities = visual.visualactivity_set.all()
        serialiser = VisualActivityListSerialiser(visual_activities, many=True)

        return JsonResponse(serialiser.data, safe=False)


class VisualActivityAPI(APIView):
    def get(self, request, visual_id, unique_id):
        visual = PlanVisual.objects.get(id=visual_id)
        activity = visual.visualactivity_set.get(unique_id_from_plan=unique_id)

        activity_plotable = activity.get_plotable()

        renderer = CanvasRenderer()
        activity_data = renderer.plot_plotable(activity_plotable)

        activities_json = json.dumps(activity_data)
        return Response(activities_json)

    def put(self, request, visual_id, unique_id, **kwargs):
        """
        I don't know whether this is the right way to do this!

        The logic is that I want to add this activity from the plan to the supplied visual.  But if I have previously
        added the activity to the visual and then removed it there will already be a record for this activity with the
        enabled flag set to False.

        This means that I don't always want to create a new record.  I think in practice the keys which define the
        Visual Activity should be included in the URL not the additional data.  As I don't have any other data to add
        then the data element of the PUT request will be empty.  I don't know whether that is seen as poor practice
        or not, but it avoids using GET incorrectly or having to access data before validation which seems wrong.

        Note - the above means we don't even need a serializer (which seems a bit wrong).
        ToDo: Revisit use of PUT with no data to check this is good practice.

        :param request:
        :param visual_id:
        :param unique_id:
        :return:
        """

        try:
            visual = PlanVisual.objects.get(id=visual_id)
        except PlanVisual.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # We have found the visual so now check whether the activity already exists for the visual.
        try:
            visual_activity = visual.visualactivity_set.get(unique_id_from_plan=unique_id)
        except VisualActivity.DoesNotExist:
            # Need to create a new record for this activity in this visual.

            # if the plan activity for this visual activity is a milestone, plot as DIAMOND, else plot as RECTANGLE
            plan_activity = visual.plan.planactivity_set.get(unique_sticky_activity_id=unique_id)
            if plan_activity.milestone_flag is True:
                initial_plotable_shape = visual.default_milestone_shape
                initial_plotable_style = visual.default_milestone_plotable_style
            else:
                initial_plotable_shape = visual.default_activity_shape
                initial_plotable_style = visual.default_activity_plotable_style

            # Check whether there is already a default swimlane for this visual.  If not create one.
            try:
                initial_swimlane = SwimlaneForVisual.objects.get(
                    plan_visual=visual,
                    swim_lane_name=DEFAULT_SWIMLANE_NAME
                )
            except SwimlaneForVisual.DoesNotExist:
                initial_swimlane = SwimlaneForVisual(
                    plan_visual=visual,
                    swim_lane_name=DEFAULT_SWIMLANE_NAME
                )
                initial_swimlane.save()


            new_visual_activity = VisualActivity(
                visual=visual,
                unique_id_from_plan=unique_id,
                vertical_positioning_type=DEFAULT_VERTICAL_POSITIONING_TYPE,
                vertical_positioning_value=initial_swimlane.get_next_unused_track_number(),
                height_in_tracks=DEFAULT_HEIGHT_IN_TRACKS,
                text_horizontal_alignment=DEFAULT_TEXT_HORIZONTAL_ALIGNMENT,
                text_vertical_alignment=DEFAULT_TEXT_VERTICAL_ALIGNMENT,
                text_flow=DEFAULT_TEXT_FLOW,
                plotable_shape=initial_plotable_shape,
                plotable_style=initial_plotable_style,
                swimlane_id=initial_swimlane.id,
                enabled=True
            )
            new_visual_activity.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            # There is already a record so we just need to change the enabled flag to true.
            visual_activity.enabled = True
            visual_activity.save()
            return Response(status=status.HTTP_201_CREATED)

    def patch(self, request, visual_id, unique_id):
        """
        Updates specified fields for a given visual activity.

        The fields to be update are provided in the body of the request as a JSON object.  The JSON object should
        contain a record for every field to be updated with the field name as the key and the new value as the value.
        """
        try:
            visual = PlanVisual.objects.get(id=visual_id)
        except PlanVisual.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # We have found the visual so now check that the activity exists for the visual (it should).
        try:
            visual_activity = visual.visualactivity_set.filter(unique_id_from_plan=unique_id)[0]
        except VisualActivity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            # We have found the activity so now we need to update the fields.
            activity_data = request.data
            for field, value in activity_data.items():
                # For now we only support updating the vertical positioning value.
                if field == 'vertical_positioning_value':
                    visual_activity.vertical_positioning_value = value
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            visual_activity.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, visual_id, unique_id):
        # visual_id = kwargs['visual_id']
        # unique_id = kwargs['unique_id']
        try:
            visual = PlanVisual.objects.get(id=visual_id)
        except PlanVisual.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # We have found the visual so now check that the activity exists for the visual (it should).
        try:
            visual_activity = visual.visualactivity_set.get(unique_id_from_plan=unique_id)
        except VisualActivity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            visual_activity.enabled = False
            visual_activity.save()
            return Response(status=status.HTTP_200_OK)

