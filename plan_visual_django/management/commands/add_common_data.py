from django.core.management import BaseCommand
from plan_visual_django.services.initialisation.db_initialisation import create_initial_users, add_initial_data


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

        if delete is True:
            add_initial_data(None, delete)
            create_initial_users(delete=True)
        else:
            user = create_initial_users(delete=False)
            add_initial_data(user, delete)
