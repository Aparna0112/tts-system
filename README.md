# Modular TTS System for RunPod

Multi-engine Text-to-Speech system with Docker containers and centralized API gateway.

## Architecture

```
API Gateway (FastAPI) → Docker Containers
├── Kokkoro TTS
└── Chatterbox TTS
```

## Quick Start

1. Clone to RunPod:
```bash
git clone <your-repo-url>
cd tts-system
```

2. Build containers:
```bash
docker-compose up --build
```

3. Test API:
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "engine": "kokkoro"}'
```

## API Endpoints

- `POST /tts` - Generate speech
- `GET /engines` - List available engines
- `GET /health` - Health check

## Deployment

Deploy to RunPod using the provided docker-compose.yml file.