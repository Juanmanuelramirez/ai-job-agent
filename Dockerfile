# Usa una imagen base oficial de Python. Se elige 'slim' para reducir el tamaño final de la imagen.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de dependencias para aprovechar el cache de capas de Docker.
# Docker solo reconstruirá esta capa si requirements.txt cambia.
COPY requirements.txt .

# Instala las dependencias de Python
# --no-cache-dir reduce el tamaño de la imagen al no almacenar la caché de pip
# --upgrade pip asegura que se use la última versión de pip
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que Streamlit se ejecuta por defecto
EXPOSE 8501

# Define un punto de control de salud para que el orquestador de contenedores (como AWS App Runner)
# sepa si la aplicación está funcionando correctamente.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD curl --fail http://localhost:8501/_stcore/health

# El comando para ejecutar la aplicación cuando se inicie el contenedor.
# --server.port escucha en el puerto 8501.
# --server.address=0.0.0.0 permite que la aplicación sea accesible desde fuera del contenedor.
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
