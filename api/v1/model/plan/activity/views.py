from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.plan.activity.serializer import ModelPlanActivityListSerialiser, ModelPlanActivitySerialiser
from plan_visual_django.models import Plan


class ModelPlanActivityListAPI(ListAPIView):
    def get(self, request, plan_id=None, **kwargs):
        plan = Plan.objects.get(id=plan_id)

        plan_activities_queryset = plan.planactivity_set.all()
        serializer = ModelPlanActivityListSerialiser(plan_activities_queryset, many=True)

        return JsonResponse(serializer.data, safe=False)


class ModelPlanActivityAPI(APIView):
    def get(self, request, plan_id, unique_id):
        # ToDo: Is it right to go Plan --> Plan.activity_set or just do in one get
        plan = Plan.objects.get(id=plan_id)
        plan_activity_queryset = plan.planactivity_set.get(unique_sticky_activity_id=unique_id)

        serializer = ModelPlanActivitySerialiser(instance=plan_activity_queryset)

        response = serializer.data
        return JsonResponse(response, safe=False)
