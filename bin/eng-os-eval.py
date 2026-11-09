#!/usr/bin/env python3
"""eng-os behavioural evaluation: scores real Claude Code sessions against scenario checks.

  eng-os-eval.py --prepare-sandbox [DIR]        create the test project (default ~/claude/eng-os-sandbox, or ~/eng-os-sandbox)
  eng-os-eval.py --prompt SUITE                 print a suite's prompt (paste into a fresh session)
  eng-os-eval.py --transcript FILE --suite S    score an existing session transcript
  eng-os-eval.py --run [--suite S] [--model M] [--claude BIN] [--budget USD]
                                                run suite prompts with `claude -p` in the sandbox and score them
  eng-os-eval.py --skills [--skill NAME] [--model M] [--budget USD]
                                                skill-trigger test: each case in tests/skill_cases.json runs in a fresh
                                                one-turn `claude -p` session in an empty folder; reports how often each
                                                skill is loaded (positives) and wrongly loaded (negatives). Costs tokens.
  eng-os-eval.py --self-test                    unit tests for the transcript and stream parsers (zero tokens)

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
import tempfile

HOME = os.path.expanduser("~")
REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_SANDBOX = os.path.join(HOME, "claude" if os.path.isdir(os.path.join(HOME, "claude")) else "", "eng-os-sandbox")


def scenarios():
    for base in (REPO, os.path.join(HOME, ".claude", "eng-os")):
        p = os.path.join(base, "tests", "scenarios.json")
        if os.path.exists(p):
            return json.load(open(p))
    sys.exit("tests/scenarios.json not found")


SKILL_EVAL_TOOLS = "Read,Glob,Grep,Skill"


def skill_cases():
    for base in (REPO, os.path.join(HOME, ".claude", "eng-os")):
        p = os.path.join(base, "tests", "skill_cases.json")
        if os.path.exists(p):
            return json.load(open(p))["cases"]
    sys.exit("tests/skill_cases.json not found")


def skills_called(stream):
    """(skills loaded with the Skill tool, cost in USD, error text) from `claude -p --output-format stream-json` output."""
    called, cost, error = [], None, None
    for line in stream.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            for b in (o.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
                    called.append((b.get("input") or {}).get("skill", "?"))
        elif o.get("type") == "result":
            cost = o.get("total_cost_usd")
            if o.get("is_error") and o.get("subtype") != "error_max_turns":
                error = str(o.get("result") or o.get("subtype"))[:200]
    return called, cost, error


def run_skills(args):
    cases = skill_cases()
    names = [args.skill] if args.skill else sorted(cases)
    unknown = [n for n in names if n not in cases]
    if unknown:
        sys.exit("no cases for: %s" % ", ".join(unknown))
    work = tempfile.mkdtemp(prefix="eng-os-skill-eval-")  # empty folder: no project, so only the prompt routes
    rows = []
    print("skill-trigger test, model %s, folder %s, stops after $%.2f" % (args.model, work, args.max_total))
    try:
        rc = skills_loop(args, cases, names, work, rows)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return rc


def skills_loop(args, cases, names, work, rows):
    total_cost, rc = 0.0, 0
    for name in names:
        hits = wrong = errors = 0
        runs = [(p, True) for p in cases[name].get("positive", [])] + [(p, False) for p in cases[name].get("negative", [])]
        for prompt, positive in runs:
            # Read-only and side-effect free: only the tools a first move needs, no MCP servers
            # (flags as in modelcontextprotocol/servers scripts/skill-eval.mjs).
            cmd = [args.claude, "-p", prompt, "--output-format", "stream-json", "--verbose", "--max-turns", "1",
                   "--tools", SKILL_EVAL_TOOLS, "--allowedTools", SKILL_EVAL_TOOLS,
                   "--disallowedTools", "Bash,Write,Edit,NotebookEdit,Task,Agent,WebFetch,WebSearch",
                   "--strict-mcp-config", "--model", args.model, "--max-budget-usd", str(args.budget)]
            try:
                r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=300)
                called, cost, error = skills_called(r.stdout)
                if not r.stdout.strip():
                    error = (r.stderr or "no output")[:200]
            except (OSError, subprocess.SubprocessError) as e:
                called, cost, error = [], None, str(e)[:200]
            total_cost += cost or 0
            if total_cost > args.max_total:
                print("STOPPED: spent $%.2f, over --max-total $%.2f" % (total_cost, args.max_total))
                return 2
            if error:
                errors += 1
                rc = 2
                print("  ERROR %s: %s" % (name, error))
                continue
            loaded = name in called
            if positive:
                hits += loaded
            else:
                wrong += loaded
            print("  %s %-16s %s %s" % ("ok  " if loaded == positive else "MISS", name, "+" if positive else "-",
                                        prompt[:70] + (" -> " + ", ".join(called) if called else "")))
        rows.append((name, hits, len(cases[name].get("positive", [])), wrong, len(cases[name].get("negative", [])), errors))
    print("\nskill              loaded on positives   wrongly loaded on negatives")
    for name, h, n, w, m, e in rows:
        print("%-18s %2d/%-2d %15s %d/%d%s" % (name, h, n, "", w, m, ("  (%d errors)" % e) if e else ""))
    hp, np_ = sum(r[1] for r in rows), sum(r[2] for r in rows)
    print("overall: %d/%d positives loaded (%.0f%%); %d wrong loads; cost $%.2f" % (
        hp, np_, 100.0 * hp / np_ if np_ else 0, sum(r[3] for r in rows), total_cost))
    return rc


def self_test():
    a = json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "x"}, {"type": "tool_use", "name": "Skill", "input": {"skill": "eng-testing"}}]}})
    b = json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {}}]}})
    done = json.dumps({"type": "result", "subtype": "error_max_turns", "is_error": True, "total_cost_usd": 0.02})
    bad = json.dumps({"type": "result", "subtype": "error_during_execution", "is_error": True, "result": "boom"})
    checks = [
        ("skill call found", skills_called("\n".join([a, done]))[0] == ["eng-testing"]),
        ("max-turns stop is not an error", skills_called("\n".join([a, done]))[2] is None),
        ("cost read", skills_called(done)[1] == 0.02),
        ("other tools ignored", skills_called(b)[0] == []),
        ("real error reported", skills_called(bad)[2] == "boom"),
        ("non-JSON lines skipped", skills_called("garbage\n" + a)[0] == ["eng-testing"]),
        ("every skill has 5 positives and 1 negative", all(
            len(v.get("positive", [])) == 5 and len(v.get("negative", [])) == 1 for v in skill_cases().values())),
    ]
    failed = [n for n, ok in checks if not ok]
    print("eval self-test: %d/%d passed%s" % (len(checks) - len(failed), len(checks),
                                              "".join("\n  FAIL " + n for n in failed)))
    return 1 if failed else 0


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
    ap.add_argument("--skills", action="store_true")
    ap.add_argument("--skill")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--model", help="default: haiku for --run, sonnet for --skills")
    ap.add_argument("--claude", default=os.environ.get("CLAUDE_CODE_EXECPATH") or shutil.which("claude") or "claude")
    ap.add_argument("--budget", type=float, default=0.50, help="per session")
    ap.add_argument("--max-total", type=float, default=5.00, help="--skills: stop once this much is spent")
    ap.add_argument("--sandbox", default=DEFAULT_SANDBOX)
    a = ap.parse_args()
    a.model = a.model or ("sonnet" if a.skills else "haiku")
    if a.self_test:
        return self_test()
    if a.skills:
        return run_skills(a)
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
