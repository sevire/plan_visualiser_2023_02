from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import PlanActivity, Plan


class ModelPlanListSerialiser(ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        depth = 2



class ModelPlanSerialiser(ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        depth = 1
