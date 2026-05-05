from kafka import KafkaConsumer
from db import get_connection
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
        key = f"{data['component_id']}_{data['message']}"

        if r.exists(key):
            print("Duplicate signal ignored:", data, flush=True)
        else:
            r.set(key, "active")

            # Insert into DB
            cursor.execute(
                "INSERT INTO incidents (component_id, message, status) VALUES (%s, %s, %s)",
                (data["component_id"], data["message"], "OPEN")
            )
            conn.commit()

            print("New incident stored in DB:", data, flush=True)


if __name__ == "__main__":
    process()
