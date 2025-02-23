from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123",
        )
        self.user = user

    def test_login_with_username(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'securepassword123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_email(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser@example.com',
            'password': 'securepassword123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'invaliduser',
            'password': 'wrongpassword',
        })
        with self.subTest("Check response is 200 (rendered template)"):
            self.assertEqual(response.status_code, 200)
        # Check the form in context_data
        form = response.context_data.get("form")
        with self.subTest("Check response context data has form"):
            self.assertIsNotNone(form, "The form was not found in the response context_data.")
        with self.subTest("Check that the form has errors"):
            self.assertTrue(form.errors, "The form should have errors for invalid login.")
        message = form.errors.get("__all__")
        with self.subTest("Check that the error in the form is general (under __all__), not related to a field"):
            self.assertIsNotNone(message, "Error message should under '__all__' field")
        with self.subTest("Check that the message is correct"):
            self.assertEqual(message[0], "Please enter a correct username and password. Note that both fields may be case-sensitive.")
