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
            create_tables(conn)
            return conn

        except Exception as e:
            print(f"DB not ready... {i}", flush=True)
            time.sleep(3)

    raise Exception("DB connection failed")


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            component_id TEXT,
            message TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    print("Incidents table ready", flush=True)
