import json

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from plan_visual_django.models import PlanVisual, Plan
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration


class PlanVisualRenderAPI(APIView):
    """
    This API is used to render the visual for display in the browser.
    """
    def get(self, request, visual_id):
        """
        This method returns a JSON object containing all plotables for the specified visual.
        :param request:
        :param visual_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)

        if visual.activity_count() == 0:
            return JsonResponse(status=status.HTTP_204_NO_CONTENT)
        else:
            visual_plotables = visual.get_plotables()







            visual_settings = VisualSettings(visual_id)
            visual_orchestrator = VisualOrchestration(visual, visual_settings)
            canvas_renderer = CanvasRenderer()
            canvas_data = canvas_renderer.plot_visual(visual_orchestrator.visual_collection)
            data = {
                "activity_data": canvas_data,
                "visual": visual
            }
            return_data = json.dumps(canvas_data)
            return JsonResponse(return_data)
