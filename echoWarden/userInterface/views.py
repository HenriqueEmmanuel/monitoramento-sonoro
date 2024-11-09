from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import NiveisDeRuido
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NiveisDeRuido
from .serializers import NiveisDeRuidoSerializer
from rest_framework import viewsets



@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        # Caso o usuário não esteja logado, redireciona para o login
        return redirect('login')  # Nome da URL de login

    # Caso o usuário esteja logado, exibe o dashboard
    return render(request, 'frontend/dashboard.html', {'usuario': request.user})

@login_required
def relatorio(request):
    if not request.user.is_authenticated:
        # Caso o usuário não esteja logado, redireciona para o login
        return redirect('login')  # Nome da URL de login
    
    return render(request, 'frontend/relatorio.html', {'usuario': request.user})


class ReceberRuido(APIView):
    permission_classes = [AllowAny]  # Permite qualquer pessoa acessar
    def post(self, request):
        ...




class NiveisDeRuidoViewSet(viewsets.ModelViewSet):
    queryset = NiveisDeRuido.objects.all()
    serializer_class = NiveisDeRuidoSerializer