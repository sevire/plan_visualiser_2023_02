from ddt import ddt, data, unpack
from django.test import TestCase

from plan_visual_django.models import TimelineForVisual
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_data

timeline_settings = {
    "timeline_collection_level_settings": {
        "timeline_vertical_gap": 0
    },
    "timelines": [
        {
            "timeline_name": "Quarter Labels",
            "timeline_type": TimelineForVisual.TimelineLabelType.QUARTERS,
            "timeline_height": 10,
            "timeline_colour_banding_settings": TimelineForVisual.TimelineLabelBandingType.ALTERNATE_AUTO_SHADE,
            "label_styles": [
                "INSERT_PLOTABLE_STYLE_1_HERE"
            ],
            "timeline_label_type_specific_settings": {
                "month_start": 1
            }
        },
        {
            "timeline_name": "Month Labels",
            "timeline_type": TimelineForVisual.TimelineLabelType.MONTHS,
            "timeline_height": 10,
            "timeline_colour_banding_settings": TimelineForVisual.TimelineLabelBandingType.ALTERNATE_AUTO_SHADE,
            "label_styles": [
                "INSERT_PLOTABLE_STYLE_1_HERE"
            ],
            "timeline_label_type_specific_settings": None
        }
    ]
}


@ddt
class TestVisualOrchestration(TestCase):
    """
    Tests the logic to control the creation of a number of linked and dependent plotable collections, and then to
    plot them into an overall visual, correctly calculating relative position of each collection and the plotables
    contained within.
    """
    def setUp(self) -> None:
        self.plan_records, self.visual_records, self.visual_activity_records = setup_common_data()

    def test_swimlane_creation(self):
        pass

    def test_activity_creation(self):
        pass

    def test_visual_plotting(self):
        pass
