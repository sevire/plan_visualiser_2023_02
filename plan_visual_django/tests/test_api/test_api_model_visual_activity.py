import json
import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.tests.resources.test_configuration import test_fixtures_folder, test_data_base_folder
from resources.utilities import generate_test_data_field_stream_multiple_inputs


@ddt
class TestApiModelVisualActivity(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json')
    ]

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("status", "text", "top", "left", "width", "height"),
        test_data=[
            # visual_id, sticky_id, activity_name, top
            (4, "ID-025", False, 200, "Milestone 6", 40 + 5*20+4*4 + 5, (214.5/275)*1000-5, 10, 20),
            (4, "ID-026", False, 200, "Project Start", 40+4*(20+4), (62.5/275)*1000-5, 10, 20),
            (4, "ID-024", True, 200, "Activity 24", 40 + 5*20 + 4*4 + 5 + 9*(20 + 4), (31 + 31 + 30 + 31 + 30 + 31 + 17) / 275 * 1000, (31 - 18 + 1) * 1000 / 275, 44),
        ]
    ))
    @unpack
    def test_get_visual_activity(self, visual_id, sticky_id, approx_flag, field_name, expected_field_value):
        """
        Just check that test data from fixtures has been correctly placed in database.
        :return:
        """
        response = self.client.get(f"/api/v1/rendered/canvas/visuals/activities/{visual_id}/{sticky_id}/")
        if field_name in {"status"}:
            actual_value = response.status_code
        else:
            json_response = response.json()
            content_list_of_dicts = json_response['activities']
            if field_name in {"text"}:
                list_item_to_check = content_list_of_dicts[1]
                actual_value = list_item_to_check[field_name]
            elif field_name in {"top", "left", "width", "height"}:
                list_item_to_check = content_list_of_dicts[0]
                actual_value = list_item_to_check['shape_plot_dims'][field_name]
            else:
                self.fail(f"Unexpected field name {field_name}")

        if approx_flag:
            self.assertAlmostEqual(expected_field_value, actual_value)
        else:
            self.assertEqual(expected_field_value, actual_value)



    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("status", "text", "top", "left", "width", "height"),
        test_data=[
            # visual_id, sticky_id, activity_name, top
            (4, 1, "ID-026", False, 200, "Project Start", 40+4*(20+4), (62.5/275)*1000-5, 10, 20),
            (4, 2, "ID-025", False, 200, "Milestone 6", 40 + 5*20+4*4 + 5, (214.5/275)*1000-5, 10, 20),
            (4, 3, "ID-024", True, 200, "Activity 24", 40 + 5*20 + 4*4 + 5 + 9*(20 + 4), (31 + 31 + 30 + 31 + 30 + 31 + 17) / 275 * 1000, (31 - 18 + 1) * 1000 / 275, 44),
        ]
    ))
    @unpack
    def test_get_visual_activities(self, visual_id, response_entry_seq_num, sticky_id, approx_flag, field_name, expected_field_value):
        response = self.client.get(f"/api/v1/rendered/canvas/visuals/activities/{visual_id}/")
        if field_name in {"status"}:
            actual_value = response.status_code
        else:
            json_response = response.json()
            content_list_of_dicts = json_response['activities']
            if field_name in {"text"}:
                list_item_to_check = content_list_of_dicts[(response_entry_seq_num-1)*2+1]
                actual_value = list_item_to_check[field_name]
            elif field_name in {"top", "left", "width", "height"}:
                list_item_to_check = content_list_of_dicts[(response_entry_seq_num-1)*2]
                actual_value = list_item_to_check['shape_plot_dims'][field_name]
            else:
                self.fail(f"Unexpected field name {field_name}")

        if approx_flag:
            self.assertAlmostEqual(expected_field_value, actual_value)
        else:
            self.assertEqual(expected_field_value, actual_value)

