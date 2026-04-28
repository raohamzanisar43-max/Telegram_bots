from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI on Railway is working!"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FastAPI on Railway"}

@app.get("/api/info")
async def info():
    return {
        "service": "Profitability Intelligence API",
        "status": "running",
        "platform": "Railway"
    }
