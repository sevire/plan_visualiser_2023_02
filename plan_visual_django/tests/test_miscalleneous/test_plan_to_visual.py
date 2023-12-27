import os
from unittest import skip

import django.test
from ddt import ddt, data, unpack

from plan_visual_django.models import VisualActivity
from plan_visual_django.services.plan_to_visual.plan_to_visual import DatePlotter
from plan_visual_django.services.visual.visual_settings import VisualSettings, SwimlaneSettings
from plan_visual_django.tests.utilities import date_from_string
from resources.test_configuration import test_data_base_folder, test_fixtures_folder

# Collection of start and end dates together with total visual width to test calculation of x values for plotables
test_date_plotter = [
    {
        'visual_width': 600,
        'dates_and_expected_results': [
            # start_date, end_date, exp_width, exp_left, exp_right
            (date_from_string("2023-01-01"), date_from_string("2023-01-31"), 600, 0, 600),
            (date_from_string("2023-01-31"), date_from_string("2023-01-31"), 19.3548387, 0, 19.3548387)
        ]
    }
]


def test_date_plotter_gen():
    """
    Generator to provide start date, end date, and expected left, right and width values for calculated plotable
    :return:
    """
    for date_set in test_date_plotter:
        visual_width = date_set['visual_width']
        dates = date_set['dates_and_expected_results']
        dates_for_data_plotter = [(start_date, end_date) for start_date, end_date, _, _, _ in dates]
        for start_end_dates in dates:
            start_date, end_date, width, left, right = start_end_dates
            yield dates_for_data_plotter, visual_width, start_date, end_date, width, left, right


test_plan_to_visal_test_data = [
    {
        'unique_id_from_plan': "UID-001",
        'swimlane': "swimlane-01",
        'plotable_shape': "RECTANGLE",
        'vertical_positioning_type': VisualActivity.VerticalPositioningType.TRACK_NUMBER,
        'vertical_positioning_value': 1,
        'height_in_tracks': 1,
        'text_horizontal_alignment': VisualActivity.HorizontalAlignment.LEFT,
        'text_vertical_alignment': VisualActivity.VerticalAlignment.MIDDLE,
        'text_flow': VisualActivity.TextFlow.FLOW_TO_LEFT,
        'plotable_style': "dummy",
        'activity_name': "Activity 1",
        'duration': 10,
        'start_date': date_from_string("2023-01-01"),
        'end_date': date_from_string("2023-01-31"),
        'level': 1
    }
]


def get_swimlanes_from_test_data(test_data):
    swimlanes = [record['swimlane'] for record in test_data]
    return swimlanes


@ddt
class TestPlanToVisual(django.test.TestCase):
    """
    Test conversion from plan elements to visual elements, including sizing and positioning.
    """

    @data(*test_date_plotter_gen())
    @unpack
    def test_date_plotter(self, dates, visual_width, start_date, end_date, exp_width, exp_left, exp_right):
        """
        Tests that when plotable elements are created to represent activities, that the dimensions are correctly
        calculated based upon the dates.

        :return:
        """
        earliest, latest = DatePlotter.get_earliest_latest_dates(dates)
        date_plotter = DatePlotter(earliest, latest, 0, visual_width)
        width = date_plotter.width(start_date, end_date)

        self.assertAlmostEqual(exp_width, width)
