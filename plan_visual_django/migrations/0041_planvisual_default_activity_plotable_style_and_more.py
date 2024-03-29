# Generated by Django 4.2.1 on 2023-08-12 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("plan_visual_django", "0040_alter_planactivity_milestone_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="planvisual",
            name="default_activity_plotable_style",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_activity_plotable_style",
                to="plan_visual_django.plotablestyle",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="planvisual",
            name="default_activity_shape",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_activity_shape",
                to="plan_visual_django.plotableshape",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="planvisual",
            name="default_milestone_plotable_style",
            field=models.ForeignKey(
                default=3,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_milestone_plotable_style",
                to="plan_visual_django.plotablestyle",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="planvisual",
            name="default_milestone_shape",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_milestone_shape",
                to="plan_visual_django.plotableshape",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="planvisual",
            name="default_swimlane_plotable_style",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="default_swimlane_plotable_style",
                to="plan_visual_django.plotablestyle",
            ),
            preserve_default=False,
        ),
    ]
