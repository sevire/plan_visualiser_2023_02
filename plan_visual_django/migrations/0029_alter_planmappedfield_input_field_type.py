# Generated by Django 4.2.1 on 2023-07-26 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0028_alter_planmappedfield_input_field_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planmappedfield",
            name="input_field_type",
            field=models.CharField(
                choices=[
                    ("INT", "Integer"),
                    ("FLOAT", "Decimal Number"),
                    ("STR", "String"),
                    ("STR_OR_INT", "String or integer"),
                    ("STR_nnd", "String of form nnd where nn is an integer value"),
                    (
                        "STR_duration_msp",
                        "String representing duration from MSP project in Excel",
                    ),
                    ("STR_DATE_DMY_01", "String of form dd MMM YYYY"),
                    ("STR_DATE_DMY_02", "String of form dd MMMMM YYYY HH:MM"),
                    ("DATE", "Date (without time)"),
                ],
                max_length=20,
            ),
        ),
    ]