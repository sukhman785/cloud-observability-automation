from src.storage import Storage


def test_storage_inserts_and_reads(tmp_path):
    db_file = tmp_path / "test.db"
    storage = Storage(db_path=str(db_file))

    log_entry = {
        "timestamp": "2026-02-16T12:00:00",
        "service": "web-server",
        "level": "ERROR",
        "event_type": "connection_timeout",
        "message": "timeout",
        "trace_id": "trace-1",
        "source_ip": "10.0.1.8",
        "metrics": {
            "cpu_usage": 20.0,
            "memory_usage": 30.0,
            "response_time_ms": 6000.0,
        },
    }
    alert = {
        "alert_id": "alert-1",
        "timestamp": "2026-02-16T12:00:01",
        "alert_generated_at": "2026-02-16T12:00:01",
        "alert_type": "High Error Rate",
        "severity": "CRITICAL",
        "description": "Error rate exceeded",
        "source_service": "web-server",
        "source_trace_id": "trace-1",
    }

    storage.insert_log(log_entry)
    storage.insert_alert(alert)

    logs = storage.get_logs(limit=10)
    alerts = storage.get_alerts(limit=10)
    summary = storage.get_metrics_summary()

    assert len(logs) == 1
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "High Error Rate"
    assert alerts[0]["status"] == "OPEN"
    assert summary["total_alerts"] == 1
    assert summary["critical_alerts"] == 1
    assert summary["open_alerts"] == 1


def test_storage_alert_lifecycle_transitions(tmp_path):
    db_file = tmp_path / "test.db"
    storage = Storage(db_path=str(db_file))

    storage.insert_alert(
        {
            "alert_id": "alert-lifecycle",
            "timestamp": "2026-02-16T12:10:01",
            "alert_generated_at": "2026-02-16T12:10:01",
            "alert_type": "High CPU Utilization",
            "severity": "CRITICAL",
            "description": "CPU spike",
            "source_service": "web-server",
            "source_trace_id": "trace-9",
        }
    )

    acknowledged = storage.update_alert_status("alert-lifecycle", "ACKNOWLEDGED")
    suppressed = storage.update_alert_status("alert-lifecycle", "SUPPRESSED")
    summary = storage.get_metrics_summary()

    assert acknowledged is not None
    assert acknowledged["status"] == "ACKNOWLEDGED"
    assert acknowledged["acknowledged_at"] is not None

    assert suppressed is not None
    assert suppressed["status"] == "SUPPRESSED"
    assert suppressed["suppressed_at"] is not None

    assert summary["open_alerts"] == 0
    assert summary["acknowledged_alerts"] == 0
    assert summary["suppressed_alerts"] == 1
