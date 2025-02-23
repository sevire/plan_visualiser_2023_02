from django.test import TestCase
from django.contrib.auth import get_user_model
from plan_visual_django.forms import CustomUserCreationForm

User = get_user_model()


class RegistrationFormTest(TestCase):
    def setUp(self):
        # Create an existing user for duplicate tests
        self.existing_user = User.objects.create_user(
            username="existinguser", email="existing@example.com", password="testpass123"
        )

    def test_registration_form(self):
        # Define test cases as a list of dictionaries
        test_cases = [
            {
                "description": "Valid username and email",
                "data": {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password1": "securepass123",
                    "password2": "securepass123",
                },
                "valid": True,
                "check_fields": ["username", "email"],
            },
            {
                "description": "Valid username only",
                "data": {
                    "username": "usernameonly",
                    "password1": "securepass123",
                    "password2": "securepass123",
                },
                "valid": True,
                "check_fields": ["username"],
            },
            {
                "description": "Valid email only (username auto-generated)",
                "data": {
                    "email": "emailonly@example.com",
                    "password1": "securepass123",
                    "password2": "securepass123",
                },
                "valid": True,
                "check_fields": ["username", "email"],
            },
            {
                "description": "Duplicate email",
                "data": {
                    "username": "newuser",
                    "email": "existing@example.com",
                    "password1": "securepass123",
                    "password2": "securepass123",
                },
                "valid": False,
                "error_field": "email",
            },
            {
                "description": "Password mismatch",
                "data": {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password1": "securepass123",
                    "password2": "wrongpass123",
                },
                "valid": False,
                "error_field": "password2",
            },
        ]

        for case in test_cases:
            form = CustomUserCreationForm(data=case["data"])

            # Assert whether the form is valid
            with self.subTest(msg=f"{case['description']} - form validity"):
                self.assertEqual(form.is_valid(), case["valid"])

            if case["valid"]:
                user = form.save()

                # Check each field specified in check_fields
                for field in case["check_fields"]:
                    with self.subTest(msg=f"{case['description']} - check {field}"):
                        self.assertEqual(getattr(user, field), case["data"].get(field, user.username))
            else:
                # Check the error field for invalid cases
                with self.subTest(msg=f"{case['description']} - check error field"):
                    self.assertIn(case["error_field"], form.errors)