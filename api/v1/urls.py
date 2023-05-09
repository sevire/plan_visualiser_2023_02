from django.urls import path, include

urlpatterns = [
    path('visual_activities/', include('api.v1.visual_activity.urls')),
]
