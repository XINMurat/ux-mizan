#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Per-flow lostness (Smith, 1996) from a screen-visit log.

    L = sqrt( (N/S - 1)^2 + (R/N - 1)^2 )

    N = distinct screens visited during the task
    S = total screens visited, repeats included
    R = minimum screens needed to complete it (canonical_path_R)

WHAT THIS SCRIPT IS AND IS NOT
------------------------------
This is the bridge that answers "a log cannot measure being lost": it can,
but ONLY if the flow declared its goal and its R in advance. R comes from
the registry, which was locked at Gate 0/1 before any data arrived. R
inferred from the data afterwards is HARKing, so this script refuses to
guess it.

Four caveats travel with every number it prints, and they are printed with
the number rather than filed in a doc nobody opens:
  (a) valid only for navigational app types -- on a single-canvas tool the
      metric is switched off by the schema's metric matrix;
  (b) L says WHERE, never WHY -- read it beside rage/dead-click/backtrack;
  (c) it is per-flow and local, never a global app score;
  (d) Smith's 0.4/0.5 cut-offs come from hypertext studies and are not
      validated for your app type -- compare against your own baseline.

INPUT (JSONL, one event per line; extra keys are ignored):
    {"session_id": "s1", "flow_id": "F-001", "screen": "/cart", "ts": 1}
Sessions that never reach the flow's success screen are reported
separately: an abandoned session has no completion path, and averaging it
into L silently mixes "wandered" with "gave up".

USAGE
    python lostness.py events.jsonl --registry ux-registry.yaml
    python lostness.py events.jsonl --registry ux-registry.yaml --flow F-001
    python lostness.py events.jsonl --flow F-001 --R 4 --success /done

Exit code 0 = computed, 2 = usage/parse error.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict, defaultdict

NAVIGATIONAL = {"navigational-multiscreen", "b2b-internal-dashboard"}


def lostness(n_distinct: int, s_total: int, r_minimum: int) -> float | None:
    """Return L, or None when the inputs make it undefined.

    L is bounded 0-1 only while R <= N <= S, i.e. for a session that could
    actually have completed the task. A session that visited FEWER distinct
    screens than the canonical path has no completion to be lost on the way
    to; the formula still returns a number there, and that number is not
    lostness -- it is an artifact of dividing by a too-small N. Returning
    None instead is the honest answer: those sessions belong in the
    abandoned bucket, counted, not averaged.
    """
    if n_distinct <= 0 or s_total <= 0 or r_minimum <= 0:
        return None
    if r_minimum > n_distinct or n_distinct > s_total:
        return None
    return math.sqrt((n_distinct / s_total - 1) ** 2 + (r_minimum / n_distinct - 1) ** 2)


def load_flow(registry_path: str, flow_id: str | None) -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("ERROR: PyYAML is required to read a registry. pip install pyyaml")
    with open(registry_path, encoding="utf-8") as handle:
        reg = yaml.safe_load(handle) or {}
    flows = [f for f in (reg.get("flows") or []) if isinstance(f, dict)]
    if flow_id:
        flows = [f for f in flows if f.get("flow_id") == flow_id]
    if not flows:
        sys.exit(f"ERROR: no flow {flow_id or ''} found in {registry_path}")
    return flows[0] if flow_id else flows


def read_events(path: str) -> dict[tuple[str, str], list[str]]:
    """-> {(flow_id, session_id): [screen, screen, ...]} in arrival order."""
    sessions: dict[tuple[str, str], list[str]] = defaultdict(list)
    with open(path, encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as err:
                sys.exit(f"ERROR: {path}:{line_no} is not valid JSON -- {err}")
            key = (str(event.get("flow_id")), str(event.get("session_id")))
            sessions[key].append(str(event.get("screen")))
    return sessions


def report_flow(flow: dict, sessions: dict, args) -> None:
    flow_id = flow.get("flow_id")
    app_type = flow.get("app_type")
    r_minimum = args.R or flow.get("canonical_path_R")
    # success_definition is prose for humans; success_screen is the
    # machine-matchable one. Matching against the prose silently files every
    # session as abandoned, which reads exactly like a catastrophic flow.
    success = args.success or flow.get("success_screen")

    print(f"\n=== {flow_id} -- {flow.get('task_name', '')} ===")
    if app_type not in NAVIGATIONAL:
        print(f"  SKIPPED: app_type '{app_type}' does not switch lostness on "
              f"(caveat a). A high revisit count here is work, not wandering.")
        return
    if not r_minimum:
        print("  SKIPPED: canonical_path_R is not declared. R inferred after "
              "the fact is HARKing; lock it at Gate 1 and re-run.")
        return

    if not success:
        print("  WARNING: this flow declares no success_screen, so completed "
              "and abandoned sessions cannot be told apart. Everything below "
              "is reported as one undifferentiated bucket -- add "
              "success_screen to the flow and re-run.")

    completed, abandoned = [], []
    for (fid, session_id), screens in sessions.items():
        if fid != flow_id:
            continue
        reached = any(str(success) in screen for screen in screens) if success else True
        n_distinct = len(OrderedDict.fromkeys(screens))
        value = lostness(n_distinct, len(screens), int(r_minimum))
        row = (session_id, n_distinct, len(screens), value)
        (completed if reached else abandoned).append(row)

    if not completed and not abandoned:
        print("  no sessions matched this flow.")
        return

    for label, rows in (("completed", completed), ("abandoned", abandoned)):
        if not rows:
            continue
        values = [r[3] for r in rows if r[3] is not None]
        mean = f"{sum(values) / len(values):.3f}" if values else "n/a"
        undefined = len(rows) - len(values)
        print(f"  {label}: n={len(rows)}  mean L={mean}"
              + (f"  ({undefined} undefined: fewer distinct screens than R)"
                 if undefined else ""))
        for session_id, n_distinct, s_total, value in rows:
            shown = f"{value:.3f}" if value is not None else "undefined"
            print(f"    {session_id}: N={n_distinct} S={s_total} "
                  f"R={r_minimum} L={shown}")
    if abandoned:
        print("  NOTE: abandoned sessions are reported apart from completed "
              "ones. Averaging them together mixes 'wandered' with 'gave up'.")

    baseline = (flow.get("baseline") or {}).get("values") or {}
    if "lostness" in baseline:
        print(f"  baseline L for this flow: {baseline['lostness']} "
              f"(compare against THIS, not against 0.4/0.5 -- caveat d).")
    else:
        print("  no baseline L recorded for this flow -- the number above is "
              "not yet interpretable (caveat d).")
    print("  L says WHERE, not WHY (caveat b): read it beside rage-click, "
          "dead-click and backtrack rates.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-flow lostness (Smith, 1996)")
    parser.add_argument("events", help="JSONL screen-visit log")
    parser.add_argument("--registry", help="ux-registry.yaml supplying R and baseline")
    parser.add_argument("--flow", help="restrict to one flow_id")
    parser.add_argument("--R", type=int, help="canonical minimum screens (overrides registry)")
    parser.add_argument("--success", help="substring marking the success screen")
    args = parser.parse_args()

    sessions = read_events(args.events)

    if args.registry:
        flows = load_flow(args.registry, args.flow)
        flows = flows if isinstance(flows, list) else [flows]
    elif args.flow and args.R:
        flows = [{"flow_id": args.flow, "app_type": "navigational-multiscreen",
                  "canonical_path_R": args.R, "task_name": "(ad hoc)"}]
    else:
        sys.exit("ERROR: pass --registry, or --flow with --R.")

    for flow in flows:
        report_flow(flow, sessions, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
