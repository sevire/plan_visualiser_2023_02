"""
Test related to management of styles for plotable objects.
"""
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder

User = get_user_model()

class TestApiPlotableStyles(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json')
    ]

    def test_get_plotable_styles_for_normal_user(self):
        """
        When plotable styles are requested, the response will depend upon which user is logged on.
        - If it's a normal user then they will get plotable styles for that user and also for the shared
          data user.
        - If it's an admin user then the response will be all plotable styles.

        This test is just for normal users.
        :return:
        """
        user_name = "app_user_01"
        user = User.objects.get(username=user_name)
        self.client.force_login(user=user)

        expected_plotable_styles = [
            "[01]Milestone Default 1",
            "[02]Milestone Default 2",
            "[03]Activity Default 1",
            "[04]Activity Default 2",
            "[05]Swimlane-odd Default 1",
            "[06]Swimlane-even Default 1",
            "app_user_style_01",
            "app_user_style_02",
        ]

        base_url = "/api/v1"
        url = base_url + "/model/visuals/styles/"

        response = self.client.get(url)
        json_response = response.json()
        returned_api_plotable_style_names = [style["style_name"] for style in json_response]
        with self.subTest(num_styles=6):
            self.assertEqual(8, len(returned_api_plotable_style_names))

        for expected_plotable_style in expected_plotable_styles:
            with self.subTest(expected_plotable_style=expected_plotable_style):
                self.assertIn(expected_plotable_style, returned_api_plotable_style_names)

