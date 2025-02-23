# plan_visual_django/management/commands/export_helptext.py
from django.core.management.base import BaseCommand
from plan_visual_django.models import HelpText


class Command(BaseCommand):
    help = "Export all HelpText records as add_helptext commands for creating them in a new environment."

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file',
            type=str,
            help="Specify a file to write the output to. If not provided, the commands will be printed to the console."
        )

    def handle(self, *args, **options):
        # Fetch all HelpText records
        help_texts = HelpText.objects.all()

        # Prepare the commands
        commands = []
        for help_text in help_texts:
            # Escape all newline characters as \\n
            escaped_content = help_text.content.replace('\n', '\\n')
            command = f'python manage.py add_helptext "{help_text.slug}" "{help_text.title}" "{escaped_content}"'
            commands.append(command)

        # Output the commands
        output_file = options.get('output_file')
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write('\n'.join(commands))
                self.stdout.write(self.style.SUCCESS(f"HelpText export completed. Saved to '{output_file}'."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error writing to file: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("HelpText export completed. Commands:"))
            for command in commands:
                self.stdout.write(command)
