.PHONY: build deploy test clean

# Build all Docker images
build:
	docker build -t tts-gateway:latest ./gateway
	docker build -t tts-kokkoro:latest ./engines/kokkoro
	docker build -t tts-chatterbox:latest ./engines/chatterbox
	docker build -t tts-coqui:latest ./engines/coqui

# Start local development environment
dev:
	docker-compose up --build

# Run tests
test:
	python test_client.py

# Deploy to RunPod
deploy:
	chmod +x deployment/deploy.sh
	./deployment/deploy.sh

# Clean up Docker images
clean:
	docker rmi tts-gateway:latest tts-kokkoro:latest tts-chatterbox:latest tts-coqui:latest || true
	docker system prune -f

# Monitor services
monitor:
	python deployment/monitoring.py

# Build and push to registry
push: build
	docker tag tts-gateway:latest $(DOCKER_REGISTRY)/tts-gateway:latest
	docker tag tts-kokkoro:latest $(DOCKER_REGISTRY)/tts-kokkoro:latest
	docker tag tts-chatterbox:latest $(DOCKER_REGISTRY)/tts-chatterbox:latest
	docker tag tts-coqui:latest $(DOCKER_REGISTRY)/tts-coqui:latest
	docker push $(DOCKER_REGISTRY)/tts-gateway:latest
	docker push $(DOCKER_REGISTRY)/tts-kokkoro:latest
	docker push $(DOCKER_REGISTRY)/tts-chatterbox:latest
	docker push $(DOCKER_REGISTRY)/tts-coqui:latest