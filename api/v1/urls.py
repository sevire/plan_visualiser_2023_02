from django.urls import path, include

urlpatterns = [
    path('model/', include('api.v1.model.urls')),
    path('canvas/', include('api.v1.canvas.urls')),
]
