from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Perfil do Usuário
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.perfil_editar_view, name='perfil_editar'),

    path('home_aluno/', views.home_aluno, name='home_aluno'),
    path('home_professor/', views.home_professor, name='home_professor'),
    path('home_ADM/', views.home_ADM_view, name='home_ADM'),


    # Aluno
    path('solicitar-notebook/', views.solicitar_notebook_view, name='solicitar_notebook'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes_view, name='minhas_solicitacoes'),
    path('solicitar-devolucao/', views.solicitar_devolucao, name='solicitar_devolucao'),

    # Professor
    path('avaliacao-solicitacao/', views.avaliacao_solicitacao_view, name='avaliacao_solicitacao'),
    path('indicar-aluno/', views.indicar_aluno_view, name='indicar_aluno'),

    # Admin
    path('cadastro-notebooks/', views.cadastro_notebooks_view, name='cadastro_notebooks'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('gerenciar-notebooks/', views.gerenciamento_notebooks_view, name='gerenciamento_notebooks'),
    path('manutencao-reciclagem/', views.manutencao_reciclagem_view, name='manutencao_reciclagem'),
    path('solicitacoes/', views.lista_solicitacoes_view, name='lista_solicitacoes'),
    path('avaliar-solicitacao/<int:solicitacao_id>/', views.avaliar_solicitacao, name='avaliar_solicitacao'),
    path('gerenciar-emprestimos/', views.gerenciamento_emprestimos_view, name='gerenciamento_emprestimos'),
    path('avaliar-alunos/', views.avaliar_aluno_view, name='avaliar_aluno'),
    path('lista-de-espera/', views.lista_de_espera_view, name='lista_de_espera'),
    path('controle-devolucao/', views.controle_devolucoes_view, name='controle_devolucao'),
    path('registrar-devolucao/<int:solicitacao_id>/', views.registrar_devolucao_view, name='registrar_devolucao'),

    # URLs de gerenciamento de notebooks (aprovar, recusar, editar, excluir, atualizar status)
    path('aprovar-notebook/<int:notebook_id>/', views.aprovar_notebook_view, name='aprovar_notebook'), # Já está aqui
    path('recusar-notebook/<int:notebook_id>/', views.recusar_notebook_view, name='recusar_notebook'), # Já está aqui
    path('notebook/<int:notebook_id>/editar/', views.editar_notebook_view, name='editar_notebook'),
    path('notebook/<int:notebook_id>/excluir/', views.excluir_notebook_view, name='excluir_notebook'),
    path('notebook/<int:notebook_id>/atualizar-status/', views.atualizar_status_notebook, name='atualizar_status_notebook'),

    # Ações da Lista de Espera (uma entrada de remover)
    path('lista-de-espera/remover/<int:solicitacao_id>/', views.remover_da_lista_espera_view, name='remover_da_lista_espera'),
    path('lista-de-espera/aprovar/<int:solicitacao_id>/', views.aprovar_da_lista_espera_view, name='aprovar_da_lista_espera'),

    #Rotas de definição de senhas
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='projeto/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='projeto/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='projeto/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='projeto/password_reset_complete.html'),
         name='password_reset_complete'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)