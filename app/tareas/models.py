from django.db import models
from django.contrib.auth.models import User


# Opciones fijas de categoria
CATEGORIAS = [
    ('tecnico', 'Técnico'),
    ('funcional', 'Funcional'),
]

# Estados de la tarea en orden de avance
ESTADOS = [
    ('relevamiento', 'Relevamiento'),
    ('analisis', 'Análisis y Desarrollo'),
    ('test', 'Test y Capacitación'),
    ('terminado', 'Terminado'),
]


class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    # Dueno del proyecto: solo el lo ve salvo que lo comparta
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos')
    # Usuarios con acceso explicito al proyecto
    colaboradores = models.ManyToManyField(User, related_name='proyectos_compartidos', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='relevamiento')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='tecnico')
    # Usuario asignado: puede gestionarla aunque no sea el creador
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas'
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    # Orden de la tarjeta dentro de su columna en el kanban
    posicion = models.PositiveIntegerField(default=0)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['estado', 'posicion']

    def __str__(self):
        return self.titulo


class ParteHoras(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='partes_horas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='partes_horas')
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True)
    horas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Misma clasificacion que la tarea
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='tecnico')

    class Meta:
        ordering = ['fecha', 'id']

    def __str__(self):
        return f"{self.tarea} - {self.horas}h"


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']

    def __str__(self):
        return f"Notificacion para {self.usuario}"
