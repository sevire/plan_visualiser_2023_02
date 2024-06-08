from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import PlotableStyle


class ModelVisualStyleSerializer(ModelSerializer):
    class Meta:
        model = PlotableStyle
        fields = "__all__"
        depth= 2

