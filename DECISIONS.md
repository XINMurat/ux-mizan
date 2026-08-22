# Open decisions from the handover brief (§11) — resolved

Each decision is tiered like everything else here. None of them is `[K]`:
nothing has run on a real application yet.

## 1. Name — `ux-mizan` `[K]` (as a decision, not as a claim about quality)

`rehber` was already taken by an unrelated product in the same working
set, and a colliding skill name inside one family is a real cost. `ux-mizan` also
states the lineage in the name, which the trigger boundary (risk #5)
benefits from.

## 2. `ux_validate.py` — standalone, not an extension of `mizan_validate.py` `[H]`

The registries are structurally different shapes. Mizan's is
hypotheses/experiments/results with rules R1–R16 built around thresholds
and arbiters; this one is flows/findings built around flow primacy and a
severity formula. Merging them would make every UX registry trip Mizan
rules it was never meant to satisfy (a finding has no `experiment`, no
`baseline` block in Mizan's sense, no `prior_art`), and the false
violations would teach people to pass `--no-verify`.

What IS shared, deliberately and by copy: the tier vocabulary, the
two-channel violation/warning split, the bilingual message catalog
pattern, and the `--against` append-only check. Copied, not imported —
the skill has to run in hosts where the Mizan repo is absent.

**Refutation condition:** if, after the self-validation run, more than
half the rules in each validator turn out to be doing the same work, merge
them. That is a measurable check, not a preference.

## 3. `app_type` — five categories `[R]` → six `[H]`

**The five-category version is REFUTED.** It preregistered its own
refutation condition ("if a real app cannot be classified without a union
of two metric sets, the taxonomy is wrong") and run #1 met exactly that
case on its first target. The refuted version stays below, in place, as the
record of what the design got wrong.

### What broke it

The fixture app's **learning mode** is a server-enforced step sequence:
each step is acknowledged before the next unlocks, progress is stored
server-side, and republishing the underlying content resets it. Against
the five:

- `content-consumption` assumes **no task**. There is a task, and it has a
  completion state.
- `form-heavy-transactional` has the right "prescribed path" premise but
  its metrics are field-level; nothing here is a field.
- `navigational-multiscreen` would switch lostness ON, and lostness is
  meaningless when the server decides the order — a revisit is re-reading.

Classifying it needed `read_completion` + `scroll_depth` from one category
and `task_success` + `step_abandonment` from another. That is the union the
rule forbids.

### The sixth category — `guided-sequence` `[H]`

Switches OFF lostness and nav_depth (order is enforced). Switches ON
`task_success`, `time_on_task`, `step_abandonment`, `read_completion`,
`scroll_depth`, `resume_rate`, `backtrack_rate`. Shipped in schema 0.2.

`resume_rate` is the metric that category exists for: a learner who leaves
mid-sequence and never comes back is the failure this app is about, and no
other category names it.

**Refutation condition (unchanged in form):** the next app that needs a
union refutes this version too. Six is not claimed to be the right number;
it is the number that survived one app.

---

## 3a. The refuted five-category version — kept on record `[R]`

`navigational-multiscreen`, `form-heavy-transactional`,
`single-canvas-tool`, `b2b-internal-dashboard`, `content-consumption`.

Chosen so that each category **switches a metric off**, which is the only
thing that makes a taxonomy load-bearing rather than decorative:

| app_type | what it switches OFF | why |
|---|---|---|
| form-heavy-transactional | lostness | the path is prescribed; failures are field-level |
| single-canvas-tool | lostness, nav_depth | one screen; revisits are work, not wandering |
| b2b-internal-dashboard | sus | a captive user cannot leave — satisfaction is floor-censored |
| content-consumption | task_success | there is often no task to succeed at |
| navigational-multiscreen | (nothing — this is the full battery) | |

A category that switches nothing off would not have earned a row.

**Refutation condition:** if a real app cannot be classified into one of
these without a union of two metric sets, the taxonomy is wrong — split it
or add a category, and record the change here.

## 4. Walkthrough output schema `[H]`

`references/walkthrough.md`: one row per step, columns = step, user goal,
which of the four Norman questions fails, mechanism, location, refutation
threshold, metric, candidate tier. The concrete form of "step × four
questions × refutation threshold" from the brief.

## 5. Registry file — separate from Mizan's `[K]` (as a decision)

`ux-registry.yaml`, its own file, its own validator, discovered by CI on
the `*ux-registry*.y*ml` glob. Same reasoning as #2. A project running
both skills keeps two files side by side; nothing needs them merged.

## 6. Lite/Full boundary — ~300 completions per flow per month `[H]`

The number is an estimate, not a measurement. What it is standing in for:
**can passive telemetry reach the decision rule inside about four weeks?**
At 300/month, a metric with a 10-point effect and a 50/50 split has enough
observations to move; below it, the moderated-session route gives you
*where* and *why* in one afternoon instead of a `[K]` that never arrives.

**Refutation condition:** on the self-validation run, record the actual
volume and how long the first `[H] → [K]` (or `[R]`) flip took. If a flow
above 300/month still could not decide anything in four weeks, the
threshold is wrong and should move — and the wrong version stays in this
file.

---

## What is still open

- **Run #1 is done and stopped at Gate 0** (see `SELF-VALIDATION.md`):
  it found four real defects in `structural_checks.py` and produced no
  finding about the audited app, because purpose was not locked. So the
  status line still stands, and decisions 2, 3, 4 and 6 above remain `[H]`
  — the run tested the Layer-A script, not the gates, the walkthrough, the
  severity formula against a real backlog, or any behavioural metric.
- **Decision 3 (the app_type taxonomy) was tested and refuted** on run #1
  and is now at six categories. The next app that needs a union of two
  metric sets refutes this version too; six is not claimed to be the right
  number, it is the number that survived one application.
- **Whether the two-model handoff is worth its cost.** The brief already
  tiers its independence claim `[H]` and expects it to be false; what is
  untested is whether the readability benefit alone pays for the step.
