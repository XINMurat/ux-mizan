#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer-A structural checks for a React/TypeScript front end.

These are PROXIES. Every count this script prints is `[KKE]` by
construction: it reports a structural shape that is *associated* with
confusion, never confusion itself. A model reading a repo cannot measure
UX; it can only check heuristic conformance and build the measuring rig.
So the output is written as candidate findings that still need a Layer-B
metric before any of them can be promoted.

Regex over source, not a parser: it over-reports on unusual code and
under-reports on generated code. Treat the counts as a place to look,
and open the file before writing a finding -- `location` in the registry
demands a file and a line, and this script gives you both.

CHECKS
  state_coverage_ratio       async views that handle loading/empty/error
  feedback_gap_count         mutations with no visible response
  generic_label_count        "Click here", "Submit", "Detail", "Tikla"...
  nonsemantic_interactive    onClick on a div/span with no role
  nav_depth                  nested route segments deeper than 3
  orphan_pages               route files nothing links to

USAGE
    python structural_checks.py path/to/src
    python structural_checks.py path/to/src --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SOURCE_EXT = {".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "__pycache__"}

GENERIC_LABELS = {
    "click here", "click", "submit", "detail", "details", "more", "learn more",
    "ok", "go", "next", "continue", "here", "link", "button", "read more",
    "tikla", "tıkla", "detay", "gonder", "gönder", "devam", "buraya tikla",
    "buraya tıkla", "daha fazla", "git", "tamam",
}

# NOTE: no trailing \b on these patterns. An alternative that ends in a
# non-word character (`useEffect(`, `axios.`, `alert(`) can never be
# followed by a word boundary, so a trailing \b silently matches nothing.
# That is how the first self-validation run found this file reporting
# "1 async view" in an app with ten data-loading pages: a checker that
# under-reports is indistinguishable from a clean codebase.
RE_ASYNC_VIEW = re.compile(
    r"\b(?:useQuery|useSWR|createResource)\b|await\s+\w+\s*\(|\.then\s*\(|"
    r"axios\.|fetch\s*\(")
# Suffix/prefix tolerant on purpose: real code writes `loadingProcesses`
# and `processesError`, and a whole-word match on `error` reports a view
# that handles its error state as one that ignores it. Found the same way
# as the word-boundary bug above -- by running this file on a real app.
# A bare `useEffect(` is deliberately NOT an async view either: it made
# providers, a theme toggle and a use-mobile hook count in the
# denominator, dragging the ratio down with files that fetch nothing.
RE_LOADING = re.compile(r"\w*(?:[Ll]oading|[Pp]ending)\w*|Skeleton|Spinner")
RE_EMPTY = re.compile(r"\w*empty\w*|noResults|no_data|EmptyState", re.I)
RE_ERROR = re.compile(r"\w*[Ee]rror\w*|catch\s*\(|onError")
RE_MUTATION = re.compile(
    r"\buseMutation\b|fetch\s*\([^)]*method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)|"
    r"axios\.(?:post|put|patch|delete)\b|"
    # An AWAITED verb call is the mutation shape. Without the `await` this
    # also matched pure helpers like `deleteImpact(step, ...)`, which have
    # no user to give feedback to -- a false positive found on the first
    # self-validation run, in the same pass as the missing-match bug above.
    r"\bawait\s+(?:create|update|delete|save|publish|submit|remove)[A-Z]\w*\s*\(")
# Prefix matching, not whole-word: real codebases wrap these
# (`notifyDone`, `toastError`, `showSnackbar`). `\bnotify\b` misses
# `notifyDone` and reports a component that does give feedback as silent.
RE_FEEDBACK = re.compile(
    r"\b(?:toast|notify|notification|setStatus|snackbar|onSuccess|"
    r"invalidateQueries|Modal|sonner)\w*|alert\s*\(|confirm\s*\(|"
    # A redirect after a mutation IS a visible response. Counting it as a
    # gap flags working flows, and a checker that cries wolf gets muted.
    r"navigate\s*\(|router\.(?:push|replace)\s*\(", re.I)
RE_TEXT_NODE = re.compile(r">\s*([A-Za-zÇĞİÖŞÜçğıöşü][^<>{}\n]{0,40}?)\s*<")
RE_LABEL_PROP = re.compile(
    r"(?:aria-label|title|label|children)\s*=\s*[\"']([^\"']{1,40})[\"']")
RE_NONSEMANTIC = re.compile(r"<(div|span|li)\b(?![^>]*\brole=)[^>]*\bonClick\b")
RE_ROUTE_PATH = re.compile(r"path\s*[:=]\s*[\"'`]([^\"'`]+)[\"'`]")


def iter_sources(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] not in SOURCE_EXT:
                continue
            # Test files make claims about the UI; they are not the UI. A
            # mutation helper called inside a test has no user to give
            # feedback to, and counting it inflates every proxy here.
            if any(part in name for part in (".test.", ".spec.")):
                continue
            yield os.path.join(dirpath, name)


def scan(root: str) -> dict:
    hits: dict[str, list[dict]] = {
        "async_views": [], "state_covered": [], "feedback_gap": [],
        "generic_label": [], "nonsemantic_interactive": [], "deep_route": [],
    }
    route_paths: dict[str, str] = {}
    all_text: list[tuple[str, str]] = []

    for path in iter_sources(root):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        all_text.append((path, text))
        lines = text.splitlines()

        if RE_ASYNC_VIEW.search(text):
            covered = bool(RE_LOADING.search(text)) and bool(RE_ERROR.search(text))
            hits["async_views"].append({"file": path})
            if covered:
                hits["state_covered"].append({
                    "file": path,
                    "empty_state": bool(RE_EMPTY.search(text)),
                })

        if RE_MUTATION.search(text) and not RE_FEEDBACK.search(text):
            line_no = next((i for i, l in enumerate(lines, 1)
                            if RE_MUTATION.search(l)), 1)
            hits["feedback_gap"].append({"file": path, "line": line_no})

        for line_no, line in enumerate(lines, 1):
            for match in list(RE_TEXT_NODE.finditer(line)) + list(
                    RE_LABEL_PROP.finditer(line)):
                label = match.group(1).strip()
                if label.lower() in GENERIC_LABELS:
                    hits["generic_label"].append({
                        "file": path, "line": line_no, "label": label})
            if RE_NONSEMANTIC.search(line):
                hits["nonsemantic_interactive"].append({
                    "file": path, "line": line_no})
            for match in RE_ROUTE_PATH.finditer(line):
                route = match.group(1)
                route_paths[route] = f"{path}:{line_no}"
                depth = len([seg for seg in route.split("/") if seg and not
                             seg.startswith((":", "*"))])
                if depth > 3:
                    hits["deep_route"].append({
                        "file": path, "line": line_no, "route": route,
                        "depth": depth})

    orphans = []
    for route, where in route_paths.items():
        if route in ("/", "*") or len(route) < 2:
            continue
        needle = route.rstrip("/")
        linked = any(needle in text and where.split(":")[0] != path
                     for path, text in all_text)
        if not linked:
            orphans.append({"route": route, "declared_at": where})

    async_n = len(hits["async_views"])
    covered_n = len(hits["state_covered"])
    return {
        "root": root,
        "state_coverage_ratio": round(covered_n / async_n, 3) if async_n else None,
        "async_views": async_n,
        "state_covered": covered_n,
        "empty_state_missing": sum(
            1 for h in hits["state_covered"] if not h["empty_state"]),
        "feedback_gap_count": len(hits["feedback_gap"]),
        "generic_label_count": len(hits["generic_label"]),
        "nonsemantic_interactive_count": len(hits["nonsemantic_interactive"]),
        "nav_depth_over_3": len(hits["deep_route"]),
        "orphan_pages": len(orphans),
        "detail": {**hits, "orphans": orphans},
    }


def print_report(result: dict) -> None:
    print(f"Layer-A structural scan -- {result['root']}")
    print("Every count below is [KKE]: a structural proxy, not a measurement "
          "of confusion. Pair each with a Layer-B metric before promoting it.\n")
    ratio = result["state_coverage_ratio"]
    print(f"  state_coverage_ratio          {ratio if ratio is not None else 'n/a'} "
          f"({result['state_covered']}/{result['async_views']} async views handle "
          f"loading+error)")
    print(f"  empty-state missing           {result['empty_state_missing']} "
          f"of the covered views")
    print(f"  feedback_gap_count            {result['feedback_gap_count']}")
    print(f"  generic_label_count           {result['generic_label_count']}")
    print(f"  nonsemantic_interactive_count {result['nonsemantic_interactive_count']}")
    print(f"  nav_depth (>3 segments)       {result['nav_depth_over_3']}")
    print(f"  orphan_pages                  {result['orphan_pages']}")

    detail = result["detail"]
    for key, label in (("feedback_gap", "feedback gaps"),
                       ("generic_label", "generic labels"),
                       ("nonsemantic_interactive", "non-semantic interactives"),
                       ("deep_route", "routes deeper than 3")):
        rows = detail[key][:10]
        if not rows:
            continue
        print(f"\n  {label} (first {len(rows)}):")
        for row in rows:
            where = f"{row['file']}:{row.get('line', '?')}"
            extra = row.get("label") or row.get("route") or ""
            print(f"    {where} {extra}")
    if detail["orphans"]:
        print(f"\n  orphan routes (first 10):")
        for row in detail["orphans"][:10]:
            print(f"    {row['route']}  declared at {row['declared_at']}")
    print("\nNext: attach each candidate to a flow (parent_flow_id is "
          "mandatory) and give it a refutation condition. A count with no "
          "flow is a component scored in isolation, which the schema rejects.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Layer-A structural UX checks")
    parser.add_argument("root", help="source directory to scan")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        sys.exit(f"ERROR: {args.root} is not a directory")

    result = scan(args.root)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
