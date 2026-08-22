#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout signals -- structural traces of arrangement, and the behavioural
hypotheses they license.

WHAT THIS CAN AND CANNOT DO. It cannot measure attention, focus or
cognitive load; nothing that reads source can. What it CAN do is find the
RENDERING SHAPES that make those failures likely, and hand back a named
hypothesis with the measurement that would settle it. So every signal
below is emitted as:

    [KKE] the structural trace   -- verifiable in the file, right now
    [H]   the behavioural claim  -- what it may do to a user, unproven
    metric                       -- what would decide it

The tier split is the whole point. "InstancePage renders 6 child sections
per repeated item with no collapse" is checkable and boring. "Users
re-derive what to do next on every visit" is interesting and unproven.
Collapsing the two -- reporting the second as if the file proved it -- is
the failure this script is shaped to prevent.

WHY THIS EXISTS. The first self-validation run met a real complaint
("everything is nested and sequential, nothing is separated, we cannot
tell what to do when") that structural_checks.py could not see: nothing
was missing. A loading state can be absent; an arrangement cannot. The
trace was found by hand, afterwards. This script is that reading, made
repeatable.

WHAT IT WILL GET WRONG. Regex over JSX, so: a file that composes its list
item from small components looks sparser than it renders, and a file with
one long inline item looks denser. Every signal is a place to LOOK. Open
the file before writing a finding -- the registry demands a file and a
line, and this gives you both.

SIGNALS
  S1 expanded-repeated-block   many-part items rendered all-open, no collapse
  S2 weak-current-marker       the "current" item differs only by colour
  S3 dense-screen              many top-level sections on one screen
  S4 control-density           many interactive controls inside one item
  S5 heading-gap               long screen, nothing to scan by
  S6 unbounded-list            list with no collapse, paging or windowing

USAGE
    python layout_signals.py path/to/src
    python layout_signals.py path/to/src --json
    python layout_signals.py path/to/src --file InstancePage.tsx
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SOURCE_EXT = {".tsx", ".jsx", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "__pycache__"}

# --- thresholds. Every one is [H] and none is validated. They are chosen
# to be quiet on small components and loud on screens, not derived from
# any study; treat a signal as "look here", never as "this is broken".
ITEM_PART_MIN = 4        # child components inside one repeated item
ITEM_LINE_MIN = 25       # lines of JSX inside one repeated item
SECTION_MAX = 5          # top-level sections on one screen
CONTROL_MAX = 5          # interactive controls inside one repeated item
LIST_UNBOUNDED_LINES = 60  # below this the signal fired on every list and taught nothing
LONG_FILE_LINES = 200
HEADING_MIN = 2

RE_MAP = re.compile(r"\.map\s*\(")
RE_CHILD_COMPONENT = re.compile(r"<([A-Z]\w+)")
# Only things that COLLAPSE THE ITEM count here. Sheet, Dialog and Popover
# were on this list first, and they silence the very sites this script
# exists for: an overlay opened from a row does not fold the row away.
# Same failure shape as the word-boundary bug in structural_checks.py --
# an over-broad exclusion reads exactly like a clean file.
# aria-expanded is the precise one: it is the row TELLING the user it
# folds. Leaving it out let the signal fire on a table that discloses
# progressively and does it accessibly -- the exact opposite of the
# problem. isOpen alone stays out; it is used for overlays too.
RE_COLLAPSE = re.compile(
    r"\b(Collapsible|Accordion|<details|isExpanded|collapsed|showMore|"
    r"Disclosure)\b|aria-expanded")
RE_DRAG = re.compile(r"onDrag\w*|onDrop")
RE_INTERACTIVE = re.compile(
    r"<(?:Button|Input|Select|Textarea|Checkbox|Switch|a\b)|onClick|onChange|onSubmit")
RE_SECTION = re.compile(r"<(?:section|Card)\b")
RE_HEADING = re.compile(r"<(?:h[1-4]|CardTitle|SheetTitle|DialogTitle)\b")
RE_PAGING = re.compile(
    r"\b(?:slice\s*\(|Pagination|useVirtual|virtual|page\s*[,)=]|take\s*\(|limit)\b")
# A ternary keyed on "this is the current one", capturing both class strings.
RE_CURRENT_TERNARY = re.compile(
    # Newlines allowed between the test and the "?": prettier puts the
    # branches of a className ternary on their own lines, and requiring
    # them on one line made this signal silently unfirable in exactly the
    # codebases it was written for.
    r"\b(?:is)?(?:[Cc]urrent|[Aa]ctive|[Ss]elected)\b[^?]{0,60}\?\s*"
    r"['\"]([^'\"]{3,300})['\"]\s*:\s*['\"]([^'\"]{3,300})['\"]",
    re.S)
# A ternary whose branches are short human words, i.e. a label, not classes.
RE_TEXT_TERNARY = re.compile(
    r"\?\s*['\"][^'\"]{1,24}['\"]\s*:\s*['\"][^'\"]{1,24}['\"]")

# Utility-class prefixes that change only how a thing LOOKS.
# The trailing "(?:-|$)" is load-bearing: Tailwind's bare utilities
# ("border", "shadow", "ring") carry no dash, and requiring one made the
# signal miss the canonical case -- "border-2 border-primary/50" against
# plain "border border-border", which is a difference in colour and
# nothing else.
COLOUR_ONLY = re.compile(
    r"^(?:border|bg|text|ring|shadow|outline|from|to|via|fill|stroke|"
    r"accent|decoration|divide)(?:-|$)")
# ...as opposed to these, which change size, position or presence.
STRUCTURAL_CLASS = re.compile(
    r"^(?:w-|h-|p-|px-|py-|pt-|pb-|m-|mx-|my-|mt-|mb-|gap-|col-|row-|order-|"
    r"grid|flex|block|hidden|absolute|relative|sticky|fixed|scale-|z-|"
    r"font-|text-(?:xs|sm|base|lg|xl|2xl|3xl)$|rounded|min-|max-|basis-)")

HYPOTHESIS = {
    "expanded-repeated-block": (
        "Every item is rendered open and carries {parts} child parts, so all "
        "items compete for attention on equal terms. A user returning to this "
        "screen re-derives 'what do I do now' from the content instead of "
        "reading it off the arrangement.",
        "time_on_task",
        "Interrupt participants mid-task and ask where they are and what is "
        "next; time the answer.",
    ),
    "weak-current-marker": (
        "The current item is distinguished from the rest only by colour "
        "({diff}). Nothing changes size, position or expansion, so the "
        "distinction competes with every other coloured element and is lost "
        "for anyone scanning, or not perceiving that hue.",
        "first_click_accuracy",
        "Ask participants to act on 'the step you should do now' and record "
        "whether the first click lands on the current item.",
    ),
    "dense-screen": (
        "{sections} top-level sections on one screen, none of them chosen by "
        "the user. Sections that are not used in the same sitting force "
        "scrolling past the others every time.",
        "time_on_task",
        "Time the path to one specific section from screen entry.",
    ),
    "control-density": (
        "{controls} interactive controls inside a single repeated item. "
        "Multiplied by the item count, the screen offers far more choices "
        "than the task needs, and the one control the user wants has to be "
        "found among its neighbours.",
        "first_click_accuracy",
        "Record first-click accuracy for the primary action on an item.",
    ),
    "heading-gap": (
        "{lines} lines of screen with {headings} headings. There is nothing "
        "to scan by, so finding anything means reading sequentially.",
        "time_on_task",
        "Ask participants to locate a named piece of content and time it.",
    ),
    "unbounded-list": (
        "A list rendered whole, with no collapse, paging or windowing. It is "
        "fine while the data is small; the arrangement fails at a size the "
        "code does not bound, so today's screenshot does not predict "
        "tomorrow's screen.",
        "step_abandonment",
        "Test with a realistically LARGE record, not the demo seed.",
    ),
}


def iter_sources(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] not in SOURCE_EXT:
                continue
            if any(part in name for part in (".test.", ".spec.")):
                continue
            yield os.path.join(dirpath, name)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def balanced_slice(text: str, open_index: int) -> str:
    """Text of the call that starts at the '(' at open_index."""
    depth = 0
    for i in range(open_index, len(text)):
        char = text[i]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_index:i + 1]
    return text[open_index:]


def class_tokens(value: str) -> set[str]:
    return {t for t in value.replace("\n", " ").split(" ") if t}


def scan_file(path: str, text: str) -> list[dict]:
    signals: list[dict] = []
    total_lines = text.count("\n") + 1

    # --- S1 / S4 / S6: repeated items
    for match in RE_MAP.finditer(text):
        open_paren = text.index("(", match.start())
        block = balanced_slice(text, open_paren)
        if "<" not in block:
            continue                      # a data map, not a render
        line = line_of(text, match.start())
        block_lines = block.count("\n") + 1
        parts = len(set(RE_CHILD_COMPONENT.findall(block)))
        collapses = bool(RE_COLLAPSE.search(block))
        # Drag-and-drop is ONE affordance wearing four handler names
        # (onDragStart/End/Over/onDrop). Counting them separately put a
        # well-built, progressively-disclosed row at "14 controls" on the
        # first real scan, and opening the file was the only thing that
        # caught it. Count the gesture once.
        controls = len(RE_INTERACTIVE.findall(block)) - max(
            0, len(RE_DRAG.findall(block)) - 1)

        if parts >= ITEM_PART_MIN and block_lines >= ITEM_LINE_MIN and not collapses:
            signals.append({
                "signal": "expanded-repeated-block", "file": path, "line": line,
                "facts": {"parts": parts, "lines": block_lines, "collapse": False},
            })
        # A row that collapses has already answered the density question:
        # the controls are behind a disclosure the user opened on purpose.
        if controls > CONTROL_MAX and not collapses:
            signals.append({
                "signal": "control-density", "file": path, "line": line,
                "facts": {"controls": controls},
            })
        if block_lines >= LIST_UNBOUNDED_LINES and not collapses and not RE_PAGING.search(block):
            signals.append({
                "signal": "unbounded-list", "file": path, "line": line,
                "facts": {"lines": block_lines},
            })

    # --- S2: how the current item is marked
    for match in RE_CURRENT_TERNARY.finditer(text):
        # If the SAME condition also switches visible text, the state is
        # carried by a label and colour is only reinforcing it. The first
        # real scan flagged a status badge reading "etkin"/"devre disi"
        # -- perfectly legible, and nothing to do with which item is
        # current. This signal is about position, not about variants.
        tail = text[match.end():match.end() + 500]
        if RE_TEXT_TERNARY.search(tail):
            continue
        a, b = class_tokens(match.group(1)), class_tokens(match.group(2))
        diff = (a - b) | (b - a)
        if not diff:
            continue
        if all(COLOUR_ONLY.match(t) and not STRUCTURAL_CLASS.match(t) for t in diff):
            signals.append({
                "signal": "weak-current-marker", "file": path,
                "line": line_of(text, match.start()),
                "facts": {"diff": " ".join(sorted(diff))[:120]},
            })

    # --- S3 / S5: whole-screen shape (pages only; a component is not a screen)
    is_screen = os.sep + "pages" + os.sep in path or path.endswith("Page.tsx")
    if is_screen:
        sections = len(RE_SECTION.findall(text))
        if sections > SECTION_MAX:
            signals.append({
                "signal": "dense-screen", "file": path, "line": 1,
                "facts": {"sections": sections},
            })
        headings = len(RE_HEADING.findall(text))
        if total_lines >= LONG_FILE_LINES and headings < HEADING_MIN:
            signals.append({
                "signal": "heading-gap", "file": path, "line": 1,
                "facts": {"lines": total_lines, "headings": headings},
            })
    return signals


def scan(root: str, only: str | None = None) -> list[dict]:
    found: list[dict] = []
    for path in iter_sources(root):
        if only and only not in os.path.basename(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        found.extend(scan_file(path, text))
    return found


def print_report(signals: list[dict], root: str) -> None:
    print(f"Layout signals -- {root}")
    print("Each signal has TWO tiers. The trace is [KKE]: checkable in the")
    print("file. The behavioural claim is [H]: what it may do to a user, and")
    print("only the named metric can settle that. Do not report the [H] line")
    print("as though the file proved it.\n")

    if not signals:
        print("  No signals. That is not a clean bill of health -- this script")
        print("  looks for six arrangement shapes and is blind to the rest.")
        return

    by_signal: dict[str, list[dict]] = {}
    for item in signals:
        by_signal.setdefault(item["signal"], []).append(item)

    for name, items in sorted(by_signal.items(), key=lambda kv: -len(kv[1])):
        template, metric, how = HYPOTHESIS[name]
        print(f"== {name}  ({len(items)} site{'s' if len(items) > 1 else ''})")
        for item in items[:6]:
            rel = os.path.relpath(item["file"], root)
            facts = ", ".join(f"{k}={v}" for k, v in item["facts"].items())
            print(f"   [KKE] {rel}:{item['line']}  ({facts})")
        if len(items) > 6:
            print(f"   ... {len(items) - 6} more")
        print(f"   [H]   {template.format(**items[0]['facts'])}")
        print(f"   metric: {metric}")
        print(f"   decide it by: {how}\n")

    print("Next: each [H] above becomes a finding only after it is attached to")
    print("a flow (parent_flow_id is mandatory) and given a threshold BEFORE")
    print("the measurement. A threshold written after the session is HARKing.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Structural layout traces and the behavioural hypotheses they license")
    parser.add_argument("root", help="source directory to scan")
    parser.add_argument("--file", help="restrict to files whose name contains this")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        sys.exit(f"ERROR: {args.root} is not a directory")

    signals = scan(args.root, args.file)
    if args.json:
        for item in signals:
            template, metric, _ = HYPOTHESIS[item["signal"]]
            item["trace_tier"] = "KKE"
            item["hypothesis_tier"] = "H"
            item["hypothesis"] = template.format(**item["facts"])
            item["metric"] = metric
        print(json.dumps(signals, indent=2, ensure_ascii=False))
    else:
        print_report(signals, args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
