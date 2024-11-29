from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NiveisDeRuidoViewSet
from django.contrib.auth import views as auth_views
from userInterface import views



router = DefaultRouter()
router.register(r'niveis_de_ruido', NiveisDeRuidoViewSet)

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relatorio/', views.relatorio, name='relatorio'),
    path('api/', include(router.urls)),
    
    path('relatorio/', views.relatorio, name='relatorio'),


]