from django.db.models import Q

from .models import Proyecto, Tarea


# Proyectos que el usuario posee o le compartieron
def proyectos_de(usuario):
    return Proyecto.objects.filter(
        Q(propietario=usuario) | Q(colaboradores=usuario)
    ).distinct()


# Tareas de proyectos accesibles o asignadas al usuario
def tareas_de(usuario):
    return Tarea.objects.filter(
        Q(proyecto__propietario=usuario)
        | Q(proyecto__colaboradores=usuario)
        | Q(responsable=usuario)
    ).distinct()


def puede_ver_proyecto(usuario, proyecto):
    return (
        proyecto.propietario_id == usuario.id
        or proyecto.colaboradores.filter(pk=usuario.pk).exists()
    )


def puede_ver_tarea(usuario, tarea):
    if tarea.responsable_id == usuario.id:
        return True
    return puede_ver_proyecto(usuario, tarea.proyecto)
