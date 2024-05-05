from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.plan.serializer import ModelPlanSerialiser, ModelPlanListSerialiser
from plan_visual_django.models import Plan


class ModelPlanListAPI(ListAPIView):
    def get(self, request, **kwargs):
        # ToDo: Need to adjust to only return plans for current user
        plans_queryset = Plan.objects.all()
        serializer = ModelPlanListSerialiser(plans_queryset, many=True)

        response = serializer.data
        
        return JsonResponse(response, safe=False)


class ModelPlanAPI(APIView):
    def get(self, request, plan_id):
        plan_queryset = Plan.objects.get(pk=plan_id)
        serializer = ModelPlanSerialiser(plan_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)



