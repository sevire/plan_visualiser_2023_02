from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.visual.activity.serializer import ModelVisualActivityListSerialiser, ModelVisualActivitySerialiser
from api.v1.model.visual.timeline.serializer import ModelVisualTimelineListSerialiser, ModelVisualTimelineSerialiser
from plan_visual_django.models import PlanVisual, TimelineForVisual


class ModelVisualTimelineListAPI(ListAPIView):
    def get(self, request, visual_id=None, **kwargs):
        visual_timelines_queryset = PlanVisual.objects.get(id=visual_id).timelineforvisual_set.all()
        serializer = ModelVisualTimelineListSerialiser(instance=visual_timelines_queryset, many=True)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualTimelineAPI(APIView):
    def get(self, request, visual_id, timeline_seq_num):
        visual_timeline_queryset = PlanVisual.objects.get(id=visual_id).timelineforvisual_set.get(sequence_number=timeline_seq_num)
        serializer = ModelVisualTimelineSerialiser(instance=visual_timeline_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)
