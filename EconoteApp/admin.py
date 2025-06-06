from django.contrib import admin
from .models import PerfilUsuario, Aluno, Professor, Notebook, SolicitacaoNotebook

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'tipo_usuario')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'matricula', 'curso', 'ira', 'status')
    search_fields = ('matricula', 'perfil__user__first_name', 'perfil__user__last_name')


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'siape')
    search_fields = ('siape', 'perfil__user__first_name', 'perfil__user__last_name')


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'status', 'usuario', 'data_entrega')
    list_filter = ('status', 'marca')
    search_fields = ('marca', 'modelo', 'processador', 'usuario__username')


@admin.register(SolicitacaoNotebook)
class SolicitacaoNotebookAdmin(admin.ModelAdmin):
    list_display = ('nome', 'aluno', 'semestre', 'contexto', 'tempo_uso', 'status', 'data_solicitacao')
    list_filter = ('contexto', 'recomendacao', 'tempo_uso', 'status')
    search_fields = ('nome', 'aluno__username')
    readonly_fields = ('data_solicitacao',)
