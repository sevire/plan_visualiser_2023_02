from io import StringIO

from django.apps import apps
from django.core.management import BaseCommand, call_command
from django.db import connection



class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Executes the built in management command sqlsequencereset which generates the SQL statements for the configured
        database to reset the pks for all tables to be higher than all the manually added records to avoid breaking the
        UNIQUE constraint when adding future records without explicit pks.

        Then executes those SQL statements.

        :param args:
        :param options:
        :return:
        """
        commands = StringIO()
        cursor = connection.cursor()

        # We have added hard-coded pk for main app and also user app, so need to reset pks for each.
        for app_label in {"plan_visual_django", "auth"}:
            call_command('sqlsequencereset', app_label, stdout=commands, no_color=True)

        print(commands.getvalue())
        cursor.execute(commands.getvalue())