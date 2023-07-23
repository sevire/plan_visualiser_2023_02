from ddt import ddt, data, unpack
from django.test import TestCase

from plan_visual_django.models import PlotableShapeType, PlotableStyle, Color, Font, TimelineForVisual, PlanVisual
from plan_visual_django.services.visual.visual_elements import MonthTimeline, \
    QuarterTimeline, TimelineVisualElement
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration
from plan_visual_django.tests.utilities import date_from_string

test_timeline_data = [
    {
        "type": "month",
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
        "type": "quarter",
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
class TestTimelines(TestCase):
    def setUp(self) -> None:
        self.colour_01 = Color(red=50, green=51, blue=52)
        self.colour_02 = Color(red=100, green=101, blue=102)
        self.colour_03 = Color(red=150, green=151, blue=152)
        self.font=Font(font_name="Arial")
        self.plotable_style = PlotableStyle(
            style_name="Style-01",
            fill_color=self.colour_01,
            line_color=self.colour_02,
            font_color=self.colour_03,
            line_thickness=3,
            font=self.font
        )

    @data(*list(timeline_test_data_gen()))
    @unpack
    def test_timeline_calculate_start_end(self, timeline_type, start_or_end, in_start_date, in_end_date, out_date, month_offset=1):
        """
        Tests the calculation of the start and end dates for each timeline type based on the start and end of the
        activities.

        :return:
        """

        if timeline_type == "month":
            timeline_object = MonthTimeline(in_start_date, in_end_date)
        elif timeline_type == "quarter":
            timeline_object = QuarterTimeline(in_start_date, in_end_date, month_offset)
        else:
            self.fail(f"Unrecognised timeline type {timeline_type}")

        timeline_start_date, timeline_end_date = timeline_object.calculate_date_range(,

        if start_or_end == "start":
            self.assertEqual(timeline_start_date, out_date)
        elif start_or_end == "end":
            self.assertEqual(timeline_end_date, out_date)

    def test_timeline_visual_element(self):
        shape_type = PlotableShapeType.PlotableShapeTypeName.RECTANGLE
        month_visual_element = TimelineVisualElement(
            shape=shape_type,
            plotable_style=self.plotable_style,
            timeline_start_date=date_from_string("2020-01-01"),
            timeline_end_date=date_from_string("2020-10-15"),
            period_num=5
        )
        plotable = month_visual_element.plot_element()

        self.assertEqual(plotable.top, 5)


class TestTimelinesWithFixtures(TestCase):
    fixtures = ["test_fixtures.json", "auth.json"]

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
