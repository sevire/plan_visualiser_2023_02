"""
Tests end to end functionality of the plan upload process, from file upload to database storage.

Reads a number of test files, and checks that the data is correctly stored in the database.
"""
import os
from unittest import mock

from ddt import ddt, data, unpack
from django.core.files import File
from django.forms import FileField
from django.test import TestCase

from plan_visual_django.models import Plan, FileType
from plan_visual_django.services.plan_file_utilities.plan_parsing import read_and_parse_plan
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.tests.test_settings import EXCEL_PLAN_FILE_FOLDER
from plan_visual_django.tests.resources.test_configuration import test_data_base_folder, test_fixtures_folder


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

    def test_file_read_and_parse(self):
        """
        Tests that a file can be read and parsed, and the data stored in the database.
        :return:
        """
        # Read an input file, then parse it using the field mapping type to populate the plan fields.
        # Then check that the data is correctly stored in the database.

        input_file_name = "D365 CRM Plan_10102023.xlsx"
        input_file_path = os.path.join(EXCEL_PLAN_FILE_FOLDER, input_file_name)

        # Read the appropriate file type from the database so use for this file
        file_type_name = "Excel (modern) MSP Export"
        file_type = FileType.objects.get(file_type_name=file_type_name)

        # Create a plan object to attach the activities from the file to
        plan_name = "Test plan"
        file_name = input_file_name
        file = FileField()
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = file_name

        plan = Plan.objects.create(
            user_id=1,  # ToDo: Replace hard-coding with something a bit better!
            plan_name=plan_name,
            file_name=file_name,
            file=file_mock,
            file_type=file_type)

        file_reader = ExcelXLSFileReader()
        input_file_data = read_and_parse_plan(plan, input_file_path, file_type.plan_field_mapping_type, file_reader)

        pass

