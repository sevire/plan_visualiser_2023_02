from unittest import skip

from django.test import TestCase
from plan_visual_django.models import PlanVisual, PlotableStyle
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration
from utilities import date_from_string


class TestTimelinesWithFixtures(TestCase):
    fixtures = [
        'plan_visual_django/tests/test_fixtures/auth_test_fixtures.json',
        'plan_visual_django/tests/test_fixtures/test_fixtures.json'
    ]

    @skip
    def test_timelines_date_range_calculation(self):
        """
        Tests the calculation of "final" start and end dates for a visual based on all the timelines that
        are to be included.
        :return:
        """
        visual_start_date = date_from_string("2020-02-15")
        visual_end_date = date_from_string("2022-05-15")

        plan_visual = PlanVisual.objects.get(id=10)
        plotable_style_01 = PlotableStyle.objects.get(id=1)

        visual_orchestrator = VisualOrchestration(plan_visual)


        pass
