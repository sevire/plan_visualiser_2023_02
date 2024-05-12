from django.urls import path
from api.v1.rendered.canvas.visual.views import RenderCanvasVisualAPI
from api.v1.visual.views import VisualActivityAPI, VisualActivityListAPI

urlpatterns = [
    path('<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
    path('<int:visual_id>/', VisualActivityListAPI.as_view()),
    path('update/<int:visual_id>/<str:unique_id>/', VisualActivityAPI.as_view()),
    path('rendered/<int:visual_id>/', RenderCanvasVisualAPI.as_view())
]
