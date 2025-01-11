from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


from django.test import TestCase
from django.urls import reverse


from django.test import TestCase
from django.urls import reverse


class TestAnonymousUser(TestCase):
    def setUp(self):
        """Define common test cases for anonymous users."""
        self.test_cases = [
            # Public pages (accessible)
            {"name": "Add Plan", "view": "add-plan", "requires_login": False, "expected_status": 200},
            {"name": "Manage Plans", "view": "manage-plans", "requires_login": False, "expected_status": 200},
            {"name": "Login Page", "view": "login", "requires_login": False, "expected_status": 200},
            {"name": "Registration Page", "view": "register", "requires_login": False, "expected_status": 200},

            # Restricted pages (should redirect)
            {"name": "Manage Visuals", "view": "manage-visuals", "params": {"plan_id": 1}, "requires_login": True},
            {"name": "Add Visual", "view": "add-visual", "params": {"plan_id": 1}, "requires_login": True},
            {"name": "Logout", "view": "logout", "requires_login": False, "expected_status": 200, "method": "post"},

            # Admin panel (should redirect to admin login)
            {"name": "Django Admin", "view": "admin:index", "requires_login": True, "expected_redirect": "admin:login"},
        ]

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
