import os
from unittest import mock

from django.core.files import File
from django.test import TestCase
from plan_visual_django.models import Plan
from plan_visual_django.services.plan_file_utilities.plan_field import FileTypes
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder


class TestReadExcelFile(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    def setUp(self):
        pass
        # setup_common_reference_data()

    def test_read_excel_file(self):
        file_path = "plan_visual_django/tests/resources/input_files/excel_plan_files/PV-Test-01.xlsx"
        file = File(file=file_path)

        file_type_name = "excel-02-smartsheet-export-01"

        plan_object = mock.Mock(spec=Plan)
        plan_object.file_type_name = file_type_name
        plan_object.file = file
        plan_object.file_name = file_path
        file_reader_object = ExcelXLSFileReader()

        raw_data, headers = file_reader_object.read(plan_object)

        file_type, plan_field_mapping = FileTypes.get_file_type_by_name(file_type_name)

        parsed_data = file_reader_object.parse(raw_data, headers, plan_field_mapping=plan_field_mapping)

        pass