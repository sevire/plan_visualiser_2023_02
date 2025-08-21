from django.urls import path, include
from api.v1.model.visual.activity.views import ModelVisualActivityAPI, \
    VisualActivityViewDispatcher, ModelVisualActivitySwimlaneDispatcher, \
    ModelVisualActivitySwimlaneSubActivities

urlpatterns = [
    path('<int:visual_id>/', VisualActivityViewDispatcher.as_view()),
    path('enabled/<int:visual_id>/', VisualActivityViewDispatcher.as_view(), {'enabled': True}),
    path('<int:visual_id>/<str:activity_unique_id>/', ModelVisualActivityAPI.as_view()),
    path('<int:visual_id>/<str:activity_unique_id>/<int:swimlane>/', ModelVisualActivitySwimlaneDispatcher.as_view()),
    path('add-sub-activities/<int:visual_id>/<str:activity_unique_id>/<int:swimlane>/', ModelVisualActivitySwimlaneSubActivities.as_view()),

]
