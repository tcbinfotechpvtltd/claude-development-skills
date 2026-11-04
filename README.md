# eng-os: TCB Infotech's engineering system for Claude Code

Install it once and every Claude Code session on your machine works to TCB's engineering standards. It is security first, works from evidence, gets on with routine work by itself, asks before anything risky, and keeps token use low. It covers Frappe/ERPNext, Odoo, PHP CodeIgniter 3, Next.js, Flutter, Linux VPS/AWS and Indian digital lending.

**New here? Install it with [INSTALL.md](INSTALL.md)** (about 5 minutes), and read the [engineering policy](docs/ENGINEERING-POLICY.md). Rolling it out to everyone: [docs/COMPANY-ROLLOUT.md](docs/COMPANY-ROLLOUT.md). Changes: [CHANGELOG.md](CHANGELOG.md).

Contents: [What's inside](#whats-inside) · [What you get in each area](#what-you-get-in-each-area) (custom projects, ERPNext, Odoo, coding, testing, GitHub, DevOps, SDLC, project management, documentation, security, tokens) · [Why it is good](#why-it-is-good) · [Limits](#limits-honest) · [Technical reference](#technical-reference)

## At a glance
| | |
|---|---|
| Version | 0.7.0 |
| Works with | Claude Code desktop app and CLI. Verified on macOS with 2.1.309; Linux and WSL should work but have not been tested |
| Applies to | every project you open with Claude Code on your machine, automatically: nobody has to name a skill |
| Cost per session | about 3.4k tokens always loaded (instructions + skill list). Everything else loads only when a task needs it |
| Quality checks | 148 automated tests for the safety hooks, a 63-point health check, and a scored test in a real Claude session |
| Standards | 129 external standards, frameworks and tool versions, each confirmed on its official site and dated ([docs/SOURCES.md](docs/SOURCES.md)) |
| Undo | one command restores your previous Claude setup exactly |

## What's inside

### Global instructions
`global/CLAUDE.md` is installed as `~/.claude/CLAUDE.md` and read in every session. Eight short sections:
1. **Instruction priority**: the safety rules come first, then your request, then project rules. A project can add rules but never relax the safety floor.
2. **When Claude acts and when it asks**: it does routine, reversible work end to end. It asks before destructive, production, outward-facing, shared-infrastructure or legal/money decisions. Production is read-only unless you say otherwise.
3. **How to engineer**: understand before changing, fix root causes, make the smallest correct diff, keep compatibility, give every fix a test, and change approach after two failed attempts.
4. **Security floor**: secrets, authorization on every request, hostile input, signed webhooks, personal and KYC data, dependencies.
5. **Done means verified**: run it and show the evidence. Status is labelled implemented / tested / verified / not verified.
6. **Skill routing table**: which skill to load for which task. Description matching alone proved unreliable.
7. **Projects, git and continuity**: read project CLAUDE.md files, record project knowledge, branch and PR, commit under your own name with no Claude co-author lines, keep a progress file for long work.
8. **Token efficiency**: targeted reads, parallel tool calls, cheaper models for mechanical subagent work, one task per session.

### Thirteen skills (loaded only when the task needs them)
| Skill | Used for | What it brings |
|---|---|---|
| `eng-design` | features, systems, APIs, data models, tech choices | requirements before solutions, 2–3 options with trade-offs, a design checklist (data, state machines, APIs, integrations, consistency, failure modes), C4 diagrams, ADRs, Twelve-Factor, an AWS Well-Architected final pass |
| `eng-security` + `stacks.md` + `standards.md` | auth, input, uploads, secrets, PII/KYC, payments, new endpoints, dependencies, servers, audits | STRIDE threat model; controls for each OWASP Top 10:2025 category; NIST 800-63B-4 password and MFA rules; CERT-In logging; pitfalls for Frappe, CI3, Next.js, Odoo, Flutter and Linux; a map of which standard governs which work (ASVS 5.0, API, mobile, LLM and agentic AI, supply chain, CIS, PCI DSS, ISO 27001, NIST CSF) |
| `eng-testing` + `test-types.md`, `browser.md`, `tooling.md` | writing or fixing tests, debugging failures, flaky tests, checking UI in a browser | the minimum tests per change and a map of 25 test types; Claude checking its own UI changes in a real browser (built-in browser, Chrome, Playwright MCP, Chrome DevTools MCP); test pyramid, contract tests, fix-with-a-failing-test, root-cause debugging; tools per stack |
| `eng-review` + `coding-standards.md` | before a commit, PR or handoff; code reviews and audits | self-review checklist based on Google's engineering practices, independent subagent review, an "audit until dry" loop, severity rubric, report format; official style guide, formatter and linter per language |
| `eng-ship` + `releases.md`, `github.md` | CI/CD, deploys, releases, migrations on shared data, servers, monitoring, backups, incidents | CI gates, a production release checklist with rollback, SemVer, Conventional Commits, Keep a Changelog, GitHub release notes, GitHub rulesets, CODEOWNERS, Dependabot, secret scanning and Actions hardening, SLOs and error budgets, DORA metrics, backups, blameless postmortems |
| `frappe-erpnext` | Frappe, ERPNext, HRMS and custom apps, bench | site isolation, permission-safe APIs, DocType JSON and patches, bench workflows, v15/v16 gotchas |
| `odoo` | Odoo modules, views, reports, upgrades (versions 17 to 20) | official module layout and naming, breaking changes per version, access rights and record rules (`ir.access` in 20), controllers, QWeb reports, `odoo-bin` tests, migration scripts and the upgrade service, performance |
| `custom-apps` + `nextjs.md`, `flutter.md`, `php-ci3.md`, `python.md` | Next.js/React/Node, PHP CodeIgniter 3, Flutter and Python apps | supported runtime versions with end-of-life dates, architecture per stack (App Router data layer, Flutter MVVM, thin CI3 controllers), Next.js 16 upgrade traps, legacy CI3 risk, deploy shape |
| `eng-delivery` + `erp-implementation.md` | scoping, estimates, plans, status, change requests, ERP implementations, UAT, handoff | in/out-of-scope, three-point estimates in ranges, Scrum/Kanban/staged plans, the TCB ERP method (discover, fit-to-standard, build, data migration, UAT and training, cutover, hypercare), a Definition of Done that includes documents, issue tracking, RAID log, weekly status, change control, UAT, go-live and handoff |
| `eng-docs` | requirements, user manuals, test-case documents, runbooks, project history, handover | the document set every project keeps and when each is written and updated, requirement ids linking issues, PRs, tests and manual pages, append-only history, Diátaxis user manuals per role, writing rules, the bus-factor check |
| `fintech-lending` | anything that moves money, computes loan amounts or stores borrower data | money as decimals, append-only double-entry ledgers, loan state machines, disbursal gates, vendor adapters and webhooks, RBI Digital Lending Directions 2025, DPDP Rules 2025, RBI NBFC cyber and outsourcing directions |
| `eng-project-init` | a repo with no CLAUDE.md, or a stale one | builds a project CLAUDE.md from the repo: commands, architecture map, invariants, environments, gotchas |
| `eng-os-review` | monthly (a reminder appears) | measures token use and adherence, checks Claude Code changes, re-checks every cited standard, proposes improvements as a PR |

### How the right skills load without anyone asking
Nobody types a skill name. Four layers make the right skill load on its own:
1. **Project detection** (session start): eng-os recognises Frappe/ERPNext, Odoo, Next.js, Node, Flutter, CodeIgniter 3 and Python projects from their files, and lending work from the project CLAUDE.md, then names the matching skills. A git repo without a CLAUDE.md is offered `/eng-project-init`.
2. **Prompt routing** (every request): keywords in the request ("loan", "deploy", "failing test", "user manual", "estimate", "Odoo"...) name the matching skills. Each skill is named at most once per session (about 40 tokens), and it stays silent when nothing matches.
3. **Path rules** (whenever matching files are touched): short must-follow rules load and point to their skill.
4. **The global instructions** tell Claude to load whatever those layers name, plus a trigger table for everything else.

Hooks can name a skill but cannot force it to load, so layers 1–2 are strong prompts and layer 3 guarantees the essential rules arrive.

### Nine path-scoped rules
These load automatically when Claude touches matching files, even if no skill was invoked:
- `frappe-erpnext`: `hooks.py`, doctypes and patches (permission checks, parameterised SQL, Server Scripts off).
- `db-migrations`: migrations, `*.sql` and schema files (reversible and re-runnable, expand-then-contract, approval and a fresh backup before destructive changes).
- `ci-deploy`: CI workflows, Dockerfiles, compose, Terraform, nginx, Kubernetes (least-privilege tokens, actions pinned to a commit, approval gate on production deploys, non-root containers, written rollback).
- `odoo`: manifests, access files, views and reports (no core edits, access rules for every model, `sudo()` with a reason, migration scripts, neutralized copies).
- `nextjs`: routes, actions, proxy and config (authorization inside every action and handler, schema validation, a `server-only` data layer, no secrets in `NEXT_PUBLIC_*`).
- `flutter`: `pubspec.yaml` and `lib/` (no secrets in the app, secure token storage, minimal permissions, keep the state pattern).
- `php-ci3`: CodeIgniter 3 controllers, models, libraries, views and config (bound queries, escaped output, CSRF on, no committed keys).
- `tests`: test files (never weaken tests, deterministic, synthetic data, failing test first).
- `docs`: `docs/` and CHANGELOG (no secrets or real data, stable requirement ids, append-only log, TO CONFIRM for unconfirmed facts).

### Safety guard
A hook checks every Claude tool call in about 50 ms and costs no tokens:
- **Refuses** catastrophic actions, such as wiping a home or system folder, dumping the keychain, or commits with a Claude co-author trailer.
- **Asks you first** before force-pushes, pushes to `main`/`prod`/`uat`, `reset --hard`, deploys, `DROP`/`TRUNCATE`, state-changing SSH, printing `.env` files, sending email or messages, and ad changes that spend money.
- **Stays silent** for everything else.

The prompts appear even in bypass-permissions mode (verified). Details are in [section 3](#3-the-guard-deterministic-safety-layer).

### Session check
A start-of-session hook names the skills for the project (see above) and otherwise stays silent unless the monthly review is due, someone edited the installed files directly, or (checked at most once a week) a newer eng-os release has been published.

### Command-line tool (`bin/eng-os`)
`install` (backup, validation, rollback), `update` (latest release tag, tests, preview, then install), `verify` (health check), `test`, `status`, `backups`, `restore`, `usage` (token and tool metrics from your local transcripts), `eval` (scores a real session against test scenarios), `audit-done`.

### Templates
- `templates/project/`: the project `CLAUDE.md`, and `claude-settings.json` (the installed-check every project repo gets).
- `templates/docs/`: the project document set:
  - documentation index, requirements, glossary;
  - architecture (arc42), test plan with test cases and traceability;
  - user manual (Diátaxis) and What's new;
  - runbook, progress and history log, handover checklist.
- `templates/github/`: issue forms (bug, feature), standard labels, CODEOWNERS, `dependabot.yml`.
- `templates/release/`: `CHANGELOG.md`, GitHub `release.yml` and `pull_request_template.md`.

### Documentation
| File | What it holds |
|---|---|
| [INSTALL.md](INSTALL.md) | install, what changes on your machine, updating, undo, troubleshooting |
| [docs/ENGINEERING-POLICY.md](docs/ENGINEERING-POLICY.md) | what every TCB engineer commits to when working with Claude Code |
| [docs/COMPANY-ROLLOUT.md](docs/COMPANY-ROLLOUT.md) | putting eng-os on every machine: per-developer install, a plugin, organisation-managed settings |
| [docs/SOURCES.md](docs/SOURCES.md) | every external standard cited, with edition, date, link and when it was last checked |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | each requirement mapped to where it is implemented and how far it is proven |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | test and live-session evidence for every release |
| [docs/metrics.md](docs/metrics.md) | token and efficiency measurements over time |
| [CHANGELOG.md](CHANGELOG.md) | what changed in each version |

## What you get in each area
What changes in your Claude Code once eng-os is installed, area by area, and which part does it. A **skill** loads when the task matches. A **rule** loads by itself when Claude touches matching files. The **guard** checks every tool call.

### Custom-built projects (Next.js, PHP CodeIgniter 3, Flutter, Node, Python)
- **The `custom-apps` skill**: one short file per stack, so only the stack in hand is loaded.
- **Supported runtimes, with end-of-life dates.** An unsupported runtime is reported as a security finding:
  - Node.js 26 LTS (20 is end-of-life);
  - PHP 8.3 to 8.5, with **8.2's security support ending 2026-12-31**;
  - Python 3.11+;
  - Next.js 16.4 with React 19.3;
  - Flutter 3.47.
- **Next.js** (`nextjs.md`):
  - Server Components by default, and a server-only data layer that checks authorization and returns minimal data.
  - The Next.js 16 upgrade traps: async request APIs, `middleware` renamed `proxy`, Turbopack by default, `next lint` removed.
  - Cache Components rules, the official Server Action security guide, and the VPS deploy shape.
- **Flutter** (`flutter.md`):
  - The official MVVM architecture: views and view models; repositories and services.
  - Existing GetX apps keep their pattern unless an ADR says otherwise.
  - Flavors, signing keys outside git, and store financial-services policy checks for loan apps.
  - Testing on low-end devices.
- **CodeIgniter 3** (`php-ci3.md`):
  - Honest status: legacy, last release in 2022.
  - The PHP support deadlines, and when CodeIgniter 4 makes sense.
  - Thin controllers, models with bound queries, one library per vendor.
  - Characterisation tests before refactoring, and the coding style applied only to changed code.
- **Python services** (`python.md`):
  - `pyproject.toml`, lock files, Ruff and type hints.
  - Timeouts on every call, `Decimal` for money.
  - Scripts that run as `--dry-run` first, and jobs with locks and alerts.
- **Onboarding a repo**: `/eng-project-init` writes the project `CLAUDE.md` (commands, architecture map, invariants, environments, gotchas), so later sessions start with that context.
- **Design before code** for anything non-trivial (`eng-design`): requirements and options, then the data model, state machines, API conventions, vendor adapters and failure modes; specs in `docs/specs/`, decisions in `docs/adr/`.
- **Security for each stack** (`stacks.md`): authorization in every Next.js action and handler, CodeIgniter 3 CSRF and session hardening, Flutter secure storage and TLS, OWASP MASVS/MASTG for mobile.
- **Lending products** (`fintech-lending`): money, ledgers, loan lifecycles, disbursal gates, webhooks, RBI and DPDP rules, built as features with tests.

### ERPNext / Frappe projects
- **A rule that always applies** to `hooks.py`, doctypes and patches:
  - Every whitelisted method checks permission.
  - No `ignore_permissions` without a documented reason.
  - `frappe.db.sql` only with parameters; prefer `frappe.qb` or the permission-aware `frappe.get_list`.
  - Server Scripts stay disabled.
  - Schema changes only through DocType JSON plus idempotent patches.
  - Money with `flt()` at field precision.
- **The `frappe-erpnext` skill**:
  - Confirm bench, versions, site and port first. One isolated site per client (`bench --site <s> serve --port <p>`).
  - Respect "UI only" projects.
  - Customise only through a custom app (fixtures, `doc_events`, `override_doctype_class`); never edit `apps/frappe` or `apps/erpnext`.
  - Follow docstatus rules; idempotent background jobs; permission-aware reports.
  - Post accounting and stock only through documents; filter every query by company.
- **Testing**: `bench run-tests` on a dedicated test site, never a client site. After changes: migrate, build and clear the cache. Verify as a non-admin role.
- **Gotchas learned on TCB projects**: the v16 setup-wizard reload loop fix, realtime/socketio, Homebrew MariaDB authentication, `get_all` vs `get_list`, backing up `encryption_key`.
- **Security** (`stacks.md`):
  - Guest endpoints validated and rate-limited; Jinja `| safe` sanitised; KYC files private.
  - An Administrator and 2FA policy.
  - Server Scripts and System Console off in production, a lesson from a real ERPNext breach.
  - `site_config.json` never printed or committed.
- **Guard**: asks before `bench drop-site`, `reinstall` or `restore`, and before any state-changing command over SSH.

### Odoo projects
- **The `odoo` skill, version-aware for 17 to 20**:
  - Confirm the version and edition first.
  - Odoo 20 was released in September 2026, and 17.0 is now out of standard support, so flag it and plan the upgrade.
- **Module layout and naming from the official coding guidelines**: folders, file names, XML ids, import order, method prefixes, no manual commits, translations, manifest versions.
- **Breaking changes per version from the official ORM changelog**:
  - 17: `attrs` removed, `name_get` replaced.
  - 18: `<tree>` becomes `<list>`, new access-check methods.
  - 19: `read_group`, `_sql_constraints` and `type='json'` replaced, the `Domain` builder.
  - 20: `ir.access` replaces access lists and record rules.
- **Security**:
  - access rights and record rules (multi-company included) for every model, and `groups=` on sensitive fields;
  - public methods treated as RPC endpoints;
  - `sudo()` only with a written reason;
  - controller `auth` and CSRF rules, parameterised SQL and `Domain`, escaped QWeb.
- **Reports**: QWeb with an explicit paper format; check layout on the production server build.
- **Tests**:
  - `TransactionCase`, `HttpCase` with tours, and `Form`;
  - run with `odoo-bin -d <test_db> -u <module> --test-tags /<module> --stop-after-init` on a test database;
  - record rules proven as a non-admin user.
- **Upgrades**:
  - versioned `migrations/<version>/pre|post|end` scripts and `upgrade-util`;
  - `-u` on a neutralized copy first (`odoo-bin neutralize`, so the copy cannot email customers or call payment providers);
  - the official upgrade service or OCA OpenUpgrade, followed by a rehearsed production window.
- **Performance**: batch ORM calls, `_read_group`, `search_fetch`, prefetching, indexes (`btree_not_null`, `trigram`), precise `@api.depends`, the built-in profiler.
- **Production basics**: `proxy_mode`, `list_db = False`, master password, `dbfilter`, sized workers.
- The database-migration rule, the guard and all the general practice below also apply.

### Coding practices
Applied in every session (global instructions section 3 and `eng-review`):
- Understand before changing: read the code, tests, conventions and recent history. Reproduce a bug before fixing it, and fix the root cause.
- Non-trivial work starts with the goal, acceptance criteria, edge cases and a short plan with risks.
- Smallest correct diff in the existing style: no drive-by refactors, speculative abstractions or unrequested dependencies.
- Keep APIs, schemas, data and config backward compatible, or provide a migration path.
- Explicit error handling, no swallowed exceptions, no silent TODOs; comments explain why.
- After two failed attempts: stop, list hypotheses with evidence, and test the most likely deliberately.
- Every diff is self-reviewed against a checklist based on Google's engineering practices: design, complexity, correctness, scope, security, compatibility, quality, tests, operations. High-risk changes also get an independent review by a fresh subagent.
- **Style per language** (`coding-standards.md`). The repo's own config comes first, and only changed code is reformatted:
  - Python: PEP 8 with Ruff (Frappe repos use their own ruff config).
  - PHP: PER Coding Style 3.1, which replaces PSR-12, with PHP-CS-Fixer and PHP_CodeSniffer.
  - TypeScript: ESLint 10 flat config with typescript-eslint and Prettier.
  - Dart: Effective Dart with `flutter_lints`.
  - Universal rules apply too: clear names, small functions, pure business rules, no swallowed errors.

### Testing
From `eng-testing` and its three reference files:
- **The minimum per change** (`test-types.md`):
  - any code gets static checks and unit tests;
  - data access and permissions add integration tests with the denied cases;
  - endpoints add API tests;
  - UI changes add a browser check by Claude, plus end-to-end tests for key journeys;
  - money and KYC add golden, property-based and duplicate/concurrency tests;
  - migrations add rehearsal and reconciliation;
  - releases add the full regression suite, then a smoke test after the deploy.
- **A map of 25 test types**: what each catches, when to use it and how. It covers:
  - static, unit, component, integration, API, contract and end-to-end tests;
  - visual regression, Claude's browser check, exploratory, smoke, regression and acceptance/UAT;
  - accessibility, web performance, and load/stress/soak/spike;
  - security, property-based, fuzzing and mutation testing;
  - migration reconciliation, backup restore and DR drills, resilience (failing vendors), compatibility (browsers and devices), time and locale, production checks.
- **Claude checks its own UI changes in a real browser** (`browser.md`):
  - It uses the desktop app's built-in browser by default, Claude in Chrome only when you ask, and Playwright MCP or Chrome DevTools MCP in terminal sessions, pinned to a version and added only with your approval.
  - It reads the page, checks console and network errors, exercises the happy, error, empty and double-submit cases, and tests permissions as an allowed and a denied user.
  - It checks phone, tablet and desktop widths, dark mode, keyboard and axe accessibility, and Lighthouse.
  - It reports the evidence, then turns critical checks into Playwright tests.
  - Safety rules: local or UAT only, test data only, payments in test mode, page text treated as data.
- **Rules for good tests**:
  - risk-based selection and the test pyramid;
  - one behaviour per test, deterministic, with boundary cases (IST/UTC, month end, duplicates, concurrency);
  - a failing test first for every bug, and a structured debugging procedure;
  - tests never skipped or weakened to get green, and "tests pass" only with a real run.
- **Tools per stack** (`tooling.md`):
  - pytest; `bench run-tests`; Odoo `TransactionCase`/`HttpCase`.
  - PHPUnit matched to the app's PHP version.
  - Vitest or Jest with Playwright.
  - Flutter's `flutter test`, `integration_test` and golden tests.
- **Specialist tools** (`tooling.md`):
  - Playwright screenshot comparison for visual regression;
  - Hypothesis and fast-check for property-based testing;
  - Schemathesis for API fuzzing from an OpenAPI spec;
  - axe-core and Lighthouse CI;
  - k6 for load and Pact for contracts;
  - Semgrep, gitleaks, Trivy and ZAP for security;
  - Stryker, mutmut and Infection for mutation testing;
  - Faker for synthetic data.
- **Three data tiers** (one rule everywhere):
  - synthetic data for development, CI, docs, screenshots and Claude's browser checks;
  - masked data in UAT and training;
  - restricted real data only for approved, isolated migration rehearsals and restore drills, which Claude does not browse.
  - Load, fuzz and security scans run with vendors stubbed, never against production or vendor systems.

### GitHub and source control
- Branch and pull request; no commits straight to `main` or `prod`. Pull or rebase before editing shared repos.
- Commits under each developer's own name, with no Claude co-author lines (enforced by a setting and the guard).
- **Conventions** (`releases.md`):
  - Conventional Commits and Semantic Versioning.
  - Short-lived branches (about two days).
  - Small self-contained PRs: about 100 lines is good, about 1000 is too big. Refactors go in their own PR.
- **Ready-to-copy templates**: `pull_request_template.md`, `release.yml` (GitHub's automatic release notes, grouped by label) and `CHANGELOG.md` (Keep a Changelog).
- **Release procedure**: move Unreleased entries into a version, bump the version, add an annotated tag, and publish reviewed release notes that name the rollback target.
- **CI hygiene** (`ci-deploy` rule): least-privilege workflow tokens, third-party actions pinned to a commit, secrets only from the secret store, and manual approval before production deploys.
- **Repository baseline** (`github.md`):
  - rulesets on the default and release branches (PR required, approvals, code-owner review, status checks, no force pushes);
  - CODEOWNERS covering workflows and deploy files;
  - Dependabot alerts, security updates and `dependabot.yml`;
  - secret scanning and push protection (private repos need the paid Secret Protection add-on, otherwise gitleaks).
- **Actions hardening**:
  - third-party actions pinned to a full commit SHA (in March 2026 attackers moved the Trivy action's tags to credential-stealing code);
  - a read-only `GITHUB_TOKEN` by default and OIDC instead of stored cloud keys;
  - no untrusted input inline in scripts, `pull_request_target` avoided;
  - artifact attestations for releases.
- **The guard asks before**:
  - force-push, a push to a protected branch, deleting branches
  - `reset --hard` or `clean -f`
  - `gh pr merge`, repo deletion, releases and secrets changes

### DevOps and operations
- **Environments** (`eng-ship`): local → UAT → production, promoting one build. The branch-to-environment map is recorded per project. Production changes only with approval.
- **CI gates**: lint, type check, tests, dependency audit, secret scan, build, SBOM.
- **Release checklist** before every production deploy:
  - the blast radius
  - a verified backup
  - migrations tested on a production-like copy
  - config present in the target environment
  - a written rollback
  - health checks to watch
  - who is told
- **Deploys**: scripted from the repo, zero-downtime where practical, with Frappe and Odoo specifics.
- **Infrastructure**: as code, least-privilege IAM, default-deny security groups, databases in private subnets, cost alerts. Paid resources need approval.
- **Servers** (`stacks.md`):
  - SSH keys only, a firewall, unattended security updates, TLS.
  - CIS Benchmark Level 1 for Ubuntu 24.04, NGINX, Docker, MySQL/MariaDB and AWS accounts.
  - For Indian clients, logs kept 180 days in India and clocks synced to NIC/NPL time servers.
- **Observability**:
  - Structured logs without personal data, error tracking, rate/error/latency metrics per endpoint, business signals.
  - Actionable alerts.
  - SLOs with error budgets and DORA delivery metrics.
- **Backups and incidents**:
  - Backups with scheduled restore tests.
  - Incidents: stabilise first, preserve evidence, meet the reporting clocks (CERT-In 6 hours, DPDP, RBI), then a blameless postmortem.
- **Automatic rules**: `db-migrations` and `ci-deploy` load whenever migration, SQL, pipeline, Docker, Terraform, nginx or Kubernetes files are touched.
- **The guard asks before**:
  - state-changing SSH, deploys and infrastructure changes (`terraform`, `kubectl`, `helm`, `aws`, `gcloud`)
  - Docker volume deletion, `sudo`, crontab and launchd changes
  - scp/rsync uploads and writes to non-local databases

### SDLC from start to finish
| Phase | What Claude does | Where it comes from |
|---|---|---|
| Requirements | goal and users, scope in and out, quality targets with numbers, constraints (RBI, DPDP, GST), acceptance criteria; asks only the questions that change the design | `eng-design` |
| Design | options and trade-offs, design checklist, C4 diagrams, spec, ADR, Well-Architected final pass | `eng-design` |
| Build | thin vertical slices, each verifiable; smallest diff; security controls designed in | global instructions, `eng-design`, `eng-security` |
| Test | risk-based tests, failing test first for every bug | `eng-testing` |
| Review | self-review, independent review, audit until dry | `eng-review` |
| Release | version, changelog, release notes, tag | `eng-ship` (`releases.md`) |
| Deploy | release checklist, backup, rollback plan, smoke test | `eng-ship` |
| Operate | monitoring, SLOs, incident handling, postmortems | `eng-ship` |
| Improve | postmortem actions; monthly review of eng-os itself | `eng-ship`, `eng-os-review` |

For client due diligence, `standards.md` maps this to the secure-development standards clients ask about: NIST SSDF and OWASP SAMM.

### Project management
The `eng-delivery` skill adds the delivery discipline a consultancy needs. It complements a tracker such as Jira and does not replace one.
- **Scope before build**:
  - the client goal and success criteria, plus in-scope and out-of-scope lists;
  - assumptions, and what the client must provide by when;
  - deliverables, each with acceptance criteria and a named sign-off owner;
  - recorded in `docs/project-brief.md`.
- **Estimates in ranges**:
  - three-point estimates per slice of at most 2–3 days: E = (O + 4M + P) / 6, with variances added for totals;
  - the cone of uncertainty, so early numbers are ranges and get re-estimated at milestones;
  - visible contingency, and non-coding work counted: migration, UAT, training, hypercare.
- **The right method for the work**:
  - a staged plan with exit criteria and tolerances for fixed-scope ERP or build projects (PRINCE2 7 ideas);
  - Scrum (2020 guide) for evolving products;
  - Kanban (guide v2025.5) for support and AMC streams, with WIP, throughput, cycle time and work-item age.
- **A TCB Definition of Done**: acceptance criteria met, tests, review, security check, UAT smoke test, release notes, docs.
- **Tracking**:
  - a RAID log (`docs/raid.md`) reviewed weekly;
  - a weekly status template (done with evidence, next, client actions, decisions, risks, schedule, scope and budget against the baseline);
  - PMBOK 8's performance domains as a health check;
  - bad news raised the day it is known.
- **Change control for fixed scope**: log every request, assess the impact on scope, time, cost and risk, get written approval before building, then update the baseline. Scope creep is never absorbed silently.
- **UAT, go-live and handoff**:
  - a UAT plan with masked data and written sign-off;
  - a go-live checklist with a migration rehearsal and a rollback decision point;
  - a handoff pack, with credentials passed only through a password manager or secret store;
  - a lessons-learned note.
- **ERP implementations** (`erp-implementation.md`), phase by phase:
  - discover and plan with one client point of contact;
  - fit-to-standard workshops that sort every requirement as standard, configuration or customisation;
  - configuration before code, with weekly key-user demos;
  - data migration with mock loads and a finance-signed reconciliation;
  - UAT and training from the user manual;
  - a rehearsed cutover with a go/no-go meeting;
  - hypercare that ends on criteria, then the next phase.
  - Every phase ends in a written sign-off.
- **Tracking**: issue forms (bug, feature), standard labels and a milestone per release. Pull requests close their issue and cite the requirement id.
- Continuity and honesty from the global rules: `docs/progress.md` and evidence-based status. Claude never invents dates, prices or commitments, and anything sent to a client is your action.

### Documentation and project history
The `eng-docs` skill keeps every project understandable by someone new. If the developer left today, the next person could carry on from the repo alone.
- **The document set** (templates in `templates/docs/`, copied in by `/eng-project-init`):
  - requirements with numbered requirement ids and a change history, and a glossary;
  - architecture on the arc42 template, with ADRs;
  - a test plan with test cases, a requirement-to-test traceability matrix and a completion report per release;
  - a user manual per role in Diátaxis form (tutorials, how-to guides, reference, explanation) plus an admin guide and "What's new";
  - a runbook;
  - a project brief, a log of client decisions and a RAID log;
  - a progress status page plus a dated log of all work, one file per entry so parallel pull requests never conflict;
  - the CHANGELOG, release notes and a handover checklist (including vendor, domain and licence ownership).
- **When each document is written**:
  - requirements and glossary after discovery, confirmed by the client before building;
  - architecture and the test plan at design;
  - the user manual drafted before UAT;
  - everything relevant updated in the same pull request as each change (part of the Definition of Done and the PR checklist).
- **History you can audit**:
  - the progress log in `docs/progress/` (who, what, why, evidence, docs updated). It is append-only, except for redacting a leaked secret or personal data;
  - the requirement change history with change-request ids;
  - ADRs, superseded rather than edited;
  - the CHANGELOG per release, and git for the detail.
- **Writing rules**:
  - the Google and Microsoft style guides: second person, active voice, short numbered steps;
  - exact screen labels and glossary terms;
  - screenshots from UAT with synthetic data;
  - no secrets, ever.
  - Business facts are confirmed by the client, never invented; open items are marked **TO CONFIRM**.
- **The bus-factor check at every milestone**: a newcomer can set up, test and deploy to UAT from the README and runbook alone; every requirement has tests and a manual page; nothing lives only in one person's head.

### Security and compliance
- **A security floor in every session**: secrets, authorization, hostile input, webhooks, personal and KYC data, dependencies.
- **Controls** (`eng-security`): a control for each OWASP Top 10:2025 category, plus NIST 800-63B-4 password and MFA rules.
- **The governing standard for each job** (`standards.md`): ASVS levels, API, mobile, LLM and agent security, supply chain (SLSA, SBOM), CIS, PCI DSS, ISO 27001, NIST CSF.
- **Indian obligations**: CERT-In, the DPDP Rules and RBI's NBFC directions.
- **Secret protection by the guard**: it asks before printing `.env` and key files and before writing credential-looking values.
- **Honest claims**: Claude never calls anything "secure"; it reports what was checked and what risk remains.

### How it uses fewer tokens
Text that loads in every session is paid for in every session, so eng-os keeps that layer small and loads the rest only when a task needs it:

| Layer | When it is loaded | Approximate cost |
|---|---|---|
| Global instructions | every session | 2.1k tokens |
| Skill list (names and descriptions) | every session | 1.3k tokens |
| One skill's full text | only when the task needs it | 0.6–2.4k tokens |
| Reference files (per stack, standards, releases, GitHub, coding standards, test tooling) | only when a skill sends Claude to them | 0.6–1.5k tokens |
| Path rules | only when a matching file is touched | 0.25–0.3k tokens |
| Guard and session hooks | run outside the model | 0 (a short message only when they ask or warn) |

Working habits that cut waste (global instructions section 8):
- Search first (`grep`/`rg`), then read only the lines needed. Trim long output, and never dump lockfiles, logs or minified files.
- Don't re-read files already in context or repeat checks that already passed.
- Run independent tool calls in parallel, and chain dependent shell steps into one command.
- Use subagents only for broad searches, noisy output, parallel work or a fresh-eyes review. Give them a tight brief and a cheaper model (Haiku for lookups, Sonnet for mechanical work).
- One task per session. A long conversation carries its whole history into every turn, so start fresh for unrelated work.
- Prefer command-line tools over MCP connectors when they do the same job, take screenshots only as final proof, and lead replies with the result.

**Less re-exploration**: a project `CLAUDE.md` (from `/eng-project-init`) and `docs/progress.md` mean the next session starts from what earlier sessions learned.

**The evidence behind these levers**, from the 30 days before install on the maintainer's machine:
- Subagents used 40% of all input tokens, almost all on the most expensive model.
- 24% of file reads were repeats.
- A 24-skill pack listed in every session was used once in over 700 sessions.

`eng-os usage` shows your own numbers, and the monthly review tracks the trend. Not measured yet: the actual reduction after installing, which needs a few weeks of sessions.

**Outside eng-os**: most of a session's starting context (80–90k tokens on the maintainer's machine) is Claude Code's own system prompt, tool definitions, plugins and connectors. Switching off plugins and connectors you don't use, and `/effort medium` for routine work, cut that part.

## Why it is good
- **Safety is enforced, not hoped for.** Risky actions are stopped by a hook that runs on every tool call, not by a sentence the model might forget. 126 automated cases cover it, and it was verified live in bypass mode.
- **Built on current standards, with sources.** 129 standards, frameworks and tool versions are named with their edition and the date each was confirmed on its official site: OWASP, NIST, CIS, MITRE, CISA, SLSA, PCI, ISO, Google SRE and DORA, RBI, DPDP and CERT-In. Nothing is quoted from memory, and a health-check warning plus the monthly review keep them current.
- **Made for TCB's real work.** The stack pitfalls, lending rules and severity examples come from TCB projects, audits and incidents, not generic advice.
- **Cheap to run.** About 3.4k tokens per session. Detail lives in files that load only when needed. The 24-skill pack it replaced was used once in more than 700 sessions.
- **Honest results.** Claude must show evidence, label what is not verified, and never call anything "secure".
- **The same standards for everyone.** Each developer still commits under their own name and keeps their own personal instructions. Improvements come in as pull requests.
- **Safe to install and remove.** Every install that changes anything takes a backup first, validates before writing and rolls back on error. A restore gives back the exact previous setup. A broken settings file is refused, never overwritten.
- **Keeps itself up to date.** The monthly review, source-freshness check and drift detection flag what needs attention.
- **Private.** Nothing is sent anywhere; usage metrics come from transcripts on your own machine.

## Limits (honest)
- Instructions and skills guide the model; they cannot force it. Only the guard and permission settings are hard controls.
- The guard matches command patterns. A cleverly disguised command or a script it cannot see can get past it, so it is a safety net, not a sandbox.
- With nobody at the keyboard (`claude -p`, unattended sessions), an approval prompt either stops the work or waits for you.
- It does not make anyone's software or organisation "compliant". It raises the floor and makes gaps visible.
- On individual Claude plans, whether Anthropic may train on your sessions is each person's account setting. eng-os cannot enforce it, so the policy requires it off ([COMPANY-ROLLOUT.md](docs/COMPANY-ROLLOUT.md)).

Full list: [section 8](#8-limitations-what-claude-code-cannot-guarantee).

# Technical reference

## 1. Design principles
1. **Deterministic where it matters, instructions where judgment is needed.** Dangerous actions are gated by a hook, not by hoping the model remembers a sentence.
2. **Pay only for what is used.** Always-loaded text is limited to rules that apply to every turn. Procedures live in skills, which load on demand. Stack rules are path-scoped and load only when matching files are touched.
3. **One source of truth.** Nothing is edited live. The repo is installed with backup, validation and rollback.
4. **Built on evidence.** Each component exists because a measurement or a doc-verified capability justified it. Things that turned out unnecessary were removed (see the decisions log).

## 2. Architecture

| Layer | Live location | Loads | Approx. cost | Purpose |
|---|---|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md` | every session, re-read after compaction | ~2.0k tokens | priority order, approval gates, engineering behaviour, security floor, skill routing table, git and token rules |
| Skills (13) | `~/.claude/skills/<name>/SKILL.md` | listing always (~1.1k tokens); body only when invoked; reference files only when the body sends Claude to them | 0.6–1.5k tokens each when used | procedures: `eng-design`, `eng-security` (+`stacks.md`, `standards.md`), `eng-testing` (+`tooling.md`), `eng-review` (+`coding-standards.md`), `eng-ship` (+`releases.md`, `github.md`), `eng-delivery` (+`erp-implementation.md`), `eng-docs`, `frappe-erpnext`, `odoo`, `custom-apps` (+ one file per stack), `fintech-lending`, `eng-project-init`, `eng-os-review` |
| Standards register | repo `docs/SOURCES.md` | never in context | 0 | every external standard the skills cite, with edition, publication date, URL and the date it was last confirmed on the official site |
| Path-scoped rules (3) | `~/.claude/rules/*.md` | only when a matching file is read or edited | ~200–300 tokens each | must-follow invariants for Frappe code, DB migrations/SQL, CI/containers/infra |
| Guard hook | `~/.claude/eng-os/hooks/guard.py` (PreToolUse: Bash, file tools, `mcp__.*`) | every matching tool call, ~50 ms | 0 tokens unless it blocks | deny catastrophic actions; ask before destructive, irreversible, outward-facing, production and secret-exposing ones |
| Session hook | `~/.claude/eng-os/hooks/session_start.py` | session start | 0 tokens normally; one line when due | monthly self-audit reminder; warns if live files were edited outside an install |
| Settings keys | `~/.claude/settings.json` (merged, other keys untouched) | always | 0 | hook wiring, `attribution` off (commits under each developer's own identity), deny reading Claude's own OAuth file |
| Subagents | `~/.claude/agents/` (existing 4 kept) | when spawned | per run | `security-auditor`, `code-reviewer`, `test-engineer`, `web-performance-auditor` are used for fresh-context review; no new agents were needed |
| CLI + tests | `~/.claude/eng-os/bin`, `tests`, `templates` | never in context | 0 | install/verify/test/usage/eval/restore, project template |

**Always-loaded total added by eng-os: ~3.4k tokens** (CLAUDE.md ~2.1k plus skill listing ~1.3k, 13 skills). The installer also removed the ~1.7k-token listing of the 24 unused agent-skills and a SessionStart hook that ran in every session and injected nothing.

### Instruction hierarchy (conflict resolution)
1. Safety floor (approval gates + security floor in the global CLAUDE.md, enforced in part by the guard)
2. The user's explicit instruction in the current session
3. Project `CLAUDE.md` / `.claude/rules` (may tighten, never relax the floor)
4. Global CLAUDE.md defaults, then skills (procedures, not policy)

Material conflicts are followed at the higher level and reported in one line. The guard reads **only** global config (`~/.claude/eng-os/config.json`), so a project file can never switch a gate off.

### Why skills need a routing table
Across 700+ transcripts, the 24 previously installed generic skills were invoked by description **once**. Description matching alone is unreliable, so the global CLAUDE.md carries a 9-line trigger table, and project CLAUDE.md files name their required skills. Path-scoped rules handle the invariants that must apply without the model deciding to load anything.

## 3. The guard (deterministic safety layer)
Fail-open (a crash never blocks work; errors are logged to `~/.claude/eng-os/state/guard-errors.log`), Python 3.9-compatible, stdlib only, ~50 ms per call. 122 guard cases in `tests/guard_cases.json` plus 4 session-hook cases.

- **Deny** (the user can still run these by hand): wiping `/`, home or system dirs; `mkfs`/`dd` to disks; fork bombs; reading Claude's OAuth credentials or dumping the keychain; git commits carrying a `Co-Authored-By: Claude` trailer (your rule).
- **Ask** (approval prompt): force-push, direct push to protected branches (`main master prod production live uat release*`), `reset --hard`, `clean -f`, discarding changes, deleting branches; `gh pr merge`/repo delete/releases/secrets; DROP/TRUNCATE, UPDATE/DELETE without WHERE, writes to non-local databases; `bench drop-site/reinstall/restore`; docker volume deletion; terraform/kubectl/helm/aws/gcloud changes and deploys; package publishing; `sudo`; world-writable chmod; `curl | sh`; crontab/launchctl/authorized_keys changes; any state-changing SSH command (deploys, restarts, git pull, migrations, SQL, redirects, remote scripts) and reading remote secrets files; scp/rsync uploads and `rsync --delete`; recursive deletes outside the project/temp dirs, of whole repos, `.git`, or unexpanded variables; printing `.env`/keys/credentials files; writing content that looks like a real credential (except into `.env`); editing live global Claude config; SSH config. MCP: sending email/messages, calendar invites, sharing files, deletes in external services, Apollo sends and purchases, Meta Ads changes that set `ACTIVE` or change budgets/bids.
- Everything else passes silently.

Tune it in `global/eng-os/config.json` (protected branches, `disabled_rules`), then re-install.

**Personal trusted projects**: a developer can create `~/.claude/eng-os/local.json` (never written by the installer, never shared) with `trusted_projects` entries. Inside a listed local project, this turns off only these approval prompts:
- `git-protected-push`
- `git-discard`
- `sql-destructive`
- `docker-destructive`

Secrets, remote servers, infra and deploys, publishing, sudo, force-push and every hard block stay on everywhere.

## 4. Token-efficiency strategy
Measured baseline (last 30 days before install, `eng-os usage`): turn-1 context **~83k tokens** median, peak context ~387k median, cache-read share 98.5%, **subagents 40% of all input tokens** (almost all on Opus), 24% of `Read` calls were repeats, and skills were almost never invoked.

Levers built in:
- Lean always-loaded layer (above); procedures in skills; invariants in path-scoped rules.
- CLAUDE.md section 8 sets explicit rules: narrow reads, no re-reads, parallel calls, subagents only when justified, with `model: haiku/sonnet` for lookups and mechanical work, one task per session, CLI over MCP, result-first replies.
- `eng-os usage` makes waste visible (baseline context, cache share, subagent share and models, repeat reads, compactions, skills used, guard blocks), and the monthly review compares it over time in `docs/metrics.md`.

Recommended on the maintainer's machine, not applied (check yours with `eng-os usage`):
- `marketing-skills@marketingskills` is enabled globally (36 skills) but was not invoked in the analysed transcripts. Disable it globally (`"enabledPlugins": {"marketing-skills@marketingskills": false}`) and enable it per project where you do marketing work.
- The desktop org plugins (marketing, HR, product, sales…) and many claude.ai connectors (Apollo, Canva, Gamma, Gmail, Calendar, Drive…) are listed in every coding session. Toggle them off per session in the app's connector menu when coding.
- Effort: thinking is always on and the main model is Opus. For routine or mechanical sessions, `/effort medium` (or `"effortLevel": "medium"` in settings) cuts output and thinking tokens. Keep high effort for design, security and hard debugging. This is left as your per-session choice rather than a global default.
- The Homebrew CLI is 2.0.53 (the app bundles 2.1.309) and its OAuth login expired in July: `brew upgrade claude-code` then `claude /login` to use the terminal and `eng-os eval --run`.

## 5. Project-level instructions
- Template: `~/.claude/eng-os/templates/project/CLAUDE.md` (what, domain risk, **required skills**, stack, commands, architecture map, invariants, env/branch mapping, conventions, gotchas). Under ~120 lines; no repetition of global rules.
- `/eng-project-init` generates or refreshes it from repo evidence. Path-specific guidance goes in `.claude/rules/*.md` with `paths:`; personal notes go in a gitignored `CLAUDE.local.md`; long efforts get `docs/progress.md`.
- Loading facts (verified on 2.1.309): nested CLAUDE.md files load when a file in that folder is read by path (Read tool, `cat`, `sed`), but **not** for `ls`, `cd` or recursive grep. The global CLAUDE.md tells Claude to read them itself in those cases.

## 6. Evaluation and continuous improvement
| Command | Cost | What it checks |
|---|---|---|
| `eng-os verify` | 0 tokens | install drift, settings wiring, matcher coverage, hooks compile on both Pythons, guard error log, CLAUDE.md/skill/rule budgets, path scoping, duplicated sentences, standards in `docs/SOURCES.md` re-checked within 120 days |
| `eng-os test [--installed]` | 0 tokens | 122 guard cases + 4 session-hook cases in a throwaway sandbox |
| `eng-os usage --since D` | 0 tokens | efficiency metrics from local transcripts |
| `eng-os eval --prompt fresh-session` / `--transcript F` | one session | instruction loading, skill listing, nested CLAUDE.md, path rules, skill adherence, guard deny/ask in a real session |
| `eng-os eval --run` | small (Haiku, budget-capped) | headless guard and context scenarios (needs a logged-in CLI) |

The SessionStart hook reminds you when 30 days have passed since the last audit. `/eng-os-review` runs the measurements, checks Claude Code changes since the recorded version, and proposes changes on a branch with a CHANGELOG entry. Nothing is installed without your approval. Then `eng-os audit-done`.

## 7. Install, update, restore
```bash
cd <your eng-os clone>
bin/eng-os test                 # unit tests
bin/eng-os install --dry-run    # preview
bin/eng-os install              # backup -> stage -> validate -> apply -> verify (auto-rollback on failure)
bin/eng-os restore latest       # undo the last install (current state is backed up first)
bin/eng-os backups              # list backups (~/.claude/eng-os/backups/)
```
- To uninstall completely, restore the first `*-pre-install` backup: `bin/eng-os restore 20261103-232146-pre-install`. This also brings back the archived agent-skills pack.
- Update flow: edit the repo on a branch, run `test` and `install --dry-run`, review the diff, `install`, commit, add a CHANGELOG line.
- Hooks hot-reload: changes apply to running sessions immediately (verified).

## 8. Limitations (what Claude Code cannot guarantee)
- Instructions and skills are probabilistic: the model can still skip a skill or a rule. Only the guard and the permission settings are deterministic, and the guard only sees tool calls. It cannot stop a risky action hidden inside a script file it does not read, or code the model writes and then executes.
- The guard pattern-matches commands. Obfuscated or novel destructive commands can evade it. It is defence in depth on top of bypass mode, not a sandbox. For untrusted repos, use Claude Code's `sandbox` setting or a container.
- `ask` decisions need a human. In the desktop app they prompt even in bypass mode (verified). In headless `claude -p` nobody can answer, so they become denials. An unattended session that hits an ask waits for you.
- The hooks fail open. If `python3` is missing or the script crashes, tool calls proceed and the error is logged. `eng-os verify` reports it.
- Transcript formats are internal to Claude Code. `eng-os usage`/`eval` may need updates after upgrades; the monthly review catches this.
- Nothing here makes software "secure". It raises the floor and forces evidence; residual risk is always reported.
- The desktop app's own system prompt and org plugins are outside this config.

## 9. Decisions log
- **Replaced the agent-skills pack** (24 skills, 9 commands, 8 hook files) with 9 focused skills. It was invoked once in 700+ transcripts, and its SessionStart hook output used an invalid JSON shape, so it injected nothing. It is archived in the first backup and fully restorable. Its 4 agents were kept because they are used heavily (security-auditor 112 spawns).
- **Dropped project-CLAUDE.md injection from the guard** after a live test showed 2.1.309 loads nested CLAUDE.md on path reads natively. The hook was duplicating it.
- **No new subagents.** The built-in ones plus the existing four cover review, security, tests and exploration. Cost is controlled by per-call `model` instead.
- **Hook "ask" over hard deny** for anything that can be legitimate, so approval stays one click. Hard deny only for actions with no legitimate agent use.
- **Copy-install with manifest, not symlinks**: edits in the repo never go live unreviewed, and drift is detectable.
- **Standards are cited and dated (0.2.0)**: 0.1 wrote most engineering practice from model knowledge without sources. Every standard is now confirmed on its official site, recorded in `docs/SOURCES.md`, cited in the skill that uses it, and re-checked at each review. Long standard-specific detail lives in skill reference files (`standards.md`, `releases.md`), so the always-loaded cost stays the same.
- **Bypass mode kept**: it is your deliberate choice, and the guard plus deny rules supply the gates. `permissions.disableBypassPermissionsMode` is available if you ever want to forbid it.
