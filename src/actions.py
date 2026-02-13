from typing import Dict, Any
import time

class ActionAutomator:
    def __init__(self):
        pass

    def execute_action(self, alert: Dict[str, Any]):
        """
        Determines and executes the appropriate automated response based on the alert.
        """
        alert_type = alert.get("alert_type")
        service = alert.get("source_service", "unknown-service")

        if alert_type == "High CPU Utilization":
            self._scale_up_service(service)
        elif alert_type == "Potential Brute Force Attack":
            self._block_ip_address(alert.get("offending_ip", "192.168.1.x"))
        elif alert_type == "High Error Rate":
            self._restart_service(service)
        elif alert_type == "High Memory Utilization":
            self._dump_heap_and_restart(service)
        else:
            self._notify_admin(alert)

    def _scale_up_service(self, service: str):
        print(f">>> AUTO-REMEDIATION: Scaling up ASG for {service} to +1 instance...")
        time.sleep(0.5)
        print(f">>> SUCCESS: {service} scaled up.")

    def _block_ip_address(self, ip: str):
        print(f">>> AUTO-REMEDIATION: Blocking malicious IP {ip} in WAF...")
        time.sleep(0.5)
        print(f">>> SUCCESS: IP {ip} blocked.")

    def _restart_service(self, service: str):
        print(f">>> AUTO-REMEDIATION: Restarting {service} to clear transient errors...")
        time.sleep(1.0)
        print(f">>> SUCCESS: {service} restarted.")

    def _dump_heap_and_restart(self, service: str):
        print(f">>> AUTO-REMEDIATION: Capturing heap dump for {service} and restarting...")
        time.sleep(1.0)
        print(f">>> SUCCESS: Heap dump saved to S3. Service restarted.")

    def _notify_admin(self, alert: Dict[str, Any]):
        print(f">>> ACTION: Simulating generic notification to generic channel for {alert['alert_type']}.")
