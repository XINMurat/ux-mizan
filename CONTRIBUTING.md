# Contributing to ux-mizan / ux-mizan'a Katkı

*(English first — Türkçe aşağıda.)*

ux-mizan audits other people's interfaces, so it holds itself to the rules
it enforces on them. A contribution that would fail its own validator is
not a contribution.

---

## English

### Ground rules (the same U1–U12 the tool enforces)

1. **A `[K]` needs an artifact.** No claim in this repo reaches `[K]`
   without a resolving evidence artifact and a non-model collector. This
   applies to claims about the skill itself: "this check works" is `[H]`
   until it has run against a case known to be positive.
2. **Every finding hangs off a flow.** No component scored in isolation,
   in the repo's own examples as much as in a user's registry.
3. **Severity is computed, never asserted.** `failure_magnitude ×
   priority_weight × frequency`, with the weight read from the flow.
4. **Append-only.** A refuted entry stays `[R]` in place. The `[R]` rows
   are the audit's own error rate, and deleting them for tidiness deletes
   the only honest measure of how often this method is wrong.
5. **Tier every non-obvious claim** in docs, PRs and issues with
   `[K]/[H]/[S]/[R]/[KKE]/[Y]`.
6. **Name the instrument.** Any threshold states what returns its verdict.
   "The model" is not an instrument; if the answer is the author, the
   claim is capped at `[KKE]`.
7. **Bilingual parity is required.** A user-facing doc change lands in
   **both** `docs/en/` and `docs/tr/`, and in both halves of `README.md`.
   Tier tags stay identical across languages — they are labels, not prose.

### A rule this project learned the hard way

**A new detector must run against a case known to be positive before it is
trusted on unknown ones.** Every structural check in this repo has shipped
with a silent under-report at least once: a trailing `\b` that could never
match, an overlay counted as a collapse, a class test that missed
Tailwind's bare utilities. A checker that under-reports is
indistinguishable from a clean codebase, which is the worst failure a
tool like this can have. `SELF-VALIDATION.md` keeps the list.

So a PR adding or changing a signal must show the before/after output on a
real file, not a synthetic fixture.

### Before opening a PR

```bash
pip install -r skill/ux-mizan/scripts/requirements.txt
python skill/ux-mizan/scripts/ux_validate.py --strict examples/ux-registry.example.yaml
git config core.hooksPath tools/hooks
```

### Rebuilding `ux-mizan.skill`

The packaged skill must stay byte-identical to `skill/ux-mizan/`; CI fails
if it drifts.

```bash
python tools/build_skill.py
git add ux-mizan.skill && git commit -m "rebuild ux-mizan.skill"
```

### Continuous integration

CI validates every `*ux-registry*.y*ml` in the repo (strict for
`examples/`, advisory elsewhere), runs U4 against the pull request's base
commit, self-tests that U1, U2, U3, U6 and the W-channel still fire, and
checks that the packaged `.skill` matches its source. A rule nobody
exercises is a rule that quietly stopped working.

### What this project does not want

- A new metric with no `app_type` gate. The matrix is what stops "good
  genericity" decaying into "the same metrics everywhere".
- A rule enforced only in prose. If it matters, it goes in the validator;
  everything else is negotiable by whatever host the skill runs in.
- Removing a `[R]` entry, an honesty annex, or a caveat that travels with
  a number.

---

## Türkçe

### Temel kurallar (aracın uyguladığı U1–U12'un aynısı)

1. **`[K]` için artefakt şart.** Bu depoda hiçbir iddia, çözümlenen bir
   kanıt artefaktı ve model olmayan bir toplayıcı olmadan `[K]` olmaz.
   Skill'in kendisi hakkındaki iddialar dahil: "bu kontrol çalışıyor",
   pozitif olduğu bilinen bir vakada koşana kadar `[H]`'dir.
2. **Her bulgu bir akışa bağlanır.** Deponun kendi örneklerinde de,
   kullanıcının registry'sinde de izole komponent puanlaması yok.
3. **Severity hesaplanır, iddia edilmez.**
4. **Yalnızca eklenir.** Reddedilen kayıt `[R]` olarak yerinde kalır.
   `[R]` satırları denetimin kendi hata payıdır; temizlik için silmek,
   yöntemin ne sıklıkla yanıldığının tek dürüst ölçüsünü silmektir.
5. **Aşikâr olmayan her iddiayı katmanlayın.**
6. **Ölçüm aracını adlandırın.** "Model" bir ölçüm aracı değildir; hakem
   iddianın sahibiyse iddia `[KKE]` tavanındadır.
7. **İki dilde eşitlik zorunlu.** Kullanıcıya görünen her doküman
   değişikliği hem `docs/en/` hem `docs/tr/` altına iner. Katman
   etiketleri dillerde aynı kalır — onlar etikettir, düzyazı değil.

### Bu projenin bedel ödeyerek öğrendiği kural

**Yeni bir dedektör, bilinmeyen vakalarda güvenilmeden önce pozitif olduğu
bilinen bir vakada koşturulur.** Bu depodaki her yapısal kontrol, en az bir
kez sessizce az-raporlayarak çıktı. Az raporlayan bir tarayıcı, temiz
koddan ayırt edilemez — bu tür bir aracın yapabileceği en kötü hata budur.
Liste `SELF-VALIDATION.md` içinde.

Bu yüzden bir sinyali ekleyen ya da değiştiren PR, çıktının **gerçek bir
dosyadaki** öncesi/sonrası hâlini göstermek zorundadır; sentetik fikstür
yetmez.

### PR açmadan önce

```bash
pip install -r skill/ux-mizan/scripts/requirements.txt
python skill/ux-mizan/scripts/ux_validate.py --lang tr --strict examples/ux-registry.example.yaml
git config core.hooksPath tools/hooks
```

### Bu projenin istemediği şeyler

- `app_type` kapısı olmayan yeni metrik. Matris, "iyi genericlik"in "her
  yerde aynı metrikler"e çürümesini engelleyen şeydir.
- Yalnızca düzyazıda uygulanan kural. Önemliyse validator'a girer;
  gerisi, skill'in koştuğu host'un düzyazısıyla pazarlık edilebilir.
- Bir `[R]` kaydını, bir dürüstlük şerhini ya da bir sayının yanında
  giden uyarıyı kaldırmak.
