from django.urls import path, include
from api.v1.model.visual.swimlane.views import ModelVisualSwimlaneListAPI, ModelVisualSwimlaneAPI

urlpatterns = [
    path('<int:visual_id>/', ModelVisualSwimlaneListAPI.as_view()),
    path('<int:visual_id>/<int:swimlane_seq_num>/', ModelVisualSwimlaneAPI.as_view()),
]
