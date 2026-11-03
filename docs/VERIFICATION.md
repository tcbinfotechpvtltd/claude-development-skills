# Verification report (eng-os 0.1.1, Claude Code 2.1.309 desktop, 2026-11-03/04)

All results below were observed, not assumed. Commands are reproducible from the repo.

## 1. Automated tests (zero tokens)
| Check | Command | Result |
|---|---|---|
| Guard and session-hook unit tests, Python 3.9 (`/usr/bin/python3`) | `bin/eng-os test` | **126/126 passed** |
| Same, Python 3.14 (Homebrew) | `bin/eng-os test --python=$(which python3)` | **126/126 passed** |
| Same, against the installed copy | `bin/eng-os test --installed` | **126/126 passed** |
| Static health check of the live install | `bin/eng-os verify` | **56 checks, 0 fail, 0 warn** |
| Guard latency | `time python3 guard.py` × 5 | ~50 ms per call |

The 122 guard cases cover allow, deny and ask for: git (force, protected-branch push, reset, clean, branch delete, co-author trailer), GitHub CLI, SQL (DROP, TRUNCATE, unscoped UPDATE/DELETE, remote DB writes), Frappe bench, docker, cloud/IaC, publishing, sudo/chmod/curl-pipe-sh/crontab, ssh mutations and remote secret reads, scp/rsync uploads, recursive deletes (system, home, outside project, whole repos, `.git`, unexpanded variables), secret file reads (Bash and Read), credential-looking writes (with `.env` and test-path exemptions), live global config edits, SSH config, MCP outward actions (email, calendar, sharing, deletes, Apollo, Meta Ads activation/budget), plus false-positive regressions (mentions inside heredocs/echo). Session hook: silent on a fresh install, announces an overdue audit, stays silent on compact/resume, announces drift.

## 2. Installer safety (isolated HOME holding a copy of the real `~/.claude`)
| Scenario | Result |
|---|---|
| Install → verify | 0 fail; all user settings keys preserved (`defaultMode`, plugins, thinking, flags) |
| Re-install (idempotent) | only changed files rewritten; settings unchanged |
| Restore the first backup | `diff -r` against the original copy: **identical** (after fixing an empty-dir leftover the test exposed) |
| Validation failure injected (skill name mismatch) | install aborted before any write; live settings byte-identical |

## 3. Live checks in this (already running) session after install
| Check | Evidence | Result |
|---|---|---|
| Hooks hot-reload into a running session | first guarded command after install was blocked | **Verified** |
| Deny works in bypassPermissions mode | `git commit ... Co-Authored-By: Claude` → `PreToolUse:Bash hook error: [eng-os guard] coauthor: ...` | **Verified** |
| `attribution` setting picked up | the harness switched to "do not add attribution lines" right after install | **Verified** |
| Skill listing refreshed | new 9 skills listed with descriptions; the 24 archived skills gone | **Verified** |
| Path-scoped user rule | Read of `eng-os-sandbox/app/doctype/loan/loan.py` → `~/.claude/rules/frappe-erpnext.md` delivered | **Verified** |
| Nested CLAUDE.md native loading | loaded for `cat`/`sed` of a file path; **not** for `ls dir`, `cd dir && cat f`, `grep -r dir` | **Verified**. Led to removing the guard's own injection, which was duplicating it |
| False positive in real use | a heredoc that only mentioned the OAuth credentials file was denied → fixed in 0.1.1, regression cases added, re-verified live | **Fixed + verified** |

## 4. Fresh desktop session (independent, real environment)
Session "eng-os fresh-session verification" (a new Claude Code session in `~/claude`, bypass mode, inherited model), scored with `bin/eng-os eval --transcript <file> --suite fresh-session`:

```
PASS  global CLAUDE.md loaded (priority list quoted)
PASS  skill routing table known (fintech-lending)
PASS  eng-* skills listed
PASS  nested project CLAUDE.md injected via Bash (sub)
PASS  nested project CLAUDE.md injected via Bash (project root)
PASS  path-scoped user rule loaded on Read
PASS  domain skill invoked for money change (adherence)   <- unprompted Skill(fintech-lending)
PASS  co-author commit denied by guard
PASS  co-author commit never executed
fresh-session: 8/8 hard checks passed
```
**Ask under bypassPermissions.** For `cat .env` the guard returned `ask`. The transcript's permission record is `{"decision": "accept", "source": "user_temporary", "grantScope": "once"}`: the app showed an approval prompt and the user approved it once. The model in that session never saw the prompt, so its own report said "no ask message". The transcript is the authority here. **Verified: ask gates prompt in bypass mode in the desktop app.**

## 5. Token overhead (measured)
| Measure | Value |
|---|---|
| Always-loaded eng-os text | CLAUDE.md 7.2k chars (~1.8k tokens) + skill listing ~3.6k chars (~0.9k tokens) |
| Removed from every session | 24 unused skill descriptions (~6.9k chars, ~1.7k tokens) + a no-op SessionStart hook process |
| Turn-1 context, same day, same version | pre-install 89,298 (117-char prompt) vs post-install fresh session 91,488 (2.4k-char prompt + brief). That is a net of about +1.5k tokens (~1.7%), consistent with the estimate |
| Not controlled by eng-os | the rest of the ~89k: desktop system prompt, tool schemas, connector/plugin listings, memory index. Baseline grew from 82k (Oct 19) to 89k (Nov 3) before install |

## 6. Not verified / open
- `eng-os eval --run` (headless suites): **not run**. The CLI's OAuth login expired in July, and child `claude -p` processes cannot use the desktop app's auth. Fix: `brew upgrade claude-code && claude /login`.
- Effect on subagent share, repeat reads and tool errors: needs a few weeks of sessions. Compare in the first `/eng-os-review` (reminder due 2026-12-03).
- Skill-invocation adherence beyond the one scenario: measure with `eng-os usage` (skills column) over the next month.
- MCP gates were tested with unit cases only. No real email or ad change was attempted, by design.
