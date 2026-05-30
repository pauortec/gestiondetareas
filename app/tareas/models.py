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

    # Extiende save para registrar cambios en el historial, notificar al asignado y avisar al tablero
    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        eventos = []
        estado_anterior = None
        responsable_anterior_id = None
        if not es_nueva:
            try:
                anterior = Tarea.objects.get(pk=self.pk)
                estado_anterior = anterior.estado
                responsable_anterior_id = anterior.responsable_id
                if anterior.estado != self.estado:
                    eventos.append(f"Estado: {anterior.get_estado_display()} -> {self.get_estado_display()}")
                if anterior.responsable_id != self.responsable_id:
                    a = anterior.responsable.username if anterior.responsable else '(sin asignar)'
                    n = self.responsable.username if self.responsable else '(sin asignar)'
                    eventos.append(f"Responsable: {a} -> {n}")
            except Tarea.DoesNotExist:
                pass
        super().save(*args, **kwargs)
        for evento in eventos:
            HistorialTarea.objects.create(tarea=self, evento=evento)
        # Notifica al nuevo responsable cuando cambia la asignacion
        if self.responsable_id and self.responsable_id != responsable_anterior_id:
            notif = Notificacion.objects.create(
                usuario=self.responsable,
                mensaje=f"Te asignaron la tarea '{self.titulo}'",
            )
            _broadcast_notificacion(notif)
        if es_nueva or estado_anterior != self.estado:
            _broadcast_tablero(self, 'crear' if es_nueva else 'mover')


# Avisa a los clientes conectados al tablero del proyecto que hubo un cambio.
# Falla en silencio si Channels no esta levantado (tests o local sin redis).
def _broadcast_tablero(tarea, accion):
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
    except ImportError:
        return
    layer = get_channel_layer()
    if not layer:
        return
    try:
        async_to_sync(layer.group_send)(f'tablero_{tarea.proyecto_id}', {
            'type': 'evento_tablero',
            'data': {'accion': accion, 'tarea_id': tarea.pk, 'estado': tarea.estado},
        })
    except Exception:
        pass


# Empuja la notificacion al canal personal del usuario asignado
def _broadcast_notificacion(notif):
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
    except ImportError:
        return
    layer = get_channel_layer()
    if not layer:
        return
    try:
        async_to_sync(layer.group_send)(f'notif_{notif.usuario_id}', {
            'type': 'evento_notif',
            'data': {
                'mensaje': notif.mensaje,
                'creada_en': notif.creada_en.isoformat(),
            },
        })
    except Exception:
        pass


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


class HistorialTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='historial')
    evento = models.CharField(max_length=200)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.tarea}: {self.evento}"


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']

    def __str__(self):
        return f"Notificacion para {self.usuario}"