from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        # Caso o usuário não esteja logado, redireciona para o login
        return redirect('login')  # Nome da URL de login

    # Caso o usuário esteja logado, exibe o dashboard
    return render(request, 'frontend/dashboard.html', {'usuario': request.user})
