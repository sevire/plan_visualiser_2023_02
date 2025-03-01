from ddt import ddt, data, unpack
from django.test import TestCase
import os

from api.v1.model.visual.activity.serializer import ModelVisualActivityListSerialiser
from plan_visual_django.models import PlanVisual
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder
from plan_visual_django.tests.resources.utilities import generate_test_data_field_stream_multiple_inputs


@ddt
class TestApiSerialisers(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("unique_id_from_plan", "swim_lane_name", "vertical_positioning_value", "height_in_tracks"),
        test_data=[
            # visual_id, timeline_seq, timeline_label_seq, approx_flag, top, left, width, height
            (4, 1, True, "ID-026", "Visual 01:01, Swimlane 1", 5, 1),
        ],
    ))
    @unpack
    def test_get_visual_activities_serialiser(self, visual_id, visual_activity_seq, approx_flag, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        visual_activities = visual.visualactivity_set.all()
        serialiser = ModelVisualActivityListSerialiser(visual_activities, many=True)

        serialized_data = serialiser.data

        # Access and check the appropriate field value depending upon which expected field has been passed in.
        visual_activity_to_check = serialized_data[visual_activity_seq-1]
        if field_name in {"unique_id_from_plan", "vertical_positioning_value", "height_in_tracks"}:
            object_to_check = visual_activity_to_check
        elif field_name in {"swim_lane_name"}:
            object_to_check = visual_activity_to_check["swimlane"]

        value_to_check = object_to_check[field_name]
        if approx_flag and not isinstance(value_to_check, str):
            self.assertAlmostEqual(field_value, value_to_check)
        else:
            self.assertEqual(field_value, object_to_check[field_name])
