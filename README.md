# Cloud Observability & Automated Response Platform

Python-based simulation of an observability pipeline that:
- generates structured service logs
- detects rule-based and ML-based anomalies
- triggers alerts
- executes simulated remediation actions
- can be deployed to AWS EC2 using Terraform

This is a portfolio project focused on practical system design and operational workflows.

## Deployment Mode

- Local mode is the default and fully supported.
- AWS/EC2 deployment is optional and used for infrastructure demonstration.

## What It Does

### Log pipeline
- `src/generator.py` emits synthetic logs with timestamps, service, metrics, and event type.
- `src/processor.py` analyzes each log entry and raises alerts when rules or ML detection trigger.
- `src/alerts.py` enriches and prints alert payloads.
- `src/actions.py` runs simulated remediation actions based on alert type.

### Detection coverage
- High CPU utilization
- High memory utilization
- Potential brute-force attack (failed auth burst)
- High error rate (sliding time window)
- ML anomaly detection per service using Isolation Forest (`scikit-learn`)

## Repository Structure

```text
src/         Application code
tests/       Unit tests
infra/       Terraform + EC2 bootstrap template
docs/        Project planning and walkthrough notes
```

## Quick Start (Local)

### 1. Install dependencies

```bash
python3 -m pip install -r requirements-dev.txt
```

### 2. Run simulation

```bash
python3 src/main.py --duration 15
```

Optional runtime tuning:

```bash
python3 src/main.py --duration 30 --min-interval 0.05 --max-interval 0.2
```

### 3. Run tests

```bash
python3 -m pytest -q
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

- Add Slack/webhook alert sink
- Add persistent storage for alert history
- Add dashboard for trends and incident timeline
- Package app and deploy via container workflow

## Documentation
