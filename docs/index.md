---
title: "ux-mizan — Evidence-Tiered UX Auditing"
description: "A Claude skill that audits experience with the same discipline Mizan applies to claims: evidence tiers, human-locked gates, preregistered thresholds, an append-only registry."
---

# ux-mizan

> **Status: v0.5 `[H]` / `[KKE]`.** One self-validation run has happened.
> It tested the Layer-A scripts and refuted one design decision; the gates,
> the walkthrough and every behavioural metric remain untested.

---

<div id="pane-en" markdown="1">

**Evidence-tiered UX auditing, packaged as a Claude skill.**

[Repository](https://github.com/XINMurat/ux-mizan) ·
[Mizan](https://github.com/XINMurat/Mizan) ·
[Kıyas](https://github.com/XINMurat/Kiyas) ·
[İskele](https://github.com/XINMurat/Iskele) ·
[**the family**](https://xinmurat.github.io/)

---

## English

Mizan audits claims. Kıyas generates ideas. İskele structures projects.
**ux-mizan audits experience** — specifically the *getting lost* and
*confused* complaints — with the same discipline.

**Where it starts:** with an application that exists and a complaint about
it — "users get lost", "this screen is confusing", "they drop off here". It
follows nothing: no registry, no backlog, no seeds. What it produces goes two
ways, and both matter: a measured finding is a task for a backlog **and** a
claim about the application — the first goes to İskele with acceptance criteria
of its own, the second re-enters the audit loop, as a Mizan entry when it needs
tiering or as a brief for Kıyas when the question is *why* users do that.

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
- **Rules in a script, not in prose.** `ux_validate.py` enforces U1–U14
  identically in every host. Whatever is enforced only by a paragraph is
  negotiable by the host's paragraphs.

### Read next

- [Quickstart](QUICKSTART.md) — install, first audit, first validation
- [Usage guide](en/usage-guide.md) — gates, modes, metrics, worked flow
- [Reference](en/reference.md) — every rule, every metric, every file
- [Project instructions](en/project-instructions.md) — paste into a Claude Project

</div>

<div id="pane-tr" markdown="1" class="pane-init">

**Kanıt-katmanlı UX denetimi — bir Claude skill'i olarak paketlenmiş.**

[Depo](https://github.com/XINMurat/ux-mizan) ·
[Mizan](https://github.com/XINMurat/Mizan) ·
[Kıyas](https://github.com/XINMurat/Kiyas) ·
[İskele](https://github.com/XINMurat/Iskele) ·
[**aile sayfası**](https://xinmurat.github.io/)

---

## Türkçe

Mizan iddiaları denetler. Kıyas fikir üretir. İskele projeyi yapılandırır.
**ux-mizan deneyimi denetler** — özellikle *kaybolma* ve *kafa karışıklığı*
şikâyetlerini — aynı disiplinle.

**Nereden başlar:** var olan bir uygulama ve onun hakkında bir şikâyetle —
"kullanıcılar kayboluyor", "bu ekran karışık", "burada bırakıyorlar". Hiçbir
şeyin ardından gelmez: ne registry, ne backlog, ne tohum. Ürettiği ise iki yere
birden gider ve ikisi de önemlidir: ölçülmüş bir bulgu hem backlog için bir
görev **hem de** uygulama hakkında bir iddiadır — birincisi kendi kabul
kriteriyle İskele'ye, ikincisi denetim döngüsüne döner; katmanlanması
gerekiyorsa Mizan girdisi, soru *kullanıcılar bunu neden yapıyor* ise Kıyas'a
brief olarak.

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
- **Kurallar betikte, düzyazıda değil.** `ux_validate.py` U1–U14'i her
  host'ta aynı şekilde uygular. Yalnızca bir paragrafla korunan şey,
  host'un paragraflarıyla pazarlık edilebilir.

### Sırada

- [Hızlı başlangıç](QUICKSTART.md) — kurulum, ilk denetim, ilk doğrulama
- [Kullanım kılavuzu](tr/kullanim-kilavuzu.md) — kurulum, kapılar, modlar, metrikler
- [Metodoloji](tr/metodoloji.md) — skill'in tam Türkçe karşılığı: iki katman, beş kapı, walkthrough, metrikler, devir
- [Referans](tr/referans.md) — her kural, her metrik, her dosya
- [Proje talimatı](tr/proje-talimati.md) — Claude Project'e yapıştırılacak metin

</div>
