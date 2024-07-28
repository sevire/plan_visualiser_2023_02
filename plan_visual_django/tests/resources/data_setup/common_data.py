# Set up fields and types used within the app
from plan_visual_django.models import TimelineForVisual

plan_fields = {
    "unique_sticky_activity_id": {"field_type": "STR", "required": True},
    "activity_name": {"field_type": "STR", "required": True},
    "activity_display_name": {"field_type": "STR", "required": False},
    "duration": {"field_type": "INT", "required": True},
    "start_date": {"field_type": "DATE", "required": True},
    "end_date": {"field_type": "DATE", "required": True},
    "level": {"field_type": "INT", "required": True},
}

field_mapping_01 = {
    "unique_sticky_activity_id": {"input_field_name": "Unique Sticky ID", "input_field_type": "STR"},
    "level": {"input_field_name": "Level #", "input_field_type": "FLOAT"},
    "activity_name": {"input_field_name": "Task Name", "input_field_type": "STR"},
    "duration": {"input_field_name": "Duration", "input_field_type": "STR_nnd"},
    "start_date": {"input_field_name": "Start", "input_field_type": "DATE"},
    "end_date": {"input_field_name": "Finish", "input_field_type": "DATE"},
}

plotable_shape_type_data = [
    {
        'name': "RECTANGLE_BASED"
    }
]

plotable_shape_data = [
    {
        'name': "RECTANGLE",
    }
]

timeline_for_visual_data = [
    {
        "plan_visual": None,  # To be filled in before creating test object.
        "timeline_type": TimelineForVisual.TimelineLabelType.MONTHS,
        "timeline_name": "Test: Months",
        "plotable_style": None,  # To be filled in during object creation
        "sequence_number": 1
    },
    # {
    #     "plan_visual": None,  # To be filled in before creating test object.
    #     "timeline_type": TimelineForVisual.TimelineLabelType.QUARTERS,
    #     "timeline_name": "Test: Quarters",
    #     "plotable_style": None  # To be filled in during objecct creation
    # }
]

colour_data = [
    {
        "name": "Green",
        "red": 0,
        "green": 255,
        "blue": 0,
        "alpha": 0,
    }
]
