#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-file consistency: what is repeated across screens, and where it diverges.

WHY THIS EXISTS
---------------
The other two scripts in this skill each look at ONE file. `structural_checks`
asks what a view is missing; `layout_signals` asks how one screen is arranged.
Neither can see the thing that only exists BETWEEN screens: the same control
built five different ways, forty-seven distinct greys, a "modal" that is a
Dialog here, a Sheet there and an Overlay in the third place.

That gap is not cosmetic. A user learns an interface once per pattern, not once
per app -- so an app with six button idioms charges the learning cost six
times. The cost is real; its SIZE is not something a file can tell you, which
is why every signal here ships with the metric that would settle it.

THE TRAP THIS SCRIPT IS BUILT AROUND
------------------------------------
This skill's own risk #1 is recursive homogenisation: a tool that recommends
"standardise your components" is one step from recommending the generic
default everyone else already uses. So every signal below measures INTERNAL
consistency -- does this app agree with itself? -- and none of them compares
the app to an external norm.

  Finding:      these seven buttons differ, and nothing explains why.
  NOT a finding: these buttons do not look like everyone else's buttons.

The second sentence is taste wearing a lab coat. If a divergence turns out to
be deliberate -- a destructive action that SHOULD look unlike the others -- it
is not a defect, and the report cannot tell the difference. A human can.

SIGNALS
  K1 value-dispersion      how many distinct raw values per visual dimension,
                           and how many are used exactly once
  K2 role-divergence       the same interactive role built from different
                           primitives (button / div+onClick / a+onClick)
  K5 local-one-off         a component defined inside a page and used once

TWO SIGNALS ARE DELIBERATELY ABSENT
-----------------------------------
Both were written, both were run against a real 89-file app, and both
over-reported badly enough to be worth removing rather than shipping. The
reasons are here so the next person does not rebuild the naive versions:

  concept-divergence -- "how many names does this app have for a modal?"
  The draft counted every exported name, so `DialogContent`, `DialogHeader`
  and `DialogTrigger` read as three competing modals when they are one
  primitive's parts. Stripping sub-part suffixes got 43 names down to 15, and
  the remaining 15 were still wrong: `AnonymizeDialog` and `PasswordDialog`
  are INSTANCES built on the Dialog primitive, not rivals to it. The signal
  needs a primitive/instance distinction -- plausibly "a component that
  imports another component of the same concept is an instance" -- and until
  that is built and tested, the check reports healthy reuse as a defect.

  near-duplicate-defs -- "which component definitions are copies?"
  The draft's shape signature was the set of JSX tags in the FILE, so every
  component in a multi-component file matched every other. It produced 32
  signals on an app with no obvious duplication. A real version needs the
  JSX subtree and prop set per definition, not per file.

A check that over-reports teaches people to ignore it, and an ignored check
is worse than an absent one because it still looks like coverage.

USAGE
    python component_inventory.py path/to/src
    python component_inventory.py path/to/src --json
    python component_inventory.py path/to/src --top 12
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

SOURCE_EXT = {".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte"}
STYLE_EXT = {".css", ".scss", ".less"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage",
             "__pycache__", ".claude", ".turbo"}

# --- K1: what counts as a raw visual value --------------------------------
# Tokens (var(--x), theme.x, tailwind classes) are deliberately NOT counted:
# the question is how many values escaped the scale, not how many exist.
RE_HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RE_RGB = re.compile(r"\b(?:rgba?|hsla?)\([^)]*\)")
RE_SPACE = re.compile(
    r"\b(?:margin|padding|gap|top|left|right|bottom)[a-zA-Z-]*\s*:\s*([^;{}\n]+)")
RE_FONT = re.compile(r"\bfont-size\s*:\s*([^;{}\n]+)")
RE_RADIUS = re.compile(r"\bborder-radius\s*:\s*([^;{}\n]+)")
RE_LEN = re.compile(r"-?\d*\.?\d+(?:px|rem|em)")

# --- K2/K4/K5: component and element shapes -------------------------------
RE_DIV_CLICK = re.compile(r"<(div|span|li|td)\b(?![^>]*\brole=)[^>]*\bonClick\b")
RE_A_CLICK = re.compile(r"<a\b(?![^>]*\bhref=)[^>]*\bonClick\b")
RE_BUTTON = re.compile(r"<button\b")
RE_COMPONENT_DEF = re.compile(
    r"(?:export\s+)?(?:default\s+)?(?:function|const)\s+([A-Z][A-Za-z0-9_]*)\s*"
    r"(?:[:=]|\()")
RE_JSX_TAG = re.compile(r"<([A-Z][A-Za-z0-9_]*)\b")
RE_IMPORT = re.compile(r"import\s+(?:\{([^}]*)\}|(\w+))\s+from\s+['\"]([^'\"]+)['\"]")

# --- K3: concepts that attract several names ------------------------------
# Each row is one concept. A codebase using two names from the same row is
# saying two things where it means one -- and the reader has to learn both.
HYPOTHESIS = {
    "K1": (
        "{dim}: {distinct} distinct values, {singletons} of them used once. A "
        "scale has steps; a list this long is not a scale, and every value "
        "used once is a decision nobody can reuse.",
        "visual-consistency rating, or first-click accuracy on the Nth screen",
        "measure first-click on a task in a screen the user has NOT seen, "
        "after they have used 3+ others; a learned interface should transfer",
    ),
    "K2": (
        "the same interactive role is built {ways} different ways ({detail}). "
        "Keyboard and screen-reader behaviour differ per idiom even when the "
        "pixels match.",
        "keyboard task success, and rage/dead clicks on the non-button idioms",
        "run the flow with a keyboard only; a div+onClick is unreachable by "
        "Tab and a dead click for anyone who cannot use a mouse",
    ),
    "K5": (
        "{n} components are defined inside a page file and used exactly once. "
        "Not wrong on its own; the number rising over time is the signal that "
        "the shared layer stopped being reached for.",
        "the trend, not the level -- re-run this after the next feature",
        "compare this count between two releases; a rising one-off count with "
        "a static shared inventory is the kit being abandoned in practice",
    ),
}


def iter_files(root: str, exts: set[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if os.path.splitext(name)[1] in exts:
                yield os.path.join(dirpath, name)


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def normalise_len(raw: str) -> list[str]:
    """The length values in a declaration, minus the ones that are structural.

    0, 1px borders, 100% and `auto` are not design decisions, so counting them
    would inflate every codebase equally and make the number useless.
    """
    out = []
    for tok in RE_LEN.findall(raw):
        if tok in ("0px", "0rem", "0em", "1px", "-1px"):
            continue
        out.append(tok)
    return out


def collect_values(root: str) -> dict:
    dims = {"colour": collections.Counter(), "spacing": collections.Counter(),
            "font-size": collections.Counter(), "radius": collections.Counter()}
    for path in list(iter_files(root, SOURCE_EXT)) + list(iter_files(root, STYLE_EXT)):
        text = read(path)
        for m in RE_HEX.findall(text):
            dims["colour"][m.lower()] += 1
        for m in RE_RGB.findall(text):
            # `hsl(var(--primary))` is the CORRECT thing to find: a token being
            # used. The first run counted it as a raw value and reported a
            # codebase with a working scale as having forty loose colours --
            # the check inverted its own signal.
            if "var(--" in m or "theme(" in m:
                continue
            dims["colour"][re.sub(r"\s+", "", m.lower())] += 1
        for raw in RE_SPACE.findall(text):
            for tok in normalise_len(raw):
                dims["spacing"][tok] += 1
        for raw in RE_FONT.findall(text):
            for tok in normalise_len(raw):
                dims["font-size"][tok] += 1
        for raw in RE_RADIUS.findall(text):
            for tok in normalise_len(raw):
                dims["radius"][tok] += 1
    return dims


def collect_components(root: str) -> dict:
    defs: dict[str, list[str]] = collections.defaultdict(list)
    usage: collections.Counter = collections.Counter()
    roles = {"button": 0, "div+onClick": 0, "a+onClick": 0}
    role_sites: dict[str, list[str]] = collections.defaultdict(list)
    one_offs: list[tuple[str, str]] = []

    for path in iter_files(root, SOURCE_EXT):
        text = read(path)
        rel = os.path.relpath(path, root)

        roles["button"] += len(RE_BUTTON.findall(text))
        for m in RE_DIV_CLICK.finditer(text):
            roles["div+onClick"] += 1
            role_sites["div+onClick"].append(f"{rel}:{text[:m.start()].count(chr(10)) + 1}")
        for m in RE_A_CLICK.finditer(text):
            roles["a+onClick"] += 1
            role_sites["a+onClick"].append(f"{rel}:{text[:m.start()].count(chr(10)) + 1}")
        if roles["button"]:
            role_sites.setdefault("button", []).append(rel)

        local_defs = set(RE_COMPONENT_DEF.findall(text))
        for name in local_defs:
            defs[name].append(rel)

        for tag in RE_JSX_TAG.findall(text):
            usage[tag] += 1

        # K5: defined in something that looks like a page, used once here.
        if re.search(r"(pages?|routes?|screens?|views?|features?)[/\\]", rel.replace(os.sep, "/")):
            for name in local_defs:
                if len(re.findall(r"<" + re.escape(name) + r"\b", text)) == 1:
                    one_offs.append((name, rel))

    return dict(defs=defs, usage=usage, roles=roles,
                role_sites=role_sites, one_offs=one_offs)


def analyse(root: str, top: int) -> dict:
    dims = collect_values(root)
    comp = collect_components(root)

    k1 = []
    for dim, counter in dims.items():
        if not counter:
            continue
        singles = sum(1 for v in counter.values() if v == 1)
        k1.append(dict(dim=dim, distinct=len(counter), singletons=singles,
                       examples=[v for v, _ in counter.most_common(top)]))

    used_roles = {k: v for k, v in comp["roles"].items() if v}
    k2 = []
    if len(used_roles) > 1:
        k2.append(dict(ways=len(used_roles),
                       detail=", ".join(f"{k} x{v}" for k, v in sorted(used_roles.items())),
                       sites=comp["role_sites"]))

    k5 = []
    if comp["one_offs"]:
        k5.append(dict(n=len(comp["one_offs"]),
                       members=[f"{n} ({f})" for n, f in comp["one_offs"][:top]]))

    return dict(K1=k1, K2=k2, K5=k5,
                totals=dict(components=len(comp["defs"]),
                            files_with_defs=len({f for v in comp["defs"].values() for f in v})))


def print_report(res: dict, root: str, top: int) -> None:
    print(f"Component inventory -- {root}")
    print("Cross-file consistency. Every count below is [KKE]: it names a place")
    print("to look, never a defect. The [H] line under each is what it MIGHT")
    print("cost a user, and only the named metric can settle that.")
    print("")
    print("This measures whether the app agrees with ITSELF. It does not")
    print("compare the app to any external design system, and a divergence")
    print("that is deliberate -- a destructive action that should look unlike")
    print("the rest -- reads here exactly like one that is not. Only a human")
    print("can tell those apart.\n")

    t = res["totals"]
    print(f"  {t['components']} component definitions across {t['files_with_defs']} files\n")

    any_signal = False
    for key in ("K1", "K2", "K5"):
        items = res[key]
        if not items:
            continue
        any_signal = True
        template, metric, how = HYPOTHESIS[key]
        for item in items:
            if key == "K1":
                if item["distinct"] <= 12:
                    continue
                print(f"== K1 value-dispersion / {item['dim']}")
                print(f"   [KKE] {item['distinct']} distinct, "
                      f"{item['singletons']} used once")
                print(f"         most common: {', '.join(item['examples'][:8])}")
            elif key == "K2":
                print("== K2 role-divergence")
                print(f"   [KKE] {item['detail']}")
                for role, sites in item["sites"].items():
                    if role != "button" and sites:
                        print(f"         {role}: {', '.join(sites[:4])}"
                              + (f" ... +{len(sites) - 4}" if len(sites) > 4 else ""))
            elif key == "K5":
                print("== K5 local-one-off")
                print(f"   [KKE] {item['n']} components defined in a page and "
                      f"used exactly once")
                print(f"         {', '.join(item['members'][:6])}")
            print(f"   [H]   {template.format(**item)}")
            print(f"   metric: {metric}")
            print(f"   decide it by: {how}\n")

    if not any_signal:
        print("  No signals. That is not a clean bill of health -- this script")
        print("  looks for three cross-file shapes and is blind to the rest;")
        print("  two more were written, over-reported on a real app, and were")
        print("  removed rather than shipped. See the header.")
        return

    print("Next: a signal becomes a finding only after it is attached to a flow")
    print("(parent_flow_id is mandatory) and given a threshold BEFORE the")
    print("measurement. And any fix proposed from these must answer the")
    print("homogenisation question in writing -- U10 -- because 'make them all")
    print("the same' is the move this skill is most likely to get wrong.")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(
        description="Cross-file component and value consistency traces")
    ap.add_argument("root", help="source directory to scan")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args()

    if not os.path.isdir(a.root):
        print(f"not a directory: {a.root}", file=sys.stderr)
        return 2

    res = analyse(a.root, a.top)
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print_report(res, a.root, a.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
