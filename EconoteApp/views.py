from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Aluno, Professor

# Página inicial
def index(request):
    return render(request, 'projeto/index.html')

# Cadastro de usuário (aluno ou professor)
def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        siape = request.POST.get('siape', '').strip()
        curso = request.POST.get('curso', '').strip()

        if not nome or not email or not senha or not tipo_usuario:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('cadastro')

        if tipo_usuario == 'aluno':
            if not matricula or not curso:
                messages.error(request, 'Matrícula e curso são obrigatórios para alunos.')
                return redirect('cadastro')
            if not email.endswith('@aluno.ifce.edu.br'):
                messages.error(request, 'E-mail inválido para aluno. Use seu e-mail institucional: @aluno.ifce.edu.br')
                return redirect('cadastro')

        if tipo_usuario == 'professor':
            if not siape:
                messages.error(request, 'SIAPE é obrigatório para professores.')
                return redirect('cadastro')
            if not email.endswith('@ifce.edu.br') or '@aluno.ifce.edu.br' in email:
                messages.error(request, 'E-mail inválido para professor. Use seu e-mail institucional.')
                return redirect('cadastro')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('cadastro')

        user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
        perfil = PerfilUsuario.objects.create(user=user, tipo_usuario=tipo_usuario)

        if tipo_usuario == 'aluno':
            Aluno.objects.create(perfil=perfil, matricula=matricula, curso=curso)
            grupo_aluno, _ = Group.objects.get_or_create(name='Aluno')
            user.groups.add(grupo_aluno)
        else:
            Professor.objects.create(perfil=perfil, SIAPE=siape)
            grupo_professor, _ = Group.objects.get_or_create(name='Professor')
            user.groups.add(grupo_professor)

        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')

    return render(request, 'projeto/cadastro.html')


# Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='Aluno').exists():
                return redirect('home_aluno')
            elif user.groups.filter(name='Professor').exists():
                return redirect('home_professor')
            else:
                messages.warning(request, 'Seu perfil não está associado a um grupo válido.')
                return redirect('login')
        else:
            messages.error(request, 'Usuário não cadastrado ou senha incorreta.')
            return redirect('login')

    return render(request, 'projeto/login.html')

# Página inicial do aluno
@login_required
def home_aluno(request):
    if request.user.groups.filter(name='Aluno').exists():
        return render(request, 'projeto/home_aluno.html')
    else:
        return redirect('index')

# Página inicial do professor
@login_required
def home_professor(request):
    if request.user.groups.filter(name='Professor').exists():
        return render(request, 'projeto/home_professor.html')
    else:
        return redirect('index')

@login_required
def perfil_view(request):
    return render(request, 'projeto/perfil.html')

@login_required
def sobre_view(request):
    return render(request, 'projeto/sobre.html')

@login_required
def solicitar_notebook_view(request):
    return render(request, 'projeto/solicitar_notebook.html')

@login_required
def minhas_solicitacoes_view(request):
    return render(request, 'projeto/minhas_solicitacoes.html')

@login_required
def devolucoes_manutencao_view(request):
    return render(request, 'projeto/devolucoes_manutencao.html')

@login_required
def cadastro_notebooks_view(request):
    return render(request, 'projeto/cadastro_notebooks.html')

@login_required
def avaliacao_solicitacao_view(request):
    if request.user.groups.filter(name='Professor').exists():
        return render(request, 'projeto/avaliacao_solicitacao.html')
    else:
        return redirect('index')

@login_required
def indicar_aluno_view(request):
    if request.user.groups.filter(name='Professor').exists():
        return render(request, 'projeto/indicar_aluno.html')
    else:
        return redirect('index')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')
