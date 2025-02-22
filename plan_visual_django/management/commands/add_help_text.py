# myapp/management/commands/add_helptext.py
from django.core.management.base import BaseCommand, CommandError
from plan_visual_django.models import HelpText


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
            # Check if a HelpText record with this slug exists
            help_text = HelpText.objects.filter(slug=slug).first()

            if help_text:
                if overwrite:
                    # Overwrite the record
                    help_text.title = title
                    help_text.content = content
                    help_text.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully overwrote HelpText with slug '{slug}'."))
                else:
                    raise CommandError(
                        f"A HelpText record with slug '{slug}' already exists. Use '--overwrite' to update it."
                    )
            else:
                # Create a new record if the slug does not exist
                HelpText.objects.create(slug=slug, title=title, content=content)
                self.stdout.write(self.style.SUCCESS(f"Successfully added HelpText '{title}' with slug '{slug}'."))

        except Exception as e:
            raise CommandError(f"An error occurred while saving HelpText: {e}")
