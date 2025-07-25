# Generated by Django 5.1.3 on 2025-06-20 23:32

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("EconoteApp", "0017_avaliacaoaluno"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notebook",
            name="data_reciclagem",
            field=models.DateField(
                blank=True,
                help_text="Data em que o notebook foi marcado como reciclado.",
                null=True,
                verbose_name="Data da Reciclagem",
            ),
        ),
        migrations.AddField(
            model_name="notebook",
            name="destino_reciclagem",
            field=models.TextField(
                blank=True,
                help_text="Detalhes sobre para onde o notebook foi reciclado ou como seus componentes foram reaproveitados.",
                null=True,
                verbose_name="Destino/Reaproveitamento da Reciclagem",
            ),
        ),
        migrations.CreateModel(
            name="Manutencao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tipo_manutencao",
                    models.CharField(
                        choices=[
                            ("reparo", "Reparo"),
                            ("limpeza", "Limpeza"),
                            ("atualizacao", "Atualização de Software/Hardware"),
                            ("diagnostico", "Diagnóstico"),
                            ("outros", "Outros"),
                        ],
                        max_length=20,
                        verbose_name="Tipo de Manutenção",
                    ),
                ),
                (
                    "data_manutencao",
                    models.DateField(
                        default=django.utils.timezone.now,
                        verbose_name="Data da Manutenção",
                    ),
                ),
                (
                    "descricao_problema",
                    models.TextField(
                        blank=True,
                        help_text="Descreva o problema encontrado (se houver).",
                        null=True,
                        verbose_name="Descrição do Problema",
                    ),
                ),
                (
                    "solucao_aplicada",
                    models.TextField(
                        blank=True,
                        help_text="Descreva a solução ou serviço realizado.",
                        null=True,
                        verbose_name="Solução Aplicada",
                    ),
                ),
                (
                    "custo_estimado",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Custo estimado da manutenção, se aplicável.",
                        max_digits=8,
                        null=True,
                        verbose_name="Custo Estimado (R$)",
                    ),
                ),
                (
                    "pronto_para_uso",
                    models.BooleanField(
                        default=False,
                        help_text="Indica se o notebook está pronto para ser disponibilizado novamente.",
                        verbose_name="Pronto para Uso",
                    ),
                ),
                (
                    "administrador",
                    models.ForeignKey(
                        blank=True,
                        help_text="Administrador que registrou a manutenção.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notebook",
                    models.ForeignKey(
                        help_text="Notebook que recebeu a manutenção.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="manutencoes",
                        to="EconoteApp.notebook",
                    ),
                ),
            ],
            options={
                "verbose_name": "Manutenção",
                "verbose_name_plural": "Manutenções",
                "ordering": ["-data_manutencao"],
            },
        ),
    ]
