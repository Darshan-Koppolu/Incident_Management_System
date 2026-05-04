from kafka import KafkaProducer
import json
import time

producer = None

def get_producer():
    global producer

    if producer is not None:
        return producer

    for i in range(10):  # retry 10 times
        try:
            producer = KafkaProducer(
                bootstrap_servers="broker:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Connected to Kafka")
            return producer
        except Exception as e:
            print(f"Kafka not ready, retrying... {i}")
            time.sleep(3)

    raise Exception("Kafka not available after retries")


def send_signal(data):
    p = get_producer()
    p.send("signals", data)
    print("Sent to Kafka:", data)
