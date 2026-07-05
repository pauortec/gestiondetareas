from django.db import migrations


def crear_grupo(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Administrador')


def eliminar_grupo(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Administrador').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0006_comentariotarea_archivotarea'),
    ]

    operations = [
        migrations.RunPython(crear_grupo, eliminar_grupo),
    ]
