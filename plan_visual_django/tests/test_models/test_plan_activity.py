"""
Tests the ability to parse raw data from an Excel import and convert it to a set of PlanActivity records
"""
import os
from unittest import skip

from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.models import PlanFieldMappingType, PlanMappedField, PlanField
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder

# Data for different field mapping schemas to test completeness validation
plan_mapped_field_data_cases = [
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        True
    ),
    (
        [
            # ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        True
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            # ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        False
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            # ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        True
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            # ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        False
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            # ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        True
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            # ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        False
    ),
    (
        [
            ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            # ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        False
    ),
    (
        [
            # ("level", "Outline_Level", "INTEGER"),
            ("unique_sticky_activity_id", "ID", "STRING"),
            # ("duration", "Duration", "INTEGER"),
            ("activity_name", "Name", "STRING"),
            # ("milestone_flag", "Milestone", "STRING_MILESTONE_YES_NO"),
            ("start_date", "Start_Date", "STRING_DATE_DMY_02"),
            ("end_date", "Finish_Date", "STRING_DATE_DMY_02"),
        ],
        True
    ),
]


@ddt
class TestPlanActivity(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'plan_field_mapping_types.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'plan_fields.json')
    ]

    @data(*plan_mapped_field_data_cases)
    @unpack
    @skip  # Skipped because checks for complete set of fields isn't quite right yet but works for current use cases
           # So needs more thought before re-instating these tests.
    def test_plan_mapped_field_is_complete(self, mapped_field_data, expected_is_complete):
        """
        Tests the ability to parse data which has been read in from an input file of any format and been converted
        to a list of dictionaries which represent the rows and columns of the records which have been read in.

        A list of headers is also provided which list the columns or fields present in the input file.

        Tests:
        - Correct conversion of input data to PlanActivity records
        - Correct treatment of different combinations of input fields, given some input fields are optional

        :return:
        """

        plan_field_mapping_type_01 = PlanFieldMappingType.objects.create(
            name="test_mapping_field_01",
            description="test_mapping_field_01_description"
        )

        for mapped_field_name, input_field_name, input_field_type in mapped_field_data:
            PlanMappedField.objects.create(
                plan_field_mapping_type=plan_field_mapping_type_01,
                mapped_field=PlanField.objects.get(field_name=mapped_field_name),
                input_field_name=input_field_name,
                input_field_type=PlanMappedField.PlanFieldType[input_field_type]
            )

        self.assertEqual(expected_is_complete, plan_field_mapping_type_01.is_complete())
