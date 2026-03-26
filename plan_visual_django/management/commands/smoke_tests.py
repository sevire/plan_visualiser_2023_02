from django.core.management.base import BaseCommand
from plan_visual_django.services.smoke_tests.smoke_test_service import run_all_smoke_tests

class Command(BaseCommand):
    help = "Run enhanced smoke tests to verify the health of the application"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("Running Application Smoke Tests..."))
        
        results = run_all_smoke_tests()
        failed_count = 0

        # Define column widths for a simple table layout
        col_width_name = 15
        col_width_status = 10
        
        for name, result in results.items():
            status = result['status']
            message = result['message']
            
            # Format status with color
            if status == "PASS":
                styled_status = self.style.SUCCESS(f" {status} ")
            else:
                styled_status = self.style.ERROR(f" {status} ")
                failed_count += 1
            
            # Print row
            row = f"{name:<{col_width_name}} [{styled_status}] {message}"
            self.stdout.write(row)

        self.stdout.write("-" * 60)
        
        if failed_count == 0:
            self.stdout.write(self.style.SUCCESS("All smoke tests passed! Application health is good."))
        else:
            self.stdout.write(self.style.ERROR(f"{failed_count} smoke test(s) failed. Please check the errors above."))
            exit(1)