import django.test
from ddt import ddt, data, unpack
from plan_visual_django.models import PlanMappedField
from plan_visual_django.services.plan_file_utilities.plan_field import RefactoredPlanField, PlanFieldEnum, \
    StoredPlanFieldTypeEnum
from plan_visual_django.services.plan_file_utilities.plan_reader import convert_dispatch
from plan_visual_django.tests.resources.utilities import date_from_string

"""
Tests that incoming fields from plan upload can be processed sensibly, coping when the field isn't 
populated cleanly.

Particularly for data imported from an Excel file exported from the source planning app,
it's not possible to be sure that the data type or value of fields will always be as expected.
For example a field which is blank in the original plan might end up as a blank or zero on the Excel 
export of the plan.
"""

# Mirroring definition of all fields required for the visual, and expected to be present in the imported
# file.


plan_fields = {
    PlanFieldEnum.STICKY_UID: {
        "field_type": StoredPlanFieldTypeEnum.STRING.value
    },
    PlanFieldEnum.DURATION: {
        "field_type": StoredPlanFieldTypeEnum.INTEGER.value
    },
    PlanFieldEnum.NAME: {
        "field_type": StoredPlanFieldTypeEnum.STRING.value
    },
    PlanFieldEnum.START: {
        "field_type": StoredPlanFieldTypeEnum.DATE.value
    },
    PlanFieldEnum.END: {
        "field_type": StoredPlanFieldTypeEnum.DATE.value
    },
    PlanFieldEnum.LEVEL: {
        "field_type": StoredPlanFieldTypeEnum.INTEGER.value
    },
}
plan_field_mappings = {
    'SmartSheetExcelExport(Default)': {
        PlanFieldEnum.STICKY_UID: {
            "input_field_name": "Unique Sticky ID",
            "input_field_type": PlanMappedField.PlanFieldType.STRING_OR_INT
        },
        PlanFieldEnum.DURATION: {
            "input_field_name": "Duration",
            "input_field_type": PlanMappedField.PlanFieldType.STRING_nnd
        },
        PlanFieldEnum.NAME: {
            "input_field_name": "Task Name",
            "input_field_type": PlanMappedField.PlanFieldType.STRING
        },
        PlanFieldEnum.START: {
            "input_field_name": "Start",
            "input_field_type": PlanMappedField.PlanFieldType.DATE
        },
        PlanFieldEnum.END: {
            "input_field_name": "End",
            "input_field_type": PlanMappedField.PlanFieldType.DATE
        },
        PlanFieldEnum.LEVEL: {
            "input_field_name": "Duration",
            "input_field_type": PlanMappedField.PlanFieldType.INTEGER
        }
    }
}

import_field_test_cases = [
    {
        "field_mapping_type": 'SmartSheetExcelExport(Default)',
        "fields": [
            {
                "plan_field_name": PlanFieldEnum.STICKY_UID,
                "test_cases": [
                    {
                        "description": "Normal pass through string",
                        "input_field_value": "ID-00",
                        "expected_parsed_value": "ID-00"
                    },
                    {
                        "description": "Pass through string with space in middle",
                        "input_field_value": "ID 00",
                        "expected_parsed_value": "ID 00"
                    },
                    {
                        "description": "Normal pass through string with space at beginning",
                        "input_field_value": " ID-00",
                        "expected_parsed_value": " ID-00"
                    },
                    {
                        "description": "Normal pass through string with space at end",
                        "input_field_value": "ID-00 ",
                        "expected_parsed_value": "ID-00 "
                    },
                    {
                        "description": "Integer",
                        "input_field_value": 0,
                        "expected_parsed_value": "0"
                    }
                ]
            },
            {
                "plan_field_name": PlanFieldEnum.DURATION,
                "test_cases": [
                    {
                        "description": "String representing integer with d at end",
                        "input_field_value": "123d",
                        "expected_parsed_value": 123
                    },
                    {
                        "description": "Integer: 0",
                        "input_field_value": 0,
                        "expected_parsed_value": "ValueError"
                    },
                    {
                        "description": "Integer: Non zero",
                        "input_field_value": 1,
                        "expected_parsed_value": "ValueError"
                    },
                    {
                        "description": "Integer: Non zero",
                        "input_field_value": 1.1,
                        "expected_parsed_value": "ValueError"
                    }
                ]
            },
            {
                "plan_field_name": PlanFieldEnum.NAME,
                "test_cases": [
                    {
                        "description": "Checking strings are passed through exactly",
                        "input_field_value": "yyy",
                        "expected_parsed_value": "yyy"
                    },
                ]
            },
            {
                "plan_field_name": PlanFieldEnum.START,
                "test_cases": [
                    {
                        "description": "Checking dates are converted correctly. Note dates are imported as true Excel dates not strings",
                        "input_field_value": date_from_string("2022-01-01"),
                        "expected_parsed_value": date_from_string("2022-01-01")
                    },
                ]
            },
            {
                "plan_field_name": PlanFieldEnum.END,
                "test_cases": [
                    {
                        "description": "Checking dates are converted correctly. Note dates are imported as true Excel dates not strings",
                        "input_field_value": date_from_string("2022-01-01"),
                        "expected_parsed_value": date_from_string("2022-01-01")
                    },
                ]
            },
            {
                "plan_field_name": PlanFieldEnum.LEVEL,
                "test_cases": [
                    {
                        "description": "Level should come in as an integer and is output as the same integer",
                        "input_field_value": 999,
                        "expected_parsed_value": 999
                    },
                ]
            }
        ]
    }
]


def import_field_test_data_gen():
    for import_mapping_type_cases in import_field_test_cases:
        mapping_type = import_mapping_type_cases['field_mapping_type']
        for field_record in import_mapping_type_cases['fields']:
            field_name = field_record['plan_field_name']
            output_type = plan_fields[field_name]['field_type']
            input_field_type = plan_field_mappings[mapping_type][field_name]['input_field_type']
            for case in field_record['test_cases']:
                description = case['description']
                input_value = case['input_field_value']
                expected_result = case['expected_parsed_value']
                yield input_field_type, field_name, output_type, input_value, expected_result, description


@ddt
class TestPlanFileFieldImport(django.test.TestCase):
    @data(*import_field_test_data_gen())
    @unpack
    def test_imported_field_parsing(
            self,
            input_field_type,
            field_name,
            output_type,
            input_value,
            expected_result,
            description
    ):
        message = f"Field:{field_name}, case:{description}"
        if expected_result == "ValueError":
            self.assertRaises(ValueError, convert_dispatch, input_field_type, output_type, input_value)
        else:
            output_value = convert_dispatch(input_field_type, output_type, input_value)
            self.assertEqual(output_value, expected_result, msg=message)
