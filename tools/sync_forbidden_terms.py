#!/usr/bin/env python3
"""Push the local .forbidden-terms list to this repository's CI secret.

WHY THIS EXISTS
---------------
The list lives in two places and cannot live in one. The pre-commit hook reads
`.forbidden-terms` from disk, because it runs before the push. CI reads the
`FORBIDDEN_TERMS` secret, because the file is gitignored and never reaches the
runner. Both are necessary, and two copies of one list drift -- this repository
has found three separate cases of exactly that this month, in prose that
claimed a rule range the validator no longer had.

This script does not prevent the drift. Nothing can: a GitHub secret is
write-only, so no tool can read it back and compare. What it does is make the
correction a single command, and make the drift *visible* with --check.

    python tools/sync_forbidden_terms.py            # push the list
    python tools/sync_forbidden_terms.py --check    # has it likely drifted?

--check compares the file's modification time against the secret's
`updated_at`. That is a SIGNAL, not a comparison: editing a comment bumps the
mtime without changing a term, and someone could have set the secret from
another machine. It answers "worth re-syncing?", never "these are identical".

The terms themselves are never printed, and never passed on a command line
(where they would land in the shell history and the process list) -- they go to
`gh` on stdin.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

LIST_FILE = ".forbidden-terms"


def repo_root() -> str:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("not inside a git repository")
    return out.stdout.strip()


def repo_slug() -> str:
    """owner/name from the origin remote, so this script is not repo-specific."""
    out = subprocess.run(["git", "remote", "get-url", "origin"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("no `origin` remote to read the repository name from")
    url = out.stdout.strip()
    m = re.search(r"(?:github\.com[:/])([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        sys.exit(f"origin is not a recognisable GitHub URL: {url}")
    return m.group(1)


def active_terms(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f
                if ln.strip() and not ln.strip().startswith("#")]


def secret_updated_at(slug: str) -> str | None:
    out = subprocess.run(
        ["gh", "api", f"repos/{slug}/actions/secrets/FORBIDDEN_TERMS"],
        capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout).get("updated_at")
    except json.JSONDecodeError:
        return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report whether the list looks newer than the secret; change nothing")
    args = ap.parse_args(argv)

    root = repo_root()
    path = os.path.join(root, LIST_FILE)
    if not os.path.isfile(path):
        print(f"{LIST_FILE} does not exist here — nothing to sync.")
        print("See tools/leak_check.py for what it is and why it is gitignored.")
        return 0

    # A tracked list would publish the names it exists to keep out.
    tracked = subprocess.run(["git", "-C", root, "ls-files", "--error-unmatch", LIST_FILE],
                             capture_output=True, text=True)
    if tracked.returncode == 0:
        print(f"REFUSING: {LIST_FILE} is tracked by git. It must be gitignored.",
              file=sys.stderr)
        return 1

    terms = active_terms(path)
    if not terms:
        print(f"{LIST_FILE} has no active terms (all comments). Nothing to push.")
        return 0

    slug = repo_slug()
    updated = secret_updated_at(slug)

    if args.check:
        if updated is None:
            print(f"{slug}: FORBIDDEN_TERMS is not set. {len(terms)} local term(s) are "
                  f"enforced at commit time but not in CI. Run without --check.")
            return 1
        mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(path), datetime.timezone.utc)
        secret_time = datetime.datetime.fromisoformat(updated.replace("Z", "+00:00"))
        newer = mtime > secret_time
        print(f"{slug}: {len(terms)} local term(s); secret last set {updated}, "
              f"list last edited {mtime.isoformat(timespec='seconds')}")
        print("  the list looks NEWER than the secret — worth re-syncing"
              if newer else
              "  the secret is at least as new as the list")
        print("  (a signal, not a comparison: a secret cannot be read back)")
        return 1 if newer else 0

    # stdin, never argv: a command line lands in the shell history and in the
    # process list of everything running on this machine.
    proc = subprocess.run(
        ["gh", "secret", "set", "FORBIDDEN_TERMS", "--repo", slug],
        input="\n".join(terms) + "\n", text=True,
        capture_output=True)
    if proc.returncode != 0:
        print(f"gh failed: {proc.stderr.strip()[:400]}", file=sys.stderr)
        return 1
    print(f"{slug}: FORBIDDEN_TERMS set from {LIST_FILE} ({len(terms)} term(s)).")
    print("The terms were not printed and were not passed on a command line.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
