from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm, CharField, Form, IntegerField
from django.http import HttpRequest

from plan_visual_django.models import Plan, PlanVisual, VisualActivity, SwimlaneForVisual, TimelineForVisual, \
    PlotableStyle, Color
from plan_visual_django.services.auth.user_services import generate_username, CurrentUser
from plan_visual_django.services.visual.model.visual_settings import VisualSettings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        """Validate form data and ensure either username or email is provided."""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Ensure at least one identifier is provided
        if not username and not email:
            raise forms.ValidationError("You must provide either a username or an email.")

        # Allow username-only registrations by explicitly handling missing email
        if not email:
            cleaned_data['email'] = None  # Explicitly set email to None if missing

        # Generate a username if none is provided
        if not username:
            cleaned_data['username'] = generate_username(email)

        return cleaned_data

    def save(self, commit=True):
        """Save the user instance after cleaning."""
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")


class PlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = ("plan_name", "file", "file_type_name")

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        # The request object is only passed in to calculate default plan name which is for
        # GET request only.  If request is not passed in don't attempt to create default plan name
        if request is not None:
            current_user = CurrentUser(request)
            default_plan_name = current_user.generate_default_plan_name()
            self.fields['plan_name'].initial = default_plan_name


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
            "default_timeline_plotable_style_odd",
            "default_timeline_plotable_style_even"
        )

    def __init__(self, *args, **kwargs):
        plan = kwargs.pop("plan", None)
        user = kwargs.pop("user", None)
        super(VisualFormForAdd, self).__init__(*args, **kwargs)

        if plan is not None: # None means we have been called from POST processing so data already populated
            field_defaults = VisualSettings.calculate_defaults_for_visual(plan)

            for field_name, field_default in field_defaults.items():
                self.fields[field_name].initial = field_default

            # Set dropdown for style so it only includes styles for this user and shared ones.
            filtered_styles = PlotableStyle.objects.for_user(user)

            self.fields["default_activity_plotable_style"].queryset = filtered_styles
            self.fields["default_milestone_plotable_style"].queryset = filtered_styles
            self.fields["default_swimlane_plotable_style"].queryset = filtered_styles
            self.fields["default_timeline_plotable_style_odd"].queryset = filtered_styles
            self.fields["default_timeline_plotable_style_even"].queryset = filtered_styles


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
            "default_timeline_height",
            "track_gap",
            "milestone_width",
            "swimlane_gap",
            "default_activity_plotable_style",
            "default_milestone_plotable_style",
            "default_swimlane_plotable_style",
            "default_timeline_plotable_style_odd",
            "default_timeline_plotable_style_even"
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Get correct queryset for styles relatig to this user plus shared styles
        filtered_styles = PlotableStyle.objects.for_user(user)

        self.fields["default_activity_plotable_style"].queryset = filtered_styles
        self.fields["default_milestone_plotable_style"].queryset = filtered_styles
        self.fields["default_swimlane_plotable_style"].queryset = filtered_styles
        self.fields["default_timeline_plotable_style_odd"].queryset = filtered_styles
        self.fields["default_timeline_plotable_style_even"].queryset = filtered_styles


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
