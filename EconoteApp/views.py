from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.utils.timezone import localdate, now as timezone_now
from django.db.models import Q
from .models import PerfilUsuario, Aluno, Professor, Notebook, SolicitacaoNotebook, DevolucaoNotebook, EmprestimoNotebook, AvaliacaoAluno, Manutencao
from .forms import NotebookForm, SolicitacaoNotebookForm, UserUpdateForm, AlunoUpdateForm, ProfessorUpdateForm
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
import datetime


def is_aluno(user):
    return user.groups.filter(name='Aluno').exists()

def is_professor(user):
    return user.groups.filter(name='Professor').exists()

def is_admin(user):
    return user.is_superuser

def index(request):
    context = {}
    if request.user.is_authenticated:
        context['user_is_aluno'] = is_aluno(request.user)
        context['user_is_professor'] = is_professor(request.user)
        context['user_is_admin'] = is_admin(request.user)

    return render(request, 'projeto/index.html', context)

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        siape = request.POST.get('siape', '').strip()
        curso = request.POST.get('curso', '').strip()

        if tipo_usuario not in ['aluno', 'professor'] or not nome or not email or not senha:
            messages.error(request, 'Preencha todos os campos obrigatórios corretamente.')
            return redirect('cadastro')

        if tipo_usuario == 'aluno':
            if not matricula or not curso or not email.endswith('@aluno.ifce.edu.br'):
                messages.error(request, 'Dados de aluno inválidos ou e-mail não institucional.')
                return redirect('cadastro')

        if tipo_usuario == 'professor':
            if not siape or not email.endswith('@ifce.edu.br') or '@aluno.ifce.edu.br' in email:
                messages.error(request, 'Dados de professor inválidos ou e-mail não institucional.')
                return redirect('cadastro')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('cadastro')

        user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
        perfil = PerfilUsuario.objects.create(user=user, tipo_usuario=tipo_usuario)

        if tipo_usuario == 'aluno':
            Aluno.objects.create(perfil=perfil, matricula=matricula, curso=curso)
            grupo, _ = Group.objects.get_or_create(name='Aluno')
        else:
            Professor.objects.create(perfil=perfil, siape=siape) # Corrigido para 'siape' minúsculo
            grupo, _ = Group.objects.get_or_create(name='Professor')

        user.groups.add(grupo)
        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')

    return render(request, 'projeto/cadastro.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        user = authenticate(request, username=email, password=senha)

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('home_ADM')
            elif is_aluno(user):
                return redirect('home_aluno')
            elif is_professor(user):
                return redirect('home_professor')
            else:
                messages.warning(request, 'Usuário sem grupo válido.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
        return redirect('login')

    return render(request, 'projeto/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def perfil_view(request):
    context = {}
    context['user_is_aluno'] = is_aluno(request.user)
    context['user_is_professor'] = is_professor(request.user)
    context['user_is_admin'] = is_admin(request.user)

    return render(request, 'projeto/perfil.html', context)

@login_required
def perfil_editar_view(request):
    user_form = UserUpdateForm(instance=request.user)
    aluno_form = None
    professor_form = None

    try:
        perfil_usuario = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        messages.error(request, 'Erro: Perfil de usuário não encontrado.')
        return redirect('perfil')

    if perfil_usuario.tipo_usuario == 'aluno':
        try:
            aluno_instance = Aluno.objects.get(perfil=perfil_usuario)
            aluno_form = AlunoUpdateForm(instance=aluno_instance)
        except Aluno.DoesNotExist:
            messages.error(request, 'Erro: Dados de aluno não encontrados.')
            return redirect('perfil')

    elif perfil_usuario.tipo_usuario == 'professor':
        try:
            professor_instance = Professor.objects.get(perfil=perfil_usuario)
            professor_form = ProfessorUpdateForm(instance=professor_instance)
        except Professor.DoesNotExist:
            messages.error(request, 'Erro: Dados de professor não encontrados.')
            return redirect('perfil')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)

        if perfil_usuario.tipo_usuario == 'aluno':
            aluno_form = AlunoUpdateForm(request.POST, instance=aluno_instance)
        elif perfil_usuario.tipo_usuario == 'professor':
            professor_form = ProfessorUpdateForm(request.POST, instance=professor_instance)

        forms_valid = True
        if user_form.is_valid():
            user_form.save()
        else:
            forms_valid = False

        if aluno_form and aluno_form.is_valid():
            aluno_form.save()
        elif aluno_form and not aluno_form.is_valid():
            forms_valid = False

        if professor_form and professor_form.is_valid():
            professor_form.save()
        elif professor_form and not professor_form.is_valid():
            forms_valid = False

        if forms_valid:
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Ocorreu um erro ao atualizar seu perfil. Por favor, verifique os dados.')

    context = {
        'user_form': user_form,
        'aluno_form': aluno_form,
        'professor_form': professor_form,
        'tipo_usuario': perfil_usuario.tipo_usuario,
        'user_is_aluno': is_aluno(request.user),
        'user_is_professor': is_professor(request.user),
        'user_is_admin': is_admin(request.user),
    }
    return render(request, 'projeto/perfil_editar.html', context)

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

@login_required
@user_passes_test(is_admin)
def home_ADM_view(request):
    return render(request, 'projeto/home_ADM.html')

@login_required
def solicitar_notebook_view(request):
    notebooks_disponiveis = Notebook.objects.filter(
        Q(status='disponivel') | Q(status='oky'),
        validado=True
    )

    if request.method == 'POST':
        form = SolicitacaoNotebookForm(request.POST, request.FILES)
        notebook_id = request.POST.get('notebook_selecionado')
        if not notebook_id:
            messages.error(request, 'Você precisa selecionar um notebook.')
        elif form.is_valid():
            notebook = get_object_or_404(Notebook,
                                         Q(status='disponivel') | Q(status='oky'),
                                         id=notebook_id,
                                         validado=True)
            solicitacao = form.save(commit=False)
            solicitacao.aluno = request.user
            solicitacao.notebook = notebook
            solicitacao.save()
            messages.success(request, 'Solicitação realizada com sucesso!')
            return redirect('minhas_solicitacoes')
    else:
        form = SolicitacaoNotebookForm(initial={'nome': request.user.get_full_name()})

    return render(request, 'projeto/solicitar_notebook.html', {
        'form': form,
        'notebooks_disponiveis': notebooks_disponiveis
    })


# --- Devoluções ---
@login_required
def solicitar_devolucao(request):
    try:
        solicitacao = SolicitacaoNotebook.objects.get(aluno=request.user, status='Aprovado')
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
                aluno=request.user,
                solicitacao=solicitacao,
                motivo=motivo,
                data_sugerida=data_sugerida,
                detalhes=detalhes,
                compromisso_aceito=True
            )
            solicitacao.status = 'devolucao_pendente'
            solicitacao.save()
            messages.success(request, 'Solicitação de devolução enviada com sucesso.')
            return redirect('solicitar_devolucao')
    return render(request, 'projeto/devolucoes_manutencao.html', {'solicitacao': solicitacao})


@login_required
def minhas_solicitacoes_view(request):
    solicitacoes = SolicitacaoNotebook.objects.filter(aluno=request.user).order_by('-data_solicitacao')
    return render(request, 'projeto/minhas_solicitacoes.html', {'solicitacoes': solicitacoes})



@login_required
@user_passes_test(is_professor)
def avaliacao_solicitacao_view(request):
    if is_professor(request.user):
        return render(request, 'projeto/avaliacao_solicitacao.html')
    return redirect('index')

@login_required
@user_passes_test(is_professor)
def indicar_aluno_view(request):
    solicitacoes_pendentes_indicacao = SolicitacaoNotebook.objects.filter(
        status='Pendente'
    ).order_by('-data_solicitacao')

    if request.method == 'POST':
        solicitacao_id = request.POST.get('solicitacao_id')
        indicacao_texto = request.POST.get('indicacao_texto')

        solicitacao_a_indicar = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)

        solicitacao_a_indicar.indicacao_professor = indicacao_texto
        solicitacao_a_indicar.indicado_por_professor = request.user
        solicitacao_a_indicar.save()

        messages.success(request, 'Indicação adicionada com sucesso!')
        return redirect('indicar_aluno')

    return render(request, 'projeto/indicar_aluno.html', {
        'solicitacoes': solicitacoes_pendentes_indicacao
    })


@login_required
@user_passes_test(is_admin)
def gerenciamento_notebooks_view(request):
    all_notebooks = Notebook.objects.all().order_by('-data_cadastro')

    notebooks_pendentes = [nb for nb in all_notebooks if not nb.validado]
    notebooks_validados = [nb for nb in all_notebooks if nb.validado]

    opcoes_status = Notebook.STATUS_CHOICES

    context = {
        'notebooks_pendentes': notebooks_pendentes,
        'notebooks_validados': notebooks_validados,
        'opcoes_status': opcoes_status,
    }
    return render(request, 'projeto/gerenciamento_notebooks.html', context)



@login_required
@user_passes_test(is_admin)
def manutencao_reciclagem_view(request):
    notebooks_em_manutencao = Notebook.objects.filter(status='manutencao').order_by('-data_cadastro')
    historico_manutencoes = Manutencao.objects.all().order_by('-data_manutencao')
    notebooks_reciclados = Notebook.objects.filter(status='reciclado').order_by('-data_reciclagem')

    notebooks_validados_nao_reciclados = Notebook.objects.filter(
        validado=True # Deve ser validado
    ).exclude(status='reciclado').order_by('marca') # Exclui os que já estão reciclados e ordena

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'registrar_manutencao':
            notebook_id = request.POST.get('notebook_id')
            tipo_manutencao = request.POST.get('tipo_manutencao')
            data_manutencao = request.POST.get('data_manutencao')
            descricao_problema = request.POST.get('descricao_problema')
            solucao_aplicada = request.POST.get('solucao_aplicada')
            custo_estimado = request.POST.get('custo_estimado')
            pronto_para_uso = request.POST.get('pronto_para_uso') == 'on'

            notebook_manutencao = get_object_or_404(Notebook, id=notebook_id)

            try:
                Manutencao.objects.create(
                    notebook=notebook_manutencao,
                    administrador=request.user,
                    tipo_manutencao=tipo_manutencao,
                    data_manutencao=data_manutencao,
                    descricao_problema=descricao_problema,
                    solucao_aplicada=solucao_aplicada,
                    custo_estimado=custo_estimado if custo_estimado else None,
                    pronto_para_uso=pronto_para_uso
                )
                if pronto_para_uso:
                    notebook_manutencao.status = 'disponivel'
                    notebook_manutencao.save()
                messages.success(request, 'Manutenção registrada com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao registrar manutenção: {e}')

        elif action_type == 'marcar_reciclado':
            notebook_id = request.POST.get('notebook_id_reciclar')
            destino_reciclagem = request.POST.get('destino_reciclagem')

            notebook_reciclar = get_object_or_404(Notebook, id=notebook_id)

            if not destino_reciclagem:
                messages.error(request, 'Por favor, informe o destino ou reaproveitamento para a reciclagem.')
            else:
                notebook_reciclar.status = 'reciclado'
                notebook_reciclar.data_reciclagem = localdate()
                notebook_reciclar.destino_reciclagem = destino_reciclagem
                notebook_reciclar.em_uso = False
                notebook_reciclar.save()
                messages.success(request, 'Notebook marcado como reciclado com sucesso!')

        return redirect('manutencao_reciclagem')

    context = {
        'notebooks_em_manutencao': notebooks_em_manutencao,
        'historico_manutencoes': historico_manutencoes,
        'notebooks_reciclados': notebooks_reciclados,
        'tipo_manutencao_choices': Manutencao.TIPO_MANUTENCAO_CHOICES,
        'notebooks_validados': notebooks_validados_nao_reciclados, # Usar a nova lista aqui
    }
    return render(request, 'projeto/manutencao_reciclagem.html', context)

@login_required
@user_passes_test(is_admin)
def controle_devolucoes_view(request):
    today = localdate()
    devolucoes_pendentes = DevolucaoNotebook.objects.filter(status='pendente').order_by('-data_envio')
    return render(request, 'projeto/controle_devolucao.html', {
        'devolucoes_pendentes': devolucoes_pendentes,
        'today': today
    })


@login_required
@user_passes_test(is_admin)
def registrar_devolucao_view(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)

    try:
        devolucao = DevolucaoNotebook.objects.get(solicitacao=solicitacao, status='pendente')
    except DevolucaoNotebook.DoesNotExist:
        messages.warning(request, "Esta solicitação de devolução já foi processada ou não está mais pendente.")
        return redirect('controle_devolucao')
    try:
        emprestimo = solicitacao.emprestimo
    except EmprestimoNotebook.DoesNotExist:
        messages.error(request, "Erro: Empréstimo associado à solicitação não encontrado. Não é possível registrar a devolução.")
        return redirect('controle_devolucao')

    if request.method == 'POST':
        estado = request.POST.get('estado')

        # Valida o estado do notebook
        if estado == 'disponivel':
            emprestimo.notebook.status = 'disponivel'
        elif estado == 'manutencao':
            emprestimo.notebook.status = 'manutencao'
        else:
            messages.error(request, "Estado inválido. Por favor, selecione uma opção válida para o estado do notebook.")

            return render(request, 'projeto/registrar_devolucao.html', {'solicitacao': solicitacao, 'emprestimo': emprestimo, 'devolucao': devolucao})


        devolucao.status = 'aprovada'
        devolucao.save()
        emprestimo.status_emprestimo = 'devolvido'
        emprestimo.data_devolucao_real = timezone_now().date()
        emprestimo.save()
        solicitacao.status = 'Devolvido'
        solicitacao.save()
        emprestimo.notebook.save()

        messages.success(request, "Devolução registrada com sucesso!")
        return redirect('controle_devolucao')


    return render(request, 'projeto/registrar_devolucao.html', {
        'solicitacao': solicitacao,
        'emprestimo': emprestimo,
        'devolucao': devolucao # Passa o objeto devolução também para acesso a motivos, etc.
    })

@require_POST
@login_required
@user_passes_test(is_admin)
def aprovar_notebook_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    notebook.status = 'disponivel'
    notebook.validado = True
    notebook.save()
    messages.success(request, 'Notebook aprovado.')
    return redirect('gerenciamento_notebooks')

@require_POST
@login_required
@user_passes_test(is_admin)
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

@login_required
@user_passes_test(is_admin)
def atualizar_status_notebook(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in [choice[0] for choice in Notebook.STATUS_CHOICES]:
            notebook.status = novo_status
            notebook.save()
            messages.success(request, 'Status do notebook atualizado com sucesso.')
        else:
            messages.error(request, 'Status inválido.')
    return redirect('gerenciamento_notebooks')

@login_required
@user_passes_test(is_admin)
def editar_notebook_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if request.method == 'POST':
        form = NotebookForm(request.POST, request.FILES, instance=notebook, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notebook atualizado com sucesso.')
            return redirect('gerenciamento_notebooks')
    else:
        form = NotebookForm(instance=notebook, user=request.user)
    return render(request, 'projeto/editar_notebook.html', {'form': form, 'notebook': notebook})

@login_required
@user_passes_test(is_admin)
def excluir_notebook_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    if request.method == 'POST':
        notebook.delete()
        messages.success(request, 'Notebook excluído com sucesso.')
        return redirect('gerenciamento_notebooks')
    return render(request, 'projeto/excluir_notebook.html', {'notebook': notebook})


@login_required
@user_passes_test(is_admin)
def gerenciamento_emprestimos_view(request):
    emprestimos = EmprestimoNotebook.objects.all().order_by('-data_retirada')
    return render(request, 'projeto/gerenciamento_emprestimos.html', {
        'emprestimos': emprestimos
    })


@login_required
@user_passes_test(is_admin)
def avaliar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)

    if request.method == 'POST':
        status_avaliacao = request.POST.get('status')
        tempo_concedido_str = request.POST.get('tempo_concedido')

        solicitacao.status = status_avaliacao
        solicitacao.tempo_concedido = tempo_concedido_str if status_avaliacao == 'Aprovado' else None
        solicitacao.avaliado_por = request.user
        solicitacao.data_avaliacao = timezone_now()
        solicitacao.save()

        if status_avaliacao == 'Aprovado' and solicitacao.notebook:
            notebook = solicitacao.notebook
            try:
                notebook.status = 'emprestado'
                notebook.em_uso = True
                notebook.save()

                EmprestimoNotebook.objects.create(
                    solicitacao=solicitacao,
                    notebook=notebook,
                    aluno=solicitacao.aluno,
                    data_retirada=timezone_now().date(),
                    avaliado_por_admin=request.user,
                    status_emprestimo='emprestado'
                )
                messages.success(request, 'Solicitação aprovada e empréstimo registrado com sucesso!')
                return redirect('gerenciamento_emprestimos')

            except Exception as e:
                messages.error(request, f'Erro ao registrar empréstimo: {e}. Verifique os logs para detalhes.')
                return redirect('lista_solicitacoes')

        elif status_avaliacao == 'Recusado':
            messages.warning(request, 'Solicitação recusada.')
            return redirect('lista_solicitacoes')

        elif status_avaliacao == 'Lista de Espera':
            messages.info(request, 'Solicitação encaminhada para lista de espera.')
            return redirect('lista_solicitacoes')

        messages.info(request, "Avaliação processada com sucesso, mas o redirecionamento foi padrão.")
        return redirect('lista_solicitacoes')

    return render(request, 'projeto/avaliacao_solicitacao.html', {'solicitacao': solicitacao})





@login_required
@user_passes_test(is_admin)
def lista_de_espera_view(request):
    solicitacoes_lista_espera = SolicitacaoNotebook.objects.filter(
        status='Lista de Espera'
    ).order_by('data_solicitacao')


    notebooks_disponiveis = Notebook.objects.filter(
        Q(status='disponivel') | Q(status='oky'),
        validado=True,
        em_uso=False
    ).order_by('marca', 'modelo')

    context = {
        'solicitacoes': solicitacoes_lista_espera,
        'notebooks_disponiveis': notebooks_disponiveis,
    }
    return render(request, 'projeto/lista_de_espera.html', context)

@require_POST
@login_required
@user_passes_test(is_admin)
def remover_da_lista_espera_view(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)


    if solicitacao.status == 'Lista de Espera':
        solicitacao.status = 'Recusado'
        solicitacao.avaliado_por = request.user
        solicitacao.data_avaliacao = timezone_now()
        solicitacao.save()
        messages.success(request, f'Solicitação do aluno {solicitacao.nome} removida da lista de espera e marcada como Recusada.')
    else:
        messages.warning(request, f'A solicitação do aluno {solicitacao.nome} não está na lista de espera ou já foi processada.')

    return redirect('lista_de_espera')


# ... (suas importações existentes)

# --- Admin: Lista de Espera ---
@login_required
@user_passes_test(is_admin)
def lista_de_espera_view(request):
    solicitacoes_lista_espera = SolicitacaoNotebook.objects.filter(
        status='Lista de Espera'
    ).order_by('data_solicitacao')

    notebooks_disponiveis = Notebook.objects.filter(
        Q(status='disponivel') | Q(status='oky'),
        validado=True,
        em_uso=False
    ).order_by('marca', 'modelo')

    context = {
        'solicitacoes': solicitacoes_lista_espera,
        'notebooks_disponiveis': notebooks_disponiveis,
    }
    return render(request, 'projeto/lista_de_espera.html', context)


@require_POST
@login_required
@user_passes_test(is_admin)
def aprovar_da_lista_espera_view(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)
    notebook_id = request.POST.get('notebook_aprovacao_id')
    tempo_concedido_str = request.POST.get('tempo_concedido_aprovacao')


    if not notebook_id:
        messages.error(request, 'Você precisa selecionar um notebook para aprovar esta solicitação.')
        return redirect('lista_de_espera')



    notebook_selecionado = get_object_or_404(
        Notebook,
        Q(status='disponivel') | Q(status='oky'),
        id=notebook_id,
        validado=True,
        em_uso=False
    )



    if solicitacao.status != 'Lista de Espera':
        messages.warning(request, 'Esta solicitação não está mais na lista de espera ou já foi processada.')
        return redirect('lista_de_espera')

    try:
        solicitacao.status = 'Aprovado'
        solicitacao.tempo_concedido = tempo_concedido_str
        solicitacao.avaliado_por = request.user
        solicitacao.data_avaliacao = timezone_now()
        solicitacao.save()

        notebook_selecionado.status = 'emprestado'
        notebook_selecionado.em_uso = True
        notebook_selecionado.save()

        EmprestimoNotebook.objects.create(
            solicitacao=solicitacao,
            notebook=notebook_selecionado,
            aluno=solicitacao.aluno,
            data_retirada=timezone_now().date(),
            avaliado_por_admin=request.user,
            status_emprestimo='emprestado'
        )
        messages.success(request, f'Solicitação do aluno {solicitacao.nome} aprovada com sucesso e notebook {notebook_selecionado.modelo} emprestado!')
        return redirect('gerenciamento_emprestimos')

    except Exception as e:
        messages.error(request, f'Erro ao aprovar solicitação da lista de espera: {e}.')
        return redirect('lista_de_espera')


@require_POST
@login_required
@user_passes_test(is_admin)
def remover_da_lista_espera_view(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoNotebook, id=solicitacao_id)

    if solicitacao.status == 'Lista de Espera':
        solicitacao.status = 'Recusado'
        solicitacao.avaliado_por = request.user
        solicitacao.data_avaliacao = timezone_now()
        solicitacao.save()
        messages.success(request, f'Solicitação do aluno {solicitacao.nome} removida da lista de espera e marcada como Recusada.')
    else:
        messages.warning(request, f'A solicitação do aluno {solicitacao.nome} não está na lista de espera ou já foi processada.')

    return redirect('lista_de_espera')

@login_required
@user_passes_test(is_admin)
def avaliar_aluno_view(request):
    emprestimos_para_avaliar = EmprestimoNotebook.objects.filter(
        status_emprestimo='devolvido',
        avaliacao_aluno__isnull=True
    ).order_by('-data_devolucao_real')

    if request.method == 'POST':
        emprestimo_id = request.POST.get('emprestimo_id')
        desempenho_academico_obs = request.POST.get('desempenho_academico_obs')
        conduta_obs = request.POST.get('conduta_obs')
        recomendacao_futura = request.POST.get('recomendacao_futura')
        observacoes_gerais = request.POST.get('observacoes_gerais')


        foto_recebimento = request.FILES.get('foto_recebimento')

        emprestimo = get_object_or_404(EmprestimoNotebook, id=emprestimo_id)

        if not desempenho_academico_obs or not conduta_obs or not recomendacao_futura:
            messages.error(request, 'Por favor, preencha as observações de desempenho, conduta e a recomendação.')
            return redirect('avaliar_aluno')

        try:
            AvaliacaoAluno.objects.create(
                aluno=emprestimo.aluno,
                emprestimo=emprestimo,
                administrador=request.user,
                desempenho_academico_obs=desempenho_academico_obs,
                conduta_obs=conduta_obs,
                recomendacao_futura=recomendacao_futura,
                observacoes_gerais=observacoes_gerais,
                foto_recebimento=foto_recebimento
            )
            messages.success(request, f'Avaliação do aluno {emprestimo.aluno.get_full_name()} registrada com sucesso!')
            return redirect('avaliar_aluno')
        except Exception as e:
            messages.error(request, f'Erro ao registrar avaliação: {e}. Verifique se a avaliação já existe para este empréstimo.')
            return redirect('avaliar_aluno')

    return render(request, 'projeto/avaliar_aluno.html', {
        'emprestimos_para_avaliar': emprestimos_para_avaliar,
        'recomendacao_choices': AvaliacaoAluno.RECOMENDACAO_CHOICES,
    })



@login_required
@user_passes_test(is_admin)
def lista_solicitacoes_view(request):
    solicitacoes = SolicitacaoNotebook.objects.filter(status='Pendente')
    return render(request, 'projeto/lista_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
@user_passes_test(is_admin)
def relatorios_view(request):

    status_notebooks = Notebook.objects.values('status').annotate(count=Count('status')).order_by('status')

    status_counts = {}
    for item in status_notebooks:
        display_name = next((label for value, label in Notebook.STATUS_CHOICES if value == item['status']), item['status'])
        status_counts[display_name] = item['count']


    total_emprestimos = EmprestimoNotebook.objects.count()


    tempo_uso_dias = EmprestimoNotebook.objects.filter(
        status_emprestimo='devolvido',
        data_devolucao_real__isnull=False
    ).annotate(
        duration=ExpressionWrapper(F('data_devolucao_real') - F('data_retirada'),
                                  output_field=fields.DurationField())
    ).aggregate(average_duration=Avg('duration'))

    media_dias_uso = None
    if tempo_uso_dias['average_duration']:
        media_dias_uso = tempo_uso_dias['average_duration'].days

    alunos_atendidos_count = EmprestimoNotebook.objects.values('aluno').distinct().count()


    total_reciclados = Notebook.objects.filter(status='reciclado').count()

    context = {
        'status_counts': status_counts, # Passamos o dicionário com nomes amigáveis
        'total_emprestimos': total_emprestimos,
        'media_dias_uso': media_dias_uso,
        'alunos_atendidos_count': alunos_atendidos_count,
        'total_reciclados': total_reciclados,
    }
    return render(request, 'projeto/relatorios.html', context)