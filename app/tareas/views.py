import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core import validators
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User

from .accesos import proyectos_de, tareas_de, puede_ver_tarea, puede_ver_proyecto
from .models import Tarea, Proyecto, ESTADOS

# Codigos de estado validos
ESTADOS_VALIDOS = {codigo for codigo, _ in ESTADOS}

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


# Solo el propietario puede compartir su proyecto con otros usuarios
@login_required
def compartir_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if proyecto.propietario != request.user:
        return redirect('lista_proyectos')

    if request.method == 'POST':
        ids = request.POST.getlist('colaboradores')
        elegidos = User.objects.filter(pk__in=ids).exclude(pk=request.user.pk)
        proyecto.colaboradores.set(elegidos)
        return redirect('lista_proyectos')

    candidatos = User.objects.exclude(pk=request.user.pk).order_by('username')
    actuales = set(proyecto.colaboradores.values_list('pk', flat=True))
    return render(request, 'proyectos/compartir.html', {
        'proyecto': proyecto,
        'candidatos': candidatos,
        'actuales': actuales,
    })


# Vista lista de tareas accesibles para el usuario
@login_required
def lista_tareas(request):
    tareas = tareas_de(request.user).select_related('proyecto', 'responsable')
    return render(request, 'tareas/lista.html', {'tareas': tareas})


# Mueve una tarjeta a otro estado y guarda el orden de la columna destino.
# Recibe JSON: {tarea_id, estado, orden: [ids en el orden final de la columna]}
@login_required
@require_POST
def mover_tarea(request):
    datos = json.loads(request.body)
    tarea = get_object_or_404(Tarea, pk=datos.get('tarea_id'))
    if not puede_ver_tarea(request.user, tarea):
        return JsonResponse({'ok': False, 'error': 'sin permiso'}, status=403)

    estado = datos.get('estado')
    if estado not in ESTADOS_VALIDOS:
        return JsonResponse({'ok': False, 'error': 'estado invalido'}, status=400)

    tarea.estado = estado
    tarea.save(update_fields=['estado'])

    # Reescribe la posicion de cada tarjeta segun el orden recibido
    for posicion, tid in enumerate(datos.get('orden', [])):
        Tarea.objects.filter(pk=tid).update(posicion=posicion)

    return JsonResponse({'ok': True})