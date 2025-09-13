from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.v1.model.visual.plotable_shape.serializer import PlotableShapeSerializer


class ModelVisualShapeAPI(ListAPIView):
    def get(self, request, **kwargs):

        serializer = PlotableShapeSerializer(many=True)

        response = serializer.data
        return Response(response)
