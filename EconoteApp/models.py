from django.db import models
from django.contrib.auth.models import User

# --------------------------------------------
# Perfil de Usuário (Aluno ou Professor)
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
    matricula = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.perfil.user.get_full_name()} - Professor"

