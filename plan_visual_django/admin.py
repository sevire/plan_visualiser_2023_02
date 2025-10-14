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
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "plan_count", "last_login", "is_currently_active")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active", "last_login")

    def plan_count(self, obj):
        """Display the number of plans associated with this user."""
        return obj.plan_set.count()
    plan_count.short_description = "Plans"

    def is_currently_active(self, obj):
        """Check if user is currently active (logged in recently)."""
        from django.utils import timezone
        from datetime import timedelta
        if obj.last_login:
            time_threshold = timezone.now() - timedelta(minutes=30)
            return obj.last_login >= time_threshold
        return False
    is_currently_active.boolean = True
    is_currently_active.short_description = "Active Now"


class AnonymousUserProxy(Plan):
    """Proxy model to display anonymous users (session-based plans) in admin."""
    class Meta:
        proxy = True
        verbose_name = "Anonymous User"
        verbose_name_plural = "Anonymous Users"


@admin.register(AnonymousUserProxy)
class AnonymousUserAdmin(admin.ModelAdmin):
    """Admin view for anonymous users identified by session_id."""
    list_display = ["session_id", "plan_count_for_session", "last_activity", "plan_names"]
    search_fields = ["session_id"]

    def get_queryset(self, request):
        """Only show plans with session_id (anonymous users)."""
        qs = super().get_queryset(request)
        return qs.filter(user__isnull=True, session_id__isnull=False).order_by('session_id')

    def plan_count_for_session(self, obj):
        """Count plans for this session."""
        return Plan.objects.filter(session_id=obj.session_id).count()
    plan_count_for_session.short_description = "Plans"

    def last_activity(self, obj):
        """Get the most recent plan modification for this session."""
        # Since Plan doesn't have a timestamp field, we show the plan name as proxy
        return "See Plans"
    last_activity.short_description = "Last Activity"

    def plan_names(self, obj):
        """Show all plan names for this session."""
        plans = Plan.objects.filter(session_id=obj.session_id)
        names = [p.plan_name for p in plans[:3]]
        result = ", ".join(names)
        if plans.count() > 3:
            result += f" (+{plans.count() - 3} more)"
        return result
    plan_names.short_description = "Plans"

    def has_add_permission(self, request):
        """Disable add functionality for this view."""
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["user", "session_id", "plan_name", "file_name", "file_type_name"]
    list_filter = ["user", "file_type_name"]
    search_fields = ["plan_name", "session_id", "user__username"]


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
    list_display = ['user', 'style_name', 'style_preview']

    def style_preview(self, obj):
        """
        Render a rectangle preview styled from the PlotableStyle:
        - background = fill_color
        - border color/thickness = line_color / line_thickness
        - text color = font_color
        - font family and size from style
        """
        try:
            bg = f"rgb({obj.fill_color.red}, {obj.fill_color.green}, {obj.fill_color.blue})"
            border = f"{obj.line_thickness}px solid rgb({obj.line_color.red}, {obj.line_color.green}, {obj.line_color.blue})"
            fg = f"rgb({obj.font_color.red}, {obj.font_color.green}, {obj.font_color.blue})"
            text = "Sample text"
            # Rectangle dimensions can be tuned to taste
            return format_html(
                '<div style="display:inline-block; width: 220px; height: 22px; line-height: 22px; '
                'background: {}; border: {}; color: {}; text-align: center; '
                'font-family: {}; font-size: {}px; border-radius: 4px; overflow: hidden;">'
                '{}</div>',
                bg,
                border,
                fg,
                obj.font.font_name,
                obj.font_size,
                text,
            )
        except Exception:
            # Fall back to a simple dash if any attribute is missing
            return "-"

    style_preview.short_description = "Preview"


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
    list_display = ('slug', 'parent', 'order', 'title')  # columns to display on admin page
    search_fields = ['slug', 'title', 'content']
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('title',)}  # Auto-fill slug based on title


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'updated_at')
    search_fields = ('slug', 'title', 'content')
    prepopulated_fields = {'slug': ('title',)}  # Auto-fill slug based on title