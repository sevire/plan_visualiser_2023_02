from django.contrib.auth.models import User
from django.test import TestCase
from plan_visual_django.forms import RegistrationForm


class TestDefaultUserRegistration(TestCase):
    def test_register_valid(self):
        response = self.client.post('/register/', {  # Assuming you implement a register view
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        })
        with self.subTest('Response'):
            self.assertEqual(response.status_code, 302)
        with self.subTest('Username'):
            self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_registration_form_invalid(self):
        """Test various validation scenarios for the registration form."""

        test_cases = [
            {
                "name": "Missing Username",
                "data": {
                    "username": "",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                },
                "error_field": "username",
                "expected_error": "This field is required.",
            },
            {
                "name": "Missing Password",
                "data": {
                    "username": "testuser",
                    "password1": "",
                    "password2": "",
                },
                "error_field": "password1",
                "expected_error": "This field is required.",
            },
            {
                "name": "Mismatched Passwords",
                "data": {
                    "username": "testuser",
                    "password1": "SecurePass123!",
                    "password2": "DifferentPass123!",
                },
                "error_field": "password2",
                "expected_error": "The two password fields didn’t match.",
            },
            {
                "name": "Weak Password (Too Short)",
                "data": {
                    "username": "testuser",
                    "password1": "123",
                    "password2": "123",
                },
                "error_field": "password2",
                "expected_error": 'This password is too short. It must contain at least 8 characters.',
            },
            {
                "name": "Invalid Email Format",
                "data": {
                    "username": "testuser",
                    "email": "invalid-email",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                },
                "error_field": "email",
                "expected_error": "Enter a valid email address.",
            },
            {
                "name": "Username with Special Characters",
                "data": {
                    "username": "invalid@user!",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                },
                "error_field": "username",
                "expected_error": "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.",
            },
        ]

        for case in test_cases:
            form = RegistrationForm(data=case["data"])

            with self.subTest(msg=f"{case['name']} - Form should be invalid"):
                self.assertFalse(form.is_valid())

            with self.subTest(msg=f"{case['name']} - Error field should exist"):
                self.assertIn(case["error_field"], form.errors)

            with self.subTest(msg=f"{case['name']} - Error message should be correct"):
                self.assertIn(case["expected_error"], form.errors[case["error_field"]])
