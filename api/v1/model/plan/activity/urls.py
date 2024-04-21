from django.urls import path
from api.v1.model.plan.views import PlanActivityListAPI

urlpatterns = [
    path('<int:plan_id>/', PlanActivityListAPI.as_view()),
]
