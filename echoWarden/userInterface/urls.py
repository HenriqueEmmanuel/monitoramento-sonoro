from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NiveisDeRuidoViewSet, ReceberRuido
from django.contrib.auth import views as auth_views
from userInterface import views



router = DefaultRouter()
router.register(r'niveis_de_ruido', NiveisDeRuidoViewSet)

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relatorio/', views.relatorio, name='relatorio'),
    path('api/', include(router.urls)),
    path('grafico/', views.grafico, name='grafico_niveis'),
    path('grafico/', views.grafico, name='grafico'),
    path('api/niveis_de_ruido/', ReceberRuido.as_view(), name='niveis_de_ruido'),

    path('relatorio/', views.historico_medicoes, name='relatorio'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('logout/', views.logout_view, name='logout'),
    
    
    
    path('gerar-relatorio/', views.gerar_relatorio, name='gerar_relatorio'),
    path('gerar_relatorio_csv/', views.relatoriofinal, name='gerar_relatorio_csv'),
    
]