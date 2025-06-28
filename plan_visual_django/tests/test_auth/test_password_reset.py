from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model

class PasswordResetTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user('foo', 'app_user_01@genonline.co.uk', 'pass')

    def test_reset_email(self):
        response = self.client.post('/accounts/password_reset/', {
            'email': 'app_user_01@genonline.co.uk'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)