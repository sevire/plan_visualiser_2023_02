# Generated by Django 4.1.7 on 2023-03-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0003_alter_planfield_field_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planfield",
            name="field_name",
            field=models.CharField(
                choices=[
                    ("unique_sticky_activity_id", "Unique id for activity"),
                    ("activity_name", "Name of activity"),
                    ("duration", "Duration of activity"),
                    ("start_date", "Start date of activity"),
                    ("end_date", "End date of activity"),
                    ("level", "The level in the hierarchy of the an activity"),
                ],
                max_length=50,
            ),
        ),
    ]
