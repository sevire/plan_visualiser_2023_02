# Generated by Django 4.2.1 on 2023-06-24 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0021_plotablestyle_font_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="swimlaneforvisual",
            name="plotable_style",
            field=models.ForeignKey(
                default=4,
                on_delete=django.db.models.deletion.CASCADE,
                to="plan_visual_django.plotablestyle",
            ),
            preserve_default=False,
        ),
    ]
