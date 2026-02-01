from django.core.management.base import BaseCommand
from plan_visual_django.models import PlanVisual, PlanActivity, TimelineForVisual, SwimlaneForVisual, VisualActivity, PlotableStyle, Color, Font
from django.core import serializers
import json

class Command(BaseCommand):
    help = "Extracts all relevant records for a given plan visual instance to a fixtures file."

    def add_arguments(self, parser):
        parser.add_argument("visual_id", type=int, help="The ID of the PlanVisual to extract.")
        parser.add_argument("--output", type=str, help="The output file path. Defaults to <visual_name>_fixture.json")

    def handle(self, *args, **options):
        visual_id = options['visual_id']
        try:
            visual = PlanVisual.objects.get(pk=visual_id)
        except PlanVisual.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"PlanVisual with ID {visual_id} does not exist."))
            return

        self.stdout.write(f"Extracting records for visual: {visual.name} (ID: {visual_id})")

        objects_to_serialize = []
        
        # 1. The PlanVisual itself
        objects_to_serialize.append(visual)
        
        # 2. The associated Plan
        plan = visual.plan
        objects_to_serialize.append(plan)
        
        # 3. All PlanActivity records for that plan
        plan_activities = PlanActivity.objects.filter(plan=plan)
        objects_to_serialize.extend(list(plan_activities))
        
        # 4. All TimelineForVisual records for the visual
        timelines = TimelineForVisual.objects.filter(plan_visual=visual)
        objects_to_serialize.extend(list(timelines))
        
        # 5. All SwimlaneForVisual records for the visual
        swimlanes = SwimlaneForVisual.objects.filter(plan_visual=visual)
        objects_to_serialize.extend(list(swimlanes))
        
        # 6. All VisualActivity records for the visual
        visual_activities = VisualActivity.objects.filter(visual=visual)
        objects_to_serialize.extend(list(visual_activities))
        
        # 7. Styles, Colors, Fonts and Users
        # We need to collect all styles used across all related objects
        styles = set()
        
        # Styles from PlanVisual
        if visual.default_activity_plotable_style:
            styles.add(visual.default_activity_plotable_style)
        if visual.default_milestone_plotable_style:
            styles.add(visual.default_milestone_plotable_style)
        if visual.default_swimlane_plotable_style:
            styles.add(visual.default_swimlane_plotable_style)
        if visual.default_timeline_plotable_style_odd:
            styles.add(visual.default_timeline_plotable_style_odd)
        if visual.default_timeline_plotable_style_even:
            styles.add(visual.default_timeline_plotable_style_even)
            
        # Styles from Timelines
        for timeline in timelines:
            if timeline.plotable_style_odd:
                styles.add(timeline.plotable_style_odd)
            if timeline.plotable_style_even:
                styles.add(timeline.plotable_style_even)
                
        # Styles from Swimlanes
        for swimlane in swimlanes:
            if swimlane.plotable_style:
                styles.add(swimlane.plotable_style)
            
        # Styles from VisualActivities
        for va in visual_activities:
            if va.plotable_style:
                styles.add(va.plotable_style)
            
        objects_to_serialize.extend(list(styles))
        
        # Now collect colors, fonts and users from styles
        colors = set()
        fonts = set()
        users = set()
        
        if plan.user:
            users.add(plan.user)
            
        # Collects style attributes for serialization
        for style in styles:
            if style.fill_color:
                colors.add(style.fill_color)
            if style.line_color:
                colors.add(style.line_color)
            if style.font_color:
                colors.add(style.font_color)
            if style.font:
                fonts.add(style.font)
            if style.user:
                users.add(style.user)
            
        # Also colors have users
        for color in colors:
            if color.user:
                users.add(color.user)
            
        objects_to_serialize.extend(list(fonts))
        objects_to_serialize.extend(list(colors))
        objects_to_serialize.extend(list(users))
        
        # Serialize to JSON
        data = serializers.serialize("json", objects_to_serialize, indent=4)
        
        output_path = options['output']
        if not output_path:
            # Clean name for filename
            clean_name = "".join([c if c.isalnum() else "_" for c in visual.name])
            output_path = f"{clean_name}_fixture.json"
            
        with open(output_path, 'w') as f:
            f.write(data)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully extracted {len(objects_to_serialize)} records to {output_path}"))
