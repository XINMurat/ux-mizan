# Recovery — what to do when the audit itself goes wrong

Read this when a run stops behaving: a script did not run, a finding will
not settle, the data contradicts the registry, the premise moved, or the
context has gone soft.

The rest of this skill describes the audit working. This file describes it
**failing**, which is the more common case and the one where the damage is
done quietly. Every ramp below has the same shape:

```
TRIGGER      what you just observed
FIRST MOVE   what to do before anything else
FORBIDDEN    the shortcut that makes the failure invisible instead of fixed
OUTPUT       what you hand back — never "fixed it"
BACKED BY    the gate, rule or script that catches you if you skip this
```

**The ramps are diagnostic, not automatic.** Name the ramp you are on out
loud, in the deliverable. An audit that silently recovered is an audit
whose error rate is unmeasurable — the same objection this skill makes to
deleting `[R]` rows.

---

## The failure classes these ramps exist for

The ramps are the remedies. These are the diseases. They are model failure
modes, not project mishaps: they recur across hosts and models because
they are properties of a producer that is also the judge.

| Class | How it shows up in a UX audit | Ramp |
|---|---|---|
| **Fabrication** | A fluent finding with no file, no line, no mechanism. A cited paper that does not say that. | R-05 |
| **Silent gap-filling** | The model does not know the app's purpose, infers one, and audits against its own inference | R-08, R-10 |
| **Finding inflation** | Twelve findings because twelve looks like work. Severity inflated so the report reads urgent. | R-06 |
| **Tautological measurement** | A metric that cannot come out badly. Lostness on a flow with no declared `canonical_path_R`. | R-03, R-12 |
| **Confirmation of one's own output** | The model that proposed the redesign scores the redesign | R-00 |
| **Optimistic reporting** | "Instrumented", "verified", "confirmed" with no artifact behind it | R-01 |
| **Threshold softening** | The result missed `threshold_support`, so the threshold moves | R-02 |
| **Scope creep** | The audit drifts onto flows Gate 0 never ranked, because they were interesting | R-07 |
| **Fake repair** | A "fix" that changes the finding's wording until it stops failing validation | R-04 |
| **Context decay** | Hour three: tiers still in place, judgment gone, everything reads `[H]` by habit | R-09 |
| **Escape without a class** | A user found it, the screen got fixed, and nothing changed about what the next audit walks or checks. The scorecard counts it; a count is not a loop | R-13 |

A model does not choose these. They are what a producer-judge does under
pressure to look useful, and the only reliable defence is a structure that
notices — which is why each row points at a ramp and most ramps point at a
validator rule.

---

## R-00 — You are about to judge your own output

**TRIGGER.** The next thing you were going to do is score, verify, review
or confirm something produced earlier in this same session — your own
walkthrough, your own redesign, your own spec.

**FIRST MOVE.** Stop and declare the change of role, in the transcript, in
one line:

```
ROLE CHANGE: auditor -> reviewer of my own Layer-A output.
This cannot produce [K]. Highest tier available: [KKE] (independence).
```

Then either hand the artifact to a genuinely separate run, or continue and
cap the tier. Both are acceptable; **an undeclared switch is not.**

**FORBIDDEN.** Reviewing your own output without saying so. Treating a
second model's agreement as independence — `handoff.md` explains why it is
readability, not verification.

**OUTPUT.** The declaration, plus the cap. If a separate run is impossible
in this host, say that instead of pretending it happened.

**BACKED BY.** SKILL.md's load-bearing fact — *if the referee writes it,
there is no `[K]`* — and U1, which rejects a `[K]` with model-side
provenance no matter how the prose frames it.

---

## R-01 — An artifact you promised did not run

**TRIGGER.** No shell, no Python, no PyYAML, no browser; or the script ran
and raised.

**FIRST MOVE.** Diagnose before substituting. Which tool is missing, and
does its absence remove a *capability* or only a *convenience*? Missing
PyYAML removes the validator — that is a capability. A missing browser
during a code-only Layer-A pass is a convenience.

**FORBIDDEN.** Writing the report the script would have written. Prose
shaped like an artifact is a producer-side claim wearing a tool's
credibility, and it is the single most likely way this skill fails
usefully-looking.

**OUTPUT.** The constraint, named in the deliverable: which check did not
run, what the audit therefore cannot claim, and the fallback you used
instead (targeted search, manual walkthrough). An audit under a constraint
is not a smaller audit; it makes a different claim.

**BACKED BY.** SKILL.md, Operating assumptions: *never assume a tool
exists.*

---

## R-02 — Layer-B data refuted a finding

**TRIGGER.** The metric came back and missed `threshold_support`, or hit
`threshold_refute`.

**FIRST MOVE.** Decide, explicitly, which of three things was wrong — and
this decision comes **before** any edit:

1. **The interface** — the finding stands; the fix did not work.
2. **The finding** — the mechanism was wrong. It becomes `[R]`.
3. **The measurement** — wrong metric, wrong instrument, `n` below
   `min_n`, or the metric was not applicable to this `app_type`.

Only (3) permits touching the measurement, and only by fixing the
instrument — never the threshold.

**FORBIDDEN.** Moving `threshold_support` after seeing the number.
Re-running until a favourable sample appears. Quietly rewording the
finding so it no longer says the thing that failed. A near-miss is a
near-miss.

**OUTPUT.** An `[R]` row that stays, with the number that refuted it. The
`[R]` rows are this audit's own error rate; a registry with none is not a
clean audit, it is an unfalsifiable one.

**BACKED BY.** U4 (append-only, `[R]` permanence), U5 (refutability), U8
(`min_n` locked in advance), U6 (metric applicability).

---

## R-03 — The metric is unstable between runs

**TRIGGER.** The same flow measured twice gives materially different
numbers, and nothing about the build changed.

**FIRST MOVE.** Determinise before interpreting. Usual causes, in the
order worth checking: the session-boundary definition moved; `n` is too
small and you are reading noise; the screen-visit log includes a
population the flow never intended (bots, internal users, re-entries);
`canonical_path_R` was inferred after the fact rather than declared.

**FORBIDDEN.** Averaging until it looks stable. Reporting the run that
agrees with your hypothesis. Dropping outliers with no rule written down
before you saw them.

**OUTPUT.** Either a deterministic definition and a re-measurement, or the
instability itself recorded as a `[KKE]` naming `validation` as the
missing control. Instability is a finding about the instrument, which is
worth knowing before it is worth hiding.

**BACKED BY.** `metrics.md` (baseline, `min_n`, the lostness caveats),
U11 (a `[KKE]` must name which control is missing).

---

## R-04 — A shipped change broke a flow that worked

**TRIGGER.** A redesign went out and a metric on a *different* flow got
worse, or a previously-settled finding reopened.

**FIRST MOVE.** Restore the working state first, argue afterwards. A
regression under investigation is a regression still being served to
users.

**FORBIDDEN.** A second change on top of the first to compensate. Deleting
the baseline that shows the regression. Treating "the new one is better
designed" as evidence against a metric.

**OUTPUT.** The kill condition being honoured — `handoff.md` requires
every spec to carry one precisely so this moment has a pre-agreed answer —
plus a new finding for the regression, tiered on its own evidence, and a
note on the original finding recording that its fix regressed. The
original does not become `[R]`: the diagnosis may have been right and the
remedy wrong.

**BACKED BY.** `handoff.md` (KILL CONDITION), U4 (nothing is deleted).

---

## R-05 — A finding you cannot settle

**TRIGGER.** You believe something is wrong but cannot say which file,
which line, which step, or which mechanism. It "feels" cluttered, heavy,
confusing.

**FIRST MOVE.** Do not fix it and do not write it up as a finding. Produce
the **minimal trace**: the smallest concrete thing that would show it
exists — one flow, one step, one file, one signal, one query someone could
run. `structural_checks.py` and `layout_signals.py` exist to turn this
class of intuition into a locatable `[KKE]`.

- **Trace found** → it is a real candidate. Enter it at `[H]` with the
  refutation condition attached, and let Gate 2 decide whether it is worth
  measuring.
- **No trace** → close it with the reason it could not be located. A
  closed intuition is a record; a vague finding in the registry is
  contamination that the next reader cannot distinguish from evidence.

**FORBIDDEN.** "Users get lost in this part." Fixing something you have
not located. Keeping it in the report because it might be right.

**OUTPUT.** Either a located `[KKE]`/`[H]` row, or a written closure. Both
go on the record; only one goes in the backlog.

**BACKED BY.** SKILL.md Anti-patterns, U11, and the positive-control rule
— a check that has never fired on a known case has not earned a finding.

---

## R-06 — The finding count is climbing and the severity is flat

**TRIGGER.** You are past a dozen findings, most are `component-
contributing`, and nothing has been ranked or refuted. Or every finding
came out `severity` high.

**FIRST MOVE.** Stop producing and start refuting. Take the three
highest-severity findings and ask, for each: what result would knock this
down? If a finding has no such result, it is not a finding — it is a
preference, and it belongs at `[S]` or nowhere.

**FORBIDDEN.** Adding a finding because the report looks thin. Raising
`failure_magnitude` to make a low-priority flow's finding surface. Both
are the same move: buying attention the evidence did not earn.

**OUTPUT.** A shorter list with refutation conditions, not a longer list.
Say how many candidates you dropped and why — that number is more
informative than the ones you kept.

**BACKED BY.** U3 (severity is recomputed from the human-locked
`priority_weight`; the model cannot re-rank the backlog), U5, W2.

---

## R-07 — The audit drifted off the locked flows

**TRIGGER.** You are reporting on a screen, module or concern that Gate 0
never ranked.

**FIRST MOVE.** List the drift explicitly — which findings came from
outside Table A. Then park them; do not fold them in.

**FORBIDDEN.** Silently widening scope because the detour was interesting.
An unranked flow has no `priority_weight`, so anything found there cannot
be severity-scored, which means it cannot be honestly prioritised against
what the human said matters.

**OUTPUT.** A parked list offered back at a gate: *"these are outside the
locked scope; add a flow to Table A, or leave them parked."* The human
decides whether the scope grows.

**BACKED BY.** U2 (`parent_flow_id` mandatory and must resolve) — a
finding with nowhere to hang cannot enter the registry anyway. U3 needs
the weight U2 makes reachable.

---

## R-08 — The premise moved mid-audit

**TRIGGER.** The human corrects the job model, re-ranks the flows, or the
product changes what it is for — after findings have already been written
against the old premise.

**FIRST MOVE.** Update the premise **first**, then re-derive. Bump the
Gate-0 version, then walk every existing finding and mark which premise
version it rests on. Findings written against the old premise are not
automatically wrong; they are *unverified against the new one*.

**FORBIDDEN.** Carrying old severities forward under the new weights.
Editing old findings in place to look as though they were always written
against the current premise — that is history falsification in a family
built on append-only.

**OUTPUT.** A new premise version, a re-derived severity ranking, and a
list of findings whose tier dropped because their premise no longer holds.
**Premise drift is itself a finding** and worth reporting: an app whose
purpose is contested is an app whose IA cannot be coherent.

**BACKED BY.** U7 (provenance and premise version on every finding), the
Gate re-opening protocol in `gates.md`.

---

## R-09 — The context has gone soft

**TRIGGER.** Long session. You are reaching for tiers by habit, cannot
remember which gate was locked by whom, or have started summarising
instead of citing.

**FIRST MOVE.** Write the state down and hand over. The registry is the
memory; the transcript is not. Before anything else: flush every settled
finding into `ux-registry.yaml`, run the validator, and write a short
handover block — which gates are locked and by whom, which premise version
is current, which findings are open with what deadline, what runs next.

**FORBIDDEN.** Pushing on because the end feels close. Writing "step
complete" for anything without an artifact behind it. Reconstructing what
Gate 0 said from memory rather than reading the locked record.

**OUTPUT.** A validated registry plus a handover block. A fresh run reads
those two things and loses nothing but the chat.

**BACKED BY.** SKILL.md step 9 (*the registry is the memory*), U12 (an
open finding with no `review_by`, or past it, forces a decision — the rule
that makes drifting findings visible instead of merely old).

---

## R-10 — Uncertainty, or the docs contradict the code

**TRIGGER.** Two readings are defensible; or the spec, the copy and the
implementation disagree about what a screen does.

**FIRST MOVE.** Do not assume. Bring it to the human — **but never
empty-handed.** The proposal rule: whoever brings the question brings
their recommendation and its reason. A bare question moves the work back
onto the person who asked for the audit; a question with a recommendation
costs them one word.

```
SITUATION:      <what is ambiguous, in one sentence>
OPTIONS:        A <...>  B <...>
RECOMMENDATION: A
BECAUSE:        <the reason, tied to Gate 0 or to evidence>
COST IF WRONG:  <what we lose by taking A and being wrong>
```

A docs/code contradiction is additionally **a finding in its own right**:
the users of that screen inherit the same contradiction, and the team has
been reading a description of an app it does not have.

**FORBIDDEN.** Picking the reading that makes the audit tidier. Recording
an inference as though it were a locked answer. Asking four open questions
in a row — that is an interrogation, and it produces rubber-stamping.

**OUTPUT.** A decision from the human, recorded with `locked_by: human`;
or, on a soft gate with no answer, a default recorded as
`locked_by: model-default` and every affected finding capped at `[H]`.

**BACKED BY.** `gates.md` (the proposal rule and the soft-gate defaults),
U7 (`locked_by` provenance).

---

## R-11 — Rolling a redesign back

**TRIGGER.** A kill condition fired, or the human decided to revert.

**FIRST MOVE.** Revert forward, not backward: the rollback is a new event
with its own record, not the erasure of the change. The measurement of the
reverted state is a *new* baseline, and it does not silently replace the
pre-change one.

**FORBIDDEN.** Deleting the finding, the spec or the `[R]` row that the
rollback produced. Reporting the rollback as "we improved it". Reusing the
pre-change baseline as though nothing had happened in between — the
population, the season and the traffic mix all moved.

**OUTPUT.** The kill condition, the number that fired it, the rollback,
and the re-measured baseline. A rollback with its reason recorded is the
most reusable artifact an audit produces: it is the one place where the
skill's own predictions were checked against reality.

**BACKED BY.** U4, `handoff.md` (KILL CONDITION).

---

## R-12 — The target was missed and the temptation is to optimise

**TRIGGER.** A metric did not reach its threshold and someone — possibly
you — is proposing several changes at once.

**FIRST MOVE.** Measure, change **one** thing, re-measure with the *same*
instrument and the same definition. Two simultaneous changes produce one
number and no attribution; the result cannot promote or refute either one.

**FORBIDDEN.** Re-measuring with a different definition and comparing.
Bundling a "while we're here" cleanup into the change. Declaring success
from a metric with no baseline — a number alone means nothing, and this is
the anti-pattern the skill names explicitly.

**OUTPUT.** One change, one attributable delta, and the alternative
explanation hunted as hard as the favourable one. A good result deserves
the same scepticism as a bad one; it just rarely gets it.

**BACKED BY.** `metrics.md` (baseline mandatory, decision rule locked
before collection), U8.

---

## R-13 — A user hit something the audit walked past

**TRIGGER.** A usability problem surfaced after this audit closed — a
support ticket, a session recording, someone watching a real user, a
complaint — and it sits on a flow this audit had locked and walked. Also
fires on the quieter version: a lesson written down as "worth checking next
time" that no check ever received.

**FIRST MOVE.** Record it as an escape before diagnosing it. The pull is to
fix the screen and move on; the fix belongs to the product, the escape
belongs to the method, and only the first of those normally gets written
down.

Then answer one question, and do not let it be skipped: **which check
should have caught this?**

- **A check exists and stayed silent.** Name it — a walkthrough principle,
  a `structural_checks.py` rule, a metric on that flow. The finding is
  about this run, not about the method: the flow was walked past, or the
  check was run and misread, or the metric was not in
  `applicable_metrics`. "We never walked F-007's error path" is a real
  answer and a better one than a new rule nobody needs.
- **No check covers it.** Then write the one that now does, as something
  that can fire on the next audit: a walkthrough question, a structural
  rule, or a metric added to that flow's `applicable_metrics`. A class that
  only matches this ticket catches this ticket and nothing else.

**FORBIDDEN.** Closing an escape with the redesign alone. Counting it in
the scorecard's **Escaped** row and stopping there — the row exists to be
consumed by this ramp, not to be admired. Quietly widening the closed
audit's coverage to include the flow you missed: the escape is evidence
that the coverage claim was wrong, and revising it visibly (R-11) is the
honest move.

**WHY IT IS THE ONE THAT MATTERS HERE.** Every other ramp fires on
something you can see from inside the audit. This one fires on the only
signal that comes from outside it, and a UX audit needs that signal more
than most: the model walks flows it can reach, in an order it chooses,
without the user's goal, history or hurry. The gap between that and a real
session is exactly where escapes live.

**BACKED BY.** The scorecard's **Escaped** row, R-11 (rolling back a
claim), U7 (a premise that moved), Gate 0's locked flow list — an escape on
an unlocked flow is a Gate-0 finding, not an audit failure.

---

## Closing an audit: the process scorecard

Fill this in when a cycle closes — after Gate 4, or when the engagement
ends. Its purpose is **not** to grade the audit. It is to find where the
method leaks, and it only works if it is filled in honestly: a high number
is not a failure, a hidden number is.

| Measure | Value | Reading |
|---|---|---|
| **Premise revisions** | | How many times Gate 0 moved after being locked. High → the purpose was never elicited properly, or the product genuinely has no settled purpose (itself a finding). |
| **Candidates raised / entered** | / | How many intuitions survived R-05. A ratio near 1.0 means nothing was filtered — finding inflation. |
| **Findings refuted (`[R]`)** | | `[R]` rows over total measured findings. **Zero is a warning, not a win**: an audit that has never been wrong has not been tested. |
| **`[KKE]` still open at close** | | Controls never run. This is what the audit does not know, stated as a number. |
| **Ramps used** | | Which R-nn fired. A run that used none either went perfectly or did not notice. |
| **Promotions to `[K]`** | | How much of the audit actually reached evidence, vs. shipped as hypothesis. |
| **Escaped** | | Problems found later that this audit's flows covered and its checks missed. The only measure that comes from outside the audit — and the only one that cannot be gamed from inside it. Each one goes through **R-13** and comes out naming a check: the one that stayed silent, or the one that now exists. A number here that never became a check is the method watching itself fail. |

**Reading:** two or three sentences. Not "the audit went well" — what
would you do differently on the next one, and which number says so.

The scorecard is a claim like any other. Filled in by the same run that
produced the audit, it is `[KKE]` on the `independence` control. Say so.
