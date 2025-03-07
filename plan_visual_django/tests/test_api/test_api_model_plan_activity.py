import os
from django.test import TestCase
from ddt import ddt, data, unpack
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder
from plan_visual_django.tests.resources.utilities import generate_test_data_field_stream_multiple_inputs
from plan_visual_django.tests.resources.utilities import extract_object_from_list_by_field


@ddt
class TestApiModelPlanActivity(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
    ]

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("status", "activity_name", "start_date", "end_date"),
        test_data=[
            # plan_id, sticky_id, activity_name, top
            (2, "ID-026", False, 200, "Project Start", "2023-09-01", "2023-09-01"),
        ]
    ))
    @unpack
    def test_get_plan_activity_list(self, plan_id, sticky_id, approx_flag, field_name, expected_field_value):
        response = self.client.get(f"/api/v1/model/plans/activities/{plan_id}/")

        if field_name in {"status"}:
            actual_value = response.status_code
        else:
            activity_dict_list = response.json()
            activity_dict = extract_object_from_list_by_field(activity_dict_list, value_to_test=sticky_id, field_name="unique_sticky_activity_id")

            if field_name in {"activity_name", "vertical_positioning_value", "height_in_tracks", "start_date", "end_date"}:
                actual_value = activity_dict[field_name]
            else:
                self.fail(f"Unexpected field name {field_name}")

        if approx_flag:
            self.assertAlmostEqual(expected_field_value, actual_value)
        else:
            self.assertEqual(expected_field_value, actual_value)
