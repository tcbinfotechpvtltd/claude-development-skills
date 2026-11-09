#!/usr/bin/env python3
"""eng-os PostToolUse hook for Bash: trims very large command output before it enters the conversation.

Why: every line a command prints stays in context and is re-read on every later turn of the session. Output over
TRIM_AT characters is cut to its first and last lines plus the error-looking lines in between. The full output is
saved first to a private file that the note names, so nothing is lost (grep or tail it). Small output passes untouched.
Switch off with ENG_OS_TRIM_OUTPUT=0. Fail-open: any problem leaves the output as it was. Python 3.9, stdlib only.
"""
import json
import os
import re
import sys
import time

ENGOS = os.environ.get("ENGOS_HOME") or os.path.expanduser("~/.claude/eng-os")
TRIM_AT = 30000          # characters; about 7,500 tokens
SAVE_MAX = 5 * 1024 * 1024    # bytes kept per saved output
DIR_MAX = 50 * 1024 * 1024    # bytes kept in the folder; oldest files go first
FULL = "# eng-os:full"            # put this in a command to keep its whole output
HEAD, TAIL, MIDDLE = 60, 40, 30  # lines kept from the start, the end, and error-looking lines in between
LINE_MAX = 400           # characters kept per line (minified files, base64)
IMPORTANT = re.compile(r"(?i)\b(?:error|exception|traceback|fatal|failed|failure|panic|denied|assert\w*)\b|^\s*E\s{2,}")
WARNING = re.compile(r"(?i)\bwarn(?:ing)?\b")


def trim(text, saved, label):
    lines = text.splitlines()
    if len(text) <= TRIM_AT or len(lines) <= HEAD + TAIL:
        if len(text) <= TRIM_AT:
            return text
        clipped = [l if len(l) <= LINE_MAX else l[:LINE_MAX] + " …[line cut]" for l in lines]
        return "\n".join(clipped) + "\n[eng-os: long lines cut to %d characters; full %s saved to %s]" % (LINE_MAX, label, saved)
    inner = lines[HEAD:-TAIL]
    errors = [l for l in inner if IMPORTANT.search(l)]
    middle = (errors + [l for l in inner if WARNING.search(l) and not IMPORTANT.search(l)])[:MIDDLE]  # errors first
    cut = lambda ls: [l if len(l) <= LINE_MAX else l[:LINE_MAX] + " …[line cut]" for l in ls]
    kept = " and %d error-looking lines from the middle" % len(middle) if middle else ""
    note = ("[eng-os: %s trimmed from %d lines (%d characters) to save tokens. Kept the first %d and last %d lines%s. "
            "Full %s: %s; grep or tail it if you need more, or add `%s` to a command to keep all its output.]"
            % (label, len(lines), len(text), HEAD, TAIL, kept, label, saved, FULL))
    return "\n".join(cut(lines[:HEAD]) + ["", note, ""] + (cut(middle) + ["…"] if middle else []) + cut(lines[-TAIL:]))


def main():
    if os.environ.get("ENG_OS_TRIM_OUTPUT") == "0":
        return 0
    data = json.loads(sys.stdin.read() or "{}")
    if data.get("tool_name") != "Bash":
        return 0
    resp = data.get("tool_response")
    if not isinstance(resp, dict):
        return 0
    streams = {k: resp.get(k) for k in ("stdout", "stderr") if isinstance(resp.get(k), str)}
    if not streams or max(len(v) for v in streams.values()) <= TRIM_AT:
        return 0
    inp = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = str(inp.get("command", ""))
    if FULL in command:
        return 0
    saved = save_full(command, streams, data.get("session_id"))
    updated = dict(resp)
    changed = False
    for k, v in streams.items():
        new = trim(v, saved, k)
        if new != v:
            updated[k] = new
            changed = True
    if changed:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": updated}}))
    else:
        os.remove(saved)
    return 0


def save_full(command, streams, session):
    """Write the full output to a private file (capped) and keep the folder small. Returns the path."""
    out_dir = os.path.join(ENGOS, "state", "out")
    os.makedirs(out_dir, mode=0o700, exist_ok=True)
    body = "$ %s\n" % command + "".join("\n----- %s -----\n%s\n" % (k, v) for k, v in streams.items())
    data = body.encode("utf-8", "replace")
    if len(data) > SAVE_MAX:
        data = data[:SAVE_MAX] + b"\n[eng-os: saved copy cut at 5 MB]\n"
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session or "nosession"))[:40]
    path = os.path.join(out_dir, "%s-%d-%d.log" % (sid, int(time.time() * 1000), os.getpid()))
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # private: output can hold secrets or personal data
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
    except Exception:
        os.remove(path)
        raise
    try:  # oldest first, until the folder is under its cap; anything over a day old goes too
        files = sorted((os.path.getmtime(os.path.join(out_dir, f)), os.path.join(out_dir, f)) for f in os.listdir(out_dir))
        total = sum(os.path.getsize(p) for _, p in files)
        for mtime, p in files:
            if p != path and (total > DIR_MAX or mtime < time.time() - 86400):
                total -= os.path.getsize(p)
                os.remove(p)
    except OSError:
        pass
    return path


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
