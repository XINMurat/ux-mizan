#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package skill/<name>/ into <name>.skill (a zip with stable contents).

<name> is the one directory under skill/, so this file is byte-identical in
every repository of the family. It was ux-mizan's alone; the others shipped
packages built by hand on Windows, with CRLF line endings inside -- including
a `#!/usr/bin/env python3\r` shebang that `./script.py` cannot run -- and no
check that the package still matched the source.

Stability matters more than it looks: CI compares the package against the
source file by file, and a zip that embeds timestamps produces a different
archive from identical sources, which turns a real drift check into noise
nobody reads. So every entry gets a fixed timestamp and the file list is
sorted.

Usage:
    python tools/build_skill.py
    python tools/build_skill.py --check     # verify without writing
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile

SOURCE_ROOT = "skill"


def _skill_name() -> str:
    names = sorted(d for d in os.listdir(SOURCE_ROOT)
                   if os.path.isdir(os.path.join(SOURCE_ROOT, d))) if os.path.isdir(SOURCE_ROOT) else []
    if len(names) != 1:
        sys.exit(f"ERROR: expected exactly one directory under {SOURCE_ROOT}/, found {names} "
                 "(run this from the repository root)")
    return names[0]


NAME = _skill_name()
SKILL_DIR = os.path.join(SOURCE_ROOT, NAME)
OUTPUT = f"{NAME}.skill"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)
SKIP_DIRS = {"__pycache__"}
SKIP_EXT = {".pyc"}


def source_files() -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(SKILL_DIR):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if os.path.splitext(name)[1] in SKIP_EXT:
                continue
            path = os.path.join(dirpath, name)
            found.append(os.path.relpath(path, SOURCE_ROOT).replace(os.sep, "/"))
    return sorted(found)


def normalise(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def build() -> list[str]:
    names = source_files()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            with open(os.path.join(SOURCE_ROOT, name), "rb") as handle:
                data = normalise(handle.read())
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return names


def check() -> int:
    if not os.path.exists(OUTPUT):
        print(f"{OUTPUT} is missing. Run: python tools/build_skill.py")
        return 1
    problems = []
    with zipfile.ZipFile(OUTPUT) as archive:
        packaged = set(archive.namelist())
        for name in source_files():
            if name not in packaged:
                problems.append(f"{name}: in source but not packaged")
                continue
            with open(os.path.join(SOURCE_ROOT, name), "rb") as handle:
                packed, source = archive.read(name), normalise(handle.read())
                # The package is compared as packaged, not normalised: a CRLF
                # inside it is the defect this check exists for.
                if packed != source:
                    problems.append(f"{name}: " + (
                        "CRLF line endings in the package"
                        if normalise(packed) == source else "content differs from source"))
        for name in sorted(packaged - set(source_files())):
            problems.append(f"{name}: packaged but missing from source")
    if problems:
        print(f"{OUTPUT} is OUT OF SYNC with {SKILL_DIR}/:")
        for problem in problems:
            print("  -", problem)
        print("\nRebuild it: python tools/build_skill.py")
        return 1
    print(f"{OUTPUT} is in sync with {SKILL_DIR}/.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Build or verify {OUTPUT}")
    parser.add_argument("--check", action="store_true",
                        help="verify the package matches the source; write nothing")
    args = parser.parse_args()

    if not os.path.isdir(SKILL_DIR):
        sys.exit(f"ERROR: run this from the repository root ({SKILL_DIR} not found)")

    if args.check:
        return check()

    names = build()
    print(f"Wrote {OUTPUT} with {len(names)} files:")
    for name in names:
        print("  ", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
