# Generated by Django 4.1.7 on 2023-04-03 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0008_planactivity_plan"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="swimlaneforvisual",
            unique_together={("plan_visual", "swim_lane_name")},
        ),
    ]
