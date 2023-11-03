from django.urls import path
from django.views.generic import RedirectView

from plan_visual_django import views

urlpatterns = [
    path("", RedirectView.as_view(url='manage-plans', permanent=False), name='index'),
    path("add-plan", views.add_plan),
    path("re-upload-plan/<int:pk>", views.re_upload_plan),
    path("add-visual/<int:plan_id>", views.add_visual),
    path("manage-swimlanes-for-visual/<int:visual_id>/", views.manage_swimlanes_for_visual, name="manage-swimlanes"),
    path("manage-timelines-for-visual/<int:visual_id>/", views.manage_timelines_for_visual, name="manage-timelines"),
    path("edit-visual/<int:visual_id>", views.edit_visual),
    path("manage-plans", views.manage_plans, name="manage-plans"),
    path("delete-plan/<int:pk>/", views.delete_plan, name='delete_plan'),
    path("delete-visual/<int:pk>/", views.delete_visual, name='delete_visual'),
    path("manage-visuals/<int:plan_id>/", views.manage_visuals, name='manage_visuals'),
    path("configure-visual-activities/<int:visual_id>/", views.select_visual_activities, name='configure-visual'),
    path("layout-visual/<int:visual_id>/", views.layout_visual, name='layout-visual'),
    path("create-milestone-swimlane/<int:visual_id>/", views.create_milestone_swimlane, name='create-milestone-swimlane'),
    path("add-or-delete-level/<int:visual_id>/<int:level>/<str:action>", views.add_or_delete_level, name='auto-add/del-levels'),
    path("visual/<int:visual_id>/", views.plot_visual, name='plot-visual'),
    path("manage-colors/", views.manage_colors, name='manage-colors'),
    path("manage-plotable-styles/", views.manage_plotable_styles, name='manage-styles'),
]
