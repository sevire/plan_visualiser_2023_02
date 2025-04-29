import os
from typing import Dict
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase,override_settings
from plan_visual_django.forms import PlanForm, ReUploadPlanForm
from plan_visual_django.models import Plan, PlanActivity
from plan_visual_django.services.plan_file_utilities.plan_field import FileType, FileTypes, PlanFieldEnum, \
    PlanInputFieldSpecification
from plan_visual_django.services.plan_file_utilities.plan_parsing import read_and_parse_plan
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.tests.resources.test_configuration import excel_reimported_files_folder, test_data_base_folder, test_fixtures_folder

import logging
logger = logging.getLogger(__name__)

base_plan_file_name = os.path.join(excel_reimported_files_folder, "PV-Test-03.xlsx")

User = get_user_model()

@override_settings(
    MEDIA_ROOT=excel_reimported_files_folder
)
class TestFileReimport(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    def setUp(self):
        """
        Import a base plan file in Excel against which the re-uploaded files will be processed.
        :return:
        """
        user = User.objects.get(pk=1)
        file_type_name: str = "excel-02-smartsheet-export-01"

        filename = base_plan_file_name
        with open(filename, 'rb') as file_data:
            uploaded_file = SimpleUploadedFile(base_plan_file_name, file_data.read())
            form_data = {
                'plan_name': 'PV-Test-03',
                'file': uploaded_file,
                'file_type_name': file_type_name,
            }
            form_files = {
                'file': uploaded_file,
            }

            form = PlanForm(form_data, form_files)
            if form.is_valid():
                plan = form.save(commit=False)

                plan.user = user
                plan.file_name = plan.file.name
                logger.info(f"Base plan file name to be saved: [{plan.file_name}]")
                plan.save()

                file_type, mapping_type = FileTypes.get_file_type_by_name(plan.file_type_name)
                file_reader = ExcelXLSFileReader()

                read_and_parse_plan(plan, mapping_type, file_reader)

                # Set up access to the before plan for use in tests
                self.plan_id = plan.id
                self.plan_before_test = plan
                self.activities_before = list(plan.planactivity_set.all())
                pass
            else:
                self.fail("Form invalid")

    def reimport_plan(self, plan_file_name):
        filename = os.path.join(excel_reimported_files_folder, plan_file_name)
        with (open(filename, 'rb') as file_data):
            uploaded_file = SimpleUploadedFile(plan_file_name, file_data.read())
            form_data = {
                'file': uploaded_file,
            }
            form_files = {
                'file': uploaded_file,
            }

            form = ReUploadPlanForm(form_data, form_files, instance=self.plan_before_test)
            print(f"Re-upload plan file name to be saved: {plan_file_name}")
            if form.is_valid():
                plan = form.save(commit=False)
                plan.file_name = plan_file_name
                plan.save()

                mapping_type: FileType
                plan_field_mapping: Dict[PlanFieldEnum, PlanInputFieldSpecification]
                mapping_type, plan_field_mapping = FileTypes.get_file_type_by_name(plan.file_type_name)
                file_reader = ExcelXLSFileReader()

                read_and_parse_plan(plan, plan_field_mapping, file_reader, update_flag=True)
                pass
            else:
                self.fail("Form invalid")
        # We have now imported a new file for this plan and so check that nothing has changed.

    def test_no_change(self):
        """
        Checking that if a file is reimported which is identical to the original, the plan records
        in the database after the reimport are unchanged.
        :return:
        """
        self.reimport_plan("PV-Test-03-t01-identical.xlsx")

        plan_after_test = Plan.objects.get(id=self.plan_id)
        plan_activities_after_test = plan_after_test.planactivity_set

        # Now check that no records have changed
        for activity in self.activities_before:
            with self.subTest(activity=activity):
                unique_id = activity.unique_sticky_activity_id
                new_activity = plan_activities_after_test.get(unique_sticky_activity_id=unique_id)

                self.assertEqual(activity.activity_name, new_activity.activity_name)

    def test_activity_deleted(self):
        """
        Checking that if a file is reimported which has a row deleted, the plan records
        in the database after the reimport are don't include the missing row.
        :return:
        """
        self.reimport_plan("PV-Test-03-t03-activity-deleted.xlsx")

        # We have now imported a new file for this plan and so check that nothing has changed.

        plan_after_test = Plan.objects.get(id=self.plan_id)
        plan_activities_after_test = plan_after_test.planactivity_set

        # Now check that no records have changed
        for activity in self.activities_before:
            with self.subTest(activity=activity):
                unique_id = activity.unique_sticky_activity_id
                if unique_id != "ID-0006":
                    # This isn't the removed line so record should exist and fields should be unchanged
                    try:
                        new_activity = plan_activities_after_test.get(unique_sticky_activity_id=unique_id)
                    except PlanActivity.DoesNotExist:
                        self.fail(f"Activity {unique_id} incorrectly removed from plan")
                    else:
                        self.assertEqual(activity.activity_name, new_activity.activity_name)
                else:
                    # noinspection PyTypeChecker
                    self.assertRaises(PlanActivity.DoesNotExist, plan_activities_after_test.get, unique_sticky_activity_id=unique_id)

    def test_activity_added(self):
        """
        Tests that a new activity is successfully added to a plan after reimporting,
        and ensures no original activities are incorrectly removed. The method validates
        both the persistence of pre-existing activities and the addition of the specified
        new activity by comparing their unique identifiers and relevant attributes.

        :raises self.fail: If an existing activity is erroneously removed from the plan
            after reimporting.
        :raises self.assertEqual: If the `activity_name` of an existing activity does not
            match between `activities_before` and `plan_activities_after_test`.
        :raises self.assertTrue: If the new activity is not successfully added to the plan.
        """
        self.reimport_plan("PV-Test-03-t02-activity-added.xlsx")

        # We have now imported a new file for this plan and so check that new task has been added.

        plan_after_test = Plan.objects.get(id=self.plan_id)
        plan_activities_after_test = plan_after_test.planactivity_set

        # First check that before activities are all still there.
        for test_type in {"original_still_there", "new_added"}:
            if test_type == "original_still_there":
                for activity in self.activities_before:
                    with self.subTest(test_type=test_type, activity=activity):
                        unique_id = activity.unique_sticky_activity_id
                        try:
                            new_activity = plan_activities_after_test.get(unique_sticky_activity_id=unique_id)
                        except PlanActivity.DoesNotExist:
                            self.fail(f"Activity {unique_id} incorrectly removed from plan")
                        else:
                            self.assertEqual(activity.activity_name, new_activity.activity_name)
            elif test_type == "new_added":
                with self.subTest(test_type=test_type):
                    added_activity = plan_activities_after_test.get(unique_sticky_activity_id="ID-0008")
                    self.assertTrue(True, "Activity ID-0008 added as expected")

    def test_sequence_after_added_activity(self):
        """
        It is critical that the sequence of activities in the plan is the same as that from the imported file, as the
        plan is effectively a tree structure and each activity relates to the previous one.

        When an activity is added to the plan, we need to ensure that this hasn't broken the correct sequence, as
        pk/ids may not be sequential for a re-imported plan (new activities will receive an id bigger than all existing
        ids).

        :return:
        """

        unique_id_sequence_original = [
            'ID-0007',
            'ID-0001',
            'ID-0002',
            'ID-0005',
            'ID-0006',
            'ID-0003',
            'ID-0004',
        ]
        unique_id_sequence_reimport_plan_expected = [
            'ID-0007',
            'ID-0001',
            'ID-0008',
            'ID-0002',
            'ID-0005',
            'ID-0006',
            'ID-0003',
            'ID-0004',
        ]
        # First check that original plan is in expected sequence.
        with self.subTest("Checking original plan sequence..."):
            sticky_ids_before = [activity.unique_sticky_activity_id for activity in self.activities_before]
            self.assertEqual(unique_id_sequence_original, sticky_ids_before)

        # Now reimport the plan with the added activity (not at end)
        self.reimport_plan("PV-Test-03-t02-activity-added-not-end.xlsx")

        # We have now imported a new file for this plan and so check that new task has been added.

        plan_after_test = Plan.objects.get(id=self.plan_id)
        plan_activities_after_test = list(plan_after_test.planactivity_set.all())

        unique_id_sequence_reimport_plan = [activity.unique_sticky_activity_id for activity in plan_activities_after_test]
        with self.subTest("Checking re-imported plan sequence..."):
            self.assertEqual(unique_id_sequence_reimport_plan_expected, unique_id_sequence_reimport_plan)



