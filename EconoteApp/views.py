from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import PerfilUsuario, Aluno, Professor


def index(request):
    return render(request, 'projeto/index.html')


def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', '').strip()  # 'aluno' ou 'professor'
        matricula = request.POST.get('matricula', '').strip()
        curso = request.POST.get('curso', '').strip()  # só se for aluno

        # Verifica campos obrigatórios
        if not nome or not email or not senha or not tipo_usuario or not matricula:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('cadastro')

        if tipo_usuario == 'aluno' and not curso:
            messages.error(request, 'O campo curso é obrigatório para alunos.')
            return redirect('cadastro')

        # Verifica se o usuário já existe
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('cadastro')

        # Cria o usuário Django
        user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)

        # Cria o perfil personalizado
        perfil = PerfilUsuario.objects.create(user=user, tipo_usuario=tipo_usuario)

        # Cria aluno ou professor
        if tipo_usuario == 'aluno':
            Aluno.objects.create(perfil=perfil, matricula=matricula, curso=curso)
        else:
            Professor.objects.create(perfil=perfil, matricula=matricula)

        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')

    return render(request, 'projeto/cadastro.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        user = authenticate(request, username=email, password=senha)
        if user is not None:
            login(request, user)
            return redirect('index')  # redireciona para a home após login
        else:
            messages.error(request, 'E-mail ou senha inválidos.')
            return redirect('login')

    return render(request, 'projeto/login.html')