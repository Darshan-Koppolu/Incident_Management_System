from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kafka_producer import send_signal

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

    send_signal(signal)

    return {
        "status": "sent to queue",
        "component": signal["component_id"]
    }
