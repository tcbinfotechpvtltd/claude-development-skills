#!/usr/bin/env python3
"""eng-os SessionStart hook. Silent (zero context) unless something needs attention:
  - the periodic self-audit is due (manifest.last_audit older than audit_interval_days)
  - installed eng-os files were edited outside `eng-os install` (checksum drift)
Also prunes per-session guard state older than 3 days. Fail-open, Python 3.9 compatible.
"""
import hashlib
import json
import os
import sys
import time

ENGOS = os.environ.get("ENGOS_HOME") or os.path.expanduser("~/.claude/eng-os")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        data = {}
    if data.get("source") not in (None, "startup"):
        return 0  # resume/clear/compact: CLAUDE.md is reloaded by the harness; stay silent
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
            notes.append("periodic self-audit is due (last %s). At a natural break, offer the user /eng-os-review; do not interrupt urgent work." % (last[:10] or "never"))
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
    state = os.path.join(ENGOS, "state")
    if os.path.isdir(state):
        cutoff = time.time() - 3 * 86400
        for f in os.listdir(state):
            p = os.path.join(state, f)
            if f.startswith("ctx-") and os.path.getmtime(p) < cutoff:
                try:
                    os.remove(p)
                except OSError:
                    pass
    if notes:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": "eng-os: " + " ".join(notes)}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
