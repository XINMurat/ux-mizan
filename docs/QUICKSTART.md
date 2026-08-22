# Quickstart

**Status: v0.1 `[H]`.** The first real run is the self-validation run; treat
its output as a test of the skill as much as of your app.

## 1. Install

```bash
cp -r skill/ux-mizan ~/.claude/skills/          # path must end .../ux-mizan/SKILL.md
pip install -r skill/ux-mizan/scripts/requirements.txt
cp templates/ux-registry.yaml <your-project>/ux-registry.yaml
```

## 2. Gate 0 and Gate 1 — before any auditing

Ask Claude for a UX audit. It will propose a job model and ask you to lock
it. Answer honestly about **volume**: below roughly 300 completions per
flow per month, passive telemetry cannot decide anything in a useful
window, and the skill switches to Lite mode (5–8 moderated sessions).

You are locking, at minimum:

- the two or three jobs the app exists to do, ranked;
- what "done" means for each (`success_definition`) and the route that
  marks it (`success_screen`);
- the `app_type` per flow — this decides which metrics are even legal;
- the minimum number of screens each flow needs (`canonical_path_R`).

The last one has to be declared **before** you look at any data. That is
the whole reason lostness can be computed passively later.

## 3. Run the Layer-A pass

```bash
python skill/ux-mizan/scripts/structural_checks.py src/
```

Every count is `[KKE]`. It tells you where to look, not what is broken.

## 4. Measure the baseline BEFORE changing anything

Whatever you plan to fix, measure it first and write the numbers into the
flow's `baseline.values`. Without a baseline, no later number is
interpretable, and the validator will refuse to promote a behavioural
finding to `[K]` (U8).

For lostness, once screen-view events exist:

```bash
python skill/ux-mizan/scripts/lostness.py events.jsonl --registry ux-registry.yaml
```

## 5. Validate before every commit

```bash
python skill/ux-mizan/scripts/ux_validate.py --strict ux-registry.yaml
git config core.hooksPath tools/hooks     # or copy tools/hooks/pre-commit
```

## What to expect in a first audit

- Most findings sit at `[H]` or `[KKE]`. That is correct, not a shortfall.
- A `[K]` requires a real artifact, a baseline, and a locked `min_n`. If
  you have none of those yet, you have no `[K]` yet.
- After the first measurement cycle you should have at least one `[R]` —
  a hypothesis the data knocked down. A registry with no `[R]` rows is an
  audit that never risked anything.
