"""
Tests the ability to read in files of different technical formats and correctly extract the data from them.

At the time of writing Excel is the only technical format supported, but this will be extended to include other
formats such as (native) MS Project at a later date.

While there is only one technical format, there will be differences and features of a file which we should manage, such
as blank lines, invalid data in a record, unexpected fields or missing fields etc.
"""
import os
from unittest import mock
from ddt import ddt, data, unpack
from django.core.files import File
from django.test import TestCase
from plan_visual_django.models import Plan, FileType
from plan_visual_django.services.plan_file_utilities.plan_reader import ExcelXLSFileReader
from plan_visual_django.tests.utilities import date_from_string
from plan_visual_django.tests.resources.test_configuration import \
    (test_data_base_folder, test_fixtures_folder, excel_input_files_folder)

# Define input file parameters and expected results separately as we may want the same data in various different input
# file variants (e.g. sheet name different), but the expected results will be the same - we don't want to have to copy
# the expected results for each variant.

# Named sheet, incorrect sheet name given, should fail
file_data_01 =  {  # Note that the data required here will vary for different file types (e.g. sheet name)
    'file_name': 'PV-Test-01.xlsx',
    'sheet_name': 'Sheet1',
    'plan_field_mapping_type': "Excel (SmartSheetDefault)"
}

# No sheet name, but only one sheet in file - should be fine.
file_data_02 =  {  # Note that the data required here will vary for different file types (e.g. sheet name)
    'file_name': 'PV-Test-02.xlsx',
    'sheet_name': None,
}

# Correct sheet name given, should be fine
file_data_03 =  {  # Note that the data required here will vary for different file types (e.g. sheet name)
    'file_name': 'PV-Test-01.xlsx',
    'sheet_name': 'PV-Test-01',
}

# If more than one sheet but not named, then should take first one
file_data_04 =  {  # Note that the data required here will vary for different file types (e.g. sheet name)
    'file_name': 'PV-Test-01.xlsx',
    'sheet_name': 'PV-Test-01',
}

file_data_05 = {
    'file_name': 'SCM_plan_v3_21_July.xlsx',
    'sheet_name': 'Task_Data'
}

expected_result_file_01 = {
    'file_data': {
        'file_read_status': 'failure',
    }
}

expected_result_file_02 = {
    'file_data': {
        'file_read_status': 'success',
        'num_valid_activities': 7
    }
}

expected_result_activity_01 = {
    'activity_data': [
        {
            'activity_sequence_number': 1,  # Note this isn't the 'sticky' id, that won't always be here
            'Unique Sticky ID': "ID-0007",
            'Level #': 0.0,
            'Name': 'Project Start',
            'Start': date_from_string('2023-01-01'),
            'Finish': date_from_string('2023-01-01'),
            'Duration': "0",
        },
        {
            'activity_sequence_number': 4,  # Note this isn't the 'sticky' id, that won't always be here
            'Unique Sticky ID': "ID-0005",
            'Level #': 2.0,
            'Name': 'Activity 5',
            'Start': date_from_string('2023-01-02'),
            'Finish': date_from_string('2023-01-13'),
            'Duration': "10d",
        },
        {
            'activity_sequence_number': 7,  # Note this isn't the 'sticky' id, that won't always be here
            'Unique Sticky ID': "ID-0004",
            'Level #': 0.0,
            'Name': 'Activity 4',
            'Start': date_from_string('2023-01-30'),
            'Finish': date_from_string('2023-02-10'),
            'Duration': "10d",
        }
    ]
}

file_format_test_cases = [
    {
        'file_reader': ExcelXLSFileReader,
        'test_files': [
            {
                'file_data': {  # Note that the data required here will vary for different file types (e.g. sheet name)
                    'file_name': 'PV-Test-02.xlsx',
                    'sheet_name': None,
                    'file_type': "Excel (modern) Smartsheet Export"
                },
                'expected_result_file': expected_result_file_02,
                'expected_result_activity': expected_result_activity_01  # As we expect an error reading the file, there will be no activities
            },
            {
                'file_data': {  # Note that the data required here will vary for different file types (e.g. sheet name)
                    'file_name': 'PV-Test-01.xlsx',
                    'sheet_name': 'PV-Test-01',
                    'file_type': "Excel (modern) Smartsheet Export"
                },
                'expected_result_file': expected_result_file_02,
                'expected_result_activity': expected_result_activity_01
            },
        ]
    },
]


def test_data_gen():
    """
    Generates a stream of input parameters to the test to allow each test to take place with a single assert so that
    any failures do not prevent a further test from being run.

    There will be a test for various properties of the file and then for each valid activity once the file has been
    read.

    NOTE: we are at this point only intersted in the input value of the data, not how it is converted to the plan field
    value.
    :return:
    """
    # Iterate through all the test cases - various test files for each file_reader class.
    for file_format_test_case in file_format_test_cases:
        file_reader = file_format_test_case['file_reader']

        # Iterate through the test_files to be tested with this reader class.
        for test_file in file_format_test_case['test_files']:
            test_file_data = test_file['file_data']
            expected_result_file = test_file['expected_result_file']['file_data']
            expected_result_activity = test_file['expected_result_activity']

            # First test the file level properties - such as number of activities found.
            # Each record provides information about what we expect to see when reading in this file.
            for exp_file_result_name, expected_file_result_value in expected_result_file.items():
                yield "file_level", exp_file_result_name, expected_file_result_value, \
                    None, file_reader, test_file_data

            # Now test the activity level properties
            if expected_result_activity is not None:
                activity_records = expected_result_activity['activity_data']
                for activity_record in activity_records:

                    # The sequence number is used to extract the record from the input file we are testing, once we've read
                    # the valid records from the file.  It's not a property of the file itself.
                    sequence_number = activity_record['activity_sequence_number']

                    for exp_activity_result_name, expected_activity_result_value in activity_record.items():
                        if exp_activity_result_name != 'activity_sequence_number':
                            yield "activity_level", exp_activity_result_name, expected_activity_result_value, \
                                sequence_number, file_reader, test_file_data


@ddt
class TestTechnicalFileFormat(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]

    @data(*test_data_gen())
    @unpack
    def test_technical_file_read(
            self,
            test_type,
            expected_result_name,
            expected_result_value,
            sequence_number,  # This is only used for activity level tests
            file_reader,
            file_data
    ):
        """
        Test the ability to read in a file of a given format and extract the data from it.  There will be some
        conditional logic based on the input reader type (e.g. Excel requires a sheet name, but CSV wouldn't).

        :param file_reader:
        :param file_data:
        :param test_type:
        :param expected_result_name:
        :param expected_result_value:
        :return:
        """
        print(f"file name {file_data['file_name']}, expected_result_name:{expected_result_name}, expected_result_value:{expected_result_value}")
        file_error_expected = False

        # Create mapping type object which will be used to work out which sheet we will find the plan data in.
        file_type = FileType(file_type_name=file_data['file_type'])

        # Read the file - slightly different logic for each reader.
        file_path = os.path.join(excel_input_files_folder, file_data['file_name'])
        file = File(file=file_path)
        if file_reader == ExcelXLSFileReader:
            # We need to create a Plan object to pass to the File Reader object.
            plan_object = mock.Mock(spec=Plan)
            plan_object.file_type = file_type
            plan_object.file = file
            plan_object.file_name = file_data['file_name']
            file_reader_object = ExcelXLSFileReader()

            # Check whether we are expecting a failure for this file and if so, whether we get one.
            if expected_result_name == 'file_read_status' and expected_result_value == 'failure':
                file_error_expected = True  # Will use to supress reading file if we are expecting an error
                with self.assertRaises(Exception):
                    file_reader_object.read(plan_object)
        else:
            self.fail(f"Unrecognised file reader type {file_reader}")

        # Now check the results of the file read.  Note, won't get here if we were expecting a failure.
        if not file_error_expected:
            input_data_from_file, headings = file_reader_object.read(plan_object)

            if test_type == "file_level":
                if expected_result_name == "num_valid_activities":
                    self.assertEqual(len(input_data_from_file), expected_result_value)
                elif expected_result_name == "file_read_status":
                    # Don't need to do anything as an expected failure is caught earlier
                    pass
                else:
                    self.fail(f"Unrecognised file level test {expected_result_name}")

            elif test_type == "activity_level":
                record = input_data_from_file[sequence_number-1]
                value = record[expected_result_name]
                self.assertEqual(value, expected_result_value ,f"Test type {test_type}, expected result name {expected_result_name}")







