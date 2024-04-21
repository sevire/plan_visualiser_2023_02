from django.urls import path, include
from api.v1.model.plan.views import PlanActivityListAPI

urlpatterns = [
    path('activities/', include('api.v1.model.plan.activity.urls')),

    # Returns information about the plan - not the actual activities from the plan (e.g. Plan Name).
    # path('<int:plan_id>/', PlanDetailsModelAPI.as_view()),
]
