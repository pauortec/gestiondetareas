from django.urls import path

from .consumers import TableroConsumer, NotificacionConsumer


websocket_urlpatterns = [
    # Un canal por proyecto: cambios del tablero
    path('ws/tablero/<int:proyecto_id>/', TableroConsumer.as_asgi()),
    # Un canal personal por usuario: notificaciones
    path('ws/notificaciones/', NotificacionConsumer.as_asgi()),
]