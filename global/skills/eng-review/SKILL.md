---
name: eng-review
description: Pre-commit, pre-PR and pre-handoff review protocol with severity rubric and "audit until dry" loop. Use before committing, opening or merging a PR, handing work to devops or a client, when asked to review code or a diff, or when auditing an existing codebase.
---

# Review and verification

## 1. Self-review every change before calling it done
Read the full diff (`git diff` / `git diff --staged`), not your memory of it, plus enough surrounding code for context. Check:
- **Design** (the most important item): does the change belong here, fit the architecture, and interact sensibly with the rest of the system?
- **Complexity**: no more than the problem needs; no speculative features or abstractions "for later".
- **Correctness**: does it meet each acceptance criterion? Edge cases, error paths, concurrency, timezones, rounding.
- **Scope**: no unrelated edits, debug prints, commented-out code, stray files, formatting churn, secrets, generated artifacts.
- **Security**: the section 2 checklist of skill `eng-security` for anything touching auth, input, data or integrations.
- **Compatibility**: public APIs, schemas, config keys, URLs, and data formats unchanged or migrated.
- **Quality**: clear names, comments that explain why, duplication, function size, error handling, logging without PII, consistency with the codebase and its style guide ([coding-standards.md](coding-standards.md): official guide, formatter and linter per language); docs updated when behaviour or setup changes.
- **Tests**: new behaviour and fixed bugs covered; suites actually run with results.
- **Ops**: migration, config/env changes, feature flags, rollback documented.

## 2. Independent review (fresh context)
Use for security-sensitive, money-moving, schema-changing or large changes, and before any production handoff:
- `code-reviewer` subagent for general quality; `security-auditor` for security; `test-engineer` to find untested paths. If one is not installed, use a general-purpose subagent and brief it as that reviewer.
- Brief them with: the goal, the diff or file list, the risk areas, and what you already verified. Ask for findings with file:line, severity and a concrete fix. Do not hand them your conclusions to confirm.
- Treat their findings as claims: verify each one against the code before fixing or dismissing it.

## 3. Audit until dry (for audits and pre-handoff)
1. Review → list findings with severity.
2. Fix confirmed Critical/High (and cheap Mediums); add regression tests.
3. Re-review the fixed areas and their neighbours with fresh context.
4. Repeat until a pass produces no new Critical/High findings. Report the number of passes and the remaining open items.

## Severity rubric
| Severity | Meaning | Examples |
|---|---|---|
| Critical | Exploitable now or data/money loss likely | auth bypass, IDOR on KYC/loan data, SQLi, RCE, secret in repo, wrong disbursal amount |
| High | Serious under realistic conditions | missing webhook signature check, privilege escalation by staff, race condition on balance, no backup before destructive migration |
| Medium | Defence-in-depth gap or correctness issue with workaround | missing rate limit, verbose errors, missing index on hot query, unhandled vendor timeout |
| Low | Hygiene | naming, minor duplication, missing docs |

## 4. Report format
```
Status: implemented | tested | verified (say which, with evidence)
Changed: <files / behaviour, one line each>
Verified: <commands run + results>
Not verified / risks: <honest list>
Next: <only if something remains>
```
For reviews: findings sorted by severity, each `file:line — problem — impact — fix`, then a one-line verdict (ship / ship after fixes / do not ship).
Reviewing someone else's change (Google eng-practices): approve once it clearly improves overall code health, even if imperfect; never approve one that makes it worse. Technical facts and data beat opinion; the style guide settles style. Prefix optional points with `Nit:`, and say what was done well.

## 5. Commit and PR
- Commit only verified work; one logical change per commit; message explains why. Author and trailer rules are in the global CLAUDE.md.
- Keep PRs small and self-contained; refactors separate. Commit format, PR template, branch lifetime and changelog rules: [releases.md](../eng-ship/releases.md).
- PR description: problem, approach, risk areas, how it was tested, rollback, screenshots for UI. Link the spec/ADR when one exists.

Sources (checked 2026-11-04): google.github.io/eng-practices (reviewer standard, what to look for, small CLs).
