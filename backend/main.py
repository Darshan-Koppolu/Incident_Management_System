from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kafka_producer import send_signal
from db import get_connection
from email_service import send_email
import time
import redis

app = FastAPI()

r = redis.Redis(host="redis", port=6379, decode_responses=True)

# =========================
# Rate Limiter
# =========================
def rate_limit():
    key = f"rate:{int(time.time())}"
    count = r.incr(key)
    r.expire(key, 1)

    return count <= 100


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Health
# =========================
@app.get("/api/health")
def health():
    return {"status": "ok"}


# =========================
# Signal API
# =========================
@app.post("/api/signal")
def ingest_signal(signal: dict):

    if not rate_limit():
        raise HTTPException(status_code=429, detail="Too many requests")

    if "component_id" not in signal:
        raise HTTPException(status_code=400, detail="component_id required")

    if "message" not in signal:
        raise HTTPException(status_code=400, detail="message required")

    if signal["message"] not in ["down", "up"]:
        raise HTTPException(status_code=400, detail="Invalid message")

    send_signal(signal)

    return {"status": "sent to queue", "component": signal["component_id"]}


# =========================
# Get Incidents
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

    return [
        {
            "id": r[0],
            "component_id": r[1],
            "message": r[2],
            "status": r[3],
            "created_at": str(r[4])
        }
        for r in rows
    ]


# =========================
# RCA
# =========================
@app.post("/api/incidents/{incident_id}/rca")
def add_rca(incident_id: int, data: dict):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rca (incident_id, root_cause, fix, prevention, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        incident_id,
        data["root_cause"],
        data["fix"],
        data["prevention"],
        data["start_time"],
        data["end_time"]
    ))

    conn.commit()

    return {"status": "RCA added"}


# =========================
# UPDATE STATUS (CRITICAL)
# =========================
@app.put("/api/incidents/{incident_id}/status")
def update_status(incident_id: int, data: dict):

    conn = get_connection()
    cursor = conn.cursor()

    new_status = data["status"]

    # ❌ Cannot CLOSE without RCA
    if new_status == "CLOSED":
        cursor.execute("SELECT * FROM rca WHERE incident_id=%s", (incident_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Cannot CLOSE without RCA"
            )

    cursor.execute(
        "UPDATE incidents SET status=%s WHERE id=%s",
        (new_status, incident_id)
    )

    conn.commit()

    # 🔥 EMAIL ON CLOSE
    if new_status == "CLOSED":
        send_email(
            "📌 Incident CLOSED",
            f"Incident {incident_id} has been CLOSED after RCA"
        )

    return {"status": "updated"}


# =========================
# MTTR
# =========================
@app.get("/api/incidents/{incident_id}/mttr")
def get_mttr(incident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT start_time, end_time
        FROM rca WHERE incident_id=%s
    """, (incident_id,))

    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="RCA not found")

    mttr = row[1] - row[0]

    return {"incident_id": incident_id, "mttr": str(mttr)}
