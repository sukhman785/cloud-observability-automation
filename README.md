# Cloud-AutoOps

Python-based simulation of an observability pipeline that:
- generates structured service logs
- detects rule-based and ML-based anomalies
- triggers alerts
- executes simulated remediation actions
- exposes API + realtime frontend dashboard for live visibility
- can be deployed to AWS EC2 using Terraform

This is a portfolio project focused on practical system design and operational workflows.

## Demo GIF

![Cloud Observability Platform Demo](demo/demo.gif)

## Current Status

Implemented through **Phase 3 foundation**:
- SQLite persistence for logs and alerts
- FastAPI read APIs
- Realtime alert updates in the frontend via WebSocket
- Alert lifecycle actions from UI (`ACKNOWLEDGED`, `SUPPRESSED`)
- Docker Compose one-command startup (`simulator + api + frontend`)
- Automated tests for storage, processor, alerts, anomaly detection, and API behavior

## Quick Start (One Command via Docker Compose)

### 1. Start all services

```bash
docker compose up --build
```

### 2. Open dashboard

- Frontend: `http://localhost:5173`
- API health: `http://localhost:8000/health`

### 3. Stop services

```bash
docker compose down
```

To remove containers + volume data:

```bash
docker compose down -v
```

## Environment Configuration

Copy `.env.example` to `.env` (optional), then adjust values:

```bash
API_PORT=8000
FRONTEND_PORT=5173
DB_PATH=/app/data/observability.db
```

## Manual Local Run (Without Docker)

### 1. Install Python dependencies

```bash
python3 -m pip install -r requirements-dev.txt
```

### 2. Run simulation (terminal A)

```bash
python3 src/main.py --duration 120
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

## Repository Structure

```text
src/         Application code (simulation + API + persistence)
tests/       Unit tests
infra/       Terraform + EC2 bootstrap template
frontend/    React + Vite dashboard
docs/        Local planning notes (ignored in git)
```

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

- Auth + RBAC
- Incident assignment workflows
