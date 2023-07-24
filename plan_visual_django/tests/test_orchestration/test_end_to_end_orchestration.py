from django.test import TestCase

from plan_visual_django.services.visual.renderers import CanvasRenderer
from plan_visual_django.services.visual.visual_settings import VisualSettings
from plan_visual_django.services.visual_orchestration.visual_orchestration import VisualOrchestration
from plan_visual_django.tests.resources.data_setup.common_data_setup import setup_common_data

"""
Tests the end to end flow of creating a visual from scratch.
"""


class TestEndToEndOrchestration(TestCase):
    def setUp(self):
        self.plan_records, self.visual_records, self.visual_activity_records = setup_common_data()

    def test_end_to_end(self):
        visual_settings = VisualSettings(width=600, height=300)
        visual_orchestrator = VisualOrchestration(self.visual_records[0], visual_settings)

        canvas_renderer = CanvasRenderer()
        canvas_data = canvas_renderer.plot_visual(visual_orchestrator.visual_collection)

        pass
