import psycopg2
import time

def get_connection():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                host="db",
                database="ims",
                user="ims",
                password="ims"
            )
            print("Connected to DB", flush=True)
            return conn
        except Exception as e:
            print(f"DB not ready... {i}", flush=True)
            time.sleep(3)

    raise Exception("DB connection failed")
