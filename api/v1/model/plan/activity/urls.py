from django.urls import path

from api.v1.model.plan.activity.views import ModelPlanActivityListAPI, ModelPlanActivityAPI

urlpatterns = [
    path('<int:plan_id>/', ModelPlanActivityListAPI.as_view()),
    path('<int:plan_id>/<str:unique_id>/', ModelPlanActivityAPI.as_view()),
]
