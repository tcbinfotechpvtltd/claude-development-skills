#!/usr/bin/env python3
"""eng-os guard: deterministic PreToolUse safety layer for Claude Code.

Runs on Bash, file tools and MCP tools. For each call it may:
  deny  - catastrophic or never-legitimate actions (the user can still run them by hand)
  ask   - destructive, irreversible, outward-facing, production or secret-exposing actions
  add context - project CLAUDE.md for subprojects touched via Bash (which the harness
          does not load on its own when files are read with cat/sed/grep)
Anything else passes through with no output (zero context cost).

Fail-open by design: an internal error never blocks work; it is logged to
~/.claude/eng-os/state/guard-errors.log and surfaced by `eng-os verify`.
Python 3.9 compatible, stdlib only. Unit tests: tests/guard_cases.json.
"""
import hashlib
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
    "project_context_max_chars": 6000,
    "disabled_rules": [],
}

# ---------------------------------------------------------------- patterns
SECRET_PATH = re.compile(
    r"""(?:^|[\s/'"=:(])(?:"""
    r"""\.env(?!\.(?:example|sample|template|dist|defaults)\b)(?:\.[\w.-]+)?"""
    r"""|id_(?:rsa|ed25519|ecdsa|dsa)(?!\.pub)"""
    r"""|[\w.-]+\.(?:pem|p12|pfx|keystore|jks|ppk)"""
    r"""|\.aws/credentials|\.netrc|\.pgpass|\.git-credentials|\.npmrc|\.pypirc"""
    r"""|\.docker/config\.json|\.kube/config|credentials\.json|service[-_]?account[\w.-]*\.json"""
    r"""|[\w.-]*_secrets(?:/|\b)|secrets\.(?:json|ya?ml|env|txt|toml)"""
    r""")(?=$|[\s'";|&)<>])""",
    re.I,
)
NEVER_READ = re.compile(r"\.claude/\.credentials\.json|security\s+(?:find-(?:generic|internet)-password\b.*\s-w\b|dump-keychain)")
READ_VERBS = re.compile(r"(?:^|[\s;&|(`$'\"])(?:cat|less|more|head|tail|bat|strings|xxd|od|hexdump|base64|grep|egrep|rg|awk|sed|cut|sort|cp|scp|rsync|open|pbcopy|curl|nl|tac|jq|yq|python3?|node|php|ruby)\b")

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
BASH_RULES = [
    ("fs-wipe", "deny", re.compile(r"\brm\s+(?:-[a-zA-Z]+\s+|--[a-z-]+\s+)*(?:--\s+)?[\"']?(?:/|~/?|\$HOME/?|\$\{HOME\}/?|/\*|~/\*|\$HOME/\*|/Users/?|/Users/[^/\s]+/?|/System\S*|/usr/?|/etc/?|/var/?)[\"']?(?:\s|$|;|&|\|)"),
     "would delete the filesystem root, a system directory or the home directory"),
    ("disk-destroy", "deny", re.compile(r"\bmkfs(?:\.\w+)?\b|\bdd\b[^\n;|&]*\bof=/dev/(?:r?disk|sd|nvme|hd)|\bdiskutil\s+(?:erase\w*|zero\w*|partitionDisk|reformat)\b|:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
     "destroys disks/partitions or is a fork bomb"),
    ("credential-dump", "deny", NEVER_READ, "reads Claude/OS keychain credentials"),
    ("git-force-push", "ask", re.compile(r"\bgit\b[^\n;|&]*\bpush\b(?:(?!--force-with-lease)[^\n;|&])*?(?:\s--force(?![-\w])|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\b|\s\+[\w./:-]+)"),
     "force-push rewrites remote history"),
    ("git-delete-remote", "ask", re.compile(r"\bgit\b[^\n;|&]*\bpush\b[^\n;|&]*(?:\s--delete\b|\s-d\b|\s:[\w./-]+)"),
     "deletes a remote branch or tag"),
    ("git-discard", "ask", re.compile(r"\bgit\b[^\n;|&]*\b(?:reset\s+(?:[^\n;|&]*\s)?--hard|clean\s+-[a-zA-Z]*f|checkout\s+(?:[^\n;|&]*\s)?--\s+\.|checkout\s+\.(?:\s|$)|restore\s+(?!--staged)[^\n;|&]*\.(?:\s|$)|stash\s+(?:drop|clear)|branch\s+-D|filter-branch|filter-repo|update-ref\s+-d|reflog\s+expire)"),
     "discards uncommitted work or rewrites/deletes git history"),
    ("gh-irreversible", "ask", re.compile(r"\bgh\s+(?:pr\s+merge|repo\s+(?:delete|archive|rename|edit\b[^\n;|&]*--visibility)|release\s+(?:create|delete|upload|edit)|secret\s+(?:set|delete)|variable\s+(?:set|delete)|workflow\s+run|api\b[^\n;|&]*(?:-X|--method)\s*(?:DELETE|PUT|PATCH|POST))\b"),
     "merges, publishes, deletes or changes GitHub state"),
    ("sql-destructive", "ask", re.compile(r"(?i)\b(?:drop\s+(?:database|schema|table|user)|truncate\s+(?:table\s+)?[`\"\w.]+|alter\s+table\s+[`\"\w.]+\s+drop\b)"),
     "destructive SQL (DROP/TRUNCATE)"),
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
    ("persistent-system", "ask", re.compile(r"\bcrontab\s+(?:-r|-\s|[^-\s]\S*\s*$)|\blaunchctl\s+(?:load|bootstrap|enable)\b|\bsystemctl\s+(?:enable|disable|mask)\b|>>?\s*~?[\w/.$]*\.ssh/authorized_keys"),
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
]
NATIVE_CTX_TOOLS = ("Read", "Write", "Edit", "MultiEdit", "NotebookEdit")
MCP_SKIP = re.compile(r"^mcp__(?:ccd_|Claude_Browser__|claude-in-chrome__|computer-use__|visualize__|terminal__|scheduled-tasks__list|mcp-registry__)")


# ---------------------------------------------------------------- helpers
def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(os.path.join(ENGOS, "config.json")) as fh:
            cfg.update(json.load(fh))
    except (OSError, ValueError):
        pass
    return cfg


def emit(decision=None, reason=None, context=None):
    out = {"hookEventName": "PreToolUse"}
    if decision:
        out["permissionDecision"] = decision
        out["permissionDecisionReason"] = "%s %s" % (MARK, reason)
    if context:
        out["additionalContext"] = context
    print(json.dumps({"hookSpecificOutput": out}))


def norm(path, cwd):
    if not path:
        return ""
    path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    return os.path.normpath(path)


def under(path, root):
    return bool(root) and (path == root or path.startswith(root.rstrip("/") + "/"))


def segments(cmd):
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
    return out


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
            if not (under(p, project) or under(p, cwd) or any(under(p, r) for r in scratch_roots())):
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


def check_bash(cmd, cwd, project, cfg):
    off = set(cfg.get("disabled_rules") or [])
    for rid, decision, rx, reason in BASH_RULES:
        if rid not in off and rx.search(cmd):
            return decision, "%s: %s" % (rid, reason)
    if "rm-outside" not in off:
        why = check_rm(cmd, cwd, project)
        if why:
            return "ask", "rm-outside: " + why
    if "git-protected-push" not in off and re.search(r"\bgit\b[^\n;|&]*\bpush\b", cmd):
        why = check_push(cmd, cwd, cfg)
        if why:
            return "ask", "git-protected-push: " + why
    if cfg.get("block_claude_coauthor") and re.search(r"\bgit\b[^\n]*\bcommit\b", cmd) and COAUTHOR.search(cmd):
        return "deny", "coauthor: the user's rule is commits under their name only; remove the 'Co-Authored-By: Claude' trailer and retry"
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
    if re.search(r"\b(?:mysql|mariadb|psql|sqlite3|bench|frappe\.db|execute)\b", cmd) and any(
            SQL_UNSCOPED.search(st) and not re.search(r"(?i)\bwhere\b", st) for st in cmd.split(";")):
        return "ask", "sql-unscoped: UPDATE/DELETE without WHERE"
    if SECRET_PATH.search(cmd) and READ_VERBS.search(cmd):
        return "ask", "secret-read: prints/copies a secrets file (its values would enter the transcript)"
    if GLOBAL_CONFIG_FILES.search(cmd) and SHELL_WRITE.search(cmd) and "eng-os install" not in cmd and "eng-os restore" not in cmd:
        return "ask", "global-config: edits live global Claude config; change ~/claude/eng-os and run `eng-os install` instead"
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
        if tool == "Read" and SECRET_PATH.search(" " + path):
            return "ask", "secret-read: reading %s puts secret values into the transcript; prefer listing key names only" % os.path.basename(path)
        return None
    # write tools
    if GLOBAL_CONFIG_FILES.search(path):
        return "ask", "global-config: %s is managed by eng-os; edit ~/claude/eng-os and run `eng-os install`" % path.replace(HOME, "~")
    if re.search(r"/\.ssh/(?:authorized_keys|config)$", path):
        return "ask", "ssh-config: changes SSH access configuration"
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


def check_mcp(tool, inp):
    if MCP_SKIP.search(tool):
        return None
    if tool.startswith("mcp__meta-ads__meta_") and ("_create_" in tool or "_update_" in tool):
        blob = json.dumps(inp).lower()
        if '"active"' in blob or ("_update_" in tool and re.search(r"budget|bid_amount|bid_strategy", blob)):
            return "ask", "meta-ads: activates delivery or changes spend on a live ad account"
        return None
    for rx, why in MCP_ASK:
        if rx.search(tool):
            return "ask", "mcp-outward: %s (%s)" % (why, tool.split("__")[-1])
    return None


# ------------------------------------------------- project CLAUDE.md context
def project_context(tool, inp, cwd, root, session, cfg):
    """Return CLAUDE.md text of a subproject touched via Bash, once per session."""
    if tool == "Bash":
        c = inp.get("command", "")
        tokens = re.findall(r"(?:~|\.{1,2}|/)?[\w@.+-]*/[\w@.+/-]*", c)
        tokens += re.findall(r"(?:\bcd|\bgit\s+-C)\s+[\"']?([^\s;&|\"']+)", c)
    else:
        tokens = [inp.get("file_path") or inp.get("notebook_path") or inp.get("path") or ""]
    found = []
    for t in tokens[:40]:
        p = norm(t, cwd)
        d = p if os.path.isdir(p) else os.path.dirname(p)
        if under(d, os.path.join(HOME, ".claude")):
            continue  # Claude's own config dir: the global CLAUDE.md is already loaded
        stop = root if under(d, root) else HOME
        chain = []
        for _ in range(8):  # every CLAUDE.md between the session root (exclusive) and the file
            if not d or d == stop or not under(d, stop) or d == "/":
                break
            for name in ("CLAUDE.md", os.path.join(".claude", "CLAUDE.md")):
                f = os.path.join(d, name)
                if os.path.isfile(f):
                    chain.append(f)
                    break
            d = os.path.dirname(d)
        found.extend(reversed(chain))  # outermost first
    if not found:
        return None
    os.makedirs(STATE, exist_ok=True)
    sfile = os.path.join(STATE, "ctx-%s.json" % hashlib.sha1((session or "none").encode()).hexdigest()[:16])
    try:
        with open(sfile) as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    new = [f for f in dict.fromkeys(found) if f not in seen]
    if not new:
        return None
    with open(sfile, "w") as fh:
        json.dump(sorted(seen | set(new)), fh)
    if tool in NATIVE_CTX_TOOLS:
        return None  # the harness loads nested CLAUDE.md itself for these; just record it
    parts, limit = [], int(cfg.get("project_context_max_chars", 6000))
    for f in new:
        rel = f.replace(HOME, "~")
        try:
            body = open(f, errors="replace").read()
        except OSError:
            continue
        if len(body) <= limit:
            parts.append("eng-os: project instructions from %s (this command touches that project; they apply to all work there):\n%s" % (rel, body.strip()))
        else:
            parts.append("eng-os: %s holds project instructions (%d chars). Read it with the Read tool before changing files in that project." % (rel, len(body)))
    return "\n\n".join(parts) or None


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
    ctx = None
    if tool in ("Bash", "Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Grep", "Glob"):
        try:
            ctx = project_context(tool, inp, cwd, os.path.normpath(root), data.get("session_id"), cfg)
        except Exception as e:  # context injection must never block a tool call
            log_error("context", e)
    if verdict:
        emit("ask", verdict[1], ctx)
    elif ctx:
        emit(context=ctx)
    return 0


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
