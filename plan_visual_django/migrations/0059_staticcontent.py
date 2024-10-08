# Generated by Django 5.0.4 on 2024-08-29 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0058_remove_visualactivity_vertical_positioning_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaticContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
            ],
        ),
    ]