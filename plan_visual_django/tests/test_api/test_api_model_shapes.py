"""
Test related to management of styles for plotable objects.
"""
import os
from django.test import TestCase
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder


class TestApiPlotableShapes(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json')
    ]

    def test_get_plotable_shapes(self):
        """
        Get all plotable shapes for use in the visual.

        :return:
        """

        expected_plotable_shapes = [
            "RECTANGLE",
            "DIAMOND",
        ]

        base_url = "/api/v1"
        url = base_url + "/model/visuals/shapes/"

        response = self.client.get(url)
        json_response = response.json()
        returned_api_plotable_shape_names = [shape["name"] for shape in json_response]
        with self.subTest(num_shapes=2):
            self.assertEqual(2, len(returned_api_plotable_shape_names))

        for expected_plotable_style in expected_plotable_shapes:
            with self.subTest(expected_plotable_style=expected_plotable_style):
                self.assertIn(expected_plotable_style, returned_api_plotable_shape_names)

