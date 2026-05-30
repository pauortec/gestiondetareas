from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyectos/', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/kanban/', views.kanban_proyectos, name='kanban_proyectos'),
    path('proyectos/<int:pk>/compartir/', views.compartir_proyecto, name='compartir_proyecto'),
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('tareas/mover/', views.mover_tarea, name='mover_tarea'),
    path('tareas/<int:pk>/asignar/', views.asignar_tarea, name='asignar_tarea'),
]