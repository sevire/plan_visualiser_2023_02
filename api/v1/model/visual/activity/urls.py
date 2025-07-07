from django.urls import path, include
from api.v1.model.visual.activity.views import ModelVisualActivityListAPI, ModelVisualActivityAPI, \
    VisualActivityViewDispatcher, ModelVisualActivityChangeSwimlaneAPI


urlpatterns = [
    path('<int:visual_id>/', VisualActivityViewDispatcher.as_view()),
    path('enabled/<int:visual_id>/', VisualActivityViewDispatcher.as_view(), {'enabled': True}),
    path('<int:visual_id>/<str:unique_id>/', ModelVisualActivityAPI.as_view()),
    path('<int:visual_id>/<str:activity_unique_id>/<int:new_swimlane_id>/', ModelVisualActivityChangeSwimlaneAPI.as_view()),

]
