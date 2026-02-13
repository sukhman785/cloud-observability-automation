# Contributing

## Scope

This repository is a portfolio project. Contributions should improve:
- correctness
- readability
- reproducibility
- operational safety

## Development Setup

```bash
python3 -m pip install -r requirements-dev.txt
```

## Local Validation Before PR

Run these before opening a pull request:

```bash
python3 -m pytest -q
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra validate
```

## Coding Guidelines

- Keep changes focused and small.
- Prefer explicit, readable logic over clever shortcuts.
- Add or update tests for behavior changes.
- Do not commit generated artifacts or sensitive files:
  - `infra/*.pem`
  - `infra/terraform.tfstate*`
  - `.terraform/`

## Pull Requests

- Use the PR template.
- Explain what changed and why.
- Call out any risk areas and manual verification steps.

## Deployment Policy

- CI validates only; it does not deploy to AWS.
- Infrastructure deployment is manual with Terraform.
