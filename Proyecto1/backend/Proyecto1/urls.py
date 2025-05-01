"""
URL configuration for Proyecto1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework import routers

from quality.views import (
    MQSViewSet, MESViewSet, PendienteViewSet,
    YieldTurnoViewSet, SamplingViewSet
)

router = routers.DefaultRouter()
router.register(r'mqs', MQSViewSet, basename='mqs')
router.register(r'mes', MESViewSet, basename='mes')
router.register(r'pendientes', PendienteViewSet, basename='pendientes')
router.register(r'yield', YieldTurnoViewSet, basename='yield')
router.register(r'sampling', SamplingViewSet, basename='sampling')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
