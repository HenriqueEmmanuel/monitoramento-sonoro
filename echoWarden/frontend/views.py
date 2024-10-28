from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError

def loginPage(request):
    if request.method == "GET":
        return render(request, 'frontend/loginPage.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'frontend/loginPage.html', {'error': 'Credenciais inválidas'})

def cadastroPage(request):
    if request.method == "GET":
        return render(request, 'frontend/cadastroPage.html')
    else:
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        errors = []

        if User.objects.filter(email=email).exists():
            errors.append('Email já cadastrado.')

        if User.objects.filter(username=name).exists():
            errors.append('Nome de usuário já cadastrado.')

        if errors:
            return render(request, 'frontend/cadastroPage.html', {'errors': errors})

        try:
            user = User.objects.create_user(username=name, email=email, password=password)
            return redirect('login')
        except ValidationError as e:
            return render(request, 'frontend/cadastroPage.html', {'errors': [str(e)]})
        except Exception as e:
            return render(request, 'frontend/cadastroPage.html', {'errors': [f'Erro ao cadastrar usuário: {str(e)}']})
