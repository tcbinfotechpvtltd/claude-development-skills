#!/usr/bin/env python3
"""eng-os UserPromptSubmit hook: tells Claude which eng-os skills a request needs, so nobody has to name them.
Keyword routing, each skill suggested at most once per session, silent when nothing matches.
Zero model tokens unless it speaks (~40 tokens). Fail-open, Python 3.9 compatible, stdlib only.
"""
import json
import os
import re
import sys

ENGOS = os.environ.get("ENGOS_HOME") or os.path.expanduser("~/.claude/eng-os")
MAX_SKILLS = 4

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


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    prompt = (data.get("prompt") or "").strip()
    if len(prompt) < 12 or prompt.startswith("/"):
        return 0
    matched = [skill for skill, rx in PATTERNS if rx.search(prompt)]
    if not matched:
        return 0
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "nosession"))[:80]
    state_dir = os.path.join(ENGOS, "state")
    seen_file = os.path.join(state_dir, "route-%s.json" % session)
    try:
        with open(seen_file) as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    new = [s for s in matched if s not in seen][:MAX_SKILLS]
    if not new:
        return 0
    os.makedirs(state_dir, exist_ok=True)
    with open(seen_file, "w") as fh:
        json.dump(sorted(seen | set(new)), fh)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "eng-os skill routing: the eng-os skills covering this request are %s."
                             % ", ".join("`%s`" % s for s in new)}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
