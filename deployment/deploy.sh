#!/bin/bash

# Build and deploy TTS system to RunPod

set -e

echo "Building Docker images..."

# Build Gateway
cd ../gateway
docker build -t tts-gateway:latest .
docker tag tts-gateway:latest your-registry/tts-gateway:latest
docker push your-registry/tts-gateway:latest

# Build Kokkoro Engine
cd ../engines/kokkoro
docker build -t tts-kokkoro:latest .
docker tag tts-kokkoro:latest your-registry/tts-kokkoro:latest
docker push your-registry/tts-kokkoro:latest

# Build Chatterbox Engine
cd ../engines/chatterbox
docker build -t tts-chatterbox:latest .
docker tag tts-chatterbox:latest your-registry/tts-chatterbox:latest
docker push your-registry/tts-chatterbox:latest

# Build Coqui Engine
cd ../engines/coqui
docker build -t tts-coqui:latest .
docker tag tts-coqui:latest your-registry/tts-coqui:latest
docker push your-registry/tts-coqui:latest

echo "Deploying to RunPod..."

# Deploy engines first
runpod create pod \
  --name "tts-kokkoro" \
  --image "your-registry/tts-kokkoro:latest" \
  --gpu-type "NVIDIA RTX 4090" \
  --gpu-count 1 \
  --memory "16GB" \
  --cpu-count 2 \
  --ports "8000:8000"

runpod create pod \
  --name "tts-chatterbox" \
  --image "your-registry/tts-chatterbox:latest" \
  --gpu-type "NVIDIA RTX 4090" \
  --gpu-count 1 \
  --memory "16GB" \
  --cpu-count 2 \
  --ports "8000:8000"

runpod create pod \
  --name "tts-coqui" \
  --image "your-registry/tts-coqui:latest" \
  --gpu-type "NVIDIA RTX 4090" \
  --gpu-count 1 \
  --memory "16GB" \
  --cpu-count 2 \
  --ports "8000:8000"

# Wait for engines to be ready
sleep 30

# Deploy gateway with engine URLs
runpod create pod \
  --name "tts-gateway" \
  --image "your-registry/tts-gateway:latest" \
  --gpu-type "NVIDIA RTX 4090" \
  --gpu-count 1 \
  --memory "16GB" \
  --cpu-count 4 \
  --ports "8000:8000" \
  --env "KOKKORO_URL=https://kokkoro-endpoint.runpod.io" \
  --env "CHATTERBOX_URL=https://chatterbox-endpoint.runpod.io" \
  --env "COQUI_URL=https://coqui-endpoint.runpod.io"

echo "Deployment complete!"
echo "Gateway URL: https://gateway-endpoint.runpod.io"