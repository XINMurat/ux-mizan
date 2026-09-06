#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish the canonical English skill documents as docs/ pages.

The Turkish half of docs/ had documents the English half did not, and the
obvious reading -- "the English versions are missing" -- was wrong. Every one
of them already existed in English, under skill/: the Turkish files are the
translations, not the originals. What was missing was not a translation but a
PAGE: the canonical English text lives in the skill package, which the Jekyll
site does not serve, so the English menu could not offer it.

So this mirrors rather than copies-by-hand. The skill package stays the single
source of truth -- it is what Claude actually loads -- and `--check` fails CI
the moment a mirrored page drifts from it. A hand-maintained second English
copy would have been a third version to keep in sync, which is exactly the
failure mode this family names in its own checklist.

Usage:
    python tools/sync_en_docs.py            # write the mirrored pages
    python tools/sync_en_docs.py --check    # exit 1 if any page is stale

The per-repository map is data, in docs/en-mirror.json, so this file stays
byte-identical across the four repositories.
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(ROOT, "docs", "en-mirror.json")
OUT_DIR = os.path.join(ROOT, "docs", "en")

BANNER = """<!-- GENERATED PAGE - do not edit here.
     Source of truth: {sources}
     Regenerate:      python tools/sync_en_docs.py
     CI (`--check`) fails if this page drifts from its source. -->

# {title}

> **Mirrored from the skill package.** This is the canonical English text that
> Claude actually loads, published here so it can be read next to its Turkish
> mirror instead of only on GitHub. Edit the source{plural} above, not this
> page{tr_note}.
"""


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def strip_front_matter(text):
    """A skill's YAML header is metadata for Claude, not for a web page.

    Left in place Jekyll would eat it as the page's own front matter and the
    skill's `description` -- a long trigger-phrase list written for a model --
    would become the page description a human reads.
    """
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5:] if end != -1 else text


def demote(text):
    """The page supplies its own H1, so the source's headings shift one level.

    Two H1s on a page is not a style quibble: it breaks the document outline
    that screen readers and the table of contents both read.
    """
    out = []
    fenced = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def build(entry):
    srcs = entry["sources"]
    body = "\n\n".join(demote(strip_front_matter(read(os.path.join(ROOT, s))).strip())
                       for s in srcs)
    tr = entry.get("tr")
    head = BANNER.format(
        sources=", ".join(srcs),
        title=entry["title"],
        plural="s" if len(srcs) > 1 else "",
        tr_note=("; the Turkish mirror is `%s`" % tr) if tr else "",
    )
    return head + "\n" + body + "\n"


def main():
    check = "--check" in sys.argv
    entries = json.loads(read(MAP_PATH))["pages"]
    stale, written = [], []
    for e in entries:
        path = os.path.join(OUT_DIR, e["out"])
        want = build(e)
        have = read(path) if os.path.exists(path) else None
        if have == want:
            continue
        if check:
            stale.append(e["out"])
        else:
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(want)
            written.append(e["out"])

    if check:
        if stale:
            sys.stderr.write(
                "en-mirror: %d page(s) drifted from the skill package:\n  %s\n"
                "Run `python tools/sync_en_docs.py` and commit the result.\n"
                % (len(stale), "\n  ".join(stale)))
            return 1
        print("en-mirror: ok -- %d page(s) match the skill package." % len(entries))
        return 0

    print("en-mirror: %d written, %d already current."
          % (len(written), len(entries) - len(written)))
    for w in written:
        print("  +", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
