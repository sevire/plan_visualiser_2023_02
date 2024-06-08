from django.urls import path
from api.v1.model.visual.plotable_shape.views import ModelVisualShapeAPI

urlpatterns = [
    path('', ModelVisualShapeAPI.as_view()),
]
