# Generated by Django 5.1.3 on 2025-06-16 18:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("EconoteApp", "0015_remove_aluno_ira_remove_aluno_status_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaonotebook",
            name="indicacao_professor",
            field=models.TextField(
                blank=True, null=True, verbose_name="Indicação do Professor"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaonotebook",
            name="indicado_por_professor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="indicacoes_feitas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Indicado Por",
            ),
        ),
    ]
