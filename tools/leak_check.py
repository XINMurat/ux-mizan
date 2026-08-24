#!/usr/bin/env python3
"""Refuse to publish a real name.

WHY THIS EXISTS
---------------
The examples in this repository use invented names on purpose. That is the
discipline; this is the net. A client name, an internal product, a private
repository or a distinctive stack that reaches a tracked file is published the
moment it is pushed -- this repository is public, and the packaged .skill goes
out to anyone who installs it. Deletion afterwards does not un-publish it.

Borrowed from vaddermail/maestro-framework (`_meta/FORBIDDEN-TERMS`, check 14),
with two changes that its own setting does not need and this one does:

  1. THE LIST IS NEVER COMMITTED. Maestro ships an empty list in-tree and
     excludes the populated copy from its release ZIP. That works when the
     repository holding the list is private. This repository is public, so a
     populated list in-tree would publish exactly the names it exists to keep
     out. The list lives in `.forbidden-terms`, which is gitignored, or in a
     CI secret.

  2. A HIT NEVER PRINTS THE TERM. Maestro's sweep prints the matched term into
     its build log. Public CI logs are public: printing the secret to prove the
     secret did not leak is self-defeating. This prints the file, the line and
     the index of the term in the list -- enough to find it, useless to a
     reader who does not already hold the list.

USAGE
-----
    python tools/leak_check.py                 # sweep tracked files
    python tools/leak_check.py --package ux-mizan.skill
    python tools/leak_check.py --staged        # what a pre-commit hook runs
    FORBIDDEN_TERMS="$(cat list)" python tools/leak_check.py   # CI, from a secret

The list is one extended-regex term per line; blank lines and lines starting
with `#` are ignored. With no list configured the sweep reports NOT CONFIGURED
and exits 0: an absent list is a repository that has not set this up, which is
not the same as a repository that failed.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import zipfile

LIST_FILE = ".forbidden-terms"
SKIP_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".xlsx", ".pyc")


def load_terms(explicit: str | None) -> tuple[list[str], str]:
    """Terms plus a one-line description of where they came from."""
    if explicit:
        with open(explicit, "r", encoding="utf-8") as f:
            return _parse(f.read()), f"--terms {explicit}"
    env = os.environ.get("FORBIDDEN_TERMS")
    if env:
        return _parse(env), "the FORBIDDEN_TERMS environment (a CI secret)"
    if os.path.isfile(LIST_FILE):
        with open(LIST_FILE, "r", encoding="utf-8") as f:
            return _parse(f.read()), LIST_FILE
    return [], "nowhere"


def _parse(blob: str) -> list[str]:
    out = []
    for line in blob.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if p and not p.endswith(SKIP_SUFFIXES)]


def staged_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True)
    return [p for p in out.stdout.splitlines()
            if p and os.path.isfile(p) and not p.endswith(SKIP_SUFFIXES)]


def sweep_text(name: str, text: str, patterns: list[re.Pattern]) -> list[str]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for n, pat in enumerate(patterns, 1):
            if pat.search(line):
                hits.append(f"{name}:{i}  matches term #{n}")
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--terms", help="file of forbidden terms (default: env, then .forbidden-terms)")
    ap.add_argument("--package", help="also sweep inside this .skill/.zip")
    ap.add_argument("--staged", action="store_true", help="sweep staged files instead of all tracked ones")
    args = ap.parse_args(argv)

    terms, source = load_terms(args.terms)
    if not terms:
        print(f"leak-check: NOT CONFIGURED (no terms in {source}) -- see the module docstring")
        return 0

    try:
        patterns = [re.compile(t, re.IGNORECASE) for t in terms]
    except re.error as e:
        print(f"leak-check: term #{terms.index(e.pattern) + 1} is not a valid regex", file=sys.stderr)
        return 2

    targets = staged_files() if args.staged else tracked_files()
    # The list must never become a tracked file; if it somehow is, that is the
    # first thing to report and the sweep would otherwise flag every term in it.
    if LIST_FILE in targets:
        print(f"leak-check: FAIL -- {LIST_FILE} is tracked by git. It must be gitignored.",
              file=sys.stderr)
        return 1

    hits: list[str] = []
    for path in targets:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                hits += sweep_text(path, f.read(), patterns)
        except OSError:
            continue

    if args.package and os.path.isfile(args.package):
        # The packaged artifact is what people install. Sweeping the tree does
        # not prove the package is clean: they are built by different code.
        with zipfile.ZipFile(args.package) as z:
            for name in z.namelist():
                if name.endswith(SKIP_SUFFIXES) or name.endswith("/"):
                    continue
                hits += sweep_text(f"{args.package}:{name}",
                                   z.read(name).decode("utf-8", "replace"), patterns)

    if hits:
        print(f"leak-check: FAIL -- {len(hits)} match(es) against {len(terms)} term(s) from {source}",
              file=sys.stderr)
        print("The term itself is not printed: this log may be public.", file=sys.stderr)
        for h in hits[:40]:
            print("  -", h, file=sys.stderr)
        if len(hits) > 40:
            print(f"  ... {len(hits) - 40} more", file=sys.stderr)
        return 1

    scope = "staged files" if args.staged else f"{len(targets)} tracked files"
    if args.package:
        scope += f" + {args.package}"
    print(f"leak-check: ok -- {len(terms)} term(s) from {source}, none present in {scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
