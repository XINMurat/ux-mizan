#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ux-mizan registry validator -- LLM-free static enforcement of U1-U11.

The rule that travels is the scripted one. Everything enforced only by
SKILL.md prose is negotiable by the host's prose; everything in here
behaves identically in every host, which is why the four rules the brief
calls load-bearing (structural [K] lock, flow primacy, the severity
formula, append-only) live here and not in a paragraph.

Two channels, for the reason Mizan and Kiyas both give: a tool that can
only block teaches authors to write registries that do not trigger it.

  * VIOLATIONS (U1-U11) block.
  * WARNINGS (W1-W4) do not block by default. --strict promotes them.

Usage:
    python ux_validate.py path/to/ux-registry.yaml
    python ux_validate.py --lang tr ux-registry.yaml
    python ux_validate.py --against HEAD ux-registry.yaml   # U4 append-only
    python ux_validate.py --strict ux-registry.yaml         # warnings fail

Exit code 0 = clean, 1 = violations found, 2 = usage/parse error.

Dependency: PyYAML  (pip install pyyaml)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "ERROR: PyYAML is required. Install it with: pip install pyyaml\n"
        "HATA: PyYAML gerekli. Kurulum: pip install pyyaml\n"
    )
    sys.exit(2)

VALID_TIERS = {"K", "H", "S", "R", "KKE", "Y"}
BEHAVIOURAL_PROVENANCE = {"real-data", "moderated-session"}
VALID_PROVENANCE = {
    "structural-check", "walkthrough", "human", "moderated-session", "real-data",
}
VALID_METRIC_KINDS = {"structural", "accessibility", "behavioural"}

# U11 — why an entry is [KKE]. A FIELD rather than four new tags: the six
# tiers are what four sibling skills share, and forking the vocabulary
# inside one member costs exactly what makes them a family. The four
# reasons are not this skill's invention -- Mizan already carries two of
# them without naming them (R2 is missing data, R8 is missing
# independence).
VALID_KKE_KINDS = {
    "control",       # a confound or symmetric control that could flip it has not run
    "independence",  # whoever produced the claim is also its judge
    "data",          # the measurement is designed but the data is not collected
    "validation",    # the INSTRUMENT is unvalidated (never run on a known-positive case)
}
VALID_FINDING_TYPES = {"flow-level", "component-contributing"}
VALID_STATUS = {"open", "instrumented", "confirmed", "refuted"}

# Metric applicability matrix (U6). Mirrors the comment block in
# schemas/ux-registry.yaml; if the two ever disagree, THIS is the one
# that runs, and that disagreement is itself a finding.
_COMMON_STRUCTURAL = {
    "generic_label_count", "state_coverage_ratio", "feedback_gap_count",
    "consistency_deviation_count", "nonsemantic_interactive_count",
}
_COMMON_A11Y = {"axe_violations", "lighthouse_a11y", "keyboard_only_completion"}

METRIC_MATRIX: dict[str, set[str]] = {
    "navigational-multiscreen": {
        "lostness", "task_success", "time_on_task", "first_click_accuracy",
        "backtrack_rate", "rage_click_rate", "dead_click_rate",
        "step_abandonment", "sus", "orphan_pages", "nav_depth",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
    "form-heavy-transactional": {
        "task_success", "time_on_task", "step_abandonment", "field_error_rate",
        "field_retry_rate", "validation_timing_violations", "rage_click_rate",
        "dead_click_rate", "sus",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
    "single-canvas-tool": {
        "task_success", "time_on_task", "undo_rate", "tool_discovery_rate",
        "rage_click_rate", "dead_click_rate", "sus",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
    "b2b-internal-dashboard": {
        "lostness", "task_success", "time_on_task", "first_click_accuracy",
        "backtrack_rate", "dead_click_rate", "filter_reset_rate",
        "export_fallback_rate", "orphan_pages", "nav_depth",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
    "content-consumption": {
        "scroll_depth", "return_rate", "read_completion",
        "first_click_accuracy", "dead_click_rate", "rage_click_rate",
        "orphan_pages", "nav_depth",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
    # Added in 0.2 after the first self-validation run refuted the
    # five-category version: a server-enforced learning sequence is a task
    # (so content-consumption's "no task" premise is wrong) whose path is
    # prescribed (so lostness is off) and whose content must actually be
    # READ (so form-heavy's field metrics say nothing). It needed the union
    # of two categories, which DECISIONS.md 3 names as the refutation.
    "guided-sequence": {
        "task_success", "time_on_task", "step_abandonment",
        "read_completion", "scroll_depth", "resume_rate",
        "backtrack_rate", "rage_click_rate", "dead_click_rate", "sus",
    } | _COMMON_STRUCTURAL | _COMMON_A11Y,
}

SEVERITY_TOLERANCE = 1e-6

# Bilingual message catalog: key -> (en, tr)
MSG = {
    "U1_no_artifact": (
        "U1: finding {id} is at [K] with no evidence_artifact_id. A model may not promote its own output.",
        "U1: {id} bulgusu evidence_artifact_id olmadan [K]. Model kendi ciktisini terfi ettiremez.",
    ),
    "U1_artifact_unresolved": (
        "U1: finding {id} cites evidence artifact {aid}, which does not exist in evidence_artifacts.",
        "U1: {id} bulgusu {aid} kanit artefaktina atif yapiyor; evidence_artifacts icinde yok.",
    ),
    "U1_bad_provenance": (
        "U1: finding {id} is at [K] with source_provenance '{prov}'. [K] needs real-data or moderated-session.",
        "U1: {id} bulgusu '{prov}' kaynagiyla [K]. [K] icin real-data veya moderated-session gerekir.",
    ),
    "U1_artifact_no_annex": (
        "U1: evidence artifact {aid} has no honesty_annexes -- scope and sample limits are mandatory.",
        "U1: {aid} kanit artefaktinda honesty_annexes yok -- kapsam ve orneklem serhleri zorunlu.",
    ),
    "U2_no_parent": (
        "U2: finding {id} has no parent_flow_id. Flow primacy: a component cannot be scored in isolation.",
        "U2: {id} bulgusunda parent_flow_id yok. Akis-primati: komponent izole puanlanamaz.",
    ),
    "U2_parent_unresolved": (
        "U2: finding {id} points at flow {fid}, which does not exist in the flows table.",
        "U2: {id} bulgusu {fid} akisina isaret ediyor; flows tablosunda boyle bir akis yok.",
    ),
    "U3_severity_mismatch": (
        "U3: finding {id} severity {got} != failure_magnitude x priority_weight x frequency = {want}.",
        "U3: {id} bulgusunun severity degeri {got}, hesaplanan {want} (failure_magnitude x priority_weight x frequency).",
    ),
    "U3_missing_input": (
        "U3: finding {id} cannot compute severity -- missing or non-numeric {field}.",
        "U3: {id} bulgusunun severity'si hesaplanamiyor -- {field} eksik veya sayisal degil.",
    ),
    "U3_weight_restated": (
        "U3: finding {id} restates priority_weight. Weight is read from the parent flow, where a human locked it.",
        "U3: {id} bulgusu priority_weight'i yeniden yaziyor. Agirlik, insanin kilitledigi ana akistan okunur.",
    ),
    "U4_deleted": (
        "U4: {kind} {id} exists in the baseline but not in this file. History is append-only.",
        "U4: {kind} {id} baseline'da var, bu dosyada yok. Gecmis yalnizca eklenir.",
    ),
    "U4_unrefuted": (
        "U4: finding {id} moved out of tier [R] (now [{tier}]). Refuted entries stay refuted and stay on record.",
        "U4: {id} bulgusu [R] katmanindan cikarilmis (simdi [{tier}]). Reddedilen kayit reddedilmis kalir.",
    ),
    "U5_no_refutation": (
        "U5: finding {id} has no refutation_condition -- a finding no measurement can falsify is decoration.",
        "U5: {id} bulgusunun refutation_condition'i yok -- hicbir olcumun yanlislayamayacagi bulgu suslemedir.",
    ),
    "U5_no_metric": (
        "U5: finding {id} has no metric.name -- nothing will ever decide it.",
        "U5: {id} bulgusunda metric.name yok -- bu bulguya hicbir sey karar veremez.",
    ),
    "U5_no_instrument": (
        "U5: finding {id} names no metric.instrument. 'The model' is not an instrument.",
        "U5: {id} bulgusu metric.instrument belirtmiyor. 'Model' bir olcum araci degildir.",
    ),
    "U5_bad_kind": (
        "U5: finding {id} has metric.kind '{kind}'; expected one of {allowed}.",
        "U5: {id} bulgusunun metric.kind degeri '{kind}'; beklenen: {allowed}.",
    ),
    "U6_not_applicable": (
        "U6: finding {id} uses metric '{metric}', which is not in flow {fid}'s applicable_metrics.",
        "U6: {id} bulgusu '{metric}' metrigini kullaniyor; {fid} akisinin applicable_metrics listesinde yok.",
    ),
    "U6_illegal_for_type": (
        "U6: flow {fid} (app_type '{atype}') lists metric '{metric}', which that app_type does not switch on.",
        "U6: {fid} akisi (app_type '{atype}') '{metric}' metrigini listeliyor; bu app_type onu acmaz.",
    ),
    "U6_unknown_app_type": (
        "U6: flow {fid} has app_type '{atype}', which is not one of {allowed}.",
        "U6: {fid} akisinin app_type degeri '{atype}'; gecerli olanlar: {allowed}.",
    ),
    "U7_no_provenance": (
        "U7: flow {fid} has no gate_provenance block -- nothing records which premise version it rests on.",
        "U7: {fid} akisinda gate_provenance blogu yok -- hangi premis surumune dayandigi kayitli degil.",
    ),
    "U7_unlocked_weight": (
        "U7: flow {fid} gate 0 is '{lock}', not human-locked, but finding {id} sits at [{tier}]. Cap is [H].",
        "U7: {fid} akisinin 0. kapisi '{lock}', insan-kilitli degil; ama {id} bulgusu [{tier}]. Tavan [H].",
    ),
    "U7_stale_premise": (
        "U7: finding {id} rests on premise version {have} of flow {fid}, now at version {cur}. Re-audit or re-tier it.",
        "U7: {id} bulgusu {fid} akisinin {have}. premis surumune dayaniyor; guncel surum {cur}. Yeniden denetle veya katmanini degistir.",
    ),
    "U8_no_baseline": (
        "U8: finding {id} is at [K] on behavioural metric '{metric}', but flow {fid} has no measured baseline for it.",
        "U8: {id} bulgusu '{metric}' davranissal metriginde [K]; ama {fid} akisinin bu metrik icin olculmus baseline'i yok.",
    ),
    "U9_no_min_n": (
        "U9: finding {id} is at [K] with no min_n.n -- the observation count was not locked before the data.",
        "U9: {id} bulgusu min_n.n olmadan [K] -- gozlem sayisi veriden once kilitlenmemis.",
    ),
    "U9_no_rule": (
        "U9: finding {id} is at [K] with no min_n.decision_rule -- the decision rule was not locked before the data.",
        "U9: {id} bulgusu min_n.decision_rule olmadan [K] -- karar kurali veriden once kilitlenmemis.",
    ),
    "bad_tier": (
        "SCHEMA: {kind} {id} has tier '{tier}'; valid tiers are {allowed}.",
        "SEMA: {kind} {id} '{tier}' katmanini tasiyor; gecerli katmanlar: {allowed}.",
    ),
    "bad_provenance": (
        "SCHEMA: finding {id} has source_provenance '{prov}'; valid values are {allowed}.",
        "SEMA: {id} bulgusunun source_provenance degeri '{prov}'; gecerli degerler: {allowed}.",
    ),
    "bad_finding_type": (
        "SCHEMA: finding {id} has finding_type '{ftype}'; valid values are {allowed}.",
        "SEMA: {id} bulgusunun finding_type degeri '{ftype}'; gecerli degerler: {allowed}.",
    ),
    "bad_status": (
        "SCHEMA: finding {id} has status '{status}'; valid values are {allowed}.",
        "SEMA: {id} bulgusunun status degeri '{status}'; gecerli degerler: {allowed}.",
    ),
    "no_location": (
        "SCHEMA: finding {id} has no location. 'In this part' is exactly what this field exists to forbid.",
        "SEMA: {id} bulgusunda location yok. 'Bu kisimda' demeyi engellemek icin var bu alan.",
    ),
    "no_mechanism": (
        "SCHEMA: finding {id} has no mechanism -- a violated principle is not yet a causal chain.",
        "SEMA: {id} bulgusunda mechanism yok -- ihlal edilen prensip henuz nedensel zincir degildir.",
    ),
    "U10_no_self_check": (
        "U10: finding {id} proposes a fix with no self_check_homogenisation. A redesign that never asked whether it is the generic default is how this skill spreads what it diagnoses.",
        "U10: {id} bulgusu duzeltme oneriyor ama self_check_homogenisation yok. Jenerik varsayilan mi diye sorulmamis bir redesign, bu skill'in teshis ettigi hastaligi yaydigi yoldur.",
    ),
    "U11_no_kke_kind": (
        "U11: finding {id} is at [KKE] with no kke_kind. 'A control is missing' is not actionable until it says WHICH one; valid: {allowed}.",
        "U11: {id} bulgusu kke_kind olmadan [KKE]. 'Kontrol eksik' hangi kontrol denmeden eyleme donusmez; gecerli: {allowed}.",
    ),
    "U11_bad_kke_kind": (
        "U11: finding {id} has kke_kind '{kind}'; valid values are {allowed}.",
        "U11: {id} bulgusunun kke_kind degeri '{kind}'; gecerli degerler: {allowed}.",
    ),
    "U11_stray_kke_kind": (
        "U11: finding {id} carries kke_kind '{kind}' but is not at [KKE] (tier [{tier}]). The field records why an entry is KKE, not a note kept after it stopped being one.",
        "U11: {id} bulgusu kke_kind '{kind}' tasiyor ama [KKE] degil (katman [{tier}]). Bu alan bir kaydin neden KKE oldugunu tutar; KKE olmaktan cikinca kalan bir not degil.",
    ),
    "W1_all_proven": (
        "W1: every tiered finding is [K]. An audit where nothing stayed hypothetical is flattery in a lab coat.",
        "W1: tum katmanli bulgular [K]. Hicbir seyin hipotez kalmadigi denetim, onlukle yapilan iltifattir.",
    ),
    "W2_no_flow_level": (
        "W2: no flow-level finding exists -- an audit made only of component nits usually means the walkthrough never ran.",
        "W2: hic flow-level bulgu yok -- yalnizca komponent ayrintilarindan olusan denetim, walkthrough kosmadi demektir.",
    ),
    "W3_no_baseline": (
        "W3: flow {fid} has no measured baseline. Without one, no number on this flow is interpretable.",
        "W3: {fid} akisinin olculmus baseline'i yok. Baseline olmadan bu akistaki hicbir sayi yorumlanamaz.",
    ),
    "W4_orphan_open": (
        "W4: finding {id} is open with no owner and no scheduled measurement -- it will age into a permanent [H].",
        "W4: {id} bulgusu acik ama sahibi ve planlanmis olcumu yok -- kalici bir [H]'ye donusecek.",
    ),
    "parse_error": (
        "Could not parse {path}: {err}",
        "{path} okunamadi: {err}",
    ),
    "not_registry": (
        "{path} does not look like a ux-mizan registry (no 'flows' key).",
        "{path} bir ux-mizan registry'sine benzemiyor ('flows' anahtari yok).",
    ),
    "clean": (
        "OK: {path} satisfies U1-U11.",
        "TAMAM: {path} U1-U11 kurallarini sagliyor.",
    ),
}


def m(key: str, lang: str, **kw: Any) -> str:
    en, tr = MSG[key]
    return (tr if lang == "tr" else en).format(**kw)


def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _get(d: Any, *path: str, default: Any = None) -> Any:
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


class Report:
    def __init__(self, lang: str) -> None:
        self.lang = lang
        self.violations: list[str] = []
        self.warnings: list[str] = []

    def v(self, key: str, **kw: Any) -> None:
        self.violations.append(m(key, self.lang, **kw))

    def w(self, key: str, **kw: Any) -> None:
        self.warnings.append(m(key, self.lang, **kw))


def _flows(reg: dict) -> list[dict]:
    return [f for f in (reg.get("flows") or []) if isinstance(f, dict)]


def _findings(reg: dict) -> list[dict]:
    return [f for f in (reg.get("findings") or []) if isinstance(f, dict)]


def _artifacts(reg: dict) -> list[dict]:
    return [a for a in (reg.get("evidence_artifacts") or []) if isinstance(a, dict)]


def check_flows(reg: dict, rep: Report) -> None:
    for flow in _flows(reg):
        fid = flow.get("flow_id", "<no id>")
        atype = flow.get("app_type")

        # U6, first hop: app_type must be known, and every listed metric legal
        allowed = METRIC_MATRIX.get(atype) if isinstance(atype, str) else None
        if allowed is None:
            rep.v("U6_unknown_app_type", fid=fid, atype=atype,
                  allowed=sorted(METRIC_MATRIX))
        else:
            for metric in (flow.get("applicable_metrics") or []):
                if metric not in allowed:
                    rep.v("U6_illegal_for_type", fid=fid, atype=atype, metric=metric)

        # U7: the premise must record who locked it
        if not isinstance(flow.get("gate_provenance"), dict):
            rep.v("U7_no_provenance", fid=fid)

        # W3: a flow with no measured baseline
        values = _get(flow, "baseline", "values", default={})
        if not values:
            rep.w("W3_no_baseline", fid=fid)


def check_findings(reg: dict, rep: Report) -> None:
    flows = {f.get("flow_id"): f for f in _flows(reg)}
    artifacts = {a.get("artifact_id") for a in _artifacts(reg)}
    tiered = [f for f in _findings(reg) if f.get("tier") in VALID_TIERS]

    for finding in _findings(reg):
        fid = finding.get("finding_id", "<no id>")
        tier = finding.get("tier")

        if tier not in VALID_TIERS:
            rep.v("bad_tier", kind="finding", id=fid, tier=tier,
                  allowed=sorted(VALID_TIERS))

        ftype = finding.get("finding_type")
        if ftype not in VALID_FINDING_TYPES:
            rep.v("bad_finding_type", id=fid, ftype=ftype,
                  allowed=sorted(VALID_FINDING_TYPES))

        status = finding.get("status")
        if status not in VALID_STATUS:
            rep.v("bad_status", id=fid, status=status, allowed=sorted(VALID_STATUS))

        prov = finding.get("source_provenance")
        if prov not in VALID_PROVENANCE:
            rep.v("bad_provenance", id=fid, prov=prov,
                  allowed=sorted(VALID_PROVENANCE))

        if not str(finding.get("location") or "").strip():
            rep.v("no_location", id=fid)
        if not str(finding.get("mechanism") or "").strip():
            rep.v("no_mechanism", id=fid)

        # ---- U5: refutability
        if not str(finding.get("refutation_condition") or "").strip():
            rep.v("U5_no_refutation", id=fid)
        metric_name = _get(finding, "metric", "name")
        if not metric_name:
            rep.v("U5_no_metric", id=fid)
        if not str(_get(finding, "metric", "instrument") or "").strip():
            rep.v("U5_no_instrument", id=fid)
        kind = _get(finding, "metric", "kind")
        if kind not in VALID_METRIC_KINDS:
            rep.v("U5_bad_kind", id=fid, kind=kind,
                  allowed=sorted(VALID_METRIC_KINDS))

        # ---- U2: flow primacy
        parent_id = finding.get("parent_flow_id")
        parent = None
        if not parent_id:
            rep.v("U2_no_parent", id=fid)
        elif parent_id not in flows:
            rep.v("U2_parent_unresolved", id=fid, fid=parent_id)
        else:
            parent = flows[parent_id]

        # ---- U6, second hop: the metric must be applicable to THIS flow
        if parent is not None and metric_name:
            if metric_name not in (parent.get("applicable_metrics") or []):
                rep.v("U6_not_applicable", id=fid, metric=metric_name,
                      fid=parent_id)

        # ---- U3: auditable severity
        if "priority_weight" in finding:
            rep.v("U3_weight_restated", id=fid)
        if parent is not None:
            mag = _num(finding.get("failure_magnitude"))
            weight = _num(parent.get("priority_weight"))
            freq = _num(finding.get("frequency"))
            if freq is None:
                freq = _num(parent.get("frequency"))
            got = _num(finding.get("severity"))
            missing = [name for name, val in (
                ("failure_magnitude", mag), ("priority_weight (parent flow)", weight),
                ("frequency", freq), ("severity", got)) if val is None]
            if missing:
                for name in missing:
                    rep.v("U3_missing_input", id=fid, field=name)
            else:
                want = mag * weight * freq
                if abs(got - want) > SEVERITY_TOLERANCE:
                    rep.v("U3_severity_mismatch", id=fid, got=got, want=round(want, 6))

        # ---- U7: gate provenance and premise drift
        if parent is not None:
            locked = _get(parent, "gate_provenance", "gate_0", "locked_by")
            if locked != "human" and tier in {"K", "R"}:
                rep.v("U7_unlocked_weight", fid=parent_id, lock=locked, id=fid,
                      tier=tier)
            cur = _get(parent, "gate_provenance", "version", default=1)
            have = finding.get("gate_provenance_version", cur)
            if _num(have) is not None and _num(cur) is not None and have != cur:
                rep.v("U7_stale_premise", id=fid, have=have, fid=parent_id, cur=cur)

        # ---- U1 / U8 / U9: everything that guards the [K] promotion
        if tier == "K":
            artifact_id = finding.get("evidence_artifact_id")
            if not artifact_id:
                rep.v("U1_no_artifact", id=fid)
            elif artifact_id not in artifacts:
                rep.v("U1_artifact_unresolved", id=fid, aid=artifact_id)
            if prov not in BEHAVIOURAL_PROVENANCE:
                rep.v("U1_bad_provenance", id=fid, prov=prov)
            if _num(_get(finding, "min_n", "n")) is None:
                rep.v("U9_no_min_n", id=fid)
            if not str(_get(finding, "min_n", "decision_rule") or "").strip():
                rep.v("U9_no_rule", id=fid)
            if kind == "behavioural" and parent is not None and metric_name:
                values = _get(parent, "baseline", "values", default={})
                if not isinstance(values, dict) or values.get(metric_name) is None:
                    rep.v("U8_no_baseline", id=fid, metric=metric_name,
                          fid=parent_id)

        # ---- U11: a [KKE] entry says WHICH control is missing.
        kke_kind = finding.get("kke_kind")
        if tier == "KKE":
            if not kke_kind:
                rep.v("U11_no_kke_kind", id=fid, allowed=sorted(VALID_KKE_KINDS))
            elif kke_kind not in VALID_KKE_KINDS:
                rep.v("U11_bad_kke_kind", id=fid, kind=kke_kind,
                      allowed=sorted(VALID_KKE_KINDS))
        elif kke_kind:
            rep.v("U11_stray_kke_kind", id=fid, kind=kke_kind, tier=tier)

        # ---- U10: a proposed fix must answer the homogenisation question.
        # SKILL.md names this self-check as the mitigation for its own top
        # risk (a skill that recommends redesigns drifting toward the
        # generic default) and then left it to prose, which is exactly the
        # gap PROSE-SCHEMA-AUDIT.md called a [Y]. A fix is where the risk
        # enters, so that is where the check belongs.
        if str(finding.get("fix") or "").strip():
            if not str(finding.get("self_check_homogenisation") or "").strip():
                rep.v("U10_no_self_check", id=fid)

        # ---- W4: an open finding nobody owns and nothing will measure
        if status == "open" and not finding.get("owner") and not finding.get(
                "evidence_artifact_id"):
            rep.w("W4_orphan_open", id=fid)

    # ---- W1 / W2: shape of the audit as a whole
    if tiered and all(f.get("tier") == "K" for f in tiered):
        rep.w("W1_all_proven")
    if _findings(reg) and not any(
            f.get("finding_type") == "flow-level" for f in _findings(reg)):
        rep.w("W2_no_flow_level")


def check_artifacts(reg: dict, rep: Report) -> None:
    for artifact in _artifacts(reg):
        aid = artifact.get("artifact_id", "<no id>")
        annexes = artifact.get("honesty_annexes") or []
        if not annexes:
            rep.v("U1_artifact_no_annex", aid=aid)


def check_append_only(reg: dict, baseline: dict, rep: Report) -> None:
    """U4 -- nothing disappears, and nothing escapes tier [R]."""
    now_flows = {f.get("flow_id") for f in _flows(reg)}
    for flow in _flows(baseline):
        if flow.get("flow_id") not in now_flows:
            rep.v("U4_deleted", kind="flow", id=flow.get("flow_id"))

    now_findings = {f.get("finding_id"): f for f in _findings(reg)}
    for old in _findings(baseline):
        oid = old.get("finding_id")
        if oid not in now_findings:
            rep.v("U4_deleted", kind="finding", id=oid)
            continue
        if old.get("tier") == "R" and now_findings[oid].get("tier") != "R":
            rep.v("U4_unrefuted", id=oid, tier=now_findings[oid].get("tier"))


def load_yaml(path: str, lang: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as err:
        sys.stderr.write(m("parse_error", lang, path=path, err=err) + "\n")
        sys.exit(2)
    if not isinstance(data, dict) or "flows" not in data:
        sys.stderr.write(m("not_registry", lang, path=path) + "\n")
        sys.exit(2)
    return data


def load_baseline(ref: str, path: str, lang: str) -> dict | None:
    """Read the same file at a git ref. A baseline that cannot be read is
    announced, never silently skipped -- a check that prints nothing is
    indistinguishable from a passing one."""
    try:
        blob = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            capture_output=True, check=True,
        ).stdout.decode("utf-8")
    except (subprocess.CalledProcessError, FileNotFoundError, UnicodeDecodeError):
        sys.stderr.write(
            f"WARNING: could not read {path} at {ref} -- U4 (append-only) did NOT run.\n"
            if lang != "tr" else
            f"UYARI: {path} dosyasi {ref} surumunde okunamadi -- U4 (yalnizca-ekleme) KOSMADI.\n"
        )
        return None
    try:
        data = yaml.safe_load(blob)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ux-mizan registry validator (U1-U11, W1-W4)")
    parser.add_argument("registry", help="path to a ux-registry.yaml")
    parser.add_argument("--lang", choices=["en", "tr"], default="en")
    parser.add_argument("--against", metavar="GITREF",
                        help="git ref to check append-only (U4) against")
    parser.add_argument("--strict", action="store_true",
                        help="promote warnings W1-W4 to violations")
    args = parser.parse_args()

    rep = Report(args.lang)
    reg = load_yaml(args.registry, args.lang)

    check_flows(reg, rep)
    check_findings(reg, rep)
    check_artifacts(reg, rep)

    if args.against:
        baseline = load_baseline(args.against, args.registry, args.lang)
        if baseline is not None:
            check_append_only(reg, baseline, rep)

    for line in rep.violations:
        print(line)
    for line in rep.warnings:
        print(line)

    failed = bool(rep.violations) or (args.strict and bool(rep.warnings))
    if not failed and not rep.warnings:
        print(m("clean", args.lang, path=args.registry))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
