from django.core.management.base import BaseCommand
from plan_visual_django.services.app_status.service_list_visuals import service_list_visuals
from plan_visual_django.services.general.text_formatting import print_formatted_dict_list, print_banner


class Command(BaseCommand):
    help = "Lists all users, their plans, and visuals for each plan"

    def handle(self, *args, **kwargs):
        visual_data = service_list_visuals()

        print_banner("All visuals, by user and plan name", 40, "*")

        print_formatted_dict_list(visual_data)
