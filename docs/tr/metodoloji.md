# ux-mizan — Kanıt-Katmanlı UX Denetimi
## Türkçe Tam Dokümantasyon (SKILL.md + kapılar + metrikler + devir)

> Bu belge, `ux-mizan.skill` paketinin içindeki altı dosyanın Türkçe
> karşılığıdır: `SKILL.md`, `references/gates.md`, `references/walkthrough.md`,
> `references/metrics.md`, `references/handoff.md`, `references/recovery.md`. Skill'in kendisi
> İngilizce çalışır (taşınabilirlik için) ama Claude ile her zaman Türkçe
> konuşabilirsiniz — skill, kullanıcının dilinde yanıt vermeyi zaten kural
> olarak içerir.
>
> **Statü: v0.3 `[H]` / `[KKE]`.** Bir öz-doğrulama koşusu yapıldı.
> Kapılar, walkthrough ve tüm davranışsal metrikler hâlâ sınanmadı.

---

## 1. Taşıyıcı gerçek

> Bir model, koda veya ekran görüntüsüne bakarak UX'i **ölçemez**. UX
> davranışsaldır — gerçek kullanıcının ne yaptığında yaşar. Model yalnızca
> **sezgisel/yapısal uygunluğu** denetleyebilir ve **ölçüm düzeneğini
> kurabilir**. Hem üretici hem yargıç olduğunda çıktısı en fazla `[KKE]`'dir.
> **Hakem yazarsa `[K]` yoktur.**

Aynı koşuda daha önce ürettiğin bir şeyi denetlemek üzereysen, denetlemeden
**önce söyle** — arıza geçişin kendisi değil, ilan edilmemiş olmasıdır
(§12, R-00).

Mimari bu yüzden iki katmanlıdır:

- **Katman A — yapısal/sezgisel denetim.** Model yapar, `[H]`/`[KKE]` üretir.
- **Katman B — davranışsal denetim.** Gerçek kullanıcı ya da otomatik
  hakem yapar, `[K]` üretir.

Katman A'nın her bulgusu, Katman B verisi onaylayana kadar `[H]`'dir.
Veriyle çöken hipotez `[R]`'dir ve **silinmez** — `[R]` satırları denetimin
kendi hata payıdır.

## 2. Kanıt katmanları

| Etiket | TR | EN | Anlam |
|---|---|---|---|
| `[K]` | Kanıtlanmış | Proven | Doğrudan kanıt; kaynak var; eşik geçildi |
| `[H]` | Makul Hipotez | Plausible hypothesis | Gerekçe var; ampirik destek eksik/eşik altı |
| `[S]` | Spekülatif | Speculative | İlginç; test edilemez ya da test tasarlanmadı |
| `[R]` | Reddedildi | Refuted | Test edildi, kendi eşiğini geçemedi — kayıtta kalır |
| `[KKE]` | Kritik Kontrol Eksik | Critical control missing | Sonuç var; onu çevirebilecek kontrol koşmadı |
| `[Y]` | Yanıltıcı | Misleading | Teknik olarak doğru; kanıtın desteklediğinden fazlasını ima ediyor |

Katman kayması bir bulgudur. **Premis kayması da bir bulgudur** (§3.6).

## 3. Kapılar — düz liste değil, bir DAG

```
Kapı 0 (amaç/öncelik) ──> Kapı 1 (tip/kısıt/hacim/mod)
        │                          │
        │                  [OTONOM DENETİM: Katman A]
        │                          │
        └──────────────────> Kapı 2 (hipotez onayı)
                                   │
                             Kapı 3 (yön onayı)
                                   │
                        [İNŞA / SPEC / DEVİR]
                                   │
                             Kapı 4 (tier çevirme) <── [Katman B verisi]
```

**Sert kapılar (model tek başına geçemez): 0, 3, 4.** Bunlar ürün ve insan
kararıdır. **Yumuşak kapılar: 1 (kısmen) ve 2** — yanıt yoksa skill
DURMAZ: varsayılan koyar, `locked_by: model-default` yazar, `[H]` işaretler,
ilerler.

Her kapıda: **model önerir, insan kilitler.** Sorular toplu, mümkünse
tek-seçim, bir seferde birkaçtan fazla değil. Kapı bir sorgu değil,
müzakeredir; yorgunluk lastik damga üretir ve lastik damgalanmış bir
Kapı 0, hiç olmayan Kapı 0'dan kötüdür — premis gibi görünür, otoritesini
taşımaz.

### 3.1 Kapı 0 — Amaç ve öncelik (SERT)

**Ürettiği:** Tablo A'yı oluşturan önceliklendirilmiş görev modeli ve her
akışın `priority_weight` değeri.

**Neden sert:** "burada neyin önemli olduğu" bir ürün kararıdır. Model
amacı kendisi çıkarıp kendi çıkarımına göre denetlerse döngü kapanır ve
denetim çürütülemez hâle gelir. U7 bunu zorlar: `gate_0.locked_by`
"human" olmadıkça o akıştaki bulgular `[H]` tavanındadır.

**Model önce taslak önerir.** Uygulamayı okur, sonra sunar: "bu uygulamanın
var olma sebebi şu üç-dört iş, bu sırayla. Düzeltin." Boş sayfa sorusu
insanın vaktini harcar; yanlış taslak tek satırda düzeltilir.

Kilitlenecekler:

1. **İşler** — birincil/ikincil/üçüncül, kullanıcının kelimeleriyle, özellik
   adlarıyla değil. "Faturanın parasını almak", "faturalama modülü" değil.
2. **Ağırlıklar** (0.0–1.0). Önce sıralama isteyin, sonra ağırlığa çevirin;
   insanlar sıralamayı puanlamaktan daha güvenilir yapar.
3. **Kuzey yıldızı değer yolu**, varsa.
4. **"Başarı neye denir"** — bu `success_definition` olur, ve makine
   eşleştirilebilir hâli `success_screen`.
5. **Kullanıcı kim** — günlük uzman akışını yılda bir gelen acemininkinden
   ayıracak kadar.

**Yanıtsız kalırsa:** tam denetime geçmeyin. Varsayılanı güvenli olmayan
tek kapı budur. Reddi kayda geçirin, yalnızca akıştan bağımsız yapısal
kontrolleri koşun ve amaç kilitlenmeden hiçbir şeyin sıralanamayacağını
açıkça söyleyin.

### 3.2 Kapı 1 — Tip, kısıt, hacim, çaba bütçesi (kısmen SERT)

**Ürettiği:** `app_type` (hangi metriklerin geçerli olduğunu belirler), mod,
ve planın gerçekçiliği.

Tek seferde sorulacaklar: uygulama tipi (akış başına), platform, olgunluk
(prototip/canlı), akış başına aylık tamamlama, ayrılabilir çaba.

Gerçekten iki tip olan uygulama **iki akış** alır; asla iki metrik
kümesinin birleşimini taşıyan tek akış değil.

**Yanıtsız varsayılanlar:** app_type koddan çıkarılır ve `model-default`
işaretlenir; mod = lite (ucuz olan yanlış); çaba bütçesi "bilinmiyor, yalnız
ilk üç düzeltme planlansın". Her varsayılan `gate_provenance` içine yazılır
— sessizce varsayılmaz.

### 3.3 Kapı 2 — Hipotez onayı (YUMUŞAK)

**Ürettiği:** ön-kayıt kilidi. Aday bulgular, eşikleriyle birlikte,
registry'ye **yazılmadan önce** insana gider.

Her adayı tek satırda sunun: akış, mekanizma, onu çürütecek ölçüm. Bu
kapıdaki düzeltmeler ucuzdur; eşik yazıldıktan sonrakiler HARKing'dir.

### 3.4 Kapı 3 — Yön onayı (SERT)

**Onaylanan şey piksel DEĞİLDİR.** Onaylanan: **teşhis** (bu akış burada,
bu mekanizmayla başarısız), **öncelik çerçevesi** (bu, şundan önce, çünkü
severity öyle diyor) ve **amaçlanan yön** (navigasyon modelini
değiştiriyoruz, düğme stilini değil).

Mockup gösterip "beğendiniz mi" diye sormak **onay tiyatrosudur**: insanın
değerlendiremeyeceği bir şeye imza aldırır ve modelin zevkini yetkili bir
ürün kararına dönüştürür. Görsel bir şey gerekiyorsa **cinsi farklı iki
yön** gösterin, aynı fikrin iki derisini değil.

### 3.5 Kapı 4 — Tier çevirme (SERT)

`[K]`, gerçek Katman-B verisi artı insan kararıyla verilir. Doğrulayıcı
mekanik kısmı zaten bloke eder (U1, U8, U9); bu kapı yargı kısmıdır: kanıt
gerçekten **bu mekanizmayı** mı ilgilendiriyor, yoksa onunla rastlaşıyor mu?

Terfi öncesi simetrik kontrol sorusu: jenerik bir alternatif değişiklik de
aynı iyileşmeyi üretir miydi? Evet ise bulgu `[K]` değil `[KKE]`'dir.

Birkaç ölçüm turundan sonra hiç `[R]` satırı olmayan registry iyi bir
denetim değil, hiçbir şeyi riske atmamış bir denetimdir.

### 3.6 Kapı yeniden-açılması (geçersizleştirme protokolü)

Sonraki bir bulgu, önceki bir premisi çürütebilir. **Skill bunu sessizce
geçemez:**

1. Kapıyı, premisi kıran somut kanıtla yeniden açın.
2. İlgili akışın `gate_provenance.version` değerini yükseltin.
3. Eski sürümü anan her bulgu artık revize edilmiş premise dayanıyor; U7
   onları işaretler, her biri yeniden denetlenir ya da katmanı değişir.
4. **Kaymanın kendisini bulgu olarak yazın.** Premis kayması, onu ortaya
   çıkaran bulgudan genellikle daha değerlidir: amacın nasıl anlaşıldığı
   hakkında bir şey söyler.

Premisi yerinde düzenleyip devam etmek, denetimin şu an iddia ettiğinden
farklı bir soruya karşı koşturulduğu gerçeğini siler.

### Öneri kuralı — her kapıda ve her açık soruda

**Soruyu getiren önerisini ve gerekçesini de getirir.** Yalnız Kapı 0'da değil:
her kapıda, her açık konuda, denetim ortasında bulunan her belirsizlikte.

```
DURUM:      <karara bağlanmamış olan, tek cümle>
SEÇENEK:    A <...>  B <...>
ÖNERİM:     A
GEREKÇE:    <Kapı 0'a veya kanıta bağlı, zevke değil>
YANILIRSAM: <A'yı seçip yanılmanın bedeli>
```

İki sebebi var. Modelin muhakemesini **denetlenebilir** yapar — öneriye itiraz
edilebilir, çıplak soruya edilemez. Ve insanın işini "sıfırdan düşün"den
"onayla ya da düzelt"e çevirir; okunan kapı ile lastik damga yiyen kapı
arasındaki fark budur.

Karar yine insanındır. **Öneri onay değildir, cevapsız öneri rıza değildir** —
sert kapıda bloke eder, yumuşak kapıda `locked_by: model-default` olur ve
bulgular `[H]`'de tavanlanır. Kendi önerini cevap gibi kaydetmek, U7'nin
önlemek için var olduğu döngü-kapatma hamlesidir.

## 4. Registry — iki bağlı tablo

**Tablo A — Akışlar (premisler).** `flow_id`, `task_name`, `app_type`,
`priority_weight` (insan-kilitli), `frequency`, `canonical_path_R`,
`success_definition` + `success_screen`, `applicable_metrics`, `baseline`,
`gate_provenance`.

**Tablo B — Bulgular.** `finding_id`, `parent_flow_id` (ZORUNLU),
`finding_type`, `principle`, `location` (dosya:satır), `mechanism`, `tier`,
`refutation_condition`, `metric` (+`instrument`), `min_n`,
`evidence_artifact_id`, `source_provenance`, `gate_provenance_version`,
`failure_magnitude`, `frequency`, `severity`, `status`, `owner`, `fix`,
`self_check_homogenisation`.

**Registry hafızadır, transcript değil.** Bulguyu doğrulanır doğrulanmaz
dosyaya ekleyin. Sona saklamak, bir sonraki bağlam sıfırlamasında kaybetmek
ve o ana kadar her turda bedelini ödemek demektir.

Sert kuralların (U1–U12) tam listesi: [`referans.md`](referans.md).

## 5. Walkthrough — Katman A şablonu

Her adımda dört Norman sorusu: **Amaç** (kullanıcı bu etkiyi hedefliyor
mu?), **Erişilebilirlik** (gereken kontrol algılanabilir mi — DOM'da var
değil, *aradığı anda* algılanabilir), **Tanıma** (bu kontrolün istediği
etkiyi ürettiğini anlayacak mı — bilgi kokusu sorusu, en sık başarısızlık),
**Geri bildirim** (eylemden sonra ilerlediğini anlayacak mı).

Satır başına sütunlar: adım · kullanıcı amacı · başarısız olan soru ·
mekanizma · konum · çürütme eşiği · metrik · aday katman.

- **mekanizma** nedensel zincirdir, yeniden ifade edilmiş prensip değil.
  "Nielsen #1 ihlali" mekanizma değildir. *Kullanıcı ne algılar, ne sonuç
  çıkarır, sonra ne yapar, bu onu neden kaybettirir?* Sıra olarak
  anlatamadığınız mekanizma bir sezgidir.
- **konum** dosya ve satırdır. "Ödeme bölümünde" yasaktır.
- **çürütme eşiği** iki taraflıdır; yalnız başarısızlık bilgilendiriciyse
  testi yeniden tasarlayın.

**Walkthrough'un sistematik kör noktaları** (raporda adlandırın):
onu koşan kişi zihinsel modeli zaten kurmuş olandır; tanıma hatalarını
amaç hatalarından çok daha güvenilir bulur; **bilişsel yükü göremez** —
uzun bir akışta biriken yük adım adım görünmezdir, her adım iyi görünür;
ve zamanı göremez.

## 6. Metrikler

**Üç sınıf:** yapısal (model + betik → `[KKE]`), erişilebilirlik (otomatik
hakem → `[K]`'ya yakın), davranışsal (gerçek kullanıcı → `[K]`).

Yapısal sayı **inşa gereği** `[KKE]`'dir, ihtiyattan değil: karışıklıkla
*ilişkili* bir şekli raporlar ve bu örneğin gerçekten birini karıştırıp
karıştırmadığını söyleyecek kontrol koşmamıştır.

**Yerleşim** yapısalın kendi alt sınıfıdır (`layout_signals.py`): yoğunluk,
açıklık, şu anki öğenin nasıl işaretlendiği kaynaktan okunabilir — ama
yol açtıkları başarısızlık okunamaz. Betik bu yüzden izi ve hipotezi
**ayrı katmanlar** olarak basar; hipotezi tek başına, dosyayı kanıt gibi
göstererek raporlamak, ayrımın engellemek için var olduğu `[Y]`'dir.

**Uygulanabilirlik matrisi** ve altı `app_type`:
[`referans.md`](referans.md).

### 6.1 Lostness (Smith, 1996)

```
L = sqrt( (N/S − 1)² + (R/N − 1)² )
N = ziyaret edilen FARKLI ekran · S = TOPLAM ziyaret · R = asgari ekran
```

Aralık 0–1. Smith'in eşikleri: **L>0.5 kayıp**, **L<0.4 değil**, arası
belirsiz.

**Pasif çalışmasını sağlayan köprü:** akış hedefini ve `R`'yi ÖNCEDEN ilan
ederse, L sıradan ekran telemetrisinden, kullanıcıya hiçbir şey sormadan
hesaplanabilir. "Log kaybolmayı ölçemez" itirazını çözen şey budur. Önceden
ilan işin tamamıdır — veriden sonra çıkarılan R HARKing'dir ve betik tahmin
etmeyi reddeder.

Dört uyarı her sayının yanında gider: (a) yalnız navigasyonel tipler;
(b) *nerede*yi söyler, *neden*i söylemez — rage/dead-click/backtrack ile
birlikte okuyun; (c) akış başına, asla global; (d) 0.4/0.5 eşikleri
hipertext çalışmalarından gelir, sizin uygulamanız için valide değildir.

Tamamlanan oturumları terk edilenlerden **ayırın**; karıştırmak "dolaştı"
ile "vazgeçti"yi tek sayıya gömer.

### 6.2 Baseline zorunluluğu

"L=0.55" tek başına anlamsızdır. **Değiştirmeden önce ölçün** ve
`baseline.values` alanına yazın. U8, baseline'ı olmayan akışta davranışsal
`[K]`'yı bloke eder — çünkü baseline'sız terfi, bir sayıyı halk hafızasıyla
karşılaştırmaktır. Kötü sonuca da iyi sonuca da alternatif açıklama arayın:
yüksek L kaybolma değil, "görev doğası gereği çok adımlı" olabilir.

### 6.3 Sessiz bozulma koruması

Ateşlenmeyi bırakan bir analitik olayı, iyileşmiş bir metrikle birebir aynı
görünür. Her olayın izlediğini iddia ettiği yolda ateşlendiğini doğrulayan
bir test yazın ve her sürümde koşturun. Test edilmemiş bir olay hattı,
"düzelttik" ile "logu bozduk"u aynı grafiğe çevirir.

### 6.4 Düşük hacim birincil aracı değiştirir

Düşük N'de pasif telemetri aylarca `[K]` üretmez. **5–8 moderasyonlu görev
oturumu, "nerede" ve "neden"i bir öğleden sonrada verir.** Pasif telemetri
yalnızca hacim gerçekten yeterliyse birincildir — bu, "pasif her zaman
daha iyidir" sezgisinin düzeltmesidir.

### 6.5 Açık geri bildirim yalnızca üçgenlemedir

Kaybolan kullanıcı formunuzu doldurmaz, terk eder. Açık geri bildirim, tam
da ölçmek istediğiniz popülasyonu sistematik olarak eksik örnekler. Araya
girmeyen ve akış-sonu kullanın; kaybolma ya da terk bulgusunda asla
birincil sinyal yapmayın.

## 7. Modlar

- **Lite** (prototip / düşük hacim): walkthrough + yapısal kontroller +
  5–8 moderasyonlu oturum önerisi.
- **Tam** (olgun / yüksek hacim): üstüne akış-registry ön-kaydı, pasif
  telemetri eklentisi, iki-model spec devri ve Katman B.

**Sınır `[H]`:** akış başına aylık ~300 tamamlamanın altı → lite. Bu bir
tasarım tahminidir, ölçülmüş eşik değil.

## 8. Redesign ve devir

**Redesign bir hipotezdir** — `[H]`, diğerleri gibi, ve daha yeni ya da
daha güzel olduğu için ayrıcalıklı değildir. Aynı yükümlülükleri taşır:
mekanizma, çürütme koşulu, metrik, karşılaştırılacak baseline. Ön-kayıtlı
metriksiz çıkan bir redesign sonradan değerlendirilemez — sayılara ne olursa
olsun birinin bir hikâyesi olur.

**Homojenleşme öz-kontrolü (zorunlu, U10).** Her öneri için yazılı yanıt:

> Bu, BU uygulamanın Kapı-0 amacından mı geliyor, yoksa jenerik
> varsayılandan mı (bileşen kütüphanesi ortalaması)?

"Jenerik varsayılan ve burada doğrusu bu" iyi bir yanıttır — yerleşik
desenler işe yaradıkları için yerleşiktir. Sormamak iyi değildir.
Başarısızlık kipi konvansiyonu seçmek değil, onu seçtiğini fark etmeden
seçmektir.

**İki-model devri bağımsız doğrulama DEĞİLDİR** `[H]`: aynı eğitim
dağılımı, aynı önyargılar. B, A'nın homojenleşmesini yakalamaz ve B'nin
katılması, doğruluk kadar paylaşılan önyargının da kanıtıdır. Devrin
gerçekten satın aldığı şey **okunabilirliktir**: başka bir ajanın
uygulayabileceği bir spec yazmak, çerçeveyi açık hâle gelmeye zorlar —
yazılamayan şey zaten karar değil, tercihti. Spec **çürütme koşullarını
da** taşır; uygulama registry'ye `[H]` olarak yeniden girer.

## 9. Bilinen riskler

1. **Özyinelemeli homojenleşme `[H]`** — redesign öneren bir skill jenerik
   varsayılana kayabilir ve teşhis ettiği hastalığı yayabilir. Tam
   çözülemez. Hafifletme: Kapı 0'ın özgül amacı, Kapı 3'ün insan onayı,
   U10'un yapısal zorlaması.
2. **`[K]` yasağının aşınması** — uzun oturumda düzyazı aşınır; yasak bu
   yüzden U1'de yapısaldır.
3. **Otorite yanılsaması** — her çıktı statüyü, geçilen kapıları ve mevcut
   kanıtı gösterir.
4. **Sürtünme vergisi** — lite/tam ayrımı.
5. **Tetikleme çakışması** — Mizan iddiaları, Kıyas fikirleri, İskele
   projeyi. Bu, deneyimi.
6. **Açık geri bildirim yanlılığı** — §6.5.
7. **İki-model devrinde sahte bağımsızlık `[H]`** — §8.

## 10. Anti-desenler (kibarca reddedin)

- Her bulgusu `[K]` olan rapor — önlükle yapılan iltifat.
- "Kullanıcılar bu kısımda kayboluyor." Hangi akış, hangi dosya, hangi
  satır, hangi mekanizma, hangi ölçüm çürütür?
- Önce redesign edip sonra teşhis etmek.
- Kıl payı sonuç görünce eşiği yükseltmek.
- `[R]` bulgularını temizlik için silmek.
- Komponentleri izole puanlayıp toplamına UX denetimi demek.
- Baseline'sız metriği anlamlıymış gibi raporlamak.

## 11. Son `[KKE]`

Tüm telemetri, lostness dâhil, kaybolmanın **vekilidir**, kendisi değil.
Düşük L "kullanıcı kaybolmuyor" demez; "kaybolmanın bilinen navigasyonel
imzası yok" der. Bu yöntemin `[K]`'ya en yaklaştığı yer, L ile gerçek görev
başarısının — ya da birkaç moderasyonlu oturumun — **aynı yöne** işaret
ettiği noktadır.

## 12. Kurtarma rampaları — denetimin kendisi bozulduğunda

`references/recovery.md` karşılığı. Diğer her bölüm denetimin **çalışan** hâlini
anlatır; bu bölüm **bozulan** hâlini — ki daha sık olan ve zararın sessizce
verildiği hâl odur. Sessizce toparlanan bir denetimin hata oranı ölçülemez, ve
bu tam olarak `[R]` satırlarını silmeye yapılan itirazın denetçiye çevrilmiş
hâlidir.

Her rampa aynı biçimde: **DURUM · İLK HAMLE · YASAK · ÇIKTI · DAYANAK.** Son
satır her zaman var olan bir kurala düşer — yalnız düzyazıya yaslanan rampayı
uzun oturum unutur.

| Kod | Durum | Temel kural | Dayanak |
|---|---|---|---|
| **R-00** | Kendi çıktını yargılamak üzeresin | Geçişi ilan et, tier'ı tavanla | U1, taşıyıcı gerçek |
| **R-01** | Söz verilen artifact çalışmadı | Düzyazıyı artifact yerine koyma; kısıtı beyan et | İşletim varsayımları |
| **R-02** | Katman B verisi bulguyu çürüttü | Arayüz mü, bulgu mu, ölçüm mü — **eşiği oynatma** | U4, U5, U6, U8 |
| **R-03** | Metrik koşular arası kararsız | Deterministikleştir; uyan koşuyu raporlama | U11, metrics.md |
| **R-04** | Redesign çalışan akışı bozdu | Önce eski hâle dön; kill condition zaten yazılıydı | handoff.md, U4 |
| **R-05** | Yerleştirilemeyen bulgu | Asgari iz; iz yoksa gerekçeli kapanış | U11, pozitif kontrol kuralı |
| **R-06** | Bulgu artıyor, severity düz | Üretmeyi bırak, çürütmeye başla | U3, U5, W2 |
| **R-07** | Kilitli akışların dışına kayma | Park listesi; kapsamı insan büyütür | U2, U3 |
| **R-08** | Premise iş ortasında kaydı | Kapı 0 sürümünü yükselt, yeniden türet | U7, kapı yeniden-açma |
| **R-09** | Bağlam bulanıklaştı | Registry hafızadır; devir bloğu yaz ve kes | U12 |
| **R-10** | Belirsizlik / docs-kod çelişkisi | Varsayma, boş elle sorma (öneri kuralı) | gates.md, U7 |
| **R-11** | Redesign'i geri alma | İleri sar; ölçüm **yeni** baseline'dır | U4, handoff.md |
| **R-12** | Hedef tutmadı | Ölç, **tek** değişiklik, aynı aletle yeniden ölç | U8, metrics.md |
| **R-13** | Kullanıcı, denetimin yanından geçtiği şeye çarptı | Kaçağı **kaydet**, sonra teşhis et; "hangi kontrol bunu yakalamalıydı?" — susan kontrolü adlandır ya da artık var olanı yaz | Çizelgedeki *Kaçan* satırı, R-11, U7 |

**Model hata sınıfları.** Rampalar çare, bunlar hastalık: uydurma · sessiz
boşluk doldurma · bulgu enflasyonu · totolojik ölçüm · kendi çıktısını onaylama
· iyimser raporlama · eşik yumuşatma · kapsam kayması · sahte onarım · bağlam
çürümesi · **sınıfsız kaçak** (kullanıcı buldu, ekran düzeltildi, bir sonraki
denetimin neye baktığı değişmedi). Model bunları seçmez; hem üretip hem yargılayan bir tarafın işe yarar
görünme baskısı altındaki davranışıdır — tek güvenilir savunma, fark eden bir
yapıdır.

**Kapanış çizelgesi.** Kapı 4'ten sonra ya da iş bittiğinde doldurulur; amaç
denetimi notlamak değil **yöntemin nereden sızdırdığını** bulmak: premise
revizyonu · aday/kayda giren oranı · **`[R]` oranı** (sıfır uyarıdır, başarı
değil — hiç yanılmamış denetim sınanmamış denetimdir) · kapanışta açık `[KKE]`
· kullanılan rampalar · `[K]`'ya terfi · **kaçan** (denetimin akışlarını kapsayıp
gözden kaçırdığı, sonradan bulunan sorun — dışarıdan gelen ve içeriden
manipüle edilemeyen tek sayı).

Çizelge de bir iddiadır: denetimi üreten koşu doldurduysa `independence`
kontrolü eksiktir, `[KKE]`'dir. Söyle.
