# ux-mizan Documentation / Dokümantasyon

**⚡ New here? / Yeni misiniz?** → [QUICKSTART.md](QUICKSTART.md)

Choose a language / Bir dil seçin:

## 🇬🇧 English — [`en/`](en/)

| Doc | What it covers |
|---|---|
| [usage-guide.md](en/usage-guide.md) | Install, the five gates, modes, metrics, the hard rules |
| [project-instructions.md](en/project-instructions.md) | Block to paste into a Claude Project |
| [reference.md](en/reference.md) | Index → every rule, every metric, every reference file |

**Why English has three docs and Turkish has four.** The family's rule:
**the skill body is English** — it has to be, for portability across
hosts — **and the documentation is bilingual.** So an English reader gets
the methodology from the skill itself
([`../skill/ux-mizan/`](../skill/ux-mizan/)): `SKILL.md` plus its four
reference files, which is the same text Claude loads and therefore cannot
drift. A Turkish reader needs those five files in Turkish, and that is what
[`tr/metodoloji.md`](tr/metodoloji.md) is. The asymmetry is the design, not
a missing translation.

## 🇹🇷 Türkçe — [`tr/`](tr/)

| Belge | Kapsam |
|---|---|
| [kullanim-kilavuzu.md](tr/kullanim-kilavuzu.md) | Kurulum, beş kapı, modlar, metrikler, sert kurallar |
| [proje-talimati.md](tr/proje-talimati.md) | Claude Project'e yapıştırılacak metin |
| [referans.md](tr/referans.md) | Dizin → her kural, her metrik, her referans dosyası |
| [metodoloji.md](tr/metodoloji.md) | `SKILL.md` + dört referans dosyasının Türkçe karşılığı |

**Neden Türkçede bir belge fazla var.** Ailenin kuralı: **skill gövdesi
İngilizcedir** — host'lar arası taşınabilirlik için öyle olmak zorunda —
**dokümanlar iki dillidir.** İngilizce okuyan metodolojiyi skill'in
kendisinden alır (`SKILL.md` + dört referans); Türkçe okuyanın o beş
dosyaya Türkçe karşılık gelen bir belgeye ihtiyacı vardır ve
`metodoloji.md` odur. Asimetri tasarımdır, eksik çeviri değil.

---

## What lives outside `docs/`

| File | Why you would open it |
|---|---|
| [`../SELF-VALIDATION.md`](../SELF-VALIDATION.md) | What the first real run found **about the skill** — four scanner defects and one refuted design decision |
| [`../DECISIONS.md`](../DECISIONS.md) | The open decisions from the handover brief, each resolved with a tier and a refutation condition |
| [`../PROSE-SCHEMA-AUDIT.md`](../PROSE-SCHEMA-AUDIT.md) | Which rules survive a host that quietly disagrees, and which are prose only |
| [`../ux-mizan-product-registry.yaml`](../ux-mizan-product-registry.yaml) | The skill's own design hypotheses, in Mizan's schema, with thresholds |
| [`../examples/`](../examples/) | A worked registry that passes `--strict`, and the portability test design |

## The family

[Mizan](https://github.com/XINMurat/Mizan) audits claims ·
[Kıyas](https://github.com/XINMurat/Kiyas) generates ideas ·
[İskele](https://github.com/XINMurat/Iskele) structures projects ·
**ux-mizan** audits experience.
