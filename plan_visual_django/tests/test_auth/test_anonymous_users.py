import os

from django.test import TestCase
from django.urls import reverse
from plan_visual_django.models import Plan
from plan_visual_django.tests.resources.unit_test_configuration import test_data_base_folder, test_fixtures_folder


class TestAnonymousUser(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'color_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'plotablestyle_fixtures.json')
    ]

    def setUp(self):
        """
        Define common test cases for anonymous users.
        """
        self.test_cases = [
            # Public pages (accessible)
            {"name": "Add Plan", "view": "add-plan", "requires_login": False, "expected_status": 200},
            {"name": "Manage Plans", "view": "manage-plans", "requires_login": False, "expected_status": 200},
            {"name": "Login Page", "view": "login", "requires_login": False, "expected_status": 200},
            {"name": "Registration Page", "view": "register", "requires_login": False, "expected_status": 200},

            # Restricted pages (should redirect)
            {"name": "Manage Visuals", "view": "manage-visuals", "params": {"plan_id": 2}, "requires_login": False, "expected_status": 200},
            {"name": "Add Visual", "view": "add-visual", "params": {"plan_id": 2}, "requires_login": False, "expected_status": 200},
            {"name": "Logout", "view": "logout", "requires_login": False, "expected_status": 200, "method": "post"},
        ]

        # Need to manipulate the Plan record from test fixtures so that it is owned by an Anonymous user in this test session
        plan_record = Plan.objects.get(pk=2)

        # Now set user to None, and session_id to this session.
        plan_record.user = None
        plan_record.session_id = self.client.session.session_key
        plan_record.save()

    def test_anonymous_user_access(self):
        """Test anonymous user access for various pages, handling dynamic URLs."""
        for case in self.test_cases:
            http_method = self.client.post if "method" in case and case["method"] == "post" else self.client.get

            url = reverse(case["view"], kwargs=case.get("params", {}))  # Dynamically inject params
            response = http_method(url)

            with self.subTest(msg=f"Anonymous access: {case['name']} - Response received"):
                self.assertIsNotNone(response)  # Ensure we got a response

            if case.get("requires_login"):
                expected_redirect = f"{reverse('login')}?next={url}"
                with self.subTest(msg=f"Anonymous access: {case['name']} - Should be redirected to login"):
                    self.assertRedirects(response, expected_redirect)

            elif "expected_redirect" in case:
                expected_redirect_url = reverse(case["expected_redirect"])
                with self.subTest(msg=f"Anonymous access: {case['name']} - Should be redirected"):
                    self.assertRedirects(response, expected_redirect_url)

            else:
                with self.subTest(msg=f"Anonymous access: {case['name']} - Should return status {case['expected_status']}"):
                    self.assertEqual(response.status_code, case["expected_status"])
