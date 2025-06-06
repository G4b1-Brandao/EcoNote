from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .models import PerfilUsuario, Aluno, Professor, Notebook, SolicitacaoNotebook, DevolucaoNotebook
from .forms import NotebookForm, SolicitacaoNotebookForm


# Helpers
def is_aluno(user):
    return user.groups.filter(name='Aluno').exists()

def is_professor(user):
    return user.groups.filter(name='Professor').exists()

def is_admin(user):
    return user.is_superuser


# Página inicial
def index(request):
    return render(request, 'projeto/index.html')


# Cadastro de usuário
def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        siape = request.POST.get('siape', '').strip()
        curso = request.POST.get('curso', '').strip()

        if tipo_usuario not in ['aluno', 'professor']:
            messages.error(request, 'Tipo de usuário inválido.')
            return redirect('cadastro')

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
            if user.is_superuser or user.is_staff:
                return redirect('home_ADM')
            elif is_aluno(user):
                return redirect('home_aluno')
            elif is_professor(user):
                return redirect('home_professor')
            else:
                messages.warning(request, 'Seu perfil não está associado a um grupo válido.')
                return redirect('login')
        else:
            messages.error(request, 'Usuário não cadastrado ou senha incorreta.')
            return redirect('login')

    return render(request, 'projeto/login.html')


# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Home
@login_required
def home_aluno(request):
    if is_aluno(request.user):
        return render(request, 'projeto/home_aluno.html')
    return redirect('index')


@login_required
def home_professor(request):
    if is_professor(request.user):
        return render(request, 'projeto/home_professor.html')
    return redirect('index')


@user_passes_test(is_admin)
@login_required
def home_ADM_view(request):
    return render(request, 'projeto/home_ADM.html')
# Informações
@login_required
def perfil_view(request):
    return render(request, 'projeto/perfil.html')

@login_required
def sobre_view(request):
    return render(request, 'projeto/sobre.html')

def solicitar_notebook_view(request):
    notebooks_disponiveis = Notebook.objects.filter(status='oky', validado=True)

    if request.method == 'POST':
        form = SolicitacaoNotebookForm(request.POST, request.FILES)
        if form.is_valid():
            notebook_id = request.POST.get('notebook_selecionado')

            if not notebook_id:
                messages.error(request, 'Você precisa selecionar um notebook.')
            else:
                notebook = get_object_or_404(Notebook, id=notebook_id, status='oky', validado=True)

                solicitacao = form.save(commit=False)
                solicitacao.aluno = request.user
                solicitacao.notebook = notebook
                solicitacao.save()

                messages.success(request, 'Solicitação realizada com sucesso!')
                return redirect('home_aluno')
    else:
        nome_completo = request.user.get_full_name()
        form = SolicitacaoNotebookForm(initial={'nome': nome_completo})

    return render(request, 'projeto/solicitar_notebook.html', {
        'form': form,
        'notebooks_disponiveis': notebooks_disponiveis
    })

@login_required
def solicitar_devolucao(request):
    aluno = request.user

    try:
        solicitacao = SolicitacaoNotebook.objects.get(aluno=aluno, status='aprovado')
    except SolicitacaoNotebook.DoesNotExist:
        solicitacao = None

    if request.method == 'POST' and solicitacao:
        motivo = request.POST.get('motivo')
        data_sugerida = request.POST.get('data')
        detalhes = request.POST.get('detalhes')
        compromisso = request.POST.get('compromisso') == 'on'

        if not compromisso:
            messages.error(request, 'Você deve aceitar o compromisso.')
        else:
            DevolucaoNotebook.objects.create(
                aluno=aluno,
                solicitacao=solicitacao,
                motivo=motivo,
                data_sugerida=data_sugerida,
                detalhes=detalhes,
                compromisso_aceito=True
            )
            solicitacao.status = 'devolucao_pendente'
            solicitacao.save()

            messages.success(request, 'Solicitação de devolução enviada com sucesso.')
            return redirect('home_aluno')

    return render(request, 'projeto/devolucoes_manutencao.html', {
        'solicitacao': solicitacao
    })

@login_required
def minhas_solicitacoes_view(request):
    solicitacoes = SolicitacaoNotebook.objects.filter(aluno=request.user).order_by('-data_solicitacao')
    return render(request, 'projeto/minhas_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def devolucoes_manutencao_view(request):
    return render(request, 'projeto/devolucoes_manutencao.html')

# Professor
@login_required
def avaliacao_solicitacao_view(request):
    if is_professor(request.user):
        return render(request, 'projeto/avaliacao_solicitacao.html')
    return redirect('index')

@login_required
def indicar_aluno_view(request):
    if is_professor(request.user):
        return render(request, 'projeto/indicar_aluno.html')
    return redirect('index')

# Admin - Gerenciamento
@user_passes_test(is_admin)
@login_required
def gerenciamento_notebooks_view(request):
    notebooks_pendentes = Notebook.objects.filter(status='pendente', validado=False)
    return render(request, 'projeto/gerenciamento_notebooks.html', {'notebooks': notebooks_pendentes})

@require_POST
@user_passes_test(is_admin)
@login_required
def aprovar_notebook_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    notebook.status = 'oky'
    notebook.validado = True
    notebook.save()
    messages.success(request, 'Notebook aprovado e validado com sucesso!')
    return redirect('gerenciamento_notebooks')

@require_POST
@user_passes_test(is_admin)
@login_required
def recusar_notebook_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    notebook.status = 'recusado'
    notebook.validado = False
    notebook.save()
    messages.warning(request, 'Notebook recusado.')
    return redirect('gerenciamento_notebooks')

@login_required
def cadastro_notebooks_view(request):
    if request.method == 'POST':
        form = NotebookForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            notebook = form.save(commit=False)
            notebook.usuario = request.user
            if not request.user.is_superuser:
                notebook.status = 'pendente'
                notebook.validado = False
            notebook.save()
            messages.success(request, 'Notebook cadastrado com sucesso!')
            return redirect('cadastro_notebooks')
        else:
            messages.error(request, 'Erro ao cadastrar notebook.')
    else:
        form = NotebookForm(user=request.user)
    return render(request, 'projeto/cadastro_notebooks.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def avaliar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        tempo_concedido = request.POST.get('tempo_concedido')

        solicitacao.status = status
        solicitacao.tempo_concedido = tempo_concedido if status == 'aprovado' else None
        solicitacao.avaliado_por = request.user
        solicitacao.data_avaliacao = timezone.now()
        solicitacao.save()

        messages.success(request, 'Solicitação avaliada com sucesso.')
        return redirect('lista_solicitacoes')

    return render(request, 'projeto/avaliacao_solicitacao.html', {'solicitacao': solicitacao})

@user_passes_test(is_admin)
@login_required
def lista_notebooks_view(request):
    return render(request, 'projeto/lista_notebooks.html')

@user_passes_test(is_admin)
@login_required
def lista_solicitacoes_view(request):
    solicitacoes = SolicitacaoNotebook.objects.all().order_by('-data_solicitacao')
    return render(request, 'projeto/lista_solicitacoes.html', {'solicitacoes': solicitacoes})

@user_passes_test(is_admin)
@login_required
def lista_usuarios_view(request):
    return render(request, 'projeto/lista_usuarios.html')

@user_passes_test(is_admin)
@login_required
def relatorios_view(request):
    return render(request, 'projeto/relatorios.html')


def lista_solicitacoes(request):
    # Busca todas as solicitações com status pendente
    solicitacoes = SolicitacaoNotebook.objects.filter(status='Pendente')
    return render(request, 'projeto/lista_solicitacoes.html', {'solicitacoes': solicitacoes})


