from django.contrib import admin
from .models import Proyecto, Tarea, ParteHoras, Notificacion, HistorialTarea

admin.site.register(Proyecto)
admin.site.register(Tarea)
admin.site.register(ParteHoras)
admin.site.register(Notificacion)
admin.site.register(HistorialTarea)