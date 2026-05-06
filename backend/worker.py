from kafka import KafkaConsumer
from db import get_connection
from mongo import signals_collection
from email_service import send_email
import json
import time
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

def get_consumer():
    for i in range(10):
        try:
            consumer = KafkaConsumer(
                "signals",
                bootstrap_servers="broker:9092",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                group_id="ims-group"
            )
            print("Connected to Kafka")
            return consumer
        except:
            print(f"Waiting Kafka {i}")
            time.sleep(3)

    raise Exception("Kafka failed")


def process():
    consumer = get_consumer()

    conn = get_connection()
    cursor = conn.cursor()

    print("Worker running...")

    for msg in consumer:
        data = msg.value

        component = data["component_id"]
        message = data["message"]

        # Store raw signal
        signals_collection.insert_one({
            "component_id": component,
            "message": message,
            "timestamp": time.time()
        })

        key = f"{component}_down"

        if message == "down":

            if r.exists(key):
                print("Duplicate DOWN ignored")

            else:
                r.set(key, "1", ex=60)

                cursor.execute(
                    "INSERT INTO incidents (component_id, message, status) VALUES (%s,%s,%s)",
                    (component, "down", "OPEN")
                )
                conn.commit()

                send_email("🚨 Incident OPEN", f"{component} DOWN")

        elif message == "up":

            if r.exists(key):
                r.delete(key)

                cursor.execute(
                    "UPDATE incidents SET status='RESOLVED' WHERE component_id=%s AND status='OPEN'",
                    (component,)
                )
                conn.commit()

                send_email("✅ Incident RESOLVED", f"{component} UP")

            else:
                print("No active incident")

if __name__ == "__main__":
    process()
