from rest_framework import serializers
from .models import Notificacion, Tarea


class NotificacionSerializer(serializers.ModelSerializer):
    # Hora formateada para mostrar en el panel (ej: "17/06 20:39")
    hora = serializers.SerializerMethodField()
    tarea_pk = serializers.IntegerField(source='tarea_id', read_only=True)

    class Meta:
        model = Notificacion
        fields = ['pk', 'mensaje', 'leida', 'tarea_pk', 'hora']

    def get_hora(self, obj):
        return obj.creada_en.strftime('%d/%m %H:%M')


class MoverTareaSerializer(serializers.Serializer):
    tarea_id = serializers.IntegerField()
    estado = serializers.CharField(max_length=20)
    # Lista de IDs en el nuevo orden dentro de la columna
    orden = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)


class TareaResumenSerializer(serializers.ModelSerializer):
    responsable = serializers.StringRelatedField()
    proyecto = serializers.StringRelatedField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Tarea
        fields = ['id', 'titulo', 'estado', 'estado_display', 'proyecto', 'responsable', 'fecha_limite']
