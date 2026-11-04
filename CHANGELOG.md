# Changelog
Material changes to the global system. Every install is also backed up under `~/.claude/eng-os/backups/`.

## 0.8.1 — 2026-11-04
- **Shorter install command**, easier to share: `git clone https://github.com/tcbinfotechpvtltd/claude-development-skills ~/.eng-os && bash ~/.eng-os/install.sh`. Updating is `bash ~/.eng-os/install.sh`, which `install.sh` now prints at the end. The 0.8.0 command still works.
- INSTALL.md gives the current counts (13 skills, 9 rules).

## 0.8.0 — 2026-11-04
- **One command installs everything**, and updates it when run again: `install.sh`, run through `git clone ... ~/.eng-os && bash ~/.eng-os/install.sh`. It:
  - checks git and Python;
  - downloads the latest release;
  - asks for the name and email once when git does not know them (or reads `ENG_OS_NAME` and `ENG_OS_EMAIL`);
  - runs the self-tests;
  - installs into `~/.claude`, which Claude Code in VS Code, the desktop app and the terminal all read.
  - It works for a private repo (the employee's GitHub login) or a public one.
- **Fresh downloads always switch to the latest release.** `install.sh` and `eng-os update` now leave alone only a maintainer copy with unreleased work (another branch, or commits that are not on origin/main).
- README, INSTALL and the rollout guide open with the one command. The rollout guide recommends a private repo and lists what to do before ever making it public.
- `stacks.md`: the Frappe Server Scripts note is phrased generally.

## 0.7.1 — 2026-11-04
- **Generic for any project**: nothing in the hooks, skills, tests or docs names a specific project or server.
  - Example project names became neutral.
  - Test hosts became `appserver`.
  - The ad-spend guard covers any ad-platform MCP server (`ads-spend`), not one particular tool.
- **Detection recognises any common stack**: Laravel, WordPress, PHP, Django, React Native, Java/Kotlin, .NET, Go, Rust, Ruby and iOS. Stacks without a dedicated skill get the general skills, with their conventions recorded in the project CLAUDE.md.
- **Projects outside git** without a CLAUDE.md are offered `/eng-project-init`, which recommends version control.
- **Learning loop**: detected stacks are counted per machine (`state/stacks-seen.json`), so `/eng-os-review` can propose skills for stacks that keep appearing.
- Tests: 153.

## 0.7.0 — 2026-11-04
- **Skills apply automatically; nobody names them.**
  - **Project detection** at session start: Frappe/ERPNext, Odoo, Next.js, Node, Flutter, CodeIgniter 3 and Python from project files; lending from the project CLAUDE.md. A repo without a CLAUDE.md is offered `/eng-project-init`.
  - **New `prompt_router.py` UserPromptSubmit hook**: names the matching skills from the request's keywords, at most once per skill per session, silent when nothing matches.
  - **6 new path rules**: odoo, nextjs, flutter, php-ci3, tests, docs (9 in total). Each states the must-follow points and names its skill.
  - **Global instructions** section 6 tells Claude to load whatever these layers name.
- Hook messages are phrased as facts, as the Claude Code docs recommend.
- Tests: 148 (13 new for detection and routing). `verify` also checks the router is wired and compiles.
- Guard: optional personal `~/.claude/eng-os/local.json` (never written by install) with `trusted_projects`. For commands run in, or `cd`/`git -C` into, a listed path, it can switch off only `git-protected-push`, `git-discard`, `sql-destructive` and `docker-destructive`. Secrets, remote, infra, publish, sudo, force-push and all deny rules stay on. It adds 6 tests.

## 0.6.0 — 2026-11-04
- For individual Claude plans, where there is no central admin console:
  - `eng-os update` switches the repo to the latest release tag, runs the tests, shows the install preview and installs after confirmation. It leaves a maintainer clone that is ahead of the latest release untouched.
  - The session-start hook says, at most once a week, when a newer release is published (no prompts, silent on any failure). There are 3 new tests (129 in total).
- Data on individual plans: the policy, the install guide and the rollout guide now require **Model Improvement** off and no `/feedback` from client work. They describe what a Team plan changes, and an optional machine-level lock (not built). Facts are from Anthropic's data-usage and privacy pages.

## 0.5.0 — 2026-11-04
- **Testing**:
  - `eng-testing/test-types.md`: the minimum tests per change, and a map of 25 test types (what each catches, when, how).
  - `eng-testing/browser.md`: Claude checks its own UI changes in a real browser (the built-in browser, Claude in Chrome, Playwright MCP 0.0.84, Chrome DevTools MCP 1.12), following a 10-step procedure with safety rules; also visual regression.
  - `tooling.md`: Hypothesis, fast-check, Schemathesis, Atheris, axe-core, Lighthouse CI, Faker, Google test sizes.
- **Documentation**: new skill `eng-docs`.
  - The document set every project keeps, when each is created and updated, append-only history, requirement ids linking everything, Diátaxis user manuals per role, writing rules and a bus-factor check.
  - Templates in `templates/docs/`: index, requirements (ISO/IEC/IEEE 29148 ideas), glossary, architecture (arc42 v9.1), test plan with test cases and traceability (ISO/IEC/IEEE 29119-3 ideas), user manual and What's new, runbook, progress log, handover.
- **Delivery**:
  - `eng-delivery/erp-implementation.md`: the TCB ERP method (discover, fit-to-standard, build, data migration, UAT and training, cutover, hypercare, next phase), from Frappe, Odoo, Microsoft and SAP methodologies.
  - Issue tracking with `templates/github/` (issue forms, labels, CODEOWNERS, Dependabot).
  - The Definition of Done now includes documents and a progress-log entry.
- **Company**:
  - `docs/ENGINEERING-POLICY.md`: what every engineer commits to when working with Claude Code.
  - `docs/COMPANY-ROLLOUT.md`: per-developer install, a plugin, and organisation-managed settings, with a recommendation.
  - `templates/project/claude-settings.json`: a per-repo installed-check, added by `/eng-project-init`.
- **Global instructions**: routing rows for `eng-docs`, browser checks and ERP phases; documents updated with every change; lessons fed back into eng-os.
- `docs/SOURCES.md`: 129 entries.

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
