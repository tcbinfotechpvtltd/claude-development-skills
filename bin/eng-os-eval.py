#!/usr/bin/env python3
"""eng-os behavioural evaluation: scores real Claude Code sessions against scenario checks.

  eng-os-eval.py --prepare-sandbox [DIR]        create the test project (default ~/claude/eng-os-sandbox)
  eng-os-eval.py --prompt SUITE                 print a suite's prompt (paste into a fresh session)
  eng-os-eval.py --transcript FILE --suite S    score an existing session transcript
  eng-os-eval.py --run [--suite S] [--model M] [--claude BIN] [--budget USD]
                                                run suite prompts with `claude -p` in the sandbox and score them

Checks are read from tests/scenarios.json. Transcripts are local JSONL files; their format is internal
to Claude Code and may change, so failures of the parser itself are reported as ERROR, not FAIL.
Python 3.9 compatible, stdlib only.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_SANDBOX = os.path.join(HOME, "claude", "eng-os-sandbox")


def scenarios():
    for base in (REPO, os.path.join(HOME, ".claude", "eng-os")):
        p = os.path.join(base, "tests", "scenarios.json")
        if os.path.exists(p):
            return json.load(open(p))
    sys.exit("tests/scenarios.json not found")


def prepare_sandbox(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    files = {
        "CLAUDE.md": "# eng-os sandbox (test project)\nThrowaway project used by `eng-os eval`. Canary: SANDBOX-ROOT-7731.\n"
                     "**Required skills**: fintech-lending (domain: loan ledger).\n",
        "sub/CLAUDE.md": "# Ledger module\nCanary: SANDBOX-SUB-4410. Amounts are integer paise.\n",
        "sub/ledger.py": "LEDGER = []\n\n\ndef post(debit, credit, amount_paise):\n    LEDGER.append((debit, credit, amount_paise))\n",
        "app/doctype/loan/loan.py": "import frappe\nfrom frappe.model.document import Document\n\n\nclass Loan(Document):\n    pass\n",
        ".env": "SANDBOX_TOKEN=not-a-real-secret\n",
        ".gitignore": ".env\n",
    }
    for rel, body in files.items():
        p = os.path.join(path, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body)
    g = ["git", "-C", path]
    subprocess.run(g + ["init", "-q", "-b", "main"], check=True)
    subprocess.run(g + ["add", "-A"], check=True)
    subprocess.run(g + ["-c", "user.name=eng-os", "-c", "user.email=eng-os@localhost", "commit", "-qm", "sandbox"], check=True)
    print("sandbox ready: " + path)


def parse(transcript):
    """Flatten a transcript into texts, tool calls (with results) and raw text."""
    texts, calls, results, raw = [], [], {}, []
    first_ctx, total_in, total_out, seen = None, 0, 0, set()
    for line in open(transcript, errors="replace"):
        raw.append(line)
        try:
            o = json.loads(line)
        except ValueError:
            continue
        msg = o.get("message") or {}
        if o.get("type") == "assistant":
            mid = msg.get("id")
            u = msg.get("usage") or {}
            if mid and mid not in seen:
                seen.add(mid)
                ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                total_in += ctx
                total_out += u.get("output_tokens", 0)
                if first_ctx is None and ctx:
                    first_ctx = ctx
            for b in msg.get("content") or []:
                if b.get("type") == "text":
                    texts.append(b.get("text", ""))
                elif b.get("type") == "tool_use":
                    calls.append({"id": b.get("id"), "name": b.get("name"), "input": b.get("input") or {}})
        elif o.get("type") == "user" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content")
                    text = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [] if isinstance(x, dict))
                    results[b.get("tool_use_id")] = {"text": text, "error": bool(b.get("is_error")),
                                                     "decision": o.get("permissionDecision") or {}}
    for c in calls:
        c["result"] = results.get(c["id"], {})
    return {"texts": texts, "calls": calls, "raw": "".join(raw), "first_ctx": first_ctx,
            "total_in": total_in, "total_out": total_out}


def run_check(chk, t):
    kind = chk["type"]
    rx = re.compile(chk.get("pattern", ".*"), re.I | re.S)
    if kind == "text":
        return any(rx.search(x) for x in t["texts"])
    if kind == "raw":
        return bool(rx.search(t["raw"]))
    name = re.compile(chk.get("tool", ".*"))
    matches = [c for c in t["calls"] if name.fullmatch(c["name"] or "") and rx.search(json.dumps(c["input"]))]
    if kind == "tool_called":
        return bool(matches)
    if kind == "tool_blocked":  # called, and the result shows a guard/permission rejection
        want = chk.get("reason", "")
        return any((c["result"].get("decision", {}).get("decision") == "reject" or c["result"].get("error"))
                   and want.lower() in (c["result"].get("text", "") + json.dumps(c["result"].get("decision"))).lower()
                   for c in matches)
    if kind == "tool_not_executed":  # never ran successfully
        return not any(c["result"] and not c["result"].get("error")
                       and c["result"].get("decision", {}).get("decision") != "reject" for c in matches)
    raise ValueError("unknown check type " + kind)


def score(transcript, suite):
    sc = scenarios()["suites"].get(suite)
    if not sc:
        sys.exit("unknown suite " + suite)
    try:
        t = parse(transcript)
    except Exception as e:
        print("ERROR parsing transcript: %r" % e)
        return 2
    print("transcript: %s" % transcript.replace(HOME, "~"))
    print("tokens: first-turn context=%s, total input=%d, output=%d, tool calls=%d" % (
        t["first_ctx"], t["total_in"], t["total_out"], len(t["calls"])))
    fails = 0
    for chk in sc["checks"]:
        try:
            ok = run_check(chk, t)
            status = "PASS" if ok else ("WARN" if chk.get("soft") else "FAIL")
        except Exception as e:
            status, ok = "ERROR %r" % e, False
        if status in ("FAIL",) or status.startswith("ERROR"):
            fails += 1
        print("%-5s %s" % (status, chk["id"]))
    print("%s: %d/%d hard checks passed" % (suite, sum(1 for c in sc["checks"] if not c.get("soft")) - fails,
                                            sum(1 for c in sc["checks"] if not c.get("soft"))))
    return 1 if fails else 0


def project_dir_for(path):
    return os.path.join(HOME, ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(path)))


def run(args):
    sandbox = args.sandbox
    prepare_sandbox(sandbox)
    data = scenarios()["suites"]
    suites = [args.suite] if args.suite else [k for k, v in data.items() if v.get("headless")]
    rc = 0
    for s in suites:
        prompt = data[s]["prompt"].replace("{SANDBOX}", sandbox)
        cmd = [args.claude, "-p", prompt, "--output-format", "json", "--model", args.model,
               "--permission-mode", "bypassPermissions", "--max-budget-usd", str(args.budget)]
        print("== %s (%s)" % (s, args.model))
        r = subprocess.run(cmd, cwd=sandbox, capture_output=True, text=True, timeout=900)
        try:
            out = json.loads(r.stdout)
        except ValueError:
            print("ERROR: claude -p returned no JSON: %s" % (r.stdout or r.stderr)[:300])
            rc = 2
            continue
        if out.get("is_error"):
            print("ERROR: %s" % str(out.get("result"))[:300])
            rc = 2
            continue
        print("cost: $%s" % out.get("total_cost_usd"))
        tr = os.path.join(project_dir_for(sandbox), out["session_id"] + ".jsonl")
        if not os.path.exists(tr):
            cand = glob.glob(os.path.join(HOME, ".claude", "projects", "*", out["session_id"] + ".jsonl"))
            tr = cand[0] if cand else tr
        rc |= score(tr, s)
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prepare-sandbox", nargs="?", const=DEFAULT_SANDBOX)
    ap.add_argument("--prompt")
    ap.add_argument("--transcript")
    ap.add_argument("--suite")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--claude", default=os.environ.get("CLAUDE_CODE_EXECPATH") or shutil.which("claude") or "claude")
    ap.add_argument("--budget", type=float, default=0.50)
    ap.add_argument("--sandbox", default=DEFAULT_SANDBOX)
    a = ap.parse_args()
    if a.prepare_sandbox:
        prepare_sandbox(a.prepare_sandbox)
        return 0
    if a.prompt:
        print(scenarios()["suites"][a.prompt]["prompt"].replace("{SANDBOX}", a.sandbox))
        return 0
    if a.transcript:
        return score(a.transcript, a.suite or "fresh-session")
    if a.run:
        return run(a)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
