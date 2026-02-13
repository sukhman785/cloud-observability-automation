from src.alerts import AlertEngine


def test_trigger_alert_does_not_mutate_input_and_adds_metadata():
    engine = AlertEngine()
    original = {
        "timestamp": "2026-02-13T12:00:00",
        "alert_type": "High CPU Utilization",
        "severity": "CRITICAL",
        "description": "CPU usage at 95.0%",
        "source_service": "web-server",
        "source_trace_id": "trace-12345",
    }
    baseline = dict(original)

    enriched = engine.trigger_alert(original)

    assert original == baseline
    assert enriched is not original
    assert "alert_id" in enriched
    assert enriched["alert_id"].startswith("alert-")
    assert "alert_generated_at" in enriched


def test_trigger_alert_generates_unique_ids():
    engine = AlertEngine()
    payload = {
        "timestamp": "2026-02-13T12:00:00",
        "alert_type": "High Memory Utilization",
        "severity": "WARNING",
        "description": "Memory usage at 90.0%",
        "source_service": "web-server",
        "source_trace_id": "trace-12345",
    }

    first = engine.trigger_alert(payload)
    second = engine.trigger_alert(payload)

    assert first["alert_id"] != second["alert_id"]
