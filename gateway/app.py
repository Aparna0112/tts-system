from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
import io
import os

app = FastAPI(title="TTS Gateway", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSRequest(BaseModel):
    text: str
    engine: str = "kokkoro"
    voice: str = "default"
    speed: float = 1.0

class EngineConfig:
    def __init__(self):
        self.engines = {
            "kokkoro": os.getenv("KOKKORO_URL", "http://localhost:8001"),
            "chatterbox": os.getenv("CHATTERBOX_URL", "http://localhost:8002"),
            "coqui": os.getenv("COQUI_URL", "http://localhost:8003")
        }
        self.client = httpx.AsyncClient(timeout=30.0)

config = EngineConfig()

@app.post("/tts")
async def generate_tts(request: TTSRequest):
    if request.engine not in config.engines:
        raise HTTPException(status_code=400, detail="Invalid engine")
    
    engine_url = config.engines[request.engine]
    
    try:
        async with config.client.stream(
            "POST",
            f"{engine_url}/generate",
            json=request.dict(),
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Engine error")
            
            async def stream_audio():
                async for chunk in response.aiter_bytes():
                    yield chunk
            
            return StreamingResponse(
                stream_audio(),
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment; filename=audio.mp3"}
            )
    except httpx.RequestError as e:
        logger.error(f"Engine request failed: {e}")
        raise HTTPException(status_code=503, detail="Engine unavailable")

@app.get("/health")
async def health_check():
    engine_status = {}
    for name, url in config.engines.items():
        try:
            logger.info(f"Checking engine {name} at {url}")
            response = await config.client.get(f"{url}/health", timeout=5.0)
            engine_status[name] = response.status_code == 200
            logger.info(f"Engine {name} status: {response.status_code}")
        except Exception as e:
            logger.error(f"Engine {name} check failed: {e}")
            engine_status[name] = False
    
    return {"status": "healthy", "engines": engine_status}

@app.get("/engines/status")
async def engines_status():
    status = {}
    for name, url in config.engines.items():
        try:
            response = await config.client.get(f"{url}/status", timeout=5.0)
            status[name] = response.json() if response.status_code == 200 else {"error": "unavailable"}
        except:
            status[name] = {"error": "unreachable"}
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)