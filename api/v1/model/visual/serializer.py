from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import Plan, PlanVisual


class ModelVisualListSerialiser(ModelSerializer):
    class Meta:
        model = PlanVisual
        fields = "__all__"
        depth = 2


class ModelVisualSettingsSerialiser(ModelSerializer):
    class Meta:
        model = PlanVisual
        fields = "__all__"
        depth = 2
