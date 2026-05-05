from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kafka_producer import send_signal
from db import get_connection

app = FastAPI()

# ✅ CORS (frontend connect avvadaniki)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev lo ok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Health Check
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# POST Signal → Kafka
# =========================
@app.post("/api/signal")
def ingest_signal(signal: dict):

    if "component_id" not in signal:
        raise HTTPException(status_code=400, detail="component_id required")

    if "message" not in signal:
        raise HTTPException(status_code=400, detail="message required")

    # Optional validation (recommended)
    if signal["message"] not in ["down", "up"]:
        raise HTTPException(status_code=400, detail="Invalid message (use 'down' or 'up')")

    send_signal(signal)

    return {
        "status": "sent to queue",
        "component": signal["component_id"]
    }


# =========================
# GET Incidents → DB
# =========================
@app.get("/api/incidents")
def get_incidents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, component_id, message, status, created_at
        FROM incidents
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    incidents = []
    for row in rows:
        incidents.append({
            "id": row[0],
            "component_id": row[1],
            "message": row[2],
            "status": row[3],
            "created_at": str(row[4])
        })

    return incidents
