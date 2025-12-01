from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    # --- campos de verificação de e-mail ---
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    # ---------------------------------------


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.tipo_usuario})"



class Aluno(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.perfil.user.get_full_name()} - {self.matricula}"



class Professor(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    siape = models.CharField(max_length=20, unique=True) # Nome do campo está consistente (minúsculo)

    def __str__(self):
        return f"{self.perfil.user.get_full_name()} - Professor"



class Notebook(models.Model):
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('emprestado', 'Emprestado'),
        ('manutencao', 'Em manutenção'),
        ('reciclado', 'Reciclado'),
        ('pendente', 'Pendente'),
        ('recebido', 'Recebido'),
    ]

    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    processador = models.CharField(max_length=100, verbose_name="Processador")
    memoria_ram = models.CharField(max_length=50, verbose_name="Memória RAM")
    armazenamento = models.CharField(max_length=50, verbose_name="Armazenamento")
    imagem = models.ImageField(upload_to='notebooks/', null=True, blank=True)
    informacoes_extras = models.TextField(blank=True, null=True, verbose_name="Informações extras")

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário Doador/Cadastrador")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_entrega = models.DateField(verbose_name="Data de entrega para o responsável", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        help_text="Atualize o status conforme o ciclo de uso do notebook."
    )

    validado = models.BooleanField(default=False, help_text="Indica se o notebook foi validado pelo administrador.")
    em_uso = models.BooleanField(default=False, help_text="Indica se o notebook está atualmente em uso.")


    data_reciclagem = models.DateField(
        null=True, blank=True,
        verbose_name="Data da Reciclagem",
        help_text="Data em que o notebook foi marcado como reciclado."
    )
    destino_reciclagem = models.TextField(
        blank=True, null=True,
        verbose_name="Destino/Reaproveitamento da Reciclagem",
        help_text="Detalhes sobre para onde o notebook foi reciclado ou como seus componentes foram reaproveitados."
    )

    def __str__(self):
        return f"{self.marca} {self.modelo}"

    def descricao_resumida(self):
        return f"{self.marca} {self.modelo}, {self.processador}, {self.memoria_ram}, {self.armazenamento}"



class Manutencao(models.Model):
    TIPO_MANUTENCAO_CHOICES = [
        ('reparo', 'Reparo'),
        ('limpeza', 'Limpeza'),
        ('atualizacao', 'Atualização de Software/Hardware'),
        ('diagnostico', 'Diagnóstico'),
        ('outros', 'Outros'),
    ]

    notebook = models.ForeignKey(
        'Notebook',
        on_delete=models.CASCADE,
        related_name='manutencoes',
        help_text="Notebook que recebeu a manutenção."
    )
    administrador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Administrador que registrou a manutenção."
    )
    tipo_manutencao = models.CharField(
        max_length=20,
        choices=TIPO_MANUTENCAO_CHOICES,
        verbose_name="Tipo de Manutenção"
    )
    data_manutencao = models.DateField(
        default=timezone.now,
        verbose_name="Data da Manutenção"
    )
    descricao_problema = models.TextField(
        blank=True, null=True,
        verbose_name="Descrição do Problema",
        help_text="Descreva o problema encontrado (se houver)."
    )
    solucao_aplicada = models.TextField(
        blank=True, null=True,
        verbose_name="Solução Aplicada",
        help_text="Descreva a solução ou serviço realizado."
    )
    custo_estimado = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        verbose_name="Custo Estimado (R$)",
        help_text="Custo estimado da manutenção, se aplicável."
    )
    pronto_para_uso = models.BooleanField(
        default=False,
        verbose_name="Pronto para Uso",
        help_text="Indica se o notebook está pronto para ser disponibilizado novamente."
    )

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ['-data_manutencao'] # Ordena por data mais recente

    def __str__(self):
        return f"Manutenção de {self.notebook.modelo} - Tipo: {self.get_tipo_manutencao_display()}"


class SolicitacaoNotebook(models.Model):
    CONTEXTOS = [
        ('Baixo', 'Baixo'),
        ('Médio', 'Médio'),
        ('Alto', 'Alto'),
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
    tempo_uso = models.CharField(max_length=20, choices=TEMPO_USO)
    justificativa = models.TextField()


    indicacao_professor = models.TextField(
        blank=True,
        null=True,
        verbose_name="Indicação do Professor"
    )
    indicado_por_professor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='indicacoes_feitas',
        verbose_name="Indicado Por"
    )

    data_solicitacao = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default='Pendente',
        choices=[
            ('Pendente', 'Pendente'),
            ('Aprovado', 'Aprovado'),
            ('Recusado', 'Recusado'),
            ('Lista de Espera', 'Lista de Espera'),
            ('devolucao_pendente', 'Devolução Pendente'),
            ('Devolvido', 'Devolvido'), # Confirmado: 'Devolvido' está presente
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
    solicitacao = models.ForeignKey(
        'SolicitacaoNotebook',
        on_delete=models.CASCADE,
        related_name='devolucao' # Confirmado: related_name 'devolucao' está presente
    )
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



class EmprestimoNotebook(models.Model):
    STATUS_EMPRESTIMO_CHOICES = [
        ('emprestado', 'Emprestado'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]

    solicitacao = models.OneToOneField(
        'SolicitacaoNotebook',
        on_delete=models.CASCADE,
        related_name='emprestimo',
        help_text="Solicitação que originou este empréstimo."
    )
    notebook = models.ForeignKey(
        'Notebook',
        on_delete=models.CASCADE,
        help_text="Notebook emprestado."
    )
    aluno = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Aluno que recebeu o empréstimo."
    )
    data_retirada = models.DateField(
        default=timezone.now,
        help_text="Data em que o notebook foi retirado."
    )
    data_prevista_devolucao = models.DateField(
        null=True, blank=True,
        help_text="Data prevista para a devolução do notebook."
    )
    data_devolucao_real = models.DateField(
        null=True, blank=True,
        help_text="Data real da devolução do notebook."
    )
    status_emprestimo = models.CharField(
        max_length=20,
        choices=STATUS_EMPRESTIMO_CHOICES,
        default='emprestado',
        help_text="Status atual do empréstimo."
    )
    avaliado_por_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='emprestimos_administrados',
        help_text="Administrador que registrou/gerenciou o empréstimo."
    )

    def __str__(self):
        return f"Empréstimo: {self.notebook.modelo} para {self.aluno.get_full_name()} - Status: {self.status_emprestimo}"

    def save(self, *args, **kwargs):
        if self.solicitacao and self.solicitacao.tempo_concedido and not self.data_prevista_devolucao:
            from datetime import timedelta
            if self.solicitacao.tempo_concedido == '1_mês':
                self.data_prevista_devolucao = self.data_retirada + timedelta(days=30)
            elif self.solicitacao.tempo_concedido == '2_meses':
                self.data_prevista_devolucao = self.data_retirada + timedelta(days=60)
            elif self.solicitacao.tempo_concedido == '3_meses':
                self.data_prevista_devolucao = self.data_retirada + timedelta(days=90)
            elif self.solicitacao.tempo_concedido == 'mais_3_meses':
                self.data_prevista_devolucao = self.data_retirada + timedelta(days=120) # Exemplo: 4 meses
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Empréstimo de Notebook"
        verbose_name_plural = "Empréstimos de Notebooks"



class AvaliacaoAluno(models.Model):
    RECOMENDACAO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('condicional', 'Condicional'),
    ]

    aluno = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='avaliacoes_recebidas',
        help_text="Aluno que está sendo avaliado."
    )

    emprestimo = models.OneToOneField(
        'EmprestimoNotebook',
        on_delete=models.CASCADE,
        related_name='avaliacao_aluno',
        help_text="Empréstimo ao qual esta avaliação se refere."
    )
    administrador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='avaliacoes_realizadas',
        help_text="Administrador que registrou a avaliação."
    )
    data_avaliacao = models.DateTimeField(
        default=timezone.now,
        help_text="Data em que a avaliação foi registrada."
    )
    desempenho_academico_obs = models.TextField(
        blank=True, null=True,
        verbose_name="Observações sobre Desempenho Acadêmico",
        help_text="Descreva o impacto do notebook no desempenho acadêmico do aluno."
    )
    conduta_obs = models.TextField(
        blank=True, null=True,
        verbose_name="Observações sobre Conduta",
        help_text="Descreva a conduta do aluno durante o período de empréstimo (cuidado, comunicação, etc.)."
    )
    recomendacao_futura = models.CharField(
        max_length=20,
        choices=RECOMENDACAO_CHOICES,
        default='sim',
        verbose_name="Recomendação para Futuros Empréstimos",
        help_text="Recomendaria o aluno para futuros empréstimos?"
    )

    observacoes_gerais = models.TextField(
        blank=True, null=True,
        verbose_name="Observações Gerais",
        help_text="Outras observações relevantes sobre o aluno."
    )

    foto_recebimento = models.ImageField(
        upload_to='avaliacoes_notebooks/',
        null=True, blank=True,
        verbose_name="Foto do Notebook no Recebimento",
        help_text="Foto do estado do notebook no momento da devolução."
    )

    class Meta:
        verbose_name = "Avaliação de Aluno"
        verbose_name_plural = "Avaliações de Alunos"
        unique_together = ('emprestimo',)

    def __str__(self):
        return f"Avaliação de {self.aluno.get_full_name()} para Empréstimo ID {self.emprestimo.id}"