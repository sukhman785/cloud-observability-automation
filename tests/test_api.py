from fastapi import HTTPException

import src.api as api
from src.storage import Storage


def _temp_storage(tmp_path):
    return Storage(db_path=str(tmp_path / "api-test.db"))


def test_health_endpoint_returns_healthy():
    payload = api.health()
    assert payload["status"] in {"healthy", "unhealthy"}


def test_alerts_endpoint_shape(tmp_path, monkeypatch):
    storage = _temp_storage(tmp_path)
    monkeypatch.setattr(api, "storage", storage)

    payload = api.get_alerts(limit=5)
    assert isinstance(payload.get("items"), list)


def test_metrics_summary_endpoint_shape(tmp_path, monkeypatch):
    storage = _temp_storage(tmp_path)
    monkeypatch.setattr(api, "storage", storage)

    payload = api.get_metrics_summary()
    assert "total_alerts" in payload
    assert "critical_alerts" in payload
    assert "open_alerts" in payload
    assert "acknowledged_alerts" in payload
    assert "suppressed_alerts" in payload
    assert "top_service_by_alerts" in payload
    assert "alerts_over_time" in payload


def test_acknowledge_and_suppress_actions(tmp_path, monkeypatch):
    storage = _temp_storage(tmp_path)
    monkeypatch.setattr(api, "storage", storage)

    storage.insert_alert(
        {
            "alert_id": "alert-api-1",
            "timestamp": "2026-02-16T13:00:01",
            "alert_generated_at": "2026-02-16T13:00:01",
            "alert_type": "High Memory Utilization",
            "severity": "WARNING",
            "description": "Memory spike",
            "source_service": "database",
            "source_trace_id": "trace-77",
        }
    )

    ack_payload = api.acknowledge_alert("alert-api-1")
    suppress_payload = api.suppress_alert("alert-api-1")

    assert ack_payload["item"]["status"] == "ACKNOWLEDGED"
    assert suppress_payload["item"]["status"] == "SUPPRESSED"


def test_acknowledge_missing_alert_raises_404(tmp_path, monkeypatch):
    storage = _temp_storage(tmp_path)
    monkeypatch.setattr(api, "storage", storage)

    try:
        api.acknowledge_alert("does-not-exist")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected HTTPException for missing alert")
