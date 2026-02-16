from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


VALID_STATUSES = {"OPEN", "ACKNOWLEDGED", "SUPPRESSED"}


class Storage:
    """SQLite persistence for simulation logs and alerts."""

    def __init__(self, db_path: str = "data/observability.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service TEXT NOT NULL,
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    trace_id TEXT,
                    source_ip TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    response_time_ms REAL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT,
                    timestamp TEXT NOT NULL,
                    alert_generated_at TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_service TEXT NOT NULL,
                    source_trace_id TEXT,
                    offending_ip TEXT,
                    status TEXT NOT NULL DEFAULT 'OPEN',
                    acknowledged_at TEXT,
                    suppressed_at TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._migrate_alerts_table(conn)
            conn.commit()

    def _migrate_alerts_table(self, conn: sqlite3.Connection) -> None:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(alerts)").fetchall()
        }

        if "status" not in columns:
            conn.execute("ALTER TABLE alerts ADD COLUMN status TEXT NOT NULL DEFAULT 'OPEN'")
        if "acknowledged_at" not in columns:
            conn.execute("ALTER TABLE alerts ADD COLUMN acknowledged_at TEXT")
        if "suppressed_at" not in columns:
            conn.execute("ALTER TABLE alerts ADD COLUMN suppressed_at TEXT")
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE alerts ADD COLUMN updated_at TEXT")
            conn.execute("UPDATE alerts SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")

    def insert_log(self, log_entry: Dict[str, Any]) -> None:
        metrics = log_entry.get("metrics", {})
        with self._lock:
            with self._conn() as conn:
                conn.execute(
                    """
                    INSERT INTO logs (
                        timestamp, service, level, event_type, message,
                        trace_id, source_ip, cpu_usage, memory_usage, response_time_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        log_entry.get("timestamp"),
                        log_entry.get("service", "unknown"),
                        log_entry.get("level", "INFO"),
                        log_entry.get("event_type", "unknown"),
                        log_entry.get("message", ""),
                        log_entry.get("trace_id"),
                        log_entry.get("source_ip"),
                        metrics.get("cpu_usage"),
                        metrics.get("memory_usage"),
                        metrics.get("response_time_ms"),
                    ),
                )
                conn.commit()

    def insert_alert(self, alert: Dict[str, Any]) -> None:
        with self._lock:
            with self._conn() as conn:
                conn.execute(
                    """
                    INSERT INTO alerts (
                        alert_id, timestamp, alert_generated_at, alert_type,
                        severity, description, source_service, source_trace_id,
                        offending_ip, status, acknowledged_at, suppressed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        alert.get("alert_id"),
                        alert.get("timestamp"),
                        alert.get("alert_generated_at"),
                        alert.get("alert_type", "Unknown"),
                        alert.get("severity", "INFO"),
                        alert.get("description", ""),
                        alert.get("source_service", "unknown"),
                        alert.get("source_trace_id"),
                        alert.get("offending_ip"),
                        "OPEN",
                        None,
                        None,
                    ),
                )
                conn.commit()

    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, alert_id, timestamp, alert_generated_at, alert_type, severity,
                       description, source_service, source_trace_id, offending_ip,
                       status, acknowledged_at, suppressed_at, updated_at
                FROM alerts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_alerts_since_id(self, after_id: int, limit: int = 200) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, alert_id, timestamp, alert_generated_at, alert_type, severity,
                       description, source_service, source_trace_id, offending_ip,
                       status, acknowledged_at, suppressed_at, updated_at
                FROM alerts
                WHERE id > ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (after_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_latest_alert_row_id(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COALESCE(MAX(id), 0) AS max_id FROM alerts").fetchone()
        return int(row["max_id"])

    def update_alert_status(self, alert_id: str, status: str) -> Optional[Dict[str, Any]]:
        status = status.upper()
        if status not in VALID_STATUSES:
            raise ValueError(f"Unsupported status: {status}")

        with self._lock:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT id, status FROM alerts WHERE alert_id = ? ORDER BY id DESC LIMIT 1",
                    (alert_id,),
                ).fetchone()
                if not row:
                    return None

                db_id = int(row["id"])
                acknowledged_at = "CURRENT_TIMESTAMP" if status == "ACKNOWLEDGED" else "acknowledged_at"
                suppressed_at = "CURRENT_TIMESTAMP" if status == "SUPPRESSED" else "suppressed_at"

                conn.execute(
                    f"""
                    UPDATE alerts
                    SET status = ?,
                        acknowledged_at = {acknowledged_at},
                        suppressed_at = {suppressed_at},
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, db_id),
                )
                conn.commit()

                updated = conn.execute(
                    """
                    SELECT id, alert_id, timestamp, alert_generated_at, alert_type, severity,
                           description, source_service, source_trace_id, offending_ip,
                           status, acknowledged_at, suppressed_at, updated_at
                    FROM alerts
                    WHERE id = ?
                    """,
                    (db_id,),
                ).fetchone()

        return dict(updated) if updated else None

    def get_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 2000))
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT timestamp, service, level, event_type, message, trace_id, source_ip,
                       cpu_usage, memory_usage, response_time_ms
                FROM logs
                ORDER BY datetime(timestamp) DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        logs: List[Dict[str, Any]] = []
        for row in rows:
            logs.append(
                {
                    "timestamp": row["timestamp"],
                    "service": row["service"],
                    "level": row["level"],
                    "event_type": row["event_type"],
                    "message": row["message"],
                    "trace_id": row["trace_id"],
                    "source_ip": row["source_ip"],
                    "metrics": {
                        "cpu_usage": row["cpu_usage"],
                        "memory_usage": row["memory_usage"],
                        "response_time_ms": row["response_time_ms"],
                    },
                }
            )
        return logs

    def get_metrics_summary(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            critical_alerts = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE severity = 'CRITICAL'"
            ).fetchone()[0]
            open_alerts = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE status = 'OPEN'"
            ).fetchone()[0]
            acknowledged_alerts = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE status = 'ACKNOWLEDGED'"
            ).fetchone()[0]
            suppressed_alerts = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE status = 'SUPPRESSED'"
            ).fetchone()[0]
            top_service_row = conn.execute(
                """
                SELECT source_service, COUNT(*) AS alert_count
                FROM alerts
                GROUP BY source_service
                ORDER BY alert_count DESC
                LIMIT 1
                """
            ).fetchone()
            alerts_over_time = conn.execute(
                """
                SELECT substr(timestamp, 1, 16) AS minute_bucket, COUNT(*) AS count
                FROM alerts
                GROUP BY minute_bucket
                ORDER BY minute_bucket DESC
                LIMIT 20
                """
            ).fetchall()

        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "open_alerts": open_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "suppressed_alerts": suppressed_alerts,
            "top_service_by_alerts": {
                "service": top_service_row["source_service"] if top_service_row else None,
                "count": top_service_row["alert_count"] if top_service_row else 0,
            },
            "alerts_over_time": [
                {"timestamp": row["minute_bucket"], "count": row["count"]}
                for row in reversed(alerts_over_time)
            ],
        }

    def healthcheck(self) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False
