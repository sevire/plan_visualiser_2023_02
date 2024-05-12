from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import PlanActivity, VisualActivity


class ModelVisualActivityListSerialiser(ModelSerializer):
    class Meta:
        model = VisualActivity
        fields = "__all__"
        depth= 2


class ModelVisualActivitySerialiser(ModelSerializer):
    class Meta:
        model = VisualActivity
        fields = "__all__"
        depth= 2
