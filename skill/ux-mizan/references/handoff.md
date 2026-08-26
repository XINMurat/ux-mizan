# Gate 3 — redesign, spec, and the two-model handoff

Read before proposing any redesign or writing a spec for another model.

## A redesign is a hypothesis

It is `[H]`, exactly like every other finding, and it is not privileged
for being newer or prettier. It carries the same obligations: a mechanism
(why this change removes the diagnosed failure), a refutation condition,
a metric, and a baseline to be compared against. A redesign shipped
without a preregistered metric cannot be evaluated afterwards — whatever
happens to the numbers, someone will have a story for it.

Write the redesign into the registry as a finding whose `fix` field holds
the change and whose `refutation_condition` holds "the new build does NOT
beat baseline on X by Y". Then it can be refuted, and it can become `[R]`,
which is the point.

## What Gate 3 approves

Not pixels. The human approves:

- the **diagnosis** — this flow fails here, by this mechanism;
- the **priority frame** — this before that, because severity says so;
- the **direction** — we change the navigation model, not the styling.

Approving a mockup is approval theatre. It extracts a signature on
something the human has no basis to evaluate, and it launders the model's
taste into an authorised product decision. If the human needs something
visual, show **two directions that differ in kind**, each tied to the
diagnosis — not two skins of the same idea.

## The homogenisation self-check (risk #1, mandatory)

An AI-generated interface is usually *usable but conventional*: it
conforms to the heuristics and is generic precisely because of it. The
pair "passes the heuristics" + "is distinctive" is what breaks. A skill
that recommends redesigns is structurally at risk of spreading the disease
it diagnoses.

So for every proposed change, answer in writing, in
`self_check_homogenisation`:

> Does this follow from THIS app's Gate-0 purpose, or is it the generic
> default (the shadcn/Tailwind mean)?

"It is the generic default, and that is the right call here" is a fine
answer — conventional patterns exist because they work, and Jakob's law is
real. Not asking is not fine. The failure mode is not choosing the
convention; it is choosing it without noticing that you did.

Two follow-ups worth asking when the answer is "from the purpose":

- What would this app lose if it looked like every other app in its
  category? If the answer is "nothing", say so — that is a legitimate
  finding about the product, not a design failure.
- Which of Gate 0's jobs does this pattern serve *better* than the generic
  default, and what would show that?

## The two-model handoff — what it can and cannot promise `[H]`

Handing a spec from model A to model B is **not independent verification.**
Same training distribution, same priors, same defaults: B will not catch
A's homogenisation, and a B that agrees is evidence of shared bias as much
as of correctness.

What a handoff genuinely buys is **readability**: writing a spec that
another agent can execute forces the frame into explicit form, and
whatever cannot be written down was never a decision — it was a
preference.

Therefore:

1. The spec carries the **whole frame**: the Gate-0 job model with
   weights, the diagnosis, the mechanism, the metric, the baseline, and
   the refutation conditions. A spec without the refutation conditions
   hands over the change and drops the way to tell whether it worked.
2. The implementation re-enters the registry as `[H]`. It does not inherit
   the diagnosis's tier.
3. If B disagrees with A, that is information worth recording — but record
   it as a disagreement between two similar models, not as a review.

## Spec skeleton

```
FLOW:            F-00x — <task name>, priority_weight <w> (human-locked, Gate 0 v<n>)
DIAGNOSIS:       <finding ids and their mechanisms>
BASELINE:        <metric: value, n, instrument, measured_at>
DIRECTION:       <what changes in kind — approved at Gate 3 on <date> by <who>>
NON-GOALS:       <what must NOT change, and why — usually the parts that work>
CONSTRAINTS:     <platform, effort budget, existing patterns that must hold>
SUCCESS:         <metric, threshold_support, threshold_refute, min_n, decision rule>
KILL CONDITION:  <what result means we revert this>
HOMOGENISATION:  <the self-check answer>
TIER ON ARRIVAL: [H] — re-measure before any promotion
```

The kill condition is not optional. A change with no condition under which
it gets reverted accumulates as permanent surface area, and the next audit
inherits it as though it were a decision someone made on purpose.

When one fires, `references/recovery.md` has the procedure: R-04 if the
change regressed a flow that worked, R-11 for the rollback itself. Both
exist to stop the same reflex — quietly removing the record of a
prediction that turned out wrong.
