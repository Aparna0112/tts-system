# Production-Ready Modular TTS System

A CUDA-accelerated serverless TTS system with three engines (Kokkoro, Chatterbox, Coqui TTS) deployed on RunPod.

## Architecture

- **Gateway**: FastAPI router with load balancing
- **Engines**: Separate CUDA-enabled containers for each TTS engine
- **Deployment**: RunPod serverless with GPU acceleration
- **Processing**: In-memory audio processing with direct streaming

## Quick Start

1. **Deploy Gateway**:
   ```bash
   cd gateway && runpod deploy --gpu-type "NVIDIA RTX 4090"
   ```

2. **Deploy Engines**:
   ```bash
   cd engines/kokkoro && runpod deploy --gpu-type "NVIDIA RTX 4090"
   cd engines/chatterbox && runpod deploy --gpu-type "NVIDIA RTX 4090"
   cd engines/coqui && runpod deploy --gpu-type "NVIDIA RTX 4090"
   ```

## API Usage

```bash
curl -X POST "https://gateway-url/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "engine": "kokkoro", "voice": "default"}' \
  --output audio.mp3
```

## Monitoring

- Health checks: `/health`
- Metrics: `/metrics`
- Engine status: `/engines/status`