from django.urls import path, include
from api.v1.rendered.canvas.visual.views import RenderCanvasVisualAPI

urlpatterns = [
    path('activities/', include('api.v1.rendered.canvas.visual.activity.urls')),
    path('settings/', include('api.v1.rendered.canvas.visual.settings.urls')),
    path('timelines/', include('api.v1.rendered.canvas.visual.timeline.urls')),
    path('swimlanes/', include('api.v1.rendered.canvas.visual.swimlane.urls')),
    path('<int:visual_id>/', RenderCanvasVisualAPI.as_view()),
]
