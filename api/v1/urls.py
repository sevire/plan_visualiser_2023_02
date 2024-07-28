from django.urls import path, include

urlpatterns = [
    path('model/', include('api.v1.model.urls')),
    path('rendered/', include('api.v1.rendered.urls')),
]
