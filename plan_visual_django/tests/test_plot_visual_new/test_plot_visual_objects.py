"""
Am including these tests as part of re-factoring the way the visual is plotted, which in turn is part of refactoring
the main screen of the app to be more responsive.

Testing the ability of each object to calculate its plot dimensions by calling its parent and children.
"""
import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.models import PlanVisual
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder
from plan_visual_django.tests.resources.utilities import generate_test_data_field_stream_multiple_inputs, date_from_string
from plan_visual_django.tests.resources.utilities import extract_object_from_list_by_field


@ddt
class TestPlotVisualObjects(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    def setUp(self):
        pass

    def test_get_swimlanes_dims(self):
        visual = PlanVisual.objects.get(pk=4)
        swimlane_dims = visual.get_swimlanesforvisual_dimensions()
        top, left, width, height = swimlane_dims
        self.assertEqual(40, top)
        self.assertEqual(0, left)
        self.assertEqual(1000, width)
        self.assertEqual(116+260+5, height)

    @data(*generate_test_data_field_stream_multiple_inputs([
        # visual_id, swimlane_seqnum, top, left, width, height
        (4, 1, 40, 0, 1000, 116),
        (4, 2, 161, 0, 1000, 236+4+20), # Note last track is 2 tracks high so increases swimlane height
        ],
        ("top", "left", "width", "height")
    ))
    @unpack
    def test_get_swimlane_plot_parameters(self, visual_id, swimlane_sequence_within_visual, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        swimlane = visual.swimlaneforvisual_set.get(sequence_number=swimlane_sequence_within_visual)
        swimlane_plotable = swimlane.get_plotable()

        # Access and check the appropriate field value depending upon which expected field has been passed in.
        self.assertEqual(field_value, getattr(swimlane_plotable, field_name))

    @data(*generate_test_data_field_stream_multiple_inputs([
        # visual_id, timeline_seqnum, top, left, width, height
        (4, 1, 0, 0, 1000, 25),
        (4, 2, 25, 0, 1000, 15),
        ],
        ("top", "left", "width", "height")
    ))
    @unpack
    def test_get_timeline_plot_parameters(self, visual_id, timeline_sequence_within_visual, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        timeline = visual.timelineforvisual_set.get(sequence_number=timeline_sequence_within_visual)
        top, left, width, height = timeline.get_plot_parameters()

        # Access and check the appropriate field value depending upon which expected field has been passed in.
        self.assertEqual(field_value, locals()[field_name])

    @data(*generate_test_data_field_stream_multiple_inputs([
        # visual_id, sticky_id, approx_flag, top, left, width, height
        (4, "ID-026", False, 40+4*(20+4), (62.5/275)*1000-5, 10, 20),
        (4, "ID-025", False, 40 + 5*20+4*4 + 5, (214.5/275)*1000-5, 10, 20),
        (4, "ID-024", True, 40+5*20+4*4+5+9*(20+4), (31+31+30+31+30+31+17)/275*1000, (31-18+1)*1000/275, 44),
        ],
        ("top", "left", "width", "height")
    ))
    @unpack
    def test_get_activity_plot_parameters(self, visual_id, activity_sticky_id, approx_flag, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        activity = visual.visualactivity_set.get(unique_id_from_plan=activity_sticky_id)
        activity_plotable = activity.get_plotable()

        # Access and check the appropriate field value depending upon which expected field has been passed in.
        if approx_flag:
            self.assertAlmostEqual(field_value, getattr(activity_plotable, field_name))
        else:
            self.assertEquals(field_value, getattr(activity_plotable, field_name))

    @data(*generate_test_data_field_stream_multiple_inputs([
        # visual_id, swimlane_seq_num, sticky_id, top, left, width, height
        (4, 1, "ID-026", 136, (62.5/275)*1000-5, 10, 20),
        ],
        ("top", "left", "width", "height")
    ))
    @unpack
    def test_get_swimlane_activity_plot_parameters(self, visual_id, swimlane_seq_num, activity_sticky_id, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        swimlane = visual.swimlaneforvisual_set.get(sequence_number=swimlane_seq_num)
        activity = swimlane.visualactivity_set.get(unique_id_from_plan=activity_sticky_id)

        activity_plotable = activity.get_plotable()

        # Access and check the appropriate field value depending upon which expected field has been passed in.
        self.assertEquals(field_value, getattr(activity_plotable, field_name))


    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("height",),
        test_data=[
            # visual_id, timeline_seq, timeline_label_seq, top, left, width, height
            (4, 40),
        ],
    ))
    @unpack
    def test_get_timelines_height(self, visual_id, field_name, field_value):
        visual = PlanVisual.objects.get(pk=visual_id)
        timeline_height = visual.get_timelines_height()

        self.assertEqual(field_value, timeline_height)

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("top", "left", "width", "height"),
        test_data=[
            # visual_id, timeline_seq, timeline_label_seq, approx_flag, top, left, width, height
            (4, 1, 1, True, 0, 0, 112.727272727273, 25),
            (4, 1, 2, True, 0, 112.727272727273, 112.727272727273, 25),
            (4, 1, 3, True, 0, 225.454545454545, 109.090909090909, 25),
            (4, 1, 4, True, 0, 334.545454545455, 112.727272727273, 25),
            (4, 1, 5, True, 0, 447.272727272727, 109.090909090909, 25),
            (4, 1, 6, True, 0, 556.363636363636, 112.727272727273, 25),
            (4, 1, 7, True, 0, 669.090909090909, 112.727272727273, 25),
            (4, 1, 8, True, 0, 781.818181818182, 105.454545454545, 25),
            (4, 1, 9, True, 0, 887.272727272727, 112.727272727273, 25),
            (4, 2, 1, True, 25, 0, 334.545454545455, 15),
            (4, 2, 2, True, 25, 334.545454545455, 334.545454545455, 15),
        ],
    ))
    @unpack
    def test_get_timeline_labels(self, visual_id, timeline_seq, timeline_label_seq, approx_flag, field_name, field_value):
        """
        Test plotting of all the labels for a timeline.  Note that this test is testing the TimelineCollection class
        which isn't (currently) part of the DB Model, but uses Timeline objects from the model.

        :param visual_id:
        :param sequence_num:
        :param field_name:
        :param field_value:
        :return:
        """
        visual = PlanVisual.objects.get(pk=visual_id)
        timeline_plotables = visual.get_timeline_plotables()


        # timelines = visual.timelineforvisual_set.all()
        #
        # earliest_date, latest_date = visual.get_visual_earliest_latest_plan_date()

        timeline_label_plotable = timeline_plotables[timeline_seq-1]
        label_plotable_to_check = timeline_label_plotable[timeline_label_seq-1]

        # If approx flag is set then we need to test for near equality (won't be exact because of rounding effects).
        if approx_flag:
            self.assertAlmostEqual(getattr(label_plotable_to_check, field_name), field_value)
        else:
            self.assertEqual(getattr(label_plotable_to_check, field_name), field_value)

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("top", "left", "width", "height"),
        test_data=[
            # visual_id, objects_to_check, seq_or_activity_name, item_sequ_num, approx_flag, top, left, width, height
            (4, "Timeline", 1, 1, True, 0, 0, 112.727272727273, 25),
            (4, "Timeline", 1, 2, True, 0, 112.727272727273, 112.727272727273, 25),
            (4, "Timeline", 1, 3, True, 0, 225.454545454545, 109.090909090909, 25),
            (4, "Timeline", 1, 4, True, 0, 334.545454545455, 112.727272727273, 25),
            (4, "Timeline", 1, 5, True, 0, 447.272727272727, 109.090909090909, 25),
            (4, "Timeline", 1, 6, True, 0, 556.363636363636, 112.727272727273, 25),
            (4, "Timeline", 1, 7, True, 0, 669.090909090909, 112.727272727273, 25),
            (4, "Timeline", 1, 8, True, 0, 781.818181818182, 105.454545454545, 25),
            (4, "Timeline", 1, 9, True, 0, 887.272727272727, 112.727272727273, 25),
            (4, "Timeline", 2, 1, True, 25, 0, 334.545454545455, 15),
            (4, "Timeline", 2, 2, True, 25, 334.545454545455, 334.545454545455, 15),
            (4, "Timeline", 2, 3, True, 25, 669.090909090909, 330.909090909091, 15),
            (4, "Swimlane", 1, None, False, 40, 0, 1000, 116),
            (4, "Swimlane", 2, None, False, 161, 0, 1000, 260),
            (4, "Visual Activities", "Project Start", None, False, 40 + 4 * (20 + 4), (62.5 / 275) * 1000 - 5, 10, 20),
            (4, "Visual Activities", "Milestone 6", None, False, 40 + 5*20+4*4 + 5, (214.5 / 275) * 1000 - 5, 10, 20),
            (4, "Visual Activities", "Activity 24", None, True, 40 + 5 * 20 + 4 * 4 + 5 + 9 * (20 + 4), (31 + 31 + 30 + 31 + 30 + 31 + 17) / 275 * 1000, (31 - 18 + 1) * 1000 / 275, 44),
        ],
    ))
    @unpack
    def test_visual_activity_plotables(self, visual_id, objects_to_check, seq_or_activity_name, item_seq_num, approx_flag, field_name, field_value):
        """
        We are checking the whole visual one element at a time, so there is a bit of logic here to route through to
        which test we need to execute for each scenario

        """

        visual = PlanVisual.objects.get(pk=visual_id)
        visual_plotables = visual.get_plotables()

        if objects_to_check == "Timeline":
            objects = visual_plotables["timelines"]
            object_to_check = objects[seq_or_activity_name - 1]
            plotable = object_to_check[item_seq_num-1]
            value_to_check = getattr(plotable, field_name)
        elif objects_to_check == "Swimlane":
            objects = visual_plotables["swimlanes"]
            plotable = objects[seq_or_activity_name - 1]
            value_to_check = getattr(plotable, field_name)
        elif objects_to_check == "Visual Activities":
            objects = visual_plotables["visual_activities"]

            #  Need to find plotable with text field equal to activity name.
            plotable = extract_object_from_list_by_field(objects, seq_or_activity_name, "text")
            value_to_check = getattr(plotable, field_name)
        else:
            self.fail(f"Unexpected objects_to_check: {objects_to_check}")

        if approx_flag is True:
            self.assertAlmostEqual(value_to_check, field_value)
        else:
            self.assertEqual(field_value, value_to_check)

    @data(*generate_test_data_field_stream_multiple_inputs(
        expected_value_field_names=("earliest_start_date", "latest_end_date"),
        test_data=[
            # visual_id,
            (1, "2023-09-01", "2023-10-26"),
        ],
    ))
    @unpack
    def test_visual_earliest_latest_date(self, visual_id, field_name, field_value):
        """
        Checks that calculation of earliest latest date for a visual is calculated correctly in cases where
        there are no timelines (other cases tested implicitly elsewhere).  If no timelines present then the earliest
        and latest date are simply the earliest and latest date of all the activities in the visual, not aligned to the
        start and end of periods in the timeline labels (eg month start or end)

        :param visual_id:
        :param field_name:
        :param field_value:
        :return:
        """
        visual = PlanVisual.objects.get(pk=visual_id)
        earliest_date, latest_date = visual.get_visual_earliest_latest_date()

        if field_name == "earliest_start_date":
            value_to_check = earliest_date
            expected_value = date_from_string(field_value)
        elif field_name == "latest_end_date":
            value_to_check = latest_date
            expected_value = date_from_string(field_value)
        else:
            self.fail(f"Unexpected field_name to check: {field_name}")

        self.assertEqual(expected_value, value_to_check)


