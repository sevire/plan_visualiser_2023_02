from django.test import TestCase
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_reference_data


class TestPlotVisual(TestCase):
    def setUp(self):
        setup_common_reference_data()
