from django.core.files import File
from django.test import TestCase
from plan_visual_django.models import PlanField, PlanFieldMappingType, PlanMappedField
from plan_visual_django.services.plan_reader import ExcelXLSFileReader


class TestReadExcelFile(TestCase):
    def setUp(cls):
        plan_field_mapping_type = PlanFieldMappingType.objects.create(
            name="Test-Excel-01",
            description="dummy for testing"
        )

        # Set up fields and types used within the app
        plan_fields = {
            "unique_sticky_activity_id": {"field_type": "STR", "required": True},
            "activity_name": {"field_type": "STR", "required": True},
            "activity_display_name": {"field_type": "STR", "required": False},
            "duration": {"field_type": "INT", "required": True},
            "start_date": {"field_type": "DATE", "required": True},
            "end_date": {"field_type": "DATE", "required": True},
            "level": {"field_type": "INT", "required": True},
        }

        for field_name, field_data in plan_fields.items():
            PlanField.objects.create(
                field_name=field_name,
                field_type=field_data['field_type'],
                field_description="testing",
                required_flag=field_data['required'],
                sort_index=50
            )

        # Setup mapping from input file fields to internally used plan fields
        cls.plan_field_mapping_type_01 = PlanFieldMappingType.objects.create(
            name="mapping-01",
            description="mapping-01 description"
        )

        field_mapping_01 = {
            "unique_sticky_activity_id": {"input_field_name": "Unique Sticky ID", "input_field_type": "STR"},
            "level": {"input_field_name": "Level #", "input_field_type": "FLOAT"},
            "activity_name": {"input_field_name": "Task Name", "input_field_type": "STR"},
            "duration": {"input_field_name": "Duration", "input_field_type": "STR_nnd"},
            "start_date": {"input_field_name": "Start", "input_field_type": "DATE"},
            "end_date": {"input_field_name": "Finish", "input_field_type": "DATE"},
        }

        for plan_field_record in PlanField.objects.all():
            plan_field_name = plan_field_record.field_name
            mandatory_flag = plan_field_record.required_flag

            if plan_field_name in field_mapping_01:
                input_field_name = field_mapping_01[plan_field_name]["input_field_name"]
                input_field_type = field_mapping_01[plan_field_name]["input_field_type"]

                PlanMappedField.objects.create(
                    plan_field_mapping_type=cls.plan_field_mapping_type_01,
                    mapped_field=PlanField.objects.get(field_name=plan_field_name),
                    input_field_name=input_field_name,
                    input_field_type=input_field_type
                )
            else:
                # Only a problem if the field is mandatory
                if mandatory_flag is True:
                    raise Exception(f"Compulsory field {plan_field_name} not included in test mapping data")

    def test_read_excel_file(self):
        file = "plan_visual_django/tests/resources/input_files/excel_plan_files/PV-Test-01.xlsx"

        file_reader = ExcelXLSFileReader()
        raw_data = file_reader.read(file)
        parsed_data = file_reader.parse(raw_data, plan_field_mapping=self.plan_field_mapping_type_01)

        pass