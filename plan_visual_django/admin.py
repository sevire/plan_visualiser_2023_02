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


# ==============================================================================
# Health Dashboard View
# ==============================================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db import connection
import time
import os


@staff_member_required
def health_dashboard_view(request):
    """
    Display application health statistics.
    Only accessible to staff/admin users.
    """

    # 1. System Health
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_response_time = round((time.time() - start) * 1000, 2)  # in ms
        db_status = "OK"
    except Exception as e:
        db_response_time = None
        db_status = f"ERROR: {str(e)}"

    # Get disk space
    try:
        media_root = settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else os.path.join(settings.BASE_DIR, 'plan_files')
        stat = os.statvfs(media_root)
        total_space = stat.f_blocks * stat.f_frsize
        free_space = stat.f_bavail * stat.f_frsize
        used_space = total_space - free_space
        disk_usage_percent = round((used_space / total_space) * 100, 2)
    except Exception:
        total_space = free_space = used_space = disk_usage_percent = None

    # 2. User Statistics
    total_registered_users = User.objects.count()
    total_anonymous_sessions = Plan.objects.filter(
        user__isnull=True, session_id__isnull=False
    ).values('session_id').distinct().count()

    now = timezone.now()
    active_24h = User.objects.filter(last_login__gte=now - timedelta(hours=24)).count()
    active_7d = User.objects.filter(last_login__gte=now - timedelta(days=7)).count()
    active_30d = User.objects.filter(last_login__gte=now - timedelta(days=30)).count()

    # 3. Plan Statistics
    total_plans = Plan.objects.count()
    registered_plans = Plan.objects.filter(user__isnull=False).count()
    anonymous_plans = Plan.objects.filter(user__isnull=True, session_id__isnull=False).count()

    # Plans by file type
    plans_by_type = Plan.objects.values('file_type_name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Plans per registered user stats
    user_plan_stats = Plan.objects.filter(user__isnull=False).values('user').annotate(
        plan_count=Count('id')
    ).aggregate(
        avg=Avg('plan_count'),
        min=Min('plan_count'),
        max=Max('plan_count')
    )

    # Plans per anonymous session - grouped by session_id
    anonymous_session_stats = Plan.objects.filter(
        user__isnull=True, session_id__isnull=False
    ).values('session_id').annotate(
        plan_count=Count('id')
    ).order_by('-plan_count')

    # Calculate aggregate stats for anonymous sessions
    anonymous_aggregate = anonymous_session_stats.aggregate(
        avg=Avg('plan_count'),
        min=Min('plan_count'),
        max=Max('plan_count')
    )

    # 4. Visual Statistics
    total_visuals = PlanVisual.objects.count()

    visuals_per_plan = PlanVisual.objects.values('plan').annotate(
        visual_count=Count('id')
    ).aggregate(
        avg=Avg('visual_count'),
        min=Min('visual_count'),
        max=Max('visual_count')
    )

    # Visuals per user
    visuals_per_user = PlanVisual.objects.filter(
        plan__user__isnull=False
    ).values('plan__user').annotate(
        visual_count=Count('id')
    ).aggregate(
        avg=Avg('visual_count'),
        min=Min('visual_count'),
        max=Max('visual_count')
    )

    # 5. Activity Statistics
    total_plan_activities = PlanActivity.objects.count()

    plan_activities_per_user = PlanActivity.objects.filter(
        plan__user__isnull=False
    ).values('plan__user').annotate(
        activity_count=Count('id')
    ).aggregate(
        avg=Avg('activity_count'),
        min=Min('activity_count'),
        max=Max('activity_count')
    )

    total_visual_activities = VisualActivity.objects.count()
    enabled_visual_activities = VisualActivity.objects.filter(enabled=True).count()
    disabled_visual_activities = total_visual_activities - enabled_visual_activities

    visual_activities_per_user = VisualActivity.objects.filter(
        visual__plan__user__isnull=False
    ).values('visual__plan__user').annotate(
        activity_count=Count('id')
    ).aggregate(
        avg=Avg('activity_count'),
        min=Min('activity_count'),
        max=Max('activity_count')
    )

    # 6. Storage Statistics
    try:
        plan_files_dir = os.path.join(
            settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else settings.BASE_DIR,
            'plan_files'
        )
        if os.path.exists(plan_files_dir):
            total_files = 0
            total_size = 0
            file_sizes = []

            for root, dirs, files in os.walk(plan_files_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        total_size += size
                        file_sizes.append(size)
                        total_files += 1
                    except Exception:
                        pass

            total_size_mb = round(total_size / (1024 * 1024), 2)
            avg_file_size_kb = round((total_size / total_files) / 1024, 2) if total_files > 0 else 0
            largest_file_mb = round(max(file_sizes) / (1024 * 1024), 2) if file_sizes else 0
        else:
            total_files = total_size_mb = avg_file_size_kb = largest_file_mb = 0
    except Exception:
        total_files = total_size_mb = avg_file_size_kb = largest_file_mb = None

    # 7. Recent Activity (last 20 plans)
    recent_plans = Plan.objects.select_related('user').order_by('-id')[:20]

    # Build context
    context = {
        # System Health
        'db_status': db_status,
        'db_response_time': db_response_time,
        'total_space_gb': round(total_space / (1024**3), 2) if total_space else None,
        'free_space_gb': round(free_space / (1024**3), 2) if free_space else None,
        'disk_usage_percent': disk_usage_percent,

        # User Stats
        'total_registered_users': total_registered_users,
        'total_anonymous_sessions': total_anonymous_sessions,
        'active_24h': active_24h,
        'active_7d': active_7d,
        'active_30d': active_30d,

        # Plan Stats
        'total_plans': total_plans,
        'registered_plans': registered_plans,
        'anonymous_plans': anonymous_plans,
        'plans_by_type': plans_by_type,
        'user_plan_avg': round(user_plan_stats['avg'], 2) if user_plan_stats['avg'] else 0,
        'user_plan_min': user_plan_stats['min'] or 0,
        'user_plan_max': user_plan_stats['max'] or 0,
        'anonymous_plan_avg': round(anonymous_aggregate['avg'], 2) if anonymous_aggregate['avg'] else 0,
        'anonymous_plan_min': anonymous_aggregate['min'] or 0,
        'anonymous_plan_max': anonymous_aggregate['max'] or 0,
        'anonymous_session_stats': anonymous_session_stats[:10],  # Top 10

        # Visual Stats
        'total_visuals': total_visuals,
        'visuals_per_plan_avg': round(visuals_per_plan['avg'], 2) if visuals_per_plan['avg'] else 0,
        'visuals_per_plan_min': visuals_per_plan['min'] or 0,
        'visuals_per_plan_max': visuals_per_plan['max'] or 0,
        'visuals_per_user_avg': round(visuals_per_user['avg'], 2) if visuals_per_user['avg'] else 0,
        'visuals_per_user_min': visuals_per_user['min'] or 0,
        'visuals_per_user_max': visuals_per_user['max'] or 0,

        # Activity Stats
        'total_plan_activities': total_plan_activities,
        'plan_activities_per_user_avg': round(plan_activities_per_user['avg'], 2) if plan_activities_per_user['avg'] else 0,
        'plan_activities_per_user_min': plan_activities_per_user['min'] or 0,
        'plan_activities_per_user_max': plan_activities_per_user['max'] or 0,
        'total_visual_activities': total_visual_activities,
        'enabled_visual_activities': enabled_visual_activities,
        'disabled_visual_activities': disabled_visual_activities,
        'visual_activities_per_user_avg': round(visual_activities_per_user['avg'], 2) if visual_activities_per_user['avg'] else 0,
        'visual_activities_per_user_min': visual_activities_per_user['min'] or 0,
        'visual_activities_per_user_max': visual_activities_per_user['max'] or 0,

        # Storage Stats
        'total_files': total_files,
        'total_size_mb': total_size_mb,
        'avg_file_size_kb': avg_file_size_kb,
        'largest_file_mb': largest_file_mb,

        # Recent Activity
        'recent_plans': recent_plans,
    }

    return render(request, 'admin/health_dashboard.html', context)