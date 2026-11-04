## Problem
<!-- What is wrong or missing, for whom. Link the issue, spec or ADR. -->

## Change
<!-- What this PR does and why this approach. One self-contained change; refactors go in their own PR. -->

## Risk areas
<!-- Money, auth/permissions, PII/KYC, migrations, integrations, performance. "None" is a valid answer. -->

## How it was tested
<!-- Commands run with results, test names, screenshots for UI. -->

## Deploy and rollback
- Migrations: <!-- none / list, backward compatible? -->
- Config / env keys: <!-- none / names only, never values -->
- Rollback: <!-- previous tag or steps -->

## Checklist (the Definition of Done, skill eng-delivery)
- [ ] Closes #<issue> and cites REQ-<nnn>
- [ ] Acceptance criteria met; tests added or updated and passing
- [ ] Security checklist done for auth, data, money or integration changes
- [ ] Deployed to UAT and smoke-tested (or: not deployable yet, why)
- [ ] Docs updated, or not needed (say why): requirements, test cases and traceability, user manual, runbook
- [ ] CHANGELOG `Unreleased` updated (if user-visible) and a progress-log entry added in `docs/progress/`
- [ ] No secrets, personal data or debug output in the diff
- [ ] Labels set (drive the release notes categories)
