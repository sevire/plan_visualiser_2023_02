from django.urls import path
from api.v1.model.plan.activity.views import ModelPlanActivityListAPI, ModelPlanActivityAPI, \
    ModelPlanActivityByVisualListAPI

urlpatterns = [
    path('<int:id>/', ModelPlanActivityListAPI.as_view()),
    path('<int:plan_id>/<str:unique_id>/', ModelPlanActivityAPI.as_view()),
    path('visuals/<int:visual_id>/', ModelPlanActivityByVisualListAPI.as_view()),
]
