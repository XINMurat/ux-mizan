#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A menu entry must be able to keep the promise its language makes.

The site offers a document under two names -- "Quickstart" and "Hızlı
başlangıç" -- and that is a promise: press TR and you get Turkish. ux-mizan's
quickstart was in both menus and was English only, with none of the two-pane
markup the other three repositories use, so pressing TR did nothing and the
page served English under a Turkish name. That is worse than an absent
translation, because an absent one can stay silent; this one advertised.

Two shapes are legal, and this checks both:

  * a page in BOTH menus is one file with two panes (`pane-en` / `pane-tr`),
    which is how the overview and quickstart pages work;
  * a page in ONE menu is a single-language document and must be listed in
    `pairs`, so the language control can navigate to its counterpart -- and
    that counterpart file has to exist.

An unpaired single-language page is fine as a page; it is only illegal as a
menu entry, because the menu is where the promise is made.

Usage:
    python tools/check_lang_parity.py     # exit 1 if a menu entry cannot deliver
"""
from __future__ import annotations

import io
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "docs", "_config.yml")


def source_of(url):
    """Map a published URL back to the file in docs/ that produces it."""
    trimmed = url.rstrip("/")
    if not trimmed:
        return "docs/index.md"
    return "docs" + trimmed.replace(".html", ".md")


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def main():
    with io.open(CONFIG, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    nav_en = [n["url"] for n in cfg.get("nav_en") or []]
    nav_tr = [n["url"] for n in cfg.get("nav_tr") or []]
    pairs = cfg.get("pairs") or []

    if len(nav_en) != len(nav_tr):
        # Not fatal on its own -- one language may legitimately have more
        # documents -- but it is worth saying out loud, because it is the
        # symptom that sent us looking the first time.
        print("note: the menus are %d and %d entries long"
              % (len(nav_en), len(nav_tr)))

    paired = set()
    problems = []

    for pair in pairs:
        for side in ("en", "tr"):
            url = pair[side]
            paired.add(url)
            rel = source_of(url + ".html")
            if not os.path.exists(os.path.join(ROOT, rel)):
                problems.append("pairs: %s points at %s, which does not exist"
                                % (url, rel))

    both = set(nav_en) & set(nav_tr)
    for url in sorted(both):
        rel = source_of(url)
        if not os.path.exists(os.path.join(ROOT, rel)):
            problems.append("%s is in both menus but %s does not exist"
                            % (url, rel))
            continue
        text = read(rel)
        if 'id="pane-en"' not in text or 'id="pane-tr"' not in text:
            problems.append(
                "%s is in BOTH menus but %s has no two-pane markup -- it will "
                "serve one language under both names" % (url, rel))

    for url in [u for u in nav_en + nav_tr if u not in both]:
        if url.replace(".html", "") not in paired:
            problems.append(
                "%s is a single-language menu entry with no `pairs` counterpart "
                "-- its language control will be silent" % url)

    if problems:
        sys.stderr.write("FAIL: menu entries that cannot keep their promise:\n")
        for line in problems:
            sys.stderr.write("  " + line + "\n")
        return 1

    print("ok  %d menu entries: %d bilingual page(s), %d pair(s), none stranded"
          % (len(set(nav_en + nav_tr)), len(both), len(pairs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
