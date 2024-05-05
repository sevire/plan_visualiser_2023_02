from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.visual.swimlane.serializer import ModelVisualSwimlaneListSerialiser
from plan_visual_django.models import PlanVisual


class ModelVisualSwimlaneListAPI(ListAPIView):
    def get(self, request, visual_id=None, **kwargs):
        visual_swimlanes_queryset = PlanVisual.objects.get(id=visual_id).swimlaneforvisual_set.all()
        serializer = ModelVisualSwimlaneListSerialiser(instance=visual_swimlanes_queryset, many=True)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualSwimlaneAPI(APIView):
    def get(self, request, visual_id, swimlane_seq_num, **kwargs):
        visual_swimlane_queryset = PlanVisual.objects.get(id=visual_id).swimlaneforvisual_set.get(sequence_number=swimlane_seq_num)
        serializer = ModelVisualSwimlaneListSerialiser(instance=visual_swimlane_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)



