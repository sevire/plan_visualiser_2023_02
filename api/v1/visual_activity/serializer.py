from rest_framework import serializers
from plan_visual_django.models import VisualActivity, PlanVisual


class VisualActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualActivity
        fields = ['visual']