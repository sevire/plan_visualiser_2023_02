from datetime import datetime
from django.contrib.auth.models import User
from plan_visual_django.models import PlanFieldMappingType, PlanField, PlanMappedField, PlanVisual, FileType, Plan, \
    PlanActivity, SwimlaneForVisual, PlotableShapeType, PlotableShape, Color, Font, PlotableStyle, VisualActivity, \
    TimelineForVisual
from plan_visual_django.tests.resources.data_setup.common_data import plan_fields, field_mapping_01, \
    plotable_shape_type_data, colour_data, timeline_for_visual_data, plotable_shape_data


def setup_common_reference_data():
    plan_field_mapping_type = PlanFieldMappingType.objects.create(
        name="Test-Excel-01",
        description="dummy for testing"
    )

    for field_name, field_data in plan_fields.items():
        PlanField.objects.create(
            field_name=field_name,
            field_type=field_data['field_type'],
            field_description="testing",
            required_flag=field_data['required'],
            sort_index=50
        )

    for plan_field_record in PlanField.objects.all():
        plan_field_name = plan_field_record.field_name
        mandatory_flag = plan_field_record.required_flag

        if plan_field_name in field_mapping_01:
            input_field_name = field_mapping_01[plan_field_name]["input_field_name"]
            input_field_type = field_mapping_01[plan_field_name]["input_field_type"]
            mapped_fields = PlanField.objects.filter(field_name=plan_field_name)  # Should only be one!
            print(f"Num mapped fields for {plan_field_name} = {len(mapped_fields)}")
            PlanMappedField.objects.create(
                plan_field_mapping_type=plan_field_mapping_type,
                mapped_field=mapped_fields[0],
                input_field_name=input_field_name,
                input_field_type=input_field_type
            )
        else:
            # Only a problem if the field is mandatory
            if mandatory_flag is True:
                raise Exception(f"Compulsory field {plan_field_name} not included in test mapping data")

    # Set up File Type record
    file_type = FileType.objects.create(
        file_type_name="dummy filename",
        file_type_description="dummy description",
        plan_field_mapping_type=plan_field_mapping_type
    )

    user = User.objects.create_user(username='testuser', password='12345')

    plotable_shape_types = [PlotableShapeType.objects.create(**shape_data) for shape_data in plotable_shape_type_data]
    plotable_shapes = [PlotableShape.objects.create(shape_type=plotable_shape_types[0], **shape_data) for shape_data in plotable_shape_data]

    # Return objects which may be needed in other test setup activities
    return user, file_type, plotable_shapes


def setup_common_plan_data(user, file_type, plotable_shapes):
    """
    Sets up actual plan data (rather than all the reference data which is required before we start)

    :return:
    """
    colour_records = []
    for colour_parameters in colour_data:
        colour_parameters.update({'user_id': user.id})
        colour_records.append(Color.objects.create(**colour_parameters))

    font_data = [
        {
            'font_name': "Ariel"
        }
    ]

    font_records = [Font.objects.create(**font_parameters) for font_parameters in font_data]

    plotable_style_data = [
        {
            "user_id": user.id,
            "style_name": "style-01",
            "fill_color": colour_records[0],
            "line_color": colour_records[0],
            "line_thickness": 10,
            "font": font_records[0],
            "font_color": colour_records[0]
        }
    ]

    plotable_style_records = [PlotableStyle.objects.create(**style_parameters) for style_parameters in plotable_style_data]

    # Set up a plan record to hook all the activities and other stuff from.
    plan_data = [
        {
            'user': user,
            'file_name': "dummy",
            'file': "dummy",
            'file_type': file_type
        }
    ]

    plan_records = [Plan.objects.create(**plan_record) for plan_record in plan_data]

    visual_data = [
        {
            'plan': plan_records[0],
            'name': "test-plan-01",
            'width': 400,
            'max_height': 300,
            'include_title': True,
            'track_height': 10,
            'track_gap': 3,
            'milestone_width': 8,
            'swimlane_gap': 3,
            'default_milestone_shape': plotable_shapes[0],
            'default_activity_shape': plotable_shapes[0],
            'default_activity_plotable_style': plotable_style_records[0],
            'default_milestone_plotable_style': plotable_style_records[0],
            'default_swimlane_plotable_style': plotable_style_records[0],
        }
    ]

    visual_records = [PlanVisual.objects.create(**visual_record) for visual_record in visual_data]

    swimlane = SwimlaneForVisual.objects.create(
        plan_visual=visual_records[0],
        swim_lane_name="Swimlane-01",
        sequence_number=1,
        plotable_style=plotable_style_records[0]
    )

    plan_activity_data = [
        {
            'plan': plan_records[0],
            'activities': [
                {
                    "unique_sticky_activity_id": "A-001",
                    "activity_name": "Activity-01",
                    "start_date": datetime(year=2023, month=1, day=1),
                    "end_date": datetime(year=2023, month=1, day=10),
                    "level": 1,
                },
                {
                    "unique_sticky_activity_id": "A-002",
                    "activity_name": "Activity-02",
                    "start_date": datetime(year=2023, month=1, day=10),
                    "end_date": datetime(year=2023, month=1, day=20),
                    "level": 1,
                }
            ]
        }
    ]

    for plan_record in plan_activity_data:
        plan = plan_record['plan']
        for activity_data in plan_record['activities']:
            activity_data['plan'] = plan
            PlanActivity.objects.create(**activity_data)

    plan_visual_data = [
        {
            'visual': visual_records[0],
            'activities': [
                {
                    'unique_id_from_plan': "A-001",
                    'enabled': True,
                    'swimlane': swimlane,
                    'plotable_shape': plotable_shapes[0],
                    'vertical_positioning_type': "TRACK",
                    'vertical_positioning_value': 1,
                    'height_in_tracks': 1,
                    'text_horizontal_alignment': VisualActivity.HorizontalAlignment.LEFT,
                    'text_vertical_alignment': VisualActivity.VerticalAlignment.MIDDLE,
                    'text_flow': "LFLOW",
                    'plotable_style': plotable_style_records[0],
                },
                {
                    'unique_id_from_plan': "A-002",
                    'enabled': True,
                    'swimlane': swimlane,
                    'plotable_shape': plotable_shapes[0],
                    'vertical_positioning_type': "TRACK",
                    'vertical_positioning_value': 1,
                    'height_in_tracks': 1,
                    'text_horizontal_alignment': VisualActivity.HorizontalAlignment.LEFT,
                    'text_vertical_alignment': VisualActivity.VerticalAlignment.MIDDLE,
                    'text_flow': "LFLOW",
                    'plotable_style': plotable_style_records[0],
                }
            ]
        }
    ]

    timeline_objects = [
        TimelineForVisual.objects.create(
            plan_visual=visual_records[0],
            timeline_type=timeline_record["timeline_type"],
            timeline_name=timeline_record["timeline_name"],
            plotable_style=plotable_style_records[0],
            sequence_number=timeline_record["sequence_number"]
        )
        for timeline_record in timeline_for_visual_data
    ]

    visual_activity_records = []
    for visual_activity_data in plan_visual_data:
        visual = visual_activity_data['visual']
        visual_data_records = visual_activity_data['activities']
        for record in visual_data_records:
            record['visual'] = visual
            activity = VisualActivity.objects.create(**record)
            visual_activity_records.append(activity)

    return plan_records, visual_records, visual_activity_records, timeline_objects


def setup_common_data():
    user, file_type, plotable_shapes = setup_common_reference_data()
    plan_records, visual_records, visual_activity_records, timeline_records = setup_common_plan_data(user, file_type, plotable_shapes)

    return plan_records, visual_records, visual_activity_records
