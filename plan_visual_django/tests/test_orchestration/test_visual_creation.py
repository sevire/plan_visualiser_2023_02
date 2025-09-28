import os
from django.test import TestCase
from plan_visual_django.models import Plan, PlanVisual, TimelineForVisual, PlotableStyle, Color
from plan_visual_django.tests.resources.unit_test_configuration import test_fixtures_folder, test_data_base_folder
from plan_visual_django.tests.resources.utilities import create_default_styles_for_tests


class TestVisualCreation(TestCase):
    """
    This class will test some of the basic functionality around creating a new visual and
    checks edge cases such as working with a visual which has no activities in it.
    """
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    def test_visual_plotting_no_activities(self):
        plan = Plan.objects.get(pk=2)
        color_to_use = Color.objects.get(pk=121)
        user_to_use = plan.user

        create_default_styles_for_tests(color_to_use, user_to_use)
        visual = PlanVisual.objects.create_with_defaults(plan=plan)

        # Add default swimlanes and timelines
        style_for_swimlane = PlotableStyle.objects.get(pk=102)
        visual.add_swimlanes_to_visual(
            style_for_swimlane,
            "Swimlane 1", "Swimlane 2", "Swimlane 3"
        )
        TimelineForVisual.create_all_default_timelines(visual)

        plotables = visual.get_plotables()

        self.assertTrue(True)  # Dummy just to get a tick if no crashes.

