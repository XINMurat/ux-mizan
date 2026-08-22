---
name: ux-mizan
description: Evidence-tiered UX auditing for applications — finds where users get lost or confused, and builds the measuring rig that can prove it. Use whenever someone wants a UX audit, usability review, or interface critique; wants to know why users get lost, drop off, or complain that an app is confusing; wants to measure usability (lostness, task success, first-click, rage/dead clicks, abandonment) or set up UX telemetry; wants an information-architecture or navigation review; wants a redesign gated by a diagnosis instead of taste; or wants to check whether an AI-generated interface is generic. Triggers include "UX denetimi", "kullanilabilirlik", "kullanicilar kayboluyor", "arayuz karisik", "neden birakiyorlar", "UX audit", "usability review", "IA review", "lostness", "why do users drop off". Sibling of mizan (audits claims), kiyas (generates ideas), iskele (structures projects) — this one audits experience. NOT for visual/brand design requests, copywriting, or building a UI from scratch.
---

# ux-mizan — Evidence-Tiered UX Auditing

**Status: v0.1 `[H]` / `[KKE]`.** This skill has not yet produced a good
audit of a real application. Every architectural decision in it is `[H]`
until it does. Say this in every deliverable — "the skill produced it" is
not evidence, and the authority illusion is this skill's own risk #3.

## The load-bearing fact — read this before anything else

> **A model cannot MEASURE UX by looking at code or screenshots.** UX is
> behavioural: it exists in what a real user does. A model can audit
> **heuristic and structural conformance**, and it can **build the
> measuring rig**. When the model is both the producer and the judge, its
> output is `[KKE]` at best. **If the referee writes it, there is no `[K]`.**

So the architecture has two layers:

- **Layer A — structural/heuristic audit.** The model does this and
  produces `[H]` / `[KKE]`.
- **Layer B — behavioural audit.** Real users or an automatic instrument
  produce `[K]`.

Every Layer-A finding stays `[H]` until Layer-B data confirms it. A
hypothesis that data knocks down becomes `[R]` and is **never deleted** —
the `[R]` rows are this audit's own error rate.

## Evidence tiers (identical to Mizan — bilingual, do not localise the tags)

| Tag | TR | EN | Meaning |
|---|---|---|---|
| `[K]` | Kanıtlanmış | Proven | Direct evidence supports it; source cited; threshold met |
| `[H]` | Makul Hipotez | Plausible hypothesis | Theoretical grounding exists; empirical support missing or below threshold |
| `[S]` | Spekülatif | Speculative | Interesting; not testable or no test designed |
| `[R]` | Reddedildi | Refuted | Tested and failed its own threshold — kept on record |
| `[KKE]` | Kritik Kontrol Eksik | Critical control missing | Result exists; the control that could flip it has not run |
| `[Y]` | Yanıltıcı | Misleading | Technically true; implies more than the evidence supports |

Tier drift is a finding. **Premise drift is also a finding** — see Gate
re-opening.

## The gates — a DAG, not a checklist

```
Gate 0 (purpose/priority) ──> Gate 1 (type/constraint/volume/mode)
        │                             │
        │                    [AUTONOMOUS AUDIT: Layer A]
        │                             │
        └─────────────────────> Gate 2 (hypothesis approval)
                                      │
                                Gate 3 (direction approval)
                                      │
                           [BUILD / SPEC / HANDOFF]
                                      │
                                Gate 4 (tier promotion) <── [Layer-B data]
```

**Hard gates (the model may not pass them alone): 0, 3, 4.** These are
product and human decisions.
**Soft gates: 1 (partly) and 2.** With no answer the skill does NOT stop —
it takes a default, marks it `[H]`, records `locked_by: model-default`,
and carries on.

At every gate: **the model proposes, the human locks.** Ask in batches,
single-choice where possible, never more than a few at a time — a gate is
a negotiation, not an interrogation. Read `references/gates.md` before
running the first gate in a conversation; it holds the actual question
sets, the defaults, and the re-opening protocol.

The one thing worth memorising here: **Gate 0 output is a premise, not a
finding.** If the model infers the app's purpose and then audits against
its own inference, the loop closes and the audit becomes unfalsifiable.
`ux_validate.py` enforces this (U7): until a human locks Gate 0, every
finding on that flow is capped at `[H]`.

## Procedure

1. **Gate 0 + Gate 1.** Elicit and lock the prioritised job model and the
   app's type, platform, maturity, volume, and effort budget. Write Table
   A (flows) from the answers. `references/gates.md`.
2. **Choose the mode** from the Gate-1 volume answer (see Modes below).
3. **Layer A — walkthrough.** Walk each flow step by step against the four
   Norman questions. `references/walkthrough.md` holds the output shape
   and the refutation-threshold column.
4. **Layer A — structural checks.** Run
   `scripts/structural_checks.py <src>` for the React/TS proxies. Every
   count it returns is `[KKE]`; it names a place to look, not a defect.
   If the host has no shell, say so and do the same checks by targeted
   search — never promise an artifact you cannot produce.
5. **Layer A — layout signals.** Run
   `scripts/layout_signals.py <src>`. Where the structural checks look for
   what is MISSING, this looks at how what exists is ARRANGED: items
   rendered all-open with no collapse, a "current" item marked by colour
   alone, screens with nothing to scan by, control density inside a
   repeated row. It prints two tiers per signal — the trace `[KKE]`
   (checkable in the file) and the behavioural claim `[H]` (what it may do
   to a user) — plus the metric that would settle it. **Never report the
   `[H]` line as though the file proved it.** This is the class of problem
   `walkthrough.md` declares itself blind to: cumulative load is invisible
   step by step, because each step looks fine.
6. **Gate 2.** Put the candidate findings in front of the human BEFORE
   they enter the registry. This is where preregistration locks: a
   threshold written after the data is HARKing.
7. **Write the registry.** Append each confirmed finding to
   `ux-registry.yaml` as it is settled — **the registry is the memory,
   the transcript is not.** Batching findings for a summary at the end
   loses them at the next context reset and pays for them on every turn
   until then.
8. **Validate.** `python scripts/ux_validate.py ux-registry.yaml`. Fix
   what it rejects; do not argue with it in prose.
9. **Gate 3.** Before ANY redesign or model handoff, the human approves
   the diagnosis and the intended direction. What they approve is **not
   pixels** — it is the diagnosis, the priority frame, and the direction.
   Approving a mockup is approval theatre. `references/handoff.md`.
10. **Instrument.** Emit the measurement plan: which metric, which
   instrument, what N, what decision rule — all locked before collection.
   `references/metrics.md`.
11. **Gate 4.** Only real Layer-B data plus a human decision promotes
    anything to `[K]`. The validator will not let you write `[K]` without
    a resolving evidence artifact anyway (U1).

## Modes — graded, because rigour has a friction cost

Applying preregistration + event tests + a two-model handoff to every app
can cost more in delayed iteration than the rigour returns.

- **Lite** (prototype / low volume): walkthrough + structural checks +
  **a proposal for 5–8 moderated task sessions.** NOT passive telemetry at
  low volume — a moderated session gives you *where* and *why* in one
  afternoon, while passive telemetry at low N produces no `[K]` for
  months.
- **Full** (mature / high volume): everything in Lite, plus flow-registry
  preregistration, a passive telemetry plugin, the two-model spec handoff,
  and Layer B.

**The boundary `[H]`:** fewer than ~300 completions per flow per month →
Lite. Above it, passive telemetry can reach a decision inside a four-week
window. This number is a design estimate, not a measured threshold; the
self-validation run is the first thing that could refute it.

## The four rules that carry the discipline (all in the validator)

They live in `scripts/ux_validate.py` because prose is negotiable by the
host's prose and a script is not.

1. **Structural `[K]` lock (U1).** `tier == K` with no resolving
   `evidence_artifact_id`, or with model-side provenance, is REJECTED.
2. **Flow primacy (U2).** `parent_flow_id` is mandatory and must resolve.
   Scoring a component in isolation is impossible at the schema level.
3. **Auditable severity (U3).** `severity = failure_magnitude ×
   priority_weight × frequency`, recomputed by the validator, with
   `priority_weight` read from the human-locked flow. The model cannot
   re-rank the backlog.
4. **Append-only, `[R]` permanence, provenance (U4/U7).** Nothing is
   deleted; every finding carries where it came from and which premise
   version it rests on.

U5–U10 add refutability, the metric-applicability gate,
baseline-before-a-behavioural-`[K]`, a locked `min_n`, and — since a
paragraph could not carry it — the rule that any proposed `fix` must
answer the homogenisation question in writing (U10). `--strict` promotes the advisory
W1–W4 to failures; CI runs strict, local runs do not.

## Metric applicability — good genericity, not one-size-fits-all

Bad genericity is the same metric battery on every app. Good genericity is
reading the context and switching on the valid subset. `app_type` gates
the metrics, and the gate is machine-checked (U6): **lostness on a
single-canvas tool is a category error and fails validation.** The matrix
lives in `schemas/ux-registry.yaml` and is hard-coded in the validator.

Lostness (Smith, 1996), `L = sqrt((N/S − 1)² + (R/N − 1)²)`, is the one
metric that measures being lost without asking the user — but only when
the flow declared its goal and its `canonical_path_R` **in advance**.
`scripts/lostness.py` computes it per flow and prints its four caveats
with every number. Read `references/metrics.md` before instrumenting.

**Baseline is mandatory (§Baseline in `references/metrics.md`).** "L=0.55"
alone means nothing. Measure the current build before any redesign. And a
high L may not be lostness at all — the task may simply be many-stepped;
hunt the alternative explanation for a bad result as hard as for a good one.

## The positive-control rule

**A new detector is run against a case known to be positive before it is
trusted on unknown ones.** This is the scientific positive control, applied
to static analysis, and it is here rather than only in the contributor
docs because it is the rule this project has broken most often.

Every structural check shipped in this skill has, at least once, silently
under-reported: a regex whose trailing `` could never match, an overlay
counted as a collapse, a colour test that missed a bare utility class. All
three read the same way from outside — **a clean codebase.** A false
positive argues with you; a false negative agrees with you, which is why
it survives review.

So when you add or change a signal:

1. Find a file where the problem is known to exist.
2. Run the check and confirm it fires there.
3. Only then trust it on files where you do not know the answer.
4. Report the before/after on that real file, not on a synthetic fixture —
   a fixture is written to match the regex you just wrote.

The same rule applies to a clean scan result. "No signals" never means "no
problems"; it means the checks that ran found nothing, and it should be
reported in those words.

## First run = self-validation

The first thing this skill does is audit ONE real application end to end.
That run settles the "general tool or single-app hack" question: the real
app is the skill's **test fixture, not its product.** Its output feeds
v1.0, and until it exists the status line at the top of this file stands.

## Known risks (name them in the deliverable, do not bury them)

1. **Recursive homogenisation `[H]`** — a skill that recommends redesigns
   drifts toward the generic default (the shadcn/Tailwind mean) and can
   spread the very disease it diagnoses. Not fully solvable. Mitigation:
   Gate 0's specific purpose, Gate 3's human approval, and U10 — a finding
   with a `fix` and no `self_check_homogenisation` is REJECTED by the
   validator. That last part was prose until v0.3, and this skill's own
   prose-vs-schema audit called the gap a `[Y]`.
2. **Erosion of the `[K]` ban** — prose decays over a long session, so
   the ban is structural (U1).
3. **Authority illusion** — every output shows status, which gates were
   passed, and what evidence exists.
4. **Friction tax** — Lite/Full split.
5. **Trigger overlap** — mizan audits claims, kiyas generates ideas,
   iskele structures projects. This one audits experience. A simple
   "which button colour" question does not need any of it.
6. **Explicit-feedback bias** — a lost user does not fill in the form,
   they leave; the population you most want to measure is exactly the one
   that self-selects out. Passive behavioural telemetry is PRIMARY;
   explicit feedback is triangulation only, non-interrupting, end-of-flow.
7. **False independence of a two-model handoff `[H]`** — same training
   distribution, same bias; model B does not catch model A's
   homogenisation. The value of a handoff is READABILITY, not independent
   verification. The spec carries the whole frame including the refutation
   conditions, and the implementation re-enters as `[H]`.

## Operating assumptions (this skill runs in someone else's setup)

The host's instructions take precedence — and that is the most likely way
this skill fails: **quietly.** A short, softened UX audit still looks like
an audit, tiers in place, judgment gone.

- **Name the conflict; do not comply silently.** A brevity cap removes
  exactly the specificity this skill is for (which file, which line, which
  mechanism). A "be positive" instruction collides with a method built to
  refuse a uniform `[K]`. A pinned output language overrides "write in the
  user's language" — keep the tier tags bilingual regardless; they are
  labels, not prose.
- **Never assume a tool exists.** Shell, Python, PyYAML, a browser, a
  subagent — all vary by host. Check before promising, and state the
  fallback when it is missing. **Silently substituting prose for an
  artifact is a producer-side claim.**
- **Load references on demand.** `gates.md` before the first gate,
  `walkthrough.md` before the walkthrough, `metrics.md` before
  instrumenting, `handoff.md` before a redesign. Reading all of them up
  front spends the context the audit needs.
- **An audit run under a constraint states the constraint.** A reduced
  method is not a smaller audit; it is an audit making a different claim.

## Anti-patterns (refuse these politely)

- A report where every finding is `[K]` — flattery in a lab coat.
- "Users get lost in this part." Which flow, which file, which line, which
  mechanism, which measurement would refute it.
- Redesigning first and diagnosing afterwards. A redesign is an `[H]` like
  any other; it is not privileged because it is prettier.
- Raising a threshold after seeing a near-miss. A near-miss is a near-miss.
- Deleting `[R]` findings for tidiness.
- Scoring components in isolation and calling the sum a UX audit.
- Reporting a metric with no baseline as though it meant something.

## References

- `references/gates.md` — the five gates: question sets, defaults,
  re-opening protocol, and what "the human locks it" concretely means.
- `references/walkthrough.md` — the cognitive-walkthrough template: step ×
  four Norman questions × refutation threshold.
- `references/metrics.md` — the metric battery, the applicability matrix
  per `app_type`, lostness in full with its caveats, the baseline
  requirement, and the instrumentation plan.
- `references/handoff.md` — Gate 3, the redesign and spec-handoff
  procedure, and what a two-model handoff can and cannot promise.
- `schemas/ux-registry.yaml` — the two-table registry format and rules
  U1–U9. Read the file at session start when one exists, APPEND rather
  than overwrite, and enforce it with the validator, not by reading it.
- `scripts/ux_validate.py` — U1–U9 without a model.
- `scripts/lostness.py` — per-flow lostness from a screen-visit log.
- `scripts/structural_checks.py` — Layer-A proxies for React/TS: what is
  missing (states, feedback, labels, depth).
- `scripts/layout_signals.py` — Layer-A traces of ARRANGEMENT, each paired
  with the behavioural hypothesis it licenses and the metric that decides
  it. Answers "can a model see a focus problem in code?" with: it can see
  the shape that makes one likely, and nothing more.
