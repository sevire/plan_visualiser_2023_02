from django.urls import path
from api.v1.canvas.visual.views import PlanVisualRenderAPI

urlpatterns = [
    path('canvas/<int:visual_id>/', PlanVisualRenderAPI.as_view()),
]
