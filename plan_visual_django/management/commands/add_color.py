from django.core.management import BaseCommand
from plan_visual_django.models import Color


class Command(BaseCommand):
    help = "Quick way of adding colours to the app."

    def add_arguments(self, parser):
        parser.add_argument("name", type=str)
        parser.add_argument("red", type=int)
        parser.add_argument("green", type=int)
        parser.add_argument("blue", type=int)

    def handle(self, name, red, green, blue, **kwargs):
        """
        Creates a record on the Color table for supplied RGB parameters.

        :param name:
        :param red:
        :param green:
        :param blue:
        :return:
        """
        Color.objects.create(name=name, red=red, green=green, blue=blue, alpha=1)