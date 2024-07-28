from django.urls import path, include
from api.v1.model.visual.timeline.views import ModelVisualTimelineListAPI, ModelVisualTimelineAPI, \
    TimelineListViewDispatcher

urlpatterns = [
    path('<int:visual_id>/', TimelineListViewDispatcher.as_view()),
    path('<int:visual_id>/<int:timeline_seq_num>/', ModelVisualTimelineAPI.as_view()),
]
