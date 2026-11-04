---
name: custom-apps
description: Building and changing custom apps outside the ERP frameworks — Next.js/React/Node web apps, PHP CodeIgniter 3 legacy apps, Flutter mobile apps and Python services: supported runtime versions, architecture and project structure, framework upgrade traps, configuration, deploy shape. Use when creating, extending, upgrading or reviewing such an app.
---

# Custom-built apps

Load the file for the stack in hand; each holds its architecture, current upgrade traps and deploy shape:
- Next.js / React / Node: [nextjs.md](nextjs.md)
- Flutter / Dart mobile: [flutter.md](flutter.md)
- PHP / CodeIgniter 3: [php-ci3.md](php-ci3.md)
- Python services and scripts: [python.md](python.md)

Security pitfalls per stack: [stacks.md](../eng-security/stacks.md). Formatter and linter per language: [coding-standards.md](../eng-review/coding-standards.md). Test tooling: [tooling.md](../eng-testing/tooling.md).

## Runtime versions (checked 2026-11-04)
| Runtime | Use for new work | Still supported | End of life / note |
|---|---|---|---|
| Node.js | 26 (Active LTS) | 24 and 22 (maintenance) | 22 ends 2027-04-30, 24 ends 2028-04-30; 20 ended 2026-04-30 |
| Next.js / React | Next.js 16.4 with React 19.3 | — | Next.js 16 needs Node 20.9+ and TypeScript 5.1+ |
| TypeScript | 7.0 once the repo's tooling supports it; otherwise stay on 6.x | — | check linters and build tools before upgrading |
| PHP | 8.4 or 8.5 | 8.3 (security until 2027-12-31) | **8.2 security support ends 2026-12-31**; 8.1 and older unsupported |
| Python | 3.14 (3.15 once the dependencies support it) | 3.11 to 3.13 (security fixes) | 3.11 ends 2027-10; 3.10 ended 2026-10-01. Frappe and Odoo dictate their own Python version |
| Flutter / Dart | Flutter 3.47 with Dart 3.13 | — | keep within a few minor releases of stable |
An unsupported runtime is a security finding: report it with its end-of-life date and an upgrade plan (skill `eng-design` for the ADR).

## For every custom app
- Project CLAUDE.md (skill `eng-project-init`) records runtime versions, commands, environments and the deploy path.
- One configuration surface: environment variables (or a git-ignored keys file where the stack requires it) with a committed `.env.example`; separate UAT and production values; no secrets in the client bundle or the app binary.
- Layering: transport (routes, controllers, screens) → application logic → data access, with dependencies pointing inward; business rules in plain, testable functions; one adapter per external vendor.
- APIs follow skill `eng-design` (error shape, pagination, idempotency keys, versioning, OpenAPI when another app consumes it).
- Dependencies: lock file committed, advisories checked before adding or upgrading (`npm audit`, `composer audit`, `pip-audit`, `dart pub outdated`), no abandoned packages.
- Every app has health checks, structured logs and error tracking before production (skill `eng-ship`).
