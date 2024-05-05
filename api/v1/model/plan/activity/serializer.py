from rest_framework import serializers
from plan_visual_django.models import PlanActivity


class ModelPlanActivityListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = PlanActivity
        fields = "__all__"


class ModelPlanActivitySerialiser(serializers.ModelSerializer):
    class Meta:
        model = PlanActivity
        fields = "__all__"

