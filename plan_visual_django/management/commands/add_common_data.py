from django.core.management import BaseCommand
from django.conf import settings
from plan_visual_django.services.initialisation.add_help_text_service import populate_help_text_fields
from plan_visual_django.services.initialisation.db_initialisation import create_initial_users, add_initial_data, \
    set_initial_user_data, initial_users_config


class Command(BaseCommand):
    """
    Add common data items required by all users.  Includes:
    - Field mapping types for each file format
    - Field mapping for each field in each file format
    - Color palette for an initial theme
    - Plotable styles for an initial theme
    """
    help = "Add set of common data items required by all users."

    def add_arguments(self, parser):
        parser.add_argument("--delete", action='store_true')

    def handle(self, *args, **options):
        """
        Creates standard shared data for following:
        - Colors
        - Styles
        - Field mapping types
        - Field mappings
        """
        delete = options['delete']

        # If we are deleting then we delete the shared user after all the other records

        initial_users_data = set_initial_user_data(initial_users_config)
        if delete is True:
            # Add initial data held in fixtures
            add_initial_data(None, delete)
            create_initial_users(initial_users_data, delete=True)

            # NOTE: Don't delete help text data - it's not necessary (I think!)
        else:
            user = create_initial_users(initial_users_data, delete=False)
            add_initial_data(user, delete)

            # Add initial data via service
            populate_help_text_fields(fixture_file="plan_visual_django/fixtures/help_text.json")
