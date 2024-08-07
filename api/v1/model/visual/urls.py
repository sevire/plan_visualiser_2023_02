from django.urls import path, include

from api.v1.model.visual.views import ModelVisualListAPI, ModelVisualAPI

urlpatterns = [
    path('swimlanes/', include('api.v1.model.visual.swimlane.urls')),
    path('timelines/', include('api.v1.model.visual.timeline.urls')),
    path('activities/', include('api.v1.model.visual.activity.urls')),
    path('styles/', include('api.v1.model.visual.plotable_style.urls')),
    path('shapes/', include('api.v1.model.visual.plotable_shape.urls')),


    path('by-plan/<int:plan_id>/', ModelVisualListAPI.as_view()),
    path('<int:visual_id>/', ModelVisualAPI.as_view()),
]
