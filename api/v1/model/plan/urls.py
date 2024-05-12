from django.urls import path, include
from api.v1.model.plan.views import ModelPlanListAPI, ModelPlanAPI

urlpatterns = [
    path('activities/', include('api.v1.model.plan.activity.urls')),
    path('', ModelPlanListAPI.as_view()),
    path('<int:id>/', ModelPlanAPI.as_view()),
]
