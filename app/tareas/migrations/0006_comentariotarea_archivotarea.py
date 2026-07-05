from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0005_notificacion_tarea'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComentarioTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('contenido', models.TextField()),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='comentarios', to=settings.AUTH_USER_MODEL,
                )),
                ('tarea', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comentarios', to='tareas.tarea',
                )),
            ],
            options={'ordering': ['creado_en']},
        ),
        migrations.CreateModel(
            name='ArchivoTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('archivo', models.FileField(upload_to='tareas/%Y/%m/')),
                ('nombre', models.CharField(max_length=200)),
                ('subido_en', models.DateTimeField(auto_now_add=True)),
                ('subido_por', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='archivos', to=settings.AUTH_USER_MODEL,
                )),
                ('tarea', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='archivos', to='tareas.tarea',
                )),
            ],
            options={'ordering': ['-subido_en']},
        ),
    ]
