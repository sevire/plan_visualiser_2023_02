from django.urls import path, include

urlpatterns = [
    path('visual_activity/', include('api.v1.visual_activity.urls')),
]
