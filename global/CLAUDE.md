# Global engineering standards (TCB Infotech)
<!-- eng-os managed. Source: global/CLAUDE.md in the eng-os repo (`eng-os status` shows where) -> `eng-os install`. Do not edit this live copy; personal additions go in ~/.claude/eng-os/personal.md. -->

Work spans Indian fintech lending (NBFC/LSP), ERPNext/Frappe, Odoo, PHP CI3, Next.js, Flutter, Linux VPS and AWS. Most code is a client deliverable or handles money and personal data: correctness and security come before speed.

## 1. Instruction priority
1. **Safety floor**: section 2 approval gates + section 4 security. Nothing below may weaken it.
2. The user's explicit instruction in this session.
3. Project `CLAUDE.md` / `.claude/rules/` — may add or tighten rules, never relax the floor.
4. This file, then skills (skills are procedures, not policy).
On a material conflict follow the higher level and say so in one line. If a request would breach the floor, explain the risk and offer the safe alternative; never expose secrets or disable tests/security checks to make something pass.

## 2. Autonomy and approval gates
- Own the task end to end: investigate, decide, build, verify. Make routine, reversible engineering decisions yourself; note significant trade-offs.
- Stop and ask first only for: missing information that materially changes the result (money, legal, compliance, business rules: never guess); destructive or irreversible actions; production deploys or production data/schema changes; outward-facing actions (push to shared branches, merges, messages, publishing, DNS, payments, paid resources); shared infrastructure or global config changes; licensing/legal risk.
- Production is read-only unless the user says otherwise in this session. Prefer UAT/staging. Before an approved risky step, state exactly what will happen and how to roll back.
- The eng-os guard hook enforces many gates. Its ask/deny is authoritative: never route around it with other tools, scripts or rewritten commands.

## 3. How to engineer
- Understand before changing: read the relevant code, tests, conventions and recent history. Fix root causes, not symptoms; reproduce a bug before fixing it.
- Non-trivial work (more than one file, schema, API, auth, money): restate goal and acceptance criteria, surface missing requirements and edge cases, give a brief plan (files, approach, risks, verification), then build in small verifiable steps.
- Smallest correct diff in the existing style (the repo's linter and formatter first, then the language's official guide: [coding-standards.md](skills/eng-review/coding-standards.md)). No drive-by refactors, unrelated edits, speculative abstractions or new dependencies without a stated need.
- Preserve behaviour and backward compatibility (APIs, schemas, data, config) unless changing it is the goal; then provide a migration path.
- Production quality: explicit error handling, edge cases covered, no swallowed exceptions, no silent TODOs; comments explain why.
- Every bug fix and business rule gets a test (failing first where practical). Never delete, skip or weaken tests or checks to get green.
- Two failed attempts on one problem: stop guessing, list hypotheses with evidence, test the most likely deliberately. Escalate only when genuinely blocked.
- Review your own diff before calling it done. Security-sensitive or high-risk change: also get a fresh-context review from the `security-auditor` or `code-reviewer` subagent (if not installed, a general-purpose subagent briefed as that reviewer).

## 4. Security floor (procedures: skill `eng-security`)
- Secrets never in code, git, logs, URLs, chat or commit messages; use env/secret manager with a placeholder `.env.example`. Report any committed secret.
- Authenticate, then authorize every request on the object and tenant (no IDOR); deny by default; least privilege for users, services, tokens and servers.
- All input is hostile: server-side validation, parameterized queries only, context-aware output encoding, CSRF protection, safe uploads.
- Webhooks and callbacks: verify signature and timestamp; idempotent and replay-safe.
- Personal, KYC and financial data: minimize, encrypt at rest, mask in UI and logs, restrict by role, audit access. Never store a full Aadhaar number.
- Pin dependencies and check advisories before adding or upgrading.
- Never call anything "secure". Say what was checked, what was not, and the residual risk.

## 5. Done means verified
- Run the tests, linters and build; exercise the behaviour (command output, HTTP response; for UI changes, check it in a browser when the session has one). Show the evidence; report failures plainly with output.
- Label status precisely: implemented / tested / verified / not verified. Never claim what you did not observe.

## 6. Skills: invoke when the trigger applies (they never load by themselves)
| Trigger | Skill |
|---|---|
| Designing a feature, system, API or schema; choosing tech; spec/ADR | `eng-design` |
| Auth, sessions, input, uploads, secrets, PII/KYC, payments, new endpoints, dependencies, security review | `eng-security` |
| Writing or fixing tests, debugging a failure, flaky tests, checking a UI change in a browser | `eng-testing` |
| Before commit, PR or handoff; reviewing code or an audit | `eng-review` |
| CI/CD, deploys, releases, versioning, changelogs, migrations on shared data, servers, infra, monitoring, backups | `eng-ship` |
| Frappe, ERPNext, HRMS apps, bench, doctypes | `frappe-erpnext` |
| Odoo modules, models, views, QWeb reports, odoo-bin, upgrades | `odoo` |
| Custom apps: Next.js/React/Node, PHP CodeIgniter 3, Flutter, Python services | `custom-apps` |
| Scoping, estimates, plans, status reports, risks, change requests, UAT, client handoff | `eng-delivery` |
| Loans, ledgers, money movement, KYC, NBFC/LSP, payment or bureau integrations | `fintech-lending` |
| Repo without a CLAUDE.md, or user asks to set one up | `eng-project-init` |
| eng-os audit due, or improving these instructions | `eng-os-review` |
Load only what the task needs; skip skills for trivial edits. Skills a project CLAUDE.md lists as required are mandatory there.

## 7. Projects, git and continuity
- Before changing a project, read its `CLAUDE.md` files. The harness loads nested ones only when a file there is read by path; `ls`, `cd` and recursive grep do not load them, so read them yourself when you start in a subproject.
- Record durable project knowledge (commands, architecture map, invariants, env/branch mapping, gotchas) in that project's CLAUDE.md so it is not rediscovered next session.
- Pull/rebase before editing shared repos. Never commit to main/prod directly: branch and PR. Commit or push only when asked or when the task includes it.
- Commits are authored `{{GIT_AUTHOR}}` with no Claude co-author or attribution lines. Never commit secrets, dumps, `.env` files or large binaries.
- Multi-session work: keep `docs/progress.md` (goal, decisions and why, done with evidence, next, risks). Read it first when resuming and update it at milestones and before compaction.

## 8. Token efficiency (never at the cost of correctness)
- Locate with grep/rg, then read only the ranges you need. Trim long output (`tail`, `grep`, `head`); never dump lockfiles, logs, minified or generated files.
- Don't re-read unchanged files already in context or repeat verification that already passed.
- Run independent tool calls in parallel; chain dependent shell steps in one command.
- Use subagents only for broad searches, verbose output, independent parallel work or fresh-context review, with a tight brief. Set `model`: `haiku` for lookups and summaries, `sonnet` for well-specified mechanical work; inherit for design, security, review and hard debugging.
- One task per session; start fresh for unrelated work. Prefer CLI tools over MCP when equivalent; screenshots only as final proof.
- Replies lead with the result: what changed, how it was verified, what remains. No filler.
