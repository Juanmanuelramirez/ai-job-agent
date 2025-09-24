# 1. Usar una imagen base de Python oficial y ligera.
FROM python:3.11-slim

# 2. Instalar las dependencias a nivel de sistema operativo necesarias para compilar faiss-cpu.
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor.
WORKDIR /app

# 4. Copiar e instalar los requerimientos de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código de la aplicación al contenedor.
COPY . .

# 6. Exponer el puerto que Streamlit usará.
EXPOSE 8080

# 7. El comando para ejecutar la aplicación cuando el contenedor inicie.
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.headless=true"]

