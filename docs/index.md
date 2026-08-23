---
title: "ux-mizan — Evidence-Tiered UX Auditing"
description: "A Claude skill that audits experience with the same discipline Mizan applies to claims: evidence tiers, human-locked gates, preregistered thresholds, an append-only registry."
---

# ux-mizan

**Evidence-tiered UX auditing, packaged as a Claude skill.**
**Kanıt-katmanlı UX denetimi — bir Claude skill'i olarak paketlenmiş.**

[Repository](https://github.com/XINMurat/ux-mizan) ·
[Mizan](https://github.com/XINMurat/Mizan) ·
[Kıyas](https://github.com/XINMurat/Kiyas) ·
[İskele](https://github.com/XINMurat/Iskele) ·
[**the family · aile**](https://xinmurat.github.io/)

> **Status: v0.2 `[H]` / `[KKE]`.** One self-validation run has happened.
> It tested the Layer-A scripts and refuted one design decision; the gates,
> the walkthrough and every behavioural metric remain untested.

---

## English

Mizan audits claims. Kıyas generates ideas. İskele structures projects.
**ux-mizan audits experience** — specifically the *getting lost* and
*confused* complaints — with the same discipline.

### The load-bearing fact

A model cannot MEASURE UX from code or screenshots. UX is behavioural. A
model can audit structural and heuristic conformance (**Layer A** →
`[H]`/`[KKE]`) and **build the measuring rig**; only real users or an
automatic instrument produce `[K]` (**Layer B**).

**If the referee writes it, there is no `[K]`.**

### What makes it more than a checklist

- **Five gates.** Purpose and priority, app type and volume, hypotheses,
  direction, promotion. Gates 0, 3 and 4 are hard: the model proposes, a
  human locks. Unanswered soft gates degrade to marked defaults instead of
  stopping the audit.
- **A two-table registry.** Flows are premises, findings hang off them.
  `parent_flow_id` is mandatory, so scoring a component in isolation is
  impossible at the schema level.
- **Metrics gated by `app_type`.** Lostness on a single-canvas tool is a
  category error and fails validation. Six app types, each switching a
  metric *off* — a taxonomy that only adds is decoration.
- **Rules in a script, not in prose.** `ux_validate.py` enforces U1–U11
  identically in every host. Whatever is enforced only by a paragraph is
  negotiable by the host's paragraphs.

### Read next

- [Quickstart](QUICKSTART.md) — install, first audit, first validation
- [Usage guide (EN)](en/usage-guide.md) — gates, modes, metrics, worked flow
- [Reference (EN)](en/reference.md) — every rule, every metric, every file
- [Project instructions (EN)](en/project-instructions.md) — paste into a Claude Project
- [Kullanım kılavuzu (TR)](tr/kullanim-kilavuzu.md) · [Metodoloji](tr/metodoloji.md) · [Referans](tr/referans.md) · [Proje talimatı](tr/proje-talimati.md)

---

## Türkçe

Mizan iddiaları denetler. Kıyas fikir üretir. İskele projeyi yapılandırır.
**ux-mizan deneyimi denetler** — özellikle *kaybolma* ve *kafa karışıklığı*
şikâyetlerini — aynı disiplinle.

### Taşıyıcı gerçek

Bir model, koda veya ekran görüntüsüne bakarak UX'i **ölçemez**. UX
davranışsaldır. Model yapısal ve sezgisel uygunluğu denetleyebilir
(**Katman A** → `[H]`/`[KKE]`) ve **ölçüm düzeneğini kurabilir**; `[K]`
yalnızca gerçek kullanıcıdan ya da otomatik bir hakemden gelir
(**Katman B**).

**Hakem yazarsa `[K]` yoktur.**

### Onu bir kontrol listesinden ayıran şey

- **Beş kapı.** Amaç ve öncelik, uygulama tipi ve hacim, hipotezler, yön,
  terfi. 0, 3 ve 4 serttir: model önerir, insan kilitler. Yanıtsız yumuşak
  kapılar denetimi durdurmaz, işaretli varsayılana düşer.
- **İki tablolu registry.** Akışlar premis, bulgular onlara bağlanır.
  `parent_flow_id` zorunludur; komponenti izole puanlamak şema düzeyinde
  imkânsızdır.
- **`app_type`'a kapılı metrikler.** Tek-tuval bir araçta lostness bir
  kategori hatasıdır ve doğrulamadan geçmez. Altı tip, her biri bir
  metriği *kapatarak* — yalnızca ekleyen taksonomi süslemedir.
- **Kurallar betikte, düzyazıda değil.** `ux_validate.py` U1–U11'i her
  host'ta aynı şekilde uygular. Yalnızca bir paragrafla korunan şey,
  host'un paragraflarıyla pazarlık edilebilir.

### Sırada

- [Hızlı başlangıç](QUICKSTART.md)
- [Kullanım kılavuzu](tr/kullanim-kilavuzu.md) — kurulum, kapılar, modlar, metrikler
- [Metodoloji](tr/metodoloji.md) — skill'in tam Türkçe karşılığı: iki katman, beş kapı, walkthrough, metrikler, devir
- [Referans](tr/referans.md) — her kural, her metrik, her dosya
- [Proje talimatı](tr/proje-talimati.md) — Claude Project'e yapıştırılacak metin
- [Usage guide (EN)](en/usage-guide.md)
