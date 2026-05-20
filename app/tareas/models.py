from django.db import models
from django.contrib.auth.models import User

class Tablero(models.Model):
    nombre = models.CharField(max_length=100)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tableros')
    colaboradores = models.ManyToManyField(User, related_name='tableros_compartidos', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    COLORES = [
        ('rojo', 'Rojo'),
        ('verde', 'Verde'),
        ('azul', 'Azul'),
        ('amarillo', 'Amarillo'),
        ('naranja', 'Naranja'),
        ('morado', 'Morado'),
    ]
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=20, choices=COLORES)
    tablero = models.ForeignKey(Tablero, on_delete=models.CASCADE, related_name='etiquetas')

    def __str__(self):
        return f"{self.nombre} ({self.color})"

class Lista(models.Model):
    nombre = models.CharField(max_length=100)
    tablero = models.ForeignKey(Tablero, on_delete=models.CASCADE, related_name='listas')
    posicion = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['posicion']

    def __str__(self):
        return self.nombre

class Tarjeta(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, related_name='tarjetas')
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarjetas_asignadas')
    fecha_limite = models.DateField(null=True, blank=True)
    posicion = models.PositiveIntegerField(default=0)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='tarjetas')

    class Meta:
        ordering = ['posicion']

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en']

    def __str__(self):
        return f"Comentario de {self.autor} en {self.tarjeta}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario} - {self.mensaje[:30]}"