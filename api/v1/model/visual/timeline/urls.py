from django.urls import path, include
from api.v1.model.visual.timeline.views import ModelVisualTimelineListAPI, ModelVisualTimelineAPI

urlpatterns = [
    path('<int:visual_id>/', ModelVisualTimelineListAPI.as_view()),
    path('<int:visual_id>/<int:timeline_seq_num>/', ModelVisualTimelineAPI.as_view()),
]
