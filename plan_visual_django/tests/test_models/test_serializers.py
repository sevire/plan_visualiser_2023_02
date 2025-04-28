import os

from django.test import TestCase
from api.v1.model.visual.activity.serializer import ModelVisualActivitySerialiser, \
    ModelVisualActivitySerialiserForUpdate
from api.v1.rendered.canvas.visual.settings.serializer import ModelVisualSerialiser
from plan_visual_django.models import VisualActivity, PlanVisual
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder


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

    def test_visual_height_field(self):
        """
        Tests that the ModelVisualSerialiser correctly adds the visual_height field
        calculated from the get_visual_dimensions method.
        """
        # Get a PlanVisual instance
        visual_instance = PlanVisual.objects.first()

        # Mock the get_visual_dimensions method to return a known value
        original_get_visual_dimensions = visual_instance.get_visual_dimensions

        def mock_get_visual_dimensions(*args, **kwargs):
            # Return a tuple with a known height value (index 3)
            return 0, 0, 100, 200, 100, 200

        visual_instance.get_visual_dimensions = mock_get_visual_dimensions

        # Serialize the instance
        serializer = ModelVisualSerialiser(instance=visual_instance)
        data = serializer.data

        # Check that the visual_height field is present and has the expected value
        self.assertIn('visual_height', data)
        self.assertEqual(data['visual_height'], 200)

        # Restore the original method
        visual_instance.get_visual_dimensions = original_get_visual_dimensions
