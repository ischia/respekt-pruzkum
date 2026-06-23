# RICE audit – vstupy z průzkumu předplatitelů

Vygenerováno z `respekt_analyticky.csv` · N = 2139 · mladší <44 = 721 · uvažovali o zrušení = 274.

**Co survey dodává:** Reach (kolik osob chce/trápí, na úrovni osoby, OR napříč zdroji) + tři Impact-signály + Confidence. **Effort, finální Impact a RICE skóre doplní produkt/eng tým** (survey je neumí).

**Impact-signály (lift vůči celku, >1 = nadprůměr):**
- **Churn-lift** – jak moc téma řeší ti, kdo *uvažovali o zrušení* → retence/ARPU.
- **Mladší-lift** – jak moc ho řeší <44 → akvizice/konverze + návyk.
- **Typ** – *oprava* (odstranění bolesti) vs *hodnota* (nová přidaná hodnota).

| # | Iniciativa | Kat. | Reach (n / %) | Churn-lift | Mladší-lift | Conf. | Typ |
|---|---|---|---|---|---|---|---|
| 1 | Doručení tisku (kvalita/včasnost) | Distribuce | 409 / 19 % | **1.2×** | 1.0× | vysoká | oprava |
| 2 | Audio: kvalita / AI hlas | Audio | 336 / 16 % | **1.4×** | **1.4×** | vysoká | oprava |
| 3 | Výraznější odlišení přečteného | App/UX | 256 / 12 % | 0.9× | **1.3×** | vysoká | hodnota |
| 4 | Přehlednost / navigace UI | App/UX | 254 / 12 % | **1.4×** | **1.5×** | vysoká | oprava |
| 5 | Vyhledávání (v appce / archiv) | App/UX | 247 / 12 % | 0.8× | **1.3×** | vysoká | oprava |
| 6 | Souhrny / kratší verze článků | Obsah | 187 / 9 % | **1.8×** | **1.2×** | střední | hodnota |
| 7 | Otevírat články ze soc. sítí v appce | App/UX | 126 / 6 % | 1.2× | **1.7×** | střední | hodnota |
| 8 | CarPlay / Android Auto | Audio | 126 / 6 % | **1.2×** | **1.3×** | střední | hodnota |
| 9 | Audio: playlist / ovládání | Audio | 125 / 6 % | **1.2×** | **1.4×** | střední | hodnota |
| 10 | Výkon / stabilita appky | App/UX | 122 / 6 % | **1.3×** | **1.4×** | střední | oprava |
| 11 | Lepší offline režim | App/UX | 93 / 4 % | **1.6×** | **1.3×** | střední | hodnota |
| 12 | Kulturní rubrika | Obsah | 85 / 4 % | **1.5×** | 0.8× | střední | oprava |
| 13 | Vnímaná jednostrannost / bias | Obsah | 64 / 3 % | **2.1×** | 1.0× | nízká | oprava |
| 14 | Personalizace rubrik / notifikace | App/UX | 47 / 2 % | 0.8× | 1.1× | nízká | hodnota |
| 15 | Grafika / obálka / ilustrace | Obsah | 39 / 2 % | 0.6× | 0.5× | nízká | hodnota |
| 16 | Chybějící oblasti (ekonomika, region…) | Obsah | 32 / 1 % | **1.2×** | 1.1× | nízká | hodnota |
| 17 | Tón / víc pozitivního | Obsah | 28 / 1 % | **2.0×** | **1.5×** | nízká | hodnota |
| 18 | Reklamy | Pricing | 21 / 1 % | **1.9×** | 0.3× | nízká | oprava |
| 19 | Cena / paywall (vč. audio-only) | Pricing | 11 / 1 % | **2.1×** | **1.6×** | nízká | oprava |
| 20 | Přístupnost (velikost písma) | App/UX | 10 / 0 % | 0.0× | 0.3× | nízká | oprava |

## Jak to číst dál (RICE)

1. **Reach** = berte `Reach_n` (počet osob za rok, případně škálujte na celou bázi předplatitelů).
2. **Impact** = zvažte podle cíle: retence → váha na churn-lift; akvizice/návyk → na mladší-lift; u *oprav* spíš obrana churnu, u *hodnoty* spíš zapojení/akvizice.
3. **Confidence** = sloupec výše (velikost vzorku + shoda víc zdrojů). Pozn.: čísla z textu jsou přibližná.
4. **Effort** = doplní eng/produkt; pak `RICE = Reach × Impact × Confidence / Effort`.

**Pozn. k Reach:** některé položky měly v dotazníku strop 2 voleb → jsou to spíš *top-2 priority*, ne plný zájem; Reach je tedy konzervativní spodní odhad.
