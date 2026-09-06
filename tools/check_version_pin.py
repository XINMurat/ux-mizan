#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every stated version must agree with the skill's own.

A version printed in prose is a claim, and in this family it is sometimes a
claim about evidence rather than a label: ux-mizan's status line says how much
of the skill has been tested, and it had been written into ten files and
pinned to none. It drifted into four different numbers at once while the
released version was a fifth, so a reader could open one file and be told the
skill was five releases younger than it is. Mizan's usage guide had the same
shape in a quieter form: six sentences still naming v2.1 after v2.6 shipped.

This repository already pins the schema version to the schema's own banner,
on the stated grounds that a version living in two places is a version that
is wrong in one of them. This applies the rule to the other versions the
prose states.

Only the NUMBER is pinned. The sentence around it is deliberately left alone:
a quickstart says something shorter than a schema banner does, and flattening
every wording so a checker could compare them would be the tail wagging the
dog. So the map names the MARKERS -- the phrases that introduce a version
claim -- and the check reads the number that follows one.

Configuration is data, in tools/version-pin.json, so this file stays
byte-identical across the repositories that need it.

Usage:
    python tools/check_version_pin.py     # exit 1 if any stated version drifts
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "tools", "version-pin.json")

VERSION = re.compile(r"v([0-9]+\.[0-9]+)")


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def declared(cfg):
    """The one place the version is allowed to be decided."""
    text = read(cfg["source_file"])
    front = yaml.safe_load(text[4:text.index("\n---\n", 4)])
    return str((front.get("metadata") or {}).get(cfg["version_key"]) or "")


def main():
    cfg = json.loads(read("tools/version-pin.json") if os.path.exists(CONFIG)
                     else "{}")
    if not cfg:
        sys.stderr.write("FAIL: tools/version-pin.json is missing or empty.\n")
        return 1

    want = declared(cfg)
    if not re.fullmatch(r"[0-9]+\.[0-9]+", want):
        sys.stderr.write(
            "FAIL: %s frontmatter has no metadata.%s to pin the prose to.\n"
            % (cfg["source_file"], cfg["version_key"]))
        return 1

    markers = cfg["markers"]
    bad, seen = [], 0
    for rel in cfg["files"]:
        hits = 0
        for n, line in enumerate(read(rel).split("\n"), 1):
            if not any(m in line for m in markers):
                continue
            found = VERSION.findall(line)
            if not found:
                bad.append("%s:%d: a version marker with no version after it"
                           % (rel, n))
                continue
            hits += len(found)
            for got in found:
                seen += 1
                if got != want:
                    bad.append("%s:%d: says v%s, the skill is v%s"
                               % (rel, n, got, want))
        if not hits:
            bad.append("%s: no version claim found at all -- either it was "
                       "removed (drop the file from the map) or its wording "
                       "changed (add the new marker)" % rel)

    if bad:
        sys.stderr.write("FAIL: stated versions disagree with the skill version:\n")
        for line in bad:
            sys.stderr.write("  " + line + "\n")
        sys.stderr.write(
            "Fix the prose, or bump metadata.%s in %s if the version really "
            "moved.\n" % (cfg["version_key"], cfg["source_file"]))
        return 1

    print("ok  %d version claim(s) across %d files all say v%s"
          % (seen, len(cfg["files"]), want))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
