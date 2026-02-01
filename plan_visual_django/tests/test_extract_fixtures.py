import json
import os
from django.test import TestCase
from django.core.management import call_command
from plan_visual_django.models import PlanVisual

class TestExtractVisualFixtures(TestCase):
    # fixtures = ['plan_visual_django/tests/resources/test_fixtures/test_fixtures.json']

    def test_extract_visual_fixtures_command(self):
        # Create a visual manually since the fixture loading failed due to integrity errors
        from django.contrib.auth import get_user_model
        from plan_visual_django.models import Plan, PlanVisual, PlotableStyle, Color, Font
        
        User = get_user_model()
        user = User.objects.create(username="testuser")
        plan = Plan.objects.create(plan_name="Test Plan", user=user)
        
        color = Color.objects.create(name="Red", red=255, green=0, blue=0, user=user)
        font = Font.objects.create(font_name="Arial")
        style = PlotableStyle.objects.create(
            style_name="Test Style", 
            fill_color=color, 
            line_color=color, 
            font_color=color, 
            line_thickness=1,
            font=font, 
            font_size=10,
            user=user
        )
        
        visual = PlanVisual.objects.create(
            plan=plan, 
            name="Test Visual",
            default_activity_plotable_style=style,
            default_milestone_plotable_style=style,
            default_swimlane_plotable_style=style,
            default_timeline_plotable_style_odd=style
        )
        
        visual_id = visual.id
        output_file = 'test_extract_fixture.json'
        
        try:
            # Run the command
            call_command('extract_visual_fixtures', visual_id, output=output_file)
            
            # Check if file exists
            self.assertTrue(os.path.exists(output_file))
            
            # Load and verify content
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            
            # Verify PlanVisual is in the data
            model_names = [item['model'] for item in data]
            self.assertIn('plan_visual_django.planvisual', model_names)
            
            # Verify specific visual is there
            visual_pks = [item['pk'] for item in data if item['model'] == 'plan_visual_django.planvisual']
            self.assertIn(visual_id, visual_pks)

        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.remove(output_file)
