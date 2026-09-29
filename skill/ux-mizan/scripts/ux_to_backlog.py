#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ux_to_backlog.py — ux-registry findings -> Iskele backlog markdown.

A finding that never becomes work is an opinion with a severity score. This
turns the registry's findings into Iskele tasks, in the format Iskele's
`backlog_to_tracker.py` / `iskele_to_registry.py` already read.

TWO KINDS OF WORK, NOT ONE
--------------------------
* status `confirmed`  -> a FIX task. Its acceptance is the finding's own
  metric re-measured past `threshold_refute`: the fix is done when the
  measurement that confirmed the problem now says it is gone. The metric's
  instrument becomes the task's **Hakem:**, so Iskele gives it a runtime
  arbiter instead of self-report.
* status `open` / `instrumented`, tier H -> a MEASURE task. Fixing a finding
  nobody has measured is building on [H]; the task is to run the
  refutation condition first.
* everything else (tier S, refuted, parked) is listed in a comment block at
  the end — visible, not counted as effort. A refuted finding stays on
  record; it does not become work.

Tasks are ordered by the validator's severity, highest first. The estimate
is not guessed: every task gets (M) and a `<!-- TAHMIN: kalibresiz -->`
mark, because a UX finding says nothing about the cost of its fix.

Usage:
    python ux_to_backlog.py ux-registry.yaml --phase F2 --out ux-gorevler.md
    python ux_to_backlog.py ux-registry.yaml --start-no 7     # stdout

Exit 0 = tasks written, 1 = no finding became a task, 2 = usage/parse error.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("ERROR: PyYAML is required. pip install pyyaml\n")
    sys.exit(2)


def one_line(v) -> str:
    return " ".join(str(v or "").split())


def classify(f: dict) -> str:
    status = str(f.get("status") or "").lower()
    tier = str(f.get("tier") or "").upper()
    if status == "confirmed":
        return "fix"
    if status in {"open", "instrumented"} and tier in {"H", "KKE"}:
        return "measure"
    return "park"


def task_lines(f: dict, kind: str, tid: str) -> list[str]:
    m = f.get("metric") or {}
    fid = f.get("finding_id")
    where = one_line(f.get("location"))
    instrument = one_line(m.get("instrument"))
    if kind == "fix":
        title = f"{fid} duzelt: {one_line(f.get('principle'))} @ {where}"
        refute = one_line(m.get("threshold_refute"))
        kabul = (f"{m.get('name')} yeniden olculdugunde {refute} esigini gecer "
                 f"(bulgu artik gecerli degil)" if refute else
                 "EKSIK — bulgunun metric.threshold_refute alani yok")
    else:
        title = f"{fid} olc: {one_line(f.get('principle'))} @ {where}"
        kabul = one_line(f.get("refutation_condition")) or \
            "EKSIK — bulgunun refutation_condition alani yok"
    if instrument:
        kabul += f" **Hakem:** {instrument}"
    return [f"- [ ] **{tid}** (M) {title[:120]} **Bağ.:** —  <!-- TAHMIN: kalibresiz -->",
            f"  - *Kabul:* {kabul}",
            f"  - <!-- ux-mizan: {fid} · akis {f.get('parent_flow_id')} · "
            f"severity {f.get('severity')} · {one_line(f.get('mechanism'))[:100]} -->",
            ""]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="ux-registry findings -> Iskele backlog")
    ap.add_argument("registry", help="ux-registry.yaml")
    ap.add_argument("--phase", default="F2")
    ap.add_argument("--layer", default="FE")
    ap.add_argument("--start-no", type=int, default=1)
    ap.add_argument("--out", default=None, help="write here (default stdout)")
    a = ap.parse_args(argv)

    try:
        data = yaml.safe_load(Path(a.registry).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        sys.stderr.write(f"ERROR: cannot read {a.registry}: {exc}\n")
        return 2
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        sys.stderr.write(f"ERROR: {a.registry} has no findings list — not a ux-registry\n")
        return 2

    findings = [f for f in data["findings"] if isinstance(f, dict) and f.get("finding_id")]
    groups = {"fix": [], "measure": [], "park": []}
    for f in findings:
        groups[classify(f)].append(f)
    sev = lambda f: -float(f.get("severity") or 0)  # noqa: E731

    out = [f"### Epik {a.phase}.UX — ux-mizan bulgulari", ""]
    n = a.start_no
    for kind in ("fix", "measure"):
        for f in sorted(groups[kind], key=sev):
            out += task_lines(f, kind, f"{a.phase}-{a.layer}-{n:02d}")
            n += 1
    if groups["park"]:
        out.append("<!-- GOREV DEGIL — S, refuted veya parked bulgular; efora sayilmaz.")
        for f in groups["park"]:
            out.append(f"     [{f.get('tier')}/{f.get('status')}] {f.get('finding_id')} — "
                       f"{one_line(f.get('mechanism'))[:90]}")
        out += ["-->", ""]

    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    made = len(groups["fix"]) + len(groups["measure"])
    sys.stderr.write(f"{len(groups['fix'])} duzeltme · {len(groups['measure'])} olcum · "
                     f"{len(groups['park'])} park edildi\n")
    return 0 if made else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
