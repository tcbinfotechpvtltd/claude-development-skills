# eng-os: TCB Infotech's engineering system for Claude Code

Install it once and every Claude Code session on your machine works to TCB's engineering standards. It is security first, works from evidence, gets on with routine work by itself, asks before anything risky, and keeps token use low. It covers Frappe/ERPNext, Odoo, PHP CodeIgniter 3, Next.js, Flutter, Linux VPS/AWS and Indian digital lending.

**New here? Install it with [INSTALL.md](INSTALL.md)** (about 5 minutes). Changes: [CHANGELOG.md](CHANGELOG.md).

## At a glance
| | |
|---|---|
| Version | 0.3.0 |
| Works with | Claude Code desktop app and CLI. Verified on macOS with 2.1.309; Linux and WSL should work but have not been tested |
| Applies to | every project you open with Claude Code on your machine, with no per-project setup |
| Cost per session | about 2.7k tokens always loaded (instructions + skill list). Everything else loads only when a task needs it |
| Quality checks | 126 automated tests for the safety hooks, a 63-point health check, and a scored test in a real Claude session |
| Standards | 53 external standards, each confirmed on its official site and dated ([docs/SOURCES.md](docs/SOURCES.md)) |
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

### Nine skills (loaded only when the task needs them)
| Skill | Used for | What it brings |
|---|---|---|
| `eng-design` | features, systems, APIs, data models, tech choices | requirements before solutions, 2–3 options with trade-offs, a design checklist (data, state machines, APIs, integrations, consistency, failure modes), C4 diagrams, ADRs, Twelve-Factor, an AWS Well-Architected final pass |
| `eng-security` + `stacks.md` + `standards.md` | auth, input, uploads, secrets, PII/KYC, payments, new endpoints, dependencies, servers, audits | STRIDE threat model; controls for each OWASP Top 10:2025 category; NIST 800-63B-4 password and MFA rules; CERT-In logging; pitfalls for Frappe, CI3, Next.js, Odoo, Flutter and Linux; a map of which standard governs which work (ASVS 5.0, API, mobile, LLM and agentic AI, supply chain, CIS, PCI DSS, ISO 27001, NIST CSF) |
| `eng-testing` | writing or fixing tests, debugging failures, flaky tests | risk-based test selection, test pyramid rules, contract tests, fix-with-a-failing-test protocol, step-by-step root-cause debugging |
| `eng-review` | before a commit, PR or handoff; code reviews and audits | self-review checklist based on Google's engineering practices, independent subagent review, an "audit until dry" loop, severity rubric, report format |
| `eng-ship` + `releases.md` | CI/CD, deploys, releases, migrations on shared data, servers, monitoring, backups, incidents | CI gates, a production release checklist with rollback, SemVer, Conventional Commits, Keep a Changelog, GitHub release notes, SLOs and error budgets, DORA metrics, backups, blameless postmortems |
| `frappe-erpnext` | Frappe, ERPNext, HRMS and custom apps, bench | site isolation, permission-safe APIs, DocType JSON and patches, bench workflows, v15/v16 gotchas |
| `fintech-lending` | anything that moves money, computes loan amounts or stores borrower data | money as decimals, append-only double-entry ledgers, loan state machines, disbursal gates, vendor adapters and webhooks, RBI Digital Lending Directions 2025, DPDP Rules 2025, RBI NBFC cyber and outsourcing directions |
| `eng-project-init` | a repo with no CLAUDE.md, or a stale one | builds a project CLAUDE.md from the repo: commands, architecture map, invariants, environments, gotchas |
| `eng-os-review` | monthly (a reminder appears) | measures token use and adherence, checks Claude Code changes, re-checks every cited standard, proposes improvements as a PR |

### Three path-scoped rules
These load automatically when Claude touches matching files, even if no skill was invoked:
- `frappe-erpnext`: `hooks.py`, doctypes and patches (permission checks, parameterised SQL, Server Scripts off).
- `db-migrations`: migrations, `*.sql` and schema files (reversible and re-runnable, expand-then-contract, approval and a fresh backup before destructive changes).
- `ci-deploy`: CI workflows, Dockerfiles, compose, Terraform, nginx, Kubernetes (least-privilege tokens, actions pinned to a commit, approval gate on production deploys, non-root containers, written rollback).

### Safety guard
A hook checks every Claude tool call in about 50 ms and costs no tokens:
- **Refuses** catastrophic actions, such as wiping a home or system folder, dumping the keychain, or commits with a Claude co-author trailer.
- **Asks you first** before force-pushes, pushes to `main`/`prod`/`uat`, `reset --hard`, deploys, `DROP`/`TRUNCATE`, state-changing SSH, printing `.env` files, sending email or messages, and ad changes that spend money.
- **Stays silent** for everything else.

The prompts appear even in bypass-permissions mode (verified). Details are in [section 3](#3-the-guard-deterministic-safety-layer).

### Session check
A start-of-session hook stays silent unless the monthly review is due or someone edited the installed files directly.

### Command-line tool (`bin/eng-os`)
`install` (backup, validation, rollback), `verify` (health check), `test`, `status`, `backups`, `restore`, `usage` (token and tool metrics from your local transcripts), `eval` (scores a real session against test scenarios), `audit-done`.

### Templates
- `templates/project/CLAUDE.md`: the project instructions template.
- `templates/release/`: `CHANGELOG.md`, GitHub `release.yml` and `pull_request_template.md`, ready to copy into a repo.

### Documentation
| File | What it holds |
|---|---|
| [INSTALL.md](INSTALL.md) | install, what changes on your machine, updating, undo, troubleshooting |
| [docs/SOURCES.md](docs/SOURCES.md) | every external standard cited, with edition, date, link and when it was last checked |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | each requirement mapped to where it is implemented and how far it is proven |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | test and live-session evidence for every release |
| [docs/metrics.md](docs/metrics.md) | token and efficiency measurements over time |
| [CHANGELOG.md](CHANGELOG.md) | what changed in each version |

## Why it is good
- **Safety is enforced, not hoped for.** Risky actions are stopped by a hook that runs on every tool call, not by a sentence the model might forget. 126 automated cases cover it, and it was verified live in bypass mode.
- **Built on current standards, with sources.** 53 standards are named with their edition and the date each was confirmed on its official site: OWASP, NIST, CIS, MITRE, CISA, SLSA, PCI, ISO, Google SRE and DORA, RBI, DPDP and CERT-In. Nothing is quoted from memory, and a health-check warning plus the monthly review keep them current.
- **Made for TCB's real work.** The stack pitfalls, lending rules and severity examples come from TCB projects, audits and incidents, not generic advice.
- **Cheap to run.** About 2.7k tokens per session. Detail lives in files that load only when needed. The 24-skill pack it replaced was used once in more than 700 sessions.
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
| Global instructions | `~/.claude/CLAUDE.md` | every session, re-read after compaction | ~1.8k tokens | priority order, approval gates, engineering behaviour, security floor, skill routing table, git and token rules |
| Skills (9) | `~/.claude/skills/<name>/SKILL.md` | listing always (~0.9k tokens); body only when invoked; reference files only when the body sends Claude to them | 0.6–1.5k tokens each when used | procedures: `eng-design`, `eng-security` (+`stacks.md`, `standards.md`), `eng-testing`, `eng-review`, `eng-ship` (+`releases.md`), `frappe-erpnext`, `fintech-lending`, `eng-project-init`, `eng-os-review` |
| Standards register | repo `docs/SOURCES.md` | never in context | 0 | every external standard the skills cite, with edition, publication date, URL and the date it was last confirmed on the official site |
| Path-scoped rules (3) | `~/.claude/rules/*.md` | only when a matching file is read or edited | ~200–300 tokens each | must-follow invariants for Frappe code, DB migrations/SQL, CI/containers/infra |
| Guard hook | `~/.claude/eng-os/hooks/guard.py` (PreToolUse: Bash, file tools, `mcp__.*`) | every matching tool call, ~50 ms | 0 tokens unless it blocks | deny catastrophic actions; ask before destructive, irreversible, outward-facing, production and secret-exposing ones |
| Session hook | `~/.claude/eng-os/hooks/session_start.py` | session start | 0 tokens normally; one line when due | monthly self-audit reminder; warns if live files were edited outside an install |
| Settings keys | `~/.claude/settings.json` (merged, other keys untouched) | always | 0 | hook wiring, `attribution` off (commits under each developer's own identity), deny reading Claude's own OAuth file |
| Subagents | `~/.claude/agents/` (existing 4 kept) | when spawned | per run | `security-auditor`, `code-reviewer`, `test-engineer`, `web-performance-auditor` are used for fresh-context review; no new agents were needed |
| CLI + tests | `~/.claude/eng-os/bin`, `tests`, `templates` | never in context | 0 | install/verify/test/usage/eval/restore, project template |

**Always-loaded total added by eng-os: ~2.7k tokens** (CLAUDE.md plus skill listing). The installer also removed the ~1.7k-token listing of the 24 unused agent-skills and a SessionStart hook that ran in every session and injected nothing.

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
