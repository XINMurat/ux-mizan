# Prose vs. schema — what this skill claims and what it actually enforces

**Tier: `[KKE]`.** This audit was written by the same author as the code it
audits. The missing control is a second reader, and it is named rather
than hidden.

The premise, inherited from Mizan: **the scripted part is the part that
travels.** Anything enforced only by `SKILL.md` prose is negotiable by
whatever host the skill runs inside. So the question worth asking of this
repo is not "does the documentation say the right thing" but **"which of
its rules would survive a host that quietly disagrees?"**

## Enforced by `ux_validate.py` — survives any host

| claim in prose | rule | genuinely checked? |
|---|---|---|
| "If the referee writes it, there is no `[K]`" | U1 | Yes. `[K]` needs a resolving `evidence_artifact_id` and `source_provenance` in {real-data, moderated-session}. |
| "Scoring a component in isolation is impossible at the schema level" | U2 | Yes. `parent_flow_id` mandatory and must resolve. |
| "The model cannot re-rank the backlog" | U3 | Yes. Severity recomputed from the flow's weight; restating the weight on a finding is rejected. |
| "Refuted entries are never deleted" | U4 | Yes, **but only when `--against` is passed.** Without a baseline the rule does not run, and the CI workflow is where that baseline is guaranteed. Locally it is opt-in. |
| "A finding no measurement can falsify is decoration" | U5 | Yes. |
| "Lostness on a single-canvas tool is a category error" | U6 | Yes, both hops. |
| "Until a human locks Gate 0, findings are capped at `[H]`" | U7 | Partly — see below. |
| "Baseline is mandatory" | U8 | Yes, for a behavioural `[K]`. |
| "min_n locked before the flip" | U9 | Yes, for `[K]`. |

## Enforced only by prose — a host can erase these

These are the honest gaps. Each is a rule the documentation states plainly
and no script checks.

1. **The gates themselves.** Nothing verifies that Gate 2 happened before
   a finding was written, or that Gate 3 preceded a redesign. The registry
   records `locked_by`, which a model could write without asking anyone.
   *Mitigation is social, not technical: the gate notes are prose a human
   recognises as theirs or not.* The one structural piece is U7's cap.
2. **"Open the file before writing a finding."** `location` must be
   non-empty; nothing checks that the file exists or that the line means
   what the mechanism says. This is the rule that caught every script bug
   in this repo, and it is entirely unenforced.
3. ~~**`self_check_homogenisation`** is unchecked; risk #1 is guarded by
   prose alone.~~ **CLOSED in v0.3 as U10** — a finding carrying a `fix`
   and no answer is now rejected. The finding stays on the record rather
   than being edited away: it was the largest gap in the repo, it was
   found by auditing the repo against its own standard, and the fix cost
   eight lines. Note what remains unchecked: U10 tests that the question
   was ANSWERED, not that the answer is honest. "Not the generic default"
   written by a model about its own proposal is still self-report.
4. **The Lite/Full boundary (~300/month).** Written in `SKILL.md`, absent
   from the validator, and unmeasured besides.
5. **"Explicit feedback is triangulation only."** `source_provenance`
   records `human`, but nothing stops a registry built entirely from user
   requests — which is precisely the sampling failure risk #6 describes.
6. **Honesty annexes are checked for presence, not for content.** A row
   reading "none" passes U1's annex check.

## Deliberately not enforced

- **W1–W4 do not block.** A tool that can only stop you teaches authors to
  write registries that never trigger it. `--strict` exists for the files
  whose job is to model the discipline.
- **Tier accuracy.** No script can tell whether `[H]` should have been
  `[S]`. That judgment is the human's, and pretending otherwise would be
  the threshold theatre this family of tools exists to refuse.

## The claim this document existed to make checkable — resolved

`SKILL.md` said the load-bearing rules "live in the validator because
prose is negotiable". That was true of U1–U4 and **not** true of the
homogenisation self-check, which the same file listed as the mitigation
for its own top risk while leaving it to a paragraph. Technically true of
some rules, framed to imply all of them: a `[Y]`.

Closed in v0.3 by the cheaper of the two options — U10 now rejects a
finding that proposes a fix without answering the question. The
alternative (drop the claim, admit it rests on the human at Gate 3) would
have been equally honest and is recorded here because a future maintainer
who finds U10 annoying should know it was a choice between two honest
options, not a law of nature.

**What this document still cannot do:** it is written by the author of the
code it audits, so it remains `[KKE]`. A second reader would likely find
gaps this one is blind to — that is what "critical control missing" means,
and it is why the tier sits at the top of the page rather than in a
footnote.
