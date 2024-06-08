from rest_framework.serializers import ModelSerializer
from plan_visual_django.models import PlotableShape


class ModelVisualShapeSerializer(ModelSerializer):
    class Meta:
        model = PlotableShape
        fields = "__all__"
        depth= 2

