# Generated by Django 4.2.1 on 2023-10-07 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0053_alter_plotablestyle_options"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="planvisual", unique_together={("plan", "name")},
        ),
    ]