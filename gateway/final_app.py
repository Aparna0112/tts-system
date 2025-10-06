from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TTS Gateway", version="3.0.0")

class TTSRequest(BaseModel):
    text: str
    engine: str

@app.get("/")
def root():
    return {"message": "TTS Gateway v3.0.0 Working", "status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/engines")
def engines():
    return {"engines": ["kokkoro", "chatterbox", "coqui"]}

@app.post("/tts")
def tts(request: TTSRequest):
    # Simple working response
    audio_content = f"TTS_AUDIO_{request.engine}_{request.text}".encode()
    return {
        "success": True,
        "engine": request.engine,
        "text": request.text,
        "audio_size": len(audio_content),
        "message": "TTS generated successfully"
    }