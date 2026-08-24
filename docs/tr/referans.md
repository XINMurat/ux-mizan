# Referans

Bu bir dizindir, yöntemin ikinci bir kopyası değil. Metodoloji
[`skill/ux-mizan/`](../../skill/ux-mizan/) içinde yaşar — Claude'un
yüklediği dosyaların ta kendisi — böylece gerçekte koşandan sapamaz.

## Hangi konu nerede

| Konu | Dosya |
|---|---|
| Tetikleme, iki katman, kapı DAG'ı, modlar, riskler, anti-desenler | [`SKILL.md`](../../skill/ux-mizan/SKILL.md) |
| Kapı soru setleri, varsayılanlar, yeniden-açma protokolü | [`references/gates.md`](../../skill/ux-mizan/references/gates.md) |
| Walkthrough şablonu ve kör noktaları | [`references/walkthrough.md`](../../skill/ux-mizan/references/walkthrough.md) |
| Metrik bataryası, uygulanabilirlik matrisi, lostness, baseline, ölçüm planı | [`references/metrics.md`](../../skill/ux-mizan/references/metrics.md) |
| Kapı 3, redesign, spec devri, iki-model devrinin vaat edemeyeceği | [`references/handoff.md`](../../skill/ux-mizan/references/handoff.md) |
| Registry formatı ve kuralların yorum hâli | [`schemas/ux-registry.yaml`](../../skill/ux-mizan/schemas/ux-registry.yaml) |

## Kanıt katmanları

| Etiket | TR | EN | Anlam |
|---|---|---|---|
| `[K]` | Kanıtlanmış | Proven | Doğrudan kanıt; kaynak var; eşik geçildi |
| `[H]` | Makul Hipotez | Plausible hypothesis | Gerekçe var; ampirik destek eksik veya eşik altı |
| `[S]` | Spekülatif | Speculative | İlginç; test edilemez ya da test tasarlanmadı |
| `[R]` | Reddedildi | Refuted | Test edildi, kendi eşiğini geçemedi — kayıtta kalır |
| `[KKE]` | Kritik Kontrol Eksik | Critical control missing | Sonuç var; onu çevirebilecek kontrol koşmadı |
| `[Y]` | Yanıltıcı | Misleading | Teknik olarak doğru; kanıtın desteklediğinden fazlasını ima ediyor |

Etiketler düzyazı değil, etikettir: her dilde iki dilli kalır.

## Doğrulayıcının uyguladığı kurallar

| Kural | Neyi reddeder |
|---|---|
| **U1** | Çözümlenen `evidence_artifact_id` olmadan ya da model-taraflı `source_provenance` ile `[K]`; dürüstlük şerhi olmayan kanıt artefaktı |
| **U2** | `parent_flow_id` olmayan ya da çözümlenmeyen bulgu |
| **U3** | `failure_magnitude × priority_weight × frequency` sonucuna eşit olmayan `severity`; `priority_weight`'i yeniden yazan bulgu |
| **U4** | Baseline'da olup şimdi olmayan akış/bulgu; `[R]` katmanından çıkarılmış kayıt (`--against` gerekir) |
| **U5** | `refutation_condition`, `metric.name`, adlandırılmış `metric.instrument` ya da geçerli `metric.kind` olmayan bulgu |
| **U6** | Akışın `applicable_metrics` listesinde olmayan metrik; `app_type`'ın açmadığı metriği listeleyen akış |
| **U7** | `gate_provenance` olmayan akış; Kapı 0'ı insan-kilitli olmayan akışta `[K]`/`[R]`; bayat premis sürümüne dayanan bulgu |
| **U8** | Akışında ölçülmüş baseline olmayan davranışsal metrikte `[K]` |
| **U9** | `min_n.n` ya da `min_n.decision_rule` olmadan `[K]` |
| **U10** | `fix` öneren ama `self_check_homogenisation` yanıtlamayan bulgu |
| **U11** | `kke_kind` olmayan ya da geçersiz olan `[KKE]` bulgusu; artık `[KKE]` olmayan bir kayıtta unutulmuş alan |

`kke_kind` **hangi** kontrolün eksik olduğunu söyler: `control` (sonucu
çevirebilecek karışıklık kontrolü koşmadı) · `independence` (iddiayı üreten
aynı zamanda hakemi) · `data` (ölçüm tasarlandı, veri gelmedi) ·
`validation` (ölçüm aracının kendisi, pozitif olduğu bilinen bir vakada hiç
koşturulmadı). Dört yeni etiket değil bir **alan** — altı katman, dört
kardeş skill'in paylaştığı tek şey; üstelik Mizan bu sebeplerden ikisini
adlandırmadan zaten taşıyor (R2 veri eksikliği, R8 bağımsızlık eksikliği).

| Uyarı | Neyi işaretler (tavsiye; `--strict` hataya çevirir) |
|---|---|
| **W1** | Katmanlı bütün bulgular `[K]` |
| **W2** | Hiç `flow-level` bulgu yok |
| **W3** | Ölçülmüş baseline'ı olmayan akış |
| **W4** | Sahibi ve planlanmış ölçümü olmayan açık bulgu |

```bash
python skill/ux-mizan/scripts/ux_validate.py --lang tr --strict ux-registry.yaml
python skill/ux-mizan/scripts/ux_validate.py --against HEAD ux-registry.yaml
```

## Metrik matrisi

Her `app_type` satırını bir metriği **kapatarak** hak eder. Yalnızca
ekleyen kategori süslemedir.

| app_type | kapattığı | neden |
|---|---|---|
| `navigational-multiscreen` | — | tam batarya |
| `form-heavy-transactional` | lostness | yol dayatılmış; hatalar alan düzeyinde |
| `single-canvas-tool` | lostness, nav_depth | tek ekran; yeniden ziyaret iştir, dolaşma değil |
| `b2b-internal-dashboard` | sus | mahsur kullanıcı ayrılamaz; memnuniyet taban-sansürlü |
| `content-consumption` | task_success | çoğu zaman görev yoktur |
| `guided-sequence` | lostness, nav_depth | sırayı sunucu dayatır; yeniden ziyaret yeniden okumadır |

Matris hem şemada belgelidir hem `ux_validate.py` içinde
(`METRIC_MATRIX`) gömülüdür. İkisi çelişirse koşan validator'dır ve
çelişkinin kendisi bir bulgudur.

## Betikler

| Betik | Ürettiği | Çıktısının katmanı |
|---|---|---|
| `ux_validate.py` | U1–U12 hükümleri, W1–W4 uyarıları | — (denetler, iddia etmez) |
| `structural_checks.py` | Durum kapsamı, geri bildirim boşlukları, jenerik etiketler, nav derinliği, yetim rotalar | `[KKE]` — ne eksik |
| `layout_signals.py` | Yerleşim izleri + her birinin izin verdiği davranışsal hipotez | iz `[KKE]`, iddia `[H]` |
| `lostness.py` | Akış başına L; tamamlanan ve terk edilen ayrı raporlanır | anlam kazanması için Katman-B verisi gerekir |

## Hiçbir betikte olmayan iki kural

İkisi de düzyazıda ve ikisi de taşıyıcı. Burada listelenmelerinin sebebi
`PROSE-SCHEMA-AUDIT.md`'nin onları gizlemek yerine açık gedik olarak
adlandırması:

1. **Bulguyu yazmadan önce dosyayı açın.** `location` boş olamaz; ama
   söylediği şeyin mekanizmayla uyuştuğunu hiçbir şey denetlemiyor. Bu
   deponun ürettiği her tarayıcı kusurunu yakalayan kural budur.
2. **Yeni bir dedektör, bilinmeyen vakalarda güvenilmeden önce pozitif
   olduğu bilinen bir vakada koşturulur.** Buradaki her yapısal kontrol en
   az bir kez sessizce az-raporlayarak çıktı; az raporlayan tarayıcı temiz
   koddan ayırt edilemez. Bu kural, dış bir incelemenin ardından katkı
   belgelerinden `SKILL.md`'ye taşındı — host'a giden dosya dışında her
   yerde yazılıydı. Hâlâ betikte değil, ama artık ona uyması gereken
   aracın görmediği bir yerde de değil.
