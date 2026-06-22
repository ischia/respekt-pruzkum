# Souhrny zpracovaných otázek (podklad pro prezentaci)

Průběžný přehled výsledků kódování volných „Jiné, doplňte" polí u uzavřených otázek.
Po každé vyřešené otázce sem přibyde tabulka nových příznaků + klíčová zjištění.

**Metoda (platí pro všechny):** každý příznak je boolean na úrovni respondující osoby
(zaškrtnuto NEBO zmíněno v textu, započítá se max. jednou). Témata se kódují per-otázka
(oddělení valence), text se bere jen z dané otázky. N = 2 139 dokončených odpovědí.
Frekvence z volného textu jsou přibližné (zachycují jasné formulace).

---

## Q28 — „Co vás přimělo nakonec si předplatné pořídit?" (konverzní motivy)

640 volných textů; pokrytí existujícími příznaky **7 % → 55 %**.

**Existující checkboxy (kontext):** Podpořit nezávislá média 1373 · Konkrétní článek/reportáž 335 ·
Akční nabídka/sleva 311 · Doporučení od známého 225 · Podcast 55 · Soc. sítě 20 · Newsletter 8.

**Nové příznaky (z volného textu, žádný neměl checkbox):**

| příznak | n | co zachycuje |
|---|---|---|
| `konv_kvalita_obsah` | 151 | kvalita / pestrost obsahu, poctivá novinařina |
| `konv_dlouholety_ctenar` | 96 | zvyk, „čtu od vzniku", cesta ze stánku k předplatnému |
| `konv_prehled` | 39 | týdenní přehled, „být v obraze" |
| `konv_duvera` | 36 | věrohodnost, ověřené / nezkreslené informace |
| `konv_pohodli` | 18 | mít to ve schránce, nemuset shánět |
| `konv_zahranici` | 15 | život v zahraničí |

**Klíčová zjištění:**
- Největší **skrytý** motiv konverze je **kvalita obsahu** (151) a **dlouholetý vztah ke značce** (96) —
  věci, které baterie checkboxů vůbec nenabízela.
- „Podpořit nezávislá média" je nejčastější *zaškrtnutá* možnost (1373), ale jako *spontánně psaný* důvod
  ji převažuje kvalita a osobní vztah → hodnotová podpora je rámec, kvalita je spouštěč.

---

## Q137 — „Setkal/a jste se při čtení/poslechu s bariérami?" (bariéry)

213 volných textů.

**Existující checkboxy (kontext):** Nesetkal, vše vyhovuje 1084 · Pozdní doručení 383 · Audio zní uměle 278 ·
UX/ovládání 200 · Délka článků 119 · Tech. problémy přístupu 97 · Rušivé reklamy 90 · Psychické/těžká témata 80.

**Nové samostatné příznaky (bez checkboxu):**

| příznak | n | co zachycuje |
|---|---|---|
| `bariera_vyhledavani` | 13 | vyhledávání, dohledání starších článků, archiv |
| `bariera_obsah` | 11 | málo/moc kultury, hudby, politiky, zrušená témata |
| `bariera_epub` | 6 | EPUB layout, Kindle/čtečka, import |

**Obohacení existujících checkboxů o text (čistý přírůstek nad zaškrtnuté):**

| příznak | změna | nuance navíc |
|---|---|---|
| `doruceni_vc_text` | 383 → 402 (+19) | bez obalu, promočený deštěm, zahraničí, urgování |
| `cas_delka_vc_text` | 119 → 138 (+19) | nejen délka, ale i množství / nedostatek času |
| `audio_umele_vc_text` | +13 → +20 | chybné čtení/výslovnost, jeden hlas pro tazatele i odpovídajícího |
| `tech_problemy_vc_text` | +10 → +18 | zasekne, vypršení tokenu/přihlášení, přestane hrát |

**Klíčová zjištění:**
- **AI audio** vadí víc, než ukázal samotný checkbox — text přidal +20 zmínek (chybné čtení, výslovnost,
  nerozlišení tazatel/odpovídající jedním hlasem).
- **Vyhledávání** je jasná produktová mezera: 13 lidí ho napsalo nevyžádaně do „Jiné" (a je to zároveň
  samostatné téma ve výtkách Q156).
- U **doručení** je vedle „pozdě" druhá osa — **balení/poškození** (bez obalu, promočený deštěm).

---

## Q60 — „Co vás přimělo přejít na digitál?" (přechod na digitál)

271 volných textů; pokrytí **35 % → 45 %**. Pole dominují lidé, kteří **nepřešli** (čtou tisk/obojí —
to už pokrývá `cte_tisk_i_digital`); nové příznaky kódují **důvody a způsob užití**.

**Existující checkboxy (kontext):** Pohodlnost (vše v telefonu) 529 · Audio dostupné jen digitálně 344 ·
Praktické (zahraničí, nestíhám fyzicky) 298 · Ekologické důvody 200 · Cena 136.

**Nové příznaky:**

| příznak | n | co zachycuje |
|---|---|---|
| `digital_doplnek` | 20 | digitál jako doplněk / situačně (doma papír, na cestách digitál, v práci) |
| `preferuje_tisk` | 15 | přednost papíru: haptika, offline, odpočinek od displeje, pondělní rituál |
| `tisk_pro_rodinu` | 12 | tištěné posílá/sdílí s rodinou, sám čte digitál |

**Klíčová zjištění:**
- Velká část předplatitelů digitál **aktivně odmítá** — tištěný **rituál** (pondělí, káva, schránka),
  **haptika** a **únava z obrazovky** jsou reálné kotvy retence, ne jen setrvačnost.
- Digitál je pro mnohé **doplněk**, ne náhrada (papír doma, digitál/audio na cestách).
- **„Tištěné posílám rodičům"** je opakovaný vzorec — relevantní pro dárkové předplatné i retenci.

---

## Q95 — „Co vám nejvíce chybí v mobilní aplikaci?" (chybějící funkce)

144 volných textů. Pole obsahuje hodně „nic nechybí" (pokrývá `aplikace_nic_nechybi`); vyhledávání je
samostatný checkbox (box 88, 229) — text k němu přidá jen +2, proto se znovu nekóduje.

**Existující checkboxy (kontext):** Výraznější odlišení přečteného 251 · Vyhledávání 229 ·
Otevírat ze soc. sítí 126 · Vlastní audio playlist 120 · CarPlay/Android Auto 118 ·
Lepší offline režim 93 · Častější notifikace 41.

**Nové příznaky (z volného textu, žádný neměl checkbox):**

| příznak | n | co zachycuje |
|---|---|---|
| `app_prehlednost` | 12 | nepřehlednost, menu, navigace, návrat zpět, „předělat" |
| `app_pristupnost` | 10 | velikost písma/fontů, zoom obrázků, popisky, čtení bez brýlí |
| `app_vykon` | 10 | pomalost, sekání, stabilita, načítání, spotřeba dat, bugy |
| `app_audio_ovladani` | 6 | vypnout autoplay, pauzy mezi články, celé vydání, pozice/délka |
| `app_personalizace` | 6 | filtrování rubrik, sekce, nepřečtené nahoře, synchronizace |
| `app_odliseni_tisk` | 5 | rozlišit, který článek vyjde v tištěné / je jen na webu |

**Klíčová zjištění:**
- Tři nejčastější stížnosti jsou **přehlednost UI** (12), **přístupnost** (velikost písma/obrázků, 10)
  a **výkon/stabilita** (10) — UX/technická triáda, kterou baterie checkboxů vůbec nenabízela.
- **Přístupnost** (zvětšení písma, čtení bez brýlí) je silný a snadno řešitelný signál vzhledem
  k věkovému profilu čtenářstva.
- Opakovaná **audio přání**: vypnout autoplay, pauzy mezi články, přehrát celé vydání najednou.
- Niche, ale konkrétní: čtenáři chtějí **poznat, který článek vyjde v tištěné verzi** (aby ho nečetli digitálně).

---

## Q73 — „S jakým hlavním cílem na domovskou stránku přicházíte?" (cíl na homepage)

70 volných textů, dosud bez příznaku. Pole je malé; checkboxy pokrývají hlavní cíle. Nové příznaky
zachycují dvě věci, které checkboxy minuly — a které spolu tvoří jeden silný závěr.

**Existující checkboxy (kontext):** Hledám nové zajímavé čtení 593 · Prolistovat vydání/archiv 580 ·
Zjistit co se děje 494 · Audioverze/podcast 485 · Konkrétní článek 271 · Správa předplatného 170.

**Nové příznaky:**

| příznak | n | co zachycuje |
|---|---|---|
| `homepage_vstup_odkaz` | 15 | přichází přes externí odkaz: newsletter/mail, sociální sítě, RSS, QR z tisku |
| `homepage_nechodi` | 8 | na homepage prakticky nechodí (jde rovnou na audio, RSS, čte papír) |

**Klíčová zjištění:**
- **Homepage často není vstupní bod.** Část čtenářů sem nepřichází přímo — dorazí přes newsletter,
  sociální sítě, RSS nebo QR kód z tištěného čísla (15), nebo homepage prakticky nepoužívá (8).
- Implikace: **distribuce přes newsletter a sítě je reálná vstupní brána** k obsahu, ne jen doplněk.

---

## Q156 — „Co vám na Respektu nejvíce vadí a co by měl zlepšit?" (výtky / náměty)

1307 volných odpovědí. **Otevřená otázka po retaxonomizaci** (rozdělena dvě příliš široká témata, valence
oddělená od chvály Q155) → 16 témat. Příznaky jsou multi-label (jedna odpověď může nést víc témat).

| téma | n | poznámka |
|---|---|---|
| Nic nevadí / spokojenost | 288 | |
| Audio / AI hlas | 102 | smíšené – část AI kritizuje, část akceptuje |
| Kulturní rubrika | 85 | nejčastější obsahová výtka |
| Aplikace / technika (UX, bugy, výkon) | 82 | bez vyhledávání/přehlednosti (ty zvlášť) |
| Délka článků (moc dlouhé) | 67 | |
| Jednostrannost / bias / aktivismus | 64 | |
| Web / navigace | 44 | |
| Grafika / obálka / ilustrace | 39 | hodně „chybí Reisenauer" |
| Přehlednost / archiv / orientace | 36 | |
| Vyhledávání | 32 | nejkonkrétnější funkční mezera |
| Chybějící oblasti (ekonomika, sport, věda, region) | 32 | |
| Doručení tisku | 29 | |
| Tón / víc pozitivního | 28 | „depresivní", chybí naděje |
| Četnost / víc obsahu | 22 | |
| Reklamy | 21 | |
| Cena / paywall | 11 | |

**Co změnila retaxonomizace:** staré „Web/aplikace/UX/technika" (220) bylo nafouknuté – přes holé „chybí"
pohlcovalo ~69 *obsahových* výtek (chybí Reisenauer, kultura, optimismus). Po rozdělení jdou správně do
grafiky/kultury/tónu a platforma se rozpadla na Aplikace/technika + Web + samostatné Vyhledávání + Přehlednost
(s odečtem, aby se nepočítaly dvakrát). Staré „Obsah" (133) → Kulturní rubrika (85) + Chybějící oblasti + Tón.

**Klíčová zjištění:**
- **Redakce:** dominují kulturní rubrika (85), vnímaná jednostrannost/aktivismus (64), depresivní tón /
  chybí pozitivní zprávy (28); opakovaný námět délka článků (67).
- **Aplikace/produkt:** platformní problémy (82) + vyhledávání (32) + přehlednost (36) = velký balík;
  vyhledávání je nejkonkrétnější funkční požadavek.
- **Audio/AI (102)** je velké a smíšené – vazby na věk/formát půjdou dotáhnout přes spojený dataset.

---

## Q155 — „V čem je podle vás Respekt výjimečný oproti jiným médiím?" (chvála)

1534 volných odpovědí. **Otevřená otázka po retaxonomizaci** (rozdělena dvě široká témata) → 13 témat.
Pozitivní valence, oddělená od výtek (Q156). Multi-label.

| téma | n |
|---|---|
| Šíře a výběr témat | 461 |
| Hloubka, kontext, souvislosti | 385 |
| Kvalita psaní, jazyk, úroveň | 370 |
| Autoři, osobnosti, redakce | 304 |
| Důvěra, věrohodnost, fakta | 194 |
| Nezávislost | 180 |
| Hodnotové souznění, světonázor | 173 |
| Vyváženost, objektivita, nestrannost | 170 |
| Investigativa, reportáže | 87 |
| Tradice, značka | 67 |
| Překlady, zahraniční obsah | 66 |
| Nepodbízivost, odvaha | 55 |
| Forma (bez reklam, audio, epub) | 20 |

**Co změnila retaxonomizace:** staré „Důvěra/věrohodnost/vyváženost" (325) → **Důvěra/fakta** (194,
ověřenost, serióznost) + **Vyváženost/objektivita** (170, různé úhly, nestrannost) – dva odlišné důvody
chvály. Z „Formy" vytažen **Překlady/zahraniční obsah** (66) – kurátorství textů z Atlantic, NYT apod.

**Klíčová zjištění:**
- Jádro značky: **šíře témat** (461), **hloubka/kontext** (385), **kvalita psaní** (370).
- **Hodnotové souznění** (173) zní v chvále pozitivně (sdílený světonázor) – tatáž osa se v Q156 objevuje
  jako „jednostrannost/bias" (64) u jiné skupiny. Stejné téma, opačná valence (proto je nemícháme).
- **Překlady/zahraniční obsah** (66) – konkrétní, propagovatelná přednost (akvizice/marketing).

---

## Q153 — „Zkoušeli jste poslech v aplikaci Respektu? V čem je pro vás méně vhodný?" (poslech v app)

378 volných odpovědí. **Otevřená otázka po retaxonomizaci** (odděleno „zvyklost" od názvu platformy,
zrušeno prázdné „Kvalita AI hlasu" n=1). **Není to bug-report** – převažuje „proč jinou platformu".

| téma | n |
|---|---|
| Jiná platforma (Spotify/Apple/…) | 126 |
| Nezkoušel / neposlouchá v app | 119 |
| Důvod: vše na jednom místě (agregace) | 65 |
| Výtka: ovládání / přehlednost | 36 |
| Zvyklost / setrvačnost | 30 |
| Technický problém (přehrávání/pozice) | 21 |
| CarPlay / Auto / Bluetooth | 18 |
| Poslouchá jen audioverze článků | 12 |
| Důvod: sledování přehraného | 11 |
| Funguje dobře / spokojen | 4 |

**Klíčová zjištění:**
- Hlavní bariéra appky pro poslech **není v chybách** – lidé už mají **jinou platformu** (126) a **zvyk**
  (30), hlavně kvůli **agregaci všech podcastů na jednom místě** (65). Tomu se těžko konkuruje.
- Skutečné technické problémy (21) a výtky k ovládání (36) jsou menšina.
- **Produkt/akvizice do app:** realističtější než přetahovat ze Spotify je cílit na 119 lidí, co app
  pro poslech *vůbec nezkusili*.

---

## Q154 — „Jaké max. tři informační zdroje (kromě Respektu) sledujete?" (zdroje)

1671 odpovědí. Kódováno jako **jmenované entity** (konkrétní médium + typ zdroje), ne vágní témata.
Multi-label (až 3 zdroje/osoba). Po retaxu zúžen vzor investigativních titulů (§1d).

**Nejčastější zdroje (n osob):**
| zdroj | n |
|---|---|
| Deník N | 549 |
| Podcast (obecně i jmenovitě) | 491 |
| iRozhlas / Český rozhlas | 414 |
| Seznam Zprávy / Seznam.cz | 403 |
| ČT / ČT24 | 374 |
| Aktuálně.cz | 118 |
| Hospodářské noviny | 116 |
| Novinky.cz | 81 |
| Slovenské (SME, Denník N, Aktuality) | 66 |
| Další zahraniční (FT, WaPo, Politico, Spiegel…) | 56 |
| BBC | 55 |
| Hlídací pes / Investigace.cz / Neovlivní / Voxpot | 48 |

**Typy zdrojů (n):** Domácí zpravodajství 983 · Veřejnoprávní 671 · Podcast 491 · Zahraniční 165 ·
Alternativní/investigativní 108 · Slovenské 66 · Domácí tisk/komentář 63 · Influencer/osobnost 45 ·
Sociální sítě/video 43 · Newsletter 8.

**Klíčová zjištění:**
- Nejčastější „jiný" zdroj je **Deník N** (549) – přímý konkurent v segmentu. Pak veřejnoprávní
  (iRozhlas, ČT) a Seznam.
- Předplatitelé Respektu jsou **náročné publikum** – běžně kombinují kvalitní domácí + veřejnoprávní
  + zahraniční zdroje (BBC, Economist, NYT…).
- §1d fix: „Alternativní/investigativní" zpřesněno (122→108) odstraněním obecného slova „investigace"
  (dříve počítalo i „Seznam – investigace").

