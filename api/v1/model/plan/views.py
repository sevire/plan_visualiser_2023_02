from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.model.plan.serializer import ModelPlanSerialiser, ModelPlanListSerialiser
from plan_visual_django.models import Plan, PlanVisual


class ModelPlanListAPI(APIView):
    def get(self, request, **kwargs):
        # ToDo: Need to adjust to only return plans for current user
        plans_queryset = Plan.objects.all()
        serializer = ModelPlanListSerialiser(plans_queryset, many=True)

        response = serializer.data
        
        return Response(response)


class ModelPlanAPI(APIView):
    @staticmethod
    def get(request, id):
        plan_queryset = Plan.objects.get(pk=id)
        serializer = ModelPlanSerialiser(plan_queryset)

        response = serializer.data

        return Response(response)



