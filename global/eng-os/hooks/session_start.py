#!/usr/bin/env python3
"""eng-os SessionStart hook. Silent (zero context) unless something needs attention:
  - the periodic self-audit is due (manifest.last_audit older than audit_interval_days)
  - installed eng-os files were edited outside `eng-os install` (checksum drift)
  - a newer eng-os release tag exists on the repo's remote (checked at most once a week)
  - the session's project uses a recognisable stack (with or without a stack-specific eng-os skill),
    or is a project (git or not) without a CLAUDE.md. Nothing here names a specific project.
  - for the project's eng-os skills, their "## Core rules" sections (also restated after compaction or /clear,
    when the per-session routing record is reset so the prompt router can insert core rules again).
Also prunes per-session guard state older than 3 days. Fail-open, Python 3.9 compatible.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ENGOS = os.environ.get("ENGOS_HOME") or os.path.expanduser("~/.claude/eng-os")
UPDATE_CHECK_DAYS = 7


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def vtuple(s):
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)$", (s or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def update_note(man, state):
    """At most once a week: is a newer release tag published on the repo's remote? Never prompts; silent on failure."""
    stamp = os.path.join(state, "update-check.json")
    try:
        with open(stamp) as fh:
            last = float(json.load(fh).get("checked", 0))
    except (OSError, ValueError, TypeError):
        last = 0
    if time.time() - last < UPDATE_CHECK_DAYS * 86400:
        return None
    os.makedirs(state, exist_ok=True)
    with open(stamp, "w") as fh:
        json.dump({"checked": time.time()}, fh)
    repo, current = man.get("repo"), vtuple(man.get("version"))
    if not repo or not current or not os.path.isdir(os.path.join(repo, ".git")):
        return None
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="echo", GIT_SSH_COMMAND="ssh -o BatchMode=yes")
    out = subprocess.run(["git", "-C", repo, "ls-remote", "--tags", "--refs", "origin"],
                         capture_output=True, text=True, timeout=4, env=env).stdout
    tags = [t for t in (vtuple(line.rsplit("/", 1)[-1]) for line in out.splitlines()) if t]
    if tags and max(tags) > current:
        return ("release v%d.%d.%d is available (installed %s). Tell the user once, briefly; they update with "
                "`~/.claude/eng-os/bin/eng-os update`, which runs the tests and shows a preview first." % (max(tags) + (man.get("version"),)))
    return None


def read_head(path, n=4000):
    try:
        with open(path, errors="replace") as fh:
            return fh.read(n)
    except OSError:
        return ""


def stack_markers(d, look_into_addons=False):
    """(name, skill) pairs whose marker files sit directly in folder d."""
    j = lambda *p: os.path.join(d, *p)
    found = []
    if os.path.isdir(j("apps", "frappe")) or (os.path.exists(j("hooks.py")) and os.path.exists(j("modules.txt"))):
        found.append(("Frappe/ERPNext", "frappe-erpnext"))
    odoo = os.path.exists(j("__manifest__.py")) or os.path.exists(j("odoo-bin"))
    if not odoo and look_into_addons:
        try:
            odoo = any(os.path.exists(os.path.join(e.path, "__manifest__.py")) for e in list(os.scandir(d))[:300] if e.is_dir())
        except OSError:
            pass
    if odoo:
        found.append(("Odoo", "odoo"))
    pkg = read_head(j("package.json"), 20000)
    if '"next"' in pkg:
        found.append(("Next.js", "custom-apps (nextjs.md)"))
    elif pkg:
        found.append(("Node/JavaScript", "custom-apps"))
    if "flutter" in read_head(j("pubspec.yaml")):
        found.append(("Flutter", "custom-apps (flutter.md)"))
    if os.path.exists(j("application", "config", "config.php")) and os.path.isdir(j("system", "core")):
        found.append(("PHP CodeIgniter 3", "custom-apps (php-ci3.md)"))
    if '"react-native"' in pkg:
        found.append(("React Native", "custom-apps"))
    if os.path.exists(j("manage.py")):
        found.append(("Django", "custom-apps (python.md)"))
    # Stacks without a stack-specific eng-os skill: the general skills still apply.
    try:
        names = os.listdir(d)
    except OSError:
        names = []
    other = [("Laravel", os.path.exists(j("artisan")) and os.path.exists(j("composer.json"))),
             ("WordPress", os.path.exists(j("wp-config.php")) or os.path.isdir(j("wp-content"))),
             ("PHP", os.path.exists(j("composer.json")) and not found),
             ("Java/Kotlin", any(n in names for n in ("pom.xml", "build.gradle", "build.gradle.kts"))),
             ("C#/.NET", any(n.endswith((".csproj", ".sln")) for n in names)),
             ("Go", "go.mod" in names), ("Rust", "Cargo.toml" in names), ("Ruby", "Gemfile" in names),
             ("iOS (Swift)", any(n.endswith(".xcodeproj") for n in names))]
    found.extend((name, None) for name, hit in other if hit and not (name == "PHP" and any(f[0] == "Laravel" for f in found)))
    return found


def record_stacks(state, found):
    """Count detected stacks per machine, so the periodic review can see which stacks still lack a skill."""
    path = os.path.join(state, "stacks-seen.json")
    try:
        with open(path) as fh:
            seen = json.load(fh)
    except (OSError, ValueError):
        seen = {}
    for name, skill in found:
        entry = seen.setdefault(name, {"sessions": 0, "skill": skill})
        entry["sessions"] += 1
    os.makedirs(state, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(seen, fh, indent=1)


def detect_project(cwd, skills=None, record=True):
    """Which eng-os skills fit the project in cwd: markers in cwd and its direct subfolders (and Odoo modules inside an
    addons folder). A folder that merely holds many separate projects stays silent. Returns the notes; when `skills`
    is a list, the matching eng-os skill names are appended to it."""
    if skills is None:
        skills = []
    home = os.path.expanduser("~")
    if not cwd or not os.path.isdir(cwd) or os.path.realpath(cwd) in (os.path.realpath(home), "/"):
        return []
    j = lambda *p: os.path.join(cwd, *p)
    found = stack_markers(cwd, look_into_addons=True)
    if not found:
        try:
            subdirs = [e for e in os.scandir(cwd) if e.is_dir() and not e.name.startswith(".")
                       and e.name not in ("node_modules", "venv", ".venv", "vendor", "env")][:200]
        except OSError:
            subdirs = []
        per_dir = [(e.name, stack_markers(e.path, look_into_addons="addons" in e.name.lower())) for e in subdirs]
        per_dir = [(n, f) for n, f in per_dir if f]
        if not os.path.isdir(j(".git")) and (len(per_dir) > 2 or len(subdirs) > 8):
            return []  # a workspace holding several projects, not one project
        for _, f in per_dir:
            found.extend(x for x in f if x not in found)
    if not found and (os.path.exists(j("pyproject.toml")) or os.path.exists(j("requirements.txt"))):
        found.append(("Python", "custom-apps (python.md)"))
    if record:
        try:
            record_stacks(os.path.join(ENGOS, "state"), found)
        except Exception:
            pass
    notes = []
    covered = [(n, s) for n, s in found if s]
    uncovered = [n for n, s in found if not s]
    if covered:
        notes.append("this project looks like %s; the eng-os skill for it is %s." % (
            " + ".join(n for n, _ in covered), ", ".join("`%s`" % s for _, s in covered)))
        for _, s in covered:
            base = s.split(" ", 1)[0]
            if base not in skills:
                skills.append(base)
    if uncovered:
        notes.append("this project uses %s, which has no stack-specific eng-os skill: the general eng-os skills apply, "
                     "and its conventions belong in the project CLAUDE.md." % " + ".join(uncovered))
    brief = read_head(j("CLAUDE.md")) + read_head(j(".claude", "CLAUDE.md"))
    facts = "\n".join(line for line in brief.splitlines() if "<e.g." not in line).replace("fintech-lending", "")
    if re.search(r"\b(loans?|lending|nbfc|lsp|disburs\w*|kyc|ledger)\b", facts, re.I):
        notes.append("its CLAUDE.md describes lending or KYC work, which skill `fintech-lending` covers.")
        if "fintech-lending" not in skills:
            skills.append("fintech-lending")
    is_git = os.path.isdir(j(".git"))
    if not brief and (is_git or found):
        notes.append("this project has no CLAUDE.md yet%s; `/eng-project-init` creates one with the docs set and templates."
                     % ("" if is_git else " and is not under version control"))
    return notes


def project_cores(data, skills):
    """Core rules of the project's skills (at most 3), recorded as already routed for this session so the prompt
    router does not repeat them. '' when there is nothing to add."""
    skills = skills[:3]
    if not skills:
        return ""
    sys.dont_write_bytecode = True  # keep the installed hooks folder free of __pycache__
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import prompt_router
    text, done = prompt_router.routing_context(skills, "eng-os project skills:")
    seen_file = route_file(data)
    try:
        with open(seen_file) as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    os.makedirs(os.path.dirname(seen_file), exist_ok=True)
    with open(seen_file, "w") as fh:
        json.dump(sorted(seen | set(done)), fh)
    return text


def route_file(data):
    """Same per-session file the prompt router uses to route each skill once."""
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "nosession"))[:80]
    return os.path.join(ENGOS, "state", "route-%s.json" % session)


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        data = {}
    source = data.get("source")
    if source in ("compact", "clear"):
        # The context that held earlier core rules is gone: let the router insert them again, and restate the
        # project's own skills. Everything else stays silent (CLAUDE.md is reloaded by the harness).
        try:
            os.remove(route_file(data))
        except OSError:
            pass
        skills = []
        try:
            detect_project(data.get("cwd"), skills, record=False)
            text = project_cores(data, skills)
        except Exception:
            text = ""
        if text:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
        return 0
    if source not in (None, "startup"):
        return 0  # resume: the conversation context is intact; stay silent
    notes = []
    try:
        with open(os.path.join(ENGOS, "manifest.json")) as fh:
            man = json.load(fh)
    except (OSError, ValueError):
        man = None
    if man:
        try:
            with open(os.path.join(ENGOS, "config.json")) as fh:
                interval = int(json.load(fh).get("audit_interval_days", 30))
        except (OSError, ValueError):
            interval = 30
        last = man.get("last_audit") or man.get("installed_at", "")
        try:
            age = (time.time() - time.mktime(time.strptime(last[:10], "%Y-%m-%d"))) / 86400
        except ValueError:
            age = interval + 1
        if age > interval:
            notes.append("periodic self-audit is due (last %s). At a natural break, suggest the user runs /eng-os-review (only they can start it); do not interrupt urgent work." % (last[:10] or "never"))
        drift = []
        for rel, digest in (man.get("files") or {}).items():
            p = os.path.expanduser(rel)
            try:
                if sha(p) != digest:
                    drift.append(rel)
            except OSError:
                drift.append(rel + " (missing)")
        if drift:
            notes.append("installed files differ from the reviewed install (%s). Treat them as unreviewed; tell the user and suggest `~/.claude/eng-os/bin/eng-os verify`." % ", ".join(drift[:5]))
    skills = []
    try:
        notes.extend(detect_project(data.get("cwd"), skills))
    except Exception:
        pass
    state = os.path.join(ENGOS, "state")
    if man:
        try:
            note = update_note(man, state)
            if note:
                notes.append(note)
        except Exception:
            pass
    if os.path.isdir(state):
        cutoff = time.time() - 3 * 86400
        for f in os.listdir(state):
            p = os.path.join(state, f)
            if f.startswith(("ctx-", "route-")) and os.path.getmtime(p) < cutoff:
                try:
                    os.remove(p)
                except OSError:
                    pass
    try:
        cores = project_cores(data, skills)
    except Exception:
        cores = ""
    if notes:
        text = "eng-os: " + " ".join(notes) + ("\n\n" + cores if cores else "")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
