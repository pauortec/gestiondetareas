from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0004_proyecto_etapa'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='tarea',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notificaciones',
                to='tareas.tarea',
            ),
        ),
    ]
