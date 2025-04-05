FROM --platform=linux/amd64 python:3.10-slim AS builder

# Establecer variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instalar dependencias de sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa final con solo los componentes necesarios
FROM --platform=linux/amd64 python:3.10-slim

# Copiar dependencias y archivos necesarios desde el builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Instalar dependencias de sistema necesarias para la ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar código y modelo
COPY api.py .
COPY models/ .
COPY models/best_model.h5 ./models
COPY models/model_metadata.txt ./models

# Puerto para la API
EXPOSE 4001

# Punto de entrada para la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:4001", "api:app"]