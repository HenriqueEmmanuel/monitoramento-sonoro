from django.shortcuts import render
from django.http import HttpResponse

def homePage(request):
    return render(request, 'frontend/loginPage.html')

def cadastroPage(request):
    return render(request, 'frontend/cadastroPage.html')

def dashboard(request):
    return render(request, 'frontend/dashboard.html')