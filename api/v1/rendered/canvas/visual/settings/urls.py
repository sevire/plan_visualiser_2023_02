from django.urls import path

from api.v1.rendered.canvas.visual.settings.views import RenderedCanvasVisualettingsAPI

urlpatterns = [
    path('<int:visual_id>/', RenderedCanvasVisualettingsAPI.as_view()),
]
