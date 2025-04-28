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

    def to_representation(self, instance):
        """
        Add visual_height field calculated from get_visual_dimensions method.
        """
        # Get the base representation from the parent class
        representation = super().to_representation(instance)

        # Get dimensions and extract height (index 3)
        _, _, _, height, _, _ = instance.get_visual_dimensions()

        # Add visual_height to the representation
        representation['visual_height'] = height

        return representation
