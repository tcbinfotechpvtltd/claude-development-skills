# <Project name>
<!-- Project instructions. Complements ~/.claude/CLAUDE.md (global eng-os standards); may add or tighten rules, never relax the global security floor. Keep under ~120 lines; move long procedures to docs/ and link them. -->

**What**: <one line: product, client, business purpose>
**Domain risk**: <e.g. moves money / stores KYC / internal tool>
**Required skills**: <e.g. eng-security, fintech-lending, frappe-erpnext> (load before changing code here)

## Stack
- <language + version>, <framework + version>, <DB + version>, <key libs>
- Runs at: <local URL/port>; services needed: <redis, workers, ...>

## Commands
<!-- Give the quiet form (`pytest -q --tb=short`, `npx vitest run --reporter=dot`, `npm ci --silent`): sessions copy these commands as written. -->
| Purpose | Command |
|---|---|
| Setup | `<...>` |
| Run locally | `<...>` |
| Tests | `<...>` |
| Lint / format / typecheck | `<...>` |
| Build | `<...>` |

## Architecture map
- `<dir>/` — <responsibility>
- `<dir>/` — <responsibility>
- Entry points: <HTTP routes / CLI / cron / webhooks>
- External integrations: <vendor → adapter file>

## Invariants (never break)
- <e.g. ledger lines are append-only; corrections are reversals>
- <e.g. every query filters by company/tenant>

## Environments and delivery
| Branch | Environment | Deploys via | Notes |
|---|---|---|---|
| `<branch>` | UAT | <CI job / script> | |
| `<branch>` | Production | <...> | read-only unless the user says otherwise |
- Repo access: <push allowed? PR into which branch? pull before change?>

## Conventions
- <naming, error handling, API style, commit/branch conventions specific to this repo>

## Gotchas
- <non-obvious things learned the hard way, with date>

## Documentation and status
- Documentation index: `docs/README.md` (requirements, architecture, test plan and cases, user manual, runbook). Keep it current with every change (skill `eng-docs`).
- Status and the dated log of all work: `docs/progress.md`. Tracking: <GitHub Issues / Jira board link>.
