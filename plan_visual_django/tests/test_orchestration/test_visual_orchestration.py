import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.models import TimelineForVisual, PlanVisual
from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder
from plan_visual_django.tests.resources.utilities import generate_test_data_field_stream_multiple_inputs


@ddt
class TestVisualOrchestration(TestCase):
    """
    Tests the logic to control the creation of a number of linked and dependent plotable collections, and then to
    plot them into an overall visual, correctly calculating relative position of each collection and the plotables
    contained within.
    """
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("top", "left", "width", "height"),
        test_data=[
            # visual_id, objects_to_check, seq_or_activity_name, item_sequ_num, approx_flag, top, left, width, height
            (4, "timelines", 1, True, 0, 0, 31*1000/275, 25),  # July month timeline label. 31 days
            (4, "timelines", 3, True, 0, 31*1000/275, 31*1000/275, 25),  # Aug (31)
            (4, "timelines", 5, True, 0, (31+31)*1000/275, 30*1000/275, 25),  # Sep (30)
            (4, "timelines", 7, True, 0, (31+31+30)*1000/275, 31*1000/275, 25),  # Oct (31)
            (4, "timelines", 9, True, 0, (31+31+30+31)*1000/275, 30*1000/275, 25),  # Nov (30)
            (4, "timelines", 11, True, 0, (31+31+30+31+30)*1000/275, 31*1000/275, 25),  # Dec (31)
            (4, "timelines", 13, True, 0, (31+31+30+31+30+31)*1000/275, 31*1000/275, 25),  # Jan (31)
            (4, "timelines", 15, True, 0, (31+31+30+31+30+31+31)*1000/275, 29*1000/275, 25),  # Feb (29)
            (4, "timelines", 17, True, 0, (31+31+30+31+30+31+31+29)*1000/275, 31*1000/275, 25),  # Mar (31)
            (4, "timelines", 19, True, 25, (0)*1000/275, (31+31+30)*1000/275, 15),  # Jul-Sep (31)
            (4, "timelines", 21, True, 25, (31+31+30)*1000/275, (31+30+31)*1000/275, 15),  # Oct-Dec (31)
            (4, "timelines", 23, True, 25, (31+31+30+31+30+31)*1000/275, (31+29+31)*1000/275, 15),  # Jan-Mar (31)

            (4, "swimlanes", 1, True, 25+15, 0*1000/275, 1000, 5*20 + 4*4),  # Swimlane 1(id=4), 5 tracks, track height 20, track gap 4
            (4, "swimlanes", 3, True, 25+15+5+(5*20+4*4), 0*1000/275, 1000, ((9+2)*20+(9+1)*4)),  # Swimlane 2(id=5), 10 tracks (activity in track 10 has height of 2 tracks), track height 20, track gap 4, swimlane gap 5

            (4, "visual_activities", 1, True, 25+15+(4*20+4*4), (31+31+0.5)*1000/275-10/2, 10, 20),  # ID-026, S1, 2023-09-01, milestone, 'Project Start',
            (4, "visual_activities", 3, True, 25+15+ 5*20+4*4 + 5, (31+31+30+31+30+31+30+0.5)*1000/275-10/2, 10, 20),  # ID-025, 2024-01-31,S2:2, Milestone 6, milestone
            (4, "visual_activities", 5, True, 25+15+(5*20+4*4)+5+9*20+9*4, (31+31+30+31+30+31+17)*1000/275, (31-18+1)*1000/275, 20+4+20),  # ID-024, S2:10, 2024-01-18:2024-01-31, Activity 24
        ],
    ))
    @unpack
    def test_visual_plotting_shape_item(self, visual_id, canvas_name, object_in_canvas_seq, approx_flag, field_name, expected_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        visual_plotables = visual.get_plotables()

        renderer = CanvasRenderer()
        rendered_plotables = renderer.render_from_iterable(visual_plotables)

        # Expect an entry for each of Timelines, Swimlanes and Visual Activities
        canvas_to_check = rendered_plotables[canvas_name]
        rendered_object_to_check = canvas_to_check[object_in_canvas_seq-1]

        if field_name in {"top", "left", "width", "height"}:
            value_to_check = rendered_object_to_check["shape_plot_dims"][field_name]
        else:
            self.fail(f"Unexpected field name {field_name}")

        if approx_flag:
            self.assertAlmostEqual(expected_value, value_to_check)
        else:
            self.assertEqual(expected_value, value_to_check)

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("text", "x", "y", "text_align", "text_baseline", "fill_color"),
        test_data=[
            # visual_id, objects_to_check, seq_or_activity_name, item_sequ_num, approx_flag, text, x, y, text_align, text_baseline
            (4, "timelines", 2, True, "Jul", 0+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 4, True, "Aug", (31*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 6, True, "Sep", ((31+31)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 8, True, "Oct", ((31+31+30)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 10, True, "Nov", ((31+31+30+31)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 12, True, "Dec", ((31+31+30+31+30)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 14, True, "Jan", ((31+31+30+31+30+31)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 16, True, "Feb", ((31+31+30+31+30+31+31)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 18, True, "Mar", ((31+31+30+31+30+31+31+29)*1000/275)+5, 0+25/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 20, True, "Jul - Sep", ((0)*1000/275)+5, 0+25+15/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 22, True, "Oct - Dec", ((31+31+30)*1000/275)+5, 0+25+15/2, "left", "middle", "rgb(64,64,64)"),
            (4, "timelines", 24, True, "Jan - Mar", ((31+31+30+31+30+31)*1000/275)+5, 0+25+15/2, "left", "middle", "rgb(64,64,64)"),

            (4, "swimlanes", 2, True, "Visual 01:01, Swimlane 1", 5, 25+15, "left", "top", "rgb(64,64,64)"),
            (4, "swimlanes", 4, True, "Visual 01:01, Swimlane 2", 5, 25+15+5*20+4*4+5, "left", "top", "rgb(64,64,64)"),

            (4, "visual_activities", 2, True, "Project Start", (31+31+.5)*(1000/275)-5-5, 25+15+4*20+4*4+0.5*20, "right", "middle", "rgb(186,186,186)"), # 2023-09-01, milestone, LFLOW
            (4, "visual_activities", 4, True, "Milestone 6", (31+31+30+31+30+31+30+0.5)*1000/275-5-5,  40 + 5*20+4*4 + 5 + 20/2, "right", "middle", "rgb(186,186,186)"),
            (4, "visual_activities", 6, True, "Activity 24", (31+31+30+31+30+31+31)*1000/275-5, 25+15+5*20+4*4+5+9*20+9*4+(20+20+4)/2, "right", "middle", "rgb(186,186,186)"),
        ],
    ))
    @unpack
    def test_visual_plotting_text_item(self, visual_id, canvas_name, object_in_canvas_seq, approx_flag, field_name, expected_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        visual_plotables = visual.get_plotables()

        renderer = CanvasRenderer()

        rendered_plotables = renderer.render_from_iterable(visual_plotables)
        # Expect an entry for each of Timelines, Swimlanes and Visual Activities
        canvas_to_check = rendered_plotables[canvas_name]
        rendered_object_to_check = canvas_to_check[object_in_canvas_seq-1]

        if field_name in {"text", "fill_color"}:
            value_to_check = rendered_object_to_check[field_name]
        elif field_name in {"x", "y", "text_align", "text_baseline"}:
            value_to_check = rendered_object_to_check["shape_plot_dims"][field_name]
        else:
            self.fail(f"Unexpected field name {field_name}")

        # Approx flag only makes sense for numeric fields
        # ToDo: Fix issue with approx flag - should be by field not test case
        if not approx_flag or isinstance(value_to_check, str):
            self.assertEqual(expected_value, value_to_check)
        else:
            self.assertAlmostEqual(value_to_check, expected_value)

