# Generated by Django 4.2.1 on 2023-09-30 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0050_alter_plotableshape_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plotableshape",
            name="name",
            field=models.CharField(
                choices=[
                    ("RECTANGLE", "Rectangle"),
                    ("ROUNDED_RECTANGLE", "Rounded Rectangle"),
                    ("DIAMOND", "Diamond"),
                    ("ISOSCELES", "Isosceles Triangle"),
                ],
                max_length=50,
            ),
        ),
    ]
