from django.contrib import admin
from .models import Proyecto, Tarea, ParteHoras, Notificacion

admin.site.register(Proyecto)
admin.site.register(Tarea)
admin.site.register(ParteHoras)
admin.site.register(Notificacion)
