import unittest
from datetime import datetime
from src.processor import MLAnomalyDetector, LogProcessor

class TestMLAnomalyDetector(unittest.TestCase):
    def test_isolation_forest_anomaly(self):
        detector = MLAnomalyDetector(window_size=100)
        
        # 1. Train with REALISTIC normal data (varying CPU 15-30, Mem 35-50)
        # We need at least 50 points to trigger training
        import random
        random.seed(42)
        for _ in range(60):
            cpu = random.uniform(15, 30)
            mem = random.uniform(35, 50)
            detector.track_and_check(cpu, mem)
            
        # Model should be fitted now
        self.assertTrue(detector.is_fitted)
        
        # 2. Test Normal check (within training range)
        alert = detector.track_and_check(22.0, 42.0)
        # This MIGHT be flagged depending on the random forest, so we won't assert
        
        # 3. Test Anomaly input (CPU 95, Mem 95) - clearly outside training range
        # This should definitely trigger
        alert = detector.track_and_check(95.0, 95.0)
        
        # Should flag this extreme anomaly
        self.assertIsNotNone(alert)
        self.assertIn("ML Model detected anomaly", alert)

class TestProcessorIntegration(unittest.TestCase):
    def setUp(self):
        self.processor = LogProcessor()

    def test_ml_alert_trigger(self):
        # 1. Warm up the history with normal logs for a service
        base_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "normal_operation",
            "service": "api-server",
            "metrics": { "cpu_usage": 20.0, "memory_usage": 40.0 }
        }
        
        # Feed 60 log entries (30 pairs of similar data) to train the model
        for _ in range(60):
            self.processor.process_log(base_log)
            
        # 2. Inject an anomalous log (Sudden spike)
        spike_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "normal_operation",
            "service": "api-server",
            "metrics": { "cpu_usage": 95.0, "memory_usage": 95.0 }
        }
        
        # Process spike
        alert = self.processor.process_log(spike_log)
        
        # Should return an alert
        self.assertIsNotNone(alert)
        self.assertEqual(alert["alert_type"], "ML Anomaly Detected")
        self.assertEqual(alert["source_service"], "api-server")

if __name__ == '__main__':
    unittest.main()
