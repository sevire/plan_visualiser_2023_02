from django.core.management.base import BaseCommand
from plan_visual_django.services.app_status.service_list_visuals import service_list_visuals


class Command(BaseCommand):
    help = "Lists all users, their plans, and visuals for each plan"

    def handle(self, *args, **kwargs):
        visual_data = service_list_visuals()

        for visual_record in visual_data:
            self.stdout.write(f"{visual_record['user']}: {visual_record['plan_name']}: {visual_record['visual_name']}: {visual_record['visual_num_activities']}")
