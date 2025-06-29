from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from plan_visual_django.models import Plan, CustomUser
from plan_visual_django.services.app_status.service_list_plans import service_list_plans
from plan_visual_django.services.general.text_formatting import print_banner, print_formatted_dict_list


class Command(BaseCommand):
    help = "Lists all users and their uploaded plans"

    def handle(self, *args, **kwargs):
        plan_data = service_list_plans()

        print_banner("All plans by user", 40, "*")
        print_formatted_dict_list(plan_data)
