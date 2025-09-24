# 1. Usar una imagen base de Python completa (no 'slim') que incluye más herramientas.
FROM python:3.11

# 2. Instalar las dependencias del sistema operativo necesarias para compilar faiss-cpu.
#    - build-essential: Contiene compiladores de C/C++.
#    - libomp-dev: Es una dependencia directa de FAISS.
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Configurar el directorio de trabajo.
WORKDIR /app

# 4. Copiar e instalar los requerimientos de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto de la aplicación.
COPY . .

# 6. Exponer el puerto.
EXPOSE 8080

# 7. Ejecutar la aplicación.
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.headless=true"]
