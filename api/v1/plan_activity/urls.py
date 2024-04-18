from django.urls import path, include
from api.v1.plan_activity.views import PlanActivityListAPI

urlpatterns = [
    path('<int:plan_id>/', PlanActivityListAPI.as_view()),
]
