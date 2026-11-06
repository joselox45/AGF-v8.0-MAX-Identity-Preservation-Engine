# AGF v12.4.7.8-STRONG - Motor Forense
FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema (OpenCV necesita libGL y libglib)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente (sin el modelo de 174MB)
COPY . .

# El modelo NO está en el repo (está en .gitignore)
# Se debe montar como volumen desde el host

# Exponer el puerto de la API
EXPOSE 8000

# Comando por defecto: levantar la API
CMD ["python", "api_server.py"]
