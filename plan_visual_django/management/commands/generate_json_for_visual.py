from io import StringIO
from django.core.management import BaseCommand, call_command
from django.db import connection

from plan_visual_django.models import PlanVisual


class Command(BaseCommand):
    help = "Add set of common data items required by all users."

    def add_arguments(self, parser):
        parser.add_argument("visual_id", type=int)

    def handle(self, visual_id, *args, **options):
        """
        Generates a single JSON file which contains all the data items required to drive the front end for
        laying out the visual.  This is mainly to support the re-design of the front end, which is taking place
        in WebStorm.

        The file will be used as a proxy database by the prototype being developed, to remove the need to connect
        the back end while we want to focus on building the front end.

        :param args:
        :param options:
        :return:
        """
        visual = PlanVisual.objects.get(id=visual_id)