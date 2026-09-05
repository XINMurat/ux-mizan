# Reference

An index, not a second copy of the method. The methodology lives in
[`skill/ux-mizan/`](../../skill/ux-mizan/) — the same files Claude loads —
so it cannot drift from what actually runs.

## Where each topic lives

| Topic | File |
|---|---|
| Triggering, the two layers, the gate DAG, modes, risks, anti-patterns | [`SKILL.md`](../../skill/ux-mizan/SKILL.md) |
| Gate question sets, defaults, the re-opening protocol | [`references/gates.md`](../../skill/ux-mizan/references/gates.md) |
| Cognitive-walkthrough template and its blind spots | [`references/walkthrough.md`](../../skill/ux-mizan/references/walkthrough.md) |
| Metric battery, applicability matrix, lostness, baselines, instrumentation plan | [`references/metrics.md`](../../skill/ux-mizan/references/metrics.md) |
| Gate 3, redesign, spec handoff, what a two-model handoff cannot promise | [`references/handoff.md`](../../skill/ux-mizan/references/handoff.md) |
| Recovery ramps R-00…R-13, the model failure classes, the closing scorecard | [`references/recovery.md`](../../skill/ux-mizan/references/recovery.md) |
| Registry format and the rules in comment form | [`schemas/ux-registry.yaml`](../../skill/ux-mizan/schemas/ux-registry.yaml) |

## Evidence tiers

| Tag | TR | EN | Meaning |
|---|---|---|---|
| `[K]` | Kanıtlanmış | Proven | Direct evidence; source cited; threshold met |
| `[H]` | Makul Hipotez | Plausible hypothesis | Grounded; empirical support missing or below threshold |
| `[S]` | Spekülatif | Speculative | Interesting; not testable, or no test designed |
| `[R]` | Reddedildi | Refuted | Tested and failed its own threshold — kept on record |
| `[KKE]` | Kritik Kontrol Eksik | Critical control missing | Result exists; the control that could flip it has not run |
| `[Y]` | Yanıltıcı | Misleading | Technically true; implies more than the evidence supports |

The tags are labels, not prose: keep them bilingual in every language.

## The rules the validator enforces

| Rule | What it rejects |
|---|---|
| **U1** | `[K]` with no resolving `evidence_artifact_id`, or with model-side `source_provenance`; an evidence artifact with no honesty annexes |
| **U2** | A finding with no `parent_flow_id`, or one that does not resolve |
| **U3** | A `severity` that does not equal `failure_magnitude × priority_weight × frequency`; a finding that restates `priority_weight` |
| **U4** | A flow or finding present in the baseline and missing now; an entry moved out of `[R]` (needs `--against`) |
| **U5** | A finding with no `refutation_condition`, no `metric.name`, no named `metric.instrument`, or an invalid `metric.kind` |
| **U6** | A metric absent from the flow's `applicable_metrics`; an `applicable_metrics` entry the flow's `app_type` does not switch on |
| **U7** | A flow with no `gate_provenance`; `[K]`/`[R]` on a flow whose Gate 0 is not human-locked; a finding citing a stale premise version |
| **U8** | `[K]` on a behavioural metric whose flow has no measured baseline for it |
| **U9** | `[K]` with no `min_n.n` or no `min_n.decision_rule` |
| **U10** | A finding proposing a `fix` with no `self_check_homogenisation` answer |
| **U11** | A `[KKE]` finding with no `kke_kind`, an invalid one, or the field left on an entry that is no longer `[KKE]` |

`kke_kind` says WHICH control is missing: `control` (a confound check that
could flip it has not run) · `independence` (the producer of the claim is
also its judge) · `data` (the measurement is designed, the data is not in)
· `validation` (the instrument itself was never run against a
known-positive case). A field, not four new tags — the six tiers are what
the four sibling skills share, and Mizan already carries two of these
reasons without naming them (R2 missing data, R8 missing independence).

| Warning | What it flags (advisory; `--strict` promotes) |
|---|---|
| **W1** | Every tiered finding is `[K]` |
| **W2** | No `flow-level` finding exists |
| **W3** | A flow with no measured baseline |
| **W4** | An open finding with no owner and no scheduled measurement |

```bash
python skill/ux-mizan/scripts/ux_validate.py --lang tr --strict ux-registry.yaml
python skill/ux-mizan/scripts/ux_validate.py --against HEAD ux-registry.yaml
```

## The metric matrix

Each `app_type` earns its row by switching a metric **off**. A category
that only adds is decoration.

| app_type | switched OFF | why |
|---|---|---|
| `navigational-multiscreen` | — | the full battery |
| `form-heavy-transactional` | lostness | the path is prescribed; failures are field-level |
| `single-canvas-tool` | lostness, nav_depth | one screen; revisits are work, not wandering |
| `b2b-internal-dashboard` | sus | a captive user cannot leave; satisfaction is floor-censored |
| `content-consumption` | task_success | there is often no task |
| `guided-sequence` | lostness, nav_depth | the server enforces the order; a revisit is re-reading |

The matrix is hard-coded in `ux_validate.py` (`METRIC_MATRIX`) as well as
documented in the schema. If the two ever disagree, the validator is the
one that runs, and the disagreement is itself a finding.

## Scripts

| Script | Produces | Tier of its output |
|---|---|---|
| `ux_validate.py` | U1–U12 verdicts, W1–W4 warnings | — (it checks, it does not claim) |
| `structural_checks.py` | State coverage, feedback gaps, generic labels, nav depth, orphan routes | `[KKE]` — what is missing |
| `layout_signals.py` | Arrangement traces + the behavioural hypothesis each licenses | trace `[KKE]`, claim `[H]` |
| `lostness.py` | Per-flow L, completed and abandoned reported apart | needs Layer-B data to mean anything |

## Two rules that are not in any script

Both are in prose, and both are load-bearing. They are listed here because
`PROSE-SCHEMA-AUDIT.md` names them as gaps rather than hiding them:

1. **Open the file before writing a finding.** `location` must be
   non-empty; nothing checks that it says what the mechanism claims. This
   rule caught every scanner defect this repo has shipped.
2. **A new detector runs against a known-positive case before it is
   trusted on unknown ones.** Every structural check here has shipped a
   silent under-report at least once, and an under-reporting checker is
   indistinguishable from a clean codebase. This one moved from the
   contributor docs into `SKILL.md` after an external review pointed out
   it was written everywhere except the file that travels into a host —
   still unscripted, but no longer invisible to the tool that must obey
   it.
