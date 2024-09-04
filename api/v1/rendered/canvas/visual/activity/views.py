from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from plan_visual_django.models import PlanVisual, Plan
from plan_visual_django.services.visual.renderers import CanvasRenderer


class RenderedCanvasVisualActivityListAPI(APIView):
    """
    This API is used to render the visual activities for display as part of the visual
    in the browser.
    """
    @staticmethod
    def get(request, visual_id):
        """
        This method returns a JSON object containing all plotables for the specified visual.
        :param request:
        :param visual_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)

        if visual.activity_count() == 0:
            return JsonResponse(status=status.HTTP_204_NO_CONTENT, data=None)
        else:
            visual_activity_plotables = {"activities": visual.get_visual_activity_plotables()}
            renderer = CanvasRenderer()
            rendered_plotables = renderer.render_from_iterable(visual_activity_plotables)
            return JsonResponse(rendered_plotables, safe=False)

class RenderedCanvasVisualActivityAPI(APIView):
    """
    This API is used to render a specific visual activity for display as part of the visual
    in the browser.
    """
    @staticmethod
    def get(request, visual_id, unique_id):
        """
        This method returns a JSON object containing all plotables for the specified visual.
        :param request:
        :param visual_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)

        if visual.activity_count() == 0:
            return JsonResponse(status=status.HTTP_204_NO_CONTENT, data=None)
        else:
            activity = visual.visualactivity_set.get(unique_id_from_plan=unique_id)
            activity_plotable = activity.get_plotable()
            visual_activity_plotables = {"activities": [activity_plotable]}
            renderer = CanvasRenderer()
            rendered_plotables = renderer.render_from_iterable(visual_activity_plotables)
            return JsonResponse(rendered_plotables, safe=False)