from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        with self.subTest("Checking username correct"):
            self.assertEqual(user.username, "testuser")
        with self.subTest("Checking email correct"):
            self.assertEqual(user.email, "test@example.com")
        with self.subTest("Checking password authenticates"):
            self.assertTrue(user.check_password("testpass123"))