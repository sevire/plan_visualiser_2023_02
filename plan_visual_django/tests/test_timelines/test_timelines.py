from unittest import skip

from ddt import ddt, data, unpack
from django.db.backends.dummy.base import ignore
from django.test import TestCase
from plan_visual_django.models import PlotableStyle, Color, Font, TimelineForVisual
from plan_visual_django.services.visual.visual_elements import MonthTimeline, QuarterTimeline
from plan_visual_django.tests.utilities import date_from_string
from resources.data_setup.common_data_setup import setup_common_data


test_timeline_data = [
    {
        "type": TimelineForVisual.TimelineLabelType.MONTHS,
        "cases": [
            {
                "start_date_in": date_from_string("2021-02-15"),
                "end_date_in": date_from_string("2021-10-16"),
                "start_date_out": date_from_string("2021-02-01"),
                "end_date_out": date_from_string("2021-10-31")
            }
        ]
    },
    {
        "type": TimelineForVisual.TimelineLabelType.QUARTERS,
        "cases": [
            {
                "month_offset": 1,
                "start_date_in": date_from_string("2021-02-15"),
                "end_date_in": date_from_string("2021-10-16"),
                "start_date_out": date_from_string("2021-01-01"),
                "end_date_out": date_from_string("2021-12-31")
            },
            {
                "month_offset": 2,
                "start_date_in": date_from_string("2021-02-15"),
                "end_date_in": date_from_string("2021-10-16"),
                "start_date_out": date_from_string("2021-02-01"),
                "end_date_out": date_from_string("2021-10-31")
            },
            {
                "month_offset": 2,
                "start_date_in": date_from_string("2021-01-15"),
                "end_date_in": date_from_string("2021-11-16"),
                "start_date_out": date_from_string("2020-11-01"),
                "end_date_out": date_from_string("2022-01-31")
            }
        ]
    }
]


def timeline_test_data_gen():
    for timeline_type in test_timeline_data:
        params = {}
        type = timeline_type["type"]
        params["timeline_type"] = type
        for case in timeline_type["cases"]:
            if type == "quarter":
                params["month_offset"] = case["month_offset"]

            params["in_start_date"] = case["start_date_in"]
            params["in_end_date"] = case["end_date_in"]

            params["start_or_end"] = "start"
            params["out_date"] = case["start_date_out"]

            yield params.copy()

            params["start_or_end"] = "end"
            params["out_date"] = case["end_date_out"]

            yield params.copy()


@ddt
@skip
class TestTimelines(TestCase):
    def setUp(self) -> None:
        plan_records, visual_records, visual_activity_records = setup_common_data()

        self.colour_01 = Color(red=50, green=51, blue=52)
        self.colour_02 = Color(red=100, green=101, blue=102)
        self.colour_03 = Color(red=150, green=151, blue=152)
        self.font=Font(font_name="Arial")
        self.plotable_style = PlotableStyle.objects.create(
            style_name="Style-01",
            fill_color=self.colour_01,
            line_color=self.colour_02,
            font_color=self.colour_03,
            line_thickness=3,
            font=self.font
        )

    @data(*list(timeline_test_data_gen()))
    @unpack
    @skip
    def test_timeline_calculate_start_end(self, timeline_type, start_or_end, in_start_date, in_end_date, out_date, month_offset=1):
        """
        Tests the calculation of the start and end dates for each timeline type based on the start and end of the
        activities.

        :return:
        """

        timeline = TimelineForVisual.objects.create(
            plan_visual=visual_records[0],
            timeline_type=timeline_type,
            timeline_name="TEST_TIMELINE",
            timeline_height=400,
            plotable_style=self.plotable_style
        )
        if timeline_type == "month":
            timeline_object = MonthTimeline(in_start_date, in_end_date, timeline)
        elif timeline_type == "quarter":
            timeline_object = QuarterTimeline(in_start_date, in_end_date, timeline)
        else:
            self.fail(f"Unrecognised timeline type {timeline_type}")

        timeline_start_date, timeline_end_date = timeline_object.calculate_date_range()

        if start_or_end == "start":
            self.assertEqual(timeline_start_date, out_date)
        elif start_or_end == "end":
            self.assertEqual(timeline_end_date, out_date)


