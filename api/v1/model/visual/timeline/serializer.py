from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import TimelineForVisual


class ModelVisualTimelineListSerialiser(ModelSerializer):
    class Meta:
        model = TimelineForVisual
        fields = "__all__"
        depth= 2


class ModelVisualTimelineSerialiser(ModelSerializer):
    class Meta:
        model = TimelineForVisual
        fields = "__all__"
        depth= 2
