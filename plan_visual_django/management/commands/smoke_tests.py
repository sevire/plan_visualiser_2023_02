from django.core.management.base import BaseCommand
from plan_visual_django.services.smoke_tests.smoke_test_data_connectivity import check_database_connection

class Command(BaseCommand):
    help = "Run smoke tests for the application"

    def handle(self, *args, **kwargs):
        # Call the database connection check
        result = check_database_connection()

        # Format and print the result to the console
        self.stdout.write(f"Database Connectivity Test: {result['status']}")
        self.stdout.write(f"Message: {result['message']}")

        # Exit with appropriate status
        if result['status'] == "FAIL":
            self.stderr.write("Smoke test failed.")
            exit(1)  # Non-zero exit code signals failure