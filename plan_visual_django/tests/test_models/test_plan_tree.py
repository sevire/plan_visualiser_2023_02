from django.core.files.base import ContentFile
from django.test import TestCase
from plan_visual_django.models import Plan, PlanActivity, CustomUser
from plan_visual_django.services.plan_file_utilities.plan_field import FileType
from plan_visual_django.tests.resources.utilities import date_from_string


class TestPlanTree(TestCase):
    """
    Tests logic to create hierarchy from flat records for a plan.
    """
    test_plan_tree_data_main = [
        (1, 1),  # - (Activity 1)
        (2, 2),  # -- (Activity 2)
        (3, 2),  # -- (Activity 3)
        (4, 3),  # --- (Activity 4)
        (5, 3),  # --- (Activity 5)
        (6, 2),  # -- (Activity 6)
        (7, 3),  # --- (Activity 7)
        (8, 3),  # --- (Activity 8)
        (9, 1),  # - (Activity 9)
        (10, 2),  # -- (Activity 10)
        (11, 2),  # -- (Activity 11)
        (12, 3),  # --- (Activity 12)
        (13, 3),  # --- (Activity 13)
        (14, 2),  # -- (Activity 14)
        (15, 3),  # --- (Activity 15)
        (16, 3),  # --- (Activity 16)
        (17, 1),  # - (Activity 17)
        (18, 2),  # -- (Activity 18)
        (19, 2),  # -- (Activity 19)
        (20, 3),  # --- (Activity 20)
    ]

    test_plan_tree_data_big_jump = [
        (1, 1),  # - (Activity 1)
        (2, 2),  # -- (Activity 2)
        (3, 2),  # -- (Activity 3)
        (4, 4),  # --- (Activity 4) - ERROR - can't jump to generations of children.
        (5, 3),  # --- (Activity 5)
        (6, 2),  # -- (Activity 6)
    ]

    def test_plan_tree_children(self):
        """
        Check basic functionality of creating a tree of activities from the plan records.
        :return:
        """
        expected_results_data = [
            ("ROOT", 3),
            ("ID-01",3),
            ("ID-02",0),
            ("ID-03",2),
            ("ID-04",0),
            ("ID-05",0),
            ("ID-06",2),
            ("ID-07",0),
            ("ID-08",0),
            ("ID-09",3),
            ("ID-10",0),
            ("ID-11",2),
            ("ID-12",0),
            ("ID-13",0),
            ("ID-14",2),
            ("ID-15",0),
            ("ID-16",0),
            ("ID-17",2),
            ("ID-18",0),
            ("ID-19",1),
            ("ID-20",0),
        ]


        plan_tree = self._set_up_plan_tree(self.test_plan_tree_data_main)
        for expected_result_record in expected_results_data:
            id, expected_depth = expected_result_record
            children_for_id = plan_tree.get_plan_tree_children_by_unique_id(id)
            with self.subTest(f"Depth for id {id}"):
                self.assertEqual(expected_depth, len(children_for_id))

    def test_plan_tree_depth(self):
        """
        Checks that the depth
        :return:
        """
        # Tests that each node has the right depth.  I know this looks like it's just testing directly against the
        # input data but it checks that the depth of the node correctly corresponds to the level of the activity, which
        # tests the conversion logic.
        expected_results_data = [
            ("ROOT", 0),
            ("ID-01",1),
            ("ID-02",2),
            ("ID-03",2),
            ("ID-04",3),
            ("ID-05",3),
            ("ID-06",2),
            ("ID-07",3),
            ("ID-08",3),
            ("ID-09",1),
            ("ID-10",2),
            ("ID-11",2),
            ("ID-12",3),
            ("ID-13",3),
            ("ID-14",2),
            ("ID-15",3),
            ("ID-16",3),
            ("ID-17",1),
            ("ID-18",2),
            ("ID-19",2),
            ("ID-20",3),
        ]

        plan_tree = self._set_up_plan_tree(self.test_plan_tree_data_main)
        for id, expected_depth in expected_results_data:
            actual_depth = plan_tree.get_plan_tree_depth_by_unique_id(id)
            with self.subTest(f"Checking depth for id {id}"):
                self.assertEqual(expected_depth, actual_depth)


    def test_plan_tree_error(self):
        """
        Checks that the depth
        :return:
        """
        # Tests that each node has the right depth.  I know this looks like it's just testing directly against the
        # input data but it checks that the depth of the node correctly corresponds to the level of the activity, which
        # tests the conversion logic.
        expected_results_data = [
            ("ROOT", 0),
            ("ID-01",1),
            ("ID-02",2),
            ("ID-03",2),
            ("ID-04",3),
            ("ID-05",3),
            ("ID-06",2),
            ("ID-07",3),
            ("ID-08",3),
            ("ID-09",1),
            ("ID-10",2),
            ("ID-11",2),
            ("ID-12",3),
            ("ID-13",3),
            ("ID-14",2),
            ("ID-15",3),
            ("ID-16",3),
            ("ID-17",1),
            ("ID-18",2),
            ("ID-19",2),
            ("ID-20",3),
        ]

        self.assertRaises(Exception, self._set_up_plan_tree, self.test_plan_tree_data_big_jump)

    def _set_up_plan_tree(self, plan_data):
        activity_name_prefix = "Activity"
        dummy_file = ContentFile(b"This is some dummy content", name="dummy.txt")
        dummy_user = CustomUser.objects.create()

        plan = Plan.objects.create(
            user=dummy_user,
            plan_name="Test Plan",
            file_name="Test Plan",
            file=dummy_file,
            file_type_name=FileType.EXCEL_MSP_EXPORT_DEFAULT.name,
            session_id=""
        )

        for test_activity_record in plan_data:
            sequence_number, level = test_activity_record
            unique_sticky_id = f"ID-{sequence_number:02}"
            activity_name = f"{activity_name_prefix}-{sequence_number:02}"
            milestone_flag = False
            start_date = date_from_string("2020-01-01")
            end_date = date_from_string("2020-01-01")

            PlanActivity.objects.create(
                plan=plan,
                level=level,
                unique_sticky_activity_id=unique_sticky_id,
                activity_name=activity_name,
                milestone_flag=milestone_flag,
                start_date=start_date,
                end_date=end_date,
                sequence_number=sequence_number,
            )
        return plan.get_plan_tree()

