from django.urls import path, include
from api.v1.model.visual.swimlane.views import ModelVisualSwimlaneListAPI, ModelVisualSwimlaneAPI, \
    SwimlaneListViewDispatcher, ModelVisualSwimlaneCompress

urlpatterns = [
    path('<int:visual_id>/', SwimlaneListViewDispatcher.as_view()),
    path('<int:visual_id>/<int:swimlane_seq_num>/', ModelVisualSwimlaneAPI.as_view()),
    path('compress/<int:visual_id>/<int:swimlane_seq_num>/', ModelVisualSwimlaneCompress.as_view()),
]
