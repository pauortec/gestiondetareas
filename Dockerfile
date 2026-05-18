# Imagen base con Python 3.12
FROM python:3.12-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /code

# Dependencias del sistema para que psycopg2 pueda compilar
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
