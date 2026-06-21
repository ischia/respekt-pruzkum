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
