import psycopg2
from psycopg2 import sql

class TrafficDatabase:
    def __init__(self):
        # Update these credentials to match your local PostgreSQL configuration
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="root",
            host="db",
            port="5432"
        )
        self.cursor = self.conn.cursor()

    def log_telemetry(self, step, junction_id, lane_id, veh_count, queue, phase, vip_flag):
        query = """
        INSERT INTO junction_telemetry 
        (timestamp_step, junction_id, incoming_lane, vehicle_count, queue_length, active_phase, vip_present)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        try:
            self.cursor.execute(query, (step, junction_id, lane_id, veh_count, queue, phase, vip_flag))
            self.conn.commit()
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to write telemetry: {e}")
            self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()