#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The tools the four repositories share must stay the same file.

Seven tools are copied, not imported, into Mizan, Kiyas, Iskele and ux-mizan
(a skill repository has no package to import from). Copies drift one line at a
time: the package sync check did, and a CRLF-blind copy passed four repos'
CI for weeks. tools/shared-tools.json names each shared file with the sha256
of its LF bytes; the manifest is itself identical in all four repositories.

This check needs no network. It fails when a shared file here no longer
matches the manifest -- that is, when one copy was edited alone. To change a
shared tool: edit it, run with --update, and copy the tool AND the manifest
to the other three repositories in the same change. The site repository runs
a daily comparison of the four `main` branches, which catches a manifest that
moved in one repository only.

Usage:
    python tools/check_shared_tools.py            # exit 1 on drift
    python tools/check_shared_tools.py --update   # rewrite the hashes as they are now
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tools", "shared-tools.json")


def digest(rel: str) -> str:
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def main(argv: list[str]) -> int:
    with io.open(MANIFEST, encoding="utf-8") as fh:
        cfg = json.load(fh)
    files = cfg["files"]
    if "--update" in argv:
        for rel in files:
            files[rel] = digest(rel)
        with io.open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("updated %d hash(es) -- copy the tools and this manifest to the other repositories" % len(files))
        return 0
    bad = []
    for rel, want in sorted(files.items()):
        if not os.path.exists(os.path.join(ROOT, rel)):
            bad.append("%s: listed as shared but missing here" % rel)
        elif digest(rel) != want:
            bad.append("%s: differs from the shared copy" % rel)
    if bad:
        print("FAIL: shared tools drifted in this repository:")
        for b in bad:
            print("  " + b)
        print("Edit shared tools in all four repositories at once, then run --update "
              "and copy tools/shared-tools.json with them.")
        return 1
    print("ok  %d shared tool(s) match the manifest" % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
