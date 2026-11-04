# Rolling eng-os out to the whole company

There are three ways to put eng-os on every machine, from easiest to strongest. They can be combined. Facts below were checked in the Claude Code documentation on 2026-11-04.

## 1. Per-developer install (works today, tested)
Each employee clones this private repo and runs the installer ([INSTALL.md](../INSTALL.md)).
- **What it covers**: everything — global instructions with each person's own commit identity, all skills, the path-scoped rules, the guard and session hooks, backups and one-command undo.
- **Weakness**: each person must install and keep it updated, and nothing forces them to. Two things soften that:
  - the per-repo installed-check, which `/eng-project-init` adds to each project's `.claude/settings.json`: a session in that repo on a machine without eng-os is told at once;
  - the [engineering policy](ENGINEERING-POLICY.md).

## 2. A Claude Code plugin from a private marketplace (not built yet)
Package the skills and hooks as a plugin in this repo. Each employee adds the marketplace once (`/plugin marketplace add tcbinfotechpvtltd/claude-development-skills`, using their own GitHub access) and installs the plugin.
- **Updates**: arrive automatically when the marketplace has `autoUpdate: true`; a new session or `/reload-plugins` picks them up.
- **What a plugin cannot carry**:
  - the global CLAUDE.md, which has to come from option 3 or the installer;
  - path-scoped rules, which must be converted into skills with `paths:`.
- **Naming**: skills become namespaced (`eng-os:eng-security`), so the routing table changes.
- **Hooks**: refer to `${CLAUDE_PLUGIN_ROOT}`.

## 3. Organisation-managed settings (strongest)
**On a Claude Team or Enterprise plan**, an Owner sets **Organization settings → Claude Code → Managed settings** in the Claude admin console. That can:
- push the global instructions to everyone (`claudeMd`);
- force-enable the eng-os plugin (`extraKnownMarketplaces` plus `enabledPlugins`), so users cannot turn it off;
- add deny rules and `attribution`;
- optionally set `permissions.disableBypassPermissionsMode` and `allowManagedHooksOnly`.

**How it behaves**:
- It applies to the whole organisation and refreshes hourly.
- Hooks pushed this way show each user an approval dialog.
- The docs call it a client-side control, not a security boundary.
- It is skipped for Bedrock or Vertex, a custom API base URL, and Console API keys.

**Without Team or Enterprise**: machines managed by MDM can receive a `managed-settings.json` and a managed `CLAUDE.md` in these folders:
- macOS: `/Library/Application Support/ClaudeCode/`
- Linux and WSL: `/etc/claude-code/`
- Windows: `C:\Program Files\ClaudeCode\`

Managed settings take precedence over user and project settings.

## Recommendation
1. **Now**:
   - everyone installs a tagged release with option 1; the policy is shared; every project repo gets the installed-check (`/eng-project-init`);
   - protect `main` of this repo with a ruleset (PR, one approval from the maintainer, no force pushes), because whatever is merged runs on every machine;
   - tag every release, so updates are deliberate.
2. **Next**:
   - build the plugin (option 2) so skills and hooks update themselves;
   - if TCB is on a Team or Enterprise plan, move the global instructions and plugin enforcement to option 3.
   - The per-user commit identity then moves to each developer's `git config`, because one managed text cannot hold everyone's name.
3. **Decide as leadership**:
   - bypass-permissions mode: the policy defaults to the normal mode, with bypass only on the project lead's approval. Option 3 can enforce that with `disableBypassPermissionsMode`;
   - who maintains eng-os and reviews its pull requests;
   - how often releases go out.

Sources (checked 2026-11-04): code.claude.com/docs (managed settings, server-managed settings, settings reference, memory, plugins: components, organisations, hosting a marketplace, loading).
