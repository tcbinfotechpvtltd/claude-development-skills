---
name: eng-docs
description: Project documentation that survives people leaving — requirements, user manuals, test cases and traceability, runbooks, project history and handover: which documents a project keeps, when each is written and updated, templates and writing rules. Use at project start, when requirements change, after every development change, before UAT or a release, and before a handover.
---

# Project documentation

Goal: anyone can understand, run, change and support the project from the repo alone. The test: if the developer left today, could someone else carry on next week without calling them?

## Core rules
- The same PR updates every document the change touches: requirements, test cases and traceability, user manual, runbook, CHANGELOG.
- Each working session adds a new dated file under `docs/progress/`; earlier entries stay as written, except to redact a leaked secret or personal data.
- `REQ-nnn` ids tie issues, PRs, test cases and manual pages together.
- Rules, rates, policies and dates come from the client or the user; until confirmed they carry **TO CONFIRM**.
- Documents and screenshots never hold credentials, secret values or real customer data.
- When a PR leaves a document out of date, its description says why.

## The document set
Docs as code: Markdown in the repo, changed in the same pull request as the code, reviewed like code. Templates live in `~/.claude/eng-os/templates/docs/`, and skill `eng-project-init` copies them in.

| Document | Create | Update |
|---|---|---|
| `README.md` (setup, run, test) and project `CLAUDE.md` | project start | when tooling, commands or gotchas change |
| `docs/README.md` (index) | project start | when a document is added |
| `docs/requirements.md` with `docs/glossary.md` | after discovery, before building; client confirms | every requirement change, with its change-history row |
| `docs/architecture.md` (arc42) and `docs/adr/` | after design, for any system with more than one component | when structure, integrations or deployment change; a new ADR per costly decision |
| `docs/test-plan.md` (plan, test cases, traceability, completion report) | with the requirements | test cases with every change; a completion report every release |
| `docs/user-manual/` (per role, Diátaxis) | first full draft before UAT | every user-visible change, plus "What's new" each release |
| `docs/runbook.md` | before the first deploy | whenever deploy, backup, jobs, monitoring or access change |
| `docs/progress.md` (current status) and `docs/progress/` (the log: one file per entry, `YYYY-MM-DD-short-title.md`, so parallel PRs never conflict) | project start | a new log entry every working session and milestone |
| `docs/decisions.md` (client decisions) and `docs/project-brief.md` | project start | each decision the client confirms |
| `CHANGELOG.md` and release notes | first release | every merged user-visible change (skill `eng-ship`, releases) |
| `docs/raid.md` (client projects) | project start | weekly (skill `eng-delivery`) |
| `docs/handover.md` | before anyone leaves | completed and proven at handover |

## When each document is written
1. **Discovery**. Understand the business first, alongside skill `eng-delivery`:
   - stakeholders and roles;
   - processes as they work today and as they will work with the system;
   - pain points and success measures.

   Write `requirements.md` and `glossary.md` and get them confirmed. Never build on unconfirmed requirements; mark open items **TO CONFIRM**.
2. **Design**: architecture, ADRs and the data model. Draft the test plan from the requirements, so every requirement has planned test cases.
3. **Every change** (part of the Definition of Done). In the same pull request, update whichever of these the change touches:
   - requirements, if behaviour changed;
   - test cases and the traceability matrix;
   - the user manual pages, for a user-visible change;
   - the runbook, for an operational change;
   - the CHANGELOG `Unreleased` section.

   Then add a progress-log entry file. If a document was not updated, the PR says why. The full Definition of Done is in skill `eng-delivery`.
4. **Release or UAT**: the test completion report, the user manual's "What's new" and version, and the release notes.
5. **Handover**: the handover checklist completed, with a new owner who has set the project up and deployed to UAT using the docs alone.

## Rules
- **Requirement ids link everything.** `REQ-nnn` appears in issues, PR descriptions, test cases and the manual's traceability column.
- **One source of truth.** Link instead of copying. Generate reference material from the code where the stack allows (OpenAPI, DocType or model definitions, CLI help).
- **History is append-only.**
  - Progress-log entries are dated and never rewritten; corrections are new entries. The one exception is redacting a leaked secret or personal data, which is noted in the entry (and the secret is rotated).
  - Requirements keep a change history.
  - ADRs are superseded, not edited.
  - Git keeps the detail.
- **Writing** (Google developer documentation style guide and Microsoft Writing Style Guide):
  - second person and active voice, conditions before instructions;
  - sentence-case headings, plain words, short numbered steps;
  - descriptive link text and alt text on images.
- **User manuals use Diátaxis**: tutorials, how-to guides, reference and explanation, never mixed on one page. Write one set per role and an admin guide for client administrators.
- **Screenshots** come only from synthetic data: a demo site or UAT records created for the purpose (the browser tools in skill `eng-testing` can take them). Refresh them at each release; never real or masked customer data, never secrets.
- **Business facts are confirmed, never invented.** Claude drafts documents from the code, the running app and the conversation, but rules, rates, policies and dates are confirmed by the client or the user.
- **Never put secrets in docs.** Docs say where credentials live, never their values.
- **Publishing**: Markdown in the repo is enough. Publishing docs anywhere outside the repo is outward-facing: the user approves it, and client documents stay behind access control. For a docs site use Docusaurus 3 or MkDocs 1.6. Material for MkDocs is in maintenance mode until 2027-05-05 and its successor (Zensical) is still alpha, so a new site on either needs an ADR. Use Mermaid for diagrams.
- **Requirements and test documents** follow the ideas of ISO/IEC/IEEE 29148 (requirements; 2018 edition, a revision is under way) and ISO/IEC/IEEE 29119-3 (test documentation, 2021), scaled to a small team.

## Bus-factor check (at every milestone)
- A new developer can set up, run the tests and deploy to UAT using only the README and the runbook.
- Every requirement has test cases and a latest result; every user-facing requirement has a manual page.
- The progress log is current, and every decision has an ADR or a log entry.
- Nothing is known by only one person: vendor contacts, server access, tricks and workarounds are written down, and secrets are in the vault.

Sources (checked 2026-11-04): diataxis.fr; arc42.org (template v9.1, October 2026); ISO/IEC/IEEE 29148:2018 (revision in progress); ISO/IEC/IEEE 29119-3:2021; developers.google.com/style; learn.microsoft.com/style-guide; docusaurus.io (3.10); mkdocs and squidfunk.github.io/mkdocs-material announcements; mermaid (12).
