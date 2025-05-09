from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase, override_settings
from django.template.loader import get_template, TemplateDoesNotExist

class TestTemplates(TestCase):
    """
    Checks that templates can handle various context variables correctly.
    """

    def test_template_with_provided_context(self):
        """
        Test that the login template renders correctly with specified context variables.
        """
        # Define the context variables you want to pass
        context = {
            "primary_heading": "Login Page",
            "secondary_heading": "Welcome back!",
        }

        try:
            # Load the template
            template = get_template('registration/login.html')

            # Render the template with the context
            rendered_template = template.render(context)

            # Assert that the template renders without raising exceptions
            self.assertTrue(rendered_template.strip())  # Ensures something was rendered

            # Optionally check for specific elements in the rendered template
            self.assertIn("Login Page", rendered_template)
            self.assertIn("Welcome back!", rendered_template)

        except TemplateDoesNotExist:
            self.fail("Template 'registration/login.html' does not exist.")
        except TemplateSyntaxError as e:
            self.fail(f"Template rendering raised a syntax error: {e}")

    def test_template_with_missing_context(self):
        """
        Test that the login template renders even with missing context variables.
        """
        # Define a partial or empty context
        context = {}

        try:
            # Load the template
            template = get_template('registration/login.html')

            # Render the template with the partial/empty context
            rendered_template = template.render(context)

            # Assert that the template renders without raising exceptions
            self.assertTrue(rendered_template.strip())  # Ensures something was rendered

            # Optionally check for default behaviors in the absence of specific variables
            self.assertNotIn("Login Page", rendered_template)
            self.assertNotIn("Welcome back!", rendered_template)

        except TemplateDoesNotExist:
            self.fail("Template 'registration/login.html' does not exist.")
        except TemplateSyntaxError as e:
            self.fail(f"Template rendering raised a syntax error: {e}")