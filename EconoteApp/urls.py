from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Home
    path('home_aluno/', views.home_aluno, name='home_aluno'),
    path('home_professor/', views.home_professor, name='home_professor'),
    path('home_ADM/', views.home_ADM_view, name='home_ADM'),

    # Informações
    path('perfil/', views.perfil_view, name='perfil'),
    path('sobre/', views.sobre_view, name='sobre'),

    # Aluno
    path('solicitar-notebook/', views.solicitar_notebook_view, name='solicitar_notebook'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes_view, name='minhas_solicitacoes'),
    path('devolucoes-manutencao/', views.devolucoes_manutencao_view, name='devolucoes_manutencao'),
    path('solicitar-devolucao/', views.solicitar_devolucao, name='solicitar_devolucao'),



    # Professor
    path('avaliacao-solicitacao/', views.avaliacao_solicitacao_view, name='avaliacao_solicitacao'),
    path('indicar-aluno/', views.indicar_aluno_view, name='indicar_aluno'),

    # Admin
    path('cadastro-notebooks/', views.cadastro_notebooks_view, name='cadastro_notebooks'),
    path('lista-notebooks/', views.lista_notebooks_view, name='lista_notebooks'),
    path('lista-usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('gerenciar-notebooks/', views.gerenciamento_notebooks_view, name='gerenciamento_notebooks'),
    path('aprovar-notebook/<int:notebook_id>/', views.aprovar_notebook_view, name='aprovar_notebook'),
    path('recusar-notebook/<int:notebook_id>/', views.recusar_notebook_view, name='recusar_notebook'),
    path('solicitacoes/', views.lista_solicitacoes, name='lista_solicitacoes'),
    path('avaliar_solicitacao/<int:solicitacao_id>/', views.avaliar_solicitacao, name='avaliar_solicitacao'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
