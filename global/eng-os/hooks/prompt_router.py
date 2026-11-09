#!/usr/bin/env python3
"""eng-os UserPromptSubmit hook: tells Claude which eng-os skills a request needs, so nobody has to name them.
Keyword routing, each skill routed at most once per session, silent when nothing matches. For each newly routed
skill it inserts that skill's "## Core rules" section, so the essentials apply even when Claude does not load the
full skill (measured: named skills were loaded in only a few sessions). About 150-250 tokens per routed skill,
once per session. Fail-open, Python 3.9 compatible, stdlib only.
"""
import json
import os
import re
import sys

ENGOS = os.environ.get("ENGOS_HOME") or os.path.expanduser("~/.claude/eng-os")
# hooks/ sits in <claude>/eng-os/hooks when installed and in global/eng-os/hooks in the repo; skills/ is beside eng-os/
SKILLS = os.environ.get("ENGOS_SKILLS") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "skills")
MAX_SKILLS = 4
# Context-size note: most of a session's cost is re-reading the whole conversation on every turn (measured: 76% of
# turns ran above 200k tokens, 43% above 400k), so say so once at 200k and again at every further 200k.
CTX_FIRST = 200000
CTX_STEP = 200000
MAX_CORE_CHARS = 1200     # per skill; `eng-os verify` keeps each section at or under 1,000
MAX_CONTEXT_CHARS = 4500  # well under Claude Code's 10,000-character hook output cap

# Most specific first: domain and stack skills, then activity skills.
ROUTES = [
    ("fintech-lending", r"loans?|lending|nbfc|lsp|disburs\w*|repayments?|emi|interest rate|ledgers?|kyc|ekyc|bureau|cibil|crif|"
                        r"account aggregator|e-?nach|e-?sign|payouts?|razorpay|payment gateway|rbi|dpdp"),
    ("frappe-erpnext", r"frappe|erpnext|bench|doctypes?|hrms"),
    ("odoo", r"odoo"),
    ("custom-apps", r"next\.?js|react|node\.?js|flutter|dart|codeigniter|ci3|php|fastapi|django|python (script|service)"),
    ("eng-security", r"auth\w*|login|passwords?|otp|sessions?|permissions?|roles?|access control|secur\w*|vulnerab\w*|xss|"
                     r"sql injection|csrf|tokens?|secrets?|encrypt\w*|uploads?|pii|aadhaar|webhooks?|pentest"),
    ("eng-testing", r"tests?|testing|unit tests?|e2e|playwright|bugs?|failing|fails|failed|errors?|exceptions?|traceback|"
                    r"debug\w*|flaky|crash\w*|not working|broken|regressions?"),
    ("eng-design", r"design|architecture|architect|schema|data model|erd|api contract|specs?|specification|adr|"
                   r"new (\w+ )?(feature|module|app|system|service|api|integration)|which (framework|database|library)|"
                   r"implementation plan|step[- ]by[- ]step plan|task breakdown|break (it|this|the work) down into (tasks|steps)"),
    ("eng-ship", r"deploy\w*|releases?|ci|cd|pipelines?|github actions|docker|servers?|vps|aws|nginx|migrations?|"
                 r"backups?|restore|monitoring|incidents?|outage|rollback|changelog|versioning|tag"),
    ("eng-docs", r"document\w*|docs|manuals?|user guide|requirements?|brd|srs|runbook|handover|test cases?"),
    ("eng-delivery", r"estimates?|estimation|timeline|project plan|scope|sprint|status report|change request|uat|"
                     r"go-?live|cutover|hypercare|milestones?|implementation"),
    ("eng-review", r"review|pull request|pr|commit|merge|code quality"),
    ("eng-project-init", r"onboard\w*|set ?up (this|the) (project|repo)|claude\.md"),
]
PATTERNS = [(skill, re.compile(r"\b(?:%s)\b" % rx, re.I)) for skill, rx in ROUTES]
CORE = re.compile(r"^## Core rules[^\n]*\n(.*?)(?=^## |\Z)", re.S | re.M)


def installed(skill):
    """Skip optional packs this company left out. If the skills folder itself is missing, filter nothing."""
    return not os.path.isdir(SKILLS) or os.path.isdir(os.path.join(SKILLS, skill))


def core_rules(skill):
    """The skill's '## Core rules' section, or '' when it is missing or unreadable."""
    try:
        with open(os.path.join(SKILLS, skill, "SKILL.md"), errors="replace") as fh:
            m = CORE.search(fh.read())
    except OSError:
        return ""
    return m.group(1).strip()[:MAX_CORE_CHARS] if m else ""


def routing_context(skills, lead):
    """(text, done): a header naming the skills, then each one's core rules while they fit in MAX_CONTEXT_CHARS.
    `done` lists the skills that need no repeat this session: core rules inserted, or none to insert. A skill
    whose rules did not fit is routed again on a later request."""
    # Explicit "call the Skill tool with `x`" wording loads skills more often than naming them (mattpocock/skills).
    text = ("%s %s. Before a task they cover, call the Skill tool with %s, unless the task is trivial. Their core "
            "rules apply from now:" % (lead, ", ".join("`%s`" % s for s in skills), ", then ".join("`%s`" % s for s in skills)))
    done = []
    for s in skills:
        core = core_rules(s)
        block = "\n\n`%s` core rules:\n%s" % (s, core)
        if not core:
            done.append(s)
        elif len(text) + len(block) <= MAX_CONTEXT_CHARS:
            text += block
            done.append(s)
    return text, done


def context_tokens(transcript_path):
    """Tokens in context at the session's latest model call, read from the tail of its transcript; 0 if unknown."""
    try:
        with open(transcript_path, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 262144))
            tail = fh.read().decode("utf-8", "replace")
    except (OSError, TypeError, ValueError):
        return 0
    for line in reversed(tail.splitlines()):
        if "compact_boundary" in line:
            return 0  # compacted since the last reply: the old figure no longer applies
        if '"usage"' not in line or '"assistant"' not in line:
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("isSidechain"):
            continue  # a subagent's own context, not this conversation's
        u = (o.get("message") or {}).get("usage") or {}
        n = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
        if n:
            return n
    return 0


def context_note(data, session, state_dir):
    """One line when the context first passes 200k tokens, and again at every further 200k; '' otherwise."""
    if os.environ.get("ENG_OS_CONTEXT_NOTE") == "0":
        return ""
    n = context_tokens(data.get("transcript_path"))
    if n < CTX_FIRST:
        return ""
    level = CTX_FIRST + ((n - CTX_FIRST) // CTX_STEP) * CTX_STEP
    f = os.path.join(state_dir, "ctx-%s.json" % session)
    try:
        with open(f) as fh:
            last = int(json.load(fh).get("level", 0))
    except (OSError, ValueError, AttributeError, TypeError):
        last = 0
    if level <= last:
        return ""
    os.makedirs(state_dir, exist_ok=True)
    tmp = "%s.%d.tmp" % (f, os.getpid())
    with open(tmp, "w") as fh:
        json.dump({"level": level}, fh)
    os.replace(tmp, f)
    return ("eng-os context note: this conversation holds about %dk tokens, and every turn re-reads all of it. Finish the "
            "current task; for a new or unrelated task, record progress in docs/progress and suggest the user starts a "
            "fresh session or runs /compact." % (n // 1000))


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    prompt = (data.get("prompt") or "").strip()
    if prompt.startswith("/"):
        return 0
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "nosession"))[:80]
    state_dir = os.path.join(ENGOS, "state")
    try:
        note = context_note(data, session, state_dir)
    except Exception:
        note = ""
    text = routing(prompt, session, state_dir) if len(prompt) >= 12 else ""
    out = "\n\n".join(t for t in (note, text) if t)
    if out:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": out}}))
    return 0


def routing(prompt, session, state_dir):
    """The routing note with core rules for newly matched skills, or ''."""
    # only skills this machine has: a company may leave out the optional packs (frappe-erpnext, odoo, fintech-lending)
    matched = [skill for skill, rx in PATTERNS if rx.search(prompt) and installed(skill)]
    if not matched:
        return ""
    seen_file = os.path.join(state_dir, "route-%s.json" % session)
    try:
        with open(seen_file) as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    new = [s for s in matched if s not in seen][:MAX_SKILLS]
    if not new:
        return ""
    text, done = routing_context(new, "eng-os skill routing: this request matches")
    os.makedirs(state_dir, exist_ok=True)
    with open(seen_file, "w") as fh:
        json.dump(sorted(seen | set(done)), fh)
    return text


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
