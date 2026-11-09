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
