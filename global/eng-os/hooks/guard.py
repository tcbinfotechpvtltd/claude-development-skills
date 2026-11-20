#!/usr/bin/env python3
"""eng-os guard: deterministic PreToolUse safety layer for Claude Code.

Runs on Bash, file tools and MCP tools. For each call it may:
  deny  - catastrophic or never-legitimate actions (the user can still run them by hand)
  ask   - destructive, irreversible, outward-facing, production or secret-exposing actions
Anything else passes through with no output (zero context cost).

Fail-open by design: an internal error never blocks work; it is logged to
~/.claude/eng-os/state/guard-errors.log and surfaced by `eng-os verify`.
Python 3.9 compatible, stdlib only. Unit tests: tests/guard_cases.json.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
ENGOS = os.environ.get("ENGOS_HOME") or os.path.join(HOME, ".claude", "eng-os")
STATE = os.path.join(ENGOS, "state")
MARK = "[eng-os guard]"

DEFAULT_CONFIG = {
    "protected_branches": ["main", "master", "prod", "production", "live", "uat", "release"],
    "block_claude_coauthor": True,
    "disabled_rules": [],
}

# ---------------------------------------------------------------- patterns
SECRET_PATH = re.compile(
    r"""(?:^|[\s/'"=:(@])(?:"""
    r"""\.env(?!\.(?:example|sample|template|dist|defaults)\b)(?:\.[\w.-]+)?"""
    r"""|id_(?:rsa|ed25519|ecdsa|dsa)(?!\.pub)"""
    r"""|[\w.-]+\.(?:pem|key|p12|pfx|keystore|jks|ppk)"""
    r"""|\.aws/credentials|\.netrc|\.pgpass|\.git-credentials|\.npmrc|\.pypirc"""
    r"""|\.docker/config\.json|\.kube/config|credentials\.json|service[-_]?account[\w.-]*\.json"""
    r"""|\.config/gh/hosts\.ya?ml|application_default_credentials\.json"""
    r"""|[\w.-]*_secrets(?:/|\b)|secrets\.(?:json|ya?ml|env|txt|toml)"""
    r""")(?=$|[\s'";|&)<>])""",
    re.I,
)
CLAUDE_CREDS = ".claude/.credentials.json"
NEVER_READ = re.compile(r"\.claude/\.credentials\.json")
KEYCHAIN_DUMP = re.compile(r"\bsecurity\s+(?:find-(?:generic|internet)-password\b.*\s-w\b|dump-keychain)")
READ_VERBS = re.compile(r"(?:^|[\s;&|(`$'\"])(?:cat|less|more|head|tail|bat|strings|xxd|od|hexdump|base64|grep|egrep|rg|awk|sed|cut|sort|cp|scp|rsync|open|pbcopy|curl|nl|tac|jq|yq|python3?|node|php|ruby)\b")
# commands that print, copy or send a file named in their own arguments (interpreters: `python3 -c "open('.env')"`)
READ_CMDS = set("cat less more head tail bat strings xxd od hexdump base64 grep egrep rg awk sed cut sort cp scp rsync "
                "open pbcopy curl nl tac jq yq zip tar python python3 node php ruby perl deno bun".split())
ENV_FILE_FLAG = re.compile(r"--env-file(?:=|\s+)\S+")  # `node --env-file=.env app.js` loads it without printing it
# Grep `glob` values that pick out secret files: they match one of these names and none of the ordinary ones
SECRET_NAMES = (".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "server.pem", "server.key", "credentials.json",
                "secrets.yaml", ".npmrc", ".netrc", ".pgpass", "service-account.json")
ORDINARY_NAMES = ("package.json", "main.py", "index.ts", "README.md", "config.yaml", "settings.py", "app.php", "app.js")
# environment variable names whose underscore-separated parts mark them as secrets ($API_KEY, $DB_PASSWORD; not $MONKEY)
SECRET_VAR = re.compile(r"(?:^|_)(?:API_?KEY|KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIALS?|PRIVATE_KEY)(?:_|$)")
SAFE_VAR_SUFFIX = re.compile(r"_(?:PATH|FILE|DIR|ID|NAME|URL|URI|LENGTH|LEN|SIZE|COUNT|TYPE|ENABLED|MIN|MAX)$")
VAR_REF = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)")
HTTP_MUTATING = ("DELETE", "PUT", "PATCH")
HTTP_VERBS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
FIND_FILTERS = {"-name", "-iname", "-path", "-ipath", "-wholename", "-iwholename", "-regex", "-iregex", "-mtime",
                "-mmin", "-atime", "-amin", "-ctime", "-cmin", "-newer", "-size", "-empty", "-user", "-group", "-perm"}
SYSTEM_DIRS = ("/System", "/Library", "/usr", "/etc", "/var", "/bin", "/sbin", "/opt", "/private/etc", "/private/var")
SQL_DESTRUCTIVE = re.compile(r"(?i)\b(?:drop\s+(?:database|schema|table|user)|truncate\s+(?:table\s+)?[`\"\w.]+|alter\s+table\s+[`\"\w.]+\s+drop\b)")
DB_TOOL = re.compile(r"sql|query|exec|database|(?:^|[-_])db(?:$|[-_])|postgres|mysql|maria|supabase|sqlite|bigquery|snowflake|neon|mongo|redshift|clickhouse", re.I)

SECRET_CONTENT = [
    ("aws-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("stripe-live", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    ("razorpay-live", re.compile(r"\brzp_live_[A-Za-z0-9]{12,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{40,}")),
    ("openai-key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{40,}")),
    ("assigned-secret", re.compile(
        r"""(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|client[_-]?secret|private[_-]?key)"""
        r"""["']?\s*[:=]\s*["']([^"'\s$<>{}]{12,})["']""")),
]
PLACEHOLDER = re.compile(r"(?i)example|sample|changeme|change_me|placeholder|dummy|your[_-]|xxxx|\*\*\*\*|redacted|test|fake|<|\$\{|env\(|getenv|process\.env")
TEST_PATH = re.compile(r"(?i)(?:^|/)(?:tests?|spec|__tests__|fixtures?|mocks?|examples?)(?:/|$)|[._-](?:test|spec|example|sample)\.")
ENV_FILE = re.compile(r"(?:^|/)\.env(?:\.[\w.-]+)?$")
ENV_TEMPLATE = re.compile(r"(?:^|/)\.env\.(?:example|sample|template|dist|defaults)$")

GLOBAL_CONFIG_FILES = re.compile(
    r"\.claude/(?:settings(?:\.local)?\.json|CLAUDE\.md|eng-os/(?:hooks|bin|config\.json)|rules/|skills/(?:eng-|frappe-erpnext|fintech-lending)|agents/)"
)
SHELL_WRITE = re.compile(r"(?:(?<![0-9&])>>?(?!&|\s*/dev/null)|\btee\b|\bsed\s+-i|\bperl\s+-pi|\bcp\b|\bmv\b|\brm\b|\bln\b|\btruncate\b|\bchmod\b)")

# (rule id, decision, regex, reason) evaluated against the full Bash command
# shell start-up files and LaunchAgents: whatever is written there runs at every login or shell start
STARTUP_FILE = (r"(?:~|\$HOME|\$\{HOME\}|/Users/[^/\s]+|/home/[^/\s]+)/(?:\.(?:zshrc|zshenv|zprofile|zlogin|bashrc|bash_profile|"
                r"bash_login|profile)(?![\w.])|\.config/fish/config\.fish|Library/LaunchAgents/[^\s;|&\"']*)")
# `git` plus its own options (`-c k=v`, `-C dir`, `--no-pager`), so the next word is the subcommand, not an argument
GIT_SUB = r"""\bgit(?:\s+(?:-[cC]\s+(?:[^\s"']*"[^"]*"|[^\s"']*'[^']*'|\S+)|--[\w-]+(?:=\S+)?|-[a-zA-Z]))*\s+"""
BASH_RULES = [
    ("fs-wipe", "deny", re.compile(r"\brm\s+(?:-[a-zA-Z]+\s+|--[a-z-]+\s+)*(?:--\s+)?[\"']?(?:/|~/?|\$HOME/?|\$\{HOME\}/?|/\*|~/\*|\$HOME/\*|/Users/?|/Users/[^/\s]+/?|/System\S*|/usr/?|/etc/?|/var/?)[\"']?(?:\s|$|;|&|\|)"),
     "would delete the filesystem root, a system directory or the home directory"),
    ("disk-destroy", "deny", re.compile(r"\bmkfs(?:\.\w+)?\b|\bdd\b[^\n;|&]*\bof=/dev/(?:r?disk|sd|nvme|hd)|\bdiskutil\s+(?:erase\w*|zero\w*|partitionDisk|reformat)\b|:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
     "destroys disks/partitions or is a fork bomb"),
    ("credential-dump", "deny", KEYCHAIN_DUMP, "dumps OS keychain secrets"),
    ("git-force-push", "ask", re.compile(r"\bgit\b[^\n;|&]*\bpush\b(?:(?!--force-with-lease)[^\n;|&])*?(?:\s--force(?![-\w])|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\b|\s\+[\w./:-]+)"),
     "force-push rewrites remote history"),
    ("git-delete-remote", "ask", re.compile(r"\bgit\b[^\n;|&]*\bpush\b[^\n;|&]*(?:\s--delete\b|\s-d\b|\s:[\w./-]+)"),
     "deletes a remote branch or tag"),
    ("git-discard", "ask", re.compile(r"\bgit\b[^\n;|&]*\b(?:reset\s+(?:[^\n;|&]*\s)?--hard|clean\s+-[a-zA-Z]*f|checkout\s+(?:[^\n;|&]*\s)?--\s+\.|checkout\s+\.(?:\s|$)|restore\s+(?!--staged)[^\n;|&]*\.(?:\s|$)|stash\s+(?:drop|clear)|branch\s+-D|filter-branch|filter-repo|update-ref\s+-d|reflog\s+expire)"),
     "discards uncommitted work or rewrites/deletes git history"),
    ("gh-irreversible", "ask", re.compile(r"\bgh\s+(?:pr\s+merge|repo\s+(?:delete|archive|rename|edit\b[^\n;|&]*--visibility)|release\s+(?:create|delete|upload|edit)|secret\s+(?:set|delete)|variable\s+(?:set|delete)|workflow\s+run|api\b[^\n;|&]*(?:-X|--method)\s*(?:DELETE|PUT|PATCH|POST))\b"),
     "merges, publishes, deletes or changes GitHub state"),
    ("sql-destructive", "ask", SQL_DESTRUCTIVE, "destructive SQL (DROP/TRUNCATE)"),
    ("git-hook-bypass", "ask", re.compile(GIT_SUB + r"(?:commit|push|merge|rebase|am|cherry-pick|revert|pull)\b[^\n;|&]*\s--no-verify\b"
                                          r"|" + GIT_SUB + r"commit\b[^\n;|&]*\s-[a-zA-Z]*n[a-zA-Z]*(?=\s|$)"
                                          r"|\bgit\s+(?:[^\n;|&]*\s)?-c\s+core\.hooks[Pp]ath=\S*\s+(?:[^\n;|&]*\s)?(?:commit|push|merge|rebase|am|cherry-pick|revert|pull)\b"
                                          r"|\bHUSKY=0\s+(?:\w+=\S*\s+)*git\b"),
     "skips the repository's git hooks (pre-commit checks, secret scans); fix what the hook reports instead"),
    ("bench-destructive", "ask", re.compile(r"\bbench\b[^\n;|&]*\b(?:drop-site|reinstall|restore|remove-app|uninstall-app|new-site\b[^\n;|&]*--force|--force\b[^\n;|&]*new-site|trim-database|trim-tables|delete-site)\b"),
     "Frappe bench operation that drops or overwrites site data"),
    ("docker-destructive", "ask", re.compile(r"\bdocker(?:-compose)?\b[^\n;|&]*\b(?:system\s+prune|volume\s+(?:rm|prune)|image\s+prune\s+-a|down\b[^\n;|&]*(?:\s-v\b|--volumes))"),
     "deletes docker volumes/images (possible data loss)"),
    ("infra-change", "ask", re.compile(r"\b(?:terraform\s+(?:apply|destroy|import|state\s+rm)|pulumi\s+(?:up|destroy)|kubectl\s+(?:delete|apply|replace|drain|scale|patch|rollout\s+undo)|helm\s+(?:install|upgrade|uninstall|delete|rollback)|aws\s+[\w-]+\s+(?:delete-|terminate-|modify-|update-|put-|create-|authorize-|revoke-|attach-|detach-|run-instances|stop-|reboot-)[\w-]*|aws\s+s3\s+(?:rm|rb|mv)\b|aws\s+s3\s+sync\b[^\n;|&]*--delete|gcloud\b[^\n;|&]*\s(?:delete|deploy|create)\b|doctl\b[^\n;|&]*\sdelete\b|vercel\b[^\n;|&]*--prod|firebase\s+deploy|fly(?:ctl)?\s+deploy|serverless\s+(?:deploy|remove))"),
     "changes cloud infrastructure or deploys"),
    ("publish", "ask", re.compile(r"\b(?:npm|yarn|pnpm)\s+publish\b|\btwine\s+upload\b|\bpoetry\s+publish\b|\bgem\s+push\b|\bcargo\s+publish\b|\bdocker\s+push\b|\bflutter\s+pub\s+publish\b"),
     "publishes a package/image publicly"),
    ("sudo", "ask", re.compile(r"(?:^|[;&|(]\s*|\s)sudo\s"), "runs with root privileges"),
    ("perm-open", "ask", re.compile(r"\bchmod\s+(?:-R\s+)?(?:0?777|a\+rwx|o\+w)\b"), "makes files world-writable"),
    ("pipe-to-shell", "ask", re.compile(r"\b(?:curl|wget)\b[^\n;]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b|\b(?:curl|wget)\b[^\n;]*\|\s*python"),
     "executes code downloaded from the internet"),
    ("persistent-system", "ask", re.compile(r"\bcrontab\s+(?:-r|-\s|[^-\s]\S*\s*$)|\blaunchctl\s+(?:load|bootstrap|enable)\b|\bsystemctl\s+(?:enable|disable|mask)\b|>>?\s*~?[\w/.$]*\.ssh/authorized_keys"
                                            r"|(?:>>?|\btee\s+(?:-\w+\s+)*)\s*[\"']?" + STARTUP_FILE +
                                            r"|\b(?:sed\s+-i\S*|cp|mv|ln|install)\b[^\n;|&]*\s[\"']?" + STARTUP_FILE + r"[\"']?\s*(?:$|[;&|])"),
     "changes persistent system configuration or access"),
]

SSH_CMD = re.compile(r"(?:^|[;&|(]\s*|\s)ssh\s")
SSH_MUTATING = re.compile(
    r"(?:\b(?:rm|mv|dd|chmod|chown|kill|pkill|killall|reboot|shutdown|halt|truncate|tee|crontab|ufw|iptables|certbot|useradd|userdel|passwd)\b"
    r"|\bsystemctl\s+(?:stop|start|restart|reload|disable|enable|mask)|\bservice\s+\S+\s+(?:stop|start|restart|reload)"
    r"|\bsupervisorctl\s+(?:stop|start|restart|update|reread)|\bpm2\s+(?:restart|stop|delete|reload|start)|\bnginx\s+-s"
    r"|\bdocker(?:-compose)?\s+(?:rm|stop|restart|run|compose|up|down|exec|pull|kill)|\bgit\s+(?:pull|reset|checkout|switch|merge|push|clean|stash|rebase|fetch\b.*&&)"
    r"|\bbench\s+(?:--site\s+\S+\s+)?(?:migrate|restart|update|build|setup|drop-site|restore|reinstall|execute|console|set-config|install-app|uninstall-app|reset-perms)"
    r"|\bapt(?:-get)?\s+(?:install|remove|purge|upgrade|dist-upgrade)|\b(?:yum|dnf)\s+(?:install|remove|update)"
    r"|\bpip3?\s+install|\bnpm\s+(?:install|ci|run|start)|\bcomposer\s+(?:install|update|require)|\bphp\s+\S*(?:migrat|artisan|spark)"
    r"|\b(?:ba)?sh\s+-[sc]\b|\bsed\s+-i|\bmysql\b|\bmariadb\b|\bpsql\b|\bmongo(?:sh)?\b|\bredis-cli\b[^\n]*\b(?:flush|del|set)\b|(?<![0-9&])>(?!&)|<<)",
    re.I,
)
SSH_SECRET = re.compile(r"site_config\.json|common_site_config\.json|\.env\b|env_keys\.php|config/database\.php|wp-config\.php|credentials", re.I)
REMOTE_COPY = re.compile(r"(?:^|[;&|(]\s*|\s)(?:scp|rsync)\s(?=[^\n;|&]*\s[\w.@-]+:)")
RSYNC_DELETE = re.compile(r"\brsync\b[^\n;|&]*--delete")
DB_CLIENT = re.compile(r"\b(?:mysql|mariadb|psql|mongo(?:sh)?)\b[^\n;|&]*?\s(?:-h\s*|--host[= ])([\w.-]+)")
SQL_WRITE = re.compile(r"(?i)\b(?:insert\s+into|update\s+[`\"\w.]+\s+set|delete\s+from|alter\s+table|create\s+(?:table|index|user|database)|grant\s|revoke\s|replace\s+into)\b")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
SQL_UNSCOPED = re.compile(r"(?is)\b(?:delete\s+from\s+[`\"\w.]+|update\s+[`\"\w.]+\s+set\b)")
COAUTHOR = re.compile(r"(?i)co-authored-by:\s*claude")

MCP_ASK = [
    (re.compile(r"__(?:send_message|send_email|forward|reply|post_message|send_now)$"), "sends a message/email on the user's behalf"),
    (re.compile(r"__(?:create_event|update_event|delete_event|respond_to_event)$"), "changes a calendar or sends invitations"),
    (re.compile(r"__(?:share_file|update_file_permissions)$"), "shares files with other people"),
    (re.compile(r"apollo_(?:emailer_messages_send_now|emailer_campaigns_approve|emailer_campaigns_add_contact_ids|email_account_purchase_create|domain_purchase\w*)$"), "sends outreach or buys something in Apollo"),
    (re.compile(r"__(?:delete|delete_[a-z_]+|trash_file)$"), "deletes data in an external service"),
    (re.compile(r"__browser_(?:run_code_unsafe|file_upload|drop)$|__upload_file$"), "runs code on this machine or sends a local file into a page"),
]
# MCP servers for code, repositories, cloud infrastructure and data: their write tools ask (docs/MCP-POLICY.md keeps
# them read-only). Matched on the server name the user chose in `claude mcp add`, and on the tool's leading verb.
CODE_INFRA_SERVER = re.compile(
    r"(?:^|[-_.])(?:github|gh|gitlab|bitbucket|git|aws|awslabs|iam|ecs|eks|lambda|serverless|cloudformation|cdk|ccapi|"
    r"terraform|pulumi|kubernetes|k8s|docker|vercel|netlify|cloudflare|supabase|firebase|serena|filesystem|fs|"
    r"postgres|mysql|mariadb|mongo|redis|sqlite|db|database|sql)(?:$|[-_.])", re.I)
MCP_WRITE_ACTION = re.compile(
    # a write verb leading the name ...
    r"^(?:create|update|delete|safe_delete|remove|push|merge|add|fork|star|unstar|assign|request|dismiss|mark|manage|"
    r"submit|resolve|unresolve|reprioritize|set|execute|exec|run|rerun|cancel|replace|insert|rename|edit|move|copy|"
    r"write|attach|detach|put|apply|deploy|upload|invoke|start|stop|reboot|terminate|grant|revoke|enable|disable|"
    r"restore|drop|truncate|hide|unhide|build_and_push|call_aws|git_(?:add|commit|reset|checkout|create_branch|merge|push))(?:_|$)"
    # ... an unambiguous one anywhere (`firestore_add_document`, `kubectl_apply`) ...
    r"|(?:^|_)(?:create|update|delete|remove|push|merge|insert|apply|deploy|put|add|write|upload|rerun|cancel|"
    r"terminate|drop|truncate|grant|revoke|attach|detach|fork|replace|rename)(?:_|$)"
    r"|_(?:write|trigger|api_operation)$", re.I)
MCP_WRITE_CAMEL = re.compile(  # camelCase tool names (`insertOne`, `updateMany`, `requestReview`); case-sensitive on purpose
    r"^(?:create|update|delete|insert|put|add|remove|push|merge|request|apply|deploy|write|upload|drop|replace|rename|"
    r"rerun|cancel)[A-Z]")
# Adding MCP servers or plugins changes what every later session can do.
MCP_CONFIG_CMD = re.compile(r"\bclaude(?:\s+--?[\w-]+(?:=\S+)?)*\s+(?:mcp\s+(?:add|add-json|add-from-claude-desktop)|plugins?\s+(?:install|marketplace\s+add|enable|update))\b")
MCP_CONFIG_FILE = re.compile(r"(?:^|/)\.mcp\.json$|/\.claude\.json$")
MCP_CONFIG_IN_CMD = re.compile(r"(?:^|[\s/'\"=])\.(?:mcp|claude)\.json(?=$|[\s'\";|&)])")
UNPINNED_PKG = re.compile(r"\b(?:npx|uvx|bunx|pnpm\s+dlx)\s+(?:--?[\w-]+\s+)*(?:@[\w.-]+/)?[\w.-]+(?:@(?:latest|next|[\^~*<>][^\s'\"]*))?(?=$|\s|['\"])")
MCP_DANGER_FLAG = re.compile(
    r"--(?:autoConnect|auto-connect|browserUrl|browser-url|wsEndpoint|ws-endpoint|cdp-endpoint|extension|"
    r"allow-unrestricted-file-access|allow-writes?|allow_write_query|no-confirmation|allow-sensitive-data-access|"
    r"allowUnrestrictedPaths|allow-unrestricted-paths|categoryNetworkMocks|category-network-mocks|categoryExtensions|"
    r"category-extensions|experimentalDevtools|experimental-devtools|insiders)(?![\w-])|--caps[= ]\S*storage"
    r"|\b(?:[A-Z]+_)*ALLOW_WRITES?=[\"']?true|\bREAD_OPERATIONS_ONLY=false|\bALLOW_SENSITIVE_DATA(?:_ACCESS)?=true"
    r"|\bX-MCP-(?:Insiders|Features)\b|/mcp/insiders\b", re.I)
MCP_SKIP = re.compile(r"^mcp__(?:ccd_|Claude_Browser__|claude-in-chrome__|computer-use__|visualize__|terminal__|scheduled-tasks__list|mcp-registry__)")


# ---------------------------------------------------------------- helpers
def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(os.path.join(ENGOS, "config.json")) as fh:
            cfg.update(json.load(fh))
    except (OSError, ValueError):
        pass
    # Personal, unmanaged overrides (install never writes local.json). Only "trusted_projects" is read:
    # [{"path": "~/code/site", "rules": ["git-protected-push", ...]}] turns those ask rules off for
    # commands that run in, or cd into, that path. deny rules can never be disabled this way.
    try:
        with open(os.path.join(ENGOS, "local.json")) as fh:
            tp = json.load(fh).get("trusted_projects") or []
        cfg["trusted_projects"] = [t for t in tp if isinstance(t, dict) and t.get("path") and t.get("rules")]
    except (OSError, ValueError, AttributeError):
        pass
    return cfg


# The only rules a trusted project may switch off: local-repo and local-DB housekeeping.
# Secrets, remote servers, infra/deploys, publishing, sudo and every deny rule stay on everywhere.
TRUSTABLE = {"git-protected-push", "git-discard", "sql-destructive", "docker-destructive"}


def trusted_off(cmd, cwd, project, cfg):
    """Ask-rule ids switched off because the command runs inside a trusted project."""
    dirs = [cwd, project] + [norm(d, cwd) for d in re.findall(r"(?:^|[;&|]\s*)cd\s+([^\s;&|]+)", cmd)]
    dirs += [norm(d, cwd) for d in re.findall(r"\bgit\s+-C\s+([^\s;&|]+)", cmd)]
    off = set()
    for t in cfg.get("trusted_projects") or []:
        root = os.path.normpath(os.path.expanduser(t["path"]))
        if any(d and under(d, root) for d in dirs):
            off.update(r for r in t["rules"] if r in TRUSTABLE)
    return off


def emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": "%s %s" % (MARK, reason)}}))


def norm(path, cwd):
    if not path:
        return ""
    path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    return os.path.normpath(path)


def under(path, root):
    return bool(root) and (path == root or path.startswith(root.rstrip("/") + "/"))


SHELL_STRING = re.compile(r"""(?:^|[\s;&|(])(?:\S*/)?(?:bash|sh|zsh|dash)\s+(?:-[a-zA-Z]+\s+)*?-[a-zA-Z]*c[a-zA-Z]*\s+("(?:[^"\\]|\\.)*"|'[^']*')"""
                          r"""|(?:^|[\s;&|(])eval\s+("(?:[^"\\]|\\.)*"|'[^']*')""")


def segments(cmd, depth=0):
    """Split a shell command into simple-command argv lists (best effort)."""
    out = []
    for part in re.split(r"&&|\|\||;|\||\n", cmd):
        try:
            argv = shlex.split(part, comments=True)
        except ValueError:
            argv = part.split()
        while argv and (argv[0] in ("sudo", "command", "builtin", "nohup", "time", "exec") or re.match(r"^\w+=", argv[0])):
            argv = argv[1:]
        if argv:
            out.append(argv)
            if depth < 3 and argv[0] == "eval" and len(argv) > 1:  # unquoted `eval rm -rf x`
                out.extend(segments(" ".join(argv[1:]), depth + 1))
    # a command handed to a shell as a quoted string (`bash -c "cd x && rm -rf y"`, `env A=1 sh -ec '...'`,
    # `eval "..."`) is checked as commands too; read from the raw text, before the split above cuts the string apart
    for m in SHELL_STRING.finditer(cmd) if depth < 3 else ():
        quoted = m.group(1) or m.group(2)
        try:
            inner = shlex.split(quoted)[0]
        except (ValueError, IndexError):
            inner = quoted[1:-1]
        out.extend(segments(inner, depth + 1))
    return out


def in_scratch(p):
    """Under a temp folder. Never the home folder, anything in it or anything above it, even on a machine whose home
    sits inside a temp folder; a temp folder that itself lives inside home (TMPDIR=~/.cache/tmp) still counts."""
    if under(HOME, p):  # p is the home folder or one of its parents
        return False
    return any(under(p, t) and (not under(p, HOME) or under(t, HOME)) for t in scratch_roots())


def scratch_roots():
    roots = ["/tmp", "/private/tmp", "/var/folders", "/private/var/folders"]
    tmp = os.environ.get("TMPDIR")
    if tmp:
        roots.append(os.path.normpath(tmp))
    return roots


# ---------------------------------------------------------------- checks
def check_rm(cmd, cwd, project):
    for argv in segments(cmd):
        if os.path.basename(argv[0]) != "rm":
            continue
        flags = "".join(a.lstrip("-") for a in argv[1:] if a.startswith("-") and a != "--")
        if not re.search(r"[rRf]|recursive|force", flags):
            continue
        for t in (a for a in argv[1:] if not a.startswith("-")):
            p = norm(t, cwd)
            if ".git" in p.split("/"):
                return "deletes git metadata (%s)" % t
            if t in (".", "./", "*", "./*", "..", "../") or p in (project, cwd):
                return "deletes the whole project directory contents (%s)" % t
            if "$" in p:
                return "target contains an unexpanded variable (%s)" % t
            if os.path.isdir(os.path.join(p, ".git")):
                return "deletes an entire git repository (%s)" % t
            if not (under(p, project) or under(p, cwd) or in_scratch(p)):
                return "recursive/forced delete outside the project and temp dirs (%s)" % t
    return None


def current_branch(cmd, cwd):
    m = re.match(r"\s*cd\s+([^\s;&|]+)\s*&&", cmd)
    d = norm(m.group(1), cwd) if m else cwd
    try:
        r = subprocess.run(["git", "-C", d, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()
    except Exception:
        return ""


def protected(branch, cfg):
    b = branch.split(":")[-1].replace("refs/heads/", "")
    return any(b == p or b.startswith(p + "/") or b.startswith(p + "-") for p in cfg["protected_branches"])


def check_push(cmd, cwd, cfg):
    for argv in segments(cmd):
        if len(argv) < 2 or os.path.basename(argv[0]) != "git":
            continue
        args = [a for a in argv[1:] if not a.startswith("-")]
        # drop global options like -C <dir> (best effort)
        if "push" not in args:
            continue
        rest = args[args.index("push") + 1:]
        refs = rest[1:] if rest else []
        targets = refs or [current_branch(cmd, cwd)]
        for r in targets:
            if r and protected(r.lstrip("+"), cfg):
                return "pushes directly to protected branch '%s'" % r
    return None


def secret_reads(cmd):
    """(credential file, secret file) printed/copied/sent by a command naming it in its own argv."""
    creds = secret = False
    for argv in segments(cmd):
        if os.path.basename(argv[0]) in READ_CMDS:
            args = " " + " ".join(argv[1:])
            creds = creds or CLAUDE_CREDS in args
            secret = secret or bool(SECRET_PATH.search(ENV_FILE_FLAG.sub(" ", args)))
    return creds, secret


def env_dump(cmd):
    """Commands that print environment variables, which often hold secrets."""
    for argv in segments(cmd):
        base, args = os.path.basename(argv[0]), argv[1:]
        if base == "printenv":
            if not args or any(secret_var(a) for a in args if not a.startswith("-")):
                return "printenv"
        elif base == "env":
            rest = list(args)
            while rest and rest[0].startswith("-"):  # options only, no command: env prints the environment
                rest = rest[2:] if rest[0] in ("-u", "--unset") else rest[1:]
            if not rest and not any(a in ("-i", "--ignore-environment") or a == "-" for a in args):
                return "env"
        elif base in ("export", "declare", "typeset") and set("".join(args)) <= set("-px"):
            return " ".join(argv)
        elif base == "set" and not args:
            return "set"
        elif base in ("echo", "printf", "print"):
            for a in args:
                for name in VAR_REF.findall(a):
                    if secret_var(name):
                        return "%s $%s" % (base, name)
    return None


def secret_var(name):
    """A variable name that marks a secret value: $API_KEY, $DB_PASSWORD; not $SSH_KEY_PATH or $PASSWORD_MIN_LENGTH."""
    n = name.upper()
    return bool(SECRET_VAR.search(n)) and not SAFE_VAR_SUFFIX.search(n)


def local_host(host):
    """Loopback, *.localhost/*.test/*.local and single-label names (docker-compose services such as `minio`).
    Private IPs and *.internal still count as remote: from a server they can be production."""
    h = host.lower().strip("[]")
    return (h in LOCAL_HOSTS or h.endswith((".localhost", ".test", ".local")) or h == ""
            or (re.match(r"^[a-z0-9-]+$", h) is not None and not h.isdigit()))


def http_mutating(cmd):
    """curl / wget / httpie sending DELETE, PUT or PATCH to a host that is not local (or to a host it cannot tell)."""
    for argv in segments(cmd):
        base, args = os.path.basename(argv[0]), argv[1:]
        method = None
        if base == "curl":
            for i, a in enumerate(args):
                m = re.match(r"^-[A-Za-z]*X(.*)$", a)  # -X DELETE, -XDELETE, and bundled short flags (-sXPUT, -sX PUT)
                if a == "--request" and i + 1 < len(args):
                    method = args[i + 1]
                elif a.startswith("--request="):
                    method = a.split("=", 1)[1]
                elif m and not a.startswith("--"):
                    method = m.group(1) or (args[i + 1] if i + 1 < len(args) else None)
        elif base == "wget":
            for i, a in enumerate(args):
                if a == "--method" and i + 1 < len(args):
                    method = args[i + 1]
                elif a.startswith("--method="):
                    method = a.split("=", 1)[1]
        elif base in ("http", "https", "xh"):
            # the method is the first bare HTTP verb; options such as --auth u:p take values that come before it
            verbs = [a for a in args if a.upper() in HTTP_VERBS]
            method = verbs[0] if verbs else None
        if not method or method.upper() not in HTTP_MUTATING:
            continue
        hosts = re.findall(r"(?i)\bhttps?://(\[[^\]]+\]|[^/\s:'\"?#]+)", " ".join(args))
        if not hosts:  # curl and httpie also take bare hosts (example.com/api, localhost:8000, :8000 for httpie)
            hosts = [m.group(1) for a in args if not a.startswith("-")
                     for m in [re.match(r"^(\[[^\]]+\]|[\w.-]*)(?::\d+)?(?:/|$)", a)]
                     if m and (a.startswith(":") or "." in m.group(1) or m.group(1).lower() == "localhost")]
        remote = [h for h in hosts if not local_host(h)]
        if remote or not hosts:
            return "%s %s to %s" % (base, method.upper(), remote[0] if remote else "a host it could not determine")
    return None


def check_find(cmd, cwd, project):
    """find ... -delete / -exec rm: same location limits as rm, and it must be filtered."""
    for argv in segments(cmd):
        if os.path.basename(argv[0]) != "find":
            continue
        args = argv[1:]
        deleting = "-delete" in args or any(
            a in ("-exec", "-execdir", "-ok", "-okdir") and i + 1 < len(args) and os.path.basename(args[i + 1]) in ("rm", "unlink", "shred")
            for i, a in enumerate(args))
        if not deleting:
            continue
        while args and args[0] in ("-H", "-L", "-P"):
            args = args[1:]
        roots = []
        for a in args:
            if a.startswith("-") or a in ("(", "!", ")"):
                break
            roots.append(a)
        for r in roots or ["."]:
            p = norm(r, cwd)
            if "$" in p:
                return "the search root contains an unexpanded variable (%s)" % r
            scratch = in_scratch(p)
            if not scratch and (p in ("/", HOME, os.path.dirname(HOME)) or any(under(p, s) for s in SYSTEM_DIRS)):
                return "deletes files under the filesystem root, a system directory or the home directory (%s)" % r
            if not (under(p, project) or under(p, cwd) or scratch):
                return "deletes files outside the project and temp dirs (%s)" % r
        if not any(a in FIND_FILTERS for a in args):
            return "deletes everything under %s: no -name, -path or age filter" % (", ".join(roots) or ".")
        for i, a in enumerate(args):
            if a in ("-name", "-iname", "-path", "-ipath") and i + 1 < len(args) and ".git" in args[i + 1] and "-prune" not in args:
                return "deletes git metadata (%s %s)" % (a, args[i + 1])
    return None


def unscoped_sql(text):
    """UPDATE/DELETE statements without a WHERE clause; comments are ignored, so `/* where */` does not count."""
    text = re.sub(r"/\*.*?\*/|--\s[^\n]*", " ", text, flags=re.S)  # "-- " comments; never CLI flags like --host
    return any(SQL_UNSCOPED.search(st) and not re.search(r"(?i)\bwhere\b", st) for st in text.split(";"))


def strings_in(value):
    """All string values inside a tool input, with real newlines kept (json.dumps would turn them into a literal \\n)."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in strings_in(v)]
    if isinstance(value, list):
        return [s for v in value for s in strings_in(v)]
    return []


def mcp_config_reason(cmd):
    why = ["mcp-config: adds an MCP server or plugin that every later session can use; only approved ones, at the pinned "
           "version with the listed flags (docs/MCP-POLICY.md in the eng-os repo)"]
    if UNPINNED_PKG.search(cmd):
        why.append("the package is not pinned to an exact version")
    if MCP_DANGER_FLAG.search(cmd):
        why.append("it enables writes, sensitive-data access, unrestricted file paths or experimental tools, or attaches to "
                   "a real browser profile, which the policy does not approve")
    return "; ".join(why)


def check_bash(cmd, cwd, project, cfg):
    off = set(cfg.get("disabled_rules") or []) | trusted_off(cmd, cwd, project, cfg)
    creds, secret = secret_reads(cmd)
    if creds:
        return "deny", "credential-dump: reads Claude's own OAuth credentials"
    # hard blocks first, so an approval for another part of the command can never let them through
    if cfg.get("block_claude_coauthor") and re.search(r"\bgit\b[^\n]*\bcommit\b", cmd) and COAUTHOR.search(cmd):
        return "deny", "coauthor: the user's rule is commits under their name only; remove the 'Co-Authored-By: Claude' trailer and retry"
    for rid, decision, rx, reason in BASH_RULES:
        if rid not in off and rx.search(cmd):
            return decision, "%s: %s" % (rid, reason)
    if "mcp-config" not in off and MCP_CONFIG_CMD.search(cmd):
        return "ask", mcp_config_reason(cmd)
    if "mcp-config" not in off and MCP_CONFIG_IN_CMD.search(cmd) and SHELL_WRITE.search(cmd):
        return "ask", "mcp-config: changes a file that lists the MCP servers Claude may use (.mcp.json or ~/.claude.json); only approved, pinned servers (docs/MCP-POLICY.md in the eng-os repo)"
    if "rm-outside" not in off:
        why = check_rm(cmd, cwd, project)
        if why:
            return "ask", "rm-outside: " + why
    if "find-delete" not in off:
        why = check_find(cmd, cwd, project)
        if why:
            return "ask", "find-delete: " + why
    if "http-mutating" not in off:
        why = http_mutating(cmd)
        if why:
            return "ask", "http-mutating: %s changes or deletes data in a remote service" % why
    if "git-protected-push" not in off and re.search(r"\bgit\b[^\n;|&]*\bpush\b", cmd):
        why = check_push(cmd, cwd, cfg)
        if why:
            return "ask", "git-protected-push: " + why
    if SSH_CMD.search(cmd):
        if SSH_SECRET.search(cmd) and READ_VERBS.search(cmd):
            return "ask", "ssh-secret: reads a remote secrets/config file (credentials would enter the transcript)"
        remote = SSH_CMD.split(cmd, 1)[1]
        if SSH_MUTATING.search(remote):
            return "ask", "ssh-mutating: changes state on a remote server"
    if REMOTE_COPY.search(cmd):
        m = re.search(r"\s([\w.@-]+):\S*\s*$", cmd.split("&&")[0].strip())
        if m:  # destination is remote => upload/deploy
            return "ask", "remote-copy: uploads files to a remote host"
    if RSYNC_DELETE.search(cmd):
        return "ask", "rsync-delete: rsync --delete removes files at the destination"
    m = DB_CLIENT.search(cmd)
    if m and m.group(1).lower() not in LOCAL_HOSTS and SQL_WRITE.search(cmd):
        return "ask", "remote-db-write: writes to a non-local database (%s)" % m.group(1)
    if re.search(r"\b(?:mysql|mariadb|psql|sqlite3|bench|frappe\.db|execute)\b", cmd) and unscoped_sql(cmd):
        return "ask", "sql-unscoped: UPDATE/DELETE without WHERE"
    if secret and "secret-read" not in off:
        return "ask", "secret-read: prints/copies/sends a secrets file (its values would enter the transcript)"
    if "env-dump" not in off:
        why = env_dump(re.sub(r"'[^']*'", "''", cmd))  # single-quoted text is literal, never an expansion
        if why:
            return "ask", ("env-dump: `%s` prints environment variables, which often hold secrets (they would enter the "
                           "transcript); to check one is set, use `[ -n \"$NAME\" ] && echo set`" % why)
    if GLOBAL_CONFIG_FILES.search(cmd) and SHELL_WRITE.search(cmd) and "eng-os install" not in cmd and "eng-os restore" not in cmd:
        return "ask", "global-config: edits live global Claude config; change the eng-os repo (`eng-os status` shows where) and run `eng-os install` instead"
    return None


def scan_secrets(text, path):
    if not text:
        return None
    if ENV_FILE.search(path) and not ENV_TEMPLATE.search(path):
        return None  # real .env files are where secrets belong (keep them gitignored)
    for name, rx in SECRET_CONTENT:
        for m in rx.finditer(text):
            val = m.group(1) if m.groups() else m.group(0)
            if name == "assigned-secret" and (PLACEHOLDER.search(val) or TEST_PATH.search(path)):
                continue
            return name
    return None


def check_file_tool(tool, inp, cwd):
    path = norm(inp.get("file_path") or inp.get("notebook_path") or inp.get("path") or "", cwd)
    if tool in ("Read", "Grep", "Glob"):
        if NEVER_READ.search(path):
            return "deny", "credential-file: Claude's own OAuth credentials are never needed"
        # Grep prints matching lines only in "content" mode; its default lists file names
        shows = tool == "Read" or (tool == "Grep" and inp.get("output_mode") == "content")
        if shows and SECRET_PATH.search(" " + path):
            return "ask", "secret-read: reading %s puts secret values into the transcript; prefer listing key names only" % os.path.basename(path)
        if shows and tool == "Grep" and secret_glob(inp.get("glob") or ""):
            return "ask", "secret-read: the glob %s selects secrets files, so matching lines would enter the transcript" % inp.get("glob")
        return None
    # write tools
    if MCP_CONFIG_FILE.search(path):
        return "ask", "mcp-config: %s lists the MCP servers Claude may use; only approved, pinned ones (docs/MCP-POLICY.md in the eng-os repo)" % os.path.basename(path)
    if GLOBAL_CONFIG_FILES.search(path):
        return "ask", "global-config: %s is managed by eng-os; edit the eng-os repo and run `eng-os install`" % path.replace(HOME, "~")
    if re.search(r"/\.ssh/(?:authorized_keys|config)$", path):
        return "ask", "ssh-config: changes SSH access configuration"
    if under(path, HOME) and re.search(r"^/(?:\.(?:zshrc|zshenv|zprofile|zlogin|bashrc|bash_profile|bash_login|profile)|\.config/fish/config\.fish|Library/LaunchAgents/.+)$", path[len(HOME):]):
        return "ask", "shell-startup: %s runs at every login or shell start, a common place to plant persistence" % path.replace(HOME, "~")
    if tool == "Write":
        text = inp.get("content", "")
    elif tool == "Edit":
        text = inp.get("new_string", "")
    elif tool == "MultiEdit":
        text = "\n".join(e.get("new_string", "") for e in inp.get("edits") or [])
    else:
        text = inp.get("new_source", "")
    hit = scan_secrets(text, path)
    if hit:
        return "ask", "secret-write: content looks like a real credential (%s); use an env var / secret manager instead" % hit
    return None


def secret_glob(glob):
    """A Grep glob that picks out secrets files: it matches a typical secret name and no ordinary source file."""
    if not glob:
        return False
    alts = [glob]
    m = re.match(r"^(.*)\{([^{}]*)\}(.*)$", glob)
    if m:
        alts = [m.group(1) + a + m.group(3) for a in m.group(2).split(",")]
    for g in alts:
        g = g.split("/")[-1]
        if any(fnmatch.fnmatchcase(n, g) for n in SECRET_NAMES) and not any(fnmatch.fnmatchcase(n, g) for n in ORDINARY_NAMES):
            return True
    return False


def check_mcp(tool, inp):
    if MCP_SKIP.search(tool):
        return None
    parts = tool.split("__")
    server, action = (parts[1] if len(parts) > 2 else ""), parts[-1]
    if DB_TOOL.search(server) or DB_TOOL.search(action):
        sql = "\n".join(strings_in(inp))
        if SQL_DESTRUCTIVE.search(re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)):
            return "ask", "mcp-sql-destructive: destructive SQL (DROP/TRUNCATE) through %s" % action
        if unscoped_sql(sql):
            return "ask", "mcp-sql-destructive: UPDATE/DELETE without WHERE through %s" % action
        if SQL_WRITE.search(sql):
            return "ask", "mcp-write: writes or changes data (INSERT/UPDATE/DELETE/ALTER/GRANT) through %s; approved servers stay read-only" % action
    if re.search(r"(^|[-_])ads?($|[-_])|adwords|advertis", server, re.I) and re.search(r"create|update|mutate|status|enable", action, re.I):
        blob = json.dumps(inp).lower()
        updating = re.search(r"update|mutate|status", action, re.I)
        if '"active"' in blob or '"enabled"' in blob or (updating and re.search(r"budget|bid_amount|bid_strategy|bidding", blob)):
            return "ask", "ads-spend: activates delivery or changes spend on a live ad account"
        return None
    for rx, why in MCP_ASK:
        if rx.search(tool):
            return "ask", "mcp-outward: %s (%s)" % (why, tool.split("__")[-1])
    # SQL and query tools are judged by their statement above, so a plain SELECT stays allowed.
    if CODE_INFRA_SERVER.search(server) and (MCP_WRITE_ACTION.search(action) or MCP_WRITE_CAMEL.search(action)) and not re.search(r"(?:^|_)(?:sql|query)(?:_|$)", action, re.I):
        return "ask", ("mcp-write: %s changes code, a repository, cloud resources or data through the %s MCP server; "
                       "approved servers stay read-only (docs/MCP-POLICY.md)" % (action, server))
    return None


# ---------------------------------------------------------------- main
def main():
    raw = sys.stdin.read()
    data = json.loads(raw or "{}")
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    cfg = load_config()

    verdict = None
    if tool == "Bash":
        verdict = check_bash(inp.get("command", ""), cwd, os.path.normpath(root), cfg)
    elif tool in ("Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "NotebookEdit"):
        verdict = check_file_tool(tool, inp, cwd)
    elif tool.startswith("mcp__"):
        verdict = check_mcp(tool, inp)

    if verdict and verdict[0] == "deny":
        emit("deny", verdict[1] + ". If it is truly intended, the user can run it themselves.")
        return 0
    if verdict:
        emit("ask", verdict[1])
        return 0
    # subagents share the session id but not the conversation, so their reads are neither noted nor recorded
    if tool == "Read" and os.environ.get("ENG_OS_REREAD_NOTE") != "0" and not data.get("agent_id"):
        try:
            note = reread_note(inp, cwd, data.get("session_id"))
        except Exception as e:  # a note is optional; never block a read over it
            log_error("reread", e)
            note = ""
        if note:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": note}}))
    elif tool in ("Write", "Edit", "MultiEdit") and os.environ.get("ENG_OS_CODE_NOTE") != "0":
        try:
            note = code_note(tool, inp, cwd, data.get("session_id"))
        except Exception as e:  # a note is optional; never block a write over it
            log_error("code-note", e)
            note = ""
        if note:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": note}}))
    return 0


# Risky code being written. A match only adds a one-line note (the write goes ahead); each pattern is noted once per
# file per session. The note names the safe form; the rule behind it is in skill eng-security.
PY, PHP, JS = (".py",), (".php",), (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue")
RISKY_CODE = [
    ("shell string", PY + PHP + JS, re.compile(r"shell\s*=\s*True|\bshell\s*:\s*true|\bos\.(?:system|popen)\(|"
     r"\b(?:shell_exec|passthru|proc_open)\(|\bexecSync\(|\bchild_process\b[^\n]*\bexec\b(?!File)"),
     "pass an argument list; never put input into a shell string"),
    ("eval of code", PY + PHP + JS, re.compile(r"(?<![\w.>$])(?:eval|exec)\(\s*(?![\"'])|\bnew\s+Function\("),
     "never run strings built from input"),
    ("unsafe deserialisation", PY + PHP, re.compile(r"\bpickle\.loads?\(|\bmarshal\.loads\(|\byaml\.load\((?![^)]*SafeLoader)|"
     r"(?<![\w>])unserialize\("), "use JSON or yaml.safe_load; unserialize/pickle on input can run code"),
    ("TLS verification off", PY + PHP + JS + (".dart",), re.compile(r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|"
     r"NODE_TLS_REJECT_UNAUTHORIZED|CURLOPT_SSL_VERIFY(?:PEER|HOST)\s*,\s*(?:0|false)|badCertificateCallback"),
     "keep certificate checks on; fix the trust store instead"),
    ("SQL built from strings", PY + PHP + JS, re.compile(r"\b(?:execute|executemany|sql|query|raw)\(\s*f[\"']|"
     r"\b(?:execute|sql|query|raw)\(\s*`[^`]*\$\{|"
     r"\b(?:execute|sql|query)\(\s*[\"'][^\"']*\b(?:select|update|delete|insert)\b[^\"']*[\"']\s*(?:%|\.format\(|\+)|"
     r"->query\(\s*\"[^\"]*\$\w|->query\([^;]*\.\s*\$_(?:GET|POST|REQUEST|COOKIE)", re.I),
     "use bound parameters (%s placeholders, query bindings, the ORM)"),
    ("HTML from strings", JS + PHP, re.compile(r"dangerouslySetInnerHTML|\.(?:inner|outer)HTML\s*=|\bdocument\.write\(|\bv-html="),
     "render text, or sanitise the HTML with a vetted library"),
    ("permission bypass", PY, re.compile(r"\ballow_guest\s*=\s*True|ignore_permissions\s*=\s*True|\.sudo\(\)"),
     "check the caller's rights first and say in a comment why the bypass is safe"),
    ("untrusted text in a workflow", (".yml", ".yaml"), re.compile(r"\$\{\{\s*github\.(?:event\.(?:issue|pull_request|comment|review|"
     r"review_comment|head_commit|commits|discussion|pages)\b|head_ref\b)"), "pass it through env: and quote it; never inline it in run:"),
]


def code_note(tool, inp, cwd, session):
    """One line when the text being written matches a risky-code pattern for its file type. Never blocks."""
    path = norm(inp.get("file_path") or "", cwd)
    ext = os.path.splitext(path)[1].lower()
    if tool == "Write":
        text = inp.get("content", "")
    elif tool == "Edit":
        text = inp.get("new_string", "")
    else:
        text = "\n".join(e.get("new_string", "") for e in inp.get("edits") or [] if isinstance(e, dict))
    if ext in (".yml", ".yaml") and "/.github/workflows/" not in path:
        return ""
    hits = [(name, fix) for name, exts, rx, fix in RISKY_CODE if ext in exts and rx.search(text or "")]
    if not hits:
        return ""
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session or "nosession"))[:80]
    f = os.path.join(STATE, "code-notes-%s.json" % sid)
    try:
        with open(f) as fh:
            seen = json.load(fh)
        if not isinstance(seen, dict):
            seen = {}
    except (OSError, ValueError):
        seen = {}
    done = set(seen.get(path) or [])
    hits = [(n, fix) for n, fix in hits if n not in done]
    if not hits:
        return ""
    seen[path] = sorted(done | {n for n, _ in hits})
    os.makedirs(STATE, mode=0o700, exist_ok=True)
    tmp = f + ".%d" % os.getpid()
    with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as fh:  # it lists file paths
        json.dump(seen, fh)
    os.replace(tmp, f)  # two parallel writes can lose one record: the worst case is a note shown twice
    return "eng-os code note for %s: %s. If this is deliberate and the input is trusted, carry on." % (
        os.path.basename(path), "; ".join("%s (%s)" % h for h in hits))


def reread_note(inp, cwd, session):
    """A one-line note when a file is read in full again with nothing changed since its last full read this session.
    It never blocks: a denied read would cost one more model round trip at full context size, which is more than the
    re-read itself. The record is cleared after compaction or /clear (session_start.py), when re-reading is needed."""
    path = norm(inp.get("file_path") or "", cwd)
    if not path or not os.path.isfile(path):
        return ""
    st = os.stat(path)
    key = [st.st_mtime_ns, st.st_size]
    full = not (inp.get("offset") or inp.get("limit") or inp.get("pages"))
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session or "nosession"))[:80]
    f = os.path.join(STATE, "reads-%s.json" % sid)
    try:
        with open(f) as fh:
            seen = json.load(fh)
        if not isinstance(seen, dict):
            seen = {}
    except (OSError, ValueError):
        seen = {}
    prev = seen.get(path)
    same = isinstance(prev, list) and len(prev) == 3 and prev[:2] == key
    note = ""
    if full and same and prev[2]:
        note = ("eng-os: %s was read in full earlier in this session and has not changed since. If that copy is still "
                "in context, use it; read only a range (offset/limit) if you need part of it again." % os.path.basename(path))
    seen[path] = key + [bool(full or (same and prev[2]))]
    if len(seen) > 400:  # keep the record small
        seen = dict(list(seen.items())[-300:])
    os.makedirs(STATE, exist_ok=True)
    tmp = "%s.%d.tmp" % (f, os.getpid())  # parallel reads: write whole, then swap in
    with open(tmp, "w") as fh:
        json.dump(seen, fh)
    os.replace(tmp, f)
    return note


def log_error(where, err):
    try:
        os.makedirs(STATE, exist_ok=True)
        with open(os.path.join(STATE, "guard-errors.log"), "a") as fh:
            fh.write("%s %s %r\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), where, err))
    except OSError:
        pass


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail-open: never break the session because of a guard bug
        log_error("main", e)
        sys.exit(0)
