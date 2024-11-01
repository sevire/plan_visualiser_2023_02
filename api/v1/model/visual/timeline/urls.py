from django.urls import path
from api.v1.model.visual.timeline.views import ModelVisualTimelineAPI, TimelineListViewDispatcher

urlpatterns = [
    path('<int:visual_id>/', TimelineListViewDispatcher.as_view()),
    path('<int:visual_id>/<int:timeline_seq_num>/', ModelVisualTimelineAPI.as_view()),
]
