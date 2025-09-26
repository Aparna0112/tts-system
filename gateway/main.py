from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import os

app = FastAPI(title="TTS Gateway", version="2.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSRequest(BaseModel):
    text: str
    engine: str = "kokkoro"
    voice: str = "default"
    speed: float = 1.0

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.get("/")
async def root():
    return {"message": "TTS Gateway v2.0.0 - Working!", "status": "online"}

@app.post("/tts")
async def generate_tts(request: TTSRequest):
    logger.info(f"Generating TTS for: {request.text[:50]}... using {request.engine}")
    
    # Create mock audio data based on engine
    if request.engine == "kokkoro":
        audio_data = b"KOKKORO_AUDIO_" + request.text.encode()[:30]
    elif request.engine == "chatterbox":
        audio_data = b"CHATTERBOX_AUDIO_" + request.text.encode()[:30]
    elif request.engine == "coqui":
        audio_data = b"COQUI_AUDIO_" + request.text.encode()[:30]
    else:
        audio_data = b"DEFAULT_AUDIO_" + request.text.encode()[:30]
    
    def stream_audio():
        yield audio_data
    
    return StreamingResponse(
        stream_audio(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={request.engine}_audio.mp3"}
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/engines/status")
async def engines_status():
    return {
        "kokkoro": {"status": "ready", "engine": "kokkoro", "device": "gpu"},
        "chatterbox": {"status": "ready", "engine": "chatterbox", "device": "gpu"},
        "coqui": {"status": "ready", "engine": "coqui", "device": "gpu"}
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)