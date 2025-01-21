from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase

User = get_user_model()


class UserLoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='securepassword')

    def test_login_success(self):
        # Perform login
        response = self.client.post('/accounts/login/', {'username': 'testuser', 'password': 'securepassword'}, follow=False)

        # Check session authentication
        user_id = self.client.session.get('_auth_user_id')
        with self.subTest("Check user_id not None"):
            self.assertIsNotNone(user_id)
        with self.subTest("Check user_id is correct value"):
            self.assertEqual(int(user_id), self.user.id)

    def test_login_without_username(self):
        """
        Test that login fails when the username is missing
        and that the appropriate error message is displayed.
        """
        form_data = {'username': '', 'password': 'securepassword'}
        form = AuthenticationForm(data=form_data)

        # Check that the form is invalid
        with self.subTest("Check form invalid"):
            self.assertFalse(form.is_valid())

        # Check that there is an error on the 'username' field
        with self.subTest("Check that username is invalid field"):
            self.assertIn('username', form.errors)

        # Check the specific error message (Django's built-in message for missing username)
        with self.subTest("Check that error message is as expected"):
            expected_error = "This field is required."
            self.assertIn(expected_error, form.errors['username'])

