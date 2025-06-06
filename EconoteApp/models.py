from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# --------------------------------------------
# Perfil genérico do usuário
# --------------------------------------------
class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.tipo_usuario})"


# --------------------------------------------
# Modelo Aluno
# --------------------------------------------
class Aluno(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.CharField(max_length=100)
    ira = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.perfil.user.get_full_name()} - {self.matricula}"


# --------------------------------------------
# Modelo Professor
# --------------------------------------------
class Professor(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    siape = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.perfil.user.get_full_name()} - Professor"


# --------------------------------------------
# Modelo Notebook
# --------------------------------------------
class Notebook(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('recebido', 'Recebido'),
        ('oky', 'Disponível'),
    ]

    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    processador = models.CharField(max_length=100, verbose_name="Processador")
    memoria_ram = models.CharField(max_length=50, verbose_name="Memória RAM")
    armazenamento = models.CharField(max_length=50, verbose_name="Armazenamento")
    imagem = models.ImageField(upload_to='notebooks/', null=True, blank=True)
    informacoes_extras = models.TextField(blank=True, null=True, verbose_name="Informações extras")

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_entrega = models.DateField(verbose_name="Data de entrega para o responsável", null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        help_text="Marque como 'oky' para disponibilizar o notebook para solicitação."
    )

    validado = models.BooleanField(default=False, help_text="Indica se o notebook foi validado pelo administrador.")
    em_uso = models.BooleanField(default=False, help_text="Indica se o notebook está atualmente em uso.")

    def __str__(self):
        return f"{self.marca} {self.modelo}"

    def descricao_resumida(self):
        return f"{self.marca} {self.modelo}, {self.processador}, {self.memoria_ram}, {self.armazenamento}"


# --------------------------------------------
# Modelo Solicitação de Notebook
# --------------------------------------------


class SolicitacaoNotebook(models.Model):
    CONTEXTOS = [
        ('Baixo', 'Baixo'),
        ('Médio', 'Médio'),
        ('Alto', 'Alto'),
    ]

    RECOMENDACOES = [
        ('Sim', 'Sim'),
        ('Não', 'Não'),
    ]

    TEMPO_USO = [
        ('1_mês', '1 mês'),
        ('2_meses', '2 meses'),
        ('3_meses', '3 meses'),
        ('mais_3_meses', 'Mais de 3 meses'),
    ]

    aluno = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    semestre = models.CharField(max_length=20)

    historico = models.FileField(upload_to='historicos/')
    contexto = models.CharField(max_length=10, choices=CONTEXTOS)
    recomendacao = models.CharField(max_length=5, choices=RECOMENDACOES)
    tempo_uso = models.CharField(max_length=20, choices=TEMPO_USO)
    justificativa = models.TextField()

    data_solicitacao = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default='Pendente',
        choices=[
            ('Pendente', 'Pendente'),
            ('Aprovado', 'Aprovado'),
            ('Recusado', 'Recusado'),
            ('Lista de Espera', 'Lista de Espera'),
        ]
    )

    tempo_concedido = models.CharField(
        max_length=20,
        choices=TEMPO_USO,
        blank=True,
        null=True
    )

    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True, blank=True)

    avaliado_por = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='avaliacoes'
    )
    data_avaliacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.status}"

class DevolucaoNotebook(models.Model):
    MOTIVOS = [
        ('nao_preciso', 'Não preciso mais do notebook'),
        ('defeito', 'Notebook com defeito'),
        ('uso_concluido', 'Uso concluído antes do prazo'),
    ]

    aluno = models.ForeignKey(User, on_delete=models.CASCADE)
    solicitacao = models.ForeignKey('SolicitacaoNotebook', on_delete=models.CASCADE)
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    data_sugerida = models.DateField()
    detalhes = models.TextField(blank=True, null=True)
    compromisso_aceito = models.BooleanField(default=False)
    data_envio = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[('pendente', 'Pendente'), ('aprovada', 'Aprovada'), ('recusada', 'Recusada')],
        default='pendente'
    )

    def __str__(self):
        return f'Devolução de {self.aluno.username} - {self.solicitacao.notebook.modelo}'