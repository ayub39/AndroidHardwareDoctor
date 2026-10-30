import os
import sys
import sqlite3
import time
import uuid
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DIR


class ServiceDatabase:
    def __init__(self, db_path=None):
        if not db_path:
            db_path = os.path.join(APP_DIR, "data", "service_records.db")

        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, timeout=10.0)

    def _init_db(self):
        with self._lock:
            conn = self._get_conn()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS service_tickets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticket_no TEXT UNIQUE,
                            created_at TEXT,
                            customer_name TEXT,
                            customer_phone TEXT,
                            device_model TEXT,
                            condition_type TEXT,
                            complaint TEXT,
                            diagnostic_summary TEXT,
                            suspected_ic TEXT,
                            estimated_cost TEXT,
                            status TEXT,
                            technician_notes TEXT
                        )
                    """)
            finally:
                conn.close()

    def add_ticket(
        self,
        customer_name: str,
        customer_phone: str,
        device_model: str,
        condition_type: str,
        complaint: str,
        diagnostic_summary: str = "",
        suspected_ic: str = "",
        estimated_cost: str = "",
        status: str = "MASUK"
    ) -> str:
        ticket_no = f"SRV-{int(time.time())}-{uuid.uuid4().hex[:4].upper()}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._lock:
            conn = self._get_conn()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO service_tickets (
                            ticket_no, created_at, customer_name, customer_phone,
                            device_model, condition_type, complaint, diagnostic_summary,
                            suspected_ic, estimated_cost, status, technician_notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticket_no, created_at, customer_name, customer_phone,
                        device_model, condition_type, complaint, diagnostic_summary,
                        suspected_ic, estimated_cost, status, ""
                    ))
            finally:
                conn.close()
        return ticket_no

    def get_all_tickets(self, filter_status: str = None) -> list:
        with self._lock:
            conn = self._get_conn()
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if filter_status and filter_status != "SEMUA":
                    cursor.execute("SELECT * FROM service_tickets WHERE status = ? ORDER BY id DESC", (filter_status,))
                else:
                    cursor.execute("SELECT * FROM service_tickets ORDER BY id DESC")
                return [dict(r) for r in cursor.fetchall()]
            finally:
                conn.close()

    def search_tickets(self, query: str) -> list:
        q = f"%{query}%"
        with self._lock:
            conn = self._get_conn()
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM service_tickets 
                    WHERE ticket_no LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ? OR device_model LIKE ?
                    ORDER BY id DESC
                """, (q, q, q, q))
                return [dict(r) for r in cursor.fetchall()]
            finally:
                conn.close()

    def update_status(self, ticket_no: str, new_status: str):
        with self._lock:
            conn = self._get_conn()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE service_tickets SET status = ? WHERE ticket_no = ?", (new_status, ticket_no))
            finally:
                conn.close()

    def delete_ticket(self, ticket_no: str):
        with self._lock:
            conn = self._get_conn()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM service_tickets WHERE ticket_no = ?", (ticket_no,))
            finally:
                conn.close()
