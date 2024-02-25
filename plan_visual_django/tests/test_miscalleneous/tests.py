import os
from unittest import mock

from django.core.files import File
from django.test import TestCase
from plan_visual_django.models import PlanFieldMappingType, Plan, FileType
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
# from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_reference_data
from resources.test_configuration import test_data_base_folder, test_fixtures_folder


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

        file_type = FileType.objects.get(file_type_name="Excel (modern) Smartsheet Export")

        plan_object = mock.Mock(spec=Plan)
        plan_object.file_type = file_type
        plan_object.file = file
        plan_object.file_name = file_path
        file_reader_object = ExcelXLSFileReader()


        raw_data, headers = file_reader_object.read(plan_object)
        plan_field_mapping_type = PlanFieldMappingType.objects.all()[0]

        parsed_data = file_reader_object.parse(raw_data, headers, plan_field_mapping=file_type.plan_field_mapping_type)

        pass