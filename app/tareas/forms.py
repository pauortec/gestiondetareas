from django import forms
from django.forms import inlineformset_factory

from .models import Tarea, ParteHoras


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'proyecto', 'estado', 'categoria',
                  'responsable', 'fecha_inicio', 'fecha_limite']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }


# Inline formset para que la pestana Parte de horas edite varias lineas a la vez
PartesHorasFormSet = inlineformset_factory(
    Tarea, ParteHoras,
    fields=['fecha', 'descripcion', 'horas', 'categoria'],
    widgets={'fecha': forms.DateInput(attrs={'type': 'date'})},
    extra=1, can_delete=True,
)