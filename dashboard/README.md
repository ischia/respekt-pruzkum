# Prototyp dashboardu

Interaktivní segmentační pohled nad `respekt_analyticky.csv`. Definuješ až **tři
segmenty (A/B/C)** a porovnáš je vedle sebe; u každého tématu vidíš podíl osob
v segmentu, volitelně i celek (baseline = svislá ryska).

## Spuštění

```bash
python3 dashboard/build_data.py     # vygeneruje dashboard/data.json z CSV
python3 dashboard/serve.py          # http://localhost:8731/
```

`data.json` je odvozený agregát (jen indexy filtrů + booleany, žádný volný text),
generuje se z `data/processed/respekt_analyticky.csv` a necommituje se.

## Ovládání segmentů

- **Ordinální osy** (délka předplatného, věk, vzdělání, uvažoval o zrušení,
  pravděpod. setrvání) – posuvník s **rozsahem** (dvě táhla). Např. „od Střední
  a lepší" = setrvání nastavíš na Střední–Velmi vysoká.
- **Kategoriální osy** (pohlaví, příjem, status) – klikací **multi-select** chipy.
- Zaškrtávátko u tabu segment zapíná/vypíná; klik na tab ho otevře k editaci.
- **Jmenovatel**: celý vzorek vs. jen ti, kdo otevřenou otázku zodpověděli
  (působí na panely Q155/Q156/Q153/Q154).
- **Řazení**: podle četnosti, nebo *podle rozdílu mezi segmenty* (vynese nahoru
  nejvíc rozlišující témata – jádro křížové analýzy).
- **Lift** (poměr segment/celek) se ukazuje jen u jednoho aktivního segmentu;
  při porovnání víc segmentů se zobrazují přímo procenta.

## Panely

Spokojenost · Zájmy (okruhy článků) · Co hledají · Proč platí · Forma konzumace ·
Situace užití · Oblíbené podcasty · Co mají na app nejradši · Frekvence užití ·
Preference délky formátu · Chvála Q155 · Výtky Q156 · Poslech v app Q153 ·
Odvozené signály z volného textu · Jiné sledované zdroje Q154.

Metriky z uzavřených baterií (`x`/prázdno) mají jmenovatel celý vzorek; otevřené
otázky (Q155/156/153/154) lze přepnout na „jen respondující".

## Panely = skutečné otázky

Každý panel odpovídá jedné otázce dotazníku (doslovné znění). V něm jsou
**původní zaškrtávací možnosti** i to, co jsme **dokódovali z volného textu**,
seřazené dohromady podle četnosti. Značky:

- **＋** = nová možnost dokódovaná z pole „Jiné" / z otevřené otázky (nebyla
  mezi zaškrtávátky). Otevřené otázky Q155/156/153/154 jsou ＋ celé.
- **⁺n** (superskript) = původní zaškrtávací možnost **obohacená o n zmínek**
  z volného textu (např. „Audio zní moc uměle ⁺20").
- bez značky = původní zaškrtávací možnost beze změny.

**Strop výběru:** u 10 z 12 uzavřených otázek byl v dotazníku limit **max. 2 možnosti**.
Panel to hlásí amber poznámkou. Důsledek: původní možnosti jsou „top-2" (vynucená
priorita), ne plné zastoupení – **nelze je napřímo srovnávat s ＋ tématy z textu**, která
limit neměla. Detekuje se automaticky z dat (pile-up na maximu). Srovnání segmentů A/B
tím ovlivněno **není** (strop platí pro všechny stejně).

## Drilldown a sdílení

- **Drilldown**: klikni na řádek s 🔍 (možnosti ＋ a ⁺n) → modal se **zněním
  konkrétních odpovědí**, přepínatelně po segmentech (Celek / A / B / C). Text se
  bere z příslušné otázky, resp. z „Jiné" pole, ze kterého možnost vznikla.
- **Sdílení**: tlačítko „🔗 zkopírovat odkaz" uloží celý stav (segmenty, rozsahy,
  jmenovatel, řazení) do URL (`#…`). Odkaz obnoví přesně tento pohled.

Protože drilldown potřebuje volný text, `data.json` ho obsahuje – proto se
**necommituje** (je v `.gitignore`).

## Možná rozšíření

- Statistická významnost rozdílu segmentů (malé segmenty mají n v tooltipu).
- Export aktuálního pohledu (PNG / CSV řádků segmentu).
- Vyhledávání/filtr ve zněních odpovědí v drilldownu.
