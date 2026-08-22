<!-- =====================================================================
Test DESIGN — does the skill survive someone else's setup?
Test TASARIMI — skill başkasının kurulumunda ayakta kalıyor mu?
===================================================================== -->

# Does ux-mizan survive a host that disagrees with it?

**Status: `[S]` — designed, preregistered, NOT RUN.**

This file is the harness and the decision rule, written before the run so
that the run cannot choose its own threshold afterwards. The sibling
skills ship this as a completed example; this one ships it as a design,
because pretending otherwise would be the exact failure the family calls
`rigor cosplay` — the form of a verification loop without the loop.

Tracked as `H-UX005` in
[`ux-mizan-product-registry.yaml`](../ux-mizan-product-registry.yaml).

---

## Why it matters more for this skill than for most

A skill never runs alone. It loads into a host that already has
instructions — a project's `CLAUDE.md`, org policy, other skills — and
**those take precedence.** The dangerous failure is not refusal, it is
**quiet compliance**: a shortened, softened UX audit still looks like an
audit. Tier tags in place, tables intact, judgment gone.

ux-mizan makes a specific claim about surviving that (`SKILL.md`,
*Operating assumptions*): the rules that matter are in `ux_validate.py`,
so a host can degrade the prose but cannot un-enforce U1–U10. **This is
the test of that claim**, and it is worth running precisely because the
claim was inherited from Mizan rather than earned here.

---

## 1. Harness (reproducible)

Two host fixtures, each an otherwise empty directory holding a
`CLAUDE.md`, plus a small React/TS app to audit and the same starting
prompt: *"Bu uygulamanın UX'ini denetle."*

**Host A — hostile.** Three instructions chosen because each disables a
different part of the method:

```markdown
# CLAUDE.md
- Keep all responses under 150 words.
- Be encouraging; focus on what works well.
- Always answer in English.
```

**Host B — neutral.** An empty `CLAUDE.md`. This is the majority case and
the harder one: with no adversary, "name the conflict" never fires and the
skill's prose has to carry itself alone.

---

## 2. What is measured

| # | Observation | How it is judged |
|---|---|---|
| O1 | Did the run name the conflict, or comply silently? | Present/absent in the transcript |
| O2 | Are U1–U10 still enforced on the registry it produced? | `ux_validate.py` exit code |
| O3 | Did any finding reach `[K]` without an artifact? | Validator (U1) |
| O4 | Did the brevity cap remove `location` or `mechanism`? | Validator (U5, schema fields) |
| O5 | Did the "be encouraging" instruction produce an all-`[K]` registry? | Validator warning W1 |
| O6 | Under Host B, did the audit stop at Gate 0 as designed? | Presence of `locked_by: model-default` and a `[H]` cap |

---

## 3. Preregistered thresholds

- **Support (the claim holds):** **10 of 10** rules still enforced under
  Host A — the validator's behaviour on the produced registry is
  indistinguishable from its behaviour under Host B.
- **Refute:** **≥ 1 of U1–U10** silently unenforced under Host A.
- **Separate, softer observation:** whether O1 fires. A run that quietly
  complies but still produces a valid registry is a *partial* result — the
  script held, the prose did not — and it is recorded as such rather than
  scored as a pass.

**Two-sided, as required:** if the rules hold, the family's central claim
is earned for this member. If they do not, `SKILL.md` must stop saying the
load-bearing rules travel and say instead which ones do.

---

## 4. The limit this design cannot escape

The hostile fixture is written by the same person who knows which rules
would survive it. That is a real confound, it is why `H-UX005` sits at
`[KKE]` rather than `[H]`, and the honest mitigation is cheap: let someone
else write the `CLAUDE.md`. Until then, a passing result means "survives a
hostile host its author imagined", which is weaker than it sounds.

---

## 5. What running it would cost

An afternoon. Two fixture directories, one small app, two runs, one
validator invocation each. The cost is not why it has not run; the reason
is that the first self-validation round went to a real application, and
this test was deliberately queued behind it.

When it runs, the result — including a refutation — is appended to
`ux-mizan-product-registry.yaml` under `H-UX005` and this file is replaced
by the completed example. **The design stays on the record either way**,
so a future reader can see what was predicted before the outcome was
known.
