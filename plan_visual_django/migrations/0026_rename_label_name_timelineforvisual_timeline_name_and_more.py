# Generated by Django 4.2.1 on 2023-07-08 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "plan_visual_django",
            "0025_rename_timelinelabelsforvisual_timelineforvisual_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="timelineforvisual",
            old_name="label_name",
            new_name="timeline_name",
        ),
        migrations.RenameField(
            model_name="timelineforvisual",
            old_name="label_type",
            new_name="timeline_type",
        ),
    ]
