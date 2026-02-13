import time
import random
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(Enum):
    NORMAL = "normal_operation"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    TIMEOUT = "connection_timeout"
    DATABASE_ERROR = "database_error"
    CPU_SPIKE = "cpu_utilization_spike"
    MEMORY_SPIKE = "memory_utilization_spike"

class LogGenerator:
    def __init__(self, output_file: str = None):
        self.output_file = output_file
        # Setup basic logging to console, and optionally to file
        handlers = [logging.StreamHandler()]
        if output_file:
            handlers.append(logging.FileHandler(output_file))
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger("SimulatedLogger")

    def generate_log(self) -> Dict[str, Any]:
        """Generates a single simulated log entry."""
        weights = [0.7, 0.1, 0.05, 0.05, 0.05, 0.025, 0.025]
        event_type = random.choices(list(EventType), weights=weights)[0]
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": random.choice(["web-server", "auth-service", "database", "analytics-engine"]),
            "level": self._get_level_for_event(event_type),
            "event_type": event_type.value,
            "message": self._get_message_for_event(event_type),
            "metrics": self._get_metrics_for_event(event_type),
            "trace_id": f"trace-{random.randint(10000, 99999)}",
            "source_ip": self._get_source_ip_for_event(event_type),
        }
        
        return log_entry

    def _get_level_for_event(self, event_type: EventType) -> str:
        if event_type in [EventType.NORMAL, EventType.AUTH_SUCCESS]:
            return LogLevel.INFO.value
        elif event_type in [EventType.AUTH_FAILURE, EventType.CPU_SPIKE, EventType.MEMORY_SPIKE]:
            return LogLevel.WARNING.value
        elif event_type in [EventType.TIMEOUT, EventType.DATABASE_ERROR]:
            return LogLevel.ERROR.value
        return LogLevel.INFO.value

    def _get_message_for_event(self, event_type: EventType) -> str:
        messages = {
            EventType.NORMAL: "Processed request successfully",
            EventType.AUTH_SUCCESS: "User authentication successful",
            EventType.AUTH_FAILURE: "Authentication failed: Invalid credentials",
            EventType.TIMEOUT: "Upstream service request timed out after 5000ms",
            EventType.DATABASE_ERROR: "Connection to primary database failed",
            EventType.CPU_SPIKE: "High CPU utilization detected",
            EventType.MEMORY_SPIKE: "High Memory utilization detected"
        }
        return messages.get(event_type, "Unknown event")

    def _get_metrics_for_event(self, event_type: EventType) -> Dict[str, float]:
        metrics = {}
        if event_type == EventType.CPU_SPIKE:
            metrics["cpu_usage"] = random.uniform(85.0, 99.9)
        elif event_type == EventType.MEMORY_SPIKE:
            metrics["memory_usage"] = random.uniform(85.0, 99.9)
        else:
            metrics["cpu_usage"] = random.uniform(10.0, 40.0)
            metrics["memory_usage"] = random.uniform(20.0, 50.0)
            
        metrics["response_time_ms"] = random.uniform(10, 200) if event_type != EventType.TIMEOUT else random.uniform(5000, 10000)
        return metrics

    def _get_source_ip_for_event(self, event_type: EventType) -> str:
        if event_type in [EventType.AUTH_FAILURE, EventType.AUTH_SUCCESS]:
            return f"203.0.113.{random.randint(1, 254)}"
        return f"10.0.1.{random.randint(1, 254)}"

    def start_stream(self, interval: float = 1.0):
        """Starts generating logs continuously."""
        try:
            while True:
                log_entry = self.generate_log()
                # Simulate JSON structured logging
                self.logger.info(json.dumps(log_entry))
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nLog generation stopped.")

if __name__ == "__main__":
    generator = LogGenerator()
    generator.start_stream(interval=0.5)
