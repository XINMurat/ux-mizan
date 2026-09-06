#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every status line must agree with the skill's own version.

The status line -- "Status: v0.x [H] / [KKE]" -- is not decoration. It is a
CLAIM about how much evidence this skill has: one self-validation run, one
refuted design decision, no behavioural evidence. It was written into ten
places, and left unpinned it drifted into four different numbers at once
(v0.1, v0.2, v0.3, v0.5) while the released version was v0.6. A reader could
open a file and be told the skill was five releases younger than it is.

This repository already pins the schema version to the schema's own banner,
for the reason stated there: a version that lives in two places is a version
that is wrong in one of them. Ten places is the same defect, louder.

Only the NUMBER is pinned. The sentence beside it stays deliberately
unpinned: a quickstart says something shorter than a schema banner does, and
flattening them all to one wording so a checker could compare them would be
the tail wagging the dog.

Usage:
    python tools/check_status_pin.py     # exit 1 if any status line disagrees
"""
from __future__ import annotations

import io
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = "skill/ux-mizan/SKILL.md"

FILES = [
    "README.md",
    "docs/index.md",
    "docs/QUICKSTART.md",
    "docs/en/usage-guide.md",
    "docs/tr/kullanim-kilavuzu.md",
    "docs/tr/metodoloji.md",
    "skill/ux-mizan/SKILL.md",
    "skill/ux-mizan/schemas/ux-registry.yaml",
    "templates/ux-registry.yaml",
]

# "Status:", the Turkish "Statü:" (and its unaccented spelling), and the
# schema banner's shouted "STATUS:".
PATTERN = re.compile(r"(?:Status: v|Statu: v|Statü: v|STATUS: v)([0-9]+\.[0-9]+)")


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def declared_version():
    text = read(SKILL)
    end = text.index("\n---\n", 4)
    front = yaml.safe_load(text[4:end])
    return str((front.get("metadata") or {}).get("version") or "")


def main():
    want = declared_version()
    if not re.fullmatch(r"[0-9]+\.[0-9]+", want):
        sys.stderr.write(
            "FAIL: %s frontmatter has no metadata.version to pin the status "
            "lines to.\n" % SKILL)
        return 1

    bad, seen = [], 0
    for rel in FILES:
        found = PATTERN.findall(read(rel))
        if not found:
            bad.append("%s: no status line at all" % rel)
            continue
        for got in found:
            seen += 1
            if got != want:
                bad.append("%s: says v%s, the skill is v%s" % (rel, got, want))

    if bad:
        sys.stderr.write("FAIL: the status lines disagree with the skill version:\n")
        for line in bad:
            sys.stderr.write("  " + line + "\n")
        sys.stderr.write(
            "The status line is a claim about evidence, not a label. Fix the "
            "files, or bump metadata.version in %s if the version really moved.\n"
            % SKILL)
        return 1

    print("ok  %d status line(s) across %d files all say v%s"
          % (seen, len(FILES), want))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
