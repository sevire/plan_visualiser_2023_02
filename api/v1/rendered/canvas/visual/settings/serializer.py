from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import PlanVisual


class RenderCanvasVisualSerialiser(ModelSerializer):
    class Meta:
        model = PlanVisual
        fields = "__all__"
        depth = 2


class ModelVisualSerialiser(ModelSerializer):
    class Meta:
        model = PlanVisual
        fields = "__all__"
        depth = 2
