from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home_aluno/', views.home_aluno, name='home_aluno'),
    path('home_professor/', views.home_professor, name='home_professor'),



    # Novas rotas adicionadas
    path('perfil/', views.perfil_view, name='perfil'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('solicitar-notebook/', views.solicitar_notebook_view, name='solicitar_notebook'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes_view, name='minhas_solicitacoes'),
    path('devolucoes-manutencao/', views.devolucoes_manutencao_view, name='devolucoes_manutencao'),
    path('cadastro-notebooks/', views.cadastro_notebooks_view, name='cadastro_notebooks'),
    path('avaliacao-solicitacao/', views.avaliacao_solicitacao_view, name='avaliacao_solicitacao'),
    path('indicar-aluno/', views.indicar_aluno_view, name='indicar_aluno'),


]


