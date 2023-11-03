from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, CharField, Form, IntegerField
from plan_visual_django.models import Plan, PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual, \
    PlotableStyle, Color


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


class SwimlaneDropdownForm(ModelForm):
    """
    This form is used to create a dropdown list of swimlanes within a visual for the user to select. Will be used when
    selecting the swimlane for an action to apply to.

    We are using ModelForm here because we want to use the queryset functionality to filter the list of swimlanes to
    only those which are in the visual.
    """
    def __init__(self, *args, **kwargs):
        visual = kwargs['instance']
        super().__init__(*args, **kwargs)
        self.fields['swimlane'].queryset = SwimlaneForVisual.objects.filter(plan_visual=visual)

    class Meta:
        model = VisualActivity
        fields = ("swimlane",)


class VisualSwimlaneFormForEdit(ModelForm):
    class Meta:
        model = PlanVisual
        fields = "__all__"


class VisualTimelineFormForEdit(ModelForm):
    class Meta:
        model = TimelineForVisual
        fields = "__all__"


class ColorForm(Form):
    id=IntegerField(widget=forms.HiddenInput(),required=False)
    name = CharField(max_length=50)
    hex_color = forms.CharField(label='hex_color', max_length=7, initial="#000000",
                                widget=forms.TextInput(attrs={'type': 'color'}))


class PlotableStyleForm(ModelForm):
    class Meta:
        model = PlotableStyle
        fields = "__all__"

    def __init__(self, *args, users:[User], **kwargs):
        """
        users will either be None, or empty or contain one or more Users whose colours should be included in the
        colour dropdown.  This is to allow standard colors to be included for any user by adding a common user
        where the standard colours are mapped to.

        :param args:
        :param user:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if users is not None and len(users) > 0:
            queryset = Color.objects.filter(user__in=users)
            self.fields['fill_color'].queryset = queryset
            self.fields['line_color'].queryset = queryset
            self.fields['font_color'].queryset = queryset
