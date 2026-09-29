#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Each validator's vocabulary must match tools/family-vocabulary.yaml.

The tier and class sets live as constants in four validators. Nothing tied
them together, and one had drifted: ux-mizan offered `status: parked` in its
schema and in its own U12 message while its validator refused it. This reads
the constants from source (no import, so no validator side effects) and
compares them, as sets, with the shared vocabulary. Only the files present in
this repository are checked; a repository with none of them is an error, since
an empty check is not a pass.

Usage:  python tools/check_vocabulary.py      # exit 0 ok, 1 drift, 2 usage
"""
from __future__ import annotations

import ast
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB = os.path.join(ROOT, "tools", "family-vocabulary.yaml")

# (file, constant, vocabulary key)
BINDINGS = [
    ("tools/mizan_validate.py", "VALID_TIERS", "evidence_tiers"),
    ("tools/mizan_validate.py", "ARBITER_CLASSES", "arbiter_classes"),
    ("tools/kiyas_validate.py", "VALID_TIERS", "seed_tiers"),
    ("tools/kiyas_validate.py", "ARBITER_CLASSES", "arbiter_classes"),
    ("skill/iskele/scripts/kiyas_to_backlog.py", "EXECUTABLE_ARBITERS", "executable_arbiters"),
    ("skill/ux-mizan/scripts/ux_validate.py", "VALID_TIERS", "evidence_tiers"),
    ("skill/ux-mizan/scripts/ux_validate.py", "VALID_STATUS", "ux_finding_statuses"),
    ("skill/ux-mizan/scripts/ux_validate.py", "VALID_KKE_KINDS", "kke_kinds"),
    ("skill/ux-mizan/scripts/ux_validate.py", "VALID_METRIC_KINDS", "ux_metric_kinds"),
    ("skill/ux-mizan/scripts/ux_validate.py", "VALID_PROVENANCE", "ux_provenance"),
]


def constant(path: str, name: str):
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return set(ast.literal_eval(node.value))
    return None


def main() -> int:
    vocab = yaml.safe_load(open(VOCAB, encoding="utf-8"))
    checked, bad = 0, 0
    for rel, name, key in BINDINGS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        got, want = constant(path, name), set(vocab[key])
        checked += 1
        if got is None:
            print(f"DRIFT {rel}: constant {name} not found (bound to '{key}')")
            bad += 1
        elif got != want:
            print(f"DRIFT {rel}: {name} != {key}; "
                  f"missing {sorted(want - got)}, extra {sorted(got - want)}")
            bad += 1
    if not checked:
        print("ERROR: none of the bound validator files exist here")
        return 2
    print(f"{'FAIL' if bad else 'ok'}  {checked} vocabulary binding(s), {bad} drifted")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
