from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core import validators
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .accesos import proyectos_de, tareas_de

class RegistroForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].max_length = 20
        self.fields['username'].validators = [
            validators.RegexValidator(
                r'^[a-zA-Z0-9]+$',
                'Solo se permiten letras y números.'
            )
        ]
        self.fields['username'].help_text = 'Máximo 20 caracteres. Solo letras y números.'
        self.fields['password1'].help_text = '''
            Tu contraseña no puede ser similar a tu información personal.<br>
            Debe tener al menos 8 caracteres.<br>
            No puede ser una contraseña común.<br>
            No puede ser completamente numérica.
        '''
        self.fields['password2'].help_text = 'Ingresá la misma contraseña para verificar.'

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'auth/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# Vista lista de proyectos visibles para el usuario
@login_required
def lista_proyectos(request):
    proyectos = proyectos_de(request.user).annotate(num_tareas=Count('tareas'))
    return render(request, 'proyectos/lista.html', {'proyectos': proyectos})


# Vista lista de tareas accesibles para el usuario
@login_required
def lista_tareas(request):
    tareas = tareas_de(request.user).select_related('proyecto', 'responsable')
    return render(request, 'tareas/lista.html', {'tareas': tareas})