from django.urls import path, include
from api.v1.plan_visual.views import PlanVisualRenderAPI

urlpatterns = [
    path('canvas/<int:visual_id>/', PlanVisualRenderAPI.as_view()),
]
