from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyectos/', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/kanban/', views.kanban_proyectos, name='kanban_proyectos'),
    path('proyectos/<int:pk>/compartir/', views.compartir_proyecto, name='compartir_proyecto'),
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('tareas/kanban/', views.kanban_tareas, name='kanban_tareas'),
    path('tareas/mover/', views.mover_tarea, name='mover_tarea'),
    path('tareas/<int:pk>/', views.detalle_tarea, name='detalle_tarea'),
    path('tareas/<int:pk>/asignar/', views.asignar_tarea, name='asignar_tarea'),
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('tareas/<int:pk>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
    path('proyectos/<int:pk>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('notificaciones/', views.notificaciones_json, name='notificaciones_json'),
    path('notificaciones/<int:pk>/leer/', views.marcar_notif_leida, name='marcar_notif_leida'),
]