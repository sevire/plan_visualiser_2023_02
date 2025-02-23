from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from plan_visual_django.models import PlanVisual
from plan_visual_django.services.visual.rendering.renderers import CanvasRenderer


class RenderedCanvasVisualTimelineListAPI(ListAPIView):
    """
    This API is used to generate data to render all the timelines for the given visual on html canvas.
    """
    def get(self, request, visual_id=None, **kwargs):
        """
        This method returns a JSON object containing all plotables for the specified visual.
        :param request:
        :param visual_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)
        timeline_plotables = {
            'timelines': visual.get_timeline_plotables()
        }

        renderer = CanvasRenderer()
        rendered_plotables = renderer.render_from_iterable(timeline_plotables)

        return JsonResponse(data=rendered_plotables, safe=False)



class RenderedCanvasVisualTimelineAPI(APIView):
    """
    This API is used to generate data to render all the timelines for the given visual on html canvas.
    """
    @staticmethod
    def get(request, visual_id, sequence_num, **kwargs):
        """
        This method returns a JSON object containing all plotables for the specified visual.
        :param request:
        :param visual_id:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)
        timeline_plotables = {
            'timelines': [visual.get_timeline_plotables(sequence_number=sequence_num)]
        }

        renderer = CanvasRenderer()
        rendered_plotables = renderer.render_from_iterable(timeline_plotables)

        return JsonResponse(data=rendered_plotables, safe=False)