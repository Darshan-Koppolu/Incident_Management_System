from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for now (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


# 🔥 Signal API
@app.post("/signal")
def ingest_signal(signal: dict):

    if "component_id" not in signal:
        raise HTTPException(status_code=400, detail="component_id required")

    if "message" not in signal:
        raise HTTPException(status_code=400, detail="message required")

    print("Received signal:", signal)

    return {
        "status": "received",
        "component": signal["component_id"]
    }