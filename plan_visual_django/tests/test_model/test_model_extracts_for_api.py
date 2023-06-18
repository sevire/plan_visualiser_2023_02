from django.test import TestCase
from ddt import ddt, data, unpack

from plan_visual_django.models import PlanVisual
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_reference_data, \
    setup_common_plan_data


@ddt
class TestModelExtracts(TestCase):
    def setUp(self):
        self.user, self.file_type, self.plotable_shapes = setup_common_reference_data()
        self.plans, self.visuals, self.visual_activities = setup_common_plan_data(self.user, self.file_type, self.plotable_shapes)

    def test_get_activity_data(self):
        visual = self.visuals[0]
        activities = visual.get_visual_activities()
        pass
