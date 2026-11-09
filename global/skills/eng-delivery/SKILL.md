---
name: eng-delivery
description: Runs client delivery — scope, estimates in ranges, plans (Scrum, Kanban or ERP phases), Definition of Done, RAID log, status reports, change requests, UAT, go-live and handoff. Use when estimating or planning a project; when reporting status; when scope changes; or when preparing UAT, go-live or handover.
---

# Delivery and project management

Goal: predictable delivery the client can see, with no surprises on scope, time, money or risk. Methods are tools: pick the one that fits the work. Claude drafts scopes, estimates, plans, logs, reports and change requests from evidence. It never invents dates, prices or commitments; commercial terms come from the user, and anything sent to a client is the user's action.

## Core rules
- Before building, write scope in and out, assumptions and acceptance criteria into `docs/project-brief.md`.
- Estimates are ranges with their assumptions, covering testing, UAT, migration, training and deployment as well as code.
- On fixed scope, every change request is logged and approved in writing by the client before work starts.
- Dates, prices and commitments come from the user; anything sent to a client is the user's action.
- `docs/raid.md` stays current, and bad news is reported the day it is known, with options.
- Work counts as done only against this skill's Definition of Done.

## 1. Scope and agreement (before any build)
- Client goal and success criteria in their words; **in scope / out of scope** lists; assumptions; what we need from the client (data, access, decisions, vendor credentials, sign-offs) with dates.
- Deliverables, each with acceptance criteria and a named sign-off owner.
- Commercial frame (fixed scope or time and material) decides how change is handled; if unknown, ask.
- Environments and who deploys where (UAT, production); data follows the three tiers in skill `eng-testing` ([test-types.md](../eng-testing/test-types.md)): synthetic by default, masked in UAT, restricted real data only for approved rehearsals.
- The contract allows AI-assisted development (code and data processed through Claude); if it is silent or forbids it, the user settles that with the client first.
- Record it in `docs/project-brief.md` (template in `~/.claude/eng-os/templates/docs/`) and the project CLAUDE.md "What" and "Domain risk" lines.

## 2. Estimate in ranges
- Break the work into vertical slices of at most 2–3 days each (skill `eng-design`).
- Three-point estimate per slice: optimistic O, most likely M, pessimistic P. Expected E = (O + 4M + P) / 6, spread SD = (P − O) / 6. For a total, add the variances (SD²) and take the square root; never add the SDs.
- Quote a range with its assumptions, never a single number as a commitment. Early estimates can be off by 4x either way (cone of uncertainty); the range narrows only as decisions are made, so re-estimate at each milestone. Show contingency openly, never as hidden padding.
- Include the work that is not coding: data migration and rehearsals, vendor sandbox integration, UAT rounds and fixes, training, documentation, deployment, hypercare. Lending and KYC features need time for compliance review.

## 3. Choose the delivery method
| Work | Method | Practice |
|---|---|---|
| ERP implementation (ERPNext, Odoo) | the phase-by-phase ERP method in [erp-implementation.md](erp-implementation.md): discover, fit-to-standard, build, data migration, UAT and training, cutover, hypercare | each phase ends with a written sign-off |
| Fixed-scope build | staged plan (PRINCE2 7 ideas: manage by stages, manage by exception) | phases with exit criteria and sign-off; tolerances on time and cost; escalate as soon as a tolerance will be breached |
| Evolving product (platform, app with a roadmap) | Scrum (2020 guide) | Product Goal; sprints of a month or less, each with a Sprint Goal; ordered backlog owned by the product owner; Definition of Done. A Sprint Goal is not a contract |
| Support, AMC, bug and change streams | Kanban (guide v2025.5) | visualise the workflow, limit work in progress, act on items that are ageing; measure WIP, throughput, cycle time and work item age; forecast from throughput |

**Definition of Done (default; projects may tighten)**: acceptance criteria met; tests added and passing; diff reviewed (skill `eng-review`); security checklist for sensitive changes; deployed to UAT and smoke-tested; documents updated in the same PR (requirements, test cases and traceability, user manual, runbook, CHANGELOG, as skill `eng-docs` lists); a dated progress-log entry; the PR closes its issue and cites the requirement id. This list is the single definition: the PR template and the engineering policy point here.

## 4. Track: RAID log and status
- `docs/raid.md`, reviewed weekly. One table each for Risks, Assumptions, Issues and Dependencies: id, description, owner, date raised, priority, status, next action. A failed assumption becomes a risk or an issue.
- Weekly status (short, evidence first):
```
Project — week of YYYY-MM-DD — overall: green | amber | red
Done (with evidence): …
Next: …
Needs from client (owner, by when): …
Decisions needed: …
Risks/issues changed: …
Schedule / scope / budget vs baseline: …
```
- Use the PMBOK 8 performance domains as a quick health check: governance, scope, schedule, finance, stakeholders, resources, risk.
- Bad news travels the day it is known, with options and a recommendation. Engineering continuity lives in `docs/progress.md` (global instructions).

## Tracking work
One issue per piece of work, from the issue forms in `~/.claude/eng-os/templates/github/`; standard labels (`templates/github/labels.md`); one milestone per release. PRs close their issue (`Fixes #123`) and cite the requirement (`REQ-nnn`). The board or tracker the client sees is the project's choice (GitHub Projects, Jira, others); record it in the project CLAUDE.md.

## 5. Change control (fixed scope)
1. Log every request, however small: who asked, what, why, date.
2. Assess the impact on scope, time, cost and risk, and what else moves; offer options.
3. Get written client approval (signed change request or confirming email) before building.
4. Update the baseline plan, estimate, acceptance criteria and RAID log.
5. Build, test and release as normal; close the request with a reference in the release notes.
Never absorb scope creep silently and never start unapproved billable work. Claude drafts the change request; the user sends it.

## 6. UAT, go-live and handoff
- **UAT plan**: scenarios traced to acceptance criteria, masked test data, testers and dates, defect severity and triage rules, exit criteria, and written sign-off.
- **Go-live**: the release checklist in skill `eng-ship`, plus a data migration rehearsal with record counts and totals reconciled, a rollback decision point, user training, support contacts, and a hypercare window.
- **Handoff pack**: architecture and runbook, admin and user guides, release notes, known issues, support or warranty terms. Credentials are handed over through a password manager or secret store, never in chat or plain email.
- **Close**: a short blameless lessons-learned note; fold improvements back into templates and skills.

Sources (checked 2026-11-04): scrumguides.org (2020 edition, current); kanbanguides.org (v2025.5); PMI PMBOK Guide 8th edition (domains per PMI's announcement; PMI pages refuse automated access); PRINCE2 7 (PeopleCert); agilemanifesto.org; three-point estimation and the cone of uncertainty (Boehm, McConnell).
