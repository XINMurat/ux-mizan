# Usage Guide

**Status: v0.2 `[H]`.** One self-validation run has happened: it exercised
the Layer-A scripts and refuted one design decision. The gates, the
walkthrough and every behavioural metric remain untested.

## Install

```bash
cp -r skill/ux-mizan ~/.claude/skills/     # path must end .../skills/ux-mizan/SKILL.md
pip install -r skill/ux-mizan/scripts/requirements.txt
cp templates/ux-registry.yaml <your-project>/ux-registry.yaml
```

The usual mistake is a doubly-nested folder. For Claude.ai and desktop,
upload `ux-mizan.skill` (Settings → Capabilities → Skills) and re-upload
to update.

## When it triggers, and when it should not

**Triggers:** UX audit, usability review, "users get lost", "the interface
is confusing", "why do they drop off", IA review, setting up usability
measurement, a redesign gated by a diagnosis.

**Does not:** visual or brand design, copywriting, building a UI from
scratch. "What colour should this button be" does not deserve this weight.

**Boundary with its siblings:** Mizan audits claims, Kıyas generates ideas,
İskele structures projects. This one audits experience.

## The flow

### 1. Gate 0 — purpose and priority (HARD)

The model proposes a draft; **a human locks it**. Until then no finding on
that flow can leave `[H]` (U7). The reason is structural: if the model
infers the purpose and audits against its own inference, the loop closes
and the audit becomes unfalsifiable.

What gets locked: the jobs in the user's words rather than feature names,
a `priority_weight` for each, what "done" means, and the route that marks
it (`success_screen`).

### 2. Gate 1 — type, volume, mode

`app_type` is chosen per flow and **decides which metrics are even valid**:

| app_type | what it switches OFF |
|---|---|
| `navigational-multiscreen` | — (the full battery) |
| `form-heavy-transactional` | lostness (the path is prescribed) |
| `single-canvas-tool` | lostness, nav_depth (one screen) |
| `b2b-internal-dashboard` | sus (a captive user; floor-censored) |
| `content-consumption` | task_success (often no task) |
| `guided-sequence` | lostness, nav_depth (the server enforces order) |

Volume picks the mode: **below ~300 completions per flow per month →
lite**. At low volume passive telemetry decides nothing for months, while
5–8 moderated sessions give *where* and *why* in one afternoon.

### 3. Layer A — walkthrough and scripts

```bash
python skill/ux-mizan/scripts/structural_checks.py src/     # what is missing
python skill/ux-mizan/scripts/layout_signals.py src/        # how it is arranged
```

Every count is `[KKE]`: a place to look, not a defect. `layout_signals`
prints two tiers per signal — the trace `[KKE]` and the behavioural claim
`[H]` — and reporting the `[H]` line as though the file proved it is
exactly the `[Y]` the split prevents.

**Open the file before writing a finding.** Both scripts in this repo have
shipped false negatives *and* false positives, and that rule is what
caught every one of them.

### 4. Gate 2 — hypothesis approval

Candidates go to the human **before** they enter the registry. This is
where preregistration locks: a threshold written after the data is HARKing.

### 5. Registry and validation

```bash
python skill/ux-mizan/scripts/ux_validate.py --strict ux-registry.yaml
git config core.hooksPath tools/hooks
```

**The registry is the memory, the transcript is not.** Append each finding
as it settles; batching them for a summary at the end loses them at the
next context reset.

### 6. Gate 3 — direction approval (HARD)

The human approves the **diagnosis, the priority frame and the
direction** — not pixels. Showing a mockup and asking whether they like it
is approval theatre.

Mandatory self-check per proposal: *does this follow from THIS app's
Gate-0 purpose, or is it the generic default?* "It is the generic default
and that is right here" is a fine answer; not asking is not.

### 7. Measurement and Gate 4

Measure the baseline **before** any redesign — there is no second chance
to measure the "before". `[K]` comes only from real Layer-B data plus a
human decision, and the validator refuses to write it without a resolving
evidence artifact anyway.

## Lostness

```
L = sqrt( (N/S − 1)² + (R/N − 1)² )
```

If a flow declares its goal and `canonical_path_R` **in advance**, L can be
computed passively from ordinary screen-view telemetry. The advance
declaration is the whole trick — R inferred after the fact is HARKing, and
the script refuses to guess it.

```bash
python skill/ux-mizan/scripts/lostness.py events.jsonl --registry ux-registry.yaml
```

Four caveats print beside every number: navigational app types only; it
says *where*, never *why*; it is per flow, never global; and Smith's
0.4/0.5 cut-offs come from hypertext studies and are not validated for
your app type — compare against your own baseline.

## The hard rules (U1–U9)

| rule | what it does |
|---|---|
| U1 | `[K]` needs a resolving evidence artifact and a non-model source |
| U2 | `parent_flow_id` mandatory and must resolve — flow primacy |
| U3 | severity recomputed; weight read from the human-locked flow |
| U4 | append-only; `[R]` entries cannot be moved out |
| U5 | refutation condition and a named instrument required |
| U6 | metric applicability gate (two hops: app_type → flow → finding) |
| U7 | gate provenance; unlocked Gate 0 caps findings at `[H]` |
| U8 | a measured baseline before any behavioural `[K]` |
| U9 | a locked `min_n` and decision rule before `[K]` |

W1–W4 warn without blocking; `--strict` promotes them. CI runs strict,
local runs do not — a tool that can only block teaches people to write
registries that never trigger it.
