# Generated by Django 4.1.7 on 2023-06-01 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0015_alter_swimlaneforvisual_swim_lane_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="swimlaneforvisual",
            name="sequence_number",
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
