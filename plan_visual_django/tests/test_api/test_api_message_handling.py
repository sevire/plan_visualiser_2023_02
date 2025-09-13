"""
Test functionality which adds messages from the session to the DRF response header.
"""
import os

from django.test import TestCase
from plan_visual_django.tests.resources.unit_test_configuration import test_data_base_folder, test_fixtures_folder


class TestApiMessagesToHeader(TestCase):
    """
    Just tests one of the api end points (for now) as functionality is common to all views
    which use the MessagesToHeaderMixin.
    """
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
    ]

    def test_message_draining(self):
        response = self.client.get(f"/api/v1/model/plans/activities/2/")

        # There should be a success message in the response header
        self.assertEqual(response.status_code, 200)
        self.assertIn("x-server-messages", response.headers)


