# eng-os: global engineering system for Claude Code

A small, tested set of instructions, skills, rules and hooks that make every Claude Code session on this machine behave like a careful principal engineer: security first, evidence-based, autonomous on routine work, gated on risky work, and frugal with tokens.

Repo: wherever you cloned eng-os (`eng-os status` shows it; the maintainer's copy is `~/claude/eng-os`), the source of truth. Live copies: `~/.claude/`. **Installing on another machine or for a teammate: [INSTALL.md](INSTALL.md).** Built and verified against Claude Code **2.1.309** (desktop app) on 2026-11-03.

## 1. Design principles
1. **Deterministic where it matters, instructions where judgment is needed.** Dangerous actions are gated by a hook, not by hoping the model remembers a sentence.
2. **Pay only for what is used.** Always-loaded text is limited to rules that apply to every turn. Procedures live in skills, which load on demand. Stack rules are path-scoped and load only when matching files are touched.
3. **One source of truth.** Nothing is edited live. The repo is installed with backup, validation and rollback.
4. **Built on evidence.** Each component exists because a measurement or a doc-verified capability justified it. Things that turned out unnecessary were removed (see the decisions log).

## 2. Architecture

| Layer | Live location | Loads | Approx. cost | Purpose |
|---|---|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md` | every session, re-read after compaction | ~1.8k tokens | priority order, approval gates, engineering behaviour, security floor, skill routing table, git and token rules |
| Skills (9) | `~/.claude/skills/<name>/SKILL.md` | listing always (~0.9k tokens); body only when invoked; reference files only when the body sends Claude to them | 0.6–1.5k tokens each when used | procedures: `eng-design`, `eng-security` (+`stacks.md`, `standards.md`), `eng-testing`, `eng-review`, `eng-ship` (+`releases.md`), `frappe-erpnext`, `fintech-lending`, `eng-project-init`, `eng-os-review` |
| Standards register | repo `docs/SOURCES.md` | never in context | 0 | every external standard the skills cite, with edition, publication date, URL and the date it was last confirmed on the official site |
| Path-scoped rules (3) | `~/.claude/rules/*.md` | only when a matching file is read or edited | ~200–300 tokens each | must-follow invariants for Frappe code, DB migrations/SQL, CI/containers/infra |
| Guard hook | `~/.claude/eng-os/hooks/guard.py` (PreToolUse: Bash, file tools, `mcp__.*`) | every matching tool call, ~50 ms | 0 tokens unless it blocks | deny catastrophic actions; ask before destructive, irreversible, outward-facing, production and secret-exposing ones |
| Session hook | `~/.claude/eng-os/hooks/session_start.py` | session start | 0 tokens normally; one line when due | monthly self-audit reminder; warns if live files were edited outside an install |
| Settings keys | `~/.claude/settings.json` (merged, other keys untouched) | always | 0 | hook wiring, `attribution` off (commits under each developer's own identity), deny reading Claude's own OAuth file |
| Subagents | `~/.claude/agents/` (existing 4 kept) | when spawned | per run | `security-auditor`, `code-reviewer`, `test-engineer`, `web-performance-auditor` are used for fresh-context review; no new agents were needed |
| CLI + tests | `~/.claude/eng-os/bin`, `tests`, `templates` | never in context | 0 | install/verify/test/usage/eval/restore, project template |

**Always-loaded total added by eng-os: ~2.7k tokens** (CLAUDE.md plus skill listing). The installer also removed the ~1.7k-token listing of the 24 unused agent-skills and a SessionStart hook that ran in every session and injected nothing.

### Instruction hierarchy (conflict resolution)
1. Safety floor (approval gates + security floor in the global CLAUDE.md, enforced in part by the guard)
2. The user's explicit instruction in the current session
3. Project `CLAUDE.md` / `.claude/rules` (may tighten, never relax the floor)
4. Global CLAUDE.md defaults, then skills (procedures, not policy)

Material conflicts are followed at the higher level and reported in one line. The guard reads **only** global config (`~/.claude/eng-os/config.json`), so a project file can never switch a gate off.

### Why skills need a routing table
Across 700+ transcripts, the 24 previously installed generic skills were invoked by description **once**. Description matching alone is unreliable, so the global CLAUDE.md carries a 9-line trigger table, and project CLAUDE.md files name their required skills. Path-scoped rules handle the invariants that must apply without the model deciding to load anything.

## 3. The guard (deterministic safety layer)
Fail-open (a crash never blocks work; errors are logged to `~/.claude/eng-os/state/guard-errors.log`), Python 3.9-compatible, stdlib only, ~50 ms per call. 122 guard cases in `tests/guard_cases.json` plus 4 session-hook cases.

- **Deny** (the user can still run these by hand): wiping `/`, home or system dirs; `mkfs`/`dd` to disks; fork bombs; reading Claude's OAuth credentials or dumping the keychain; git commits carrying a `Co-Authored-By: Claude` trailer (your rule).
- **Ask** (approval prompt): force-push, direct push to protected branches (`main master prod production live uat release*`), `reset --hard`, `clean -f`, discarding changes, deleting branches; `gh pr merge`/repo delete/releases/secrets; DROP/TRUNCATE, UPDATE/DELETE without WHERE, writes to non-local databases; `bench drop-site/reinstall/restore`; docker volume deletion; terraform/kubectl/helm/aws/gcloud changes and deploys; package publishing; `sudo`; world-writable chmod; `curl | sh`; crontab/launchctl/authorized_keys changes; any state-changing SSH command (deploys, restarts, git pull, migrations, SQL, redirects, remote scripts) and reading remote secrets files; scp/rsync uploads and `rsync --delete`; recursive deletes outside the project/temp dirs, of whole repos, `.git`, or unexpanded variables; printing `.env`/keys/credentials files; writing content that looks like a real credential (except into `.env`); editing live global Claude config; SSH config. MCP: sending email/messages, calendar invites, sharing files, deletes in external services, Apollo sends and purchases, Meta Ads changes that set `ACTIVE` or change budgets/bids.
- Everything else passes silently.

Tune it in `global/eng-os/config.json` (protected branches, `disabled_rules`), then re-install.

## 4. Token-efficiency strategy
Measured baseline (last 30 days before install, `eng-os usage`): turn-1 context **~83k tokens** median, peak context ~387k median, cache-read share 98.5%, **subagents 40% of all input tokens** (almost all on Opus), 24% of `Read` calls were repeats, and skills were almost never invoked.

Levers built in:
- Lean always-loaded layer (above); procedures in skills; invariants in path-scoped rules.
- CLAUDE.md section 8 sets explicit rules: narrow reads, no re-reads, parallel calls, subagents only when justified, with `model: haiku/sonnet` for lookups and mechanical work, one task per session, CLI over MCP, result-first replies.
- `eng-os usage` makes waste visible (baseline context, cache share, subagent share and models, repeat reads, compactions, skills used, guard blocks), and the monthly review compares it over time in `docs/metrics.md`.

Recommended on the maintainer's machine, not applied (check yours with `eng-os usage`):
- `marketing-skills@marketingskills` is enabled globally (36 skills) but was not invoked in the analysed transcripts. Disable it globally (`"enabledPlugins": {"marketing-skills@marketingskills": false}`) and enable it per project where you do marketing work.
- The desktop org plugins (marketing, HR, product, sales…) and many claude.ai connectors (Apollo, Canva, Gamma, Gmail, Calendar, Drive…) are listed in every coding session. Toggle them off per session in the app's connector menu when coding.
- Effort: thinking is always on and the main model is Opus. For routine or mechanical sessions, `/effort medium` (or `"effortLevel": "medium"` in settings) cuts output and thinking tokens. Keep high effort for design, security and hard debugging. This is left as your per-session choice rather than a global default.
- The Homebrew CLI is 2.0.53 (the app bundles 2.1.309) and its OAuth login expired in July: `brew upgrade claude-code` then `claude /login` to use the terminal and `eng-os eval --run`.

## 5. Project-level instructions
- Template: `~/.claude/eng-os/templates/project/CLAUDE.md` (what, domain risk, **required skills**, stack, commands, architecture map, invariants, env/branch mapping, conventions, gotchas). Under ~120 lines; no repetition of global rules.
- `/eng-project-init` generates or refreshes it from repo evidence. Path-specific guidance goes in `.claude/rules/*.md` with `paths:`; personal notes go in a gitignored `CLAUDE.local.md`; long efforts get `docs/progress.md`.
- Loading facts (verified on 2.1.309): nested CLAUDE.md files load when a file in that folder is read by path (Read tool, `cat`, `sed`), but **not** for `ls`, `cd` or recursive grep. The global CLAUDE.md tells Claude to read them itself in those cases.

## 6. Evaluation and continuous improvement
| Command | Cost | What it checks |
|---|---|---|
| `eng-os verify` | 0 tokens | install drift, settings wiring, matcher coverage, hooks compile on both Pythons, guard error log, CLAUDE.md/skill/rule budgets, path scoping, duplicated sentences, standards in `docs/SOURCES.md` re-checked within 120 days |
| `eng-os test [--installed]` | 0 tokens | 122 guard cases + 4 session-hook cases in a throwaway sandbox |
| `eng-os usage --since D` | 0 tokens | efficiency metrics from local transcripts |
| `eng-os eval --prompt fresh-session` / `--transcript F` | one session | instruction loading, skill listing, nested CLAUDE.md, path rules, skill adherence, guard deny/ask in a real session |
| `eng-os eval --run` | small (Haiku, budget-capped) | headless guard and context scenarios (needs a logged-in CLI) |

The SessionStart hook reminds you when 30 days have passed since the last audit. `/eng-os-review` runs the measurements, checks Claude Code changes since the recorded version, and proposes changes on a branch with a CHANGELOG entry. Nothing is installed without your approval. Then `eng-os audit-done`.

## 7. Install, update, restore
```bash
cd <your eng-os clone>
bin/eng-os test                 # unit tests
bin/eng-os install --dry-run    # preview
bin/eng-os install              # backup -> stage -> validate -> apply -> verify (auto-rollback on failure)
bin/eng-os restore latest       # undo the last install (current state is backed up first)
bin/eng-os backups              # list backups (~/.claude/eng-os/backups/)
```
- To uninstall completely, restore the first `*-pre-install` backup: `bin/eng-os restore 20261103-232146-pre-install`. This also brings back the archived agent-skills pack.
- Update flow: edit the repo on a branch, run `test` and `install --dry-run`, review the diff, `install`, commit, add a CHANGELOG line.
- Hooks hot-reload: changes apply to running sessions immediately (verified).

## 8. Limitations (what Claude Code cannot guarantee)
- Instructions and skills are probabilistic: the model can still skip a skill or a rule. Only the guard and the permission settings are deterministic, and the guard only sees tool calls. It cannot stop a risky action hidden inside a script file it does not read, or code the model writes and then executes.
- The guard pattern-matches commands. Obfuscated or novel destructive commands can evade it. It is defence in depth on top of bypass mode, not a sandbox. For untrusted repos, use Claude Code's `sandbox` setting or a container.
- `ask` decisions need a human. In the desktop app they prompt even in bypass mode (verified). In headless `claude -p` nobody can answer, so they become denials. An unattended session that hits an ask waits for you.
- The hooks fail open. If `python3` is missing or the script crashes, tool calls proceed and the error is logged. `eng-os verify` reports it.
- Transcript formats are internal to Claude Code. `eng-os usage`/`eval` may need updates after upgrades; the monthly review catches this.
- Nothing here makes software "secure". It raises the floor and forces evidence; residual risk is always reported.
- The desktop app's own system prompt and org plugins are outside this config.

## 9. Decisions log
- **Replaced the agent-skills pack** (24 skills, 9 commands, 8 hook files) with 9 focused skills. It was invoked once in 700+ transcripts, and its SessionStart hook output used an invalid JSON shape, so it injected nothing. It is archived in the first backup and fully restorable. Its 4 agents were kept because they are used heavily (security-auditor 112 spawns).
- **Dropped project-CLAUDE.md injection from the guard** after a live test showed 2.1.309 loads nested CLAUDE.md on path reads natively. The hook was duplicating it.
- **No new subagents.** The built-in ones plus the existing four cover review, security, tests and exploration. Cost is controlled by per-call `model` instead.
- **Hook "ask" over hard deny** for anything that can be legitimate, so approval stays one click. Hard deny only for actions with no legitimate agent use.
- **Copy-install with manifest, not symlinks**: edits in the repo never go live unreviewed, and drift is detectable.
- **Standards are cited and dated (0.2.0)**: 0.1 wrote most engineering practice from model knowledge without sources. Every standard is now confirmed on its official site, recorded in `docs/SOURCES.md`, cited in the skill that uses it, and re-checked at each review. Long standard-specific detail lives in skill reference files (`standards.md`, `releases.md`), so the always-loaded cost stays the same.
- **Bypass mode kept**: it is your deliberate choice, and the guard plus deny rules supply the gates. `permissions.disableBypassPermissionsMode` is available if you ever want to forbid it.
