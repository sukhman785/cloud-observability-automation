## Summary

Describe what changed and why.

## Changes

- 

## Validation

Checklist:

- [ ] `python3 -m pytest -q`
- [ ] `terraform -chdir=infra fmt -check -recursive`
- [ ] `terraform -chdir=infra init -backend=false -input=false`
- [ ] `terraform -chdir=infra validate`

## Risk / Impact

- Affected areas:
- Potential regressions:
- Rollback plan:

## Notes

Any reviewer context, tradeoffs, or follow-ups.
