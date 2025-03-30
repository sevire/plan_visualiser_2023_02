from rest_framework import serializers
from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName


class PlotableShapeSerializer():
    """
    Serializer for PlotableShapeName choices.  Very basic functionality as the data is pre-defined so doesn't
    need validation or any other fancy processing.

    We either want to serialize a specific shape or a list of all shapes.

    I have implemented it in a similar way to the DRF Serializer to allow for future expansion.
    """
    def __init__(self, data: PlotableShapeName=None, many=False):
        """
        If data is populated then we are serializing a specific shape.  Otherwise we are serializing a list of all
        shapes.

        :param shape:
        :param many:
        """

        if data is not None:
            self.data = {
                'id': data.id,
                'value': data.value,
                'label': data.label
            }
        elif many:
            self.data = [{'id': choice.id, 'name': choice.value, 'label': choice.label} for choice in PlotableShapeName]
        else:
            raise ValueError('Either data or many must be populated.')
