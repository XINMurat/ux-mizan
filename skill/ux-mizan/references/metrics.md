# Metrics — the battery, its applicability gate, and the rig

Read before instrumenting anything.

## The three classes and what each can produce

| class | who judges | best tier reachable | examples |
|---|---|---|---|
| **structural** | the model + a script | `[KKE]` | state coverage, orphan pages, generic labels, feedback gaps, nav depth |
| **accessibility** | an automatic instrument | close to `[K]` | axe-core violations, Lighthouse a11y, keyboard-only task completion |
| **behavioural** | a real user | `[K]` | lostness, task success, time on task, first-click accuracy, rage/dead clicks, step abandonment, SUS |

Arrangement is its own sub-class of structural, and `scripts/layout_signals.py`
covers it: density, expansion, and how the current item is marked are
readable from source even though the failure they cause -- losing track of
what to do now -- is not. The script therefore emits the trace and the
hypothesis as SEPARATE tiers, and the hypothesis is decided by
`time_on_task` or `first_click_accuracy` like any other behavioural claim.
Reporting the hypothesis alone, with the file cited as if it were
evidence, is the `[Y]` this split exists to prevent.

A structural count is `[KKE]` **by construction**, not by caution: it
reports a shape associated with confusion, and the control that would tell
you whether this instance actually confuses anyone has not run.

Keyboard-only task completion deserves its place beside the behavioural
ones: it is cheap, automatic, and a good predictor of getting lost —
a flow that cannot be completed by keyboard usually has a focus order that
does not match its visual order, which is a lostness mechanism.

## Applicability — the gate that makes genericity good

Bad genericity: the same battery on every app. Good genericity: read the
context, switch on the valid subset, and **switch the rest off explicitly**
so nobody quietly reports them later.

`app_type` gates the metrics. The full matrix lives in
`schemas/ux-registry.yaml` and is hard-coded in `ux_validate.py`
(`METRIC_MATRIX`), which checks two hops: the flow may only list metrics
its `app_type` allows, and a finding may only use a metric its flow lists.

The gates that matter most, and why:

- **`single-canvas-tool` switches lostness and nav_depth OFF.** There is
  one screen. Revisits are work, not wandering. Reporting L here is a
  category error, and the validator rejects it.
- **`form-heavy-transactional` switches lostness OFF.** The path is
  prescribed; failures are field-level. Use field error rate, field retry
  rate, validation timing, step abandonment.
- **`b2b-internal-dashboard` switches SUS OFF as a headline.** A captive
  user cannot leave, so satisfaction scores are floor-censored and move
  for reasons unrelated to the interface. Task success and time on task
  still move.
- **`content-consumption` switches task_success OFF.** There is often no
  task. Scroll depth, read completion and return rate carry the signal.

## Lostness (Smith, 1996) — measuring lost without asking

```
L = sqrt( (N/S - 1)^2 + (R/N - 1)^2 )

N = distinct screens visited during the task
S = total screens visited, repeats included
R = minimum screens required to complete it  (canonical_path_R)
```

Range 0–1. Smith's cut-offs: **L > 0.5 lost**, **L < 0.4 not lost**,
0.4–0.5 undecided.

**The bridge that makes it work passively:** if the flow declares its goal
and its `R` IN ADVANCE, L can be computed from ordinary screen-view
telemetry with no user-facing instrument at all. That is the answer to
"a log cannot measure being lost". The advance declaration is the whole
trick — `R` inferred after seeing the data is HARKing, and
`scripts/lostness.py` refuses to guess it.

Four caveats, and they travel with every number:

- **(a) Navigational types only.** Enforced by the matrix, not by memory.
- **(b) L says WHERE, never WHY.** Read it beside rage-click, dead-click
  and backtrack rates. On its own it names a flow, not a cause.
- **(c) Per flow, never global.** A single app-wide L number averages
  unrelated tasks into a figure that cannot be acted on.
- **(d) The 0.4/0.5 cut-offs come from hypertext studies** and are NOT
  validated for your app type. Use your own baseline as the comparison
  point; treat Smith's numbers as orientation, not as a threshold you may
  lock against.

Separate completed sessions from abandoned ones before averaging.
Abandonment has no completion path, and mixing the two silently blends
"wandered" with "gave up" — two different findings with two different
fixes.

## Frustration signals — borrow the operational definition, then say whose

`rage clicks` and `dead clicks` appear in the behavioural battery, and the word
alone is not a metric: two tools counting "rage clicks" on the same session can
disagree by a factor of three because they define the window differently. So
take the definition from the instrument you will actually use, cite it, and put
it in the registry beside the number.

PostHog's is a usable reference point because it is written down and
configurable: a `$rageclick` fires on **three clicks, each within 30 px and
1000 ms of the one before** — and all three of those are settings, not
constants. A dead click is a click on something interactive that produces no
navigation, no state change and no visible feedback within a short window;
the window is again a setting.

Two consequences worth writing into the entry rather than discovering later:

- **The number belongs to its instrument.** A rage-click count measured under
  3/30px/1000ms is not comparable to one measured under 5 clicks or a 2-second
  window, and it is not comparable across tools at all. A threshold calibrated
  on one instrument is never inherited by another — the same rule the metric
  battery applies to every other number here.
- **These are frustration proxies, not lostness.** A rage click says a user
  hit something that did not answer; it does not say they could not find their
  way. Read them *beside* lostness and step abandonment, never as a substitute:
  a flow can score clean on rage clicks and still lose people silently, which
  is the failure mode explicit feedback also misses.

If you instrument these, record the three parameters in the flow's registry
entry the way `min_n` is recorded — before collection, not after.

## Baseline — mandatory, and prior to any redesign

"L = 0.55" alone is meaningless. Good and bad exist only against a
comparison point. So: **measure the current build before you change it**,
write the numbers into the flow's `baseline.values`, and compare against
them. U8 blocks a behavioural `[K]` on a flow with no measured baseline,
because without one the promotion is comparing a number to a folk memory.

And hunt the alternative explanation for a bad result as hard as for a
good one: a high L may not be lostness at all — the task may be
intrinsically many-stepped, or the flow may be used by two populations
with different paths. Mizan's rule about surprising positives applies
symmetrically here.

## The instrumentation plan (what Gate 3 hands to engineering)

For each finding being instrumented, lock all six BEFORE collection:

1. **Metric** and its `kind`.
2. **Instrument** — the concrete thing that returns the verdict. Not "the
   model". A named analytics event, an axe-core run, a session protocol.
3. **N** and the **decision rule**, written out: "8 moderated sessions;
   supported if ≥ 5 fail step 3 at first click".
4. **The two-sided threshold** — what supports, what refutes.
5. **Who collects it**, and who is NOT the model.
6. **The honesty annexes you already know you will owe**: recruitment
   bias, single-session caveats, instrument dependence.

### Silent-failure guard

An analytics event that stops firing looks exactly like a metric that
improved. Before trusting any passive measurement, ship a test that
asserts each event fires on the path it claims to watch, and re-run it
with every release. An un-tested event pipeline turns "we fixed it" and
"we broke the logging" into the same graph.

### Low volume changes the primary instrument

At low N, passive telemetry produces no `[K]` for months. **5–8 moderated
task sessions give you where AND why in one afternoon.** Passive telemetry
is primary only when volume is genuinely sufficient — that is the Lite/Full
split, and it is a correction of the intuition that passive is always
better.

### Explicit feedback is triangulation only

A lost user does not fill in your form; they leave. Explicit feedback
systematically under-samples exactly the population you are trying to
measure. Use it non-interrupting and end-of-flow, and never as the primary
signal for a lostness or abandonment finding.

## The last `[KKE]`

All telemetry, lostness included, is a **proxy** for being lost, not the
thing itself. A low L does not say "the user is not lost"; it says "the
known navigational signature of being lost is absent". The closest this
method gets to `[K]` is the point where L and real task success — or a
handful of moderated sessions — point the same way.
