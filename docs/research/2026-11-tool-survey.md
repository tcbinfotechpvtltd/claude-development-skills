# Survey of agent-tooling repos for eng-os (2026-11-09)

The user asked for 11 well-known repos to be analysed in depth, and their best ideas put into eng-os. Each repo was cloned and read by a separate research agent that ran none of its code. The key claims were then spot-checked against the clones and against the Claude Code docs (code.claude.com, fetched 2026-11-09). This file records what was found, what eng-os adopted, and what it rejected and why, so the reasoning survives.

## Verdicts
| Repo (version read) | Licence | What it is | Verdict for TCB |
|---|---|---|---|
| obra/superpowers (v7.0.2) | MIT | workflow skills: brainstorm, plan, subagent-per-task, TDD | ideas adapted in 0.9.0; not installed |
| affaan-m/ECC (v2.2.3) | MIT | 314 skills, 71 agents, about 28 hooks, many harnesses | not installed: size, hooks on every call, auto-update, no domain fit |
| mattpocock/skills (v1.3.2) | MIT | 29 engineering and productivity skills | ideas adapted; not installed (assumes an issue tracker per repo) |
| Graphify-Labs/graphify (v0.9.104) | Apache-2.0 | code knowledge graph, MCP, hooks | pilot only, code-only and offline ([MCP-POLICY.md](../MCP-POLICY.md)) |
| github/github-mcp-server (v2.1.0) | MIT | GitHub's official MCP server | approved read-only; `gh` preferred |
| upstash/context7 (4.5.1) | MIT client, closed service | hosted library docs | approved for Next.js and Flutter projects without customer data |
| microsoft/playwright-mcp (v0.0.84) | Apache-2.0 | browser automation over accessibility snapshots | approved, pinned, isolated |
| oraios/serena (v2.1.0) | GPL-3.0 (SolidLSP MIT) | language-server code tools | pilot only, planning mode; no text copied |
| ChromeDevTools/chrome-devtools-mcp (v1.12.0) | Apache-2.0 | DevTools: traces, network, console | approved, pinned, telemetry off |
| awslabs/mcp (2026.10 release) | Apache-2.0 | 63 AWS servers | 7 read-only servers approved |
| modelcontextprotocol/servers (v2.3.0) | MIT moving to Apache-2.0; docs CC-BY-4.0 | reference servers | none approved (built-ins cover them); skill-authoring findings adopted |

## Facts confirmed in the Claude Code docs (they drive the skill-loading fixes)
- **The skill listing is a budget**: 1% of the context window, with an 8,000-character fallback. When it is exceeded, descriptions are dropped from the least-invoked skills first, and only their names remain. eng-os skills are rarely invoked, so they lose their descriptions first when many plugins are installed.
  - Each entry (`description` plus `when_to_use`) is capped at 1,536 characters.
  - Settings: `skillListingBudgetFraction`, `skillListingMaxDescChars`, `skillOverrides` (`"name-only"`).
  - The 4,000-character total quoted in modelcontextprotocol/servers is not in the docs.
- **`disable-model-invocation: true`** removes a skill's description from the listing entirely. The user can still run it as `/name`.
- **Skills accept `paths:` globs** and then load automatically only around matching files.
- **`CLAUDE_CODE_SUBAGENT_MODEL`** sets the default subagent model when Claude passes none and the agent definition sets none.
- **Hooks**:
  - SessionStart matchers are `startup`, `resume`, `clear`, `compact` and `fork`.
  - Hook output is capped at 10,000 characters.
  - `Skill` is a tool name hooks can match.
- **Subagents** load the global CLAUDE.md (except Explore, Plan and agents with `omitClaudeMd`). They get skills only through their `skills` field or the Skill tool.

## Adopted into eng-os (0.11.0)
| Idea | From | Where in eng-os |
|---|---|---|
| Measure skill triggering: 5 should-trigger and 1 should-not case per skill, each in a fresh one-turn session | modelcontextprotocol/servers (`docs/skill-authoring.md`) | `tests/skill_cases.json`, `eng-os eval --skills` |
| Measure whether named skills actually get loaded | ECC (`skill-run-tracker.js`) | `eng-os usage` routing line, read from local transcripts (no extra hook needed) |
| Description formula: verb phrase, then "Use when…", key case first | modelcontextprotocol/servers, mattpocock/skills | all skill descriptions |
| Fewer model-invoked skills; rare ones user-invoked only | mattpocock/skills (19 of 29 user-invoked) | `eng-os-review` frontmatter |
| "Call the Skill tool with `x`" instead of naming a skill | mattpocock/skills (`.agents/invocation.md`) | router wording |
| Re-insert core rules after compaction | graphify, superpowers (SessionStart `compact`) | `session_start.py` (built in 0.10.0) |
| Approved MCP list, prefer a command-line tool plus a skill, pin, telemetry off, data-out record | ECC (`docs/MCP-CONNECTOR-POLICY.md`), context7 (`docs/security/data-privacy.mdx`), all MCP repos | `docs/MCP-POLICY.md` |
| Guard on MCP write tools, MCP installs, unpinned packages and dangerous MCP flags | github-mcp-server, awslabs/mcp, serena, chrome-devtools-mcp | `guard.py` + cases |
| Browser flags and safety (redirects pass origin lists, code-running default tools, isolated profiles, uploads) | playwright-mcp, chrome-devtools-mcp | `eng-testing/browser.md` |
| Spec template (problem, user stories, decisions without file paths, test seams, out of scope) and thin tickets | mattpocock/skills (`to-spec`, `to-tickets`, `triage/AGENT-BRIEF.md`) | `templates/docs/specs/`, `templates/github/ISSUE_TEMPLATE/task.yml`, `eng-design` |
| Ask only decisions whose prerequisites are settled, numbered, with a recommendation | mattpocock/skills (`grilling`) | `eng-design` section 1 |
| Debug by first building a fast, repeatable pass/fail check; redact secrets in output | mattpocock/skills (`diagnosing-bugs`) | `eng-testing` |
| Test at agreed seams; expected values from an independent source; test anti-patterns | mattpocock/skills (`tdd`) | `eng-testing` |
| Two-part review (standards, spec) in fresh contexts; evidence tags on findings | mattpocock/skills (`code-review`), graphify (confidence labels) | `eng-review` |
| Untrusted-data rule for tool output and plan files; nothing identifying in outside queries | ECC, graphify, context7, github-mcp-server | global CLAUDE.md section 4, `eng-security` |
| Default subagent model | ECC (`docs/token-optimization.md`), Claude Code docs | `settings.json` env, CLAUDE.md section 8 |

## Rejected, and why
- **Installing any whole pack** (superpowers, ECC, mattpocock/skills):
  - each competes with eng-os for control of the chat;
  - each adds dozens or hundreds of skills, which also pushes eng-os descriptions out of the listing;
  - each updates itself without review.
- **ECC's first-edit "fact-forcing" gate**: its evidence is the author's own two A/B runs, and it adds friction to every first edit. eng-os keeps "understand before changing" as an instruction instead.
- **Serena as a default**:
  - GPL licence;
  - its Claude Code prompt forbids the built-in Read and Edit tools;
  - shell and edit tools are on by default;
  - little benefit on Frappe or Odoo.
- **Graphify as a default**:
  - unproven token savings (one benchmark of 6 questions, measuring accuracy);
  - optional LLM backends that can send content out;
  - it rewrites CLAUDE.md and installs git hooks.
- **The MCP reference servers**: duplicates of Claude Code's built-in tools; the memory server stores plain files.
- **Context7 on customer-data projects**: queries leave the machine and are kept for benchmarking.
- **AWS write-capable servers and `aws-api-mcp-server`**: writes are allowed by default; IAM must stay the control.
- **Copying text verbatim**: everything adopted is rewritten in eng-os's words. Serena's GPL text is never copied.

## Limits of this survey
- Clones were shallow (`--depth 1`), so commit history was not assessed.
- Token costs of MCP tool definitions were not measured on a live session.
- Context7's library coverage for Frappe, Odoo and CodeIgniter needs a live query to check.
- Whether `${VAR}` expands in `claude mcp add --header` values is not documented. The install commands read secrets with `read -rs` instead.

## Addendum: token-optimisation repos (2026-11-09)
The user asked for the best token-saving repos to be analysed too. Five were read by separate research agents (Serena had been read already), and the hook facts were confirmed in the Claude Code docs. Measured first, on 96 local sessions since 2026-11-04:
- Bash output was 78% of all tool output (15,701 calls, average 1.7k characters, 71 over 20k).
- Read was 9.8%; 20% of reads re-read an unchanged file.
- 76% of turns ran with more than 200k tokens of context and 43% with more than 400k (median session peak 292k).

So the largest cost is the whole conversation being re-read on every turn. No single output was the driver.

| Repo (version read) | Licence | What it does | Evidence of savings | Verdict |
|---|---|---|---|---|
| rtk-ai/rtk (v1.2.0) | Apache-2.0 (CLI, hooks, filters); BUSL-1.1 (engine, proxy) | PreToolUse rewrite of shell commands to filtered `rtk <cmd>`; failure-only test output; raw output kept for recall | fixture benchmarks, bytes/4; says itself that "90% less output" is not 90% cheaper | pilot only, `rtk-oss` edition, telemetry off |
| Mibayy/token-savior (v4.24.0) | MIT | MCP code index plus memory; Read limit injection; quiet-flag rewrites | a self-run sample of 8 tasks: cost -45%, wall time +40%; an earlier claim withdrawn | not approved; ideas adopted |
| AMKhaan/token-saver (v1.1.0) | MIT | PostToolUse head/tail truncation; large-Read deny; re-read ledger | synthetic tests only, never run in a real session | not approved; ideas adopted |
| thedotmack/claude-mem (v15.13.0) | Apache-2.0 | a model summarises every tool event into a local database; memory injected at start | counterfactual "~10x"; the observer's own cost not netted out | not approved: sends tool I/O to a model, plain storage, telemetry on |
| mksglu/context-mode (v2.1.7) | Elastic-2.0 | replaces large output with indexed chunks; runs model-written code | own bench: -19.6% on large tasks, +5.7% on small; offline replay 1–7% | not approved: runs code, stores output in plain text, licence |

Adopted (0.13.0):
- **Context-size note**, from the measured context sizes plus claude-mem's and ECC's compaction ideas: the prompt hook reads the latest usage from the transcript tail.
- **Resume brief** from local `docs/progress`, claude-mem's idea done with no model call.
- **Re-read note**, from token-saver, token-savior and context-mode. It is a note, never a block: a refused read costs another round trip at full context size.
- **Large-output trim with the full copy saved**, from RTK's recovery pointer, context-mode's "never cut without keeping" rule and token-saver's error-line keeping. It uses PostToolUse `updatedToolOutput`, which the docs say replaces what Claude sees.
- **Quiet-output rule**, from RTK and token-savior, done as an instruction instead of command rewriting.
- **Usage breakdown**, from token-savior's transcript audit.

Rejected:
- **Rewriting commands automatically**: it changes what runs, and RTK's changelog shows a steady stream of silent-loss fixes.
- **Denying reads**: each refusal costs an extra round trip at full context size.
- **Model-based memory and indexing**: privacy, quota use and stale indexes.
- **Running model-written code outside the guard**.

## Refresh (2026-11-18)
The user asked for every repo above to be checked against its latest release, and for token savings to be looked for in all of them. The latest releases came from `gh api`. Each changed repo was shallow-cloned at its new tag and read by one research agent (Sonnet) that ran none of its code. The claims that change eng-os were spot-checked in the clones.

| Repo | Read → latest | What changed that matters | What eng-os did |
|---|---|---|---|
| obra/superpowers | v7.0.2 → v7.0.2 | no release, no commits | nothing needed |
| affaan-m/ECC | v2.2.3 → v2.2.3 | no release; main has an unreleased, opt-in "context gate" hook that checkpoints and restarts at 90% context | nothing needed (the context-size note measures the same thing) |
| mattpocock/skills | v1.3.2 → v1.3.2 | no release | nothing needed |
| Graphify-Labs/graphify | v0.9.104 → v0.9.112 | needs Python 3.11+; sign-up prompts (`GRAPHIFY_NO_CTA`); `graphify <platform> install` writes CLAUDE.md or AGENTS.md; `GRAPHIFY_BACKEND=none` and `--code-only` unchanged; no new benchmark | pilot pin, install and never-run list updated |
| github/github-mcp-server | v2.1.0 → v2.2.0 | headers and toolsets unchanged; new non-default `copilot_automations` toolset with `create_`, `update_`, `delete_` and `run_automation` | toolset left out of the install; the guard already asks for those tools (cases added) |
| upstash/context7 | 4.5.1 → 4.7.3 | same URL and key; "research preview" renamed experimental tools, off unless `?experimental=1` or the dashboard turns them on; also sends a session ID and server version; API logs kept 30 days; the free tier is per account | data-out row and install notes corrected |
| microsoft/playwright-mcp | v0.0.84 → v0.0.85 | a thin wrapper; same flags; new flags apply only with `--extension`; bundles a Playwright 1.66 alpha | pin bumped; the bundled build is noted as not audited |
| oraios/serena | v2.1.0 → v2.1.0 | no release | nothing needed |
| ChromeDevTools/chrome-devtools-mcp | v1.12.0 → v1.13.0 | same flags; new default `set_logpoints` runs page code; off-by-default network-mock tools can make the server itself fetch URLs | pin bumped; network mocks never added; `--no-javascript-evaluation` noted |
| awslabs/mcp | 2026.10.20261030201955 → 2026.11.20261117195521 | all 7 approved servers have new versions; billing adds read-only tools and needs Python 3.11; the docs server's `recommend` now accepts only AWS documentation URLs; **the IAM server has no `--readonly` flag** (its argument parser rejects it, at the old version too), so the old install command could not start | 7 pins bumped; `--readonly` removed (read-only is the default); section 5 now asks for flags checked in the code |
| modelcontextprotocol/servers | v2.3.0 → v2.5.0 | 14 security advisories fixed (git settings running programs, filesystem symlink races, fetch SSRF); every server can serve Streamable HTTP; `docs/skill-authoring.md` unchanged | still not approved; reason extended |
| rtk-ai/rtk | v1.2.0 → v1.2.0 | only 1.3.0 release candidates | nothing needed |
| Mibayy/token-savior | v4.24.0 → v4.24.0 | no release | nothing needed |
| AMKhaan/token-saver | v1.1.0 → v1.1.0 | no commits since July | nothing needed |
| thedotmack/claude-mem | v15.13.0 → v16.0.0 | a UI release; still sends tool input and output to Claude Haiku by default, telemetry still on; retention and secret-redaction settings exist but are off by default | still not approved; reason made precise |
| mksglu/context-mode | v2.1.7 → v2.2.1 | agent support and fixes; still runs model-written code with the user's environment, keeps a plain index, Elastic-2.0 | nothing needed |

Token-saving pass, measured on 49 local sessions from 2026-11-12 to 2026-11-18 (`eng-os usage`):
- Turns above 200k tokens of context fell from 76% to 69%, and above 400k from 43% to 32%. The work mix differed, so this is not a controlled comparison.
- Bash is 56% of tool output and Read 35%; MCP output is about 2%.
- A new session starts at a median of 92.7k tokens, of which eng-os is about 3.5k. The rest is the harness, plugins and connectors.

Adopted (0.14.0):
- **No skill routing on prompts Claude Code writes itself** (a background agent's notification, side-session and CI events). In this refresh session, subagent reports routed five unrelated skills, about 5,000 characters that every later turn re-read.

Not adopted:
- **Trimming MCP output**, context-mode's main idea: MCP is about 2% of tool output here.
- **ECC's context gate**: unreleased, and the context-size note already covers it.
- **claude-mem's 40% clear trigger and continuation template**: no measured benefit, and the resume brief covers restarts.
- **Chrome DevTools `--slim`** (3 tools): it drops the tracing tools eng-os approves the server for.
- **A stricter re-read rule**: the usage report's 34% repeated reads counts range reads and reads after edits, so it overstates the waste. The re-read note already covers unchanged full re-reads.

The largest cost left is outside eng-os: the plugins and connectors that load into every session. [MCP-POLICY.md](../MCP-POLICY.md) section 6 already says to remove unused ones.

## Addendum: tcb-developer/work-summary-skills (2026-11-20)
The user asked for this repo to be analysed and anything clearly worth having brought into eng-os. Metadata came from `gh api`; the repo was shallow-cloned at commit `586cc12` and every file read. It holds no code, hooks or scripts, so nothing could run.

| Repo (version read) | Licence | What it is | Verdict for TCB |
|---|---|---|---|
| tcb-developer/work-summary-skills (`586cc12`, 2026-11-20; no releases or tags) | MIT | 2 Markdown skills: `work-summary` keeps a per-task daily log in an uncommitted `WORK_SUMMARY/` folder (day files, a one-line `INDEX.md`, a `CONTEXT.md` project map, a block added to the project CLAUDE.md); `end-of-day-summary` turns a day file into a copy-ready "Task N:" summary in plain English | two ideas adapted in 0.15.0; not installed |

Who owns it (per `gh api`; the shallow clone cannot show history): a public repo on a personal GitHub user account named "TCB DEVELOPER" (created 2024-11-19, 4 public repos), not the company organisation. Created on 2026-11-20 with 2 commits, no stars or forks.

Risk check:
- **Data leaving the machine**: none from the repo itself. It has no code, telemetry or network calls; the summary is printed in chat and the user pastes it.
- **What the log holds**: each task's request, files, decisions and a plain-English summary, listed in `.git/info/exclude` (`skills/work-summary/SKILL.md`, section 1). Our reading, not a claim of the repo: a request copied from a prompt can carry client names, customer details or secrets into a file no review sees. The repo itself warns that `git clean -x` deletes the folder and suggests pinning it outside the repository (`README.md`, "Where the files go").
- **Control of the chat**: the `work-summary` description says "Use PROACTIVELY" at session start and on every code-touching task. Installed beside eng-os it would compete with `eng-docs` on every task, which is the same reason whole packs were rejected above.

Adopted (0.15.0), in eng-os's words:
- **A plain-English summary line in each progress-log entry** (`templates/docs/progress/0000-entry-template.md`, `**Summary**`): the repo's two-readers idea (technical detail for the next engineer, an outcome a manager can read), kept to one or two sentences so the entry stays short. A day's summary is then a `grep`, not a re-read.
- **A daily or end-of-day work summary** in skill `eng-delivery` beside the weekly status: built only from the day's progress entries, commits and merged PRs; one task per deliverable; work in progress as a note, never a task; same-day reverts left out; the project's own terms with no paths, hashes, commands or engineering acronyms; plain punctuation for pasting; the user sends it. Its core rule says the same in one line.
- **Routing**: before this, prompts such as "give me today's work summary" or "write my end of day update" routed no skill. The router now sends work summaries, daily or weekly work or status updates, end-of-day and stand-up updates, "what did I work on today" and "summarise today's work" to `eng-delivery`. "Daily sales report", "status update webhook" and "work update field" stay unrouted, so features named like reports are not mistaken for status work.

Not adopted:
- **The `WORK_SUMMARY/` log itself**: a second, uncommitted history beside `docs/progress/`. eng-os keeps history in the repo so the project survives people leaving; a local-only log defeats that, and `git clean -x` loses it.
- **A section per task, opened when the task arrives**: a write on every message and many sections per session. eng-os logs per working session and milestone, with one session per task.
- **`INDEX.md`**: `docs/progress/` files are already named `YYYY-MM-DD-short-title.md`, so a sorted listing is the index, and the resume brief reads the newest entry.
- **`CONTEXT.md`**: the project CLAUDE.md already holds commands, the code map and gotchas (global CLAUDE.md section 7), loaded at no extra read.
- **Appending a block to the project CLAUDE.md**: `eng-project-init` owns that file, and every line there is paid in every session.
- **Fixed markers for timesheet extraction**: nothing reads them yet. Worth revisiting if an ERPNext timesheet import is built.
- **Checking whether code changed since the recorded commit before trusting line numbers**: eng-os entries cite PRs and commits, not line ranges.
- **The session-end audit and backfill**: the Definition of Done in `eng-delivery` already requires the progress entry.

## Gap audit (2026-11-20)
The user asked for a complete gap audit of eng-os against every repo it had learned from, and for every good idea still missing to be added in one release (0.16.0). During the work the user added eight more repos: elementalsouls/Claude-BugHunter, trailofbits/skills, trailofbits/claude-code-config, anthropics/claude-code-security-review, anthropics/claude-plugins-official (the official plugins moved there from anthropics/claude-code, whose `examples/` and `mods/` were read too), getsentry/skills, github/spec-kit and cloudflare/security-audit-skill. The brief said 18 repos but listed 17; with the additions, 25 were read.

**Method.** Releases and latest commits came from `gh api`. Every repo was shallow-cloned into its own empty scratch folder and read by one research agent (Sonnet) that ran none of its code. Each agent listed every idea worth considering, with the repo path, and proposed a status against the eng-os files. Every "in eng-os" claim that decided something was then checked in the eng-os files; one was wrong the other way (token-savior's blanket-DELETE guard is already `sql-unscoped`), and two "in" claims were downgraded (graphify's redaction; ECC's inherited style is only partly in). Flags that a change depends on were confirmed in the clones and, for pins, in the released version (Chrome DevTools v1.13.0 docs, Serena v2.1.0 tool classes, npm `@playwright/mcp@0.0.86`, PyPI `graphifyy` 0.9.113).

**Refresh.** Four repos had new releases since the 2026-11-18 refresh: Graphify 0.9.113 (Python 3.11.5 floor, soupsieve advisories), Playwright MCP 0.0.86 (extension-only features), RTK 1.2.1 (fixes; the classifier still runs only for user-written rules) and claude-mem 16.0.1 (fixes, an observer switch). The other 13 had no new release; ECC, mattpocock/skills, github-mcp-server, Serena, Chrome DevTools, awslabs and context-mode had commits on main, read as unreleased.

**Statuses.** *In* means an eng-os file really covers it, named in the row. *Rejected* means an earlier recorded rejection that still holds, or for a new repo the same reason (mostly the whole-pack rejection). *Not adopted* means missing, with the reason it is not worth its tokens or risk. *Added* names where 0.16.0 put it. The same idea appears under more than one repo where several had it, so 110 added rows are about 60 distinct changes.

**Licences.** trailofbits/skills is CC-BY-SA-4.0 and trailofbits/claude-code-config and anthropics/claude-code carry no open licence, so only ideas were taken; nothing from any repo was copied.

**Main reasons for rejecting or not adopting.** Whole packs and marketplaces compete with eng-os for control of the chat (broad triggers, their own hooks, self-update). Anything that sends code, diffs or transcripts to a model or vendor on every turn. Rewriting or denying tool calls. Offensive tooling against third parties (Claude-BugHunter's hunting payloads, scope gate, recon). Heavy machinery whose useful core fits in a line (Cloudflare's coverage ledger, JSON findings). Exclusion lists that conflict with eng-os's stance on logging and availability (claude-code-security-review). Flags and settings with no measured need here.

**Guard replay, first run** (`eng-os usage --guard --since 2026-11-13`, leaving out this audit's own session): 4,172 shell commands from 90 transcripts; 80.1% allowed with no prompt. The new `git-hook-bypass` rule matched 18 commands, every one a real `git commit --no-verify` that skipped a repository's hooks (17 would see it as their first ask). Its first draft also matched `git log --grep commit -n 5`; the rule now anchors on the git subcommand.

| Repo | Ideas | In | Added | Rejected | Not adopted |
|---|---|---|---|---|---|
| obra/superpowers | 24 | 9 | 10 | 2 | 3 |
| affaan-m/ECC | 20 | 8 | 4 | 3 | 5 |
| mattpocock/skills | 25 | 13 | 3 | 1 | 8 |
| Graphify-Labs/graphify | 15 | 7 | 2 | 2 | 4 |
| github/github-mcp-server | 14 | 3 | 4 | 0 | 7 |
| upstash/context7 | 15 | 5 | 2 | 2 | 6 |
| microsoft/playwright-mcp | 12 | 2 | 1 | 0 | 9 |
| oraios/serena | 16 | 7 | 3 | 3 | 3 |
| ChromeDevTools/chrome-devtools-mcp | 12 | 4 | 4 | 1 | 3 |
| awslabs/mcp | 17 | 6 | 4 | 0 | 7 |
| modelcontextprotocol/servers | 25 | 5 | 13 | 1 | 6 |
| rtk-ai/rtk | 18 | 8 | 4 | 3 | 3 |
| Mibayy/token-savior | 18 | 8 | 1 | 6 | 3 |
| AMKhaan/token-saver | 13 | 9 | 0 | 1 | 3 |
| thedotmack/claude-mem | 14 | 4 | 4 | 3 | 3 |
| mksglu/context-mode | 17 | 8 | 1 | 2 | 6 |
| tcb-developer/work-summary-skills | 25 | 12 | 0 | 9 | 4 |
| elementalsouls/Claude-BugHunter | 12 | 1 | 6 | 1 | 4 |
| trailofbits/skills | 22 | 7 | 8 | 1 | 6 |
| trailofbits/claude-code-config | 20 | 6 | 6 | 2 | 6 |
| anthropics/claude-code-security-review | 18 | 5 | 7 | 0 | 6 |
| anthropics/claude-plugins-official (+ claude-code examples, mods) | 17 | 4 | 5 | 2 | 6 |
| getsentry/skills | 16 | 6 | 4 | 1 | 5 |
| github/spec-kit | 16 | 6 | 3 | 2 | 5 |
| cloudflare/security-audit-skill | 18 | 3 | 11 | 1 | 3 |
| **Total (25 repos)** | **439** | **156** | **110** | **49** | **124** |

### obra/superpowers (v7.0.2, unchanged; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Plan ledger; after compaction trust the ticked plan and `git log` over memory (subagent-driven-development/references/resuming.md) | **added** | eng-design/implementation-plans.md §2 |
| Pick the form of guidance from the failure seen: prohibition plus excuse table, template, required slot (writing-skills) | **added** | eng-os-review §5 |
| A description says when to use a skill, never its workflow (writing-skills) | **added** | eng-os-review §5 |
| Eval hygiene: control run, repeated runs, variance as a signal (writing-skills) | **added** | eng-os-review §4; `eval --runs` |
| Subagent dispatch: brief or diff as a file, model set on every dispatch, one task each (subagent-driven-development) | **added** | implementation-plans.md §2 |
| Subagents and reviewers start no subagents of their own (implementer and reviewer prompts) | **added** | implementation-plans.md §2; eng-review §2 |
| Review package from a recorded base, never `HEAD~1` (scripts/review-package) | **added** | eng-review §2 |
| Do not pre-judge a reviewer ("do not flag") (task-reviewer-prompt.md) | **added** | eng-review §2 |
| Fix-loop round cap; minor findings deferred to a list (references/fix-loop.md) | **added** | implementation-plans.md §2 |
| Red-green proof of a regression test: undo the fix, see it fail, restore (verification-before-completion) | **added** | eng-testing bug-fix protocol |
| Delete code written before its test (test-driven-development) | not adopted | friction for little gain; global CLAUDE.md keeps "failing first where practical" |
| Three failed fixes: question the architecture (systematic-debugging) | in | global CLAUDE.md §3 (two failed attempts) |
| Plan header with global constraints, per-task interfaces, review focus (writing-plans) | not adopted | the spec template's decisions and test seams already carry these |
| Skill-package layout and size tests (tests/skill-layout, tests/skill-size) | in | `eng-os verify` budgets and referenced-file checks |
| Per-subagent token breakdown from transcripts (analyze-token-usage.py) | in | `eng-os usage` |
| Worktree detection first and check-ignore before an in-repo worktree (using-git-worktrees) | not adopted | implementation-plans.md §3 already puts worktrees outside the repo |
| Finishing menu: tests, then merge, PR or keep; discard only on request (finishing-a-development-branch) | in | implementation-plans.md §3 |
| Evidence before claims; verify agent reports (verification-before-completion) | in | global CLAUDE.md §5; eng-review red flags |
| No performative agreement; verify review feedback (receiving-code-review) | in | eng-review "Receiving review feedback" |
| Re-insert core rules after compaction (hooks.json) | in | session_start.py |
| Ask only when the answer changes what gets built (brainstorming) | in | eng-design §1 |
| Session diagnosis from transcripts with cited evidence (diagnosing-superpowers) | in | `eng-os usage`; eng-os-review |
| Check for a skill before every response (using-superpowers) | rejected | competes with eng-os routing; still holds |
| Installing the whole pack | rejected | competes for control and updates itself; still holds |

### affaan-m/ECC (v2.2.3 release, main 4adeee6; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Block git hook bypass: `--no-verify`, `core.hooksPath` (scripts/hooks/block-no-verify.js) | **added** | guard rule `git-hook-bypass` (ask) |
| CI install hardening: `npm ci --ignore-scripts`, `persist-credentials: false`, no cache in privileged jobs (scripts/ci/validate-workflow-security.js) | **added** | eng-ship/github.md |
| Hidden-unicode scan of skill and rule files (scripts/ci/check-unicode-safety.js) | **added** | `eng-os verify` |
| Supply-chain incident: remove persistence before rotating tokens (docs/security/supply-chain-incident-response.md) | **added** | eng-ship "Incidents" |
| Block edits to linter and formatter config (scripts/hooks/config-protection.js) | not adopted | many false positives on framework repos; global CLAUDE.md §3 already forbids weakening checks |
| pass@k and pass^k eval metrics (skills/eval-harness) | not adopted | trigger cases are cheap; `--runs` gives repeat rates |
| Record an inherited codebase's conventions (skills/inherit-legacy-style) | in | templates/project/CLAUDE.md "Conventions", filled by eng-project-init |
| Freeze mode: writes limited to one folder (skills/safety-guard) | not adopted | advisory only; the guard's project-root checks already apply |
| Review of unpinned MCP package selectors (skills/mcp-dependency-review) | in | guard `UNPINNED_PKG`; MCP-POLICY §1 |
| Dangerous-command list (skills/safety-guard) | in | guard rules (force push, reset, DROP, prune, kubectl delete, chmod 777, publish) |
| Secret and credential patterns (rules/common/security.md) | in | guard `SECRET_CONTENT`, `SECRET_PATH` |
| Default of one MCP server; a CLI plus a skill preferred (docs/MCP-CONNECTOR-POLICY.md) | in | MCP-POLICY §1 |
| Playwright CLI instead of Playwright MCP for token cost | not adopted | follow-up: the CLI is unaudited and MCP output is about 2% of tool output here |
| Skill-run tracking, compaction hints, context notes (skill-run-tracker.js, suggest-compact.js) | in | `eng-os usage`; prompt_router context-size note |
| GateGuard fact-forcing gate on the first edit (gateguard-fact-force.js) | rejected | friction on every edit; ECC's own pilot found no benefit; still holds |
| Context gate at 90% (context-gate.js, unreleased) | rejected | the context-size note covers it; still holds |
| Session summaries written by `claude -p` at PreCompact and Stop (scripts/lib/llm-summary.js) | rejected | sends transcripts to a model; still holds |
| Per-language security rules (rules/*/security.md) | in | eng-security/stacks.md; global/rules |
| Verification loops and a silent-failure hunter (skills, agents) | in | global CLAUDE.md §3 and §5; eng-testing; eng-review/coding-standards.md |
| Hook profiles, hookify rules, watchdog, stdin caps, tmux block, MCP health check (scripts/hooks) | not adopted | Windows or Node specific, or friction; `ENG_OS_*` switches cover profiles |

### mattpocock/skills (v1.3.2 release, main abeeaf9; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Writing for agents: pointer wording, positive phrasing, delete no-op sentences, checkable steps (writing-for-agents) | **added** | eng-os-review §5 |
| Strict YAML check of SKILL.md frontmatter (scripts/check-frontmatter.mjs, unreleased) | **added** | `eng-os verify` |
| Retro rule: a mechanical violation gets a deterministic check (engineering/retro) | **added** | eng-review "Before a finding goes in the report" |
| Client discovery questionnaire (to-questionnaire) | not adopted | eng-design §1 open-question rules cover discovery |
| Dated claims citing the commit (in-progress/chief-of-staff) | in | progress-entry template "Evidence" (PR or commit) |
| `.out-of-scope/` record of rejected requests (triage/OUT-OF-SCOPE.md) | in | eng-delivery: change requests logged and approved in writing; docs/decisions.md |
| Research against primary sources, each claim cited (engineering/research) | not adopted | low value for project work; global CLAUDE.md §5 already bars unobserved claims |
| Throwaway prototype rules (engineering/prototype) | not adopted | low value |
| Design it twice, deep modules, import boundaries (codebase-design, setup-ts-deep-modules) | not adopted | Frappe and Odoo dictate the structure |
| Fowler smell baseline in review (engineering/code-review) | not adopted | linters cover it; token cost |
| Wayfinder ticket map, setup wizard (wayfinder, wizard) | not adopted | needs an issue tracker; the wizard writes secrets |
| Integration branch plus merger agent (implement-spec) | not adopted | eng-os subagents do not commit |
| AI-generated disclaimer on tracker comments (triage) | not adopted | conflicts with the no-attribution commit rule |
| Grilling: frontier questions, numbered, with a recommendation (grilling) | in | eng-design §1 |
| Spec and thin tickets (to-spec, to-tickets) | in | templates/docs/specs/; templates/github/ISSUE_TEMPLATE/task.yml |
| Fast pass/fail check before debugging; test seams (diagnosing-bugs, tdd) | in | eng-testing |
| Two-part review: standards, then spec (code-review) | in | eng-review §2 |
| Git guardrails (git-guardrails) | in | guard `git-discard`, `git-force-push` |
| Subagent brief; worktrees | in | eng-design/implementation-plans.md |
| Rare skills user-invoked only | in | eng-os-review frontmatter |
| "Call the Skill tool with x" wording (.agents/invocation.md) | in | prompt_router.py |
| Handoff document | in | session_start.py resume brief; progress log |
| PR body with evidence, risk and rollback | in | templates/release/pull_request_template.md |
| Glossary and ADRs | in | eng-docs; eng-design |
| Installing the whole pack | rejected | competes for control and updates itself; still holds |

### Graphify-Labs/graphify (v0.9.112 → v0.9.113; Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Pin bump; Python 3.11.5 floor (pyproject.toml, 0.9.113 notes) | **added** | MCP-POLICY §3 pilot entry |
| `AGENTS.md` versus `CLAUDE.md`: Claude Code reads only CLAUDE.md (install.py) | **added** | eng-project-init §2 (`@AGENTS.md` import) |
| Per-agent nudge cap (cli.py `_nudge_allowed`) | not adopted | the router names each skill once per session and skips subagent prompts |
| Timeout on every hook (install.py) | in | global/settings.json |
| SessionStart `compact` re-inserts context (install.py) | in | session_start.py |
| Match the Grep tool as well as Bash (install.py) | in | settings.json PreToolUse matcher |
| Confidence labels EXTRACTED / INFERRED / AMBIGUOUS (analyze.py) | in | eng-review evidence tags |
| Telemetry-free posture; query log off by default (querylog.py) | in | MCP-POLICY §3 |
| Hash-stamped untrusted-source delimiters (SECURITY.md, llm.py) | not adopted | eng-os runs no model pipeline; global CLAUDE.md §4 data rule |
| Redact secrets before persisting text (security.py) | not adopted | saved output is private (0600) and deleted within a day; redaction could hide evidence |
| Uninstall refuses to delete home or root (SECURITY.md) | in | guard `fs-wipe` |
| Guard `graphify install`, `hook install`, `ingest` | not adopted | pilot only; the policy forbids them and they are rare |
| Trusted publishing, no tokens (RELEASING.md) | in | eng-ship/github.md (attestations, OIDC) |
| Auto-refresh of installed skill files (__main__.py) | rejected | updates without review; still holds |
| Rewrites CLAUDE.md; installs git hooks and merge drivers (hooks.py) | rejected | still holds |

### github/github-mcp-server (v2.2.0 release, main c855185; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| `hide_*` and `unhide_*` comment tools are writes the guard missed (pkg/github/comment_minimize.go) | **added** | guard `MCP_WRITE_ACTION`; 2 cases |
| Insiders and feature flags turn on experimental tools (docs/insiders-features.md, docs/feature-flags.md) | **added** | MCP-POLICY §2; guard `MCP_DANGER_FLAG` |
| Lockdown is a best-effort content filter, not a boundary (docs/server-configuration.md) | **added** | MCP-POLICY §2 |
| Hidden text in issue bodies (pkg/sanitize) | **added** | eng-security "Agents and tools" |
| `X-MCP-Tools` allowlist and `X-MCP-Exclude-Tools` | not adopted | the toolset list already narrows it |
| Read-only overrides everything | in | MCP-POLICY §2 (`X-MCP-Readonly`) |
| Toolset trimming for tokens | in | MCP-POLICY install command |
| Integrity and confidentiality labels (pkg/ifc) | not adopted | enforced by a separate service |
| Fine-grained, scoped, expiring token | in | MCP-POLICY §2 |
| Classic token scope filtering (docs/scope-filtering.md) | not adopted | fine-grained tokens are required anyway |
| `hide_secret` on secret-scanning reads | not adopted | that toolset is not installed |
| `readOnlyHint` validation test (pkg/toolvalidation) | not adopted | the guard matches verbs instead |
| Signed image, SHA-pinned actions (docker-publish.yml) | not adopted | the remote server is used |
| MCP skills catalog (pkg/skills) | not adopted | insiders only |

### upstash/context7 (@upstash/context7-mcp 4.7.3, unchanged; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Experimental source-code tools replaced `query-code` (code-tools.ts, CHANGELOG 4.7.3) | **added** | MCP-POLICY §2 |
| Data out also names the plugin, transport and experimental flag (docs/security/data-privacy.mdx) | **added** | MCP-POLICY §2 table |
| No secrets or code in queries (src/index.ts, skills/find-docs) | in | global CLAUDE.md §4; MCP-POLICY §1 |
| One concept per query (rules/context7-mcp.md) | not adopted | a quality tip, no safety value |
| Pass the version as its own argument (skills/context7-mcp) | not adopted | minor |
| Say when a lookup failed instead of falling back silently (skills/find-docs) | in | global CLAUDE.md §5 |
| At most 3 lookups per question (skills/find-docs) | not adopted | low value |
| "Use it even when you know the answer" trigger (rules/context7-mcp.md) | not adopted | broad triggers cost tokens and send queries out |
| `ctx7 setup` writes rules; runs `npx ctx7@latest` (packages/cli) | in | guard unpinned-package and `mcp-config` asks |
| `OTEL_SDK_DISABLED` (telemetry-config.ts) | not adopted | applies to a self-hosted server only |
| Dashboard-selected tools re-read every few minutes (CHANGELOG 4.7.2) | in | MCP-POLICY §2 keeps experimental tools off |
| opencode and pi plugins (packages/opencode, packages/pi) | not adopted | not used |
| Description formula and trigger eval (skills/*) | in | tests/skill_cases.json; `eval --skills` |
| Context7 on customer-data projects | rejected | queries kept for benchmarking; still holds |
| Installing its rules and skills | rejected | competes for control; still holds |

### microsoft/playwright-mcp (v0.0.85 → v0.0.86; Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Pin bump; bundled Playwright 1.66.0-alpha-2026-11-18 (package.json) | **added** | MCP-POLICY §2; eng-testing/browser.md |
| `--snapshot-mode`, `--snapshot-boxes` | not adopted | savings unmeasured; MCP output is about 2% here |
| `--mobile` | not adopted | no measured need |
| `--idle-timeout` | not adopted | the default suits |
| `--secrets` dotenv file | not adopted | browser checks use test credentials only |
| `--host`, `--allowed-hosts` for HTTP mode | not adopted | eng-os runs it over stdio only |
| `--file-paths`, `--console-level`, `--output-max-size` | not adopted | no value found |
| Playwright CLI more token-efficient than MCP (README) | not adopted | follow-up: unaudited |
| Isolated mode, accessibility snapshots, storage state | in | eng-testing/browser.md |
| File access limited to workspace roots | in | browser.md and MCP-POLICY ban `--allow-unrestricted-file-access` |
| Docker image | not adopted | not needed |
| `--session-name`, `--session-color`, extension-only flags | not adopted | `--extension` is not approved |

### oraios/serena (v2.1.0 release, main 7f7d624; GPL-3.0, ideas only)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Planning mode leaked edit tools in 2.1.0: exclude them by name (CHANGELOG #2210) | **added** | MCP-POLICY §3 `excluded_tools` |
| Trusted projects can run commands (docs/02-usage/050_configuration.md) | **added** | MCP-POLICY §3 (reason stated) |
| `ext-full`, `ext-readonly` modes (main) | **added** | MCP-POLICY §3 (never) |
| Memory threshold: stable, non-obvious conventions only (memory_maintenance.md) | in | global CLAUDE.md §7 (durable project knowledge) |
| Memory as a graph of topic notes (memory_maintenance.md) | not adopted | project CLAUDE.md and path rules suffice |
| Batch independent tool calls (system_prompt.yml) | in | global CLAUDE.md §8 |
| Trust a refactor tool's success without re-checking (modes/editing.yml) | not adopted | contradicts "done means verified" |
| Targeted replace instead of whole-file rewrite (modes/editing.yml) | not adopted | the Edit tool already does this |
| Read-only and onboarding modes (modes/*.yml) | in | MCP-POLICY §3 (planning mode) |
| Telemetry off: `SERENA_USAGE_REPORTING=false` | in | MCP-POLICY §3 |
| Guard asks on Serena shell and edit tools | in | tests/guard_cases.json |
| Version pin | in | MCP-POLICY §3 |
| Single-project context | in | MCP-POLICY §3 (`--project`) |
| Claude Code context forbids the built-in Read and Edit (contexts/claude-code.yml) | rejected | overrides built-in tools; still holds (upstream plans to drop it) |
| GPL-3.0 licence | rejected | ideas only; still holds |
| Shell and edit tools on by default | rejected | still holds; handled by the exclusions |

### ChromeDevTools/chrome-devtools-mcp (v1.13.0, main bdecb63; Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| `--redact-network-headers` masks auth and cookie headers (docs/configuration.md) | **added** | MCP-POLICY §2 install; browser.md |
| `--allowUnrestrictedPaths` opens the whole disk to its file tools (docs/configuration.md) | **added** | guard `MCP_DANGER_FLAG`; MCP-POLICY §2 |
| Config-file discovery; `CHROME_DEVTOOLS_MCP_NO_CONFIG_DISCOVERY` (docs/configuration.md) | **added** | MCP-POLICY §2 install; browser.md |
| Guard `--categoryNetworkMocks`, `--experimentalDevtools`, `--categoryExtensions` | **added** | guard `MCP_DANGER_FLAG`; cases |
| `--blocked-url-pattern` | not adopted | `--allowed-url-pattern` is preferred |
| Its skills folder: LCP subparts, cookie triage, memory leaks (skills/) | not adopted | detail the trace tools report; memory tools are not approved |
| Paging and `includeSnapshot:false` token tips (skills/chrome-devtools) | not adopted | browser.md already saves big snapshots to a file |
| Page content returned as-is (SECURITY.md) | in | global CLAUDE.md §4; browser.md |
| `--slim` | rejected | drops the tracing tools it is approved for; still holds |
| `--no-javascript-evaluation` | in | browser.md |
| Telemetry and update-check flags | in | MCP-POLICY §2 |
| Pinned npx install | in | MCP-POLICY §2; guard |

### awslabs/mcp (release 2026.11.20261117195521, main dc925c8; Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| `--allow-sensitive-data-access` flag form (serverless, dataprocessing READMEs) | **added** | guard `MCP_DANGER_FLAG`; MCP-POLICY §4 |
| Prefixed write switches such as `SITEWISE_MCP_ALLOW_WRITES="True"` | **added** | guard `MCP_DANGER_FLAG`; MCP-POLICY §4 |
| `aws-api-mcp-server` telemetry on by default (`AWS_API_MCP_TELEMETRY`) | **added** | MCP-POLICY §4 |
| Dependency review on PRs (.github/workflows) | **added** | eng-ship/github.md |
| `--allow-write`, `--allow-writes`, `--no-confirmation` | in | guard; MCP-POLICY §4 |
| ccapi `--readonly` | in | MCP-POLICY §4 |
| `READ_OPERATIONS_ONLY=false` | in | guard |
| Prompt-injection warning on untrusted data | in | global CLAUDE.md §4; MCP-POLICY §1 |
| Least-privilege role and a dedicated profile | in | MCP-POLICY §2 AWS section |
| well-architected-security server | not adopted | follow-up: its tools are not yet confirmed read-only |
| aws-network server | not adopted | follow-up: check it is read-only |
| security-agent server | not adopted | writes to S3 and logs |
| aws-support server | not adopted | can open support cases |
| checkov and detect-secrets in CI | not adopted | Trivy and gitleaks are already listed |
| AST denylist and import allowlist for server code (DESIGN_GUIDELINES.md) | not adopted | eng-os builds no MCP servers |
| "CRITICAL: the assistant must…" text in tool descriptions (DESIGN_GUIDELINES.md) | not adopted | instruction-shaped text in tool descriptions is what eng-os treats as data |
| Few servers, one conversation per feature (VIBE_CODING_TIPS_TRICKS.md) | in | MCP-POLICY §1; global CLAUDE.md §8 |

### modelcontextprotocol/servers (v2.5.0, unchanged; MIT and Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Negatives scored against every model-invoked skill (docs/skill-authoring.md) | **added** | bin/eng-os-eval.py |
| `$ARGUMENTS` and `$0`–`$9` in a skill body get rewritten (skill-authoring.md) | **added** | `eng-os verify` |
| Unquoted `:` or `#` in a description; `---` on line 1 (skill-authoring.md) | **added** | `eng-os verify` (line 1 was already required) |
| Five runs per case; one sample is noise (skill-authoring.md) | **added** | `eval --runs`; eng-os-review §4 |
| Cases must not be answerable from always-loaded rules (skill-authoring.md) | **added** | eng-os-review §4 |
| First-move wording, no file or symbol names (skill-authoring.md) | **added** | eng-os-review §4 |
| SSRF: pin the vetted address, re-check redirects, block mapped IPv6 and 100.64/10 (src/fetch) | **added** | eng-security/stacks.md |
| Untrusted repo config runs code: fsmonitor, hooksPath, drivers, submodules (src/git `HARDENED_CONFIG`) | **added** | eng-security "Agents and tools" |
| Resolve real paths; re-check symlinks (src/filesystem) | **added** | eng-security/stacks.md |
| Refuse argument values that start with `-` (src/git) | **added** | eng-security/stacks.md |
| No dependency install or build in a credentialed publish job (AGENTS.md) | **added** | eng-ship/github.md |
| No automatic test retries (scripts/verify-no-test-retries.mjs) | **added** | eng-testing "Flaky tests" |
| Vulnerability details never in public issues, PRs or branch names (.claude/skills/security-advisory) | **added** | eng-security §4 |
| Chained hand-off cases (skill-authoring.md) | not adopted | eng-os skills do not hand off as a measured path |
| `paths:` halved a skill's trigger rate (skill-authoring.md) | not adopted | eng-os uses path rules, not path-scoped skills |
| Overrides instead of `npm audit fix` (AGENTS.md) | not adopted | minor |
| Never poll while waiting (AGENTS.md) | not adopted | the harness already instructs it |
| Reply in each review thread (AGENTS.md) | not adopted | low value |
| Pacing GitHub writes, DCO, gate lease | not adopted | specific to that project |
| Description formula, listing budget, `disable-model-invocation` | in | survey "Adopted"; verify budgets |
| Five positives and one negative per skill | in | eng-os-eval.py self-test |
| Probe flags for a one-turn eval | in | eng-os-eval.py |
| A rule that must survive compaction lives in the always-loaded file | in | session_start.py |
| Stale-instruction check at session start | in | session_start.py; eng-project-init installed-check |
| Installing the servers | rejected | duplicate built-in tools; still holds |

### rtk-ai/rtk (v1.2.0 → v1.2.1; Apache-2.0 (rtk-oss))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Strip colour codes and redrawn progress lines (src/filters, pip_cmd.rs) | **added** | post_tool.py |
| Failure-only test output for phpunit, jest, vitest, flutter, bench | **added** | eng-testing/tooling.md |
| Recovery store default is `sqlite`, kept 30 days; `[retriever] mode = "failures"` | **added** | MCP-POLICY §3 |
| Classifier, upstream and task blocks post output to a model (src/core/classify.rs) | **added** | MCP-POLICY §3 (never write them) |
| Dedup repeated log lines with counters (log_cmd.rs) | not adopted | more hook code; no measured need |
| Filter fixture tests, never-worse fuzz (src/filters/*.toml, tests/) | in | trim self-tests in bin/eng-os |
| Redact secrets in saved output (aws_cmd.rs) | not adopted | the saved copy is private and short-lived; redaction could hide evidence |
| Never emit more than the raw output (src/core/guard.rs) | in | post_tool.py trims only above 30k |
| Full output kept and pointed to (retriever.rs, tee.rs) | in | post_tool.py `save_full` |
| Per-line cap; head, tail and error lines (truncate.rs) | in | post_tool.py |
| Per-command escape hatch (`RTK_DISABLED`, `rtk bypass`) | in | `# eng-os:full`; `ENG_OS_TRIM_OUTPUT=0` |
| Quiet flags as an instruction (hooks/rtk-awareness.md) | in | global CLAUDE.md §8 |
| Measure savings on real use (docs/usage/AUDIT_GUIDE.md) | in | `eng-os usage` |
| Hook-script integrity hashes (src/hooks/integrity.rs) | in | install manifest; `verify` drift check |
| Rewriting commands automatically (src/discover/registry.rs) | rejected | changes what runs; still holds |
| Rewrite hook answering `permissionDecision: allow` (src/hooks/permissions.rs) | rejected | the guard stays authoritative; still holds |
| Project-local filters behind a trust store (src/hooks/trust.rs) | not adopted | eng-os has no project filters |
| Model "judge" classifiers (src/core/classify.rs) | rejected | model-based processing of output; still holds |

### Mibayy/token-savior (v4.24.0, unchanged; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Replay a guard against real past tool calls to measure false positives (scripts/rules_backtest.py) | **added** | `eng-os usage --guard` |
| Block `DELETE` with no `WHERE` (hooks/ledger-rules.json) | in | guard `sql-unscoped` (UPDATE or DELETE without WHERE) |
| Backup before destructive DB commands (ledger-rules.json) | not adopted | a hook cannot check a backup exists; eng-ship and the frappe-erpnext core rules require it |
| A benchmark must assert the tools were called (README) | in | the trigger eval counts Skill tool calls |
| Prune stale per-session state (ts_discipline_guard.py) | in | session_start.py (3 days) |
| Re-read note, never a block (ts_discipline_guard.py) | in | guard `reread_note` |
| Inject `limit` on large Reads (read_guard_hook.py) | rejected | changes the call; still holds |
| Quiet-flag command rewrites (bash_rewriter/rules.py) | rejected | changes what runs; still holds (the instruction form is in CLAUDE.md §8) |
| Rewrite only simple commands (bash_rewriter) | rejected | part of the rewriting design |
| Per-command output compactors (src/token_savior/compactors) | rejected | rewriting; post_tool.py trims generically |
| Large output replaced by a pointer (tool_capture_hook.py) | in | post_tool.py |
| Transcript audit of where tokens go (scripts/audit_budget.py) | in | `eng-os usage` |
| Memory injected by hooks (hooks/memory-*.sh) | rejected | model-based memory; still holds |
| Symbol-level reads through an MCP index (server.py) | rejected | not approved; still holds |
| Forbid subagents (CLAUDE.md) | not adopted | conflicts with global CLAUDE.md §8 |
| Force-push block; pre-push checklist (ledger-rules.json, preflight.sh) | in | guard `git-force-push`; global CLAUDE.md §7 |
| Semantic duplicate detection (memory/dedup.py) | not adopted | a product feature |
| Dependency bounds with the reason beside each pin (pyproject.toml) | in | global CLAUDE.md §4 |

### AMKhaan/token-saver (v1.1.0, unchanged; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Trim Grep, Glob and web output too (hooks/hooks.json) | not adopted | Bash and Read are 91% of tool output |
| Persistent savings ledger and report (scripts/lib/ledger.js) | not adopted | `eng-os usage` reads transcripts; a dollar figure from chars/4 is not evidence |
| Measured proof script in CI (test/prove.js) | in | `bin/eng-os test` trim cases |
| Head and tail keeping error lines (truncate-output.js) | in | post_tool.py |
| Hard cut of very long lines (truncate-output.js) | in | post_tool.py `LINE_MAX` |
| Kill switch; fail-open (truncate-output.js) | in | post_tool.py |
| Re-read advisory (guard-large-read.js, read-tracker.js) | in | guard `reread_note` |
| Deny a Read over 2 MB (guard-large-read.js) | rejected | a refusal costs a round trip; still holds |
| Ledger pruning after a day (read-tracker.js) | in | post_tool.py, session_start.py |
| Exec-form hook commands for Windows (hooks/hooks.json) | not adopted | eng-os supports macOS and Linux |
| Clone-and-pull installer; pipe-to-shell one-liner (install.sh) | in | guard `pipe-to-shell` |
| Tell the model how to re-run narrower (truncate-output.js) | in | post_tool.py note |
| "Hooks beat prompts" | in | survey decision: instruction, not rewriting |

### thedotmack/claude-mem (v16.0.0 → v16.0.1; Apache-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Telemetry kill switch `DO_NOT_TRACK` (telemetry/consent.ts) | **added** | MCP-POLICY §4 |
| Setup installs a runtime at session start (bun-auto-install.ts) | **added** | MCP-POLICY §4 and §6 checklist |
| Observer switch `CLAUDE_MEM_OBSERVER_ENABLED=false` (16.0.1) | **added** | MCP-POLICY §4 |
| Handoff records failed attempts (plugin/skills/handoff) | **added** | progress-entry template "Tried and dropped" |
| Strip private and system tags before storing (tag-stripping.ts) | not adopted | eng-os stores no tool input or output |
| Secret redaction patterns (auto-redaction.mdx) | not adopted | saved output is private and short-lived |
| Skip lists for capture (`CLAUDE_MEM_SKIP_*`) | not adopted | only matters with capture |
| Retention limits for a memory store | in | MCP-POLICY §5 point 5 (how long data is kept) |
| Search, then timeline, then fetch by id (mem-search) | in | the resume brief reads only the newest entry |
| SessionStart restore on startup, clear, compact; silent on resume (hooks.json) | in | session_start.py |
| Capped context injection (SettingsDefaultsManager.ts) | in | resume brief size cap |
| Deny full Reads of large files (file-context.ts) | rejected | a refusal costs a round trip; still holds |
| Auto-clear at 40% context (`CLAUDE_MEM_AUTO_CLEAR_*`) | rejected | no measured benefit; still holds |
| A model summarises every tool event (src/sdk) | rejected | privacy and quota; still holds |

### mksglu/context-mode (v2.2.1 release, main a0e4295; Elastic-2.0)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Unwrap commands handed to a shell as a string (src/core/policy/unwrap.ts) | **added** | guard `segments()`: `bash -c`, `sh -c`, `eval` |
| Decide per pipeline, allowing bounded sinks (ADR-0008) | not adopted | the guard replay shows no false positives of this kind |
| User deny rules applied to wrapped code (user-deny.ts) | in | partly, through the unwrap above |
| Stateless hooks; hints once per session (ADR-0008) | in | guard; prompt_router |
| Output replaced through `updatedToolOutput`, full copy kept (ADR-0016) | in | post_tool.py |
| Deny a large Read (ADR-0008) | rejected | a refusal costs a round trip; still holds |
| Run model-written code in its sandbox (src/core/sandbox) | rejected | runs code outside the guard; still holds |
| Strip `NODE_OPTIONS` from spawned children (sandbox/env.ts) | not adopted | eng-os spawns no model code |
| Compaction block re-inserted at SessionStart (ADR-0009) | in | session_start.py |
| Journal of failed tool calls (ADR-0009) | not adopted | no measured need |
| Prompt-cache check: no dynamic text in instructions (ADR-0021) | not adopted | eng-os hook text is per session, not part of a cross-session cached prefix |
| Same output budget for subagents (ADR-0016) | not adopted | no problem seen |
| Benchmark method: live A/B, medians, negative rows kept (bench/RESULTS.md) | in | `eng-os usage`, `eval`; survey |
| Doctor with one exact fix per failure (ADR-0010) | in | `eng-os verify` |
| Release checksums and a clean-home install test (SHA256SUMS, ADR-0013) | in | install manifest hashes; throwaway-home verify before every release |
| Recorded real hook payloads as fixtures (scripts/record-fixtures.mjs) | not adopted | hand-written cases follow the documented payload |
| No routing text in subagent prompts (ADR-0004) | in | prompt_router.py (0.14.0) |

### tcb-developer/work-summary-skills (586cc12, unchanged; MIT)
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Date taken from the harness and checked against the clock | not adopted | eng-delivery reads dated entries and git history |
| Parallel sessions append, never overwrite | not adopted | one progress file per session |
| Resume mentions open or blocked rows | not adopted | low value; the resume brief shows Follow-ups |
| Ask once when several folders fit | not adopted | not applicable |
| Plain-English summary beside the technical detail | in | progress-entry template `**Summary**` |
| "Task N:" end-of-day block | in | eng-delivery daily summary |
| One task per deliverable | in | eng-delivery |
| Same-day reverts left out | in | eng-delivery |
| Work in progress as a note | in | eng-delivery |
| Project terms; no paths, hashes or acronyms | in | eng-delivery |
| Plain punctuation for pasting | in | eng-delivery |
| No filler words | in | eng-delivery |
| Grep summary lines instead of reading files | in | eng-delivery |
| Never invent work | in | eng-delivery |
| Read-only formatter; the user sends it | in | eng-delivery |
| Routing for work-summary prompts | in | prompt_router.py |
| Uncommitted `WORK_SUMMARY/` log | rejected | a second history, lost on `git clean -x`; still holds |
| A section opened per task | rejected | a write per message; still holds |
| `INDEX.md` | rejected | dated file names already index; still holds |
| `CONTEXT.md` | rejected | the project CLAUDE.md holds it; still holds |
| A block appended to the project CLAUDE.md | rejected | eng-project-init owns that file; still holds |
| Markers for timesheet extraction | rejected | nothing reads them yet; still holds |
| Check whether code changed since the recorded commit | rejected | entries cite PRs and commits; still holds |
| Session-end audit and backfill | rejected | the Definition of Done requires the entry; still holds |
| "Use PROACTIVELY" description | rejected | competes with eng-docs; still holds |

### elementalsouls/Claude-BugHunter (v2.1, main 5b7e76e; code MIT, content CC BY 4.0 (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| A 400 from validation does not prove a missing auth check (skills/triage-validation) | **added** | eng-review "Before a finding goes in the report" |
| No "could potentially"; reproduce from a fresh session; exact request (report-writing, triage-validation) | **added** | eng-review |
| Impact proof: IDOR shows another user's data; SSRF shows a callback (triage-validation, bb-methodology) | **added** | eng-review |
| Per-class "where bugs hide" lists (hunt-idor, hunt-business-logic, hunt-race-condition, hunt-file-upload, hunt-oauth) | **added** | eng-security/stacks.md "Where bugs hide in any stack" |
| Evidence hygiene: mask your tokens and other people's data (evidence-hygiene) | **added** | eng-review |
| Identifier denylist pre-commit hook (.githooks/pre-commit) | **added** | eng-ship/github.md (public repos) |
| Marker, body-diff and statistical-sample discipline (bb-methodology) | not adopted | pen-test detail; the proof rule covers the core |
| Skills-off ablation and false-positive fixtures (eval/) | in | eng-os-review §4 (with and without); skill_cases negatives |
| Deterministic scope gate (engine/scope.py) | not adopted | offensive scoping |
| Ledger rotation (commands/memory-gc.md) | not adopted | eng-os data is small |
| Offensive skills: payload tables, identity and VPN attacks, recon, autopilot, HackerOne MCP | not adopted | offensive; out of scope for eng-os |
| Installing the pack | rejected | whole-pack rejection: 82 skills plus commands would take over the chat |

### trailofbits/skills (main 149d7b2; CC-BY-SA-4.0, ideas only (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| A checker that inspects zero items must fail, with a known-bad self-test (AGENTS.md) | **added** | eng-testing/tooling.md |
| Fail-open fallback secrets (insecure-defaults/references/fallback-secrets.md) | **added** | eng-security/stacks.md |
| Reviewers report everything with a severity; filter later (AGENTS.md) | **added** | eng-review §2 |
| Skill linting: unquoted `: ` drops metadata (AGENTS.md) | **added** | `eng-os verify` |
| Differential review: risk not size, blame removed security code, blast radius (differential-review) | **added** | eng-review §2 |
| Verify a finding: attacker control, reachability, impact, a negative case (fp-check) | **added** | eng-review |
| AI agents in GitHub Actions (agentic-actions-auditor) | **added** | eng-ship/github.md "A model in CI" |
| zizmor, actionlint, `persist-credentials: false` (.github/workflows) | **added** | eng-ship/github.md |
| Dangling reference links in skills (AGENTS.md) | in | `eng-os verify` referenced-file check |
| Hardcoded `/Users/` paths in skills (AGENTS.md) | not adopted | the installer renders paths; no hardcoded home in eng-os skills |
| Supply-chain audit: missing data is never "clean"; maintainer concentration (supply-chain-risk-auditor) | not adopted | eng-security A03 covers abandoned packages; low frequency here |
| Rationalisations-to-reject tables (AGENTS.md) | in | red-flags tables in eng-review, eng-testing, eng-ship |
| API footgun review (sharp-edges) | not adopted | low value |
| Grader judges the artifact, not the reply (AGENTS.md) | in | the trigger eval scores tool calls |
| Stop and SubagentStop prompt hooks (fp-check/hooks) | not adopted | a model call on every stop |
| Redirect GitHub fetches to `gh` (gh-cli/hooks) | not adopted | small gain; breaks on private repos |
| Second opinion from another vendor's model (second-opinion) | not adopted | code leaves the machine |
| Mutation and property tests | in | eng-testing/test-types.md |
| Skill size cap | in | `eng-os verify` budgets |
| Fast, regex-first hooks | in | guard.py |
| Variant search after a fix (variant-analysis) | in | eng-testing bug-fix protocol step 4 |
| Installing the marketplace | rejected | whole-pack rejection; still applies |

### trailofbits/claude-code-config (main 2109be9; no licence file, ideas only (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Read-deny for credential stores (settings.json) | **added** | guard `SECRET_PATH` gains `~/.config/gh/hosts.yml` and gcloud default credentials (`.kube/config`, `.docker/config.json` were already there) |
| Release-age delay, install scripts off, hashes, Dependabot cooldown (rules/typescript.md, rules/python.md) | **added** | eng-security A03; eng-ship/github.md |
| Ask on edits to shell start-up files (settings.json) | **added** | guard `persistent-system` and `shell-startup` |
| Do not leave work as "pre-existing" or "out of scope" (README) | **added** | eng-review §3 |
| Transcript retention `cleanupPeriodDays` (settings.json) | **added** | docs/COMPANY-ROLLOUT.md (option) |
| Actions: `persist-credentials: false`, actionlint, zizmor, input via `env:` (rules/github-actions.md) | **added** | eng-ship/github.md; rule ci-deploy |
| Telemetry env (`DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`) | not adopted | a company decision, and it may switch off features; not set by default |
| `enableAllProjectMcpServers: false` | not adopted | already the default; a project's settings outrank it, so managed settings are the place (COMPANY-ROLLOUT) |
| Pin the subagent spawn depth | not adopted | variable not confirmed in the docs; the rule is in implementation-plans.md instead |
| Status line with context and cache rate (scripts/statusline.sh) | not adopted | the context-size note covers it |
| Fast-mode cost note | not adopted | not relevant to policy |
| Output style, `/rewind`, per-language lint configs | not adopted | overlaps global CLAUDE.md §8; other stacks |
| Block recursive rm, force push, reset, pipe to shell | in | guard rules |
| Hook errors say what to do instead | in | guard messages |
| Path-scoped rules and a lean CLAUDE.md | in | global/rules |
| Mutation and property tests | in | eng-testing |
| Pin versions; no unpinned `npx` | in | eng-security A03; guard |
| Re-insert rules after compaction | in | session_start.py |
| Autonomous fix, review and merge commands that do not ask (commands/) | rejected | conflict with the approval gates (global CLAUDE.md §2) |
| `--dangerously-skip-permissions` (README) | rejected | conflicts with the approval gates |

### anthropics/claude-code-security-review (main 0c6a49f; MIT (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Find, then verify each finding in its own sub-task; drop low confidence (security-review.md) | **added** | eng-review "Before a finding goes in the report" |
| Report floor: unconfirmed findings get no severity (security-review.md) | **added** | eng-review ("needs validation") |
| Scope: only issues the diff introduces (security-review.md) | **added** | eng-review |
| Skip generated files (github_action_audit.py) | **added** | eng-review §2 |
| Keep the API key from the model's tools, `ps` blocked (github_action_audit.py) | **added** | eng-ship/github.md "A model in CI" |
| Read-only tool allowlist for a review (security-review.md frontmatter) | **added** | eng-ship/github.md; eng-review §2 |
| Approval before workflows run for outside contributors (README) | **added** | eng-ship/github.md |
| Hard-exclusion list: DoS, rate limits, log spoofing, React XSS (security-review.md) | not adopted | conflicts with eng-os's A09 and A10 stance; taken only where it matches the boundary rule |
| Organisation-tunable exclusions (docs/custom-*.md) | not adopted | the project CLAUDE.md does this |
| Regex post-filter of findings (findings_filter.py) | not adopted | code-only |
| Retry without the diff when the prompt is too long (prompts.py) | not adopted | narrow |
| Comment de-duplication and run cache (action.yml) | not adopted | product feature |
| SHA-pinned actions; least-privilege permissions | in | eng-ship/github.md |
| Its own unpinned `npm install -g` (a counter-example) | in | eng-security A03 |
| Finding format with exploit scenario and fix | in | eng-security §4; eng-review §4 |
| PR content as untrusted | in | eng-security "Agents and tools" |
| No `pull_request_target` | in | eng-ship/github.md |
| Its eval harness (claudecode/evals) | not adopted | eng-os has its own |

### anthropics/claude-plugins-official (+ claude-code examples, mods) (main d7d3279 (Apache-2.0); claude-code 16043fc (all rights reserved, ideas only) (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Risky-code reminders on Edit and Write (security-guidance/hooks/patterns.py) | **added** | guard code note, with PHP, Frappe and Odoo patterns (`ENG_OS_CODE_NOTE=0` turns it off) |
| Actions injection field list (patterns.py) | **added** | eng-ship/github.md; rule ci-deploy; code note for workflows |
| Managed settings: `strictKnownMarketplaces`, `allowManagedMcpServersOnly`, `allowManagedPermissionRulesOnly`, sandbox domains (examples/settings) | **added** | docs/COMPANY-ROLLOUT.md §3 |
| Verifiers told to disprove each finding (claude-security/agents/scan-verifier.md) | **added** | eng-review |
| Whole-repo audit accounting: each folder reviewed or set aside (claude-security README) | **added** | eng-review §3 |
| Silent-failure checklist (pr-review-toolkit/agents/silent-failure-hunter.md) | in | eng-review/coding-standards.md |
| Language-server plugins (php-lsp, pyright-lsp, typescript-lsp) | not adopted | follow-up pilot: savings unmeasured; dynamic Frappe and Odoo code limits them |
| Train and held-out split for description tuning (skill-creator/scripts/run_loop.py) | not adopted | eng-os routes by regex |
| Blind A/B comparator (skill-creator/agents/comparator.md) | not adopted | pressure tests exist |
| Hook `if:` filter and `asyncRewake` (security-guidance/hooks/hooks.json) | not adopted | spawn cost is small; a background model review is model-based review |
| With and without baseline runs (skill-creator) | in | eng-os-review §4 |
| Session usage report (session-report) | in | `eng-os usage` |
| Repo content as data; no credential values in reports (claude-security) | in | global CLAUDE.md §4 |
| CLAUDE.md quality rubric (claude-md-management) | not adopted | eng-project-init §3 checklist |
| Branch cleanup, `rg` validator, SARIF ids, privacy and HIPAA mods | not adopted | no transferable lesson |
| User-written guard rules (hookify) | rejected | docs/REQUIREMENTS.md bars project-level guard switches |
| Installing security-guidance or claude-security | rejected | they send diffs to a model each turn and take over the chat (model-based review; whole-pack) |

### getsentry/skills (main a582c51; Apache-2.0 (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Scan third-party skills: hidden characters, symlinks out, frontmatter hooks, load-time commands (skill-scanner) | **added** | `eng-os verify` (warns); MCP-POLICY §6 checklist |
| Secrets leaking through generated repr and serialisation (secret-serialization) | **added** | eng-security/stacks.md |
| Commit messages carry no customer names, emails or ticket text (commit) | **added** | eng-ship/releases.md |
| GitHub Actions: comment triggers, agents on PR content, cache poisoning (gha-security-review) | **added** | eng-ship/github.md |
| PR screenshot hygiene (pr-screenshots) | in | rule docs (no secrets or customer data in screenshots) |
| CI-fix loop triage (iterate-pr) | not adopted | low value |
| SECURITY_MODEL.md with a resolver (security-model) | not adopted | eng-security threat-models per change |
| Skill-writer tooling and AXIS evals (skill-writer) | not adopted | tests/skill_cases.json; an npm dependency |
| Exploitable-only findings with evidence levels (security-review, find-bugs) | in | eng-review evidence tags |
| Conventional commits; branch names (commit, create-branch) | in | eng-ship/releases.md; github.md |
| Never commit to main; PR body as cover note (commit, pr-writer) | in | global CLAUDE.md §7; templates/release |
| Short agent instruction file (agents-md) | in | eng-project-init (under 120 lines) |
| IDOR and ORM review (django-*) | in | eng-security A01 |
| Prompt optimiser, code simplifier, doc co-authoring, warden | not adopted | no need here |
| Sentry-specific skills | not adopted | product-specific |
| Installing the marketplace | rejected | whole-pack rejection: broad triggers ("every request to commit") |

### github/spec-kit (v1.4.3, main 61d3abb; MIT (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| Ambiguity pass over the spec (templates/commands/analyze.md) | **added** | eng-design §1 |
| Converge: re-check code against acceptance criteria; "unrequested" gap type (converge.md) | **added** | implementation-plans.md §3 |
| Assumptions stated for what was decided without asking (specify.md) | **added** | spec template §7 "Assumptions" |
| Cap clarifying questions at five (clarify.md) | not adopted | eng-design §1 already limits questions |
| Requirements-quality checklist (checklist.md) | not adopted | overlaps the ambiguity pass |
| Stop on unchecked checklists before implementing (implement.md) | not adopted | eng-os gates on plan approval |
| Ignore-file check before building (implement.md) | not adopted | eng-project-init and the guard cover it |
| Hash-tracked install manifest (integrations/manifest.py) | in | bin/eng-os install manifest |
| Bounded downloads (_download_security.py) | not adopted | eng-os installs nothing from archives |
| Constitution of governing principles (constitution-template.md) | in | global CLAUDE.md |
| Prioritised user stories with an independent test (spec-template.md) | in | spec template §3 and §5 |
| Task format with parallel marks (tasks.md) | in | implementation-plans.md |
| TDD order; halt on failure (implement.md) | in | global CLAUDE.md §3; implementation-plans.md |
| `disable-model-invocation` for user-only skills | in | eng-os-review frontmatter |
| Model-interpreted before and after hooks (.specify/extensions.yml) | rejected | competes with eng-os hooks (whole-pack reasoning) |
| Auto-commit extension (extensions/git) | rejected | commits only when asked (global CLAUDE.md §7) |

### cloudflare/security-audit-skill (main c1c8a8c; MIT (new))
| Idea (repo file) | Status | eng-os file, or the reason |
|---|---|---|
| "Needs validation" state with the missing fact and an owner check, no severity (VALIDATION-AND-REPORTING.md) | **added** | eng-review |
| Candidate gate: lower-trust actor, crossed boundary, concrete result (HUNTING.md) | **added** | eng-review |
| Verifier briefed to refute, given the finding alone; upgrades re-checked (VALIDATION-AND-REPORTING.md) | **added** | eng-review |
| High versus Medium: defeats or weakens a control (SKILL.md) | **added** | eng-review severity rubric |
| Data isolation: derived copies, soft delete, migration defaults, restores (DATA-ISOLATION-AND-LIFECYCLE.md) | **added** | eng-security/stacks.md |
| Auth transitions: MFA, step-up, recovery, linking, API-key scope (WEB-PROTOCOL-AND-AUTH.md) | **added** | eng-security/stacks.md |
| Mobile: deep links, WebView bridges, logout leakage (DESKTOP-MOBILE-AND-LOCAL-IPC.md) | **added** | eng-security/stacks.md Flutter |
| LLM features: tool handlers re-check permission; approvals bound to the action (AI-AND-LLM.md) | **added** | eng-security "Agents and tools" |
| Messaging: duplicates, ordering, acknowledgement before commit (PROTOCOLS-RPC-AND-MESSAGING.md) | **added** | eng-security/stacks.md |
| Say what a scoped run did not cover (SKILL.md run profiles) | **added** | eng-review §3 |
| Untrusted target code: read it, do not run it (SKILL.md execution safety) | **added** | eng-security "Agents and tools" (untrusted clones) |
| Business-logic and feature-abuse classes (ATTACK-CLASSES.md) | in | eng-security A06; stacks.md "Steps and state" |
| Coverage ledger, fingerprints, critic waves (SKILL.md, HUNTING.md) | not adopted | heavy and token-hungry; the coverage line keeps the useful part |
| JSON findings schema and validators (report-schema.json, *.cjs) | not adopted | needs node; suits a harness |
| File-promotion procedure (SKILL.md) | not adopted | not needed here |
| Supply-chain, CI, cloud, client-side, resource-exhaustion checklists | in | eng-ship/github.md; eng-security A02, A03 |
| "Obvious things" sweep: debug gates, seed credentials, open redirects (ATTACK-CLASSES.md) | in | eng-security §2 |
| Installing the skill | rejected | its description triggers on any security question and would collide with eng-security (whole-pack reasoning) |

