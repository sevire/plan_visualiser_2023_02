from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.visual.serializer import ModelVisualListSerialiser
from api.v1.rendered.canvas.visual.settings.serializer import ModelVisualSerialiser
from plan_visual_django.models import Plan


class ModelVisualListAPI(ListAPIView):
    def get(self, request, plan_id=None, **kwargs):
        visuals_queryset = Plan.objects.get(id=plan_id).planvisual_set.all()
        serializer = ModelVisualListSerialiser(instance=visuals_queryset, many=True)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualAPI(APIView):
    def get(self, request, plan_id, visual_id):
        # ToDo: Not sure if this is right - I don't really need plan_id as visual_id is a PK
        visual_queryset = Plan.objects.get(id=plan_id).planvisual_set.get(pk=visual_id)
        serializer = ModelVisualSerialiser(instance=visual_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)




