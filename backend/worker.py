from kafka import KafkaConsumer
from db import get_connection
from mongo import signals_collection
from email_service import send_email
import json
import time
import redis

# Redis connection
r = redis.Redis(host="redis", port=6379, decode_responses=True)

consumer = None


def get_consumer():
    global consumer

    if consumer is not None:
        return consumer

    for i in range(10):
        try:
            consumer = KafkaConsumer(
                "signals",
                bootstrap_servers="broker:9092",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                group_id="ims-group"
            )
            print("Worker connected to Kafka", flush=True)
            return consumer
        except Exception:
            print(f"Worker waiting for Kafka... {i}", flush=True)
            time.sleep(3)

    raise Exception("Kafka not available")


def process():
    c = get_consumer()

    print("Worker started listening...", flush=True)

    # DB connection
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB", flush=True)

    for message in c:
        data = message.value

        component = data.get("component_id")
        msg = data.get("message")

        # 🟢 STEP 1: Store EVERY signal in MongoDB (Data Lake)
        signals_collection.insert_one({
            "component_id": component,
            "message": msg,
            "timestamp": time.time()
        })

        # 🔥 Redis key (only track DOWN state)
        key = f"{component}_down"

        # =========================
        # 🔴 DOWN EVENT
        # =========================
        if msg == "down":

            if r.exists(key):
                print("Duplicate DOWN ignored:", data, flush=True)

            else:
                r.set(key, "active")

                cursor.execute(
                    "INSERT INTO incidents (component_id, message, status) VALUES (%s, %s, %s)",
                    (component, "down", "OPEN")
                )
                conn.commit()

                print("Incident OPENED:", data, flush=True)
                send_email(
                    "🚨 Incident OPEN",
                    f"{component} is DOWN"
                )


        # =========================
        # 🟢 UP EVENT
        # =========================
        elif msg == "up":

            if r.exists(key):
                r.delete(key)

                cursor.execute(
                    "UPDATE incidents SET status='RESOLVED' WHERE component_id=%s AND status='OPEN'",
                    (component,)
                )
                conn.commit()

                print("Incident RESOLVED:", data, flush=True)
                send_email(
                    "✅ Incident RESOLVED",
                    f"{component} is UP"
                )

            else:
                print("UP received but no active incident:", data, flush=True)


        # =========================
        # ❓ UNKNOWN EVENT
        # =========================
        else:
            print("Unknown message type:", data, flush=True)


if __name__ == "__main__":
    process()
