# Generated by Django 4.1.7 on 2023-03-04 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0002_alter_planfieldmappingtype_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planfield",
            name="field_name",
            field=models.CharField(
                choices=[
                    (
                        "unique_sticky_activity_id",
                        "Unique id used to ensure that an activity can be remembered after changes to a plan",
                    ),
                    ("activity_name", "Name of the activity"),
                    ("duration", "Duration of activity"),
                    ("start_date", "Start date of activity"),
                    ("end_date", "End date of activity"),
                    (
                        "level",
                        "The level in the hierarchy of the an activity - allows hierarchy to be inferred",
                    ),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="planfieldmappingtype",
            name="name",
            field=models.CharField(max_length=50),
        ),
    ]
