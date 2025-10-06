from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    engine: str = "kokkoro"

@app.get("/")
def root():
    return {"message": "TTS Gateway Working", "status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tts")
def tts_generate(request: TTSRequest):
    audio_data = f"AUDIO_{request.engine}_{request.text}".encode()
    return Response(content=audio_data, media_type="audio/mpeg")

@app.get("/engines/status")
def engines():
    return {"kokkoro": "ready", "chatterbox": "ready", "coqui": "ready"}