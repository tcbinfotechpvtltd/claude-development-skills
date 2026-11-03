---
name: eng-os-review
description: Periodic self-evaluation and improvement of the eng-os global Claude Code system (CLAUDE.md, skills, rules, hooks, settings). Use when the SessionStart note says the audit is due, when the user asks to review or improve their Claude setup, or after a Claude Code upgrade.
---

# eng-os review

Evidence first, change second, never silently. Critical global config changes are proposed and installed only with the user's explicit approval.

## 1. Measure (zero or low tokens)
Run from anywhere:
```
E=~/.claude/eng-os/bin/eng-os
$E status
$E verify                      # drift, wiring, budgets, duplication
$E test --installed            # guard + session hook unit tests
$E usage --since <last_audit>  # tokens, cache, subagents, repeat reads, guard blocks, skills used
```
Compare with the previous rows in `<repo>/docs/metrics.md` (repo path: `$E status`). Look for:
- Baseline context at turn 1 rising (new plugins, MCP servers, skills, longer CLAUDE.md).
- Subagent share of input tokens, repeated reads, tool errors, compactions.
- Skills never invoked (description or trigger table wrong, or skill not needed), or invoked when irrelevant.
- `guard-errors.log` entries and guard decisions in transcripts: false positives (annoying asks) and misses (risky commands that ran without a gate).

## 2. Check for drift in the platform
- `claude --version` / desktop version vs the version recorded in `docs/metrics.md`.
- Ask one `claude-code-guide` subagent for changes since that version that affect: CLAUDE.md/rules loading, skills frontmatter and listing budget, hook events and output schema, permission modes, subagent frontmatter. Ask for a short answer with doc URLs only.
- Note deprecated settings or new capabilities that would remove custom code (prefer built-ins over eng-os code).

## 3. Optional behavioural eval (costs tokens; ask first)
`$E eval --run` executes the scenarios in `tests/scenarios.json` with `claude -p` (needs a logged-in CLI). `$E eval --transcript <file>` scores an existing session transcript. Report pass/fail per scenario with token cost.

## 4. Propose
- Write findings: what is working (with numbers), what is not, proposed changes with expected effect on tokens, safety and adherence.
- Make the changes in the repo on a branch (`git -C <repo> switch -c review-YYYY-MM`), update `CHANGELOG.md` and bump `VERSION`, run `bin/eng-os test` and `bin/eng-os install --dry-run`.
- Never weaken a security gate, approval requirement or test rule to reduce friction without the user explicitly agreeing to that specific trade-off.
- Show the user the diff summary and ask for approval to install.

## 5. After approval
`bin/eng-os install` (backs up first; `eng-os restore latest` undoes it), then `eng-os verify`, commit in the repo, append a row to `docs/metrics.md`, and run `eng-os audit-done`.
