import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Proyecto
from .accesos import puede_ver_proyecto


# Consumer del tablero: agrupa por proyecto y reenvia eventos a todos los conectados
class TableroConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.proyecto_id = int(self.scope['url_route']['kwargs']['proyecto_id'])
        self.grupo = f'tablero_{self.proyecto_id}'
        user = self.scope.get('user')

        # Rechaza si no esta autenticado o no tiene acceso al proyecto
        if not user or not user.is_authenticated or not await self._tiene_acceso(user):
            await self.close()
            return

        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'grupo'):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    # Reenvia al cliente cualquier mensaje del grupo
    async def evento_tablero(self, event):
        await self.send_json(event['data'])

    @database_sync_to_async
    def _tiene_acceso(self, user):
        try:
            proyecto = Proyecto.objects.get(pk=self.proyecto_id)
        except Proyecto.DoesNotExist:
            return False
        return puede_ver_proyecto(user, proyecto)


# Consumer personal de notificaciones: un grupo por usuario
class NotificacionConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return
        self.grupo = f'notif_{user.id}'
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'grupo'):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def evento_notif(self, event):
        await self.send_json(event['data'])