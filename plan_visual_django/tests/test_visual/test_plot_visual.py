from django.test import TestCase
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_reference_data, \
    setup_common_data


class TestPlotVisual(TestCase):
    def setUp(self):
        self.plan_records, self.visual_records, self.visual_activity_records = setup_common_data()

