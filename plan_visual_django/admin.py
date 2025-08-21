from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from plan_visual_django.models import (
    Plan,
    Color,
    Font,
    PlotableStyle,
    PlanVisual,
    SwimlaneForVisual,
    VisualActivity,
    PlanActivity,
    TimelineForVisual,
    StaticContent, HelpText
)


User = get_user_model()

admin.site.register(Permission)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom user model."""
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["user", "plan_name", "file_name", "file_type_name"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "red", "green", "blue", "alpha", "show_color"]
    list_filter = ['user']

    def show_color(self, obj):
        return format_html(
            '<div style="width: 36px; height: 18px; background-color: rgb({}, {}, {});"></div>',
            obj.red, obj.green, obj.blue)

    show_color.short_description = 'Color Preview'


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(PlotableStyle)
class PlotableStyleAdmin(admin.ModelAdmin):
    list_display = ['user', 'style_name', 'fill_color_preview', 'line_color_preview', 'font_color_preview']

    def color_preview(self, color):
        """
        Helper method to render a color preview box for a given Color instance.
        """
        return format_html(
            '<div style="width: 36px; height: 18px; background-color: rgb({}, {}, {});"></div>',
            color.red, color.green, color.blue
        )

    def fill_color_preview(self, obj):
        return self.color_preview(obj.fill_color)
    fill_color_preview.short_description = 'Fill Color'

    def line_color_preview(self, obj):
        return self.color_preview(obj.line_color)
    line_color_preview.short_description = 'Line Color'

    def font_color_preview(self, obj):
        return self.color_preview(obj.font_color)
    font_color_preview.short_description = 'Font Color'


@admin.register(PlanVisual)
class PlanVisualAdmin(admin.ModelAdmin):
    list_display =  ('id', 'name', 'plan')
    ordering = ('plan',)


@admin.register(SwimlaneForVisual)
class SwimlaneForVisualAdmin(admin.ModelAdmin):
    list_display = ("id", "plan_visual", "sequence_number", "swim_lane_name")
    ordering = ("plan_visual", "sequence_number")
    list_filter = ('plan_visual', )


@admin.register(VisualActivity)
class VisualActivityAdmin(admin.ModelAdmin):
    list_display = ('visual', 'unique_id_from_plan', 'enabled')
    ordering = ('enabled',)
    list_filter = ('visual',)


@admin.register(PlanActivity)
class PlanActivityAdmin(admin.ModelAdmin):
    list_display = ('plan', 'sequence_number', 'unique_sticky_activity_id', 'activity_name', 'start_date', 'end_date')
    list_filter = ('plan',)


@admin.register(TimelineForVisual)
class TimelineForVisualAdmin(admin.ModelAdmin):
    list_filter = ('plan_visual',)


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')  # columns to display on admin page
    search_fields = ['slug', 'title', 'content']
    prepopulated_fields = {'slug': ('title',)}  # Auto-fill slug based on title


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'updated_at')
    search_fields = ('slug', 'title', 'content')
    prepopulated_fields = {'slug': ('title',)}  # Auto-fill slug based on title