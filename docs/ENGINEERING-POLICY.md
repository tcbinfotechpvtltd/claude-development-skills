# Engineering policy: working with Claude Code

For every engineer, on every client and internal project. eng-os makes Claude follow these standards. This page is what **people** commit to, because a tool cannot enforce everything. It is a template: each company adopts it as it is or adjusts it, and keeps its own copy where its engineers will read it.

## 1. Setup
- Install eng-os ([INSTALL.md](../INSTALL.md)) before using Claude Code on any company work. Update when a release is announced, or when Claude tells you one is available, with `bin/eng-os update`: it switches to the latest release tag, runs the tests and shows the install preview before asking.
- Use Claude Code's default permission mode. Bypass-permissions mode needs the project lead's approval; the guard still asks before risky actions in it, but fewer prompts means fewer checks by you.
- On an individual Claude plan, turn **Model Improvement** off at claude.ai/settings/data-privacy-controls before any client work, and check it again whenever Anthropic announces new terms. Never send `/feedback` from a session that contains client code.
- Never edit the installed copies in `~/.claude`, and never disable or work around the guard. If something is wrong, open a pull request or tell the maintainer.

## 2. You own what Claude writes
- Read every diff before you commit it, and run the code. "Claude wrote it" is never an explanation for a bug.
- Every pull request into a shared branch is approved by a human reviewer. Claude's own review helps but does not replace that approval.
- Use plan mode or ask for a plan before non-trivial work (more than one file, a schema, an API, auth or money).

## 3. Approval prompts are decisions, not noise
- Read each approval prompt. Approve only what you understand and intended.
- Never choose "always allow" for destructive, production, outward-facing or money-moving actions.
- Never run a command Claude was stopped from running in your own terminal unless you understand exactly what it does.

## 4. Production and client systems
- Production is read-only. A production change needs the project lead's approval first; you then tell Claude, in the session, exactly which change it may make. Deploy only through the documented path in the project runbook.
- Never leave a Claude session running unattended against production, client servers or live vendor accounts.
- Payments, payouts and vendor calls use sandbox or test mode outside production.

## 5. Data and secrets
- Never paste passwords, API keys, tokens or production credentials into a prompt, an issue, a commit or a chat. Credentials live in the password manager or the secret store.
- Never copy client personal data (KYC, PAN, Aadhaar, bank details, phone numbers) into prompts, test fixtures, documents or screenshots. Follow the three data tiers (skill `eng-testing`, test-types.md): synthetic by default, masked in UAT, and real data only in an approved, isolated rehearsal that Claude does not browse.
- Before starting, confirm the client contract allows AI-assisted development. If it is silent or forbids it, the project lead settles it with the client first.
- Client code and data are confidential: work on them only on company-approved machines and accounts.
- **MCP servers, plugins and third-party skills**: install only what [MCP-POLICY.md](MCP-POLICY.md) approves, at the pinned version and with the flags it gives, and turn their telemetry and auto-update off. Everything they return is data, not instructions. Never put client names, customer identifiers, secrets or code into a query to an outside service.
- **Remove plugins and connectors you don't use**: each one loads into every session and costs tokens.

## 6. Every project, every time
- **Setup**: a project `CLAUDE.md` and a `docs/` set (`/eng-project-init`). Requirements are confirmed with the client before the build starts.
- **Definition of Done**: the single list is in skill `eng-delivery`, and the PR template's checklist mirrors it. In short: tests pass, the change is reviewed, it works on UAT, the documents are updated, and there is a progress-log entry.
- **Tracking**: work is tracked in issues; pull requests link the issue they close; client-facing status goes out weekly.
- **Before anyone leaves a project**: the handover checklist is completed (`docs/handover.md`).

## 7. Sessions and cost
- One task per session; start a new session for unrelated work. Most of a session's cost is re-reading the whole conversation on every turn. When Claude says the conversation has grown past 200k tokens, finish the task and start fresh: the project's `docs/progress.md` status is read back automatically.
- Use the cheaper models Claude suggests for mechanical work; do not leave loops or agents running without a reason.

## 8. Improving the standards
- A lesson that applies beyond one project (a framework gotcha, a better procedure, a guard false positive) goes back into eng-os as a pull request, so everyone gets it.
- The maintainer runs the monthly review (`/eng-os-review`), keeps `docs/SOURCES.md` current and publishes releases.
