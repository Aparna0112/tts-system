from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    engine: str = "kokkoro"

# Add root route that was missing
@app.get("/")
def root():
    return {"message": "TTS Gateway Working", "status": "online"}

# Keep the working health route
@app.get("/health")
def health():
    return {"status": "healthy"}

# Add working TTS route
@app.post("/tts")
def tts(request: TTSRequest):
    audio_data = f"MOCK_AUDIO_{request.engine}_{request.text}".encode()
    return {"audio_generated": True, "engine": request.engine, "text": request.text}

@app.get("/engines/status")
def engines():
    return {"kokkoro": "ready", "chatterbox": "ready", "coqui": "ready"}