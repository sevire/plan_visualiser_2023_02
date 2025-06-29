from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from plan_visual_django.models import Plan, CustomUser
from plan_visual_django.services.app_status.service_list_plans import service_list_plans


class Command(BaseCommand):
    help = "Lists all users and their uploaded plans"

    def handle(self, *args, **kwargs):


        plan_data = service_list_plans()
        for plan_record in plan_data:
            self.stdout.write(f" - {plan_record['user']}: {plan_record['plan_name']}")

