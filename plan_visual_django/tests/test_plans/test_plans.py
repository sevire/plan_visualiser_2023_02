from django.test import TestCase
from unittest.mock import patch
from plan_visual_django.models import Plan, PlanActivity


# Mock PlanActivity's objects.filter method to return an empty queryset
@patch('plan_visual_django.models.PlanActivity.objects.filter', return_value=PlanActivity.objects.none())
class TestExtractSummaryPlanInfo(TestCase):
    def setUp(self):
        self.plan = Plan(
            plan_name='Test Plan 1',
            file_name='Test File 1',
            file_type_name='Test Type 1'
        )

    def test_extract_summary_plan_info_with_no_activities(self, mock_filter):
        # Note mock_filter is used by function as it is modified by @patch decorator - so don't remove!
        from plan_visual_django.models import extract_summary_plan_info
        summary = extract_summary_plan_info(self.plan)

        expected_output = {
            'plan_file_name': ('Last uploaded file name', 'Test File 1'),
            'number_of_activities': ('# Activities', 0),
            'number_of_milestones': ('# Milestones', 0),
            'earliest_start_date': ('Earliest date', None),
            'latest_end_date': ('Latest date', None),
            'duration': ('Plan Duration', None),
            'levels': ('# Levels', None),
        }

        self.assertDictEqual(summary, expected_output)