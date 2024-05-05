from django.urls import path, include

from api.v1.model.visual.activity.views import ModelVisualActivityListAPI, ModelVisualActivityAPI
from api.v1.model.visual.views import ModelVisualListAPI

urlpatterns = [
    path('<int:visual_id>/', ModelVisualActivityListAPI.as_view()),
    path('enabled/<int:visual_id>/', ModelVisualActivityListAPI.as_view(), {'enabled': True}),
    path('<int:visual_id>/<str:unique_id>/', ModelVisualActivityAPI.as_view()),
]
