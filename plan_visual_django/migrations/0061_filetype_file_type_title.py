# Generated by Django 5.0.4 on 2024-09-08 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0060_alter_filetype_file_type_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="filetype",
            name="file_type_title",
            field=models.CharField(default="dummy", max_length=50),
            preserve_default=False,
        ),
    ]
