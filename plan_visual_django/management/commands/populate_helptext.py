import json
from django.core.management.base import BaseCommand, CommandError
from plan_visual_django.services.initialisation.add_help_text_service import populate_help_text_fields


class Command(BaseCommand):
    help = "Pre-populate the HelpText model with predefined help text data"

    def add_arguments(self, parser):
        # Add an argument to specify the path to the fixture file
        parser.add_argument(
            "fixture_file",
            type=str,
            help="Path to the JSON fixture file containing help text data",
        )

    def handle(self, *args, **options):
        # Get the fixture file path from command-line arguments
        fixture_file = options["fixture_file"]

        try:
            populate_help_text_fields(fixture_file=fixture_file)

        except FileNotFoundError:
            message = f"File not found: {fixture_file}"
            print(message)
            raise CommandError(message)

        except json.JSONDecodeError:
            message = f"Invalid JSON format in file: {fixture_file}"
            print(message)
            raise CommandError(message)

        except Exception as e:
            message = f"Error adding HelpText {slug}: {e}"
            print(message)
            raise CommandError(message)

