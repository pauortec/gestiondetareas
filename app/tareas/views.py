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
from .models import Tarea, Proyecto, ESTADOS, CATEGORIAS, ETAPAS_PROYECTO
from .forms import TareaForm, PartesHorasFormSet

ESTADOS_VALIDOS = {codigo for codigo, _ in ESTADOS}

class RegistroForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].max_length = 20
        self.fields['username'].label = 'Usuario'
        self.fields['username'].validators = [
            validators.RegexValidator(
                r'^[a-zA-Z0-9]+$',
                'Solo se permiten letras y números.'
            )
        ]
        self.fields['username'].help_text = 'Máximo 20 caracteres. Solo letras y números.'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = 'Mínimo 4 caracteres.'
        self.fields['password2'].label = 'Confirmar contraseña'
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
    # Traducimos las labels nativas a espanol
    form.fields['username'].label = 'Usuario'
    form.fields['password'].label = 'Contraseña'
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    proyectos = proyectos_de(request.user).annotate(num_tareas=Count('tareas'))
    return render(request, 'dashboard.html', {'proyectos': proyectos})

def _proyectos_filtrados(request):
    qs = proyectos_de(request.user).annotate(num_tareas=Count('tareas'))
    filtros = {
        'q': request.GET.get('q', '').strip(),
        'etapa': request.GET.get('etapa', ''),
    }
    if filtros['q']:
        qs = qs.filter(nombre__icontains=filtros['q'])
    if filtros['etapa']:
        qs = qs.filter(etapa=filtros['etapa'])
    return qs, filtros


@login_required
def lista_proyectos(request):
    proyectos, filtros = _proyectos_filtrados(request)
    return render(request, 'proyectos/lista.html', {
        'proyectos': proyectos,
        'filtros': filtros,
        'etapas': ETAPAS_PROYECTO,
    })


@login_required
def kanban_proyectos(request):
    qs = proyectos_de(request.user).annotate(num_tareas=Count('tareas'))
    filtros = {'q': request.GET.get('q', '').strip()}
    if filtros['q']:
        qs = qs.filter(nombre__icontains=filtros['q'])
    proyectos_lista = list(qs)
    indice = {codigo: [] for codigo, _ in ETAPAS_PROYECTO}
    for p in proyectos_lista:
        if p.etapa in indice:
            indice[p.etapa].append(p)
    columnas = [{'codigo': c, 'label': l, 'proyectos': indice[c]} for c, l in ETAPAS_PROYECTO]
    return render(request, 'proyectos/kanban.html', {
        'columnas': columnas,
        'filtros': filtros,
    })

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

@login_required
def lista_tareas(request):
    tareas = tareas_de(request.user).select_related('proyecto', 'responsable')
    return render(request, 'tareas/lista.html', {'tareas': tareas})

@login_required
def kanban_tareas(request):
    qs = tareas_de(request.user).select_related('proyecto', 'responsable').order_by('posicion')
    filtros = {
        'q': request.GET.get('q', '').strip(),
        'proyecto_q': request.GET.get('proyecto_q', '').strip(),
        'responsable_q': request.GET.get('responsable_q', '').strip(),
        'categoria': request.GET.get('categoria', ''),
        'estado': request.GET.get('estado', ''),
        'responsable': request.GET.get('responsable', ''),
        'fecha_desde': request.GET.get('fecha_desde', ''),
        'fecha_hasta': request.GET.get('fecha_hasta', ''),
        'proyecto': request.GET.get('proyecto', ''),
    }
    if filtros['q']:
        qs = qs.filter(titulo__icontains=filtros['q'])
    if filtros['proyecto_q']:
        qs = qs.filter(proyecto__nombre__icontains=filtros['proyecto_q'])
    if filtros['responsable_q']:
        qs = qs.filter(responsable__username__icontains=filtros['responsable_q'])
    if filtros['categoria']:
        qs = qs.filter(categoria=filtros['categoria'])
    if filtros['estado']:
        qs = qs.filter(estado=filtros['estado'])
    if filtros['responsable'] == 'sin_asignar':
        qs = qs.filter(responsable__isnull=True)
    elif filtros['responsable']:
        qs = qs.filter(responsable_id=filtros['responsable'])
    if filtros['fecha_desde']:
        qs = qs.filter(fecha_limite__gte=filtros['fecha_desde'])
    if filtros['fecha_hasta']:
        qs = qs.filter(fecha_limite__lte=filtros['fecha_hasta'])
    if filtros['proyecto']:
        qs = qs.filter(proyecto_id=filtros['proyecto'])
    columnas = [{'codigo': codigo, 'label': label, 'tareas': []} for codigo, label in ESTADOS]
    indice = {c['codigo']: c for c in columnas}
    for t in qs:
        if t.estado in indice:
            indice[t.estado]['tareas'].append(t)
    try:
        proyecto_actual_id = int(filtros['proyecto']) if filtros['proyecto'] else None
    except ValueError:
        proyecto_actual_id = None
    return render(request, 'tareas/kanban.html', {
        'columnas': columnas,
        'usuarios': User.objects.order_by('username'),
        'categorias': CATEGORIAS,
        'estados': ESTADOS,
        'filtros': filtros,
        'proyectos_disponibles': proyectos_de(request.user),
        'proyecto_actual_id': proyecto_actual_id,
    })

@login_required
def detalle_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not puede_ver_tarea(request.user, tarea):
        return redirect('lista_tareas')

    # Cambio rápido de estado desde la barra superior
    set_estado = request.GET.get('set_estado')
    if set_estado in ESTADOS_VALIDOS:
        tarea.estado = set_estado
        tarea.save(update_fields=['estado'])
        messages.success(request, 'Estado actualizado.')
        return redirect('detalle_tarea', pk=tarea.pk)

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        formset = PartesHorasFormSet(request.POST, instance=tarea)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Tarea guardada correctamente.')
            return redirect('detalle_tarea', pk=tarea.pk)
    else:
        form = TareaForm(instance=tarea)
        formset = PartesHorasFormSet(instance=tarea)

    return render(request, 'tareas/detalle.html', {
        'tarea': tarea,
        'form': form,
        'formset': formset,
        'historial': tarea.historial.all()[:50],
    })

@login_required
def asignar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not puede_ver_tarea(request.user, tarea):
        return redirect('lista_tareas')
    if request.method == 'POST':
        uid = request.POST.get('responsable') or None
        tarea.responsable = User.objects.filter(pk=uid).first() if uid else None
        tarea.save(update_fields=['responsable'])
        return redirect('lista_tareas')
    candidatos = User.objects.order_by('username')
    return render(request, 'tareas/asignar.html', {'tarea': tarea, 'candidatos': candidatos})

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
    for posicion, tid in enumerate(datos.get('orden', [])):
        Tarea.objects.filter(pk=tid).update(posicion=posicion)
    return JsonResponse({'ok': True})

@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        etapa = request.POST.get('etapa', 'implementacion')
        if nombre:
            Proyecto.objects.create(nombre=nombre, etapa=etapa, propietario=request.user)
            messages.success(request, 'Proyecto creado correctamente.')
            return redirect('dashboard')
    return render(request, 'proyectos/crear.html', {'etapas': ETAPAS_PROYECTO})

@login_required
def crear_tarea(request):
    # Proyecto fijo via URL (?proyecto=ID) o hidden en POST: queda preseleccionado
    proyecto_id = request.GET.get('proyecto') or request.POST.get('proyecto_fijo_id')
    proyecto_fijo = None
    if proyecto_id:
        proyecto_fijo = proyectos_de(request.user).filter(pk=proyecto_id).first()

    if request.method == 'POST':
        datos = request.POST.copy()
        if proyecto_fijo:
            datos['proyecto'] = proyecto_fijo.pk
        form = TareaForm(datos)
        if form.is_valid():
            tarea = form.save()
            messages.success(request, f'Tarea "{tarea.titulo}" creada correctamente.')
            return redirect('kanban_tareas')
    else:
        initial = {'estado': request.GET.get('estado', 'relevamiento')}
        if proyecto_fijo:
            initial['proyecto'] = proyecto_fijo.pk
        form = TareaForm(initial=initial)

    return render(request, 'tareas/crear.html', {
        'form': form,
        'proyectos': proyectos_de(request.user),
        'usuarios': User.objects.order_by('username'),
        'categorias': CATEGORIAS,
        'proyecto_fijo': proyecto_fijo,
    })

@login_required
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not puede_ver_tarea(request.user, tarea):
        return redirect('lista_tareas')
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada.')
        return redirect('kanban_tareas')
    return render(request, 'tareas/eliminar.html', {'tarea': tarea})

@login_required
def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, propietario=request.user)
    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado.')
        return redirect('dashboard')
    return render(request, 'proyectos/eliminar.html', {'proyecto': proyecto})