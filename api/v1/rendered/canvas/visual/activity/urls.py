from django.urls import path

from api.v1.rendered.canvas.visual.activity.views import RenderedCanvasVisualActivityListAPI, \
    RenderedCanvasVisualActivityAPI

urlpatterns = [
    path('<int:visual_id>/', RenderedCanvasVisualActivityListAPI.as_view()),
    path('<int:visual_id>/<str:unique_id>/', RenderedCanvasVisualActivityAPI.as_view()),
]
