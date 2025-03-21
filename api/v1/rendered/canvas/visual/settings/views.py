from django.http import JsonResponse
from rest_framework.views import APIView

from api.v1.model.visual.serializer import ModelVisualSettingsSerialiser
from plan_visual_django.models import PlanVisual


class RenderedCanvasVisualettingsAPI(APIView):
    """
    This API is used to send key settings for the visual which the client needs to plot the visual.
    E.g the width of the canvas to plot the visual on.

    """
    @staticmethod
    def get(request, visual_id):
        """
        returns settings as JSON.

        :param request:
        :param visual_id:
        :return:
        """
        visual_queryset = PlanVisual.objects.get(id=visual_id)
        serializer = ModelVisualSettingsSerialiser(instance=visual_queryset)

        response = serializer.data
        return JsonResponse(response, safe=False)