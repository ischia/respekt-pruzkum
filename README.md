# Respekt – předplatitelský průzkum: datový model a pipeline

Reprodukovatelné zpracování předplatitelského dotazníku Respektu (export ze SurveyHero).
Pipeline normalizuje znečištěné uzavřené otázky, vytahuje nové proměnné z volného textu
(s důsledným **odečtením již zaškrtnutých**, aby se nic nepočítalo dvakrát) a koduje
čtyři otevřené otázky do tematické taxonomie.

Zpracováno genericky neutrální češtinou; původní znění odpovědí a možností je zachováno doslovně.

---

## Struktura repa

```
respekt-pruzkum/
├── README.md                 ← tento soubor (datový model)
├── requirements.txt
├── run_all.py                ← spustí celou pipeline
├── data/
│   ├── raw/                  ← sem patří export SurveyHeroResponses*.csv (necommituje se)
│   └── processed/            ← generované výstupy (necommituje se)
└── src/
    ├── prekodovani.py        ← uzavřené otázky → nové proměnné
    ├── koduj_otevrene.py     ← otevřené otázky → taxonomie + kódování
    └── spoj_dataset.py       ← spojí oba výstupy přes ID → analytický dataset
```

## Jak spustit

```bash
python -m venv .venv && source .venv/bin/activate     # volitelné
pip install -r requirements.txt
python run_all.py
```

`run_all.py` automaticky vezme **nejnovější** `data/raw/SurveyHeroResponses*.csv`
(řazeno podle názvu, takže nový export jen vlož do `data/raw/`) a zapíše výstupy do `data/processed/`.

---

## Datový model

Zdroj: SurveyHero CSV. Pipeline filtruje na `Status == 'Completed'`.
V aktuálním exportu (2026-06-20) to je **2 139** dokončených odpovědí, **162** sloupců.
Baterie s výběrem více možností jsou kódované hodnotou `x` / prázdno.

> **Upozornění:** sloupce se v pipeline adresují podle **pozice** (indexu), protože SurveyHero
> nedává stabilní názvy. Pokud se v novém exportu změní pořadí nebo přibude/ubude otázka,
> je třeba indexy v obou skriptech zkontrolovat.

### Metadata (sloupce 0–10)
`ID`, časy, `Status`, `Collector`, `Language`, `IP`, `Device`, `{mwg_rnd}`, `{url}`, `{userid}`.

### Uzavřené otázky – jedna odpověď
Délka předplatného; věk; pohlaví; vzdělání; příjem; dvě škály 1–5 (spokojenost s doručováním,
pravděpodobnost setrvání); baterie spokojenosti (7 oblastí); baterie preferované délky formátů (4);
úvahy o zrušení; frekvence návštěv webu a aplikace; zapojení do podcastů; dříve čtený tištěný časopis aj.

### Baterie – výběr více možností
Akvizice; co přimělo pořídit; co lidé hledají; důvody platby; forma čtení; co přimělo přejít na digitál;
využití digitálního přístupu; cíl na homepage; okruhy; situace čtení; oblíbenost aplikace; co v aplikaci chybí;
bariéry; oblíbené podcasty. Většina má pole „Jiné/Jinak, doplňte".

### Otevřené otázky
Pole „Jiné, doplňte" napříč bateriemi (11×) + samostatné otevřené otázky.
**Čtyři velké otevřené otázky** zpracovává `koduj_otevrene.py` zvlášť (viz Taxonomie níže):
poslech v aplikaci (153), zdroje kromě Respektu (154), v čem výjimečný (155), co vadí/zlepšit (156).

---

## Nové proměnné (`prekodovani.py`)

59 nových sloupců (37 obecných + 6 konverzních z col 28 + 5 bariérových z col 137 + 3 digitální z col 60
+ 6 aplikačních z col 95 + 2 z col 73); detail a počty v `data/processed/respekt_codebook_nove.csv`.
Obohacený dataset je `respekt_obohaceno.csv`.

**Řídící pravidlo – nenadhodnocovat:** každá příznaková proměnná je boolean na úrovni
respondující osoby = `zaškrtnuto NEBO zmíněno v textu`. Osoba se započítá nejvýše jednou.

**A) Normalizace znečištěných „uzavřených" otázek**
`pracovni_status_clean` (6 čistých kategorií + zpětvzatá skupina **Pracující důchod**;
kombinace → první uvedený status), `duchodce` (flag, jakákoli penze),
`podcast_platforma_clean` (sloučení dlouhého ocasu třetích aplikací do „Jiná podcastová aplikace").

**B) Nové binární příznaky z textu** (žádný existující checkbox)
`pouziva_audioteku`, `predplatne_darek`, `cte_tisk_i_digital` (korekce „nepřešel/a, čtu obojí"
u otázky na přechod – ⅓ tamních textových odpovědí!), `situace_jidlo`, `situace_cekani`,
`situace_prochazka`, `situace_kavarna`, `styk_pres_zname_rodinu`, `zajem_krizovka`, `aplikace_nic_nechybi`.

**B2) Konverzní motivy z volného textu „Co vás přimělo pořídit předplatné" (col 28)** – témata, která
v baterii (cols 21–27) nemají checkbox, takže jde o čistý přírůstek: `konv_kvalita_obsah` (151),
`konv_dlouholety_ctenar` (96), `konv_prehled` (39), `konv_duvera` (36), `konv_pohodli` (18), `konv_zahranici` (15).
Pokrytí volného textu vzrostlo ze 7 % na 55 % (zbytek jsou jednorázové odpovědi / „nevzpomínám si").

**B3) Bariérové motivy z volného textu „Setkal/a jste se s bariérami" (col 137)** – témata bez checkboxu
v baterii bariér: `bariera_vyhledavani` (13), `bariera_obsah` (11), `bariera_epub` (6).

**B4) Přechod na digitál z volného textu „Co vás přimělo přejít na digitál" (col 60)** – pole dominují lidé,
kteří nepřešli (pokrývá `cte_tisk_i_digital`); nové příznaky kódují *důvody/způsob užití*: `preferuje_tisk` (15),
`digital_doplnek` (20), `tisk_pro_rodinu` (12). Pokrytí pole 35 % → 45 %.

**B5) Co chybí v aplikaci z volného textu „Co vám nejvíce chybí" (col 95)** – produktové požadavky bez
checkboxu (vyhledávání je už checkbox box 88, proto se nekóduje znovu): `app_prehlednost` (12),
`app_pristupnost` (10, velikost písma/obrázků), `app_vykon` (10), `app_audio_ovladani` (6),
`app_personalizace` (6), `app_odliseni_tisk` (5, který článek vyjde v tištěné).

**B6) Cíl na homepage z volného textu „S jakým cílem na homepage přicházíte" (col 73)** – homepage často
není vstupní bod: `homepage_vstup_odkaz` (15, přes newsletter/sítě/RSS/QR), `homepage_nechodi` (8).

**C) Obohacení existujících možností** – původní „jak zaškrtnuto" je zachováno; varianta `_vc_text`
přidává jen text navíc (po odečtení překryvu): `audio_umele_vc_text`, `tech_problemy_vc_text`,
`styk_soc_site_vc_text`, `doruceni_vc_text`, `cas_delka_vc_text` (z col 137; recall audio/tech rozšířen).

**D) Ordinální → numerické** (strukturální příprava pro korelace): délka předplatného, věk, vzdělání,
příjem („Nechci odpovídat" = chybějící), frekvence web/app, pravděpodobnost setrvání, úvahy o zrušení,
zapojení do podcastů, baterie spokojenosti (Spokojen=1/Nespokojen=0/Nevím=chybějící),
baterie délky (delší=+1/kratší=−1/Nevím=chybějící).

---

## Taxonomie otevřených otázek (`koduj_otevrene.py`)

Pravidlová multi-label klasifikace (klíčová slova) zakotvená ve čtení vzorků.
Výstupy: `respekt_otevrene_taxonomie.xlsx` (list na otázku: téma, n, %, doslovné příklady)
a `respekt_otevrene_kodovano.csv` (boolean příznaky na respondující osobu).

- **154 – zdroje:** zpracováno jako **jmenované entity** (médium + typ zdroje), ne jako vágní témata.
  Nejčastější „jiný" zdroj je Deník N. Typy: veřejnoprávní, domácí zpravodajství, domácí tisk/komentář,
  alternativní/investigativní, zahraniční, slovenské, podcast, influencer/osobnost, sociální sítě, newsletter.
  *(Retax §1d: vzor investigativních titulů zúžen na názvy – holé „investigace" už nekontaminuje.)*
- **155 – chvála (pozitivní valence), 13 témat po retaxu:** šíře témat, hloubka/kontext, kvalita psaní,
  autoři/redakce, nezávislost, *(rozděleno)* důvěra/věrohodnost/fakta + vyváženost/objektivita/nestrannost,
  investigativa, hodnotové souznění, *(vytaženo)* překlady/zahraniční obsah, forma, nepodbízivost, tradice.
- **156 – výtky/náměty (negativní/konstruktivní), 16 témat po retaxu:** nic nevadí; *web/app rozděleno na*
  web/navigace, aplikace/technika (s odečtem specifik), vyhledávání, přehlednost/archiv; audio/AI (smíšená
  valence); *obsah rozdělen na* kulturní rubrika, chybějící oblasti, tón/víc pozitivního; grafika/obálka,
  jednostrannost/bias, délka článků, četnost, doručení, cena, reklamy.
- **153 – poslech v aplikaci (10 témat, retax):** **není to bug-report** – převažuje „proč jinou platformu"
  (nově oddělena *jiná platforma* vs *zvyklost/setrvačnost*; agregace všech podcastů na jednom místě);
  technické problémy jsou menšina. Zrušeno prázdné „Kvalita AI hlasu" (n=1).

---

## Klíčové principy a upozornění

- **De-duplikace / nenadhodnocování:** příznaky se počítají na úrovni osoby (logické NEBO), ne jako
  součet zaškrtnutí + zmínek. U obohacení existujících možností je čistý přírůstek = jen text bez překryvu.
- **Oddělení valence:** chvála (155) a výtky (156) se nekódují společně – stejné téma (např. hodnoty/světonázor)
  zní v 155 pozitivně, v 156 negativně. Sloučení by vyrobilo falešné signály.
- **Frekvence z otevřených otázek jsou přibližné** – zachycují jasné formulace; nuance a překlepy mohou unikat.
- **Poziční indexy sloupců** – viz upozornění výše; po novém exportu ověřit.
- **Čeština** – výstupní popisy genericky neutrální; původní znění odpovědí a možností doslovné.

## Výstupy (`data/processed/`)

| soubor | obsah |
|---|---|
| `respekt_obohaceno.csv` | původní data + 59 nových sloupců |
| `respekt_codebook_nove.csv` | seznam nových proměnných (skupina, typ, n) |
| `respekt_otevrene_taxonomie.xlsx` | taxonomie 4 otevřených otázek (četnosti, příklady) |
| `respekt_otevrene_kodovano.csv` | boolean kódování otevřených otázek na respondující osobu |
| `respekt_analyticky.csv` | **spojený dataset** (obohaceno + kódování otevřených přes `ID`) – 1 řádek/respondent, 294 sloupců; základ pro křížové analýzy |

> Pozn.: `*.xlsx` ukládá procenta jako vzorce; hodnoty se dopočítají při otevření v Excelu/LibreOffice.
