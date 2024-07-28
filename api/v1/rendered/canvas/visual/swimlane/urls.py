from django.urls import path, include

from api.v1.rendered.canvas.visual.swimlane.views import RenderedCanvasVisualSwimlaneListAPI, \
    RenderedCanvasVisualSwimlaneAPI

urlpatterns = [
    path('<int:visual_id>/', RenderedCanvasVisualSwimlaneListAPI.as_view()),
    path('<int:visual_id>/<int:sequence_num>/', RenderedCanvasVisualSwimlaneAPI.as_view()),
]
