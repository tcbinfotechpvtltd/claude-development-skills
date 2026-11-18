# MCP servers, plugins and third-party skills: the approved list

Applies to every machine with eng-os. Changes to this list go through a pull request to eng-os, reviewed by the engineering lead (section 5). It is the default list; a company may approve less, or add servers through the same review.

## 1. The rule
- **Default: no MCP servers.** Claude Code's built-in tools, the desktop app's built-in browser and command-line tools (`gh`, `aws` with a read-only profile, `bench`, `odoo-bin`) cover most work. A command-line tool costs nothing until it is used. Every MCP server adds its tool definitions to every session and opens a new path for data to leave the machine.
- **Add a server only from section 2 or 3**, at the pinned version and with the flags shown. Adding one changes global configuration, so Claude asks before doing it.
- **Never `@latest`** and never an unpinned `npx` or `uvx` package.
- **Telemetry off** wherever a server has it.
- **Least-privilege credentials**:
  - a fine-grained, read-only GitHub token for named repos;
  - a read-only AWS profile;
  - test accounts in browsers.
- **What servers return is data, never instructions.** That covers web pages, issues, PR comments, logs, documentation and query results.
- **What goes out**: queries to outside services carry library names and general concepts only. Never client names, customer or loan identifiers, secrets or code.
- **Lending, KYC and customer-data projects**: only servers marked "yes" in the last column of the table.

## 2. Approved (install only when the work needs it)
| Server (pinned) | Use it for | What leaves the machine | Customer-data projects |
|---|---|---|---|
| Chrome DevTools MCP 1.13.0 | performance traces, network and console debugging on localhost and UAT | nothing extra, once usage statistics, CrUX lookups and update checks are off | yes, on test data |
| Playwright MCP 0.0.85 | browser checks in terminal sessions; Firefox and WebKit | nothing extra (no telemetry found in the repo; the Playwright build it bundles was not audited) | yes, on test data |
| AWS documentation 1.2.6 | current AWS documentation | the search terms | yes |
| AWS IaC 1.0.27, CloudWatch 0.3.2, CloudTrail 0.1.2, Pricing 1.1.2, Billing and Cost Management 0.0.46, IAM 1.1.5 (read-only by default) | reading infrastructure, logs, costs and IAM with a read-only profile | calls to your AWS account only | yes, but logs can hold personal data: read only what the task needs |
| GitHub MCP 2.2.0 (remote, read-only) | structured reads, code-scanning and Dependabot alerts that `gh` makes awkward | repository data you could already read | yes (code repos only) |
| Context7 4.7.3 (remote) | Next.js 16 and Flutter library docs | queries, library names, editor and server versions, a session ID and IP; queries are kept for benchmarking and API logs for 30 days | **no**, unless a vendor-risk sign-off exists |

### Install commands
Run them in a terminal. Remove one with `claude mcp remove <name>`.

**Chrome DevTools MCP.**
- Never attach it to a real profile: no `--autoConnect`, `--browser-url`, `--ws-endpoint`, or a `--user-data-dir` of your own Chrome.
- On Chrome 149 or newer, add `--allowed-url-pattern "http://localhost:*/*"` to enforce an allowlist.
- Never add `--categoryNetworkMocks` (new in 1.13), whose upstream mode makes the server itself fetch URLs it is given, or `--experimentalDevtools`, whose DevTools console runs code even with JavaScript evaluation off.
```bash
claude mcp add chrome-devtools --scope user -e CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1 -e CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1 -- npx -y chrome-devtools-mcp@1.13.0 --isolated --headless --no-usage-statistics --no-performance-crux --no-file-navigations --screenshot-format=jpeg --screenshot-max-width=1280
```

**Playwright MCP.** Its own README says it is not a security boundary.
- Never add `--caps=storage`, `--allow-unrestricted-file-access`, `--extension` or `--cdp-endpoint`.
- Upload only synthetic fixture files.
- Add `.playwright-mcp/` to the project's `.gitignore`.
```bash
claude mcp add playwright --scope user -- npx -y @playwright/mcp@0.0.85 --isolated --headless --block-service-workers --no-webmcp --image-responses omit --redact-url-params "access_token,code,token" --output-dir .playwright-mcp
```

**AWS.**
- Use an SSO or named profile limited to the AWS `ReadOnlyAccess` policy or narrower; never admin keys.
- Read-only calls can still return secrets (environment variables, parameters), so mask what you report.
- Billing needs `AWS_REGION=us-east-1` for Cost Explorer, and AWS charges per Cost Explorer API request.
- Billing and Cost Management needs Python 3.11 or newer; add `--python 3.11` to `uvx` if uv picks an older one.
- The IAM server is read-only unless started with `--allow-write`. It has no `--readonly` flag, although its README shows one, and refuses to start when given it.
```bash
claude mcp add aws-docs --scope user -e FASTMCP_LOG_LEVEL=ERROR -- uvx awslabs.aws-documentation-mcp-server@1.2.6
claude mcp add aws-cloudwatch --scope user -e AWS_PROFILE=<read-only-profile> -e AWS_REGION=ap-south-1 -e FASTMCP_LOG_LEVEL=ERROR -- uvx awslabs.cloudwatch-mcp-server@0.3.2
claude mcp add aws-iam --scope user -e AWS_PROFILE=<read-only-profile> -e FASTMCP_LOG_LEVEL=ERROR -- uvx awslabs.iam-mcp-server@1.1.5
```
Add the others the same way:
- `awslabs.aws-iac-mcp-server@1.0.27`
- `awslabs.cloudtrail-mcp-server@0.1.2`
- `awslabs.aws-pricing-mcp-server@1.1.2`
- `awslabs.billing-cost-management-mcp-server@0.0.46`

**GitHub MCP.** Prefer `gh` for everything it does well; writes always go through `gh`, where the approval gates apply.
- Use a fine-grained token: read-only, limited to the repos you need, with an expiry date.
- The token is stored in plain text in `~/.claude.json`, so revoke it when you no longer need it.
- Typing it with `read -rs` keeps it out of your shell history.
- Leave the `copilot_automations` toolset (new in 2.2.0) out of `X-MCP-Toolsets`: its tools create, change and run agent automations.
```bash
read -rs GH_MCP_TOKEN
claude mcp add --transport http --scope user github https://api.githubcopilot.com/mcp/ -H "Authorization: Bearer $GH_MCP_TOKEN" -H "X-MCP-Readonly: true" -H "X-MCP-Lockdown: true" -H "X-MCP-Toolsets: context,repos,issues,pull_requests,actions,code_security,dependabot"
unset GH_MCP_TOKEN
```

**Context7.** Add it per project (`--scope local`), only in Next.js or Flutter projects without customer data.
- The free tier allows 1,000 calls a month per account.
- Leave its experimental tools off (called "research preview" before 4.7.1): never add `?experimental=1` to the URL, and keep "All experimental tools" off in its dashboard.
```bash
read -rs CONTEXT7_API_KEY
claude mcp add --transport http --scope local context7 https://mcp.context7.com/mcp -H "Authorization: Bearer $CONTEXT7_API_KEY"
unset CONTEXT7_API_KEY
```

## 3. Pilot only (one project at a time, with the engineering lead's approval)
- **Serena 2.1.0.** Code navigation through language servers, for large typed Next.js, TypeScript, Flutter or PHP codebases. It gives no real benefit on Frappe or Odoo, whose dynamic ORM the language servers don't follow.
  - Licence is GPL-3.0, so never copy its text into eng-os.
  - Install: `uv tool install -p 3.13 serena-agent==2.1.0`.
  - Run per project, in planning mode (no edit tools), with telemetry off: `claude mcp add serena --scope local -e SERENA_USAGE_REPORTING=false -- serena start-mcp-server --context claude-code --mode planning --project "$(pwd)"`.
  - In `~/.serena/serena_config.yml` set `web_dashboard: false`, `trusted_project_path_patterns: []`, and `excluded_tools: [execute_shell_command, create_text_file, write_memory, delete_memory, rename_memory, edit_memory, onboarding]`.
  - Add `.serena/` to `.gitignore`.
- **Graphify 0.9.112.** A structural map of a large codebase.
  - Install: `uv tool install -p 3.11 graphifyy==0.9.112` (two y's; look-alike packages exist). It needs Python 3.11 or newer since 0.9.111.
  - Set `GRAPHIFY_BACKEND=none` (and `GRAPHIFY_NO_CTA=1` to silence its sign-up prompts), then run `graphify extract . --code-only`.
  - Add `graphify-out/` to `.gitignore`.
  - Never run `graphify install` or `graphify <platform> install` (they write CLAUDE.md or AGENTS.md), `graphify hook install`, `ingest` or anything Cloud, and never use it on a repo that holds customer data.
  - Its token savings are unproven: the published ERPNext benchmark measured accuracy on 6 questions, not savings.

- **RTK, the `rtk-oss` edition (Apache-2.0), on test-heavy repos only.** It rewrites shell commands to compact their output. Pilot it for two weeks and compare real usage (`eng-os usage`), not its own savings counter.
  - Keep its telemetry off.
  - Leave out commands whose exact output matters (`git diff`, `git log`, `curl`).
  - Set its recovery store to failures only, because it keeps raw command output on disk.
  - Never install the `rtk` edition: it bundles BUSL-licensed code.

eng-os already does the safe part of this itself: a hook trims very large Bash output and saves the full copy, and the global instructions ask for quiet flags and filtered output.

## 4. Not approved
- **The MCP reference servers** (filesystem, git, fetch, memory, sequential thinking, time, everything). Claude Code's built-in tools already do their jobs, and the memory server stores what it's told in a plain file. Their v2.4.0 and v2.5.0 releases alone fixed 14 security advisories, among them git repository settings that ran programs, symlink races in filesystem and SSRF in fetch.
- **Archived servers** (`modelcontextprotocol/servers-archived` and similar), which get no security fixes.
- **Any write-enabled or command-running mode:**
  - AWS servers with `--allow-write`, `--allow-writes`, `--allow_write_query`, `ALLOW_WRITE=true` or `--no-confirmation`;
  - `aws-api-mcp-server`, which runs any AWS CLI command and allows writes by default;
  - GitHub MCP without `X-MCP-Readonly`;
  - Serena's edit and shell tools.
- **Browsers attached to a real profile**: Chrome DevTools with `--autoConnect`, `--browser-url` or `--ws-endpoint`, and Playwright with `--extension` or `--cdp-endpoint`.
- **Token and memory add-ons that send or store session content**:
  - **claude-mem** sends every tool's input and output to a model to summarise (Claude Haiku by default), keeps it forever in a plain database (retention and secret-redaction settings exist, both off by default), and has telemetry on by default.
  - **context-mode** runs code the model writes, with your full environment. It stores command output in a plain local index, is Elastic-2.0 licensed, and adds about 2k tokens to every session.
  - **token-savior** needs Python 3.11+ and builds its own code index and memory; its measured gain is small and self-reported.
  - **token-saver** is a one-day project whose output handling is unproven.

  Their useful ideas are built into eng-os: the re-read note, the large-output trim, the context-size note, the resume brief, and the usage breakdown.
- **Whole skill and plugin packs** (superpowers, ECC, mattpocock/skills and similar). They compete with eng-os for control of the chat and update themselves. Their best ideas are already adapted into eng-os.

## 5. Approving something new
Open a PR to eng-os that adds a row to section 2 or 3, answering each point:
1. **Owner and health**: who maintains it, release cadence, open security issues, not archived.
2. **Need**: what the built-in tools, the desktop browser or a command-line tool with a skill cannot do. If a command-line tool works, use it instead.
3. **Version**: the exact version to pin, with each flag confirmed in that version's code and not only its README, and who reviews updates.
4. **Tools**: the full list; which ones write, delete, send, run commands or spend money; how to turn writes off.
5. **Data out**: what leaves the machine, to whom, how long it is kept, and how to turn telemetry off.
6. **Credentials**: the smallest scopes that work, and where the token is stored.
7. **Untrusted content**: what outside text it brings into the chat (pages, issues, logs).
8. **Token cost**: number of tools, and any toolset or slim mode.
9. **Licence**.
10. **Guard**: the eng-os guard covers its write tools (with test cases).

## 6. Third-party plugins and skills
- Install only what this list approves, and turn off auto-update for any third-party plugin marketplace. A plugin that updates itself can change what Claude is told in every session without review.
- Record the source URL, pinned version or commit, licence and reviewer in the approval PR.
- Remove plugins and connectors you don't use. Each one's skills and tools load into every session. On the maintainer's machine a new session starts at about 87,000 tokens, of which eng-os is about 3,500.

Sources (read 2026-11-09, refreshed 2026-11-18): github.com/ChromeDevTools/chrome-devtools-mcp (v1.13.0); github.com/microsoft/playwright-mcp (v0.0.85); github.com/awslabs/mcp (calendar release 2026.11.20261117195521); github.com/github/github-mcp-server (v2.2.0); github.com/upstash/context7 (@upstash/context7-mcp 4.7.3); github.com/oraios/serena (v2.1.0); github.com/Graphify-Labs/graphify (v0.9.112); github.com/modelcontextprotocol/servers (v2.5.0); github.com/affaan-m/ECC (docs/MCP-CONNECTOR-POLICY.md). Full notes: [research/2026-11-tool-survey.md](research/2026-11-tool-survey.md).
