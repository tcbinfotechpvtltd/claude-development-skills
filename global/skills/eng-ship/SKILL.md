---
name: eng-ship
description: Delivery and operations procedure covering CI/CD pipelines, environments, releases and deploys, rollback, database migrations on shared data, server and cloud infrastructure (VPS, AWS), observability, backups and incident handling. Use when setting up or changing pipelines, deploying, migrating data, provisioning or hardening servers, or adding monitoring.
---

# Shipping and operations

## Environments and promotion
- Flow: local → UAT/staging → production. Build once, promote the same artifact; environments differ only in config (env vars / secret store).
- Know the branch → environment mapping from the project CLAUDE.md before touching anything; if it is missing, find it (CI config, deploy scripts) and record it there.
- Production changes need explicit user approval in this session; prefer doing the dry run on UAT first.

## CI gates (minimum for a repo you own)
lint + format check → type check (where applicable) → unit/integration tests → dependency audit → secret scan → build. Merge is blocked on red. Cache dependencies; keep the pipeline under ~10 minutes; fail fast on the cheapest checks first.

## Release checklist (before any production deploy)
1. What exactly changes (commits, migrations, config, infra) and the blast radius.
2. Backup taken and verified restorable for affected data (timestamp noted).
3. Migrations tested on a production-like copy; timing known; backward compatible with the currently running code.
4. Config/secrets present in the target environment (names checked, values never printed).
5. Rollback written down: previous artifact/tag, migration down or restore steps, who decides.
6. Health checks and the metrics/logs to watch for the first 30 minutes.
7. Communication: who is told, maintenance window if needed.
After deploy: smoke test the critical paths, watch error rates, then record the release (tag, notes).

## Deploy patterns
- Prefer automated, repeatable deploys (CI job or script in the repo) over hand-typed SSH sequences. Every manual step goes into the repo runbook.
- Zero-downtime where practical: blue/green or rolling restarts; run migrations before code only when they are backward compatible.
- Frappe: `bench --site <site> migrate` after `bench update`/pull with a backup first; build assets; restart workers. Odoo: `-u module` on a copy first.

## Infrastructure
- Infrastructure as code or scripted provisioning; no undocumented console clicks.
- Least-privilege IAM (per-service roles, no root keys, MFA); security groups default-deny; private subnets for databases.
- Cost awareness: right-size instances, set billing alerts, tag resources. Provisioning paid resources needs user approval.
- Server hardening baseline: skill `eng-security`, [stacks.md](../eng-security/stacks.md) "Linux servers".

## Observability
- Structured logs (JSON) with request id, user id (not PII), and outcome; no secrets, OTPs, full PAN/Aadhaar or bank numbers.
- Error tracking (Sentry or equivalent) with release tagging.
- Metrics: RED (rate, errors, duration) per endpoint; queue depth and job failures; business signals (failed disbursals, webhook failures, KYC vendor errors).
- Alerts are actionable: each has an owner and a runbook line. Uptime checks on public endpoints and certificate expiry.

## Backups and recovery
Automated, encrypted, off-site, retention defined, and a restore test on a schedule (an untested backup is not a backup). Document RPO/RTO per system.

## Incidents
Stabilise first (rollback, feature flag off, scale), then diagnose. Preserve evidence (logs, DB snapshots) before cleanup. Afterwards: short blameless write-up with timeline, root cause, and the guard that prevents recurrence.
