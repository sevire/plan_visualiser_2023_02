from django.urls import path, include

from api.v1.rendered.canvas.visual.timeline.views import RenderedCanvasVisualTimelineListAPI, \
    RenderedCanvasVisualTimelineAPI

urlpatterns = [
    path('<int:visual_id>/', RenderedCanvasVisualTimelineListAPI.as_view()),
    path('<int:visual_id>/<int:sequence_num>/', RenderedCanvasVisualTimelineAPI.as_view()),
]
