from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('cadastro/', views.cadastroPage, name='cadastro'),
]

