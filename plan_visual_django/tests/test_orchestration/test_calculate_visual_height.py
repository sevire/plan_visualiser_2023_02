import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.models import PlanVisual, Plan, PlotableStyle, PlanActivity, VisualActivity, TimelineForVisual, \
    SwimlaneForVisual
from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName
from plan_visual_django.tests.resources.unit_test_configuration import test_fixtures_folder, test_data_base_folder


@ddt
class TestCalculateVisualHeight(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    @staticmethod
    def gen_visual_height_test_data():
        """
        Helper method which is a generator which presents the test function with a stream of input parameters which
        the components of a visual and additional parameters (such as track_height, which will influence the overall
        height of the visual, with the expected height of the resulting visual.

        The generator presents the following in each yield
        - plan_id (needs to reference a plan in installed test fixtures for the test)
        - track_height.
        - track_gap.
        - swimlane_gap.
        - list of swimlane names, one for each swimlane to be added.
        - list of attributes for each visual_activity to add to the visual.
          - sticky_id
          - enabled_flag
          - swimlane_name
          - track_number
          - height_in_tracks
        - list of attributes for each timeline to add to the visual.
          - timeline_label_type
          - enabled
          - timeline_height
        - expected_height.
        :return:
        """
        visual_height_test_data = [
            # See comments above to decode below test data values

            # Simple case to demonstrate typical case - one visual activity
            (
                # plan_id, track_height, track_gap, swimlane_gap
                2, 12, 4, 5,
                ("Swimlane 1", "Swimlane 2", "Swimlane 3"),
                [
                    ("ID-001", True, "Swimlane 1", 1, 1),
                ],
                [
                    (TimelineForVisual.TimelineLabelType.HALF_YEAR.value, True, 17),
                ],
                29
            ),
            # Simple case to demonstrate typical case - two visual activities
            (
                # plan_id, track_height, track_gap, swimlane_gap
                2, 12, 4, 5,
                ("Swimlane 1", "Swimlane 2", "Swimlane 3"),
                [
                    ("ID-001", True, "Swimlane 1", 1, 1),
                    ("ID-002", True, "Swimlane 1", 3, 1),
                ],
                [
                    (TimelineForVisual.TimelineLabelType.HALF_YEAR.value, True, 17),
                ],
                61
            ),
            (
                # No activities, one Timeline - can we cope?
                # plan_id, track_height, track_gap, swimlane_gap
                2, 12, 4, 5,
                ("Swimlane 1", "Swimlane 2", "Swimlane 3"),
                [],
                [
                    (TimelineForVisual.TimelineLabelType.HALF_YEAR.value, True, 17),
                ],
                17
            ),
            (
                # No activities, two Timelines
                # plan_id, track_height, track_gap, swimlane_gap
                2, 12, 4, 5,
                ("Swimlane 1", "Swimlane 2", "Swimlane 3"),
                [],
                [
                    (TimelineForVisual.TimelineLabelType.HALF_YEAR.value, True, 17),
                    (TimelineForVisual.TimelineLabelType.QUARTERS.value, True, 87),
                ],
                104
            ),
            (
                # No activities, no Timelines - can we cope?
                # plan_id, track_height, track_gap, swimlane_gap
                2, 12, 4, 5,
                ("Swimlane 1", "Swimlane 2", "Swimlane 3"),
                [],
                [
                ],
                0
            ),
        ]
        for visual_height_test_data_entry in visual_height_test_data:
            plan_id, track_height, track_gap, swimlane_gap, swimlanes, visual_activities, timelines, expected_height\
                = visual_height_test_data_entry
            yield plan_id, track_height, track_gap, swimlane_gap, swimlanes, visual_activities, timelines, expected_height

    @data(*gen_visual_height_test_data())
    @unpack
    def test_calculate_visual_height(
        self,
        plan_id,
        track_height,
        track_gap,
        swimlane_gap,
        swimlanes,
        visual_activities,
        timelines,
        expected_height
    ):
        """
        Create new visual and add components, including plan activities from the fixtures and also
        swimlanes and timelines, and then check that the visual height is calculated correctly.
        
        :return: 
        """
        plan = Plan.objects.get(pk=plan_id)  # Hard coded pk from test_fixtures
        default_plotable_style = PlotableStyle.objects.get(style_name="app_user_style_01")
        visual = PlanVisual.objects.create_with_defaults(
            plan=plan,
            default_activity_plotable_style=default_plotable_style,
            default_milestone_plotable_style=default_plotable_style,
            default_swimlane_plotable_style=default_plotable_style,
            default_timeline_plotable_style_odd=default_plotable_style,
            default_timeline_plotable_style_even=default_plotable_style,
            track_height=track_height,
            track_gap=track_gap,
            swimlane_gap=swimlane_gap,
            timeline_gap=0,
            timeline_to_swimlane_gap=0
        )
        # Now add some sub-components

        # First add three swimlanes
        style_to_use = PlotableStyle.objects.get(pk=7)  # Corresponds to test fixtures
        visual.add_swimlanes_to_visual(style_to_use, *swimlanes)

        # Add visual activities
        for visual_activity_test_data in visual_activities:
            sticky_id, enabled_flag, swimlane_name, track_number, height_in_tracks = visual_activity_test_data
            swimlane = SwimlaneForVisual.objects.get(swim_lane_name=swimlane_name)
            VisualActivity.objects.create(
                visual=visual,
                unique_id_from_plan=sticky_id,
                enabled=enabled_flag,
                swimlane=swimlane,
                plotable_shape=PlotableShapeName.BULLET.value,
                vertical_positioning_value=track_number,
                height_in_tracks=height_in_tracks,
                text_horizontal_alignment=VisualActivity.HorizontalAlignment.CENTER.value,
                text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE.value,
                text_flow=VisualActivity.TextFlow.FLOW_TO_LEFT.value,
                plotable_style=style_to_use,
            )

        # Add Timelines
        for index, timeline in enumerate(timelines):
            timeline_label_type, enabled_flag, timeline_height = timeline
            TimelineForVisual.objects.create(
                plan_visual=visual,
                timeline_type=timeline_label_type,
                timeline_name=timeline_label_type,
                timeline_height=timeline_height,
                plotable_style_odd=style_to_use,
                plotable_style_even=style_to_use,
                sequence_number=index+1,
                enabled=enabled_flag
            )

        top, left, width, height, right, bottom = visual.get_visual_dimensions()
        self.assertEqual(expected_height, height)




