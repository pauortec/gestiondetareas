from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyectos/', views.lista_proyectos, name='lista_proyectos'),
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('tareas/mover/', views.mover_tarea, name='mover_tarea'),
]