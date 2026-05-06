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
            create_tables(conn)
            return conn
        except:
            print("DB retry", i)
            time.sleep(3)

    raise Exception("DB failed")


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id SERIAL PRIMARY KEY,
        component_id TEXT,
        message TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rca (
        id SERIAL PRIMARY KEY,
        incident_id INT REFERENCES incidents(id),
        root_cause TEXT,
        fix TEXT,
        prevention TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP
    )
    """)

    conn.commit()
