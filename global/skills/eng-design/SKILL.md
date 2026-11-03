---
name: eng-design
description: Architecture and design procedure for new features, systems, APIs, data models and technology choices. Use before building anything non-trivial, when requirements are vague, when choosing between designs or frameworks, or when writing a spec or ADR.
---

# Engineering design

Goal: the simplest design that meets the real requirements, with trade-offs made explicit. Scale effort to risk: a small feature gets a paragraph, a new system gets a written spec.

## 1. Requirements before solutions
Capture, in a few lines each:
- **Problem and users**: who needs what, and why now. The business outcome, not the feature list.
- **Functional scope**: in scope / explicitly out of scope.
- **Quality attributes** with numbers where possible: latency, throughput, data volume and growth, availability target, RPO/RTO, concurrency.
- **Constraints**: regulation (RBI, DPDP, GST), existing stack, budget, team skills, deadlines, client hosting.
- **Acceptance criteria**: observable checks that prove it works.
- **Open questions**: anything that would change the design. Ask the user only those that materially change it. Answer the rest from code, docs or sensible defaults, and record them as assumptions.

## 2. Understand the existing system
Read the current architecture, conventions, data model and integration points before proposing anything new. Reuse what exists; extend the framework's native mechanisms (Frappe doctypes and hooks, Odoo ORM, Next.js routing, CI3 MVC) before building custom plumbing.

## 3. Options and trade-offs
For any decision that is costly to reverse (data model, service boundary, framework, vendor, sync vs async), write 2–3 options:

| Option | Fit to requirements | Complexity / cost | Risk (security, ops, lock-in) | Reversibility |

Pick one and give the reason in one or two sentences. Prefer boring, proven technology and fewer moving parts. A new service, queue, cache or dependency must earn its place with a requirement it serves.

## 4. Design checklist (cover what applies)
- **Boundaries**: modules or bounded contexts with one owner each; dependencies point inward toward the domain; no circular imports. Use DDD vocabulary where the domain is rich (lending, accounting); plain layering where it is CRUD.
- **Data**: entities, ownership and invariants; constraints in the database (NOT NULL, FK, UNIQUE, CHECK), not only in code; indexes for real query patterns; money as DECIMAL or integer minor units; UTC timestamps; soft delete only with a reason; tenant/company key on every multi-tenant table.
- **State**: explicit state machines for lifecycles (application, loan, payment, document); transitions validated server-side and recorded.
- **APIs**: resource-oriented, versioned when external; consistent error shape (`code`, `message`, `details`); pagination on lists; idempotency keys on create/payment endpoints; contract-first (OpenAPI) for anything consumed by another team or app.
- **Integrations**: adapter interface per vendor (swappable); timeouts, bounded retries with backoff and jitter, circuit breaking; sandbox mode; reconciliation job against the provider's source of truth.
- **Consistency**: transactions around invariants; outbox pattern or idempotent consumers for cross-system events; never a dual write without reconciliation.
- **Security by design**: threat model the new surface (skill `eng-security`); authorization model decided up front.
- **Operability**: logs, metrics, alerts, feature flags, migrations and rollback considered in the design, not bolted on.
- **Scalability**: design for 10x current load, not 1000x; name the first bottleneck and how you would detect it.
- **Failure modes**: what happens when each dependency is slow, down or returns garbage.

## 5. Write it down
- Small change: plan in chat (files, approach, risks, verification).
- Significant change: `docs/specs/<feature>.md` with the sections above, plus a task breakdown into vertical slices that can each be verified.
- Decision that is costly to reverse: an ADR at `docs/adr/NNNN-title.md`:

```
# NNNN. Title
Status: proposed | accepted | superseded by NNNN    Date: YYYY-MM-DD
Context: forces and constraints.
Decision: what we chose.
Alternatives: what we rejected and why.
Consequences: what gets easier, harder, and what we must now watch.
```

## 6. Then build
Implement in thin vertical slices (schema, logic, API, UI, test). Each slice is independently verifiable. Keep the system working between slices. Revisit the design if a slice disproves an assumption; don't silently drift from it.
