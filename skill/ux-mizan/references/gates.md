# The gates — human-in-the-loop protocol

Read this before running the first gate in a conversation.

A gate is a negotiation, not an interrogation. **The model proposes, the
human locks.** Ask in batches, prefer single-choice, never more than three
or four questions at once. Fatigue produces rubber-stamping, and a
rubber-stamped Gate 0 is worse than no Gate 0: it looks like a premise and
carries none of the authority.

Hard gates (0, 3, 4) the model may not pass alone. Soft gates (1 partly, 2)
degrade gracefully: with no answer, take a default, record
`locked_by: model-default`, mark the affected findings `[H]`, and continue.

## The proposal rule — applies at every gate, and to every open question

**Whoever brings the question brings their recommendation and its reason.**
Not only at Gate 0, where "the model proposes first" is written out below,
but at every gate, every open item, every ambiguity found mid-audit.

```
SITUATION:      <what is undecided, one sentence>
OPTIONS:        A <...>  B <...>
RECOMMENDATION: A
BECAUSE:        <tied to Gate 0 or to evidence, not to taste>
COST IF WRONG:  <what taking A and being wrong costs>
```

Two reasons this is a rule and not a courtesy. It makes the model's
reasoning **inspectable** — a recommendation can be disagreed with, a bare
question cannot. And it changes what the human has to do from *think about
this from scratch* to *confirm or correct*, which is the difference
between a gate that gets read and a gate that gets rubber-stamped.

The decision still belongs to the human. **A recommendation is not an
approval, and an unanswered recommendation is not consent** — on a hard
gate it blocks; on a soft gate it becomes a `locked_by: model-default`
with the findings capped. Recording your own recommendation as though it
were the answer is the loop-closing move U7 exists to prevent.

---

## Gate 0 — Purpose and priority (HARD)

**What it produces:** the prioritised job model that becomes Table A, and
the `priority_weight` on every flow.

**Why it is hard:** "what matters here" is a product decision. If the model
infers the purpose and then audits against its own inference, the loop
closes and nothing can refute the audit. U7 enforces this — until
`gate_0.locked_by == "human"`, findings on that flow cannot leave `[H]`.

**The model proposes first.** Read the app, then present a draft: "these
look like the three or four jobs this app exists to do, in this order.
Correct me." A blank-page question wastes the human's time; a wrong draft
gets corrected in one line.

Elicit:

1. **The jobs.** Primary / secondary / tertiary tasks, in the user's words,
   not in feature names. "Get paid for an invoice", not "invoicing module".
2. **`priority_weight` per job** (0.0–1.0). Ask for a rank first and turn
   it into weights; people rank more reliably than they score.
3. **The north-star value path**, if there is one — the single sequence
   whose completion is the reason the app exists.
4. **"What counts as success"** per job. This becomes `success_definition`
   and, downstream, the success screen the lostness script looks for.
5. **Who the user is** — enough to tell an expert daily-use flow from a
   once-a-year first-timer flow. The same interface fails differently for
   each.

**Default if unanswered:** do NOT proceed to a full audit. This is the one
gate with no safe default — record the refusal, run Layer-A structural
checks only (they are flow-independent counts), and say plainly that the
audit cannot rank anything until purpose is locked.

---

## Gate 1 — Type, constraint, volume, effort budget (partly HARD)

**What it produces:** `app_type` (which decides which metrics are even
valid), the mode, and the realism of the whole plan.

Elicit, in one batch:

1. **App type** — pick one per flow:
   `navigational-multiscreen` / `single-canvas-tool` /
   `form-heavy-transactional` / `b2b-internal-dashboard` /
   `content-consumption`. An app that is genuinely two of these gets two
   flows, never one flow with the union of both metric sets.
2. **Platform** — web / iOS / Android / desktop. Decides what can be
   instrumented at all.
3. **Maturity** — prototype or live. A prototype has no telemetry to read
   and no users to lose.
4. **Volume** — completions per flow per month. This picks the mode:
   below ~300 → Lite. `[H]`, a design estimate; the number that matters is
   whether passive telemetry can reach your decision rule in four weeks.
5. **Effort budget** — hours or days the team can actually spend. An audit
   that proposes more work than the budget produces a backlog nobody runs,
   which measures nothing.

**Defaults if unanswered:** app_type inferred from the code and marked
`model-default`; maturity from whether analytics exist; mode = Lite (the
cheaper wrong answer); effort budget = "unknown, plan the top-3 fixes
only". Every default is written into `gate_provenance` where it is
visible, not assumed silently.

---

## Gate 2 — Hypothesis approval (SOFT)

**What it produces:** the preregistration lock. Candidate findings go in
front of the human *before* they are written to the registry, with their
thresholds attached.

Present each candidate in one line: flow, mechanism, the measurement that
would refute it. The human confirms, corrects, or kills it. Corrections at
this gate are cheap; corrections after the threshold is written are
HARKing.

**Default if unanswered:** write the candidates as `[H]` with
`source_provenance: structural-check` or `walkthrough`, and note in the
report that Gate 2 was unanswered. Do not stop.

---

## Gate 3 — Direction approval (HARD)

**What it produces:** permission to design, spec, or hand off.

**What the human approves is NOT pixels.** It is:
- the **diagnosis** (this flow fails here, by this mechanism),
- the **priority frame** (this is worth fixing before that, and why),
- the **intended direction** (we will change the navigation model, not
  the button styling).

Showing a mockup and asking "do you like it?" is approval theatre: it
produces a signature on something the human cannot evaluate, and it
launders the model's taste into an authorised decision. If the human wants
to see something, show the diagnosis and two directions that differ in
kind, not two skins of the same one.

At this gate, ask the homogenisation question out loud for each proposed
direction: **does this follow from Gate 0's specific purpose, or is it the
generic default?** The answer goes into
`self_check_homogenisation` on the finding. "It is the generic default and
that is fine here" is an acceptable answer; not asking is not.

---

## Gate 4 — Tier promotion (HARD)

`[K]` is given by real Layer-B data plus a human decision. The validator
already blocks the mechanical part (U1, U8, U9); this gate is the
judgment part: does the evidence actually address THIS mechanism, or
merely coincide with it?

Ask the symmetric-control question before any promotion: would a generic
alternative change have produced the same improvement? If yes, the
finding is `[KKE]`, not `[K]`.

A finding whose measurement came back the wrong way becomes `[R]` — and
`[R]` is written down, kept, and counted. A registry with no `[R]` rows
after several measurement cycles is not a good audit; it is an audit that
never risked anything.

---

## Re-opening a gate (invalidation protocol)

A later finding can refute an earlier premise — the walkthrough shows the
job model was wrong, or the volume answer turns out to be off by an order
of magnitude. **The skill may not pass over this silently.**

1. Re-open the gate, with the specific evidence that broke the premise.
2. Bump `gate_provenance.version` on the affected flow.
3. Every finding still citing the old version is now resting on a revised
   premise. U7 flags them; re-audit or re-tier each one.
4. Record the drift itself as a finding. **Premise drift is a finding** —
   it says something about how the purpose was understood, which is
   usually more valuable than the finding that exposed it.

Never edit a premise in place and carry on. That erases the fact that the
audit was run against a different question than the one it now claims.
