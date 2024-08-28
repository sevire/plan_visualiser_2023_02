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


class ModelVisualActivitySerialiserForUpdate(ModelVisualActivitySerialiser):
    """
    Not 100% sure whether this is right or good practice.  When updating the activity I don't want the depth=2
    because I am not trying to update the value of any related records through this API call.  I will simply
    update the foreign key reference (e.g. the change the swimlane).

    So this is a copy of the ModelVisualActivitySerialiser simply with depth = 1
    """
    class Meta:
        model = VisualActivity
        fields = "__all__"

