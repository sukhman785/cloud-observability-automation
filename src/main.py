import time
import sys
import os
import random
import argparse

# Add src to path if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.generator import LogGenerator
from src.processor import LogProcessor
from src.alerts import AlertEngine
from src.actions import ActionAutomator

def main():
    parser = argparse.ArgumentParser(description="Cloud Observability Simulation")
    parser.add_argument("--duration", type=int, help="Duration to run simulation in seconds", default=None)
    parser.add_argument("--min-interval", type=float, help="Minimum delay between generated logs", default=0.1)
    parser.add_argument("--max-interval", type=float, help="Maximum delay between generated logs", default=0.5)
    args = parser.parse_args()
    min_interval = max(0.01, args.min_interval)
    max_interval = max(min_interval, args.max_interval)

    print("Initializing Cloud Observability & Automated Response Platform Simulation...")
    if args.duration:
        print(f"Running for {args.duration} seconds...")
    print("Press Ctrl+C to stop.")
    time.sleep(1)

    # Initialize components
    generator = LogGenerator()
    processor = LogProcessor()
    alert_engine = AlertEngine()
    automator = ActionAutomator()

    print("Components initialized. Starting log stream...\n")
    
    start_time = time.time()
    
    try:
        while True:
            # Check duration
            if args.duration and (time.time() - start_time > args.duration):
                print(f"\nTime limit of {args.duration}s reached.")
                break

            # 1. Generate Log
            log_entry = generator.generate_log()
            
            # Print log summary (simulating log ingestion)
            if log_entry['level'] in ['ERROR', 'CRITICAL', 'WARNING']:
                print(f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}")
            
            # 2. Process Log
            alert = processor.process_log(log_entry)
            
            # 3. Handle Alert if triggered
            if alert:
                enriched_alert = alert_engine.trigger_alert(alert)
                automator.execute_action(enriched_alert)
            
            # Simulate variable traffic
            time.sleep(random.uniform(min_interval, max_interval))

    except KeyboardInterrupt:
        print("\nStopping simulation...")
    
    print("Simulation stopped.")

if __name__ == "__main__":
    main()
