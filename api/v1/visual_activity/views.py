from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from plan_visual_django.models import TRACK_NUMBER, DEFAULT_VERTICAL_POSITIONING_TYPE, \
    DEFAULT_VERTICAL_POSITIONING_VALUE, DEFAULT_HEIGHT_IN_TRACKS, DEFAULT_TEXT_HORIZONTAL_ALIGNMENT, \
    DEFAULT_TEXT_VERTICAL_ALIGNMENT, DEFAULT_TEXT_FLOW, PlotableShape, PlotableShapeType, DEFAULT_PLOTABLE_SHAPE_NAME, \
    SwimlaneForVisual, DEFAULT_SWIMLANE_NAME, PlotableStyle, DEFAULT_PLOTABLE_STYLE_NAME, VisualActivity, PlanVisual


class VisualActivityAPI(APIView):
    def put(self, request, visual_id, unique_id, format=None, **kwargs):
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
            # Need to create a new record for this activity in this visual
            initial_plotable_shape = PlotableShape.objects.get(shape_type__name=DEFAULT_PLOTABLE_SHAPE_NAME)

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

            initial_style = PlotableStyle.objects.get(style_name=DEFAULT_PLOTABLE_STYLE_NAME)

            new_visual_activity = VisualActivity(
                visual=visual,
                unique_id_from_plan=unique_id,
                vertical_positioning_type=DEFAULT_VERTICAL_POSITIONING_TYPE,
                vertical_positioning_value=DEFAULT_VERTICAL_POSITIONING_VALUE,
                height_in_tracks=DEFAULT_HEIGHT_IN_TRACKS,
                text_horizontal_alignment=DEFAULT_TEXT_HORIZONTAL_ALIGNMENT,
                text_vertical_alignment=DEFAULT_TEXT_VERTICAL_ALIGNMENT,
                text_flow=DEFAULT_TEXT_FLOW,
                plotable_shape_id=initial_plotable_shape.id,
                plotable_style_id=initial_style.id,
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