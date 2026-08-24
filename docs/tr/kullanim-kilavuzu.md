# Kullanım Kılavuzu

**Statü: v0.2 `[H]`.** Bir öz-doğrulama koşusu yapıldı; Katman-A betikleri
sınandı ve bir tasarım kararı çürüdü. Kapılar, walkthrough ve tüm
davranışsal metrikler hâlâ sınanmadı.

## Kurulum

```bash
cp -r skill/ux-mizan ~/.claude/skills/     # yol .../skills/ux-mizan/SKILL.md olmalı
pip install -r skill/ux-mizan/scripts/requirements.txt
cp templates/ux-registry.yaml <projeniz>/ux-registry.yaml
```

En sık hata çift iç içe klasördür: `~/.claude/skills/ux-mizan/ux-mizan/`
değil, `~/.claude/skills/ux-mizan/SKILL.md`.

Claude.ai / masaüstü için `ux-mizan.skill` dosyasını yükleyin
(Ayarlar → Yetenekler → Skills); güncellemek için yeniden yükleyin.

## Ne zaman tetiklenir, ne zaman tetiklenmez

**Tetiklenir:** UX denetimi, kullanılabilirlik incelemesi, "kullanıcılar
kayboluyor", "arayüz karışık", "neden bırakıyorlar", bilgi mimarisi
incelemesi, kullanılabilirlik ölçümü kurmak, teşhise dayanan redesign.

**Tetiklenmez:** görsel/marka tasarımı, metin yazımı, sıfırdan arayüz
kurmak. "Bu düğme hangi renk olsun" sorusu bu ağırlığı hak etmez.

**Kardeşleriyle sınır:** Mizan iddiaları denetler, Kıyas fikir üretir,
İskele projeyi yapılandırır. Bu, deneyimi denetler.

## Akış

### 1. Kapı 0 — amaç ve öncelik (SERT)

Model taslak önerir, **insan kilitler**. Kilitlenmeden hiçbir bulgu
`[H]`'nin üstüne çıkamaz (U7). Sebep basit: model amacı kendisi çıkarıp
kendi çıkarımına göre denetlerse döngü kapanır ve denetim çürütülemez
hâle gelir.

Kilitlenecekler: işler (kullanıcının kelimeleriyle, özellik adlarıyla
değil), her birinin `priority_weight`'i, "tamamlandı" ne demek, ve onu
işaretleyen rota (`success_screen`).

### 2. Kapı 1 — tip, hacim, mod

`app_type` her akış için ayrı seçilir ve **hangi metriklerin geçerli
olduğunu belirler**. Altı seçenek:

| app_type | kapattığı metrik |
|---|---|
| `navigational-multiscreen` | — (tam batarya) |
| `form-heavy-transactional` | lostness (yol dayatılmış) |
| `single-canvas-tool` | lostness, nav_depth (tek ekran) |
| `b2b-internal-dashboard` | sus (mahsur kullanıcı, taban sansürü) |
| `content-consumption` | task_success (görev yok) |
| `guided-sequence` | lostness, nav_depth (sırayı sunucu dayatıyor) |

Hacim modu belirler: akış başına aylık **~300 tamamlamanın altı → lite**.
Düşük hacimde pasif telemetri aylarca karar üretmez; 5–8 moderasyonlu
oturum "nerede" ve "neden"i bir öğleden sonrada verir.

### 3. Katman A — walkthrough ve betikler

```bash
python skill/ux-mizan/scripts/structural_checks.py src/     # ne eksik
python skill/ux-mizan/scripts/layout_signals.py src/        # nasıl yerleşmiş
```

Her sayı `[KKE]`: bakılacak yeri söyler, kusuru değil. `layout_signals`
iki katman basar — iz `[KKE]`, davranışsal iddia `[H]` — ve `[H]` satırını
dosya kanıtlamış gibi raporlamak yasaktır.

**Bulguyu yazmadan önce dosyayı açın.** Bu depoda hem yanlış negatif hem
yanlış pozitif üretmiş her iki betik de bu kuralla yakalandı.

### 4. Kapı 2 — hipotez onayı

Aday bulgular registry'ye **yazılmadan önce** insana gider. Ön-kayıt kilidi
burada kapanır: veriden sonra yazılan eşik HARKing'dir.

### 5. Registry ve doğrulama

```bash
python skill/ux-mizan/scripts/ux_validate.py --strict ux-registry.yaml
git config core.hooksPath tools/hooks
```

**Registry hafızadır, transcript değil.** Bulguyu doğrulanır doğrulanmaz
dosyaya ekleyin; sona saklamak, bir sonraki bağlam sıfırlamasında
kaybetmek demektir.

### 6. Kapı 3 — yön onayı (SERT)

İnsan **pikseli değil**, teşhisi + öncelik çerçevesini + yönü onaylar.
Mockup gösterip "beğendiniz mi" diye sormak onay tiyatrosudur.

Her öneri için zorunlu öz-kontrol: *bu, bu uygulamanın Kapı-0 amacından mı
geliyor, yoksa jenerik varsayılandan mı?* "Jenerik varsayılan ve burada
doğrusu bu" kabul edilebilir bir yanıttır; sormamak değil.

### 7. Ölçüm ve Kapı 4

Baseline **redesign'dan önce** ölçülür — sonradan "öncesi"ni ölçmenin
ikinci şansı yoktur. `[K]` yalnızca gerçek Katman-B verisi ve insan
kararıyla verilir; doğrulayıcı zaten kanıt artefaktı olmadan `[K]`
yazılmasına izin vermez.

## Lostness

```
L = sqrt( (N/S − 1)² + (R/N − 1)² )
```

Akış hedefini ve `canonical_path_R`'ı **önceden** ilan ederse, L sıradan
ekran telemetrisinden pasif hesaplanabilir. Önceden ilan, işin tamamıdır:
veriden sonra çıkarılan R, HARKing'dir ve betik tahmin etmeyi reddeder.

```bash
python skill/ux-mizan/scripts/lostness.py events.jsonl --registry ux-registry.yaml
```

Dört uyarı her sayının yanında basılır: yalnızca navigasyonel tipler için
geçerlidir; *nerede*yi söyler, *neden*i söylemez; akış başınadır, global
değil; ve 0,4/0,5 eşikleri hipertext çalışmalarından gelir, sizin
uygulamanız için valide değildir.

## Sert kurallar (U1–U12)

| kural | ne yapar |
|---|---|
| U1 | `[K]` için çözümlenen kanıt artefaktı + model olmayan kaynak şart |
| U2 | `parent_flow_id` zorunlu ve çözümlenmeli — akış-primatı |
| U3 | severity yeniden hesaplanır; ağırlık insan-kilitli akıştan okunur |
| U4 | yalnızca ekleme; `[R]` kayıtları çıkarılamaz |
| U5 | çürütme koşulu + adlandırılmış ölçüm aracı zorunlu |
| U6 | metrik uygulanabilirlik kapısı (iki sıçrama: app_type → akış → bulgu) |
| U7 | kapı provenance; Kapı 0 kilitli değilse tavan `[H]` |
| U8 | davranışsal `[K]` öncesi ölçülmüş baseline şart |
| U9 | `[K]` öncesi kilitli `min_n` ve karar kuralı |
| U10 | önerilen düzeltme homojenleşme öz-kontrolü taşır — jenerik varsayılan mı diye sorulmamış bir redesign, bu skill'in teşhis ettiği hastalığın kendisidir |
| U11 | `[KKE]` *hangi* kontrolün eksik olduğunu adlandırır; "kontrol eksik" hangisi denmeden eyleme dönüşmez |
| U12 | açık bir bulgu `review_by` taşır; tarih geçtiğinde bulgu bir karar kaydetmek zorundadır — uzat, beklet ya da kapat. W4 bunu 0.1'den beri uyarıyordu; U12, uyarıyı terminal yapan tarihtir |

W1–W4 uyarıları bloke etmez; `--strict` onları hataya çevirir. CI strict
koşar, yerel koşu koşmaz — yalnızca durdurabilen bir araç, insanlara onu
tetiklemeyen registry yazmayı öğretir.
