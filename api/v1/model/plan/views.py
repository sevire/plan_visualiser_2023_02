from django.http import JsonResponse
from rest_framework.views import APIView
from api.v1.model.plan.serializer import PlanActivityListSerialiser
from plan_visual_django.models import Plan


class PlanActivityListAPI(APIView):
    def get(self, request, plan_id):
        plan = Plan.objects.get(id=plan_id)

        plan_activities = plan.planactivity_set.all()
        serializer = PlanActivityListSerialiser(plan_activities, many=True)

        return JsonResponse(serializer.data, safe=False)
