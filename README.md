# 🚨 Incident Management System (IMS)

A complete **Incident Management System** built using modern backend architecture.

This system simulates how companies like Amazon, Google, and Netflix handle production incidents.

---

# 📌 What This Project Does

👉 Collects system signals (e.g., DB down, API failure)  
👉 Processes them asynchronously using Kafka  
👉 Prevents duplicate incidents using Redis  
👉 Stores raw signals in MongoDB (Data Lake)  
👉 Stores incidents in PostgreSQL (Source of Truth)  
👉 Sends email alerts on incidents  
👉 Tracks RCA (Root Cause Analysis)  
👉 Calculates MTTR (Mean Time To Resolve)  
👉 Displays incidents in a React dashboard  

---

# 🧠 Architecture
[Client/API] → [FastAPI] → [Kafka] → [Worker]
Worker: → MongoDB (Raw Signals) → Redis (Deduplication) → PostgreSQL (Incidents + RCA) → Email Alerts
Frontend: → React Dashboard (via Nginx)

---

# ⚙️ Tech Stack

### Backend
- FastAPI (Python)
- Kafka (Event Streaming)
- Redis (Cache / Deduplication)
- PostgreSQL (Relational DB)
- MongoDB (Data Lake)

### Frontend
- React (Dashboard UI)
- Nginx (Serving + Proxy)

### DevOps
- Docker
- Docker Compose

---

# 🚀 How to Run (Docker)

## 1. Clone Repo

git clone <your-repo-url>
cd Incident_Management_System

## 2. Add Environment Variables

Create .env file:

Environment
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
EMAIL_TO=receiver_email@gmail.com

## 3. Start Application

docker compose up --build

## 4. Access Application

Service
URL
Frontend UI
http://
Backend API
http:///api
Health Check
http:///api/health

🔥 API Usage
## 1. Send Signal

curl -X POST http://<ip>/api/signal \
-H "Content-Type: application/json" \
-d '{"component_id":"DB","message":"down"}'
## Supported messages:

down → creates incident
up → resolves incident

## 2. Get Incidents

GET /api/incidents

## 3. Add RCA

curl -X POST http://<ip>/api/incidents/1/rca \
-H "Content-Type: application/json" \
-d '{
  "root_cause":"DB disk full",
  "fix":"Cleared disk",
  "prevention":"Add monitoring",
  "start_time":"2026-05-06 10:00:00",
  "end_time":"2026-05-06 10:30:00"
}'

## 4. Close Incident

curl -X PUT http://<ip>/api/incidents/1/status \
-H "Content-Type: application/json" \
-d '{"status":"CLOSED"}'
⚠️ Cannot close without RCA

## 5. Get MTTR

GET /api/incidents/1/mttr
📊 Database Design
PostgreSQL
incidents
id
component_id
message
status (OPEN / RESOLVED / CLOSED)
created_at

rca
incident_id
root_cause
fix
prevention
start_time
end_time
MongoDB
signals
Stores all raw incoming signals:
JSON
{
  "component_id": "db",
  "message": "down",
  "timestamp": 1710000000
}

⚡ Key Features
✅ Async Processing
Kafka-based architecture ensures high scalability
✅ Deduplication
Redis prevents duplicate incidents
✅ Data Lake
MongoDB stores raw signals
✅ RCA Enforcement
Incident cannot be closed without RCA
✅ Email Alerts
Triggered on:
Incident OPEN
Incident RESOLVED
✅ MTTR Calculation
Time taken to resolve incidents

🧪 Testing Flow
Send down signal → Incident created
Send duplicate down → Ignored
Send up → Incident resolved
Add RCA → Stored
Close incident → Allowed only after RCA

## 📦 Docker Services

frontend (React + Nginx)
backend (FastAPI)
worker (Kafka consumer)
kafka broker
redis
postgres
mongodb
