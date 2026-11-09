---
name: eng-ship
description: Ships and runs software — CI/CD, releases and changelogs, GitHub and Actions security, deploys and rollback, migrations on shared data, servers and AWS, monitoring, backups and incidents. Use when deploying or releasing; when changing a pipeline; when migrating shared data; or when setting up servers, monitoring or backups.
---

# Shipping and operations

## Core rules
- Production changes need the user's explicit approval in this session, after a dry run on UAT.
- Before a production deploy: backup verified, migrations tried on a copy, rollback written down, health checks named.
- Where the stack builds an artifact, build it once and promote that same artifact; environments differ only in configuration.
- Take the branch-to-environment mapping from the project CLAUDE.md before deploying anything.
- Check configuration by key names; secret values are never printed.
- After a deploy, smoke-test the critical paths, watch error rates and record the release with its rollback target.

## Environments and promotion
- Flow: local → UAT/staging → production. Build once, promote the same artifact; environments differ only in config (env vars / secret store).
- Know the branch → environment mapping from the project CLAUDE.md before touching anything; if it is missing, find it (CI config, deploy scripts) and record it there.
- Production changes need explicit user approval in this session; prefer doing the dry run on UAT first.

## CI gates (minimum for a repo you own)
lint + format check → type check (where applicable) → unit/integration tests → dependency audit → secret scan → build → SBOM for delivered artifacts. Merge is blocked on red. Cache dependencies; keep the pipeline under ~10 minutes; fail fast on the cheapest checks first. Supply-chain targets (SLSA, pinned actions, least-privilege tokens): skill `eng-security`, [standards.md](../eng-security/standards.md).

## Versions, commits, PRs, changelogs and release notes
Read [releases.md](releases.md) when versioning, tagging, writing a CHANGELOG or release notes, setting up PR templates, or choosing a commit/branch convention.

## GitHub repository and Actions security
Read [github.md](github.md) when creating or hardening a repo, writing or reviewing workflows, or setting branch rulesets, CODEOWNERS, Dependabot, secret scanning or cloud credentials for CI.

## Release checklist (before any production deploy)
1. What exactly changes (commits, migrations, config, infra) and the blast radius.
2. Backup taken and verified restorable for affected data (timestamp noted).
3. Migrations tested on a production-like copy; timing known; backward compatible with the currently running code.
4. Config/secrets present in the target environment (names checked, values never printed).
5. Rollback written down: previous artifact/tag, migration down or restore steps, who decides.
6. Health checks and the metrics/logs to watch for the first 30 minutes.
7. Communication: who is told, maintenance window if needed.
After deploy: smoke test the critical paths, watch error rates, then record the release (tag, CHANGELOG, release notes naming the rollback target).

### Red flags before a production change
| The thought | The rule |
|---|---|
| "It's only a one-line change on production" | Production stays read-only unless the user said otherwise in this session. Ask first. |
| "The backup is probably recent" | Check that it exists and restores into a scratch environment, never over production, before any destructive step. |
| "It worked on UAT, so production will be fine" | Production differs in data, config and load. Run the checklist anyway. |
| "The guard blocked it; I'll do it another way" | The block is the answer. Report it and let the user decide. |

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
- Reliability targets (Google SRE): an SLI is a measured number (success rate, p95 latency), the SLO is its target, the error budget is 1 − SLO. Alert on budget burn, not on every blip; when the budget is spent, reliability work comes before features.
- Delivery metrics (DORA, five since 2024): change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate. Use them to find bottlenecks, never as individual targets.

## Backups and recovery
Automated, encrypted, off-site, retention defined, and a restore test on a schedule (an untested backup is not a backup). Document RPO/RTO per system.

## Incidents
Stabilise first (rollback, feature flag off, scale), then diagnose. Preserve evidence (logs, DB snapshots) before cleanup. Regulated clients have reporting clocks (CERT-In, RBI, DPDP Board): check [standards.md](../eng-security/standards.md) and tell the user at once.
Write a blameless postmortem (timeline, contributing causes, actions that fix the system, not the person) for: user-visible downtime or degradation, any data loss, a rollback or other manual intervention, slow resolution, or an incident monitoring failed to catch.

Sources (checked 2026-11-04): sre.google (SLO chapter, postmortem culture, error budget policy); dora.dev/guides/dora-metrics; 12factor.net.
