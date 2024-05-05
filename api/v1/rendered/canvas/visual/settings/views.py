import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from api.v1.model.visual.serializer import ModelVisualSettingsSerialiser
from plan_visual_django.models import PlanVisual, Plan
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings


class RenderedCanvasVisualettingsAPI(APIView):
    """
    This API is used to send key settings for the visual which the client needs to plot the visual.
    E.g the width of the canvas to plot the visual on.

    """
    def get(self, request, visual_id):
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