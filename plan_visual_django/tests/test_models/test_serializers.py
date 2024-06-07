import os

from django.test import TestCase
from api.v1.model.visual.activity.serializer import ModelVisualActivitySerialiser, \
    ModelVisualActivitySerialiserForUpdate
from plan_visual_django.models import VisualActivity
from resources.test_configuration import test_data_base_folder, test_fixtures_folder


class TestSerializers(TestCase):
    """
    Tests for correct translation to and from table entries. Mostly to test for unusual scenarios
    such as updating swimlane for a visual activity based on swimlane name rather than id.
    """

    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]
    def test_update_swimlane(self):
        """
        Tests updating of foreign key to swimlane within a VisualActivity object.
        :return:
        """
        activity_instance = VisualActivity.objects.get(pk=1)

        # Temp to check things are as I expect before testing changes
        self.assertEqual(4, activity_instance.swimlane_id)
        self.assertEqual(5, activity_instance.vertical_positioning_value)

        activity_update_data = {
            'id': 1,
            'swimlane': 5,
            'vertical_positioning_value': 4
        }

        serializer = ModelVisualActivitySerialiserForUpdate(activity_instance, data=activity_update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        # Now check that record has been changed to point to new swimlane
        activity_instance = VisualActivity.objects.get(pk=1)

        # Temp to check things are as I expect before testing changes
        self.assertEqual(5, activity_instance.swimlane_id)
