from datetime import datetime
from ddt import ddt
from django.test import TestCase

from plan_visual_django.models import PlanField

test_plan_data = [
    ("001", "activity-01", 5, datetime(year=2021, month=11, day=30), datetime(year=2021, month=12, day=4), 1)
]

def gen_test_plan_data():
    for plan_record in test_plan_data:
        sticky_id, name, duration, start, end, level = plan_record
        yield sticky_id, name, duration, start, end, level

@ddt
class TestApiGetPlanData(TestCase):
    fixtures = ["test_fixtures.json"]

    def test_01(self):
        """
        Just check that test data from fixtures has been correctly placed in database.
        :return:
        """
        planfields = PlanField.objects.all()
        planfield_names = [record.field_name for record in planfields]

        self.assertTrue('unique_sticky_activity_id' in planfield_names)
        self.assertTrue('start_date' in planfield_names)
        self.assertTrue('end_date' in planfield_names)
        self.assertTrue('duration' in planfield_names)