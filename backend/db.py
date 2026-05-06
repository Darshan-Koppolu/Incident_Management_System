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

            create_tables(conn)  # 🔥 tables auto create

            return conn

        except Exception:
            print(f"DB not ready... {i}", flush=True)
            time.sleep(3)

    raise Exception("DB connection failed")


def create_tables(conn):
    cursor = conn.cursor()

    # ✅ INCIDENTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            component_id TEXT,
            message TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ✅ RCA TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rca (
            id SERIAL PRIMARY KEY,
            incident_id INT REFERENCES incidents(id),
            root_cause TEXT,
            fix TEXT,
            prevention TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP
        );
    """)

    conn.commit()

    print("Tables ready (incidents + rca)", flush=True)
