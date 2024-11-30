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
from datetime import datetime, timedelta
from django.http import HttpResponse
import logging
from django.db.models import Q
from django.http import JsonResponse
from .models import NiveisDeRuido
from django.db.models import F
import matplotlib.dates as mdates
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
from django.shortcuts import redirect
from django.contrib.auth import logout
from io import StringIO
import csv


@login_required
def dashboard(request):
    total_medicoes = NiveisDeRuido.objects.count() 
    
    # esse aqui so calcula se for TRUE 
    niveis_atividade = NiveisDeRuido.objects.filter(status=True)
    
    tempo_atividade_total = timedelta()
    for nivel in niveis_atividade:
        data_hora = datetime.combine(nivel.data, nivel.hora)

        
        
        

        tempo_atividade_total += timedelta(hours=1)  
        
    horas_atividade = tempo_atividade_total.total_seconds() / 3600  
    
    ultima_medicao_registro = NiveisDeRuido.objects.latest('data')  
    ultima_medicao_decibel = ultima_medicao_registro.decibeis if ultima_medicao_registro else None

    
    
    return render(request, 'frontend/dashboard.html', {
        'total_medicoes': total_medicoes,
        'horas_atividade': round(horas_atividade, 2),  
        'ultima_medicao': ultima_medicao_decibel,  
        
    })





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
    periodo_dia = request.GET.get('periodo-dia')
    perturbacao = request.GET.get('perturbacao')
    mes_registro = request.GET.get('mes-registro')

    niveis = NiveisDeRuido.objects.all()

    if periodo_dia:
        if periodo_dia == 'manha':
            niveis = niveis.filter(hora__lt='12:00:00')
        elif periodo_dia == 'tarde':
            niveis = niveis.filter(hora__gte='12:00:00', hora__lt='18:00:00')
        elif periodo_dia == 'noite':
            niveis = niveis.filter(hora__gte='18:00:00')

    if perturbacao:
        if perturbacao == 'sim':
            niveis = niveis.filter(status=True)
        elif perturbacao == 'nao':
            niveis = niveis.filter(status=False)

    if mes_registro:
        niveis = niveis.filter(data__month=mes_registro)

    context = {
        'niveis': niveis,
        'periodo_dia': periodo_dia,
        'perturbacao': perturbacao,
    }
    return render(request, 'relatorio.html', context)




#ESTE JA ESTÁ FUNCIONANDO


def grafico(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    try:
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Datas inválidas fornecidas.", status=400)

    niveis = NiveisDeRuido.objects.all()
    if data_inicio and data_fim:
        niveis = niveis.filter(data__range=(data_inicio, data_fim))

    dates = []
    decibeis = []

    for nivel in niveis:
        if nivel.data and nivel.hora:
            combined_date = datetime.combine(nivel.data, nivel.hora)
            dates.append(combined_date)
            decibeis.append(nivel.decibeis)

    if not decibeis:
        return HttpResponse("Nenhum dado disponível para o período selecionado.", status=404)

    sorted_data = sorted(zip(dates, decibeis), key=lambda x: x[0])
    dates, decibeis = zip(*sorted_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(dates, decibeis, color='skyblue', width=0.01) 

    ax.set_xlabel('Data e Hora')
    ax.set_ylabel('Nível de Ruído (dB)')
    ax.set_title('Gráfico de Níveis de Ruído ao Longo do Tempo')
    plt.xticks(rotation=45, ha='right')
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.set_ylim(0, max(decibeis) * 1.1)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    return HttpResponse(buffer, content_type='image/png')




def logout_view(request):
    logout(request) 
    return redirect('/')




def gerar_relatorio(request):
    periodo_dia = request.GET.get('periodo-dia')
    perturbacao = request.GET.get('perturbacao')
    mes_registro = request.GET.get('mes-registro')

    niveis = NiveisDeRuido.objects.all()

    if periodo_dia:
        if periodo_dia == 'manha':
            niveis = niveis.filter(hora__lt='12:00:00')
        elif periodo_dia == 'tarde':
            niveis = niveis.filter(hora__gte='12:00:00', hora__lt='18:00:00')
        elif periodo_dia == 'noite':
            niveis = niveis.filter(hora__gte='18:00:00')

    if perturbacao:
        if perturbacao == 'sim':
            niveis = niveis.filter(status=True)
        elif perturbacao == 'nao':
            niveis = niveis.filter(status=False)

    if mes_registro:
        niveis = niveis.filter(data__month=mes_registro)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_niveis_ruido.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'dB', 'Perturbacao', 'Mês', 'Período'])

    for nivel in niveis:
        data_formatada = nivel.data.strftime('%B') if nivel.data else 'Data não disponível'
        writer.writerow([nivel.data, nivel.decibeis, 'Sim' if nivel.status else 'Não', data_formatada, nivel.hora])

    return response















