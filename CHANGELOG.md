# Changelog
Material changes to the global system. Every install is also backed up under `~/.claude/eng-os/backups/`.

## 0.4.0 — 2026-11-04
- New skills, each researched against official sources:
  - `odoo`: versions 17 to 20; Odoo 20 released Sept 2026, 17.0 out of standard support. Covers module layout and naming, breaking ORM and view changes per version, `ir.access` in 20, security, controllers, QWeb, tests, migration scripts, the upgrade service and performance.
  - `custom-apps`, with one file per stack:
    - Next.js 16.4: upgrade traps, Cache Components, Server Action security.
    - Flutter 3.47: official MVVM architecture.
    - PHP and CodeIgniter 3: legacy status; PHP 8.2 security support ends 2026-12-31.
    - Python services.
    - A runtime support table with end-of-life dates.
  - `eng-delivery`: scope, three-point estimates, Scrum (2020), Kanban (v2025.5), staged plans (PRINCE2 7), Definition of Done, RAID log, status template (PMBOK 8 domains), change control, UAT, go-live and handoff.
- New reference files:
  - `eng-review/coding-standards.md`: PEP 8 and Ruff, PER Coding Style 3.1, ESLint 10 with typescript-eslint and Prettier, Effective Dart, Frappe's lint setup.
  - `eng-ship/github.md`: rulesets, CODEOWNERS, Dependabot, secret scanning and push protection, Actions hardening (SHA pinning, after the March 2026 Trivy action compromise), OIDC, attestations, GitHub Flow.
  - `eng-testing/tooling.md`: tools per stack, WCAG 2.2, Core Web Vitals, k6, Pact, security scanners, mutation testing.
- Global routing table: rows for `odoo`, `custom-apps` and `eng-delivery`, plus a coding-standards pointer. `eng-project-init` suggests the new skills. `stacks.md` Odoo section updated for 18 to 20.
- `docs/SOURCES.md`: 103 entries.
- README: per-area detail (custom apps, ERPNext, Odoo, coding, testing, GitHub, DevOps, SDLC, project management, security, tokens).

## 0.3.0 — 2026-11-04
- Shareable with other developers ([INSTALL.md](INSTALL.md)). Commit identity is per user: `install --name= --email=`, saved in `~/.claude/eng-os/user.json`, written into the global CLAUDE.md at install (`{{GIT_AUTHOR}}`). No personal names, paths or usernames remain in installed files.
- An existing global CLAUDE.md that eng-os did not write is kept: saved to `~/.claude/eng-os/personal.md` and appended as section 9 on every install.
- Archiving the old agent-skills pack (skills, commands and its hooks) is now opt-in (`--archive-legacy`); legacy hook matching narrowed to `~/.claude/hooks/...` so a teammate's own `session-start.sh` hook is never removed.
- Installer refuses to run when `~/.claude/settings.json` is invalid JSON (it previously treated it as empty and replaced it, with a backup).
- Skills and CLAUDE.md fall back to a general-purpose subagent when the `security-auditor`/`code-reviewer`/`test-engineer` agents are not installed (they are not part of eng-os).
- `eng-os status` shows the commit identity; `/eng-os-review` opens a PR on shared repos instead of installing locally.

## 0.2.0 — 2026-11-04
- Sourced standards: 53 external standards confirmed on their official sites and recorded with edition, date and URL in `docs/SOURCES.md`. 0.1.x had written most engineering practice from model knowledge without citations; this corrects that and the overstated row in `docs/REQUIREMENTS.md`.
- New `eng-ship/releases.md`: SemVer 2.0.0, Conventional Commits 1.0.0, short-lived branches, small PRs, Keep a Changelog 1.1.0, GitHub release notes (`.github/release.yml`), release procedure. Templates in `templates/release/`.
- New `eng-security/standards.md`: which standard governs which work (ASVS 5.0.0 levels, API Top 10 2023, MASVS/MASTG, OWASP LLM Top 10 2026 and Agentic Top 10, NIST SSDF/CSF 2.0/800-63B-4/800-53/800-207, SLSA v1.2, SBOM, CWE Top 25 2025, ATT&CK v20, CIS, PCI DSS 4.0.1, ISO 27001:2022, CISA Secure by Design), Indian reporting clocks, post-quantum timeline (NIST IR 8547 final), watch list of drafts.
- eng-security: NIST 800-63B-4 password and MFA rules, CERT-In log/NTP rules, post-quantum line, supply-chain items; stacks.md: CIS benchmark versions, MASVS/MASTG.
- fintech-lending: checked against the RBI Digital Lending Directions 2025 primary text and the Nov 2025 consolidation; fund flows, cooling-off minimum, no auto limit increase, data in India (24-hour return), app permissions, grievance and Ombudsman escalation, recovery-agent notice, multi-lender LSP rules, CIMS reporting, DLG cap; DPDP Rules 2025 phases, breach, logs, rights; RBI NBFC cyber (2026) and outsourcing (2025) directions for tech vendors.
- eng-review (Google eng-practices approval standard and checklist), eng-design (C4, MADR 4.0.0, Twelve-Factor, Well-Architected pillars), eng-testing (pyramid rules, contract tests, WSTG/ASVS), eng-ship (SLOs and error budgets, DORA five metrics, postmortem triggers, SBOM gate).
- `eng-os verify` warns when a standard in `docs/SOURCES.md` was checked more than 120 days ago; `/eng-os-review` re-checks every source.

## 0.1.1 — 2026-11-03
- Guard: credential and secret-file rules now fire only when a printing/copying/sending command (`cat`, `cp`, `grep`, `curl @file`, `tar`…) names the file in its own arguments. Mere mentions (docs, heredocs, commit messages) no longer trigger. Found in live use: a heredoc writing this changelog was denied. 5 regression cases added.
- Frappe rule: prefer permission-aware `frappe.get_list` over `frappe.get_all` when results reach a user.

## 0.1.0 — 2026-11-03
- First install. Global CLAUDE.md (priority order, approval gates, engineering behaviour, security floor, skill routing, git, token rules).
- 9 skills: eng-design, eng-security (+stacks.md), eng-testing, eng-review, eng-ship, frappe-erpnext, fintech-lending, eng-project-init, eng-os-review.
- 3 path-scoped rules: frappe-erpnext, db-migrations, ci-deploy.
- Guard PreToolUse hook (deny/ask gates) and SessionStart hook (audit reminder, drift warning).
- Settings: hooks wired, `attribution` hidden, deny reading Claude's own OAuth credentials file; existing keys preserved.
- Archived (restorable): agent-skills pack skills/commands/hooks and its non-functional SessionStart hook. Agents kept.
- Removed before release: guard project-CLAUDE.md injection (native in 2.1.309, verified live).
