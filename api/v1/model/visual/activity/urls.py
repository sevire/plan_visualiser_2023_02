from django.urls import path, include
from api.v1.model.visual.activity.views import ModelVisualActivityListAPI, ModelVisualActivityAPI, \
    VisualActivityViewDispatcher

urlpatterns = [
    path('<int:visual_id>/', VisualActivityViewDispatcher.as_view()),
    path('enabled/<int:visual_id>/', VisualActivityViewDispatcher.as_view(), {'enabled': True}),
    path('<int:visual_id>/<str:unique_id>/', ModelVisualActivityAPI.as_view()),
]
