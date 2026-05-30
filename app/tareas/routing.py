from django.urls import path

from .consumers import TableroConsumer


# Un websocket por proyecto: ws/tablero/<proyecto_id>/
websocket_urlpatterns = [
    path('ws/tablero/<int:proyecto_id>/', TableroConsumer.as_asgi()),
]
