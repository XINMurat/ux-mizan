# ux-mizan

**Evidence-tiered UX auditing, packaged as a Claude skill.**
**Kanıt-katmanlı UX denetimi — bir Claude skill'i olarak paketlenmiş.**

[![CI](https://github.com/XINMurat/ux-mizan/actions/workflows/ux-mizan.yml/badge.svg)](https://github.com/XINMurat/ux-mizan/actions/workflows/ux-mizan.yml)

🌐 **Languages / Diller:** [English](#english) · [Türkçe](#türkçe)
📚 **Docs:** [ux-mizan.github.io](https://xinmurat.github.io/ux-mizan/) ·
**Family:** [Mizan](https://github.com/XINMurat/Mizan) ·
[Kıyas](https://github.com/XINMurat/Kiyas) ·
[İskele](https://github.com/XINMurat/Iskele)

Tiers / Katmanlar: **[K]** proven/kanıtlanmış · **[H]** plausible hypothesis/makul hipotez ·
**[S]** speculative/spekülatif · **[R]** refuted/reddedildi (never deleted / silinmez) ·
**[KKE]** critical control missing/kritik kontrol eksik · **[Y]** misleading/yanıltıcı.

> **Status: v0.3 `[H]` / `[KKE]`.** One self-validation run has happened:
> it found four real defects in the Layer-A scanner, refuted one design
> decision on contact with a real app, and produced no `[K]` about that
> app — which is the designed behaviour, not a shortfall. The gates, the
> walkthrough and every behavioural metric remain untested.
> **Statü: v0.3 `[H]` / `[KKE]`.** Bir öz-doğrulama koşusu yapıldı: Katman-A
> tarayıcısında dört gerçek kusur bulundu, bir tasarım kararı gerçek bir
> uygulamayla temasta çürüdü ve o uygulama hakkında hiç `[K]` üretilmedi —
> ki bu tasarlanmış davranıştır, eksiklik değil. Kapılar, walkthrough ve
> tüm davranışsal metrikler hâlâ sınanmadı.

---

## English

Mizan audits claims. Kiyas generates ideas. Iskele structures projects.
**ux-mizan audits experience** — specifically the *getting lost* and
*confused* complaints — with the same discipline: tiers, preregistration,
refutation conditions, an append-only registry.

### The load-bearing fact

A model cannot MEASURE UX from code or screenshots. UX is behavioural. A
model can audit structural/heuristic conformance (Layer A → `[H]`/`[KKE]`)
and **build the measuring rig**; only real users or an automatic instrument
produce `[K]` (Layer B). **If the referee writes it, there is no `[K]`.**

### What it ships

- **Five gates** (0 purpose · 1 type/volume/mode · 2 hypotheses ·
  3 direction · 4 promotion). 0, 3 and 4 are hard: the model proposes, a
  human locks. The rest degrade gracefully to marked defaults.
- **A two-table registry** — flows (premises) and findings — where flow
  primacy and the severity formula are structural, not advisory.
- **A metric applicability matrix** gated by `app_type`, so lostness on a
  single-canvas tool fails validation instead of being reported.
- **`ux_validate.py`** — rules U1–U10 enforced without a model.
- **`lostness.py`** — Smith (1996) per flow, from ordinary screen-view
  telemetry, with its four caveats printed beside every number.
- **`structural_checks.py`** — Layer-A React/TS proxies, all `[KKE]`.
- **`layout_signals.py`** — traces of ARRANGEMENT (items rendered all-open,
  a current item marked by colour alone, a screen with nothing to scan by),
  each paired with the behavioural hypothesis it licenses and the metric
  that would decide it.

### Install

- **Claude.ai / desktop / mobile:** upload [`ux-mizan.skill`](ux-mizan.skill)
  (Settings → Capabilities → Skills). Re-upload to update.
- **Claude Code / Desktop (raw skill):** copy `skill/ux-mizan/` into `~/.claude/skills/`
  (personal) or `.claude/skills/` in a repo (project-scoped). The path must
  be `~/.claude/skills/ux-mizan/SKILL.md` — a doubly-nested folder is the
  usual mistake.
- **Registry:** copy `templates/ux-registry.yaml` next to your project and
  fill it as the gates close. `examples/ux-registry.example.yaml` is a
  worked one that passes `--strict`.

### Use

```bash
pip install -r skill/ux-mizan/scripts/requirements.txt
python skill/ux-mizan/scripts/structural_checks.py path/to/src
python skill/ux-mizan/scripts/ux_validate.py --strict ux-registry.yaml
python skill/ux-mizan/scripts/lostness.py events.jsonl --registry ux-registry.yaml
```

### The rules that actually travel

Prose is negotiable by the host's prose; a script is not. So the four
load-bearing rules live in the validator: the structural `[K]` lock,
mandatory `parent_flow_id`, the recomputed severity formula, and
append-only with `[R]` permanence. U5–U10 add refutability, the metric
gate, baseline-before-a-behavioural-`[K]`, a locked `min_n`, and the rule
that any proposed fix must answer the homogenisation question in writing.

That last one exists because this repo audited itself and did not like the
answer: `PROSE-SCHEMA-AUDIT.md` found the skill claiming a structural
mitigation for its own top risk while shipping a paragraph, called it a
`[Y]`, and U10 closed it. The finding stayed on the record.

### Known risk, stated up front

A skill that recommends redesigns can drift toward the generic default and
spread the homogenisation it diagnoses. Not fully solvable. Mitigated by
Gate 0's specific purpose, Gate 3's human approval, and U10 — the
validator rejects a finding that proposes a fix without answering, in
writing, whether that fix comes from the app's purpose or from the generic
default. U10 checks that the question was answered, not that the answer is
honest; that part is still the human's.

---

## Türkçe

Mizan iddiaları denetler. Kiyas fikir üretir. İskele projeyi yapılandırır.
**ux-mizan deneyimi denetler** — özellikle *kaybolma* ve *kafa karışıklığı*
şikâyetlerini — aynı disiplinle: katmanlar, ön-kayıt, çürütme koşulları,
yalnızca-eklenen registry.

### Taşıyıcı gerçek

Bir model, koda veya ekran görüntüsüne bakarak UX'i ÖLÇEMEZ. UX
davranışsaldır. Model yapısal/heuristik uygunluğu denetleyebilir
(Katman A → `[H]`/`[KKE]`) ve **ölçüm düzeneğini kurabilir**; `[K]` yalnızca
gerçek kullanıcı veya otomatik hakemden gelir (Katman B).
**Hakem yazarsa `[K]` yoktur.**

### İçindekiler

- **Beş kapı** (0 amaç · 1 tip/hacim/mod · 2 hipotez · 3 yön · 4 terfi).
  0, 3 ve 4 serttir: model önerir, insan kilitler. Diğerleri yanıtsız
  kalınca durmaz — işaretlenmiş varsayılana düşer.
- **İki tablolu registry** — akışlar (premisler) ve bulgular. Akış-primatı
  ve severity formülü yapısaldır, tavsiye değil.
- **`app_type`'a kapılı metrik uygulanabilirlik matrisi**: tek-tuval bir
  araçta lostness raporlanamaz, doğrulamadan geçemez.
- **`ux_validate.py`** — U1–U10, modelsiz.
- **`lostness.py`** — Smith (1996), akış başına, sıradan ekran
  telemetrisinden; dört uyarısı her sayının yanında basılır.
- **`structural_checks.py`** — Katman-A React/TS vekilleri, hepsi `[KKE]`.
- **`layout_signals.py`** — YERLEŞİM izleri (hepsi açık basılan öğeler,
  yalnızca renkle işaretlenen "şu anki" öğe, taranacak hiçbir şeyi olmayan
  ekran); her iz, izin verdiği davranışsal hipotez ve ona karar verecek
  metrikle birlikte.

### Kurulum

- **Claude.ai / masaüstü / mobil:** [`ux-mizan.skill`](ux-mizan.skill)
  dosyasını yükleyin (Ayarlar → Yetenekler → Skills); güncellemek için
  yeniden yükleyin.
- **Claude Code:** `skill/ux-mizan/` klasörünü `~/.claude/skills/` içine kopyalayın
(`~/.claude/skills/ux-mizan/SKILL.md` olmalı; en sık hata çift iç içe
klasör). Registry için `templates/ux-registry.yaml` dosyasını projenizin
yanına kopyalayıp kapılar kapandıkça doldurun.

### Baştan söylenen risk

Redesign öneren bir skill, jenerik varsayılana kayıp teşhis ettiği
homojenleşmeyi yayabilir. Tam çözülemez. Hafifletme: Kapı 0'ın özgül amacı,
Kapı 3'ün insan onayı ve U10 — doğrulayıcı, düzeltme öneren ama bu
düzeltmenin uygulamanın amacından mı yoksa jenerik varsayılandan mı
geldiğini yazılı olarak yanıtlamayan bulguyu reddeder. U10 sorunun
yanıtlandığını denetler, yanıtın dürüst olduğunu değil; o kısım hâlâ
insanın işi.
