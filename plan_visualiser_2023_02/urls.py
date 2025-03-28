"""plan_visualiser_2022_10 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import plan_visual_django
from plan_visual_django import views
from plan_visual_django.views import CustomLoginView

urlpatterns = [
    path("", RedirectView.as_view(url='pv/textpages/landing-page/', permanent=True), name='index'),
    path("admin/", admin.site.urls),
    path("pv/", include('plan_visual_django.urls')),
    path('api/', include('api.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
]