from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="TTS Gateway")

class TTSRequest(BaseModel):
    text: str
    engine: str

ENGINES = {
    "kokkoro": os.getenv("KOKKORO_URL", "http://kokkoro:8001"),
    "chatterbox": os.getenv("CHATTERBOX_URL", "http://chatterbox:8002")
}

@app.post("/tts")
async def generate_tts(request: TTSRequest):
    if request.engine not in ENGINES:
        raise HTTPException(400, f"Engine {request.engine} not supported")
    
    engine_url = ENGINES[request.engine]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{engine_url}/generate",
            json={"text": request.text}
        )
        
        if response.status_code != 200:
            raise HTTPException(500, "TTS generation failed")
        
        return response.json()

@app.get("/engines")
async def list_engines():
    return {"engines": list(ENGINES.keys())}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)