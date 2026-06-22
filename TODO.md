# TODO – čištění a refaktor (pro práci v Claude Code)

Kontext a principy jsou v `README.md` (de-duplikace, oddělení valence, poziční indexy, gender-neutral).
Diagnóza níže vznikla nad exportem 2026-06-20; čísla v závorkách jsou tehdejší počty.
Po každé změně: `python run_all.py` a kontrola počtů + namátkový QA proti vzorkům.

---

## 1) Taxonomie otevřených otázek (`src/koduj_otevrene.py`) – refaktor

> ✅ **HOTOVO (2026-06-22):** Q156 a Q155 rozdělena široká témata; Q153 oddělena zvyklost + zrušeno prázdné téma;
> Q154 zúžen vzor investigativních titulů (§1d). MECE řešeno mechanismem tématu `(include, exclude)`.
> Souhrny per otázka v `SOUHRNY.md`. Text níže je původní zadání.

### 1a) Rozdělit příliš široká témata

**156 „Web / aplikace / UX / technika" (220) → 5 témat.** Připravené sub-vzorce:
- `aplikace_chovani` — `aplikac|\bapp\b|zapomina|kde jsem (skoncil|prestal)|spadne|zamrz|nefunguje app` (~99)
- `web_navigace` — `\bweb|listovat|posunovat|mezi clanky|na webu|prochazet` (~43)
- `vyhledavani` — *(už existuje, ponechat)* (~32)
- `prehlednost_archiv` — *(už existuje, ponechat)* (~36)
- `technicke_nacitani` — `pomal|nacit|technic|nestabil` (~31)
- ⚠️ Po rozdělení **zrušit** původní široký vzor, ať se vyhledávání a přehlednost/archiv nepočítají dvakrát (viz 1c).

**156 „Obsah / chybějící témata" (133) → 3 témata.** „Kulturní rubrika" je dominantní a patří zvlášť:
- `kulturni_rubrika` — `kultur|recenz|\btipy` (~85)
- `chybejici_oblasti` — `ekonom|\bsport|region|\bveda|domaci tema` (~32)
- `ton_vic_pozitivnich` — `pozitivn|nadej|depres|optimis` (~28)
- (Grafika/obálka už je samostatné téma – ponechat.)

**155 „Důvěra / věrohodnost / vyváženost" (325) → 2 témata:**
- `duvera_verohodnost` — `duver|verohodn|overen|\bfakt|pravd|serioz`
- `vyvazenost_objektivita` — `vyvazen|objektiv|nestrann|\bveci\b|obe strany`

**(Nižší priorita)**
- 155 „Forma" (54) → vytáhnout `preklady_zahranici` (`preklad|zahranicni media|spoluprac.*(atlantic|nyt|economist)`); zbytek nech jako forma/bez reklam.
- 153 „Jiná platforma / zvyklost" (133) → oddělit `zvyklost` (`zvykl|\bzvyk|jsem zvykly`) od názvu platformy.

### 1b) Zrušit / sloučit téměř prázdná témata
- 153 `Kvalita AI hlasu` (n=1) – zrušit (signál k AI hlasu je hlavně v 156).
- 156 `Jazyk / anglicismy` (n=1) – zrušit nebo sloučit do širší jazykové výhrady.

### 1c) Odstranit duplicitu / vnoření
- Po 1a zajistit **MECE** u 156 web/app: žádná odpověď ať není zachycená zároveň širokým i specifickým (vyhledávání, přehlednost) vzorem.
- 153: zvážit dvouúrovňovou strukturu – nadřazené `nepouziva_app_pro_poslech` (nezkoušel ∪ jiná platforma) + důvody (`agregace`, `zvyklost`, `sledovani_prehraneho`) jako pod-tagy. „Agregace" je z 68 % uvnitř „jiné platformy".
- Opravit kontaminaci vzoru `funguje_dobre` v 153 (chytá „na Spotify to funguje") – zúžit na hodnocení aplikace Respektu.

### 1d) Precision keyword vzorů
- 154 `Hlídací pes / Investigace / Neovlivní / Voxpot` (62) – vzor `investigace` chytá i obecné slovo; zúžit na názvy titulů (`investigace.cz`, `hlidacipes`, `neovlivni`, `voxpot`).
- 155 příklady – občas padá tatáž multi-label odpověď u více témat; vybírat distinktivnější (např. první odpověď, která téma matchuje a nematchuje sousední).

---

## 2) Čištění uzavřených proměnných (`src/prekodovani.py`)

- `pracovni_status_clean`: ~10 obecných profesí bez markeru typu úvazku (lékař, starosta, ředitelka…) teď padá do „Zaměstnaneckého poměru", pár je sporných (Hudebník ~ OSVČ). Projít a rozhodnout pravidlo.
- Zvážit připojení příznaků z otevřených otázek (`respekt_otevrene_kodovano.csv`) k hlavnímu `respekt_obohaceno.csv` přes `ID` – jeden analytický dataset.

---

## 3) QA

- Namátkový průchod: pro 2–3 témata u každé otázky ručně ověřit ~20 zakódovaných odpovědí (precision) a ~20 nezachycených (recall).
- Po každém refaktoru porovnat počty před/po, ať nedošlo k nečekanému propadu (jako u `podcasty_zapojeni_ord` při překlepu v transliteraci).

---

## 4) Další vrstvy (až bude taxonomie čistá)
- Strukturovaný brief: strojově čitelná struktura, RICE scaffolding, interpretace.
- Kompozitní/segmentové proměnné (denní segment, churn-risk) – teprve po dohodě, ne v rámci čištění.
