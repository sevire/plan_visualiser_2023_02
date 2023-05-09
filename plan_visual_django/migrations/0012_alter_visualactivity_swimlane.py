# Generated by Django 4.1.7 on 2023-04-30 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0011_alter_visualactivity_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visualactivity",
            name="swimlane",
            field=models.ForeignKey(
                limit_choices_to={
                    "plan_visual": models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="plan_visual_django.planvisual",
                    )
                },
                on_delete=django.db.models.deletion.CASCADE,
                to="plan_visual_django.swimlaneforvisual",
            ),
        ),
    ]
