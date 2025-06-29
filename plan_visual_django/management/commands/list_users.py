from django.core.management.base import BaseCommand
from plan_visual_django.services.app_status.service_list_users import service_list_users


class Command(BaseCommand):
    help = "Lists all users and flags those with superuser status"

    def handle(self, *args, **kwargs):
        user_data = service_list_users()

        for user_record in user_data:
            self.stdout.write(f" - {user_record['username']}{user_record['superuser_flag']}{user_record['is_staff_flag']}")

