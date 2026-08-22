# Cognitive walkthrough — the Layer-A template

Read before the first walkthrough. Output goes to Gate 2 first, then to
Table B.

## What this is

A step-by-step pass through ONE flow, asking the four Norman questions at
each step. It produces hypotheses, never measurements. Everything here
lands at `[H]` or `[KKE]`; the strongest thing a walkthrough can say is
"here is a specific mechanism and here is the measurement that would
falsify it".

Run it per flow, in Gate-0 priority order. A walkthrough of a flow nobody
locked a weight for is a walkthrough of an assumption.

## The four questions, per step

For each step the user must take:

1. **Goal** — will the user be trying to achieve this effect at all? (Is
   the sub-goal even in their head at this point in the flow?)
2. **Availability** — is the required control perceivable? Not "present in
   the DOM" — perceivable, at the moment they look for it.
3. **Recognition** — will they recognise that THIS control produces the
   effect they want? This is the information-scent question and the most
   common failure: the control is visible and its label carries no scent.
4. **Feedback** — after acting, will they understand that progress was
   made toward the goal? Silence after a mutation is the classic failure.

## Output shape (one row per step)

| step | user goal | question that fails | mechanism | location | refutation threshold | metric | candidate tier |
|---|---|---|---|---|---|---|---|
| 3 | pick a delivery slot | Recognition | The slot grid uses `Continue` as the only affordance, so a user who wants to change the date reads the grid as read-only and backtracks to the address step to look for it | `src/checkout/SlotGrid.tsx:88` | first-click accuracy on step 3 ≥ 0.8 in 8 moderated sessions → refuted; ≤ 0.5 → supported | first_click_accuracy | `[H]` |

Rules for the columns that people get wrong:

- **mechanism** is a causal chain, not a restated principle. "Violates
  Nielsen #1" is not a mechanism. *What does the user perceive, what do
  they conclude, what do they then do, and why does that leave them lost?*
  A mechanism you cannot narrate as a sequence is a hunch.
- **location** is a file and a line, or a component path. "In the checkout
  area" is banned; the schema rejects an empty location and a human should
  reject a vague one.
- **refutation threshold** is two-sided. Both outcomes must teach
  something. If only "it fails" is informative, redesign the test.
- **metric** must be in the flow's `applicable_metrics`, which is gated by
  `app_type`. If the natural metric is not applicable, that is a real
  finding about the flow's classification, not a reason to smuggle the
  metric in.

## Where walkthroughs systematically fail

Name these in the report rather than pretending they are absent:

- **The walkthrough is run by whoever built the mental model.** You know
  where everything is. The step you cannot see is the one a first-timer
  fails. Mitigation: walk it as the once-a-year user from Gate 0, not the
  daily user, and say which persona you walked.
- **It finds recognition failures far more reliably than goal failures.**
  Whether the user even wants this sub-goal is a question about people,
  and a walkthrough cannot answer it. Those rows should be marked `[S]`
  until a session touches them.
- **It cannot see load.** Cumulative cognitive load across a long flow is
  invisible step by step; each step looks fine. Time-on-task and
  step-abandonment carry that signal, not this table.
- **It cannot see time.** Anything about waiting, latency or interrupted
  sessions is out of scope here.

## Feeding findings into the registry

One walkthrough row becomes one finding. `finding_type` is `flow-level`
when the failure is about the sequence (the user cannot tell where they
are, or what comes next), and `component-contributing` when a specific
control contributes to a flow-level failure. A component finding still
hangs off the flow — U2 makes the alternative impossible.

If a walkthrough produces only `component-contributing` rows, the
walkthrough did not actually walk the flow; it reviewed screens. W2 warns
about exactly this shape.
