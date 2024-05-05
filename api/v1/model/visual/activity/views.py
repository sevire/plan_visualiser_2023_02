from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.visual.activity.serializer import ModelVisualActivityListSerialiser, ModelVisualActivitySerialiser
from plan_visual_django.models import PlanVisual


class ModelVisualActivityListAPI(ListAPIView):
    def get(self, request, visual_id=None, enabled=False, **kwargs):
        if enabled is True:
            visual_activities_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.filter(enabled=True)
        else:
            visual_activities_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.all()
        serializer = ModelVisualActivityListSerialiser(instance=visual_activities_queryset, many=True)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualActivityAPI(APIView):
    def get(self, request, visual_id, unique_id):
        visual_activity_queryset = PlanVisual.objects.get(id=visual_id).visualactivity_set.get(unique_id_from_plan=unique_id)
        serializer = ModelVisualActivitySerialiser(instance=visual_activity_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)
