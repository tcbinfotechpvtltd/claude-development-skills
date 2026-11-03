# Changelog
Material changes to the global system. Every install is also backed up under `~/.claude/eng-os/backups/`.

## 0.1.1 — 2026-11-03
- Guard: credential and secret-file rules now fire only when a printing/copying/sending command (`cat`, `cp`, `grep`, `curl @file`, `tar`…) names the file in its own arguments. Mere mentions (docs, heredocs, commit messages) no longer trigger. Found in live use: a heredoc writing this changelog was denied. 5 regression cases added.
- Frappe rule: prefer permission-aware `frappe.get_list` over `frappe.get_all` when results reach a user.

## 0.1.0 — 2026-11-03
- First install. Global CLAUDE.md (priority order, approval gates, engineering behaviour, security floor, skill routing, git, token rules).
- 9 skills: eng-design, eng-security (+stacks.md), eng-testing, eng-review, eng-ship, frappe-erpnext, fintech-lending, eng-project-init, eng-os-review.
- 3 path-scoped rules: frappe-erpnext, db-migrations, ci-deploy.
- Guard PreToolUse hook (deny/ask gates) and SessionStart hook (audit reminder, drift warning).
- Settings: hooks wired, `attribution` hidden, deny reading Claude's own OAuth credentials file; existing keys preserved.
- Archived (restorable): agent-skills pack skills/commands/hooks and its non-functional SessionStart hook. Agents kept.
- Removed before release: guard project-CLAUDE.md injection (native in 2.1.309, verified live).
