"""
Tests the ability to parse raw data from an Excel import and convert it to a set of PlanActivity records
"""
import os
from ddt import ddt
from django.test import TestCase
from plan_visual_django.tests.resources.unit_test_configuration import test_data_base_folder, test_fixtures_folder

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
    ]
