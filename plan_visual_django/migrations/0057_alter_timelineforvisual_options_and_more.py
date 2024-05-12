# Generated by Django 5.0 on 2024-03-31 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0056_alter_swimlaneforvisual_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="timelineforvisual",
            options={"ordering": ["plan_visual", "sequence_number"]},
        ),
        migrations.AddField(
            model_name="timelineforvisual",
            name="sequence_number",
            field=models.IntegerField(default=23),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="timelineforvisual",
            unique_together={("plan_visual", "sequence_number")},
        ),
    ]
