from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
import httpx
import os
import base64
from io import BytesIO
from pydub import AudioSegment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TTS Gateway API",
    description="Centralized gateway for multiple TTS engines on RunPod",
    version="1.0.0"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine configuration - set these as environment variables in Render
ENGINES = {
    "kokkoro": os.getenv("KOKKORO_URL"),
    "chatterbox": os.getenv("CHATTERBOX_URL"),
    "coqui": os.getenv("COQUI_URL")
}

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", min_length=1, max_length=5000)
    engine: Literal["kokkoro", "chatterbox", "coqui"] = Field(..., description="TTS engine to use")
    voice: Optional[str] = Field(None, description="Voice ID or name (engine-specific)")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    format: Literal["mp3", "wav"] = Field("mp3", description="Output audio format")

class HealthResponse(BaseModel):
    status: str
    engines: dict

@app.post("/tts", 
    response_class=Response,
    responses={
        200: {
            "content": {"audio/mpeg": {}, "audio/wav": {}},
            "description": "Generated audio file"
        }
    }
)
async def generate_tts(request: TTSRequest):
    """
    Generate speech from text using specified TTS engine.
    Returns audio file in requested format (MP3 or WAV).
    """
    if request.engine not in ENGINES:
        raise HTTPException(400, f"Engine '{request.engine}' not supported")
    
    engine_url = ENGINES[request.engine]
    if not engine_url:
        raise HTTPException(500, f"Engine '{request.engine}' not configured")
    
    logger.info(f"Generating TTS with {request.engine} engine for text: {request.text[:50]}...")
    
    try:
        # Prepare request payload for engine
        payload = {
            "text": request.text,
            "voice": request.voice,
            "speed": request.speed
        }
        
        # Call the TTS engine with timeout
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{engine_url}/generate",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Engine returned status {response.status_code}: {response.text}")
                raise HTTPException(500, f"TTS generation failed: {response.text}")
            
            # Get audio data from response
            result = response.json()
            
            # Handle base64-encoded audio
            if "audio_base64" in result:
                audio_data = base64.b64decode(result["audio_base64"])
            elif "audio_file" in result:
                # If engine returns file path, fetch it
                file_response = await client.get(f"{engine_url}/download/{result['audio_file']}")
                audio_data = file_response.content
            else:
                raise HTTPException(500, "Invalid response format from TTS engine")
            
            # Process audio in-memory
            audio = AudioSegment.from_file(BytesIO(audio_data))
            
            # Apply speed adjustment if needed
            if request.speed and request.speed != 1.0:
                audio = audio.speedup(playback_speed=request.speed)
            
            # Convert to requested format in-memory
            output = BytesIO()
            if request.format == "mp3":
                audio.export(output, format="mp3", bitrate="192k")
                media_type = "audio/mpeg"
            else:
                audio.export(output, format="wav")
                media_type = "audio/wav"
            
            output.seek(0)
            
            logger.info(f"Successfully generated {request.format} audio")
            
            return Response(
                content=output.read(),
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="speech.{request.format}"'
                }
            )
    
    except httpx.TimeoutException:
        logger.error("Request to TTS engine timed out")
        raise HTTPException(504, "TTS engine request timed out")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to TTS engine: {str(e)}")
        raise HTTPException(503, f"Unable to connect to TTS engine: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

@app.get("/engines")
async def list_engines():
    """List all available TTS engines and their status"""
    engine_status = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in ENGINES.items():
            if not url:
                engine_status[name] = {"status": "not_configured", "url": None}
                continue
            
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    engine_status[name] = {"status": "online", "url": url}
                else:
                    engine_status[name] = {"status": "offline", "url": url}
            except:
                engine_status[name] = {"status": "unreachable", "url": url}
    
    return {"engines": engine_status}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "engines": {
            name: "configured" if url else "not_configured"
            for name, url in ENGINES.items()
        }
    }

@app.get("/")
async def root():
    """API information"""
    return {
        "service": "TTS Gateway",
        "version": "1.0.0",
        "documentation": "/docs",
        "available_engines": list(ENGINES.keys())
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
