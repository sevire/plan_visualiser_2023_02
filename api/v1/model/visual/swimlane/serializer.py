from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import TimelineForVisual, SwimlaneForVisual


class ModelVisualSwimlaneListSerialiser(ModelSerializer):
    class Meta:
        model = SwimlaneForVisual
        fields = "__all__"
        depth= 2


class ModelVisualSwimlaneSerialiser(ModelSerializer):
    class Meta:
        model = SwimlaneForVisual
        fields = "__all__"
        depth= 2
