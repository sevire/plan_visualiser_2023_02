from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from api.v1.model.visual.plotable_shape.serializer import ModelVisualShapeSerializer
from plan_visual_django.models import PlotableShape


class ModelVisualShapeAPI(ListAPIView):
    def get(self, request, **kwargs):
        shape_queryset = PlotableShape.objects.all()

        serializer = ModelVisualShapeSerializer(instance=shape_queryset, many=True)

        response = serializer.data
        return JsonResponse(response, safe=False)
