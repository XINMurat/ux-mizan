#!/usr/bin/env python3
"""Record which rules block a commit, so rule health has data.

Rule health counted rules on the family's git history and found nothing: a
violation is fixed before the push, so it never reaches git. The one place a
rule demonstrably does its job is the pre-commit hook that blocks. This
records those blocks.

    log VALIDATOR FILE   called by tools/hooks/pre-commit when a validator
                         fails: re-runs it with --format json and appends the
                         rule codes to .git/rule-hits.jsonl. Never fails the
                         hook; logging is not a gate.
    summary              counts per rule code from the local log.
    export               writes counts only (no file names, no messages) to
                         rule-hits/<date>-<id>.json for you to commit; the site's
                         daily rule-health report reads that directory in all
                         four repositories.

The local log stays in .git and is never pushed. Only what `export` writes is
shared, and only when you commit it.
"""
from __future__ import annotations

import collections
import datetime
import json
import os
import subprocess
import sys
import uuid


def git_dir() -> str:
    return subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True,
                          text=True, check=True).stdout.strip()


def log_path() -> str:
    return os.path.join(git_dir(), "rule-hits.jsonl")


def read_log() -> list[dict]:
    try:
        return [json.loads(l) for l in open(log_path(), encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        return []


def cmd_log(validator: str, path: str) -> int:
    try:
        out = subprocess.run([sys.executable, validator, "--format", "json", path],
                             capture_output=True, text=True, timeout=120)
        try:
            res = json.loads(out.stdout)
        except json.JSONDecodeError:
            # exit 2: the file did not parse or is not this validator's kind.
            # That blocked the commit too, so it is counted, under PARSE.
            res = {"violations": [{"code": "PARSE"}]}
        rec = {"date": datetime.date.today().isoformat(),
               "validator": os.path.basename(validator),
               "violations": sorted({f["code"] for f in res.get("violations", []) if f.get("code")}),
               "warnings": sorted({f["code"] for f in res.get("warnings", []) if f.get("code")})}
        with open(log_path(), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception as exc:  # logging must never block a commit
        sys.stderr.write(f"rule-hits: not logged ({exc})\n")
    return 0


def counts(recs: list[dict]) -> dict:
    v, w = collections.Counter(), collections.Counter()
    for r in recs:
        v.update(r.get("violations", []))
        w.update(r.get("warnings", []))
    return {"blocks": len(recs), "violations": dict(v), "warnings": dict(w)}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("log", "summary", "export"):
        print(__doc__)
        return 2
    if argv[0] == "log":
        if len(argv) != 3:
            print("usage: rule_hits.py log VALIDATOR FILE", file=sys.stderr)
            return 2
        return cmd_log(argv[1], argv[2])
    recs = read_log()
    c = counts(recs)
    if argv[0] == "summary":
        print(json.dumps(c, indent=2))
        return 0
    if not recs:
        print("rule-hits: nothing logged yet; nothing to export")
        return 0
    dates = sorted(r["date"] for r in recs)
    c.update({"from": dates[0], "to": dates[-1]})
    os.makedirs("rule-hits", exist_ok=True)
    out = os.path.join("rule-hits", f"{dates[-1]}-{uuid.uuid4().hex[:8]}.json")
    json.dump(c, open(out, "w", encoding="utf-8"), indent=2)
    open(log_path(), "w").close()  # exported records are not exported twice
    print(f"rule-hits: {c['blocks']} blocked commit(s) -> {out}; commit that file")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
