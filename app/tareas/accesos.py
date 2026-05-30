"""
Reglas de acceso a proyectos y tareas.

Centraliza aca quien puede ver que, asi las vistas y los consumers de
websocket aplican el mismo criterio sin duplicar logica.

Reglas:
- Un proyecto lo ve su propietario y los colaboradores que invito.
- Una tarea la ve cualquiera con acceso al proyecto, mas el responsable
  asignado (aunque no este en el proyecto).
"""

from django.db.models import Q

from .models import Proyecto, Tarea


# Queryset de proyectos accesibles para el usuario.
# Distinct evita duplicados cuando el M2M de colaboradores hace join.
def proyectos_de(usuario):
    return Proyecto.objects.filter(
        Q(propietario=usuario) | Q(colaboradores=usuario)
    ).distinct()


# Queryset de tareas accesibles para el usuario.
# Incluye tareas asignadas aunque el usuario no este en el proyecto.
def tareas_de(usuario):
    return Tarea.objects.filter(
        Q(proyecto__propietario=usuario)
        | Q(proyecto__colaboradores=usuario)
        | Q(responsable=usuario)
    ).distinct()


# Chequeo puntual para un proyecto ya cargado (evita otro query si ya esta en memoria).
def puede_ver_proyecto(usuario, proyecto):
    return (
        proyecto.propietario_id == usuario.id
        or proyecto.colaboradores.filter(pk=usuario.pk).exists()
    )


# Chequeo puntual para una tarea ya cargada.
def puede_ver_tarea(usuario, tarea):
    if tarea.responsable_id == usuario.id:
        return True
    return puede_ver_proyecto(usuario, tarea.proyecto)
