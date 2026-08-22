# Self-validation run #1 — target: a real internal application

Date: 2026-08-22 · Skill version: v0.1 → v0.2 (this run bumped it) · Run status: **stopped at Gate 0**

Per the brief (§8.4), the first run exists to test the SKILL, not the app.
The fixture is a live in-house application for institutional process
memory — a React/TypeScript front end with about ten routed screens,
serving three audiences on the same data: people running processes,
people authoring them, and newcomers learning them. It is described here
rather than named, because the audit belongs to its owner and this
document belongs to the skill.

This file records what the run found **about ux-mizan**. The findings
about the fixture stay with its owner, and in any case none existed at the
point this run stopped: Gate 0 was unanswered, and `references/gates.md`
says the audit may not rank anything until purpose is locked.

## What ran

- `scripts/structural_checks.py <app>/src` — 136 source files,
  Vite + React + TypeScript + shadcn/Radix, 10 routed pages.
- Nothing else. No walkthrough (needs Gate 0), no registry (findings need
  a `parent_flow_id`, and flows come from Gate 0/1).

## Findings about the skill `[K]` — the checker was measurably wrong

Arbiter: the runtime. Same command, same codebase, different output before and after; anyone can re-run it.

Four defects in `structural_checks.py`, all found by running it on real
code and all fixed in this pass. They share one shape: **the checker
under-reported, and an under-reporting checker is indistinguishable from a
clean codebase.**

| # | Defect | Effect on the first output | Fix |
|---|---|---|---|
| 1 | Trailing `\b` after alternatives ending in a non-word character (`useEffect(`, `axios.`, `alert(`, `confirm(`) — a word boundary can never follow `(` or `.`, so those alternatives matched nothing | Reported **1 async view** in an app with ten data-loading pages; `state_coverage_ratio` read a perfect `1.0` | Dropped the trailing `\b`; non-capturing groups |
| 2 | `RE_ERROR`/`RE_LOADING` matched whole words only | A page holding `processesError` and `loadingProcesses` counted as handling neither | Prefix/suffix tolerant patterns |
| 3 | A bare `useEffect(` counted as an "async view" | Providers, a theme toggle and a `use-mobile` hook padded the denominator | An async view now needs a real data call |
| 4 | `RE_FEEDBACK` matched `\bnotify\b`, missing `notifyDone`; the mutation heuristic matched pure helpers like `deleteImpact(...)` | 17 "feedback gaps", nearly all false | Prefix matching for feedback (plus `navigate(` as feedback); mutations must be `await`ed |

Numbers before and after the fixes, same codebase, same command:

```
before:  state_coverage_ratio 1.0 (1/1)    feedback_gap_count 17
after:   state_coverage_ratio 0.324 (11/34) feedback_gap_count 0
```

Both readings were wrong in opposite directions, which is the useful part:
the first flattered the app, the second cried wolf. A structural checker
has two failure modes and this run produced both within an hour.

## What this says about the architecture `[H]`

- **The `[KKE]` label on structural output was doing real work.** Had the
  first run's `1.0` coverage ratio been reportable as evidence, the audit
  would have blessed a codebase it had barely read.
- **The "open the file before writing a finding" rule in
  `references/walkthrough.md` is what caught defects 1 and 4.** The counts
  looked plausible; the files did not match them. A workflow that lets a
  count become a finding without opening the file would have shipped all
  four defects into a registry.
- **Untested by this run:** the gates, the walkthrough template, the
  severity formula against a real backlog, and every behavioural metric.
  None of them can be exercised until Gate 0 closes. The validator's rules
  were tested against fixtures, not against a real registry.

## What is still `[H]` and now has a sharper test

- The Lite/Full boundary (~300 completions/flow/month). the fixture's real
  volume is unknown; Gate 1 asks for it.
- ~~The five-category `app_type` taxonomy.~~ **Tested and refuted** — see
  below.

## Finding about the skill `[KKE]` — the app_type taxonomy is refuted

The five-category taxonomy of schema 0.1 preregistered its own refutation:
"if a real app cannot be classified without a union of two metric sets, the
taxonomy is wrong." The fixture's **learning mode** met that condition on
the first target the skill ever saw.

Learning mode opens steps in a server-enforced order, each acknowledged
before the next unlocks, progress stored server-side and reset when the
process is republished. It is a
task with a completion state (so `content-consumption`'s "no task" premise
is false), on a prescribed path (so lostness is meaningless — the server,
not the user, chooses the order), and made of prose that must actually be
read (so `form-heavy-transactional`'s field metrics say nothing about it).
Classifying it required `read_completion` + `scroll_depth` from one
category and `task_success` + `step_abandonment` from another.

Schema 0.2 adds `guided-sequence`, which switches lostness and nav_depth
off and adds `resume_rate` — the metric that category exists for, since a
learner who leaves mid-sequence and never returns is precisely the failure
this product is about. The refuted five-category version is kept in
DECISIONS.md §3a, not edited away.

**Why `[KKE]` and not `[K]`:** the premises are checkable in the repo
(the server enforces step order; progress resets on republish),
but the judgment "this cannot be classified without a union" is the
author's own, and this skill's U1 forbids the model that produced a
finding from also promoting it. The missing control is cheap: hand the
five categories and the learning mode to a second reader, or to the next
app, and see whether they reach for a union too.

This is still the run doing what §8.4 of the brief asked of it: the real
app is the fixture, and it broke a design decision on contact.

## Reading the app properly changed the draft job model

The owner's description and one of the project's own design documents
named a job the route-only draft had missed entirely — and it was the
north-star one: **knowledge is distilled bottom-up.** A person records
what they learned while doing the work as a personal note, and an editor
later promotes it into the official process.

A UX audit driven by the route list would have weighted "edit a process"
as the primary job and treated personal notes as a side feature. That is
the closed-loop failure Gate 0 exists to prevent — and it nearly happened
here, in the run that was supposed to demonstrate the gate. The lesson
generalises past this fixture: **routes show what an app CAN do, never
what it is FOR**, and only the owner holds the second one.

## New capability, and the finding that forced it `[KKE]`

Users of the audited app reported that execution "reads as nested,
sequential text with no separation -- we cannot tell what to do when".
`structural_checks.py` could not see it, and the reason is structural:
that script looks for what is MISSING (a loading state, a feedback path,
a label), and here nothing was missing. An arrangement cannot be absent.

`references/walkthrough.md` already declared this blind spot in writing --
"it cannot see load: cumulative cognitive load across a long flow is
invisible step by step, each step looks fine" -- so the gap was predicted
and unfilled. `scripts/layout_signals.py` fills it, with the two-tier
output the architecture requires:

  [KKE] the trace       one screen renders 6 child parts per repeated
                        item across 111 lines with no collapse, and marks
                        the current item with a difference of
                        "border-2 border-primary/50" against "border
                        border-border" -- colour only.
  [H]   the claim       users re-derive "what now" from content instead
                        of reading it off the arrangement
  metric                time_on_task / first_click_accuracy

**The tool was validated the only honest way available: it had to
rediscover, unaided, the trace that had been found by hand.** It did --
after three of its own bugs were fixed, all of the same shape as the
first run's:

  1. Sheet/Dialog/Popover counted as "collapse", so any row with an
     overlay silenced the signal it existed for.
  2. The current-item ternary had to be on one line; prettier puts the
     branches on their own lines, making the signal unfirable in exactly
     the codebases it targets.
  3. Tailwind's bare utilities ("border", "shadow") have no dash, so the
     colour-only test missed the canonical case.

Three for three, the same failure mode as run #1: **the checker
under-reported, and an under-reporting checker looks exactly like a clean
codebase.** That is now this project's most repeated finding about itself,
and it is worth naming as a rule rather than a coincidence -- a new
detector must be run against a case that is known to be positive before it
is trusted on cases that are unknown.

## Where the run stopped, and why

Gate 0 is hard. The model can read the routes and guess the jobs; auditing
against its own guess closes the loop and makes the audit unfalsifiable
(U7 enforces this). So the run stops here with a **draft** for a human to
correct and lock:

The eight candidate jobs drafted for it stay with the owner. What belongs
here is their shape: two of the eight were the product's north-star pair
and were absent from the route-only draft, and a third was the flow that
refuted the app_type taxonomy. Three of the eight needed a different
`app_type` from the one the routes suggested.



Gate 0 needs: the ranking, a `priority_weight` per job, what "done" means
for each, and the `success_screen` that marks it. Gate 1 needs: `app_type`
per flow, maturity, monthly completions per flow, and the effort budget.

Until those are locked, this run has produced findings about ux-mizan and
none about the application — which is the correct outcome, not a
shortfall.
