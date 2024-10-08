# Generated by Django 5.1.1 on 2024-09-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0061_filetype_file_type_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plotableshape",
            name="name",
            field=models.CharField(
                choices=[
                    ("RECTANGLE", "Rectangle"),
                    ("ROUNDED_RECTANGLE", "Rounded Rectangle"),
                    ("BULLET", "Bullet"),
                    ("DIAMOND", "Diamond"),
                    ("ISOSCELES", "Isosceles Triangle"),
                ],
                max_length=50,
            ),
        ),
    ]
