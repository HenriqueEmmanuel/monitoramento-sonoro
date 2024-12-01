import os
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
from fpdf import FPDF
import tempfile 
from PIL import Image
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt


@login_required
def dashboard(request):
    total_medicoes = NiveisDeRuido.objects.count() 

    niveis_atividade = NiveisDeRuido.objects.filter(status=True)
    
    tempo_atividade_total = timedelta()
    for nivel in niveis_atividade:
        data_hora = datetime.combine(nivel.data, nivel.hora)
        tempo_atividade_total += timedelta(hours=1)  
    horas_atividade = tempo_atividade_total.total_seconds() / 3600  

    try:
        ultima_medicao_registro = NiveisDeRuido.objects.latest('data')
        ultima_medicao_decibel = ultima_medicao_registro.decibeis
        ultima_medicao_status = ultima_medicao_registro.status
    except NiveisDeRuido.DoesNotExist:
        ultima_medicao_decibel = None
        ultima_medicao_status = False 

    if ultima_medicao_status:
        status_sensor = "ON"
    else:
        status_sensor = "OFF"
    
    nome_sensor = "Sensor 1"
    
    return render(request, 'frontend/dashboard.html', {
        'total_medicoes': total_medicoes,
        'horas_atividade': round(horas_atividade, 2),  
        'ultima_medicao': ultima_medicao_decibel,  
        'status_sensor': status_sensor,
        'nome_sensor': nome_sensor,
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





def nome_mes_sem_acentuacao(mes_num):
    meses = [
        "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    return meses[mes_num - 1] if 1 <= mes_num <= 12 else 'Mes invalido'
from django.core.exceptions import ValidationError

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
        else:
            raise ValidationError("Período do dia inválido")

    if perturbacao:
        if perturbacao == 'sim':
            niveis = niveis.filter(status=True)
        elif perturbacao == 'nao':
            niveis = niveis.filter(status=False)
        else:
            raise ValidationError("Valor de perturbacao inválido")

    if mes_registro:
        try:
            mes_registro = int(mes_registro)
            niveis = niveis.filter(data__month=mes_registro)
        except ValueError:
            raise ValidationError("Mês de registro inválido")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_niveis_ruido.csv"'

    writer = csv.writer(response)

    writer.writerow(['Relatorio Tecnico de Niveis de Ruido'])
    writer.writerow(['Este relatorio contem dados sobre os niveis de ruido coletados pela plataforma EchoWarden.'])
    writer.writerow(['A plataforma EchoWarden e um sistema de monitoramento ambiental projetado para registrar e analisar os niveis de ruido em areas urbanas e industriais.'])
    writer.writerow(['Ele utiliza sensores acusticos distribuídos para coletar dados em tempo real, permitindo uma analise detalhada das condicoes de ruido e seu impacto na saude publica e qualidade de vida.'])
    writer.writerow([f'Relatorio gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow(['Fonte de dados: Banco de Dados - Modelo NiveisDeRuido'])
    writer.writerow([''])
    
    writer.writerow(['Campos do Relatorio:'])
    writer.writerow(['- "Data": Data e hora em que o nivel de ruido foi registrado. Essa informacao e crucial para determinar a tendencia temporal dos niveis de ruido e identificar padroes.'])
    writer.writerow(['- "Nivel de Ruido (dB)": Representa o nivel de pressao sonora medido em decibeis (dB), uma unidade logaritmica que expressa a intensidade do som. Niveis mais altos podem indicar poluicao sonora e impacto ambiental.'])
    writer.writerow(['- "Status de Perturbacao": Indica se o nivel de ruido registrado ultrapassou o limite toleravel para o ambiente em questao. A presenca de um "status de perturbacao" sugere que os niveis de ruido podem ser prejudiciais.'])
    writer.writerow(['- "Mes": Mes em que o dado foi registrado. Isso ajuda a observar variacoes sazonais ou tendencias anuais no comportamento do ruido.'])
    writer.writerow(['- "Periodo do dia": Define a faixa horaria em que o dado foi coletado, ajudando a analisar as variacoes nos niveis de ruido ao longo do dia.'])

    writer.writerow([''])
    writer.writerow([f'Filtro - Periodo do dia: {periodo_dia if periodo_dia else "Todos os periodos"}'])
    writer.writerow([f'Filtro - Status de perturbacao: {perturbacao if perturbacao else "Todos os status"}'])
    writer.writerow([f'Filtro - Mes de registro: {mes_registro if mes_registro else "Todos os meses"}'])
    writer.writerow([''])

    writer.writerow(['Descricao do Status de Perturbacao:'])
    writer.writerow(['- "Perturbado" (status=1): Indica que o nivel de ruido registrado ultrapassou o limite estabelecido, podendo causar impactos na saude humana e no bem-estar social.'])
    writer.writerow(['- "Normal" (status=0): Indica que o nivel de ruido esta dentro dos parametros aceitaveis para o ambiente e nao e considerado perturbador.'])
    writer.writerow([''])
    
    writer.writerow(['Limites de Nivel de Ruido:'])
    writer.writerow(['- Os limites de ruido considerados seguros podem variar de acordo com o local (urbano, industrial, residencial) e a legislacao local. Em areas residenciais, por exemplo, niveis superiores a 55 dB durante a noite sao geralmente considerados prejudiciais.'])
    writer.writerow(['- O monitoramento continuo de ruido e fundamental para identificar fontes de poluicao sonora e adotar medidas corretivas, como o controle de trafego ou regulamentacao de horarios de funcionamento de industrias.'])
    writer.writerow([''])

    writer.writerow(['Data', 'Nivel de Ruido (dB)', 'Status de Perturbacao', 'Mes', 'Periodo do dia'])

    for nivel in niveis:
        data_formatada = nome_mes_sem_acentuacao(nivel.data.month) if nivel.data else 'Data nao disponivel'
        status_texto = 'Perturbado' if nivel.status else 'Normal'
        writer.writerow([nivel.data, nivel.decibeis, status_texto, data_formatada, nivel.hora])


    writer.writerow([''])
    writer.writerow(['Conclusao:'])
    writer.writerow(['Este relatório fornece uma visão detalhada sobre os níveis de ruído em áreas monitoradas pela plataforma EchoWarden, permitindo a identificação de períodos críticos de poluição sonora e o acompanhamento da eficácia de medidas corretivas, caso necessário.'])
    writer.writerow(['Com base nas medições coletadas e nos filtros aplicados, é possível observar padrões de variação nos níveis de ruído ao longo do tempo, bem como a relação entre o status de perturbação e os horários de maior incidência de níveis elevados de ruído.'])
    writer.writerow(['A coleta contínua e a análise desses dados são fundamentais para a implementação de políticas públicas eficazes de controle da poluição sonora e para a melhoria da qualidade de vida nas comunidades.'])
    writer.writerow(['Medidas corretivas podem incluir ajustes no planejamento urbano, como a regulamentação de horários de funcionamento de atividades industriais e comerciais, a implantação de zonas silenciosas em áreas residenciais, e o incentivo ao uso de tecnologias que reduzam a emissão de ruído.'])
    writer.writerow(['Além disso, a conscientização pública sobre os impactos da poluição sonora na saúde humana deve ser uma prioridade, com campanhas educativas sobre limites de exposição ao ruído e práticas adequadas para minimizar os efeitos negativos da exposição contínua ao som excessivo.'])
    writer.writerow(['A plataforma EchoWarden, ao fornecer dados em tempo real sobre os níveis de ruído, pode ser um instrumento valioso para órgãos de regulamentação, comunidades locais e pesquisadores que buscam entender e combater a poluição sonora.'])
    writer.writerow(['A continuidade do monitoramento será essencial para garantir que as intervenções adotadas sejam eficazes na melhoria das condições acústicas das áreas monitoradas.'])
    writer.writerow([''])

    return response






def relatoriofinal(request):
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
        else:
            raise ValidationError("Período do dia inválido")

    if perturbacao:
        if perturbacao == 'sim':
            niveis = niveis.filter(status=True)
        elif perturbacao == 'nao':
            niveis = niveis.filter(status=False)
        else:
            raise ValidationError("Valor de perturbacao inválido")

    if mes_registro:
        try:
            mes_registro = int(mes_registro)  #TEM QUE CONVERTER PARA INTERIROR PARA FUNCIONAR
            if not (1 <= mes_registro <= 12):
                raise ValidationError("Mês de registro inválido")
            niveis = niveis.filter(data__month=mes_registro)
        except ValueError:
            raise ValidationError("Mês de registro inválido")

    context = {
        'niveis': niveis,
        'periodo_dia': periodo_dia,
        'perturbacao': perturbacao,
        'mes_registro': mes_registro
    }

    return render(request, 'frontend/relatorio.html', context)
