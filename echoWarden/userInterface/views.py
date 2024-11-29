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
from datetime import datetime
from django.http import HttpResponse
import logging
from django.db.models import Q
from django.http import JsonResponse
from .models import NiveisDeRuido



@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    return render(request, 'frontend/dashboard.html', {'usuario': request.user})

@login_required
def relatorio(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'frontend/relatorio.html', {'usuario': request.user})


class ReceberRuido(APIView):
    permission_classes = [AllowAny]  
    def post(self, request):
        ...


class NiveisDeRuidoViewSet(viewsets.ModelViewSet):
    queryset = NiveisDeRuido.objects.all()
    serializer_class = NiveisDeRuidoSerializer




@login_required
def historico_medicoes(request):
    """
    View para filtrar o histórico de medições baseado nos parâmetros fornecidos pelo usuário.
    """
    # Obtendo os parâmetros do filtro a partir da URL (query parameters)
    data = request.GET.get('data', None)
    hora = request.GET.get('hora', None)
    status = request.GET.get('status', None)
    decibeis = request.GET.get('decibeis', None)

    # Inicia um queryset para os níveis de ruído
    niveis = NiveisDeRuido.objects.all()

    # Aplica os filtros de acordo com os parâmetros recebidos
    filtros = Q()  # Filtro dinâmico usando Q

    if data:
        filtros &= Q(data=data)  # Filtra por data
    if hora:
        filtros &= Q(hora=hora)  # Filtra por hora
    if status is not None:
        # Converte status para booleano (True ou False)
        filtros &= Q(status=status == 'true')  # Filtra por status
    if decibeis:
        try:
            decibeis_valor = float(decibeis)
            filtros &= Q(decibeis=decibeis_valor)  # Filtra por decibéis
        except ValueError:
            pass  # Ignora erro caso o valor de decibéis não seja válido

    # Aplica os filtros no queryset
    niveis = niveis.filter(filtros)

    # Ordena os resultados por data (opcional)
    niveis = niveis.order_by('-data', '-hora')

    # Retorna a resposta com os dados filtrados


            
    return render(request, 'relatorio.html', {'niveis': niveis})




