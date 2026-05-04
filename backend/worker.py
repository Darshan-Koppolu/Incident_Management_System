from kafka import KafkaConsumer
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

    for message in c:
        data = message.value
        key = f"{data['component_id']}_{data['message']}"

        # 🔥 CHECK REDIS
        if r.exists(key):
            print("Duplicate signal ignored:", data, flush=True)
        else:
            # first time
            r.set(key, "active")
            print("New incident created:", data, flush=True)


if __name__ == "__main__":
    process()
