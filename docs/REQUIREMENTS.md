# Requirement → implementation map

Status legend. **Verified**: observed working in a live Claude Code 2.1.309 session. **Tested**: automated test passes, zero tokens. **Implemented**: exists and was reviewed, but there is no automated proof. **Limited**: Claude Code cannot guarantee it; the best available alternative is noted.

## Core objectives
| # | Requirement | Implementation | Status |
|---|---|---|---|
| 1 | Complete engineering OS across all projects and sessions | User-level `~/.claude/CLAUDE.md`, skills, rules, hooks, settings: they apply to every project on this machine, CLI and desktop | Verified (fresh session, see VERIFICATION.md) |
| 2 | Research official docs and industry sources | Claude Code docs checked by a docs agent (memory, skills, hooks, settings, subagents, plugins, costs, headless); OWASP Top 10:2025 and RBI DL Directions 2025 checked by web search; findings drove the decisions log in README §9 | Implemented |
| 3 | Analyse my real environment and projects | Inventory of `~/.claude`, 33 projects in `~/claude` (Frappe ×8, Next.js ×6, Odoo, Flutter, PHP CI3, static sites), 700+ transcripts with `eng-os usage`; the draft `claude-playbook/CLAUDE.global.md` was folded in | Implemented |
| 4 | Don't blindly follow my assumptions | Built on evidence: removed the unused skill pack, dropped my own context-injection hook once a live test showed it duplicated native behaviour, kept agents that data showed were used | Implemented |
| 5 | Ask only when needed | CLAUDE.md §2: autonomous by default, an explicit list of ask-first cases, "money/legal/compliance: never guess" | Implemented (instruction-level) |

## Engineering standards (§4)
| Discipline | Where | Status |
|---|---|---|
| Design, architecture, DDD, trade-offs, ADRs, specs | `eng-design` | Implemented |
| Application and infrastructure security, OWASP Top 10:2025, ASVS-style checklist, threat modelling, stack pitfalls | `eng-security` + `stacks.md`, CLAUDE.md §4, guard | Implemented; guard Tested + Verified |
| Database architecture and migrations | `eng-design` (data), rule `db-migrations` (path-scoped), guard SQL gates | Rule loading Verified (same mechanism as Frappe rule); guard Tested |
| Performance and scalability | `eng-design` (10x design, bottleneck), `eng-ship` (RED metrics); existing `web-performance-auditor` agent | Implemented. No dedicated perf skill, by choice: the old one was never used |
| Cloud, DevOps, CI/CD, deploy, rollback | `eng-ship`, rule `ci-deploy`, guard infra/deploy/ssh gates | Implemented; guard Tested |
| Testing, QA, debugging | `eng-testing`, CLAUDE.md §3/§5, `test-engineer` agent | Implemented |
| Observability, reliability, incidents, backups | `eng-ship` | Implemented |
| API design and integrations | `eng-design` (APIs, integrations), `fintech-lending` (vendor adapters, webhooks) | Implemented |
| Maintainability, tech debt, governance, docs | CLAUDE.md §3, `eng-review`, ADR template, project template | Implemented |
| Domain: Indian lending, ERPNext/Frappe | `fintech-lending`, `frappe-erpnext` skill + path rule | Frappe rule Verified; skills Implemented |

## Behaviour (§5)
| Requirement | Where | Status |
|---|---|---|
| Understand before modifying; root cause; reproduce | CLAUDE.md §3, `eng-testing` | Implemented (instruction) |
| Requirements and trade-offs before significant work | CLAUDE.md §3, `eng-design` | Implemented |
| Preserve compatibility; no unrelated changes, deps or abstractions | CLAUDE.md §3 | Implemented |
| Critical self-review; verify with evidence; no false completion | CLAUDE.md §3/§5, `eng-review` report format | Implemented |

## Security and risk (§6, §15A)
| Requirement | Where | Status |
|---|---|---|
| Never expose credentials | CLAUDE.md §4; guard: secret-file reads ask, credential-looking writes ask, Claude OAuth file denied (settings deny + guard) | Tested; deny Verified live |
| No destructive / prod / irreversible git / shared infra actions without approval | Guard deny/ask rules (README §3) + CLAUDE.md §2 | Tested (122 cases); deny Verified live; ask Verified in the fresh session (prompt shown under bypass mode, approved once by the user) |
| Don't bypass security controls or disable tests | CLAUDE.md §1/§2/§3 ("never route around the guard") | Implemented (instruction) |
| Projects can't silently weaken security | Priority order (CLAUDE.md §1); the guard reads only global config, never project files | Tested (by design: no project-level switch exists) |
| Outward-facing and financial MCP actions gated | Guard MCP rules (email, calendar, sharing, deletes, Apollo, Meta Ads activation/budget) | Tested |

## Token efficiency (§7, §15B)
| Requirement | Where | Status |
|---|---|---|
| Lean always-loaded layer | CLAUDE.md 7.2k chars (~1.8k tokens); skill listing ~0.9k tokens; rules path-scoped | Tested (`eng-os verify` budgets) |
| Selective loading | 9 skills (bodies only on invoke), 3 path-scoped rules, skill reference files | Rule Verified; skill listing Verified |
| Avoid repeated exploration and doc loading | CLAUDE.md §7 (record project knowledge), §8 (narrow reads, no re-reads); project template + `eng-project-init` | Implemented |
| Subagents, parallelism, model and effort choice | CLAUDE.md §8 (when to delegate, `model` per call) | Implemented. Effect measurable with `eng-os usage` (subagent share baseline 40.5%) |
| Measure it | `eng-os usage` (turn-1 context, cache %, subagent share and models, repeat reads, compactions, skills, guard blocks); `docs/metrics.md` | Tested on 700+ real transcripts |
| Remove waste found | Archived 24 unused skills + 9 commands + no-op SessionStart hook | Verified (skills gone from listing in fresh session) |

## Persistence and architecture (§8)
| Requirement | Where | Status |
|---|---|---|
| Global CLAUDE.md, skills, rules, hooks, settings | `~/.claude/...` via `eng-os install` | Verified |
| Project-specific architecture that complements global | Template, `eng-project-init`, `.claude/rules` with `paths:`, `CLAUDE.local.md`, required-skills line | Implemented; nested CLAUDE.md loading Verified (path reads; gap documented for ls/cd/grep) |
| No duplication across files | `eng-os verify` duplicate-sentence check | Tested |
| Don't assume skills auto-activate | Routing table in CLAUDE.md + project "required skills" + path rules for must-apply invariants | Verified once: the fresh session invoked `fintech-lending` unprompted for a money change. Ongoing rate measurable with `eng-os usage` |

## Continuous improvement (§9, §15C)
| Requirement | Where | Status |
|---|---|---|
| Measurable criteria | `verify`, `test`, `usage`, `eval` (README §6) | Tested |
| Practical test scenarios | `tests/guard_cases.json` (126 cases), `tests/scenarios.json` (fresh-session + 2 headless suites) | Tested / fresh-session scored |
| Periodic evaluation without auto-modifying critical config | SessionStart reminder after 30 days, `/eng-os-review` (proposes on a branch, installs only on approval), guard asks before direct edits to live global config | Tested (reminder, drift); live-config ask Tested |
| Version history and record of changes | git repo, `CHANGELOG.md`, `VERSION`, `docs/metrics.md` | Implemented |

## Resilience (§15E)
| Requirement | Where | Status |
|---|---|---|
| Back up before changes | Every install/restore writes a backup first | Tested (isolated HOME) + used for real (3 backups) |
| Recoverable versions, documented restore | `eng-os restore [id|latest]`, README §7 | Tested: restore of the first backup produced a byte-identical tree |
| Failed update leaves no inconsistent state | Stage, then validate, then apply; auto-rollback on exception; validation failure aborts before any write | Tested (injected invalid skill: aborted, live settings unchanged) |

## Honest limitations (§13, §15F)
| Requirement | Why it cannot be guaranteed | Best alternative in place |
|---|---|---|
| "Always" follow instructions and load the right skill | LLM adherence is probabilistic | Deterministic guard for the dangerous subset; routing table; path rules; measured adherence in eval |
| Maximum security | Pattern guards can be evaded; there is no OS sandbox in bypass mode | Defence in depth; recommend `sandbox` or containers for untrusted code |
| Persistence across all projects | Applies on this machine and user account only; cloud sessions and other machines need their own install | Repo is portable: clone it and run `bin/eng-os install` |
| Headless eval (`eng-os eval --run`) | CLI OAuth expired; Homebrew CLI is 2.0.53 | Fresh desktop session used instead; `brew upgrade claude-code && claude /login` enables it |
