from django.forms import ModelForm, CharField
from plan_visual_django.models import Plan, PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual


class PlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = ("plan_name", "file", "file_type")


class ReUploadPlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = ("file",)


class VisualFormForAdd(ModelForm):
    class Meta:
        model = PlanVisual
        fields = (
            "name",
            "width",
            "max_height",
            "include_title",
            "max_height",
            "default_activity_shape",
            "default_milestone_shape",
            "track_height",
            "track_gap",
            "milestone_width",
            "swimlane_gap",
            "default_activity_plotable_style",
            "default_milestone_plotable_style",
            "default_swimlane_plotable_style",
        )


class VisualFormForEdit(ModelForm):
    class Meta:
        model = PlanVisual
        fields = (
            "name",
            "width",
            "max_height",
            "include_title",
            "max_height",
            "default_activity_shape",
            "default_milestone_shape",
            "track_height",
            "track_gap",
            "milestone_width",
            "swimlane_gap",
            "default_activity_plotable_style",
            "default_milestone_plotable_style",
            "default_swimlane_plotable_style",
        )


class VisualActivityFormForEdit(ModelForm):
    def __init__(self, *args, **kwargs):
        unique_id = kwargs['instance'].unique_id_from_plan
        visual = kwargs['instance'].visual
        activity_from_plan = visual.plan.planactivity_set.filter(unique_sticky_activity_id=unique_id)
        activity_name = activity_from_plan[0].activity_name

        super().__init__(*args, **kwargs)

        self.fields['activity'] = CharField(max_length=200)
        self.fields['unique_id_from_plan'] = CharField(max_length=50)
        self.fields['swimlane'].queryset = SwimlaneForVisual.objects.filter(plan_visual=visual)
        self.initial['activity'] = activity_name
        self.initial['unique_id_from_plan'] = unique_id
        field_order = ["unique_id_from_plan", "activity", "swimlane", "vertical_positioning_type", "vertical_positioning_value"]

    class Meta:
        model = VisualActivity
        fields = "__all__"


class VisualSwimlaneFormForEdit(ModelForm):
    class Meta:
        model = SwimlaneForVisual
        fields = "__all__"


class VisualTimelineFormForEdit(ModelForm):
    class Meta:
        model = TimelineForVisual
        fields = "__all__"
