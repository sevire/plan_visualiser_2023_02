from django.test import TestCase
from plan_visual_django.models import PlanFieldMappingType
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_reference_data


class TestReadExcelFile(TestCase):
    def setUp(self):
        setup_common_reference_data()

    def test_read_excel_file(self):
        file = "plan_visual_django/tests/resources/input_files/excel_plan_files/PV-Test-01.xlsx"

        file_reader = ExcelXLSFileReader(sheet_name="PV-Test-01")
        raw_data = file_reader.read(file)
        plan_field_mapping_type = PlanFieldMappingType.objects.all()[0]
        parsed_data = file_reader.parse(raw_data, plan_field_mapping=plan_field_mapping_type)

        pass