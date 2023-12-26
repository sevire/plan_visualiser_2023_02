"""
Create unit tests to test the creation of PlanField entries from the django model
"""
from ddt import ddt, data, unpack
from django.test import TestCase
from model_bakery import baker

from plan_visual_django.models import PlanField
from plan_visual_django.tests_new.resources.utilities import generate_test_data_field_stream


@ddt
class TestPlanFieldCreation(TestCase):
    fixtures = ['plan_visual_django/tests_new/resources/fixtures/plan_fields.json']

    def test_plan_field_creation(self):
        self.plan_fields = PlanField.objects.all()
        self.assertEqual(7, self.plan_fields.count())

    @data(
        *generate_test_data_field_stream(
            ["value", "is_stored", "label"],
            [
                (PlanField.PlanFieldName.STICKY_UID, "unique_sticky_activity_id", True, "Unique id for activity"),
                (PlanField.PlanFieldName.NAME, "activity_name", True, None),
                (PlanField.PlanFieldName.DURATION, "duration", False, None),
                (PlanField.PlanFieldName.MILESTONE_FLAG, "milestone_flag", True, None),
                (PlanField.PlanFieldName.START, "start_date", True, None),
                (PlanField.PlanFieldName.END, "end_date", True, None),
                (PlanField.PlanFieldName.LEVEL, "level", True, None),
            ])
    )
    @unpack
    def test_plan_field_name(self, plan_field_name: PlanField.PlanFieldName, field_name, expected_value):
        if field_name == "label":
            # We are testing the label (the last field passed to each choices value), which is stored automatically and
            # exposed via the choices property.
            # Not testing exact value of label, just that it exists and is a non-empty string.
            label = plan_field_name.label
            self.assertTrue(isinstance(label, str) and len(label)>0)
        else:
            self.assertEqual(getattr(plan_field_name, field_name), expected_value)

