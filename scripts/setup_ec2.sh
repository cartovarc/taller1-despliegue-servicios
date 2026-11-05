#!/usr/bin/env bash
# Acondiciona una EC2 Ubuntu: instala Docker, habilita al usuario 'ubuntu'
# y ejecuta el contenedor publicado en Docker Hub en el puerto 80.
#
# Uso (dentro de la EC2):
#   bash setup_ec2.sh <usuario_dockerhub>
set -euo pipefail

DOCKERHUB_USER="${1:?Uso: bash setup_ec2.sh <usuario_dockerhub>}"
IMAGE="${DOCKERHUB_USER}/stock-market:2.0"

# 1. Instalar Docker (https://docs.docker.com/engine/install/ubuntu/)
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker

# 2. Habilitar al usuario 'ubuntu' para ejecutar contenedores (aplica al reconectar)
sudo usermod -aG docker ubuntu

# 3. Descargar la imagen y ejecutar el contenedor (80 del host -> 5000 del contenedor)
sudo docker pull "$IMAGE"
sudo docker rm -f stock-market 2>/dev/null || true
sudo docker run -d --restart unless-stopped --name stock-market -p 80:5000 "$IMAGE"
sudo docker ps

echo
echo "Listo. Abre en el navegador: http://$(curl -s https://checkip.amazonaws.com)"
