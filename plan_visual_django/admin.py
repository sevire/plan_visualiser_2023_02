from django.contrib import admin
from plan_visual_django.models import Plan, Color, Font, PlotableStyle, PlotableShapeType, \
    PlotableShape, FileType, PlotableShapeAttributesRectangle, PlotableShapeAttributesDiamond, \
    PlanVisual, SwimlaneForVisual, VisualActivity, PlanMappedField, PlanField, PlanFieldMappingType


@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ["file_type_name", "file_type_description"]

@admin.register(PlanField)
class PlanFieldAdmin(admin.ModelAdmin):
    list_display = ["field_name", "field_type"]
    ordering = ["sort_index"]


@admin.register(PlanMappedField)
class PlanMappedFieldAdmin(admin.ModelAdmin):
    list_display = ["plan_field_mapping_type", "mapped_field", "input_field_name", "input_field_type"]


@admin.register(PlanFieldMappingType)
class PlanFieldMappingTypeAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["user", "file", "file_type"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(PlotableStyle)
class PlotableStyleAdmin(admin.ModelAdmin):
    exclude = []


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
    exclude = []


@admin.register(VisualActivity)
class VisualActivityAdmin(admin.ModelAdmin):
    exclude = []
