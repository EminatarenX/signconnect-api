#!/bin/bash
set -e

# Variables de configuración
DOCKER_REGISTRY="your-registry.com"  # Reemplaza con tu registro de Docker
IMAGE_NAME="signconnect-api"
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)  # Versión basada en fecha y hora

# Verificar archivos necesarios
if [ ! -f "api.py" ] || [ ! -f "models/model_metadata.txt" ] || [ ! -d "models" ] || [ ! -f "models/best_model.h5" ]; then
    echo "Error: Faltan archivos requeridos. Verifica que api.py, model_metadata.txt y models/best_model.h5 existan."
    exit 1
fi

# Crear requirements.txt si no existe
if [ ! -f "requirements.txt" ]; then
    echo "Creando requirements.txt..."
    cat > requirements.txt << EOL
flask==2.2.5
tensorflow==2.10.1
opencv-python-headless==4.7.0.72
numpy==1.24.3
gunicorn==21.2.0
werkzeug==2.2.3
EOL
fi

echo "Construyendo imagen Docker: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
docker buildx build --platform linux/amd64 -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest --push .

echo "Subiendo imagen a registro Docker..."
docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest

echo "Actualizando manifiestos de Kubernetes..."
# Reemplazar placeholder en deployment.yaml
sed -i "s|\${DOCKER_REGISTRY}|${DOCKER_REGISTRY}|g" deployment.yaml

echo "Aplicando manifiestos a Kubernetes..."
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
# Opcional: aplicar ingress
# kubectl apply -f ingress.yaml

echo "Esperando a que los pods estén listos..."
kubectl rollout status deployment/signconnect-api

echo "Despliegue completado exitosamente."
echo "URL de la API: http://api.signconnect.example.com (o la URL configurada en tu entorno)"