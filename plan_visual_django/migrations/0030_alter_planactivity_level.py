# Generated by Django 4.2.1 on 2023-07-31 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0029_alter_planmappedfield_input_field_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planactivity",
            name="level",
            field=models.IntegerField(default=1),
        ),
    ]