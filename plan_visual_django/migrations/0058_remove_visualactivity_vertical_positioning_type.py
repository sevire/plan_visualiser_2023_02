# Generated by Django 5.0.4 on 2024-08-28 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0057_alter_timelineforvisual_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="visualactivity", name="vertical_positioning_type",
        ),
    ]