from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"working": True}

@app.get("/{path:path}")
def catch_all(path: str):
    return {"path": path, "working": True}