from django.urls import path
from django.views.generic import RedirectView

from plan_visual_django import views

urlpatterns = [
    path("", RedirectView.as_view(url='manage-plans', permanent=False), name='index'),
    path("add-plan", views.add_plan),
    path("add-visual/<int:plan_id>", views.add_visual),
    path("edit-visual/<int:visual_id>", views.edit_visual),
    path("manage-plans", views.manage_plans, name="manage_plans"),
    path("delete-plan/<int:pk>/", views.delete_plan, name='delete_plan'),
    path("delete-visual/<int:pk>/", views.delete_visual, name='delete_visual'),
    path("manage-visuals/<int:plan_id>/", views.manage_visuals, name='manage_visuals'),
    path("configure-visual-activities/<int:visual_id>/", views.configure_visual_activities, name='configure-visual'),
    path("layout-visual/<int:visual_id>/", views.layout_visual, name='layout-visual'),
    path("visual/<int:pk>/", views.PlotVisualView.as_view(), name='plot-visual'),
]
