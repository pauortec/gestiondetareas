import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0002_remove_etiqueta_tablero_remove_tarjeta_etiquetas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento', models.CharField(max_length=200)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('tarea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='tareas.tarea')),
            ],
            options={
                'ordering': ['-creado_en'],
            },
        ),
    ]