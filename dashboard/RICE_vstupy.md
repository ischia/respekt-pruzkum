# RICE audit – vstupy z průzkumu předplatitelů

Vygenerováno z `respekt_analyticky.csv` · N = 2139 · mladší <44 = 721 · uvažovali o zrušení = 274.

**Co survey dodává:** Reach (kolik osob chce/trápí, na úrovni osoby, OR napříč zdroji) + dva Impact-signály + Confidence. **Effort, finální Impact a RICE skóre doplní produkt/eng tým** (survey je neumí).

**Impact-signály (lift vůči celku, >1 = nadprůměr):**
- **Churn-lift** – jak moc téma řeší ti, kdo *uvažovali o zrušení* → retence/ARPU.
- **Mladší-lift** – jak moc ho řeší <44 → akvizice/konverze + návyk.

| # | Iniciativa | Reach (n / %) | Churn-lift | Mladší-lift | Conf. |
|---|---|---|---|---|---|
| 1 | Audiočlánky ladění (kvalita / AI hlas) | 336 / 16 % | **1.4×** | **1.4×** | vysoká |
| 2 | Výraznější odlišení přečteného | 256 / 12 % | 0.9× | **1.3×** | vysoká |
| 3 | Přehlednost / navigace UI | 254 / 12 % | **1.4×** | **1.5×** | vysoká |
| 4 | Vyhledávání (v appce / archiv) | 247 / 12 % | 0.8× | **1.3×** | vysoká |
| 5 | Souhrny / kratší verze článků | 187 / 9 % | **1.8×** | **1.2×** | střední |
| 6 | Deeplinky (otevírat články z odkazů v appce) | 126 / 6 % | 1.2× | **1.7×** | střední |
| 7 | CarPlay / Android Auto | 126 / 6 % | **1.2×** | **1.3×** | střední |
| 8 | Audio: playlist / ovládání | 125 / 6 % | **1.2×** | **1.4×** | střední |
| 9 | Výkon / stabilita appky | 122 / 6 % | **1.3×** | **1.4×** | střední |
| 10 | Lepší offline režim | 93 / 4 % | **1.6×** | **1.3×** | střední |
| 11 | Notifikace – automatizace, podcasty/témata/autoři | 47 / 2 % | 0.8× | 1.1× | nízká |
| 12 | Vypnout self-promo bannery pro přihlášené [ⓘ](# "měřeno přes výtku „reklamy“ (Q156); ~5 zmínek explicitně self-promo, low-effort") | 21 / 1 % | **1.9×** | 0.3× | nízká |
| 13 | Přístupnost (velikost písma) | 10 / 0 % | 0.0× | 0.3× | nízká |
| 14 | Příznak „vyjde v tištěném vydání“ † [ⓘ](# "5 zmínek v textu (Q153) – aby čtenáři článek nečetli digitálně dřív") | ~5 | — | — | nízká |
| 15 | Kopírování textu † [ⓘ](# "z volného textu (Q156), počet zmínek nevyčíslen") | — | — | — | nízká |
| 16 | Landing page pro Instagram † [ⓘ](# "doporučení (slide 12 decku), survey nevyčísluje") | — | — | — | nízká |
| 17 | Připomínací newslettery (zvýšení frekvence návštěv) † [ⓘ](# "doporučení z chování segmentů (reaktivace pasivních), survey nevyčísluje") | — | — | — | nízká |

**†** = z volného textu / doporučení, survey nevyčísluje (*Reach* = ruční odhad počtu zmínek, nebo „—“). **ⓘ** = detail po najetí myší. Reach i Effort doplní tým.

## Jak to číst dál (RICE)

1. **Reach** = berte `Reach_n` (počet osob za rok, případně škálujte na celou bázi předplatitelů).
2. **Impact** = zvažte podle cíle: retence → váha na churn-lift; akvizice/návyk → na mladší-lift.
3. **Confidence** = sloupec výše (velikost vzorku + shoda víc zdrojů). Pozn.: čísla z textu jsou přibližná.
4. **Effort** = doplní eng/produkt; pak `RICE = Reach × Impact × Confidence / Effort`.

**Pozn. k Reach:** některé položky měly v dotazníku strop 2 voleb → jsou to spíš *top-2 priority*, ne plný zájem; Reach je tedy konzervativní spodní odhad.
