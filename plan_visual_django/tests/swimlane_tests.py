import django.test
from ddt import ddt, data, unpack

from plan_visual_django.services.plan_to_visual.plan_to_visual import SwimlaneManager
from plan_visual_django.services.visual.formatting import VerticalPositioningOption, TextHorizontalAlign, \
    TextVerticalAlign, TextLayout
from plan_visual_django.services.visual.visual_settings import VisualSettings, SwimlaneSettings
from plan_visual_django.tests.utilities import date_from_string

swimlane_test_data = {
    'swimlane_settings': {
        'swimlanes': [
            'swimlane-01',
            'swimlane-02'
        ],
        'swimlane_gap': 5,
        'swimlane_formats': None,
        'swimlane_label_horizontal_alignment': None,
        'swimlane_label_vertical_alignment': None,
        'margin': None,
        'swimlanes_enabled': None,
    },
    'visual_settings': {
        'width': 600,
        'height': 400,
        'track_height': 10,
        'track_gap': 2,
    },
    'activities': [
        {
            'unique_id_from_plan': "UID-001",
            'swimlane': "swimlane-01",
            'plotable_shape': "RECTANGLE",
            'vertical_positioning_type': VerticalPositioningOption.TRACK_NUMBER,
            'vertical_positioning_value': 1,
            'height_in_tracks': 1,
            'text_horizontal_alignment': TextHorizontalAlign.LEFT,
            'text_vertical_alignment': TextVerticalAlign.MIDDLE,
            'text_flow': TextLayout.WRAP,
            'plotable_style': "dummy",
            'activity_name': "Activity 1",
            'duration': 10,
            'start_date': date_from_string("2023-01-01"),
            'end_date': date_from_string("2023-01-31"),
            'level': 1
        },
        {
            'unique_id_from_plan': "UID-003",
            'swimlane': "swimlane-01",
            'plotable_shape': "RECTANGLE",
            'vertical_positioning_type': VerticalPositioningOption.TRACK_NUMBER,
            'vertical_positioning_value': 3,
            'height_in_tracks': 1,
            'text_horizontal_alignment': TextHorizontalAlign.LEFT,
            'text_vertical_alignment': TextVerticalAlign.MIDDLE,
            'text_flow': TextLayout.WRAP,
            'plotable_style': "dummy",
            'activity_name': "Activity 1",
            'duration': 10,
            'start_date': date_from_string("2023-01-01"),
            'end_date': date_from_string("2023-01-31"),
            'level': 1
        },
        {
            'unique_id_from_plan': "UID-004",
            'swimlane': "swimlane-01",
            'plotable_shape': "RECTANGLE",
            'vertical_positioning_type': VerticalPositioningOption.TRACK_NUMBER,
            'vertical_positioning_value': 2,
            'height_in_tracks': 4,
            'text_horizontal_alignment': TextHorizontalAlign.LEFT,
            'text_vertical_alignment': TextVerticalAlign.MIDDLE,
            'text_flow': TextLayout.WRAP,
            'plotable_style': "dummy",
            'activity_name': "Activity 1",
            'duration': 10,
            'start_date': date_from_string("2023-01-01"),
            'end_date': date_from_string("2023-01-31"),
            'level': 1
        },

        {
            'unique_id_from_plan': "UID-002",
            'swimlane': "swimlane-02",
            'plotable_shape': "RECTANGLE",
            'vertical_positioning_type': VerticalPositioningOption.TRACK_NUMBER,
            'vertical_positioning_value': 1,
            'height_in_tracks': 1,
            'text_horizontal_alignment': TextHorizontalAlign.LEFT,
            'text_vertical_alignment': TextVerticalAlign.MIDDLE,
            'text_flow': TextLayout.WRAP,
            'plotable_style': "dummy",
            'activity_name': "Activity 2",
            'duration': 10,
            'start_date': date_from_string("2023-01-01"),
            'end_date': date_from_string("2023-01-31"),
            'level': 1
        }
    ],
    'expected_results': [
        ('swimlane-01', 1, None, 0),
        ('swimlane-01', 2, None, (2-1)*(10+2)),
        ('swimlane-01', 3, None, (3-1)*(10+2)),
        ('swimlane-01', 4, None, (4-1)*(10+2)),
        ('swimlane-01', 5, None, (5-1)*(10+2)),
        ('swimlane-01', 6, ValueError, None),  # Track number too high - will throw exception
        ('swimlane-02', 1, None, 5*10+4*2+5),
    ]
}


@ddt
class SwimlaneTests(django.test.TestCase):
    """
    Tests the ability to manage activities within a number of swimlanes and correctly calculate the vertical position
    of the tracks within each swim lane and the shape and position of each swimlane.
    """
    def setUp(self) -> None:
        swimlane_settings = SwimlaneSettings(**swimlane_test_data['swimlane_settings'])
        visual_settings = VisualSettings(**swimlane_test_data['visual_settings'], swimlane_settings=swimlane_settings)
        self.swimlane_manager = SwimlaneManager(visual_settings=visual_settings)

        for activity in swimlane_test_data['activities']:
            self.swimlane_manager.add_activity_to_swimlane(activity)

    @data(*swimlane_test_data['expected_results'])
    @unpack
    def test_track_top_calculation(self, swimlane_name, track_number, exception, top):

        if exception is None:
            self.assertEqual(self.swimlane_manager.get_track_top_within_swimlane(swimlane_name, track_number), top)
        else:
            self.assertRaises(exception)

