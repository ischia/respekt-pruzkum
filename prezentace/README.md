# Prezentace – Klíčová zjištění (reveal.js)

Webová prezentace (HTML), obsah editovatelný v Markdownu.

## Spuštění
```bash
python3 prezentace/serve.py     # → http://localhost:8790/
```
(Reveal načítá `slides.md` přes fetch, takže `index.html` nestačí otevřít přes `file://` —
je potřeba server. Stačí i `cd prezentace && python3 -m http.server 8790`.)

## Editace obsahu
Vše je v **`slides.md`**:
- snímky odděluje `---` na samostatném řádku (prázdné řádky kolem)
- nadpis snímku `## 2 · Nadpis`
- odrážky `- text`, tučně `**takto**`
- graf `![](charts/nazev.png)`
- callout „Co s tím" = blokcitace `> text`
- velké číslo (snímek bez grafu) `<p class="stat">11×</p>`

Po úpravě stačí **refresh prohlížeče**. Vzhled (barvy, fonty, layout) je v `index.html` v `<style>`.

## Ovládání
Šipky / mezerník = další snímek · `Esc` = přehled všech snímků · `F` = celá obrazovka ·
`S` = poznámky/řečnický pohled · číslo snímku vpravo dole.

## Export do PDF
V prohlížeči otevři `http://localhost:8790/?print-pdf`, pak Tisk → Uložit jako PDF
(okraje „žádné", pozadí grafiky zapnuté).

## Online sdílení
Složku `prezentace/` lze nahrát na GitHub Pages / Netlify a sdílet odkazem
(je self-contained – grafy jsou v `charts/`).

## Grafy
Generují se z dat skriptem `python3 charts/make_charts.py`; pak je zkopíruj sem:
`cp charts/*.png prezentace/charts/`.
