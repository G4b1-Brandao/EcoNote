from django import forms
from .models import Notebook, SolicitacaoNotebook

class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        exclude = ['usuario']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pega o usuário passado na view
        super().__init__(*args, **kwargs)

        # Estilização e configuração dos campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'bloco-form-input'})
            field.label_suffix = ''

        if 'data_entrega' in self.fields:
            self.fields['data_entrega'].widget = forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'required': 'required',
                    'id': 'data_entrega'
                }
            )
            self.fields['data_entrega'].label = 'Quando este notebook será entregue para o responsável?'

        # Se o usuário não for admin, oculta os campos 'status' e 'validado'
        if not (user and user.is_superuser):
            self.fields.pop('status', None)
            self.fields.pop('validado', None)



class SolicitacaoNotebookForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoNotebook
        fields = [
            'nome',
            'semestre',
            'historico',
            'contexto',
            'recomendacao',
            'tempo_uso',
            'justificativa'
        ]
        labels = {
            'nome': 'Nome do Aluno',
            'semestre': 'Semestre Atual',
            'contexto': 'Contexto Socioeconômico',
            'recomendacao': 'Recomendação de Professor',
            'tempo_uso': 'Tempo de Uso do Notebook',
            'justificativa': 'Justificativa',
        }
        widgets = {
            'justificativa': forms.Textarea(attrs={'rows': 10}),
            'contexto': forms.Select(attrs={'required': 'required'}),
            'recomendacao': forms.Select(attrs={'required': 'required'}),
            'tempo_uso': forms.Select(attrs={'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'bloco-form-input',
                'required': 'required'
            })
            field.label_suffix = ''

        # Campo de upload com mensagem de ajuda
        self.fields['historico'].widget.attrs.update({
            'accept': 'application/pdf'
        })
        self.fields['historico'].label = 'Histórico Escolar (PDF)'
        self.fields['historico'].help_text = 'Envie apenas arquivos no formato PDF.'
