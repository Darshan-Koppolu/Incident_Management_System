from kafka import KafkaConsumer
import json
import time

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
                group_id="ims-group"   # IMPORTANT
            )
            print("Worker connected to Kafka", flush=True)
            return consumer
        except Exception as e:
            print(f"Worker waiting for Kafka... {i}", flush=True)
            time.sleep(3)

    raise Exception("Kafka not available")


def process():
    c = get_consumer()

    print("Worker started listening...", flush=True)

    for message in c:
        print("Received from Kafka:", message.value, flush=True)


if __name__ == "__main__":
    process()
