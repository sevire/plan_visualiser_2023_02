from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.model.visual.serializer import ModelVisualListSerialiser
from api.v1.rendered.canvas.visual.settings.serializer import ModelVisualSerialiser
from plan_visual_django.models import Plan, PlanVisual


class ModelVisualListAPI(ListAPIView):
    def get(self, request, plan_id=None, **kwargs):
        visuals_queryset = Plan.objects.get(id=plan_id).planvisual_set.all()
        serializer = ModelVisualListSerialiser(instance=visuals_queryset, many=True)

        response = serializer.data

        return Response(response)


class ModelVisualAPI(APIView):
    @staticmethod
    def get(request, visual_id):
        visual_queryset = PlanVisual.objects.get(id=visual_id)
        serializer = ModelVisualSerialiser(instance=visual_queryset)

        response = serializer.data

        return Response(response)




