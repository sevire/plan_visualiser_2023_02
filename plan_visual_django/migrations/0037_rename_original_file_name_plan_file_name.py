# Generated by Django 4.2.1 on 2023-08-09 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0036_plan_plan_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="plan", old_name="original_file_name", new_name="file_name",
        ),
    ]