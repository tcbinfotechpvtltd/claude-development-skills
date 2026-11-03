# eng-os (source of the global Claude Code engineering system)

**What**: source of truth for `~/.claude/CLAUDE.md`, `~/.claude/skills/{eng-*,frappe-erpnext,fintech-lending}`, `~/.claude/rules/*`, `~/.claude/eng-os/` (hooks, CLI, tests) and the eng-os keys in `~/.claude/settings.json`.
**Required skills**: eng-review before committing changes here.

## Rules for changing this repo
- Edit only here, never the live copies (the guard asks before edits to live global config).
- Every always-loaded token is paid in every session: keep `global/CLAUDE.md` under 9,000 chars, skill descriptions under 600, skill bodies under 14,000; long material goes in skill reference files.
- No sentence may be duplicated across CLAUDE.md, skills and rules (`eng-os verify` checks).
- Never weaken a guard rule, approval gate or security instruction without the user's explicit agreement to that specific change.
- Guard changes need a matching case in `tests/guard_cases.json`. Fake secrets are built at runtime (`fake_secrets()`), never written literally.
- Hooks must stay Python 3.9 compatible (`/usr/bin/python3`), stdlib only, fail-open, and silent when nothing needs attention.

## Commands
| Purpose | Command |
|---|---|
| Unit tests (zero tokens) | `bin/eng-os test` (add `--python=$(which python3)` for 3.14) |
| Preview install | `bin/eng-os install --dry-run` |
| Install (backs up first) | `bin/eng-os install` — only with the user's approval |
| Health check | `bin/eng-os verify` |
| Undo last install | `bin/eng-os restore latest` |
| Usage metrics | `bin/eng-os usage --since YYYY-MM-DD` |
| Behavioural eval | `bin/eng-os eval --prompt fresh-session` / `--transcript F` / `--run` |

## Layout
`global/` mirrors what gets installed; `bin/` CLI; `tests/` guard cases + behavioural scenarios; `templates/project/` project CLAUDE.md template; `docs/` architecture, requirement map, verification report, metrics.
