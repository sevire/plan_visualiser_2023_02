from django.urls import path, include

from api.v1.visual_activity.views import VisualActivityAPI

urlpatterns = [
    path('add/<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
    path('remove/<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
]
