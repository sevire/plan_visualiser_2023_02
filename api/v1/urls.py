from django.urls import path, include

urlpatterns = [
    path('visual-activities/', include('api.v1.visual_activity.urls')),
    path('plan-activities/', include('api.v1.plan_activity.urls')),
    path('visual/', include('api.v1.plan_visual.urls')),
]
