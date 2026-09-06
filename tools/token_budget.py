#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse to let the context budget drift without anyone noticing.

WHY THIS EXISTS
---------------
A skill costs tokens the way a dependency costs bytes: continuously, invisibly,
and to everyone who installs it. This one was designed to be cheap, and the
intention lived only in prose -- so between two releases the SKILL.md body grew
13%, the schema 52%, and a registry-writing run went from ~15.9k to ~20.8k
estimated tokens. Nothing failed, because a budget nobody checks is a
preference, not a budget. That is this family's own rule about prose-only rules,
pointed at itself.

THREE TIERS, BECAUSE THEY ARE NOT PAID AT THE SAME RATE
-------------------------------------------------------
  T0  the frontmatter `description`  -- in context in EVERY session where the
      skill is installed, used or not. The only always-on cost, and the one
      that deserves the tightest ceiling.
  T1  the SKILL.md body              -- paid whenever the skill triggers, and
      paid again on every cold start.
  T2  references / schemas           -- paid only when the procedure sends the
      model to that file. Progressive disclosure lives here, which is why a
      big T2 is not automatically a problem and a big T1 is.

Scripts and assets are NOT counted: they are executed or handed to a tool, not
read into context. Counting them would inflate the number with tokens nobody
pays, and a number nobody pays is the fastest way to make a budget ignored.

RUN SETS
--------
The tier totals do not answer the operational question, which is what ONE run
loads. `runs` in the config names the files a given mode actually pulls in --
SKILL.md plus whatever the procedure mandates -- and gives that set its own
ceiling. Those file lists are a reading of the procedure, not a measurement of
a live session: they are `[H]`, and the config says so in its own comment.

THE INSTRUMENT, STATED
----------------------
No tokenizer vocabulary is reachable offline, so tokens are ESTIMATED from
characters at the ratio declared in the config. Two consequences, both
deliberate:

  * The ceilings are expressed in the SAME estimated unit. The check is
    internally consistent whatever the true ratio is, because both sides are
    measured with one instrument.
  * The absolute numbers are `[H]`. A drift of +30% is `[K]`: it survives any
    fixed ratio.

Exit 0 clean, 1 over budget, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

CONFIG_DEFAULT = "tools/token-budget.json"


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def frontmatter_description(body: str) -> str:
    """The one line that is in context in every session. Measured on its own."""
    if not body.startswith("---"):
        return ""
    end = body.find("\n---", 3)
    if end < 0:
        return ""
    for line in body[3:end].splitlines():
        if line.startswith("description:"):
            return line
    return ""


def walk_prose(root: str) -> list[str]:
    """Everything under the skill that can end up in a context window.

    Scripts, assets and lockfiles are excluded on purpose -- see the module
    docstring. `.md`, `.yaml` and `.yml` are what the model reads.
    """
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith((".md", ".yaml", ".yml")):
                out.append(os.path.join(base, name).replace(os.sep, "/"))
    return sorted(out)


def measure(cfg: dict) -> tuple[dict, dict, list[str]]:
    root = cfg["skill_root"]
    ratio = float(cfg.get("chars_per_token", 3.6))
    skill_md = f"{root}/SKILL.md"
    problems: list[str] = []

    body = read(skill_md)
    if not body:
        problems.append(f"{skill_md} okunamadi / not readable")

    def tok(text: str) -> int:
        return round(len(text) / ratio)

    desc = frontmatter_description(body)
    tiers = {"T0": tok(desc), "T1": tok(body) - tok(desc), "T2": 0}
    per_file: dict[str, int] = {}
    for path in walk_prose(root):
        n = tok(read(path))
        per_file[path] = n
        if path != skill_md:
            tiers["T2"] += n
    return tiers, per_file, problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Skill context-budget checker (tier + per-run ceilings)")
    ap.add_argument("--config", default=CONFIG_DEFAULT)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--update", action="store_true",
                    help="write the CURRENT numbers back as the ceilings. A "
                         "deliberate act with a diff to review -- never run it "
                         "to make a red build green without reading what moved.")
    args = ap.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass

    try:
        cfg = json.loads(read(args.config) or "{}")
    except json.JSONDecodeError as exc:
        print(f"config parse error: {exc}", file=sys.stderr)
        return 2
    if not cfg.get("skill_root"):
        print(f"config missing 'skill_root': {args.config}", file=sys.stderr)
        return 2

    tiers, per_file, problems = measure(cfg)
    ratio = float(cfg.get("chars_per_token", 3.6))
    budgets = cfg.get("budgets", {})
    runs = cfg.get("runs", {})

    rows: list[tuple[str, int, int | None]] = []
    for tier in ("T0", "T1", "T2"):
        rows.append((tier, tiers[tier], budgets.get(tier)))

    run_rows: list[tuple[str, int, int | None, list[str]]] = []
    for name, spec in runs.items():
        files = spec.get("files", [])
        total = 0
        missing = []
        for path in files:
            if path not in per_file:
                missing.append(path)
            total += per_file.get(path, 0)
        run_rows.append((name, total, spec.get("ceiling"), missing))

    if args.json:
        print(json.dumps({"tiers": tiers, "runs": {n: t for n, t, _, _ in run_rows},
                          "per_file": per_file, "ratio": ratio}, indent=2))
        return 0

    over: list[str] = []
    print(f"olcum: {ratio} karakter/token (tahmin) · kaynak: {cfg['skill_root']}")
    print(f"{'katman':<8} {'token':>8} {'tavan':>8}  durum")
    for name, value, ceiling in rows:
        if ceiling is None:
            state = "tavan yok"
        elif value > ceiling:
            state = f"ASILDI (+{value - ceiling})"
            over.append(f"{name}: {value} > {ceiling}")
        else:
            state = f"ok ({ceiling - value} pay)"
        print(f"{name:<8} {value:>8} {str(ceiling or '-'):>8}  {state}")

    if run_rows:
        print(f"\n{'kosu':<26} {'token':>8} {'tavan':>8}  durum")
        for name, value, ceiling, missing in run_rows:
            if missing:
                print(f"{name:<26} {'?':>8} {'-':>8}  config'te olmayan dosya: "
                      f"{', '.join(missing)}")
                over.append(f"{name}: dosya yok ({', '.join(missing)})")
                continue
            if ceiling is None:
                state = "tavan yok"
            elif value > ceiling:
                state = f"ASILDI (+{value - ceiling})"
                over.append(f"{name}: {value} > {ceiling}")
            else:
                state = f"ok ({ceiling - value} pay)"
            print(f"{name:<26} {value:>8} {str(ceiling or '-'):>8}  {state}")

    biggest = sorted(per_file.items(), key=lambda kv: -kv[1])[:5]
    print("\nen buyuk dosyalar:")
    for path, n in biggest:
        print(f"  {n:>7}  {path}")

    if args.update:
        cfg.setdefault("budgets", {}).update({k: v for k, v, _ in rows})
        for name, value, _, missing in run_rows:
            if not missing:
                cfg["runs"][name]["ceiling"] = value
        with open(args.config, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\ntavanlar guncellendi: {args.config} -- diff'i oku, sayilarin "
              f"NEDEN buyudugunu commit mesajina yaz.")
        return 0

    if problems:
        for p in problems:
            print(f"\nHATA: {p}", file=sys.stderr)
        return 2
    if over:
        print("\nBUTCE ASILDI / OVER BUDGET:", file=sys.stderr)
        for line in over:
            print(f"  - {line}", file=sys.stderr)
        print("\nUcunden biri: (1) metni kisalt, (2) gerekcenin yerini "
              "degistir -- her yuklemede odenen bir dosyadan yalnizca "
              "sorulunca okunan bir dosyaya, (3) tavani BILEREK yukselt "
              "(--update) ve nedenini commit mesajina yaz. Sessizce buyumek "
              "bu ucunun arasinda yok.", file=sys.stderr)
        return 1

    print("\nok — her katman ve her kosu tavanin altinda.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
