from django.urls import path, include

from api.v1.visual_activity.views import VisualActivityAPI, VisualActivityListAPI, VisualRenderAPI

urlpatterns = [
    path('<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
    path('<int:visual_id>/', VisualActivityListAPI.as_view()),
    path('update/<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
    path('rendered/<int:visual_id>/', VisualRenderAPI.as_view())
]
