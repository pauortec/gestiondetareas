from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0003_historialtarea'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='etapa',
            field=models.CharField(
                choices=[
                    ('implementacion', 'En Implementación'),
                    ('produccion', 'En Producción'),
                    ('con_soporte', 'Con soporte'),
                    ('sin_soporte', 'Sin soporte'),
                    ('interno', 'Interno'),
                    ('cancelado', 'Cancelado'),
                ],
                default='implementacion',
                max_length=20,
            ),
        ),
    ]
