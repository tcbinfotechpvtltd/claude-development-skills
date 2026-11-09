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
- Stacks this machine works on that have no stack-specific skill: `~/.claude/eng-os/state/stacks-seen.json` (entries with `"skill": null`). A stack that keeps appearing across developers is a candidate for a new skill.
- `guard-errors.log` entries and guard decisions in transcripts: false positives (annoying asks) and misses (risky commands that ran without a gate).

## 2. Check for drift in the platform
- `claude --version` / desktop version vs the version recorded in `docs/metrics.md`.
- Ask one `claude-code-guide` subagent for changes since that version that affect: CLAUDE.md/rules loading, skills frontmatter and listing budget, hook events and output schema, permission modes, subagent frontmatter. Ask for a short answer with doc URLs only.
- Note deprecated settings or new capabilities that would remove custom code (prefer built-ins over eng-os code).

## 3. Re-verify cited standards
`eng-os verify` warns when a row of `<repo>/docs/SOURCES.md` was last checked more than 120 days ago. At every review, one research subagent (`model: sonnet`, WebSearch + WebFetch, official sites only, report under 600 words) confirms the latest edition and date of each row and lists new standards in the field (a new OWASP list, a NIST revision, an RBI direction or amendment, a DPDP rules phase). Update SOURCES.md, then every skill that cites a changed source. Adopt a new edition only after reading its content, not just its title; drafts are noted, not adopted.

## 4. Optional behavioural eval (costs tokens; ask first)
`$E eval --run` executes the scenarios in `tests/scenarios.json` with `claude -p` (needs a logged-in CLI). `$E eval --transcript <file>` scores an existing session transcript. Report pass/fail per scenario with token cost.

**Pressure-test changed and often-skipped rules.** Targets: every skill or rule changed since the last review, and those that `usage` or transcripts show being skipped.
1. For each target, brief a fresh subagent (`model: sonnet`) with a realistic task plus a pressure that tempts it to break the rule. Examples: a deadline, "it's tiny", the user asking to skip a step, or code already written without tests. Ask it to describe step by step what it would do and which commands it would run, with no tool use.
2. Run each scenario twice: once with the skill text in the brief and once without it. Subagents still see the installed instructions and skills, so treat the comparison as indicative only. For a clean run, add the scenario to `tests/scenarios.json` and run it with `$E eval --run`, which works in the eval sandbox.
3. Act on the result:
   - **Same behaviour both ways**: the rule may add nothing; consider shortening it. Never shorten an approval gate or a security rule (global CLAUDE.md sections 2 and 4) on this evidence alone.
   - **It argued its way around the rule**: add that argument and the answer to the skill's red-flags table, then run the scenario again.
4. Record the results in `docs/metrics.md`.

## 5. Propose
- Write findings: what is working (with numbers), what is not, proposed changes with expected effect on tokens, safety and adherence.
- Make the changes in the repo on a branch (`git -C <repo> switch -c review-YYYY-MM`), update `CHANGELOG.md` and bump `VERSION`, run `bin/eng-os test` and `bin/eng-os install --dry-run`.
- Never weaken a security gate, approval requirement or test rule to reduce friction without the user explicitly agreeing to that specific trade-off.
- Show the user the diff summary and ask for approval to install.
- Shared repo (it has a remote that other developers install from): with the user's approval, push the branch and open a PR for the maintainer instead of installing it locally; everyone installs from the default branch.

## 6. After approval
`bin/eng-os install` (backs up first; `eng-os restore latest` undoes it), then `eng-os verify`, commit in the repo, append a row (with your name) to `docs/metrics.md`, and run `eng-os audit-done`.
