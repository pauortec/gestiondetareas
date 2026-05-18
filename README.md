# Gestion de Tareas

Proyecto en Django con base PostgreSQL, todo corriendo en contenedores Docker.

---

## Setup inicial (Isaias)

- Arme el `Dockerfile` con Python 3.12 y las dependencias necesarias para Django + psycopg2.
- Cree el `docker-compose.yml` con tres servicios: `web` (Django), `db` (Postgres 16) y `pgadmin` (administrador web de la base).
- Configure credenciales, nombres y volumenes de la base.
- El puerto de Postgres lo expuse en `5433` del host porque el `5432` ya lo usaba un Postgres local.
- El volumen de pgAdmin lo deje como volumen nombrado de Docker para evitar problemas de permisos al levantarlo en otra PC.
- Verifique que `db` y `pgadmin` levantan correctamente y se comunican entre si.

El proyecto Django todavia no esta creado, eso lo arma el siguiente paso del equipo.

---

## Como funciona Docker en este proyecto

Tres contenedores se levantan juntos con `docker-compose`:

- **web**: Python 3.12 + Django. Aca corre el servidor de desarrollo.
- **db**: PostgreSQL 16. La base del proyecto.
- **pgadmin**: interfaz web para mirar y administrar la base.

Ningun dev tiene que instalar Python, Django ni Postgres en su PC. Solo Docker.

Cada PC tiene su **propia base local** (los datos viven en `volumes/pg-data/`, que esta en el `.gitignore`). Lo que se comparte por git son las **migraciones de Django**, que son la receta para recrear el esquema de la base en cualquier PC.

El puerto **5433** del host se mapea al `5432` del contenedor. Solo importa si te queres conectar desde afuera de Docker (DBeaver, psql del host, etc.). Adentro de la red de Docker, los servicios se hablan en el `5432` normal.

---

## Comandos utiles

```bash
# Levantar todo en segundo plano
docker-compose up -d

# Levantar y ver logs en vivo
docker-compose up

# Apagar todo
docker-compose down

# Apagar y borrar volumenes (CUIDADO: borra los datos de la base)
docker-compose down -v

# Ver servicios corriendo
docker-compose ps

# Ver logs de un servicio
docker-compose logs web
docker-compose logs -f db    # -f para seguir en vivo

# Entrar a la consola de un contenedor
docker-compose exec web bash
docker-compose exec db psql -U gestion_user -d gestion_tareas

# Ejecutar comandos de Django dentro del contenedor
docker-compose exec web python app/manage.py migrate
docker-compose exec web python app/manage.py makemigrations
docker-compose exec web python app/manage.py createsuperuser
docker-compose exec web python app/manage.py shell

# Reconstruir la imagen (si cambia requirements.txt o Dockerfile)
docker-compose build
docker-compose up -d
```
