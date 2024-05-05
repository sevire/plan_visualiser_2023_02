from django.urls import path, include

urlpatterns = [
    path('plans/', include('api.v1.model.plan.urls')),
    path('visuals/', include('api.v1.model.visual.urls')),
]
