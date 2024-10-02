from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from plan_visual_django.models import (
    Plan,
    Color,
    Font,
    PlotableStyle,
    PlotableShapeType,
    PlotableShape,
    FileType,
    PlotableShapeAttributesRectangle,
    PlotableShapeAttributesDiamond,
    PlanVisual,
    SwimlaneForVisual,
    VisualActivity,
    PlanMappedField,
    PlanFieldMappingType,
    PlanActivity,
    TimelineForVisual,
    StaticContent
)


@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ["file_type_name", "plan_field_mapping_type_name", "file_type_description"]

    def plan_field_mapping_type_name(self, obj):
        return obj.plan_field_mapping_type.name


@admin.register(PlanMappedField)
class PlanMappedFieldAdmin(admin.ModelAdmin):
    list_display = ["plan_field_mapping_type", "mapped_field", "input_field_name", "input_field_type"]
    ordering = ['plan_field_mapping_type', 'mapped_field']
    list_filter = ('plan_field_mapping_type', )


@admin.register(PlanFieldMappingType)
class PlanFieldMappingTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["user", "plan_name", "file_name", "file_type"]


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
    list_display = ['user', 'style_name']

@admin.register(PlanVisual)
class PlanVisualAdmin(admin.ModelAdmin):
    list_display =  ('name', 'plan')
    ordering = ('plan',)


@admin.register(PlotableShapeType)
class PlotableShapeTypeAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(PlotableShape)
class PlotableShapeAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(PlotableShapeAttributesRectangle)
class PlotableShapeAttributesRectangleAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(PlotableShapeAttributesDiamond)
class PlotableShapeAttributesDiamondAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(SwimlaneForVisual)
class SwimlaneForVisualAdmin(admin.ModelAdmin):
    list_display = ("plan_visual", "sequence_number", "swim_lane_name")
    ordering = ("plan_visual", "sequence_number")
    list_filter = ('plan_visual', )


@admin.register(VisualActivity)
class VisualActivityAdmin(admin.ModelAdmin):
    list_display = ('visual', 'unique_id_from_plan', 'enabled')
    ordering = ('enabled',)
    list_filter = ('visual',)


@admin.register(PlanActivity)
class PlanActivityAdmin(admin.ModelAdmin):
    list_display = ('unique_sticky_activity_id', 'activity_name', 'start_date', 'end_date')
    list_filter = ('plan',)


@admin.register(TimelineForVisual)
class TimelineForVisualAdmin(admin.ModelAdmin):
    list_filter = ('plan_visual',)


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')  # columns to display on admin page
    search_fields = ['title', 'content']

