from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, CharField, Form, IntegerField
from plan_visual_django.models import Plan, PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual, \
    PlotableStyle, Color
from plan_visual_django.services.visual.visual_settings import VisualSettings


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

    def __init__(self, *args, **kwargs):
        plan = kwargs.pop("plan", None)

        if plan is not None: # None means we have been called from POST processing so data already populated
            super(VisualFormForAdd, self).__init__(*args, **kwargs)

            field_defaults = VisualSettings.calculate_defaults_for_visual(plan)

            for field_name, field_default in field_defaults.items():
                self.fields[field_name].initial = field_default
        else:
            super(VisualFormForAdd, self).__init__(*args, **kwargs)



class VisualFormForEdit(ModelForm):
    class Meta:
        model = PlanVisual
        fields = (
            "name",
            "width",
            "max_height",
            "include_title",
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

        new_fields = {}

        new_fields['unique_id_from_plan'] = CharField(max_length=50)
        new_fields['activity'] = CharField(max_length=200)

        new_fields.update(self.fields)
        self.fields = new_fields
        self.fields['swimlane'].queryset = SwimlaneForVisual.objects.filter(plan_visual=visual)
        self.initial['activity'] = activity_name
        self.fields['unique_id_from_plan'].label = "Id"
        self.fields['vertical_positioning_value'].label = "Track #"
        self.initial['unique_id_from_plan'] = unique_id

        # Set the order of fields in the form with activity first

    field_order = ["unique_id_from_plan", "activity", "swimlane", "vertical_positioning_value"]


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
        super().__init__(*args, **kwargs)

        # Adding 'form-select' class to the widgets
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})

        if users is not None and len(users) > 0:
            queryset = Color.objects.filter(user__in=users)
            self.fields['fill_color'].queryset = queryset
            self.fields['line_color'].queryset = queryset
            self.fields['font_color'].queryset = queryset
