from rest_framework import serializers
from plan_visual_django.models import VisualActivity, PlanVisual


class VisualActivityListSerialiser(serializers.Serializer):
    class Meta:
        model = VisualActivity
        fields = ['unique_id_from_plan', 'text_flow']
