---
name: eng-review
description: Reviews work before it leaves your hands — self-review checklist, independent reviews, severity rubric and audit until dry. Use before a commit, PR, merge or handoff; when asked to review code, a diff or a PR; or when auditing a codebase.
---

# Review and verification

## Core rules
- Before saying "done", read the whole diff: design fit, correctness, scope, security, compatibility and tests.
- Strip debug prints, commented-out code, stray files and secrets before a commit.
- Changes to money, auth, KYC, schemas or production get an independent reviewer subagent; check each of its findings against the code before acting.
- Review comments are claims: verify them, push back with evidence, and skip performative agreement.
- Report a finding only once its path is reachable and its impact concrete; an unconfirmed one goes in as "needs validation", with no severity.
- State the status as implemented, tested or verified, with the commands that were run and what was not verified.
- One logical change per commit, with a message that explains why.

## 1. Self-review every change before calling it done
Read the full diff (`git diff` / `git diff --staged`), not your memory of it, plus enough surrounding code for context. Check:
- **Design** (the most important item): does the change belong here, fit the architecture, and interact sensibly with the rest of the system?
- **Complexity**: no more than the problem needs; no speculative features or abstractions "for later".
- **Correctness**: does it meet each acceptance criterion? Edge cases, error paths, concurrency, timezones, rounding.
- **Scope**: no unrelated edits, debug prints, commented-out code, stray files, formatting churn, secrets, generated artifacts.
- **Security**: the section 2 checklist of skill `eng-security` for anything touching auth, input, data or integrations.
- **Compatibility**: public APIs, schemas, config keys, URLs, and data formats unchanged or migrated.
- **Quality**: clear names, comments that explain why, duplication, function size, error handling, logging without PII, consistency with the codebase and its style guide ([coding-standards.md](coding-standards.md): official guide, formatter and linter per language); docs updated when behaviour or setup changes (requirements, test cases, user manual, runbook, CHANGELOG, progress log: skill `eng-docs`).
- **Tests**: new behaviour and fixed bugs covered; suites actually run with results.
- **Ops**: migration, config/env changes, feature flags, rollback documented.

## 2. Independent review (fresh context)
Use for security-sensitive, money-moving, schema-changing or large changes, and before any production handoff:
- `code-reviewer` subagent for general quality; `security-auditor` for security; `test-engineer` to find untested paths. If one is not installed, use a general-purpose subagent and brief it as that reviewer.
- Brief them with: the goal, the diff or file list, the risk areas, and what you already verified. Ask for findings with file:line, severity and a concrete fix. Do not hand them your conclusions to confirm.
- Ask for every finding with its severity and filter in a later pass. Never tell a reviewer what not to flag or that the change is safe: a reviewer told what to expect finds that.
- Hand over the diff from a recorded base (`git diff <base>...HEAD`, never `HEAD~1`), without generated or lock files. A reviewer reviews; it does not edit code or start further subagents.
- Judge a diff by risk, not size: a "small refactor" that touches auth, money or a permission check is high risk. For deleted security code, `git blame` why it was there; count the callers of a changed function.
- Treat their findings as claims: verify each one against the code before fixing or dismissing it.
- Large or risky changes get the review in two parts, each in its own fresh context: one against the coding standards (section 1), one against the spec and its acceptance criteria.

### Receiving review feedback (from a person, a bot or a subagent)
- Read every comment before changing anything, then work in severity order.
- Check each one against the code (trace it, reproduce it, or run the test):
  - **Correct**: fix it, with a test when it is a behaviour bug.
  - **Wrong**: explain why with the evidence (file:line, a test, the spec) and leave the code as it is.
  - **Unclear**: ask the user (or the reviewer, if the user says so) before touching the code; a guessed fix is worse than a question.
- No performative agreement ("great catch", "you're absolutely right"): say what changed and where, or why nothing changed.
- A suggestion that conflicts with the spec, a security rule or a decision the user already made goes to the user, not into the code.
- "Make it more complete" for something nothing calls: grep for callers first; if there are none, propose removing it instead.
- One fix at a time, tests re-run after each. Draft a reply per comment (what changed and where, or the evidence for leaving it); post replies on the PR only when the user approves.

### Red flags before saying "done"
| The thought | The rule |
|---|---|
| "That should fix it" | Nothing is fixed until a command shows it. Run it and quote the result. |
| "The subagent says the tests pass" | Its report is a claim: read its diff and run the tests yourself. |
| "Too small to need a review" | Small diffs hide debug prints, stray files and secrets. Read it. |
| "The tests were green earlier" | Earlier is not now. Re-run after the last change. |
| "I'll mention the failing check later" | Report it now, with the output. |
| "The user is in a hurry, so skip the gate" | Approval gates do not bend for speed: state the risk, ask, and offer the safe path. |

## 3. Audit until dry (for audits and pre-handoff)
1. Review → list findings with severity.
2. Fix confirmed Critical/High (and cheap Mediums); add regression tests.
3. Re-review the fixed areas and their neighbours with fresh context.
4. Repeat until a pass produces no new Critical/High findings. Report the number of passes and the remaining open items.

A whole-repo audit lists every top-level folder as reviewed or set aside, with the reason, so the report says what it did not cover. Nothing is left undone by calling it pre-existing or out of scope without saying so.

### Before a finding goes in the report
- **Boundary and result**: keep it only if someone with less trust can cross a real boundary to a concrete result (another tenant's record, money moved, code run). A missing best practice with no such path is a hardening note.
- **Proof**: who controls the input, is the path reachable, what is the real impact, and one negative case. An IDOR shows another user's data in the response, not just a 200. An SSRF shows the server calling an address you control. A 400 from input validation does not prove a missing auth check: resend a well-formed body.
- **Independent check** for Critical and High: a fresh subagent briefed to refute the finding, given the finding alone and not your reasoning. If it raises the severity, a second fresh one checks that.
- **Not confirmed**: report it as *needs validation*, naming the missing fact and how the owner can check it, with no severity. Never write "could potentially".
- **Evidence**: reproduce it from a fresh session; give the exact request or steps; mask your own tokens and other people's personal data.
- **Scope**: a diff review reports what the change introduces. Risky old code on a touched path is listed separately.
- A rule that is broken mechanically (a banned call, formatting, a missing header) gets a linter, hook or CI check rather than another review comment; judgement calls go in the standards.

## Severity rubric
| Severity | Meaning | Examples |
|---|---|---|
| Critical | Exploitable now or data/money loss likely | auth bypass, IDOR on KYC/loan data, SQLi, RCE, secret in repo, wrong disbursal amount |
| High | Serious under realistic conditions | missing webhook signature check, privilege escalation by staff, race condition on balance, no backup before destructive migration |
| Medium | Defence-in-depth gap or correctness issue with workaround | missing rate limit, verbose errors, missing index on hot query, unhandled vendor timeout |
| Low | Hygiene | naming, minor duplication, missing docs |

High fully defeats a control; Medium weakens one. If you cannot name the concrete damage, go one level lower.

## 4. Report format
```
Status: implemented | tested | verified (say which, with evidence)
Changed: <files / behaviour, one line each>
Verified: <commands run + results>
Not verified / risks: <honest list>
Next: <only if something remains>
```
For reviews: findings sorted by severity, each `file:line — problem — impact — fix`, tagged by evidence (**read** in the code, **inferred**, or **unverified**), then a one-line verdict (ship / ship after fixes / do not ship).
Reviewing someone else's change (Google eng-practices): approve once it clearly improves overall code health, even if imperfect; never approve one that makes it worse. Technical facts and data beat opinion; the style guide settles style. Prefix optional points with `Nit:`, and say what was done well.

## 5. Commit and PR
- Commit only verified work; one logical change per commit; message explains why. Author and trailer rules are in the global CLAUDE.md.
- Keep PRs small and self-contained; refactors separate. Commit format, PR template, branch lifetime and changelog rules: [releases.md](../eng-ship/releases.md).
- PR description: problem, approach, risk areas, how it was tested, rollback, screenshots for UI. Link the spec/ADR when one exists.

Sources (checked 2026-11-04): google.github.io/eng-practices (reviewer standard, what to look for, small CLs).
