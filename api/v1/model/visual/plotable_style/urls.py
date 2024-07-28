from django.urls import path, include
from api.v1.model.visual.plotable_style.views import ModelVisualStyleAPI

urlpatterns = [
    path('', ModelVisualStyleAPI.as_view()),
]
