from django import forms
from django.contrib.auth.models import User
from .models import Notebook, SolicitacaoNotebook, Aluno, Professor, PerfilUsuario


class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        exclude = ['usuario']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'validado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'em_uso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

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

        if not (user and user.is_superuser):
            self.fields.pop('status', None)
            self.fields.pop('validado', None)
            self.fields.pop('em_uso', None)



class SolicitacaoNotebookForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoNotebook
        fields = [
            'nome',
            'semestre',
            'historico',
            'contexto',
            'tempo_uso',
            'justificativa'
        ]
        labels = {
            'nome': 'Nome do Aluno',
            'semestre': 'Semestre Atual',
            'contexto': 'Contexto Socioeconômico',
            'tempo_uso': 'Tempo de Uso do Notebook',
            'justificativa': 'Justificativa',
        }
        widgets = {
            'justificativa': forms.Textarea(attrs={'rows': 10}),
            'contexto': forms.Select(attrs={'required': 'required'}),
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


        self.fields['historico'].widget.attrs.update({
            'accept': 'application/pdf'
        })
        self.fields['historico'].label = 'Histórico Escolar (PDF)'
        self.fields['historico'].help_text = 'Envie apenas arquivos no formato PDF.'



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Nome"
        self.fields['first_name'].required = True


class AlunoUpdateForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['matricula', 'curso']
        widgets = {
            'matricula': forms.TextInput(attrs={'placeholder': 'Sua matrícula'}),
            'curso': forms.TextInput(attrs={'placeholder': 'Seu curso'}),
        }


class ProfessorUpdateForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['siape']
        widgets = {
            'siape': forms.TextInput(attrs={'placeholder': 'Seu SIAPE'}),
        }
