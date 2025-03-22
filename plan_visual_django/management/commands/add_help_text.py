# myapp/management/commands/add_helptext.py
from django.core.management.base import BaseCommand, CommandError
from plan_visual_django.models import HelpText
from plan_visual_django.services.initialisation.add_help_text_service import add_help_text_service


class Command(BaseCommand):
    help = "Add a new HelpText record to the database. Use '--overwrite' to update an existing record."

    def add_arguments(self, parser):
        # Define arguments for slug, title, and content
        parser.add_argument('slug', type=str, help="The unique slug identifier for the HelpText record")
        parser.add_argument('title', type=str, help="The title of the HelpText")
        parser.add_argument('content', type=str,
                            help="The text content of the HelpText. Use '\\n' to represent newlines.")
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help="Overwrite the HelpText record if the slug already exists."
        )

    def handle(self, *args, **options):
        # Extract options
        slug = options['slug']
        title = options['title']
        content = options['content'].replace("\\n", "\n")  # Replace \n with actual newline
        overwrite = options['overwrite']  # Check if overwrite flag is provided

        try:
            add_help_text_service(slug, title, content, overwrite)

        except Exception as e:
            raise CommandError(f"An error occurred while saving HelpText: {e}")
