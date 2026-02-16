# Cloud Observability & Automated Response Platform

Python-based simulation of an observability pipeline that:
- generates structured service logs
- detects rule-based and ML-based anomalies
- triggers alerts
- executes simulated remediation actions
- exposes API + realtime frontend dashboard for live visibility
- can be deployed to AWS EC2 using Terraform

This is a portfolio project focused on practical system design and operational workflows.

## Current Status

Implemented through **Phase 2**:
- SQLite persistence for logs and alerts
- FastAPI read APIs
- Realtime alert updates in the frontend via WebSocket
- Alert lifecycle actions from UI (`ACKNOWLEDGED`, `SUPPRESSED`)
- Automated tests for storage, processor, alerts, anomaly detection, and API behavior

## Deployment Mode

- Local mode is the default and fully supported.
- AWS/EC2 deployment is optional and used for infrastructure demonstration.

## What It Does

### Log pipeline
- `src/generator.py` emits synthetic logs with timestamps, service, metrics, and event type.
- `src/processor.py` analyzes each log entry and raises alerts when rules or ML detection trigger.
- `src/alerts.py` enriches and prints alert payloads.
- `src/actions.py` runs simulated remediation actions based on alert type.
- `src/storage.py` persists logs + alerts in SQLite.
- `src/api.py` serves dashboard data and alert lifecycle actions via FastAPI.

### Detection coverage
- High CPU utilization
- High memory utilization
- Potential brute-force attack (failed auth burst)
- High error rate (sliding time window)
- ML anomaly detection per service using Isolation Forest (`scikit-learn`)

## Repository Structure

```text
src/         Application code (simulation + API + persistence)
tests/       Unit tests
infra/       Terraform + EC2 bootstrap template
frontend/    React + Vite dashboard
docs/        Local planning notes (ignored in git)
```

## Quick Start (Local)

### 1. Install Python dependencies

```bash
python3 -m pip install -r requirements-dev.txt
```

### 2. Run simulation (terminal A)

```bash
python3 src/main.py --duration 120
```

Optional runtime tuning:

```bash
python3 src/main.py --duration 120 --min-interval 0.05 --max-interval 0.2
```

### 3. Run API (terminal B)

```bash
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run frontend (terminal C)

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

### 5. Run tests

```bash
python3 -m pytest -q
```

## Demo Flow

1. Start simulator, API, and frontend.
2. Open `http://localhost:5173`.
3. Watch the alert table update in near real time (WebSocket stream).
4. Use `Ack` on an `OPEN` alert and verify status changes to `ACKNOWLEDGED`.
5. Use `Suppress` and verify status changes to `SUPPRESSED`.
6. Confirm summary cards update (`Open`, `Acknowledged`, `Suppressed`).
7. Refresh browser and verify alert status persistence.

## API Endpoints

### Read endpoints
- `GET /health`
- `GET /alerts?limit=100`
- `GET /logs?limit=200`
- `GET /metrics/summary`

### Alert lifecycle actions
- `POST /alerts/{alert_id}/acknowledge`
- `POST /alerts/{alert_id}/suppress`

### Realtime stream
- `WS /ws/alerts`
  - `snapshot` frame on connect (latest alerts)
  - `delta` frame for newly inserted alerts

## Deploy to AWS (EC2 + Terraform)

```bash
cd infra
terraform init
terraform validate
terraform apply -var="ssh_allowed_cidr=<your_public_ip>/32"
terraform output ssh_command
```

To stream logs on the instance:

```bash
sudo journalctl -u cloud-observability -f
```

To tear down resources:

```bash
terraform destroy -auto-approve
```

## CI

GitHub Actions workflow: `.github/workflows/ci.yml`

Runs on push and pull request:
- Python tests (`pytest`)
- Terraform format check
- Terraform config validation

CI intentionally does not deploy infrastructure.

## Roadmap

- Phase 3: Docker Compose for one-command startup (`simulator + api + frontend`)
- Auth + RBAC
- Incident assignment workflows
