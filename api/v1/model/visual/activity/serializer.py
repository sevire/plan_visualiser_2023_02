from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.v1.model.visual.plotable_shape.serializer import PlotableShapeSerializer
from plan_visual_django.models import VisualActivity
from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName


class BaseVisualActivitySerialiser(ModelSerializer):
    """
    A base serializer containing shared logic across all VisualActivity serializers.
    """

    class Meta:
        model = VisualActivity
        fields = "__all__"

    def to_representation(self, instance):
        """
        Custom serialization logic for plotable_shape.
        """
        # Get the base representation from the parent class
        representation = super().to_representation(instance)

        # Get the raw plotable_shape value from the instance
        shape_name = PlotableShapeName.get_by_value(instance.plotable_shape)

        # Map the shape_name to the full Enum details
        representation['plotable_shape'] = PlotableShapeSerializer(shape_name).data

        return representation

    def validate_plotable_shape(self, value):
        """
        Validate the incoming string to ensure it's a valid Enum member.
        """
        normalized_value = value.upper()  # Normalize to uppercase to match Enum names
        if normalized_value not in PlotableShapeName.values():
            raise serializers.ValidationError(f"Invalid shape name: {value}")
        return normalized_value  # Return the validated string as is


class ModelVisualActivityListSerialiser(BaseVisualActivitySerialiser):
    """
    Serializer for listing VisualActivity with detailed relationships (depth=2).
    """

    class Meta(BaseVisualActivitySerialiser.Meta):
        depth = 2


class ModelVisualActivitySerialiser(BaseVisualActivitySerialiser):
    """
    Serializer for retrieving a single VisualActivity with detailed relationships (depth=2).
    """

    class Meta(BaseVisualActivitySerialiser.Meta):
        depth = 2


class ModelVisualActivitySerialiserForUpdate(BaseVisualActivitySerialiser):
    """
    Serializer for updating VisualActivity, with simplified relationships (depth=1).
    """

    class Meta(BaseVisualActivitySerialiser.Meta):
        pass
#
#
#
# class ModelVisualActivityListSerialiser(ModelSerializer):
#
#     class Meta:
#         model = VisualActivity
#         fields = "__all__"
#         depth= 2
#
#     def to_representation(self, instance):
#         """
#         Custom serialization logic for plotable_shape.
#         """
#         # Get the base representation from the parent class
#         representation = super().to_representation(instance)
#
#         # Get the raw plotable_shape value from the instance
#         shape_name = instance.plotable_shape
#
#         # Map the shape_name to the full Enum details
#         if shape_name in PlotableShapeName.__members__:
#             shape_enum = PlotableShapeName[shape_name]
#             representation["plotable_shape"] = {
#                 "name": shape_enum.name,
#                 "value": shape_enum.value,
#                 "description": getattr(shape_enum, "description", None),  # Optional field
#             }
#
#         return representation
#
#     # def get_plotable_shape(self, obj):
#     #     shape = PlotableShapeName.get_by_value(obj.plotable_shape)
#     #     return PlotableShapeSerializer(shape).data
#
# class ModelVisualActivitySerialiser(ModelSerializer):
#
#     class Meta:
#         model = VisualActivity
#         fields = "__all__"
#         depth= 2
#
#     def to_representation(self, instance):
#         """
#         Custom serialization logic for plotable_shape.
#         """
#         # Get the base representation from the parent class
#         representation = super().to_representation(instance)
#
#         # Get the raw plotable_shape value from the instance
#         shape_name = instance.plotable_shape
#
#         # Map the shape_name to the full Enum details
#         if shape_name in PlotableShapeName.__members__:
#             shape_enum = PlotableShapeName[shape_name]
#             representation["plotable_shape"] = {
#                 "name": shape_enum.name,
#                 "value": shape_enum.value,
#                 "description": getattr(shape_enum, "description", None),  # Optional field
#             }
#
#         return representation
#
#
#     # def get_plotable_shape(self, obj):
#     #     shape = PlotableShapeName.get_by_value(obj.plotable_shape)
#     #     return PlotableShapeSerializer(shape).data
#
# class ModelVisualActivitySerialiserForUpdate(ModelVisualActivitySerialiser):
#     """
#     Not 100% sure whether this is right or good practice.  When updating the activity I don't want the depth=2
#     because I am not trying to update the value of any related records through this API call.  I will simply
#     update the foreign key reference (e.g. the change the swimlane).
#
#     So this is a copy of the ModelVisualActivitySerialiser simply with depth = 1
#     """
#     class Meta:
#         model = VisualActivity
#         fields = "__all__"
#
#     def validate_plotable_shape(self, value):
#         """
#         Validate that the incoming value is a valid Enum member.
#         """
#         if value not in PlotableShapeName.__members__:
#             raise serializers.ValidationError(f"Invalid shape name: {value}")
#         return value  # Return the validated string as is
#
