"""
Tests end to end functionality of the plan upload process, from file upload to database storage.

Reads a number of test files, and checks that the data is correctly stored in the database.
"""
import os
from ddt import ddt, data, unpack
from django.test import TestCase
from plan_visual_django.exceptions import ExcelPlanSheetNotFound
from plan_visual_django.services.plan_file_utilities.plan_field import FileType
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader, PlanFileReader
from plan_visual_django.tests.resources.unit_test_configuration import test_data_base_folder, test_fixtures_folder


@ddt
class TestFileReadAndParse(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    test_sheet_name_selection_data = [
        (["test_file_1", "sheet_name_2", "sheet_name_3"], "test_file_1", "excel-02-smartsheet-export-01", "test_file_1"),
        (["Task_Data", "sheet_name_2", "sheet_name_3"], "test_file_1", "excel-01-msp-export-default-01", "Task_Data"),
        (["Single Sheet"], "test_file_1", "excel-01-msp-export-default-01", "Single Sheet"),
        (["Single Sheet"], "test_file_1", "excel-02-smartsheet-export-01", "Single Sheet"),
        (["Sheet1", "Sheet2", "Sheet3"], "test_file_1", "excel-02-smartsheet-export-01", "ExcelPlanSheetNotFound"),
        (["Sheet1", "Sheet2", "Sheet3"], "test_file_1", "excel-01-msp-export-default-01", "ExcelPlanSheetNotFound"),
    ]

    @data(*test_sheet_name_selection_data)
    @unpack
    def test_sheet_name_selection(
            self,
            sheet_list: [str],
            file_name: str,
            file_type_name:str,
            expected_sheet_name: str
    ):
        """
        Tests that the correct sheet is selected in the Excel input file
        :return:
        """
        file_reader: ExcelXLSFileReader = ExcelXLSFileReader()
        file_type: FileType = FileType.from_name(file_type_name)

        # Check type of expected sheet name.  If it is an exception then that's what we are expecting.
        if expected_sheet_name == "ExcelPlanSheetNotFound":
            self.assertRaises(ExcelPlanSheetNotFound, file_reader.get_sheet_name, sheet_list, file_name, file_type)
        else:
            output_sheet_name = file_reader.get_sheet_name(sheet_list, file_name, file_type_name)
            self.assertEqual(expected_sheet_name, output_sheet_name)

