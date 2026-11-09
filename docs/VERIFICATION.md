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

The 122 guard cases cover allow, deny and ask for: git (force, protected-branch push, reset, clean, branch delete, co-author trailer), GitHub CLI, SQL (DROP, TRUNCATE, unscoped UPDATE/DELETE, remote DB writes), Frappe bench, docker, cloud/IaC, publishing, sudo/chmod/curl-pipe-sh/crontab, ssh mutations and remote secret reads, scp/rsync uploads, recursive deletes (system, home, outside project, whole repos, `.git`, unexpanded variables), secret file reads (Bash and Read), credential-looking writes (with `.env` and test-path exemptions), live global config edits, SSH config, MCP outward actions (email, calendar, sharing, deletes, Apollo, ad-platform activation/budget), plus false-positive regressions (mentions inside heredocs/echo). Session hook: silent on a fresh install, announces an overdue audit, stays silent on compact/resume, announces drift.

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

## 7. Release 0.2.0: sourced standards (2026-11-04)
| Check | Evidence | Result |
|---|---|---|
| Sources confirmed on official sites | 6 research subagents (Sonnet; WebSearch + WebFetch); 53 rows in `docs/SOURCES.md` with edition, date, URL; unconfirmed facts were left out or marked | **Done**; pages that refused automated access are noted per row (DPDP gazette, iso.org) |
| OWASP Top 10 latest | owasp.org project page and OWASP/Top10 repo show 2025 final as current; no 2026 web edition or draft. The 2026-labelled OWASP lists are LLM Top 10 2026 and Agentic Top 10 2026, both added | **Confirmed** |
| Unit tests after changes | `bin/eng-os test` on Python 3.9 and 3.14 | **126/126** both |
| Install | `bin/eng-os install` (backup `20261104-084319-pre-install`) | applied; `verify` 63 checks, 0 fail, 0 warn |
| Live reload | updated eng-security, eng-ship and fintech-lending descriptions appeared in the running session's skill listing right after install | **Verified** |
| Freshness check | copy of the repo with one row backdated to 2026-01-02 → `WARN ... stale Semantic Versioning`; real register → PASS | **Tested** |
| Token cost | always-loaded ~1,830 tokens (CLAUDE.md) + ~961 tokens (skill listing), about +60 over 0.1.1; new detail sits in reference files read only on demand | **Measured** |
| Not verified | skill adherence to the new standards in real work (measure at the next review); RBI text that governs each NBFC client after the Nov 2025 consolidation (client compliance owner decides) | open |

## 8. Release 0.3.0: install on another developer's machine (2026-11-04)
Simulated in a throwaway HOME containing a personal `CLAUDE.md`, a personal skill, a skill named like the old pack, and a settings file with its own `session-start.sh` hook and `model` key.
| Check | Result |
|---|---|
| No identity given and none in git config | install stops with the exact command to run; nothing written |
| Install with `--name/--email` | identity written into the commit rule; `user.json` saved; personal CLAUDE.md kept as section 9 (`personal.md`); personal skill, pack-named skill, own hook and `model` untouched; `verify` 64 checks, 0 fail, 0 warn |
| Restore the first backup | `diff -r` against the original `~/.claude`: identical (eng-os state dir excluded) |
| Invalid `settings.json` | install refused; file unchanged |
| Maintainer machine | reinstalled with his identity; second install "already up to date"; tests 126/126 on Python 3.9 and 3.14 |
| Shared files scanned | no personal paths, emails, IPs, account ids or key-shaped strings (only Anthropic's noreply address in test cases) |
| Not verified | Linux and WSL installs; a real second machine; Claude Code versions other than 2.1.309 |

## 9. Release 0.4.0: full area coverage (2026-11-04)
| Check | Result |
|---|---|
| Research | 5 research subagents (Sonnet) confirmed Odoo 17–20, app stacks, coding standards and GitHub security, delivery standards, test tooling on official sites; 48 new rows in `docs/SOURCES.md` (103 total); unconfirmed facts left out or marked |
| Unit tests | `bin/eng-os test`: 126/126 |
| Install | backup `20261104-115830-pre-install`; `verify` 82 checks, 0 fail, 0 warn (all new reference links resolve) |
| Token cost | always loaded ~1,970 tokens (CLAUDE.md) + ~1,100 tokens (12 eng-os skill descriptions), about +500 over 0.3.0 for three new skills and routing rows; new detail sits in on-demand files |
| Independent review | a fresh Sonnet reviewer found 12 issues (5 practical: missing `odoo-bin neutralize` on database copies, wrong `--reinit` description confirmed against the local Odoo 19 source, `NEXT_PUBLIC_*` vs build-once, PHPUnit forcing PHP upgrades, an incomplete Flutter build flag; 7 consistency); all fixed, reinstalled, `verify` 0 fail |
| Not verified | behaviour of the new skills in real Odoo, Next.js, Flutter and delivery work (measure with `eng-os usage` at the next review) |

## 10. Release 0.5.0: testing, documentation, delivery and company rollout (2026-11-04)
| Check | Result |
|---|---|
| Research | Four research subagents (Sonnet), plus the Claude Code docs guide, covered:<br>• browser MCP servers and test tools<br>• documentation standards (Diátaxis, arc42 9.1, ISO/IEC/IEEE 29148 and 29119-3, style guides)<br>• ERP implementation methods (Frappe, Odoo, Microsoft, SAP)<br>• organisation rollout (managed settings, plugins)<br><br>`docs/SOURCES.md` now has 129 rows. MCP flag names were confirmed against the official READMEs (`--isolated`, `--allowed-origins`, `--no-usage-statistics`, `--no-performance-crux`). The Frappe `disable-scheduler` command and the `mute_emails` key were confirmed in local Frappe source. |
| Independent review | A fresh Sonnet reviewer raised 12 findings, all fixed:<br>• three data tiers replace contradictory client-data rules<br>• the per-repo check no longer needs Python and is added only with approval<br>• CODEOWNERS covers `/.claude/` and `CLAUDE.md`<br>• one production approver<br>• a single Definition of Done, mirrored in the PR template<br>• missing templates added (ADR, RAID, project brief, decisions)<br>• the progress log is one file per entry, with redaction allowed<br>• Frappe copies are neutralized and requirements baselined<br>• vendors are stubbed for load and fuzz tests<br>• browser MCP isolation and telemetry flags<br>• tagged releases and bypass off by default<br>• a shorter `eng-docs` description<br><br>Kept by choice: the one-line "Sources" footers in skill files (about 50 tokens each, loaded only with their skill). |
| Installed-check hook | Tested in a temporary home: without eng-os it prints valid SessionStart JSON; with eng-os it prints nothing. |
| Unit tests | 126/126 |
| Install | `verify` 92 checks, 0 fail, 0 warn (the duplicate-sentence check caught and forced a reworded ERP pointer) |
| Token cost | Always loaded: about 2,080 tokens (CLAUDE.md) plus about 1,300 tokens (13 eng-os skill descriptions), roughly 3.4k in total. |
| Not verified | • Real-project use of the documentation and ERP method.<br>• The plugin and managed-settings rollout (documented, not built).<br>• Windows (the installed-check uses POSIX `sh`). |

## 11. Release 0.6.0: individual plans (2026-11-04)
| Check | Result |
|---|---|
| Plan facts | Confirmed by the Claude Code docs guide from code.claude.com data-usage, the privacy center and the Team plan pages:<br>• Pro and Max sessions, Claude Code included, are used for training when Model Improvement is on.<br>• Retention is 5 years with it on and 30 days with it off.<br>• The setting cannot be managed centrally.<br>• File-based managed settings and plugins state no plan requirement.<br>• Server-managed settings need Team or Enterprise. |
| Unit tests | 129/129 on Python 3.9 and 3.14. The 3 new cases cover the weekly update check (newer release announced, at most weekly, silent when current). |
| `eng-os update` end to end | Throwaway home and clone at v0.5.0 with a newer tag on its origin:<br>• switched to the latest tag, ran the tests, previewed and installed<br>• a second run reported "at release", asked, and installed nothing without a yes |
| Install on maintainer machine | `verify` 92 checks, 0 fail, 0 warn |

## 12. Release 0.7.0: skills apply automatically (2026-11-04)
| Check | Result |
|---|---|
| Mechanics | Confirmed in the Claude Code hooks, skills and memory docs:<br>• UserPromptSubmit and SessionStart accept `additionalContext` (10,000-character limit, not shown to the user).<br>• No hook can force a skill to load.<br>• Path rules load on Read/Write/Edit of matching files.<br>• Hook text should be phrased as facts. |
| Unit tests | 148/148 on Python 3.9 and 3.14 (13 new here, plus 6 for the personal trusted-projects guard option from the same release):<br>• Odoo, Next.js and lending detection; stacks one level down<br>• the home folder and workspace folders stay silent<br>• no lending match from template placeholders or skill names<br>• repos without a CLAUDE.md are offered `/eng-project-init`<br>• router: routes once per session, silent for small talk and slash commands |
| Router on 12 realistic requests | Each lending, ERPNext, Odoo, Next.js, manual, estimate, deploy, setup and Flutter/KYC request was routed to sensible skills. "Refactor this", "what does this regex do" and "rename a variable" stayed silent. The one gap found ("new Odoo module" without design) was fixed. |
| Detection on real projects | Run against the maintainer's real folders: an Odoo 19 install with an addons folder, an ERPNext bench, two Next.js apps, a Frappe app repo without a CLAUDE.md, a workspace holding many projects, and the eng-os repo. Every stack was recognised; the workspace and eng-os stayed silent after two false results found in this run were fixed. Nothing in the hooks names a specific project. |
| Install | `verify` 102 checks, 0 fail, 0 warn (the router wiring and compilation are checked) |
| Not verified | That Claude actually loads every named skill in real sessions. The hooks only name them, and the global instructions ask Claude to load them. The next sessions show it; measure with `eng-os usage` (skills column) at the review. |

## 13. Release 0.8.0: one-command install (2026-11-04)
| Check | Result |
|---|---|
| Fresh machine (throwaway home with no eng-os or git identity; name and email from the environment) | cloned, switched to the latest release, ran the self-tests, installed: 13 skills, 9 rules, 3 hook events, identity written; `verify` 0 fail |
| Same command again | "updating", already up to date, identity remembered, no questions |
| No identity, piped, no terminal | stops with a clear message; nothing installed |
| The exact one-liner, against a bare copy of the repo with a newer release tag | first run installed that release; second run was already up to date; the clone sits on the release tag |
| Bug found and fixed | a fresh clone on `main` was mistaken for a maintainer copy because `main` is ahead of the last tag. Now only an existing copy with unreleased work (another branch, or commits not on origin/main) is left alone. The same rule applies in `eng-os update`. |
| Not verified | a real employee machine; Windows without WSL (not supported); private-repo sign-in prompts (depend on each person's GitHub setup) |

## 14. Release 0.8.1: shorter install command (2026-11-04)
| Check | Result |
|---|---|
| The shorter install command against the real private GitHub repo (throwaway home, GitHub login through `gh`) | cloned, installed v0.8.0: 13 skills, 9 rules; `verify` 102 checks, 0 fail, 0 warn |
| The update command `bash ~/.eng-os/install.sh` | "updating", release v0.8.0, 0 files changed |
| The install command run a second time | git stops with "already exists" before anything runs; nothing changes |
| Not verified | a real employee machine; Windows without WSL (not supported) |

## 15. Release 0.9.0: ideas adapted from superpowers (2026-11-09)
| Check | Result |
|---|---|
| Source read | obra/superpowers v7.0.2 (released 2026-11-03): its 15 skills, the startup hook, the README, the brainstorming server and its telemetry |
| Budgets | global CLAUDE.md about 8,950 of 9,000 characters; every skill body under 14,000; always-loaded text up by about 75 tokens per session (about 3,490 in total) |
| Independent review | A fresh Sonnet reviewer found no High issues, 6 Medium and 4 Low, all fixed:<br>• the user's go-ahead on a plan covers local commits only, and push, PR and other outward steps still need a yes<br>• subagent briefs state their limits<br>• discard covers local work only and checks for uncommitted changes first<br>• review replies are drafted and posted only with approval<br>• pressure tests use plan-only subagents, are marked indicative, and can never shorten a gate or security rule<br>• the model rule says to leave `model` out for design and review work<br>• quarantine needs a note and the user told<br>• backups are restored to a scratch environment<br>• tasks may say "Test first: n/a" with a reason<br>• the router no longer fires on "break this down for me" (test added; the old pattern matched it) |
| Tests and verify | `bin/eng-os test` 155/155 (new cases: "implementation plan" routes to `eng-design`; "break this down for me" does not); installed into a throwaway home, `verify` 103 checks, 0 fail, 0 warn, including the new reference-file link and no duplicated instructions |
| Not verified | whether the red-flags tables change behaviour in real sessions; the first pressure tests at the next eng-os review will show it |

