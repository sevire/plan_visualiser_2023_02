from django.test import TestCase, Client
from django.urls import reverse


class TestAdminAccess(TestCase):
    def setUp(self):
        # Create a client to simulate a browser
        self.client = Client()

    def test_redirect_to_admin_login(self):
        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(response, '/admin/login/?next=/admin/')