# Generated by Django 4.2.1 on 2023-06-27 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0022_swimlaneforvisual_plotable_style"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planmappedfield",
            name="input_field_type",
            field=models.CharField(
                choices=[
                    ("INT", "Integer"),
                    ("FLOAT", "Decimal Number"),
                    ("STR", "String"),
                    ("STR_OR_INT", "String or integer"),
                    ("STR_nnd", "String of form nnd where nn is an integer value"),
                    ("DATE", "Date (without time"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="visualactivity",
            name="text_flow",
            field=models.CharField(
                choices=[
                    ("LFLOW", "Align right, flow to left"),
                    ("RFLOW", "Align left, flow to right"),
                    ("WSHAPE", "Align centre, flow left/right"),
                    ("CLIPPED", "Align centre, clipped to shape"),
                    ("CENTRE", "Align centre"),
                ],
                max_length=20,
            ),
        ),
    ]
