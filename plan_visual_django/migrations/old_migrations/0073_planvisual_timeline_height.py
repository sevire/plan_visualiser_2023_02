# Generated by Django 5.1.1 on 2024-10-13 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "plan_visual_django",
            "0072_remove_planmappedfield_plan_field_mapping_type_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="planvisual",
            name="timeline_height",
            field=models.FloatField(default=20),
        ),
    ]
