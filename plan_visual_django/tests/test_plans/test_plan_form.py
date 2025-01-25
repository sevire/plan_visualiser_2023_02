from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from plan_visual_django.forms import PlanForm
from plan_visual_django.services.auth.user_services import CurrentUser

User = get_user_model()


class TestYourModelForm(TestCase):
    def setUp(self) -> None:
        self.logged_in_user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword')

        # Create request with our test user
        self.request = RequestFactory().get('/')
        self.request.user = self.logged_in_user

    def test_form_default_values(self):
        form = PlanForm(request=self.request)

        # Your 'expected' values based on those you have given as defaults in form
        expected_form_defaults = {
            'plan_name': 'Plan-testuser-001',
        }

        for field_name, expected_default_value in expected_form_defaults.items():
            self.assertEqual(expected_default_value, form.fields[field_name].initial)