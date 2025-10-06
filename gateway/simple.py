from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "working": True}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tts")
def tts(data: dict):
    return {"received": data, "audio": "mock_audio_data"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)