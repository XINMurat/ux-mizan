#!/usr/bin/env python3
"""Do the rules overlap or contradict each other? A pair test, no field data.

Rules only accumulate, and each new one is checked alone. Two failure modes
appear only in pairs:

  overlap   one defect is reported by two rules. Harmless for one run, but
            the two rules then evolve separately and drift apart.
  conflict  no registry can satisfy both rules at once. The first time a
            user meets it, fixing one violation creates the other.

Method. A BASE registry that is clean under every rule proves that all the
rules it exercises can be satisfied together (no conflict among them, on
this base). Each MUTATION then breaks exactly one thing; the finding codes it
fires are compared to the one it was written for:

  isolated  fires exactly its target: that rule does not overlap here
  overlap   fires its target and others: listed as pairs
  silent    fires nothing / not the target: the fixture or the rule is broken

Codes come from the message catalog key (R8_no_who, not just R8), so two
checks inside one rule number are told apart. Findings are gathered by
running the validator's own main() on each mutated file, with its catalog
lookup recorded. A shared tool, identical in all four repositories; the
three with a validator keep their fixtures in tests/rule-pairs/ and run it
in CI (Iskele has no validator and nothing to run it on).

The lock file freezes the fired set of every mutation. CI fails when a
mutation's fired set changes (a new overlap appeared, or a rule stopped
firing) or a catalog code is neither covered nor listed as uncovered, so a
new rule arrives with its fixture or with a stated reason it has none.

Usage:
    python tools/rule_pairs.py            # report, exit 1 on drift
    python tools/rule_pairs.py --update   # rewrite the lock after a reviewed change
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import inspect
import io
import json
import os
import re
import sys
import tempfile

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "rule-pairs", "mutations.yaml")
LOCK = os.path.join(ROOT, "tests", "rule-pairs", "rule-pairs.lock.json")


class Validator:
    """The repository's own validator, driven through its command line.

    The fixture file names it (`validator`), the arguments every run gets
    (`args`, `{file}` is the registry), the catalog-key pattern (`codes`), and
    for append-only rules the function that reads the git baseline
    (`baseline_loader`), which is replaced by one returning the base. This
    file therefore has no per-repository code and is shared byte for byte.
    """

    def __init__(self, spec: dict):
        path = os.path.join(ROOT, spec["validator"])
        sys.path.insert(0, os.path.dirname(path))
        mspec = importlib.util.spec_from_file_location("_rule_pairs_validator", path)
        self.mod = importlib.util.module_from_spec(mspec)
        mspec.loader.exec_module(self.mod)
        self.args = spec.get("args") or ["{file}"]
        self.code = re.compile(spec["codes"])
        self.loader = spec.get("baseline_loader")
        self.dir = os.path.dirname(os.path.join(ROOT, spec["base"]))

    def catalog(self) -> list[str]:
        return sorted(k for k in self.mod.MSG if self.code.match(k))

    def run(self, data: dict, baseline: dict | None = None, extra: list | None = None) -> list[str]:
        fired: list[str] = []
        mod, orig = self.mod, self.mod.m

        def spy(key, lang, **kw):
            if self.code.match(key):
                fired.append(key)
            return orig(key, lang, **kw)

        # next to the base, so paths the registry names relative to itself resolve
        fd, tmp = tempfile.mkstemp(suffix=".yaml", dir=self.dir)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
        argv = [a.replace("{file}", tmp) for a in self.args] + list(extra or [])
        saved = {}
        if baseline is not None:
            saved[self.loader] = getattr(mod, self.loader)
            setattr(mod, self.loader, lambda *a, **k: copy.deepcopy(baseline))
            argv += ["--against", "HEAD"]
        mod.m = spy
        old_argv = sys.argv
        sys.argv = [mod.__file__] + argv
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    if inspect.signature(mod.main).parameters:
                        mod.main(argv)
                    else:
                        mod.main()  # a main() that reads sys.argv itself
                except SystemExit:
                    pass
        finally:
            mod.m = orig
            sys.argv = old_argv
            for k, v in saved.items():
                setattr(mod, k, v)
            os.unlink(tmp)
        return sorted(set(fired))


def _walk(doc, path: str):
    # "features.0.cost_actual": a digit segment indexes a list
    parts = [int(p) if p.isdigit() else p for p in path.split(".")]
    node = doc
    for p in parts[:-1]:
        node = node[p]
    return node, parts[-1]


def mutate(base: dict, ops: list[dict]) -> dict:
    doc = copy.deepcopy(base)
    for op in ops:
        node, key = _walk(doc, op["path"])
        if "delete" in op:
            del node[key]
        elif "append" in op:
            node[key].append(copy.deepcopy(op["append"]))
        else:
            node[key] = copy.deepcopy(op["set"])
    return doc


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args(argv)

    spec = yaml.safe_load(open(FIXTURES, encoding="utf-8"))
    v = Validator(spec)
    raw = yaml.safe_load(open(os.path.join(ROOT, spec["base"]), encoding="utf-8"))
    base = mutate(raw, spec.get("base_ops") or [])
    base_fired = v.run(base)
    report: dict = {"base": spec["base"], "base_fired": base_fired, "mutations": {}}

    for mu in spec["mutations"]:
        doc = mutate(base, mu["ops"])
        bl = mutate(base, mu["baseline_ops"]) if "baseline_ops" in mu else None
        if mu.get("baseline_is_base"):
            bl = base
        fired = v.run(doc, bl, mu.get("args"))
        report["mutations"][mu["id"]] = {"target": mu["target"], "fired": fired}

    covered = {v["target"] for v in report["mutations"].values()}
    uncovered = spec.get("uncovered") or {}
    cat = v.catalog()
    unaccounted = [c for c in cat if c not in covered and c not in uncovered]

    iso, over, silent = [], [], []
    pairs: dict[str, list[str]] = {}
    for mid, r in report["mutations"].items():
        t, f = r["target"], r["fired"]
        if t not in f:
            silent.append(mid)
        elif f == [t]:
            iso.append(mid)
        else:
            over.append(mid)
            for o in f:
                if o != t:
                    pairs.setdefault(" + ".join(sorted([t, o])), []).append(mid)

    print(f"# Rule pairs — {len(cat)} catalog codes, {len(covered)} covered by a mutation, "
          f"{len(uncovered)} listed uncovered")
    print(f"base {spec['base']}: " + ("clean — every rule it exercises is satisfiable at once"
                                      if not base_fired else f"NOT clean: {base_fired}"))
    print(f"isolated {len(iso)} · overlap {len(over)} · silent {len(silent)}")
    for p, mids in sorted(pairs.items()):
        print(f"  overlap  {p}  ({', '.join(mids)})")
    for mid in silent:
        print(f"  silent   {mid}: target {report['mutations'][mid]['target']}, "
              f"fired {report['mutations'][mid]['fired'] or 'nothing'}")
    for c in unaccounted:
        print(f"  unaccounted  {c}: no mutation and no reason in 'uncovered'")

    locked = {k: v["fired"] for k, v in report["mutations"].items()}
    if args.update:
        json.dump({"base_fired": base_fired, "mutations": locked}, open(LOCK, "w", encoding="utf-8"),
                  indent=1, sort_keys=True)
        print(f"lock written: {os.path.relpath(LOCK, ROOT)}")
        return 0

    bad = bool(base_fired or silent or unaccounted)
    try:
        prev = json.load(open(LOCK, encoding="utf-8"))
    except FileNotFoundError:
        print("no lock file; run with --update after review")
        return 1
    for k in sorted(set(prev["mutations"]) | set(locked)):
        if prev["mutations"].get(k) != locked.get(k):
            bad = True
            print(f"  DRIFT  {k}: locked {prev['mutations'].get(k)} -> now {locked.get(k)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
