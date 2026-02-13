from datetime import datetime, timedelta

from src.processor import LogProcessor


def _log(ts: datetime, event_type: str, service: str = "web-server"):
    return {
        "timestamp": ts.isoformat(),
        "service": service,
        "event_type": event_type,
        "metrics": {"cpu_usage": 25.0, "memory_usage": 35.0},
        "trace_id": "trace-1",
    }


def test_high_cpu_spike_triggers_critical_alert():
    processor = LogProcessor()
    ts = datetime(2026, 2, 13, 12, 0, 0)
    entry = _log(ts, "cpu_utilization_spike")
    entry["metrics"]["cpu_usage"] = 95.0

    alert = processor.process_log(entry)

    assert alert is not None
    assert alert["alert_type"] == "High CPU Utilization"
    assert alert["severity"] == "CRITICAL"


def test_brute_force_alert_triggers_within_time_window():
    processor = LogProcessor()
    base = datetime(2026, 2, 13, 12, 0, 0)

    alert = None
    for i in range(5):
        entry = _log(base + timedelta(seconds=i * 10), "auth_failure")
        entry["source_ip"] = "203.0.113.8"
        alert = processor.process_log(entry)

    assert alert is not None
    assert alert["alert_type"] == "Potential Brute Force Attack"
    assert alert["offending_ip"] == "203.0.113.8"


def test_error_rate_alert_uses_sliding_window_not_consecutive_errors():
    processor = LogProcessor()
    base = datetime(2026, 2, 13, 12, 0, 0)

    events = [
        "connection_timeout",
        "normal_operation",
        "database_error",
        "normal_operation",
        "normal_operation",
        "normal_operation",
        "normal_operation",
        "normal_operation",
        "normal_operation",
        "normal_operation",
    ]

    alerts = []
    for i, event in enumerate(events):
        maybe_alert = processor.process_log(_log(base + timedelta(seconds=i), event))
        if maybe_alert:
            alerts.append(maybe_alert)

    assert any(a["alert_type"] == "High Error Rate" for a in alerts)


def test_error_rate_alert_does_not_fire_before_minimum_samples():
    processor = LogProcessor()
    base = datetime(2026, 2, 13, 12, 0, 0)

    events = [
        "connection_timeout",
        "normal_operation",
        "database_error",
        "normal_operation",
        "normal_operation",
    ]

    alerts = []
    for i, event in enumerate(events):
        maybe_alert = processor.process_log(_log(base + timedelta(seconds=i), event))
        if maybe_alert:
            alerts.append(maybe_alert)

    assert not any(a["alert_type"] == "High Error Rate" for a in alerts)
