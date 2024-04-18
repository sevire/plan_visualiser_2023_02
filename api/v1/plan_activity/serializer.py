from rest_framework import serializers
from plan_visual_django.models import PlanActivity


class PlanActivityListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = PlanActivity
        fields = "__all__"

