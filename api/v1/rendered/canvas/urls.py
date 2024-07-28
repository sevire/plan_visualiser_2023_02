from django.urls import path, include

urlpatterns = [
    path('visuals/', include('api.v1.rendered.canvas.visual.urls')),
]
