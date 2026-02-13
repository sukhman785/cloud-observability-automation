from datetime import datetime
from typing import Dict, Any, Optional
from collections import deque
from sklearn.ensemble import IsolationForest

class MLAnomalyDetector:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_buffer = deque(maxlen=window_size) # Store [cpu, memory] samples
        self.model = IsolationForest(contamination="auto", random_state=42)
        self.is_fitted = False
        self.training_interval = 20
        self.sample_count = 0

    def track_and_check(self, cpu: float, memory: float) -> Optional[str]:
        """
        Tracks the metrics and returns a description if it's an anomaly.
        Returns None if normal or not enough data.
        """
        sample = [cpu, memory]
        self.data_buffer.append(sample)
        self.sample_count += 1

        # Train model periodically once we have enough data
        if len(self.data_buffer) >= 50 and (self.sample_count % self.training_interval == 0 or not self.is_fitted):
            self.model.fit(list(self.data_buffer))
            self.is_fitted = True

        if not self.is_fitted:
            return None

        # Predict: -1 is anomaly, 1 is normal
        prediction = self.model.predict([sample])[0]
        
        if prediction == -1:
            # We can also get the anomaly score (lower is more anomalous)
            score = self.model.decision_function([sample])[0]
            return f"ML Model detected anomaly (Score: {score:.2f}) [CPU: {cpu:.1f}%, Mem: {memory:.1f}%]"
            
        return None

class LogProcessor:
    def __init__(self):
        self.auth_failures = deque()  # Store timestamps of failures
        self.error_window = deque()   # Store timestamps of errors
        self.total_window = deque()   # Store timestamps of all logs
        
        # Configuration
        self.auth_failure_threshold = 5
        self.auth_failure_window_sec = 60
        self.error_rate_threshold = 0.2   # Alert at >= 20% errors
        self.error_rate_window_sec = 60
        self.error_rate_min_samples = 10
        self.error_rate_alert_active = False

        # Phase 3: Intelligence Layer (Scikit-Learn)
        # Store a separate detector for each service to learn its specific pattern
        self.service_detectors: Dict[str, MLAnomalyDetector] = {}

    def process_log(self, log_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes a log entry and returns an Alert dictionary if a rule is triggered.
        Returns None if no alert is triggered.
        """
        timestamp = datetime.fromisoformat(log_entry["timestamp"])
        event_type = log_entry.get("event_type")
        metrics = log_entry.get("metrics", {})
        service = log_entry.get("service", "unknown")
        error_events = {"connection_timeout", "database_error"}
        pending_alert = None

        # Track events for a true sliding-window error-rate rule.
        self.total_window.append(timestamp)
        self._clean_window(self.total_window, self.error_rate_window_sec, timestamp)
        if event_type in error_events:
            self.error_window.append(timestamp)
        self._clean_window(self.error_window, self.error_rate_window_sec, timestamp)

        # Rule 1: High Resource Utilization (Immediate Trigger)
        if event_type == "cpu_utilization_spike":
            cpu = metrics.get("cpu_usage", 0)
            if cpu > 80.0:
                pending_alert = self._create_alert("High CPU Utilization", "CRITICAL", f"CPU usage at {cpu:.2f}%", log_entry)

        if event_type == "memory_utilization_spike":
            mem = metrics.get("memory_usage", 0)
            if mem > 80.0:
                pending_alert = self._create_alert("High Memory Utilization", "WARNING", f"Memory usage at {mem:.2f}%", log_entry)

        # Phase 3: Machine Learning Anomaly Detection (Isolation Forest)
        # We need both CPU and Memory for the model. Fill defaults if missing.
        if "cpu_usage" in metrics or "memory_usage" in metrics:
            cpu_val = metrics.get("cpu_usage", 20.0)    # Default to nominal 20%
            mem_val = metrics.get("memory_usage", 40.0) # Default to nominal 40%
            
            if service not in self.service_detectors:
                self.service_detectors[service] = MLAnomalyDetector(window_size=100)
            
            anomaly_desc = self.service_detectors[service].track_and_check(cpu_val, mem_val)
            
            if anomaly_desc:
                 if not pending_alert: 
                     pending_alert = self._create_alert(
                         "ML Anomaly Detected",
                         "WARNING",
                         f"{anomaly_desc} for {service}",
                         log_entry
                     )

        # Rule 2: Brute Force Detection (Frequency based)
        if event_type == "auth_failure":
            self._clean_window(self.auth_failures, self.auth_failure_window_sec, timestamp)
            self.auth_failures.append(timestamp)
            
            if len(self.auth_failures) >= self.auth_failure_threshold:
                # Reset to avoid spamming alerts for the same burst
                self.auth_failures.clear() 
                pending_alert = self._create_alert(
                    "Potential Brute Force Attack",
                    "CRITICAL",
                    f"{self.auth_failure_threshold} failed login attempts in {self.auth_failure_window_sec}s",
                    log_entry,
                    extra_fields={"offending_ip": log_entry.get("source_ip")},
                )

        # Rule 3: High Error Rate (actual percentage over sliding window)
        total_count = len(self.total_window)
        error_count = len(self.error_window)
        if total_count >= self.error_rate_min_samples:
            error_rate = error_count / total_count
            if error_rate >= self.error_rate_threshold:
                if not self.error_rate_alert_active and pending_alert is None:
                    self.error_rate_alert_active = True
                    return self._create_alert(
                        "High Error Rate",
                        "ERROR",
                        f"Error rate {error_rate:.2%} over last {total_count} logs in {self.error_rate_window_sec}s",
                        log_entry,
                    )
                self.error_rate_alert_active = True
            else:
                self.error_rate_alert_active = False

        return pending_alert

    def _clean_window(self, window: deque, max_age_seconds: int, current_time: datetime):
        """Removes old timestamps from the window."""
        while window and (current_time - window[0]).total_seconds() > max_age_seconds:
            window.popleft()

    def _create_alert(
        self,
        title: str,
        severity: str,
        description: str,
        source_log: Dict[str, Any],
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        alert = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": title,
            "severity": severity,
            "description": description,
            "source_service": source_log.get("service"),
            "source_trace_id": source_log.get("trace_id")
        }
        if extra_fields:
            alert.update(extra_fields)
        return alert
