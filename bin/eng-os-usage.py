#!/usr/bin/env python3
"""eng-os usage analyzer: measures token/tool efficiency from Claude Code transcripts.

Reads ~/.claude/projects/**/*.jsonl (local transcripts, never sent anywhere).
Python 3.9 compatible, stdlib only.

  eng-os-usage.py [--since YYYY-MM-DD] [--project SUBSTR] [--json] [--top N]
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys

PROJECTS = os.path.expanduser("~/.claude/projects")
GUARD_MARK = "[eng-os guard]"
REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TICKED = re.compile(r"`([a-z0-9-]+)`")


def eng_os_skills():
    """Names of the eng-os skills: from the repo when run there, else from the install manifest."""
    d = os.path.join(REPO, "global", "skills")
    if os.path.isdir(d):
        return set(os.listdir(d))
    try:
        with open(os.path.expanduser("~/.claude/eng-os/manifest.json")) as fh:
            files = json.load(fh).get("files") or {}
        return {f.split("/")[3] for f in files if f.startswith("~/.claude/skills/") and f.count("/") >= 4}
    except (OSError, ValueError):
        return set()


SKILLS = eng_os_skills()


def named_skills(texts):
    """eng-os skills that the session or prompt hooks named: on lines that start with "eng-os" or head a core-rules block."""
    found = set()
    for t in texts:
        for line in str(t).splitlines():
            line = line.strip()
            if line.startswith("eng-os") or line.endswith("core rules:"):
                found.update(n for n in TICKED.findall(line) if n in SKILLS)
    return found


def iter_records(path):
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            # cheap prefilter: skip record types we never use
            if '"assistant"' not in line and '"user"' not in line and "compact_boundary" not in line \
                    and "hook_additional_context" not in line:
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def tool_result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def analyze_file(path, since):
    s = {
        "file": path, "start": None, "version": None, "cwd": None,
        "requests": 0, "input": 0, "cache_create": 0, "cache_read": 0, "output": 0,
        "first_context": None, "max_context": 0, "models": collections.Counter(),
        "tools": collections.Counter(), "skills": collections.Counter(),
        "agents": collections.Counter(), "reads": collections.Counter(),
        "compactions": 0, "guard_blocks": 0, "tool_errors": 0,
        "named": set(), "loaded": set(),
        "uses": {}, "out_chars": collections.Counter(), "turns": 0, "turns_200k": 0, "turns_400k": 0,
    }
    seen = set()
    for o in iter_records(path):
        ts = o.get("timestamp")
        if ts and s["start"] is None:
            if since and ts[:10] < since:
                return None
            s["start"] = ts
            s["version"] = o.get("version")
            s["cwd"] = o.get("cwd")
        if o.get("subtype") == "compact_boundary":
            s["compactions"] += 1
            continue
        att = o.get("attachment") if o.get("type") == "attachment" else None
        if isinstance(att, dict):
            if att.get("type") == "hook_additional_context" and att.get("hookEvent") in ("SessionStart", "UserPromptSubmit"):
                c = att.get("content")
                s["named"] |= named_skills(c if isinstance(c, list) else [c])
            continue
        msg = o.get("message") or {}
        if o.get("type") == "assistant":
            mid = msg.get("id") or o.get("requestId")
            if mid and mid not in seen:
                seen.add(mid)
                u = msg.get("usage") or {}
                ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                s["requests"] += 1
                s["input"] += u.get("input_tokens", 0)
                s["cache_create"] += u.get("cache_creation_input_tokens", 0)
                s["cache_read"] += u.get("cache_read_input_tokens", 0)
                s["output"] += u.get("output_tokens", 0)
                s["max_context"] = max(s["max_context"], ctx)
                s["turns"] += 1
                s["turns_200k"] += ctx > 200000
                s["turns_400k"] += ctx > 400000
                if s["first_context"] is None and ctx:
                    s["first_context"] = ctx
                if msg.get("model"):
                    s["models"][msg["model"]] += 1
            for b in msg.get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name = b.get("name", "?")
                inp = b.get("input") or {}
                s["tools"][name] += 1
                s["uses"][b.get("id")] = name if not name.startswith("mcp__") else "mcp:" + name.split("__")[1][:20]
                if name == "Skill":
                    s["skills"][inp.get("skill", "?")] += 1
                    if inp.get("skill") in SKILLS:
                        s["loaded"].add(inp["skill"])
                elif name in ("Agent", "Task"):
                    s["agents"][inp.get("subagent_type", "general-purpose")] += 1
                elif name == "Read" and inp.get("file_path"):
                    s["reads"][inp["file_path"]] += 1
        elif o.get("type") == "user" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    s["out_chars"][s["uses"].get(b.get("tool_use_id"), "?")] += len(tool_result_text(b))
                    if b.get("is_error"):
                        s["tool_errors"] += 1
                    if GUARD_MARK in tool_result_text(b):
                        s["guard_blocks"] += 1
    if s["start"] is None:
        return None
    s["repeat_reads"] = sum(n - 1 for n in s["reads"].values() if n > 1)
    return s


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="only sessions starting on/after YYYY-MM-DD")
    ap.add_argument("--project", help="substring of the transcript project dir")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    mains, subs = [], []
    for proj in sorted(glob.glob(os.path.join(PROJECTS, "*"))):
        if a.project and a.project not in proj:
            continue
        mains += glob.glob(os.path.join(proj, "*.jsonl"))
        subs += glob.glob(os.path.join(proj, "*", "subagents", "*.jsonl"))

    sessions = [x for x in (analyze_file(p, a.since) for p in mains) if x and x["requests"]]
    agents = [x for x in (analyze_file(p, a.since) for p in subs) if x and x["requests"]]
    if not sessions:
        print("no sessions found", file=sys.stderr)
        return 1

    def total(rows, k):
        return sum(r[k] for r in rows)

    def agg(rows, k):
        c = collections.Counter()
        for r in rows:
            c.update(r[k])
        return c

    billed_in = lambda rows: total(rows, "input") + total(rows, "cache_create") + total(rows, "cache_read")
    first = [r["first_context"] for r in sessions if r["first_context"]]
    out = {
        "sessions": len(sessions),
        "date_range": [min(r["start"] for r in sessions)[:10], max(r["start"] for r in sessions)[:10]],
        "versions": agg([{"v": collections.Counter([r["version"]])} for r in sessions], "v").most_common(5),
        "main": {
            "requests": total(sessions, "requests"),
            "input_tokens_total": billed_in(sessions),
            "output_tokens": total(sessions, "output"),
            "cache_read_pct": round(pct(total(sessions, "cache_read"), billed_in(sessions)), 1),
            "baseline_context_median": int(statistics.median(first)) if first else 0,
            "baseline_context_p90": int(sorted(first)[int(len(first) * 0.9) - 1]) if first else 0,
            "max_context_median": int(statistics.median([r["max_context"] for r in sessions])),
            "compactions": total(sessions, "compactions"),
            "repeat_reads": total(sessions, "repeat_reads"),
            "reads": sum(agg(sessions, "tools")[t] for t in ("Read",)),
            "tool_errors": total(sessions, "tool_errors"),
            "guard_blocks": total(sessions, "guard_blocks"),
        },
        "subagents": {
            "runs": len(agents),
            "input_tokens_total": billed_in(agents) if agents else 0,
            "output_tokens": total(agents, "output") if agents else 0,
            "share_of_all_input_pct": round(pct(billed_in(agents), billed_in(agents) + billed_in(sessions)), 1) if agents else 0,
            "models": agg(agents, "models").most_common(5),
        },
        "models_main": agg(sessions, "models").most_common(6),
        "tools": agg(sessions, "tools").most_common(a.top),
        "skills": agg(sessions + agents, "skills").most_common(a.top),
        "agent_types": agg(sessions, "agents").most_common(a.top),
        "routing": routing(sessions),
        "tool_output": [(k, round(pct(v, sum(agg(sessions, "out_chars").values())), 1))
                        for k, v in agg(sessions, "out_chars").most_common(6)],
        "turns_over_200k_pct": round(pct(total(sessions, "turns_200k"), total(sessions, "turns")), 1),
        "turns_over_400k_pct": round(pct(total(sessions, "turns_400k"), total(sessions, "turns")), 1),
    }
    if a.json:
        print(json.dumps(out, indent=1, default=str))
        return 0
    m, sa = out["main"], out["subagents"]
    print("eng-os usage  sessions=%d  %s..%s" % (out["sessions"], *out["date_range"]))
    print("versions: %s" % ", ".join("%s(%d)" % v for v in out["versions"]))
    print("MAIN  requests=%d  input=%.1fM  output=%.2fM  cache_read=%.1f%%" % (
        m["requests"], m["input_tokens_total"] / 1e6, m["output_tokens"] / 1e6, m["cache_read_pct"]))
    print("      baseline context at turn 1: median=%d p90=%d tokens; peak context median=%d" % (
        m["baseline_context_median"], m["baseline_context_p90"], m["max_context_median"]))
    print("      compactions=%d  Read calls=%d  repeated reads=%d (%.0f%%)  tool errors=%d  guard blocks=%d" % (
        m["compactions"], m["reads"], m["repeat_reads"], pct(m["repeat_reads"], m["reads"]), m["tool_errors"], m["guard_blocks"]))
    print("SUBAGENTS runs=%d input=%.1fM output=%.2fM (%.1f%% of all input)  models=%s" % (
        sa["runs"], sa["input_tokens_total"] / 1e6, sa["output_tokens"] / 1e6, sa["share_of_all_input_pct"],
        ", ".join("%s:%d" % x for x in sa["models"])))
    for k in ("models_main", "tools", "skills", "agent_types"):
        print("%-11s %s" % (k, ", ".join("%s:%d" % x for x in out[k]) or "-"))
    print("where tokens go: tool output by tool %s; turns with context over 200k: %.0f%%, over 400k: %.0f%%" % (
        ", ".join("%s %.0f%%" % x for x in out["tool_output"]) or "-", out["turns_over_200k_pct"], out["turns_over_400k_pct"]))
    r = out["routing"]
    print("routing     eng-os skills named in %d sessions; named and loaded in the same session: %d of %d (%.0f%%)%s" % (
        r["sessions_named"], r["loaded"], r["named"], pct(r["loaded"], r["named"]),
        ("  per skill: " + ", ".join("%s %d/%d" % (k, v[1], v[0]) for k, v in r["per_skill"])) if r["per_skill"] else ""))
    return 0


def routing(sessions):
    """How often a skill the hooks named in a session was then loaded with the Skill tool in that same session."""
    per = collections.defaultdict(lambda: [0, 0])
    for r in sessions:
        for k in r["named"]:
            per[k][0] += 1
            per[k][1] += k in r["loaded"]
    named = sum(v[0] for v in per.values())
    return {"sessions_named": sum(1 for r in sessions if r["named"]), "named": named,
            "loaded": sum(v[1] for v in per.values()),
            "per_skill": sorted(per.items(), key=lambda kv: -kv[1][0])}


if __name__ == "__main__":
    sys.exit(main())
