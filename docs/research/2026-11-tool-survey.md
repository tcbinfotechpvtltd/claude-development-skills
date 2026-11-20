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
