# Generated by Django 5.1.1 on 2024-10-14 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "plan_visual_django",
            "0080_alter_planvisual_default_timeline_plotable_style_even",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="timelineforvisual",
            name="enabled",
            field=models.BooleanField(default=False),
        ),
    ]
