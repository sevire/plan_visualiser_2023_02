from django.urls import path, include

from api.v1.visual_activity.views import VisualActivityAPI
from plan_visual_django.models import VisualActivity

urlpatterns = [
    path('', VisualActivityAPI.as_view()),
]
