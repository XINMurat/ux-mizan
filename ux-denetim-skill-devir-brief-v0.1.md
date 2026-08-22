# UX Denetim Skill'i — Devir & Tasarım Brief'i (v0.1)
### Claude Code oturumuna taşınmak üzere hazırlanmış oturum çıktısı

**Statü:** `[H]` / `[KKE]` — Bu mimari tasarım henüz hiçbir gerçek uygulamada
koşmadı. Aşağıdaki her mimari karar, skill bir gerçek vakada iyi denetim
ürettiğini gösterene kadar `[H]`'dir. **Skill'in ilk işi kendini
doğrulamaktır** (bkz. §8).

**Kaynak:** Çok turlu bir sohbet penceresi tartışması (UI/UX prensipleri →
YZ-üretimi arayüzlerde homojenleşme → UX şikâyetlerinin ölçümü → model-denetim
mimarisi → amaç fonksiyonu → taşınabilir skill). Bu belge o tartışmanın
konsolide, kendine-yeten halidir.

**Çalışma adı:** `rehber` veya `ux-mizan` (aile ile tutarlı; CC oturumunda
kesinleştir).

**Provenance uyarısı:** Bu belgedeki bulgular bir *tasarım tartışmasından*
gelir; ampirik doğrulama değil, gerekçelendirilmiş mimaridir. Metrik eşikleri
ve mekanizma iddiaları uygun tier'lerle işaretlendi.

---

## 0. Bu skill neden var — tek cümlelik problem

Bir uygulamanın UX'ini (özellikle *kaybolma* ve *kafa karışıklığı*
şikâyetlerini), taşınabilir ve tekrar kullanılabilir biçimde, **YZ modelinin
yapabileceği kadarını otonom yapıp insan gerektiren kısımlarda insana danışarak**
denetleyen; çıktısı ölçülebilir, çürütülebilir ve tier'lenmiş olan bir araç
kiti.

Ekosistemdeki yeri: Kiyas üretir → Iskele yapılandırır → Mizan iddiaları
denetler → **bu skill deneyimi (UX) denetler.** Aynı disiplini (tier'ler,
ön-kayıt, çürütme koşulları, append-only registry) UX alanına taşır.

---

## 1. Devredilmeden önce anlaşılması gereken temel gerçek

> **Bir model, koda veya ekran görüntüsüne bakarak UX'i ÖLÇEMEZ.** UX
> davranışsaldır — gerçek kullanıcının ne yaptığında yaşar. Model yalnızca
> **heuristik/yapısal uygunluğu** denetleyebilir ve **ölçüm düzeneğini
> kurabilir.** Model hem üretici hem yargıç olduğunda çıktısı en fazla
> `[KKE]`'dir. **Hakem yazarsa `[K]` yoktur.**

Bu yüzden mimari iki katmanlıdır:

- **Katman A — Yapısal/heuristik denetim** (model yapar → `[H]`/`[KKE]` üretir).
- **Katman B — Davranışsal denetim** (gerçek kullanıcı/otomatik hakem →
  `[K]` üretir).

Katman A'nın her bulgusu, Katman B verisi onaylayana kadar `[H]`'dir. Veriyle
çöken hipotez `[R]`'dir ve **silinmez.**

---

## 2. Evidence tier'leri (Mizan ile birebir aynı — bilingual)

| Tag | TR | EN | Anlam |
|---|---|---|---|
| `[K]` | Kanıtlanmış | Proven | Doğrudan kanıt destekliyor; kaynak var; eşik geçildi |
| `[H]` | Makul Hipotez | Plausible hypothesis | Teorik gerekçe var; ampirik destek eksik/eşik altı |
| `[S]` | Spekülatif | Speculative | İlginç; test edilemez veya test tasarlanmadı |
| `[R]` | Reddedildi | Refuted | Test edildi, kendi eşiğini geçemedi — kayıtta kalır |
| `[KKE]` | Kritik Kontrol Eksik | Critical control missing | Sonuç var; onu çevirebilecek kontrol/baseline koşmadı |
| `[Y]` | Yanıltıcı | Misleading | Teknik olarak doğru; kanıtın desteklediğinden fazlasını ima ediyor |

Tier kayması bir bulgudur (premis kayması dâhil — bkz. Kapı yeniden-açılması).

---

## 3. İnsan-döngü kapı yapısı (bağımlılık grafiği)

Kapılar düz liste değil, bir DAG. Akış:

```
Kapı 0 (amaç/öncelik) ──> Kapı 1 (tip/kısıt/hacim/mod)
        │                          │
        │                    [OTONOM DENETİM: Katman A]
        │                          │
        └──────────────────> Kapı 2 (hipotez onayı)
                                   │
                             Kapı 3 (yön onayı)
                                   │
                        [İNŞA / SPEC / DEVİR]
                                   │
                             Kapı 4 (tier çevirme) <── [Katman B verisi]
```

### Kapı sınıfları
- **Sert bloklayan (model geçemez):** Kapı 0, Kapı 3, Kapı 4. Bunlar
  ürün/insan kararıdır.
- **Tavsiye eden (yumuşak):** Kapı 1 (kısmen), Kapı 2. Yanıt yoksa skill
  DURMAZ — varsayılan koyar, `[H]` işaretler, ilerler.

### Her kapının içeriği

**Kapı 0 — Amaç & öncelik (SERT).**
Model taslak önerir; insan onaylayıp kilitler. "Neyin önemli olduğu" bir
üründür kararıdır, premis, model çıktısı değil. Elicit edilecek: önceliklendirilmiş
görev modeli (jobs-to-be-done) — birincil/ikincil/üçüncül görevler, her birinin
`priority_weight`'i, varsa "kuzey yıldızı" değer-yolu, ve "başarı neye denir"
tanımı. **Kilitlenene dek premis değildir.** Model amacı kendi çıkarıp kendine
göre denetlerse döngü kapanır ve denetim çürütülemez hale gelir.

**Kapı 1 — Tip, kısıt, hacim, çaba bütçesi (kısmen SERT).**
Elicit: uygulama tipi (çok-ekranlı navigasyonel / tek-tuval / yoğun-form /
B2B iç araç), platform, olgunluk (prototip/canlı), kullanıcı hacmi, ayrılabilir
çaba. Bu yanıtlar **hangi metriklerin geçerli olduğunu VE lite/tam modu**
belirler. Yanıtsız dallar: "bilinmiyor → varsayılan + işaret."

**Kapı 2 — Hipotez onayı (YUMUŞAK).**
Walkthrough + yapısal kontroller hipotez üretir; registry'ye *yazılmadan önce*
insan doğrular/düzeltir. Ön-kayıt kilidi burada kapanır (HARKing'i önler).

**Kapı 3 — Yön onayı (SERT).**
Herhangi bir redesign/model-devri *öncesinde* insan teşhisi + önerilen yönü
onaylar. İnsanın onayladığı şey piksel-düzeyi karar DEĞİL; **teşhis + öncelik
çerçevesi + amaçlanan yön** olmalı (yoksa onay tiyatrosu / sahte-kontrol
zararı).

**Kapı 4 — Tier çevirme (SERT).**
`[K]` yalnızca gerçek Katman B verisiyle ve insan kararıyla verilir.

### Kapı yeniden-açılması (invalidation protokolü)
Bir bulgu, daha önceki bir premisi çürütebilir (ör. walkthrough "amaç modeli
yanlıştı" gösterir). Skill bunu **sessizce geçemez**: ilgili kapıyı yeniden
açar ve o premise dayanan tüm alt-kayıtları "revize edilmiş premise dayanıyor"
diye işaretler (`gate_provenance` alanı). Premis kayması da bir bulgudur.

### Yorgunluğa karşı
Sorular toplu, mümkünse tek-seçim, bir seferde birkaçtan fazla değil. Kapı bir
sorgu değil müzakere. Her kapıda: **model önerir, insan kilitler.**

---

## 4. Registry şeması — iki bağlı tablo

Akış-primatı ve amaç-ağırlığı prose'da kalırsa aşınır; şemaya yapısal gömülür.
İki bağlı tablo (UMT "her şey bir tablodur" ile uyumlu; premis/bulgu ayrımı
Mizan'ın claim/evidence ayrımı).

### Tablo A — Flows (premisler; Kapı 0+1 doldurur)
| alan | açıklama |
|---|---|
| `flow_id` | benzersiz |
| `task_name` | görev adı |
| `priority_weight` | Kapı 0'da **insan-kilitli** ağırlık |
| `frequency` | kullanım sıklığı tahmini |
| `app_type` | Kapı 1'den; metrik geçerliliğini belirler |
| `canonical_path_R` | optimal adım sayısı (lostness'ın R'si) |
| `baseline_L` | ölçülene dek `null` |
| `applicable_metrics` | app_type'a göre kapılı alt küme |
| `gate_provenance` | hangi premise/kapı sürümüne dayanıyor |

### Tablo B — Findings (bulgular; denetim doldurur, A'ya bağlı)
| alan | açıklama |
|---|---|
| `finding_id` | benzersiz |
| `parent_flow_id` | **ZORUNLU** — akış-primatını zorlar |
| `finding_type` | `flow-level` \| `component-contributing` |
| `principle` | hangi UX prensibi (IA, bilgi kokusu, tutarlılık, geri bildirim…) |
| `location` | dosya / komponent / satır (muğlak "bu kısımda" yasak) |
| `mechanism` | neden kaybolmaya/karışıklığa yol açıyor — nedensel zincir |
| `tier` | `[H]`/`[KKE]`/`[K]`/`[R]`/`[S]`/`[Y]` |
| `refutation_condition` | hangi ölçüm bunu yanlışlar |
| `metric` | kararı verecek otomatik kontrol / davranışsal metrik |
| `evidence_artifact_id` | null olabilir; **`[K]` için null OLAMAZ** |
| `severity` | hesaplanır (aşağıda) |
| `status` | `open`/`instrumented`/`confirmed`/`refuted` |
| `min_n` | tier çevirmeden önce gerekli gözlem + karar kuralı |
| `source_provenance` | `structural-check`/`walkthrough`/`human`/`real-data` |
| `fix` | somut, en küçük değişiklikle en büyük etki |

### Disiplini TAŞIYAN dört kural (hepsi validator'a — prose'a değil)
1. **Yapısal `[K]` kilidi:** `tier==[K] && evidence_artifact_id==null` →
   validator REDDEDER. (Mizan: "the scripted part is the part that travels.")
2. **Akış-primatı:** `parent_flow_id` zorunlu; `component-contributing` bir
   kayıt flow'a bağlanmadan var olamaz. Komponentin izole puanlanması şema
   düzeyinde imkânsız.
3. **Severity denetlenebilir formül:**
   `severity = failure_magnitude × priority_weight × frequency`.
   `priority_weight` insan-kilitli olduğu için model önceliklendirmeyi
   oynatamaz.
4. **Append-only + `[R]` kalıcılığı + provenance:** reddedilen silinmez;
   her bulgu nereden geldiğini taşır.

---

## 5. Metrik bataryası — UYGULANABİLİRLİK KOŞULLARIYLA

Kötü genericlik = her uygulamaya aynı metrikler. İyi genericlik = uygulamadan
bağlam çıkarıp geçerli alt kümeyi seçmek. Metrikler `app_type`'a kapılı.

### Yapısal (model + betik; proxy → `[KKE]`)
- Durum-kapsam oranı: (loading+empty+error içeren görünüm)/(toplam async görünüm)
- Yetim-sayfa sayısı; azami nav derinliği (>3 sayısı)
- Jenerik-etiket sayısı ("Tıkla", "Detay", "Gönder" → zayıf bilgi kokusu)
- Geri-bildirim-boşluğu sayısı (görünür tepkisiz mutasyon)
- Tutarlılık-sapma sayısı; semantik-olmayan-etkileşimli öğe (`onClick`'li `div`)

### Erişilebilirlik (otomatik hakem → `[K]`'ya yakın)
- axe-core ihlal sayısı; Lighthouse a11y skoru
- **Klavye-yalnız görev tamamlama** (kaybolmanın iyi yordayıcısı)

### Davranışsal (gerçek hakem → `[K]`)
- **Lostness (L)** — aşağıda, ayrıntılı
- Görev başarı oranı; görev süresi; ilk-tıklama doğruluğu
- Geri-dönüş / öfke-tıklaması / ölü-tıklama oranı
- Adım-bazlı terk (funnel); SUS skoru (zaman serisi)

### Lostness metriği (Smith, 1996) — kullanıcıya SORMADAN kaybolma ölçümü
```
L = sqrt( (N/S − 1)^2 + (R/N − 1)^2 )
```
- **N** = görevde ziyaret edilen FARKLI ekran sayısı
- **S** = ziyaret edilen TOPLAM ekran sayısı (tekrarlar dâhil)
- **R** = görevi tamamlamak için gereken ASGARİ ekran sayısı (`canonical_path_R`)
- Aralık 0–1. Eşikler (Smith): **L>0.5 kayıp**, **L<0.4 kayıp değil**,
  0.4–0.5 belirsiz.

**Kritik köprü:** Eklenti her akış için hedefi/görevi ve R'yi ÖNCEDEN ilan
ederse, L gerçek telemetriden PASİF hesaplanabilir — "log kaybolmayı ölçemez"
itirazını çözen şey budur. Uyarılar: (a) sadece navigasyonel `app_type` için
geçerli — tek-tuval araçta metrik kapatılır; (b) L *neden*'i söylemez → rage/
dead-click/backtrack ile birlikte kullan; (c) global değil AKIŞ-BAŞINA (yerel)
hesapla; (d) 0.4/0.5 eşiği hipertext çalışmalarından türedi, senin app tipinde
valide DEĞİL → baseline şart (§6).

---

## 6. Baseline zorunluluğu

"L=0.55" tek başına anlamsız. İyi/kötü ancak kıyas noktasıyla anlam kazanır.
En pratik strateji: herhangi bir redesign'dan ÖNCE mevcut halin L'sini (ve
diğer metrikleri) ölç, `baseline_L`'e yaz, referans al. Yüksek L "kaybolma"
değil "görev doğası gereği çok-adımlı" olabilir → beklenmedik kötü sonuca da
alternatif açıklama ara. Baseline olmadan tüm sayılar yorumlanamaz.

---

## 7. Modlar — kademeli (friction-vergisi kontrolü)

Tüm ağırlık (ön-kayıt + olay testleri + iki-model devri) her uygulamaya
uygulanırsa, üretilen titizlik geciktirdiği iterasyondan az değer üretebilir.

- **Lite mod** (prototip / düşük-hacim): walkthrough + yapısal kontroller +
  **5–8 moderasyonlu görev-oturumu önerisi.** DÜŞÜK HACİMDE PASİF TELEMETRİ
  DEĞİL — moderasyonlu oturum "nerede" + "neden"i aynı anda, bir öğleden
  sonrada verir; pasif telemetri düşük-N'de aylarca `[K]` üretmez.
- **Tam mod** (olgun / yüksek-hacim): + akış-registry ön-kaydı + pasif
  telemetri eklentisi + iki-model spec/devir + Katman B.

Kapı 1 hangi modun uygun olduğunu sorar. (Not: önceki tur "pasif-telemetri
birincil" demiştim; bu yalnızca YETERLİ HACİM varsa doğru — düşük hacimde
öncelik moderasyonlu oturuma çevrilir. Bu bir öz-düzeltme.)

---

## 8. İnşa planı — Claude Code oturumu için

1. **Önce oku (repo erişimiyle):**
   - `skill-creator` SKILL.md — skill inşa/eval iş akışı
   - Mizan reposu (`mizan/SKILL.md`, `schemas/mizan-registry.yaml`,
     `references/*`) — aile konvansiyonu, validator deseni, registry YAML
   - Iskele & Kiyas — kardeş skill'lerin yapısı/tetikleme dili
2. **İskele kur (Mizan kalıbına birebir):**
   - `SKILL.md` (bilingual tier tablosu, on-demand referans yükleme,
     tetikleme sınırları)
   - `references/` (kapı protokolü, walkthrough şablonu, metrik uygulanabilirlik
     matrisi, redesign/spec-devir prosedürü)
   - `schemas/ux-registry.yaml` (iki-tablo şeması + sert kurallar)
   - **`ux_validate.py`** — dört yapısal kuralı MODELSİZ uygular
     (`[K]`-kilidi, `parent_flow_id` zorunluluğu, severity formülü,
     append-only). "Kuralı taşıyan şey betiktir."
3. **Referans betikler:** lostness hesabı (akış-başı N/S/R), olay-ateşleme
   testi (sessiz-hata koruması), grep-tabanlı yapısal kontroller (React/TS).
4. **İLK KOŞU = ÖZ-DOĞRULAMA:** skill'i kullanıcının GERÇEK uygulamasında bir
   kez koştur. Bu, "genel çözüm mü tek-uygulama mı" ikilemini çözer: gerçek
   uygulama skill'in test fikstürüdür, ürünü değil. Çıktı v1.0'ı besler.
5. **v0.1 statüsünü her çıktıda görünür kıl** (hangi tier, hangi kapılar
   geçildi, hangi kanıt) — "skill üretti" otorite yanılsamasına karşı.

---

## 9. Paketlemeye özgü riskler (v0.1'de akılda tut)

| # | Risk | Hafifletme |
|---|---|---|
| 1 | **Özyinelemeli homojenleşme** `[H]` — skill redesign önerirken jenerik varsayılana (shadcn/Tailwind ortalaması) kayar; teşhis ettiğimiz hastalığı önerileriyle yayabilir | Tam çözülemez. Kapı 0 (özgül amaç) + Kapı 3 (insan onayı) + her redesign için "bu amaçtan mı, jenerik varsayılan mı?" öz-kontrolü |
| 2 | **`[K]` yasağının aşınması** — prose talimatı uzun oturumda aşınır | Yasak validator'da yapısal (evidence_artifact_id olmadan `[K]` yazılamaz) |
| 3 | **Otorite yanılsaması** — "skill üretti" → aşırı güven, oysa v0.1 doğrulanmamış | Her çıktıda statü + kanıt şeffaflığı |
| 4 | **Friction-vergisi** — denetim ağırlığı iterasyonu geciktirir | Lite/tam mod ayrımı (§7) |
| 5 | **Tetikleme/kapsam** — Mizan/Iskele/Kiyas ile çakışma veya basit sorularda gereksiz ağırlık | Açıklamada tetikleme sınırlarını net çiz |
| 6 | **Açık geri bildirim yanlılığı** — kayıp kullanıcı formu doldurmaz, terk eder → tam da ölçmek istediğin popülasyonu eksik örnekler | Pasif davranışsal telemetri BİRİNCİL; açık geri bildirim yalnızca üçgenleme, araya girmeyen, akış-sonu |
| 7 | **İki-model devri sahte bağımsızlık** `[H]` — aynı eğitim dağılımı, aynı önyargı; B, A'nın homojenleşmesini yakalamaz | Devrin değeri OKUNABİLİRLİK, bağımsız doğrulama değil. Spec tam çerçeveyi + çürütme koşullarını taşımalı; uygulama `[H]` olarak yeniden girer |

---

## 10. Aile konvansiyonu (Mizan'dan devralınan sabit kısıtlar)

- Bilingual tier etiketleri (yukarıdaki tablo, değişmez)
- Referansları on-demand yükle, başta hepsini değil (context ekonomisi)
- **Registry hafızadır, transcript değil** — bulguyu doğrulanınca dosyaya
  ekle, sona saklamadan; append-only
- Skill başka birinin host'unda koşar → **sessizce bozunur.** Çatışmayı
  adlandır, sessizce uyma (brevity cap, "pozitif ol" baskısı, sabitlenmiş dil)
- **Asla bir aracın varlığını varsayma** (subagent, shell, kütüphane host'a
  göre değişir) — söz vermeden kontrol et, yoksa fallback söyle
- Sessizce prose ile artefakt ikame etmek üretici-taraflı bir iddiadır
- "Kuralı taşıyan şey betiktir" — sert kurallar validator'da

---

## 11. Claude Code'da çözülecek AÇIK kararlar

1. Skill adı: `rehber` mi `ux-mizan` mı?
2. `ux_validate.py` bağımsız mı, yoksa `mizan_validate.py`'nin uzantısı mı
   (registry şemaları paylaşılabilir mi)?
3. Metrik-uygulanabilirlik matrisi: `app_type` kaç kategoriye ayrılacak, her
   biri hangi metrikleri açıyor/kapatıyor?
4. Walkthrough çıktı şeması: adım × dört-Norman-sorusu × çürütme-eşiği somut
   formu.
5. Registry YAML'ın Mizan'ınkiyle birleşmesi mi, ayrı dosya mı?
6. Lite/tam mod arasındaki tam sınır (hangi hacim eşiği?).

---

## 12. Bu oturumun genel çıktısı (özet zincir)

1. **UI/UX prensipleri** dört katman: algı (Gestalt) → biliş (yük, tanıma>hatırlama)
   → etkileşim (Norman: affordance/signifier/mapping/feedback; Fitts) →
   sezgisel kontrol (Nielsen 10, Jakob). Miller "7±2" bir `[Y]`.
2. **YZ homojenleşmesi** ölçülmüş olgu `[K]`; mekanizmalar (eğitim dağılımı,
   decoding, RLHF, araç varsayılanları, sürtünmesizlik) çoğunlukla `[H]` —
   göreli ağırlık ablate edilmedi (`[KKE]`). "Model collapse bugünkü nedendir"
   bir `[Y]`. YZ "usable but conventional": prensiplere UYAR, tam da bu yüzden
   jeneriktir (çift-sınama: "heuristik-geçer + ayırt-edici" çifti kırılır).
3. **UX ölçümü** davranışsaldır → model ölçemez, ölçüm düzeneğini kurar.
   İki katman (A yapısal `[KKE]` / B davranışsal `[K]`).
4. **Amaç fonksiyonu** premistir, bulgu değil; insan kilitler. Severity =
   başarısızlık × öncelik × sıklık. Redesign `[H]`'dir, ayrıcalıklı değil.
5. **Taşınabilir skill** → bu belge. Genericlik = adapte olma yeteneği,
   tek-tip kontrol değil. İnsan-döngü = kapı yapısı. İlk iş = öz-doğrulama.

**Son `[KKE]`:** Tüm telemetri (lostness dâhil) kaybolmanın VEKİLİDİR, kendisi
değil. Düşük L "kullanıcı kaybolmuyor" değil, "kaybolmanın bilinen navigasyonel
imzası yok" der. `[K]`'ya en yakın nokta, L ile gerçek görev başarısının (ya da
birkaç moderasyonlu oturumun) AYNI yöne işaret ettiği yerdir.
