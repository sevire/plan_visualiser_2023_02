from rest_framework import serializers
from plan_visual_django.models import PlanActivity, PlanVisual


class PlanVisualSerialiser(serializers.ModelSerializer):
    class Meta:
        model = PlanVisual
        fields = "__all__"

