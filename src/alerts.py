from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

class AlertEngine:
    def __init__(self):
        pass

    def trigger_alert(self, alert_data: Dict[str, Any]):
        """
        Receives an alert and 'sends' it (prints to console/file).
        """
        # Copy input to avoid mutating caller-owned state.
        enriched_alert = dict(alert_data)
        enriched_alert["alert_id"] = f"alert-{uuid4().hex}"
        enriched_alert["alert_generated_at"] = datetime.now().isoformat()
        
        # In a real system, this would push to PagerDuty/Slack
        self._log_alert(enriched_alert)
        return enriched_alert

    def _log_alert(self, alert: Dict[str, Any]):
        print(f"\n[!!! ALERT TRIGGERED !!!]")
        print(f"Severity: {alert['severity']}")
        print(f"Type:     {alert['alert_type']}")
        print(f"Message:  {alert['description']}")
        print(f"Service:  {alert['source_service']}")
        print(f"Timestamp:{alert['timestamp']}\n")
