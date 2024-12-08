from django.urls import path
from django.views.generic import RedirectView

from plan_visual_django import views
from plan_visual_django.views import StaticPageView, FileTypeListView

urlpatterns = [
    # Management of Plans
    path("", RedirectView.as_view(url='manage-plans', permanent=False), name='index'),
    path("manage-plans", views.manage_plans, name="manage-plans"),
    path("add-plan", views.add_plan),
    path("re-upload-plan/<int:pk>", views.re_upload_plan),
    path("delete-plan/<int:pk>/", views.delete_plan, name='delete-plan'),
    path("view-file-types/", FileTypeListView.as_view(), name="view-file-types"),

    # Maintenance of Visuals
    path("manage-visuals/<int:plan_id>/", views.manage_visuals, name='manage_visuals'),
    path("add-visual/<int:plan_id>", views.add_visual),
    path("edit-visual/<int:visual_id>", views.edit_visual, name='edit-visual'),
    path("delete-visual/<int:pk>/", views.delete_visual, name='delete-visual'),
    path("visual/<int:visual_id>/", views.plot_visual, name='plot-visual'),

    # Visual features management
    path("manage-swimlanes-for-visual/<int:visual_id>/", views.manage_swimlanes_for_visual, name="manage-swimlanes"),
    path("manage-timelines-for-visual/<int:visual_id>/", views.manage_timelines_for_visual, name="manage-timelines"),
    path("create-milestone-swimlane/<int:visual_id>/", views.create_milestone_swimlane, name='create-milestone-swimlane'),
    path("swimlane_action/<int:visual_id>/", views.swimlane_actions, name='auto-add/del-levels'),

    # Visual Styling
    path("manage-colors/", views.manage_colors, name='manage-colors'),
    path("manage-plotable-styles/", views.manage_plotable_styles, name='manage-styles'),

    # Static pages
    path("textpages/<int:pk>", StaticPageView.as_view(), name='static-pages'),
]



