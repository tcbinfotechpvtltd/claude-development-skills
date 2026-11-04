# Installing eng-os (for TCB Infotech developers)

eng-os sets up Claude Code with TCB's engineering standards: global instructions, 9 skills, 3 path-scoped rules and a safety guard. It applies to every project you open with Claude Code on your machine. The architecture and the reasoning behind each piece are in [README.md](README.md).

## Requirements
- macOS or Linux. On Windows use WSL; native Windows has not been tested.
- Claude Code (desktop app or CLI). Verified on 2.1.309.
- `python3` 3.9 or newer on your PATH, and `git`.

## Install (about 5 minutes)
1. Put the repo somewhere permanent; installed copies point back to it. Clone the private TCB repo (ask the maintainer for access):
   ```bash
   git clone https://github.com/tcbinfotechpvtltd/claude-development-skills.git ~/claude/eng-os
   ```
   If you received a zip, unzip it to `~/claude/eng-os`.
2. Run the self-tests (no Claude tokens used). Expect `126/126 passed`:
   ```bash
   cd ~/claude/eng-os && bin/eng-os test
   ```
3. Preview the install with your own commit identity. It lists every file it will write:
   ```bash
   bin/eng-os install --dry-run --name="Your Name" --email=you@example.com
   ```
4. Install. Your current config is backed up first:
   ```bash
   bin/eng-os install --name="Your Name" --email=you@example.com
   ```
5. Start a new Claude Code session. Hooks and skills apply at once; the global instructions load in new sessions.
6. Check: `bin/eng-os verify` should end with `0 fail`. In a new session, ask Claude *"What is the instruction priority in your global CLAUDE.md?"*. It should start with the safety floor.

## What changes on your machine
| Path | Change |
|---|---|
| `~/.claude/CLAUDE.md` | Replaced by the TCB standards, with your name and email in the commit rule. **Your existing file is kept**: its text is saved to `~/.claude/eng-os/personal.md` and appended as section 9. To change it later, edit `personal.md` and re-install |
| `~/.claude/skills/` | Adds `eng-design`, `eng-security`, `eng-testing`, `eng-review`, `eng-ship`, `frappe-erpnext`, `fintech-lending`, `eng-project-init`, `eng-os-review`. A skill of yours with one of these names is replaced (it is in the backup). Your other skills are untouched |
| `~/.claude/rules/` | Adds 3 rules that load only when matching files are touched (Frappe code, DB migrations/SQL, CI/infra files) |
| `~/.claude/settings.json` | Merged; your other keys stay. Adds: a guard hook on tool calls, a session-start check, a deny rule on Claude's own login file, and `attribution` off (no Claude co-author lines) |
| `~/.claude/eng-os/` | Hooks, CLI, tests, templates, your `user.json` (identity) and backups |

Nothing else is touched: no project files, plugins, MCP servers or agents. Nothing is sent anywhere. `eng-os usage` reads only your local transcripts.

## What you will notice
- **Approval prompts** before risky actions, even in bypass mode. Examples: force-push or push to `main`/`prod`/`uat`, `reset --hard`, deploys, `DROP`/`TRUNCATE`, state-changing SSH, printing `.env` files, sending email, Meta Ads changes that spend money. Catastrophic commands (wiping home, dumping the keychain) are refused outright. In headless `claude -p` an approval prompt becomes a refusal, because nobody is there to answer.
- **Commit trailers**: commits carrying a Claude co-author trailer are blocked (TCB policy, `block_claude_coauthor` in `global/eng-os/config.json`).
- **Skills** load when the task matches, for example `fintech-lending` for anything that moves money. Project CLAUDE.md files can make skills mandatory.
- **Monthly review**: after 30 days, a start-of-session note asks you to run `/eng-os-review`.

## Optional
- The skills mention the `security-auditor`, `code-reviewer` and `test-engineer` subagents. They are not part of eng-os; without them Claude uses a general-purpose subagent briefed for the same job.
- Project knowledge (commands, architecture, gotchas) is not in eng-os. It belongs in each project's own `CLAUDE.md`; run `/eng-project-init` in a repo to create one.
- The guard only sees Claude's tool calls. For repos you do not trust, also use Claude Code's sandbox setting or a container.

## Updating and changing it
- Update: `git pull && bin/eng-os test && bin/eng-os install`. Your identity is remembered.
- Never edit the live copies in `~/.claude` (the guard asks first). Change the repo on a branch, run `bin/eng-os test`, and open a pull request for the maintainer. Everyone installs from the default branch.
- `docs/SOURCES.md` lists every external standard the skills cite, with the date each was last checked. `eng-os verify` warns when one is older than 120 days.

## Undo
- Undo the last install: `bin/eng-os restore latest`.
- Remove eng-os completely: `bin/eng-os backups`, then `bin/eng-os restore <id>` with the first `*-pre-install` backup. This restores your config as it was before eng-os.

## Troubleshooting
| Message | Fix |
|---|---|
| `commit identity unknown` | pass `--name="…" --email=…` once, or set `git config --global user.name/user.email` |
| `settings.json is not valid JSON` | fix `~/.claude/settings.json` first; the installer never overwrites a broken file |
| `verify` WARN about the guard error log | the guard hit an error and let the action through (it fails open). Send `~/.claude/eng-os/state/guard-errors.log` to the maintainer |
| `verify` WARN about stale standards | run `/eng-os-review` |
| hooks not running | check `python3 --version`; if Python is missing the hooks cannot run, and `verify` reports it |
