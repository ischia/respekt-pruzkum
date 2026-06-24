#!/usr/bin/env python3
"""Extrahuje z respekt_analyticky.csv kompaktní data.json pro prototyp dashboardu.

Panely kopírují skutečné otázky dotazníku. Každá metrika má původ (origin):
  orig = původní zaškrtávací možnost (bez značky)
  new  = možnost, kterou jsme dokódovali z pole „Jiné" / z otevřené otázky (＋)
  enr  = původní možnost obohacená o zmínky z textu (zobrazí superskript ⁺n)

Výstup data.json:
  filters, metric_groups, metric_keys, metric_labels,
  metric_origin{col->orig|new|enr}, metric_increment{col->n}, metric_textkey{col->key},
  text_labels, respond, rows[[filtry..,metriky..,respond_flagy]], texts[]

Princip projektu: nenadhodnocovat – každá metrika je bool na úrovni osoby.
Sloupce se adresují názvem (DictReader); po novém exportu ověřit, že existují.
"""
import csv
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "processed", "respekt_analyticky.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# --- Segmentační osy ---------------------------------------------------------
FILTERS = [
    {"key": "delka", "label": "Délka předplatného", "type": "ordinal",
     "col": "Jak dlouho si předplácíte Respekt?",
     "order": ["< 1 rok", "1–5 let", "6–10 let", "11–15 let", "16–20 let", "21+ let"],
     "map": {"Kratší dobu než rok": "< 1 rok", "1–5 let": "1–5 let",
             "6–10 let": "6–10 let", "11–15 let": "11–15 let",
             "16–20 let": "16–20 let", "21 a více let": "21+ let"}},
    {"key": "vek", "label": "Věk", "type": "ordinal",
     "col": "Jaký je váš věk?",
     "order": ["<18", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"],
     "map": {"Méně než 18": "<18", "18–24": "18–24", "25–34": "25–34",
             "35–44": "35–44", "45–54": "45–54", "55–64": "55–64",
             "65 a více": "65+"}},
    {"key": "vzdelani", "label": "Vzdělání", "type": "ordinal",
     "col": "Jaké je vaše nejvyšší dosažené vzdělání?",
     "order": ["Základní", "Vyučen/SŠ", "SŠ s maturitou", "Vysokoškolské"],
     "map": {"Základní": "Základní", "Vyučen / SŠ bez maturity": "Vyučen/SŠ",
             "SŠ s maturitou": "SŠ s maturitou", "Vysokoškolské": "Vysokoškolské"}},
    {"key": "zruseni", "label": "Uvažoval/a o zrušení", "type": "ordinal",
     "col": "uvazoval_zruseni_ord",
     "order": ["Ne", "Spíše ano", "Ano"],
     "map": {"0.0": "Ne", "1.0": "Spíše ano", "2.0": "Ano"}},
    {"key": "setrvani", "label": "Pravděpod. setrvání", "type": "ordinal",
     "col": "pravdep_setrvani_ord",
     "order": ["Velmi nízká", "Nízká", "Střední", "Vysoká", "Velmi vysoká"],
     "map": {"1.0": "Velmi nízká", "2.0": "Nízká", "3.0": "Střední",
             "4.0": "Vysoká", "5.0": "Velmi vysoká"}},
    {"key": "frekv_app", "label": "Frekvence aplikace", "type": "ordinal",
     "col": "frekvence_app_ord",
     "order": ["Nepoužívá", "Několikrát/měsíc", "Každý týden",
               "Několikrát/týden", "Každý den"],
     "map": {"0.0": "Nepoužívá", "1.0": "Několikrát/měsíc", "2.0": "Každý týden",
             "3.0": "Několikrát/týden", "4.0": "Každý den"}},
    {"key": "frekv_web", "label": "Frekvence webu", "type": "ordinal",
     "col": "frekvence_web_ord",
     "order": ["Nepoužívá", "Několikrát/měsíc", "Každý týden",
               "Několikrát/týden", "Každý den"],
     "map": {"0.0": "Nepoužívá", "1.0": "Několikrát/měsíc", "2.0": "Každý týden",
             "3.0": "Několikrát/týden", "4.0": "Každý den"}},
    {"key": "pohlavi", "label": "Pohlaví", "type": "categorical",
     "col": "Jaké je vaše pohlaví?",
     "order": ["Žena", "Muž", "Jiné / nechci uvést"]},
    {"key": "prijem", "label": "Příjem domácnosti", "type": "categorical",
     "col": "Jaký je čistý měsíční příjem vaší domácnosti?",
     "order": ["Do 40 000 Kč", "40 001–70 000 Kč", "70 001–100 000 Kč",
               "Nad 100 000 Kč", "Nechci odpovídat"]},
    {"key": "status", "label": "Pracovní status", "type": "categorical",
     "col": "pracovni_status_clean",
     "order": ["Zamestnanecky pomer", "OSVC / podnikani", "Student/ka",
               "V domacnosti / na rodicovske", "Duchod (nepracujici)",
               "Pracujici duchod", "Nezamestnany/a", "Neuvedeno / jine"]},
    {"key": "poslech", "label": "Poslech podcastů", "type": "categorical",
     "col": "Posloucháte podcasty Respektu?",
     "order": ["Ano, pravidelně", "Ano, občas", "Vím o nich, ale neposlouchám",
               "Zkoušel/a, ale přestal/a", "Nevím o nich"],
     "map": {"Ano, pravidelně": "Ano, pravidelně", "Ano, občas": "Ano, občas",
             "Vím o nich, ale neposlouchám": "Vím o nich, ale neposlouchám",
             "Zkoušel/a jsem, ale přestal/a": "Zkoušel/a, ale přestal/a",
             "Nevím o nich": "Nevím o nich"}},
    {"key": "platforma", "label": "Platforma podcastů", "type": "categorical",
     "col": "podcast_platforma_clean",
     "order": ["Aplikace Respektu", "Spotify", "Web Respektu", "Apple Podcasts",
               "Jiná aplikace", "YouTube", "Audiotéka"],
     "map": {"Aplikace Respektu": "Aplikace Respektu", "Spotify": "Spotify",
             "Web Respektu": "Web Respektu", "Apple Podcasts": "Apple Podcasts",
             "Jina podcastova aplikace": "Jiná aplikace", "YouTube": "YouTube",
             "Audioteka": "Audiotéka"}},
]

# Kanál (forma) – multi-label boolean filtr (osoba má víc kanálů; OR logika)
FORMA_CHANNELS = [
    ("Papírové vydání", "Papírové vydání"),
    ("Web Respekt.cz", "Web"),
    ("Mobilní aplikace.1", "Aplikace"),
    ("Podcastové aplikace", "Podcastové aplikace"),
    ("Newslettery", "Newslettery"),
    ("Čtečka EPUB verze (Kindle, Pocketbook apod.)", "EPUB"),
]

# --- Otevřené otázky: respond flag (zodpověděl/a otevřenou otázku) ------------
RESPOND_COLS = {
    "q153": "Zkoušeli jste poslech v aplikaci Respektu? Popište, v čem je pro vás méně preferovaná než vámi vybraná varianta.",
    "q154": "Napište, jaké max. tři informační zdroje (média, ale i podcasty nebo influencery) kromě Respektu pravidelně sledujete a v čem jsou pro vás výjimeční?",
    "q155": "V čem je podle vás Respekt výjimečný oproti jiným médiím?",
    "q156": "Co vám na Respektu nejvíce vadí a co by měl zlepšit?",
}

# --- Zdroje volného textu pro drilldown (textkey -> (sloupec, popis)) ---------
TEXTCOLS = {
    "q155": (RESPOND_COLS["q155"], "V čem je Respekt výjimečný (Q155)"),
    "q156": (RESPOND_COLS["q156"], "Co nejvíc vadí (Q156)"),
    "q153": (RESPOND_COLS["q153"], "Poslech v aplikaci (Q153)"),
    "q154": (RESPOND_COLS["q154"], "Jiné sledované zdroje (Q154)"),
    "jine_styk": ("Jinak, doplňte", "Styk před předplacením – Jiné"),
    "jine_konv": ("Jiné, doplňte", "Co přimělo pořídit předplatné – Jiné"),
    "jine_hleda": ("Jiné, doplňte.1", "Co hledáte – Jiné"),
    "jine_forma": ("Jiné, doplňte.3", "Forma čtení/poslechu – Jiné"),
    "jine_digital": ("Jiné, doplňte.4", "Proč přejít na digitál – Jiné"),
    "jine_homepage": ("Jiné, doplňte.5", "Cíl na homepage – Jiné"),
    "jine_app": ("Jiné, doplňte.7", "Co chybí v aplikaci – Jiné"),
    "jine_situace": ("Jiné, doplňte.8", "Situace užití – Jiné"),
    "jine_bariery": ("Jiné, doplňte.9", "Bariéry při čtení/poslechu – Jiné"),
}

# --- Pomocné konstruktory položek (col, label, kind, origin, textkey, origcol)
def o(col, label, kind="check"):
    return (col, label, kind, "orig", None, None)
def nw(col, label, tk):
    return (col, label, "bool", "new", tk, None)
def en(vccol, label, tk, origcol):
    return (vccol, label, "bool", "enr", tk, origcol)

# jednovýběrové / škálové otázky → rozbalení na rozdělení (id, syrový sloupec, [(hodnota,label)])
DIST_SPECS = [
    ("podlisten", "Posloucháte podcasty Respektu?", [
        ("Ano, pravidelně", "Ano, pravidelně"),
        ("Ano, občas", "Ano, občas"),
        ("Vím o nich, ale neposlouchám", "Vím o nich, ale neposlouchám"),
        ("Zkoušel/a jsem, ale přestal/a", "Zkoušel/a, ale přestal/a"),
        ("Nevím o nich", "Nevím o nich")]),
    ("podfreq", "Jak často váš oblíbený pořad Respektu posloucháte?", [
        ("Pravidelně každou epizodu", "Pravidelně každou epizodu"),
        ("Přibližně každou druhou epizodu", "Přibližně každou druhou epizodu"),
        ("Nepravidelně", "Nepravidelně")]),
    ("podplat", "podcast_platforma_clean", [
        ("Aplikace Respektu", "Aplikace Respektu"), ("Spotify", "Spotify"),
        ("Web Respektu", "Web Respektu"), ("Apple Podcasts", "Apple Podcasts"),
        ("Jina podcastova aplikace", "Jiná podcastová aplikace"),
        ("YouTube", "YouTube"), ("Audioteka", "Audiotéka")]),
    ("doruc", "Jak jste spokojen/a s doručováním tištěného Respektu?", [
        ("5", "5 – velmi spokojen/a"), ("4", "4"), ("3", "3"), ("2", "2"),
        ("1", "1 – velmi nespokojen/a")]),
    ("ctedrive", "Četl/a jste dříve tištěný časopis?", [
        ("Ano", "Ano"), ("Ne", "Ne")]),
    ("changeform", "Uvažujete o změně formy čtení Respektu?", [
        ("Ne, neuvažuji", "Ne, neuvažuji"),
        ("Ano, přechod z tisku do digitálu", "Ano – z tisku do digitálu"),
        ("Ano, přechod z digitálu na tisk", "Ano – z digitálu na tisk")]),
    ("predpl", "Jak dlouho si předplácíte Respekt?", [
        ("Kratší dobu než rok", "Kratší dobu než rok"), ("1–5 let", "1–5 let"),
        ("6–10 let", "6–10 let"), ("11–15 let", "11–15 let"),
        ("16–20 let", "16–20 let"), ("21 a více let", "21 a více let")]),
    ("zruseni", "uvazoval_zruseni_ord", [
        ("0.0", "Ne"), ("1.0", "Spíše ano"), ("2.0", "Ano")]),
    ("setrvani", "pravdep_setrvani_ord", [
        ("5.0", "Velmi vysoká"), ("4.0", "Vysoká"), ("3.0", "Střední"),
        ("2.0", "Nízká"), ("1.0", "Velmi nízká")]),
]

# Barevné palety kategorií pro panely typu „rozdělení" (naskládaný pruh).
# Zelená = pozitivní/silné využití, šedá = žádné/Nevím, červená = negativní.
GREEN, TEAL, BLUE, AMBER, CORAL, RED, GRAY = (
    "#639922", "#1D9E75", "#378ADD", "#EF9F27", "#F0997B", "#E24B4A", "#B4B2A9")
DIST_PALETTE = {
    "podlisten": [GREEN, TEAL, "#9FE1CB", CORAL, GRAY],
    "podfreq": [GREEN, "#5DCAA5", GRAY],
    "podplat": ["#534AB7", TEAL, BLUE, "#5F5E5A", AMBER, RED, CORAL],
    "doruc": [GREEN, "#9FE1CB", AMBER, CORAL, RED],
    "ctedrive": [TEAL, GRAY],
    "changeform": [GRAY, BLUE, AMBER],
    "predpl": ["#B5D4F4", "#85B7EB", BLUE, "#185FA5", "#0C447C", "#042C53"],
    "zruseni": [GREEN, AMBER, RED],
    "setrvani": [TEAL, "#9FE1CB", AMBER, CORAL, RED],
    "freq": [GREEN, TEAL, "#5DCAA5", "#9FE1CB", GRAY],  # web/app 5 úrovní
}

# Baterie (matice) – 3 kategorie na řádek. Pořadí řádků = pořadí v dotazníku.
FREQ_LEVELS = [(4, "Každý den"), (3, "Několikrát za týden"), (2, "Každý týden"),
               (1, "Několikrát za měsíc"), (0, "Nepoužívám")]
SPOK_AREAS = [
    ("mnozstvi", "Množství článků", "Množství článků"),
    ("delka", "Délka článků", "Délka článků"),
    ("temata", "Výběr témat", "Výběr témat"),
    ("vyvazenost", "Vyváženost", "Vyváženost"),
    ("prehlednost", "Přehlednost", "Přehlednost"),
    ("reklama", "Množství reklamy", "Množství reklamy"),
    ("audio", "Kvalita načtení audiočlánků", "Kvalita audia"),
]
LEN_FMT = [
    ("texty", "Texty (kratší zprávy/komentáře vs. reportáže, rozhovory apod.)", "Texty"),
    ("audioclanky", "Audiočlánky (kratší zprávy/komentáře vs. reportáže, rozhovory apod.)", "Audiočlánky"),
    ("podcasty", "Podcasty (souhrny a glosy událostí vs. delší rozhovory a diskuze)", "Podcasty"),
    ("videa", "Videa (souhrny a glosy událostí vs. delší rozhovory a diskuze)", "Videa"),
]
SPOK_CATS = [("Spokojen/a", GREEN), ("Nespokojen/a", RED), ("Nevím", GRAY)]
SPOK_VALS = ["Spokojen/a", "Nespokojen/a", "Nevím"]
LEN_CATS = [("Spíše delší", TEAL), ("Spíše kratší", BLUE), ("Nevím", GRAY)]
LEN_VALS = ["Spíše delší", "Spíše kratší", "Nevím"]


def matrix_items(prefix, rows, cats):
    """Položky matice: pro každý řádek × kategorii jeden bool sloupec
    (mx_<prefix>_<rowid>_<catidx>). Popisek = kategorie (pro tooltip)."""
    items = []
    for rid, _, _ in rows:
        for ci, (clab, _) in enumerate(cats):
            items.append((f"mx_{prefix}_{rid}_{ci}", clab, "bool", "orig", None, None))
    return items


def matrix_rows(prefix, rows, cats):
    """Render-metadata: [(popisek řádku, [sloupce kategorií])]."""
    return [(rlab, [f"mx_{prefix}_{rid}_{ci}" for ci in range(len(cats))])
            for rid, _, rlab in rows]


def _dist_opts(sid):
    return next(opts for s, _, opts in DIST_SPECS if s == sid)

# --- Panely = skutečné otázky dotazníku --------------------------------------
GROUPS = [
    ("spok", "Jak vnímáte Respekt v následujících oblastech?",
     "Rozdělení odpovědí na řádek (součet = 100 % z těch, kdo oblast hodnotili). "
     "Pruh „Nevím\" = nevyužívá / bez expozice.", None,
     matrix_items("spok", SPOK_AREAS, SPOK_CATS)),

    ("styk", "Jak jste přišel/a do styku s Respektem před předplacením?",
     "Podíl osob. ＋ = dokódováno z „Jinak, doplňte\".", None, [
        o("Četl/a jsem články na webu", "Četl články na webu"),
        o("Kupoval/a jsem si ho na stáncích", "Kupoval na stáncích"),
        o("Poslouchal/a jsem podcasty", "Poslouchal podcasty"),
        o("Sledoval/a jsem videopodcasty na YouTube", "Videopodcasty na YouTube"),
        en("styk_soc_site_vc_text", "Na sociálních sítích", "jine_styk",
           "Sledoval/a jsem Respekt a/nebo jeho redaktory/ky na sociálních sítích"),
        o("Dříve jsem ho nečetl/a", "Dříve nečetl"),
        nw("styk_pres_zname_rodinu", "Přes známé / rodinu", "jine_styk"),
     ]),

    ("konv", "Co vás přimělo nakonec si předplatné pořídit?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Obecně jsem chtěl/a podpořit nezávislá média", "Podpořit nezávislá média"),
        o("Konkrétní článek nebo reportáž, která mě zaujala", "Konkrétní článek/reportáž"),
        o("Akční nabídka/sleva", "Akční nabídka/sleva"),
        o("Doporučení od známé/ho", "Doporučení od známého"),
        o("Podcast — dostal/a jsem se přes něj k obsahu a chtěl/a víc", "Podcast"),
        o("Příspěvek nebo reklama na sociálních sítích", "Sociální sítě"),
        o("Newsletter", "Newsletter"),
        nw("konv_kvalita_obsah", "Kvalita / pestrost obsahu", "jine_konv"),
        nw("konv_dlouholety_ctenar", "Dlouholetý vztah ke značce", "jine_konv"),
        nw("konv_prehled", "Přehled / být v obraze", "jine_konv"),
        nw("konv_duvera", "Důvěra / věrohodnost", "jine_konv"),
        nw("konv_pohodli", "Pohodlí (mít to ve schránce)", "jine_konv"),
        nw("konv_zahranici", "Život v zahraničí", "jine_konv"),
        nw("predplatne_darek", "Dostal/a jako dárek", "jine_konv"),
     ]),

    ("hleda", "Když čtete nebo posloucháte Respekt, co hledáte?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Hloubkový kontext", "Hloubkový kontext"),
        o("Názory/interpretace", "Názory / interpretace"),
        o("Inspiraci/nové pohledy", "Inspirace / nové pohledy"),
        o("Rychlé shrnutí, co se děje", "Rychlé shrnutí"),
        o("Odpočinek/čtení pro radost", "Odpočinek / radost"),
        nw("zajem_krizovka", "Křížovka", "jine_hleda"),
     ]),

    ("procplati", "Jaké jsou pro vás hlavní důvody, proč za Respekt platíte?",
     "Podíl osob, které důvod označily.", None, [
        o("Podpora nezávislé žurnalistiky a hodnot, které Respekt hájí", "Podpora nezávislosti"),
        o("Přístup k exkluzivnímu obsahu", "Exkluzivní obsah"),
        o("Oblíbení autoři", "Oblíbení autoři"),
        o("Audiočlánky", "Audiočlánky"),
        o("Mobilní aplikace", "Mobilní aplikace"),
        o("Tištěný časopis", "Tištěný časopis"),
        o("Podpora vzniku podcastů", "Podpora podcastů"),
     ]),

    ("forma", "V jaké formě čtete/posloucháte Respekt nejčastěji?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Mobilní aplikace.1", "Mobilní aplikace"),
        o("Papírové vydání", "Papírové vydání"),
        o("Web Respekt.cz", "Web"),
        o("Podcastové aplikace", "Podcastové aplikace"),
        o("Newslettery", "Newslettery"),
        o("Čtečka EPUB verze (Kindle, Pocketbook apod.)", "EPUB čtečka"),
        nw("pouziva_audioteku", "Audiotéka", "jine_forma"),
     ]),

    ("digital", "Co vás přimělo přejít na digitál?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Pohodlnost (mám vše v telefonu)", "Pohodlnost (vše v telefonu)"),
        o("Audiočlánky/podcasty jsou dostupné jen digitálně", "Audio jen digitálně"),
        o("Praktické důvody (bydlím v zahraničí, nestíhám číst fyzicky)", "Praktické důvody"),
        o("Ekologické důvody (tisk časopisu, plastový obal, rozvoz,…)", "Ekologické důvody"),
        o("Cena (digitál je levnější)", "Cena"),
        nw("preferuje_tisk", "Preferuje tisk (rituál, haptika)", "jine_digital"),
        nw("digital_doplnek", "Digitál jen jako doplněk", "jine_digital"),
        nw("tisk_pro_rodinu", "Tisk pro rodinu", "jine_digital"),
        nw("cte_tisk_i_digital", "Nepřešel/a – čte tisk i digitál", "jine_digital"),
     ]),

    ("homepage", "S jakým hlavním cílem na domovskou stránku přicházíte?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Hledám nové zajímavé čtení", "Nové zajímavé čtení"),
        o("Chci si prolistovat nové vydání nebo archiv starších čísel", "Prolistovat vydání/archiv"),
        o("Chci zjistit, co se dneska stalo / co se děje", "Zjistit co se děje"),
        o("Jdu si poslechnout audioverzi článku nebo podcast", "Audioverze / podcast"),
        o("Hledám konkrétní článek, o kterém jsem slyšel/a", "Konkrétní článek"),
        o("Spravuji si zde své předplatné", "Správa předplatného"),
        nw("homepage_vstup_odkaz", "Vstup přes externí odkaz", "jine_homepage"),
        nw("homepage_nechodi", "Na homepage prakticky nechodí", "jine_homepage"),
     ]),

    ("apprado", "Co máte na mobilní aplikaci Respekt nejradši?",
     "Podíl osob, které možnost označily.", None, [
        o("Všechny audiočlánky a podcasty na jednom místě", "Audio na jednom místě"),
        o("Funkci uložení článků", "Uložení článků"),
        o("Archiv vydání", "Archiv vydání"),
        o("Možnost souvisle poslouchat celé vydání", "Souvislý poslech vydání"),
        o("Možnost stáhnout si vydání a číst ho offline", "Offline čtení"),
        o("Možnost využívat tmavý režim (vzhled)", "Tmavý režim"),
        o("Uživatelské rozhraní aplikace (rychlost, vzhled,…)", "UI aplikace"),
        o("Notifikace na důležité články a nová vydání", "Notifikace"),
     ]),

    ("appchybi", "Co vám nejvíce chybí v mobilní aplikaci?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Výraznější odlišení přečteného/poslouchaného", "Odlišení přečteného"),
        o("Vyhledávání", "Vyhledávání"),
        o("Možnost otevírat články Respektu ze sociálních sítí rovnou v aplikaci", "Otevírat ze soc. sítí"),
        o("Možnost sestavit si vlastní audio playlist", "Vlastní audio playlist"),
        o("Podpora pro Carplay/Android Auto", "CarPlay / Android Auto"),
        o("Lepší offline režim", "Lepší offline režim"),
        o("Častější notifikace (autoři, rubriky)", "Častější notifikace"),
        nw("aplikace_nic_nechybi", "Nic nechybí", "jine_app"),
        nw("app_prehlednost", "Přehlednost UI", "jine_app"),
        nw("app_pristupnost", "Přístupnost (velikost písma)", "jine_app"),
        nw("app_vykon", "Výkon / stabilita", "jine_app"),
        nw("app_audio_ovladani", "Ovládání audia", "jine_app"),
        nw("app_personalizace", "Personalizace", "jine_app"),
        nw("app_odliseni_tisk", "Odlišení tisk / web", "jine_app"),
     ]),

    ("situace", "V jakých situacích Respekt nejčastěji čtete nebo posloucháte?",
     "Podíl osob. ＋ = dokódováno z „Jiné, doplňte\".", None, [
        o("Při odpočívání doma", "Odpočinek doma"),
        o("Při dojíždění", "Dojíždění"),
        o("Když se dějí důležité události", "Důležité události"),
        o("V práci", "V práci"),
        o("Při vaření/uklízení doma", "Vaření / úklid"),
        o("Při sportování", "Sportování"),
        nw("situace_jidlo", "Při jídle", "jine_situace"),
        nw("situace_cekani", "Při čekání", "jine_situace"),
        nw("situace_prochazka", "Na procházce", "jine_situace"),
        nw("situace_kavarna", "V kavárně", "jine_situace"),
     ]),

    ("zajmy", "Jaké okruhy článků vás u nás zajímají nejvíce?",
     "Podíl osob, které okruh označily.", None, [
        o("Politické", "Politické"),
        o("Reportáže", "Reportáže"),
        o("Komentáře k aktuálnímu dění", "Komentáře"),
        o("Rozhovory", "Rozhovory"),
        o("Kulturní", "Kulturní"),
        o("Překlady zahraničních médií (The Atlantic, NYT, Die Zeit)", "Překlady zahraničí"),
        o("Ekonomické", "Ekonomické"),
        o("Podcasty/videa", "Podcasty / videa"),
        o("O rodině a vztazích", "Rodina a vztahy"),
     ]),

    ("podcasty", "Které podcasty Respektu posloucháte nejčastěji?",
     "Podíl osob, které podcast poslouchají.", None, [
        o("Výtah Respektu", "Výtah Respektu"),
        o("Vládneme, nerušit", "Vládneme, nerušit"),
        o("(Ne)bezpečí Ondřeje Kundry", "(Ne)bezpečí O. Kundry"),
        o("Ženy XYZ", "Ženy XYZ"),
        o("Dělníci kultury", "Dělníci kultury"),
        o("Tekutá společnost", "Tekutá společnost"),
        o("Československý podcast", "Československý podcast"),
        o("Zeitgeist", "Zeitgeist"),
     ]),

    ("bariery", "Setkal/a jste se při čtení nebo poslechu s bariérami?",
     "Podíl osob. ＋ = nová z „Jiné\"; ⁺n u obohacených = přidané zmínky z textu.", None, [
        o("Nesetkal/a, vše mi vyhovuje", "Nesetkal, vše vyhovuje"),
        en("doruceni_vc_text", "Časopis nepřišel včas", "jine_bariery",
           "Časopis mi nepřišel včas do schránky"),
        en("audio_umele_vc_text", "Audio zní moc uměle", "jine_bariery",
           "Audiočlánky zní moc uměle"),
        o("Problémy s uživatelským rozhraním (špatné ovládání aplikace, nepřehledný web)", "UX / ovládání"),
        en("cas_delka_vc_text", "Články jsou moc dlouhé", "jine_bariery",
           "Časové (články jsou moc dlouhé)"),
        en("tech_problemy_vc_text", "Technické problémy s přístupem", "jine_bariery",
           "Technické problémy s přístupem (nefunkční předplatné, problémy s přihlášením)"),
        o("Rušivé reklamy", "Rušivé reklamy"),
        o("Psychické (témata jsou pro mě těžká)", "Psychické (těžká témata)"),
        nw("bariera_vyhledavani", "Vyhledávání / archiv", "jine_bariery"),
        nw("bariera_obsah", "Obsah (málo/moc témat)", "jine_bariery"),
        nw("bariera_epub", "EPUB / čtečka", "jine_bariery"),
     ]),

    ("freqweb", "Jak často navštěvujete web Respekt.cz?",
     "Rozdělení frekvence (z těch, kdo na položku odpověděli). Součet ≈ 100 %.", None, [
        o("freq_web_lvl4", "Každý den", "bool"),
        o("freq_web_lvl3", "Několikrát za týden", "bool"),
        o("freq_web_lvl2", "Každý týden", "bool"),
        o("freq_web_lvl1", "Několikrát za měsíc", "bool"),
        o("freq_web_lvl0", "Nepoužívám", "bool"),
     ]),

    ("freqapp", "Jak často navštěvujete aplikaci Respekt?",
     "Rozdělení frekvence (z těch, kdo na položku odpověděli). Součet ≈ 100 %.", None, [
        o("freq_app_lvl4", "Každý den", "bool"),
        o("freq_app_lvl3", "Několikrát za týden", "bool"),
        o("freq_app_lvl2", "Každý týden", "bool"),
        o("freq_app_lvl1", "Několikrát za měsíc", "bool"),
        o("freq_app_lvl0", "Nepoužívám", "bool"),
     ]),

    ("delkapref", "Která kombinace formátů vám osobně vyhovuje nejvíce?",
     "Rozdělení na řádek (součet = 100 % z těch, kdo formát hodnotili). "
     "Pruh „Nevím\" = bez preference / formát nevyužívá.", None,
     matrix_items("len", LEN_FMT, LEN_CATS)),

    ("q155", "V čem je podle vás Respekt výjimečný? (otevřená otázka)",
     "Celá taxonomie kódována z volného textu (＋). Multi-label.", "q155", [
        nw("155_sire_a_vyber_temat", "Šíře a výběr témat", "q155"),
        nw("155_hloubka_kontext_souvislosti", "Hloubka, kontext", "q155"),
        nw("155_kvalita_psani_jazyk_uroven", "Kvalita psaní", "q155"),
        nw("155_autori_osobnosti_redakce", "Autoři, redakce", "q155"),
        nw("155_duvera_verohodnost_fakta", "Důvěra, fakta", "q155"),
        nw("155_nezavislost", "Nezávislost", "q155"),
        nw("155_hodnotove_souzneni_svetonazo", "Hodnotové souznění", "q155"),
        nw("155_vyvazenost_objektivita_nestr", "Vyváženost", "q155"),
        nw("155_investigativa_reportaze", "Investigativa", "q155"),
        nw("155_tradice_znacka", "Tradice, značka", "q155"),
        nw("155_preklady_zahranicni_obsah", "Překlady, zahraničí", "q155"),
        nw("155_nepodbizivost_odvaha", "Nepodbízivost", "q155"),
        nw("155_forma_bez_reklam_audio_epub", "Forma (bez reklam…)", "q155"),
     ]),

    ("q156", "Co vám na Respektu nejvíce vadí? (otevřená otázka)",
     "Celá taxonomie kódována z volného textu (＋). Multi-label.", "q156", [
        nw("156_nic_nevadi_spokojenost", "Nic nevadí", "q156"),
        nw("156_audio_ai_hlas_smisene", "Audio / AI hlas", "q156"),
        nw("156_kulturni_rubrika", "Kulturní rubrika", "q156"),
        nw("156_aplikace_technika_ux_bugy_vy", "Aplikace / technika", "q156"),
        nw("156_delka_clanku_moc_dlouhe", "Délka článků", "q156"),
        nw("156_jednostrannost_bias_aktivism", "Jednostrannost / bias", "q156"),
        nw("156_web_navigace", "Web / navigace", "q156"),
        nw("156_grafika_obalka_ilustrace", "Grafika / obálka", "q156"),
        nw("156_prehlednost_archiv_orientace", "Přehlednost / archiv", "q156"),
        nw("156_vyhledavani", "Vyhledávání", "q156"),
        nw("156_chybejici_oblasti", "Chybějící oblasti", "q156"),
        nw("156_doruceni_tisku", "Doručení tisku", "q156"),
        nw("156_ton_vice_pozitivniho", "Tón / víc pozitivního", "q156"),
        nw("156_cetnost_vice_obsahu_podcastu", "Četnost / víc obsahu", "q156"),
        nw("156_reklamy", "Reklamy", "q156"),
        nw("156_cena_paywall", "Cena / paywall", "q156"),
     ]),

    ("q153", "Poslech v aplikaci – proč jinou platformu? (otevřená otázka)",
     "Celá taxonomie kódována z volného textu (＋). Multi-label.", "q153", [
        nw("153_jina_platforma_spotify_apple", "Jiná platforma", "q153"),
        nw("153_nezkousel_neposloucha_v_app", "Nezkoušel v app", "q153"),
        nw("153_duvod_vse_na_jednom_miste_ag", "Vše na jednom místě", "q153"),
        nw("153_vytka_ovladani_prehlednost", "Ovládání / přehlednost", "q153"),
        nw("153_zvyklost_setrvacnost", "Zvyklost", "q153"),
        nw("153_technicky_problem_prehravani", "Technický problém", "q153"),
        nw("153_carplay_auto_bluetooth", "CarPlay / Auto", "q153"),
        nw("153_posloucha_jen_audioverze_cla", "Jen audioverze článků", "q153"),
        nw("153_duvod_sledovani_prehraneho", "Sledování přehraného", "q153"),
        nw("153_funguje_dobre_spokojen", "Funguje dobře", "q153"),
     ]),

    ("q154", "Jaké jiné zdroje sledujete? (otevřená otázka)",
     "Jmenované zdroje kódované z volného textu (＋). Multi-label.", "q154", [
        nw("154_src_denik_n", "Deník N", "q154"),
        nw("154_src_podcast_obecne_i_jmenovite", "Podcasty", "q154"),
        nw("154_src_irozhlas_cesky_rozhlas", "iRozhlas / ČRo", "q154"),
        nw("154_src_seznam_zpravy_seznam_cz", "Seznam Zprávy", "q154"),
        nw("154_src_ct_ct24", "ČT / ČT24", "q154"),
        nw("154_src_aktualne_cz", "Aktuálně.cz", "q154"),
        nw("154_src_hospodarske_noviny", "Hospodářské noviny", "q154"),
        nw("154_src_novinky_cz", "Novinky.cz", "q154"),
        nw("154_src_slovenske_sme_dennik_n_aktua", "Slovenské", "q154"),
        nw("154_src_dalsi_zahranicni_ft_wapo_pol", "Další zahraniční", "q154"),
        nw("154_src_bbc", "BBC", "q154"),
        nw("154_src_hlidaci_pes_investigace_neov", "Hlídací pes ad.", "q154"),
     ]),

]


# --- Doplňkové panely k dosud nezobrazeným otázkám (vloží se na vhodná místa) -
def _dist_items(sid):
    return [o(f"dist_{sid}_{i}", lab, "bool")
            for i, (_, lab) in enumerate(_dist_opts(sid))]


_EXTRA = [
    ("forma", ("digiaccess", "Využíváte také digitální přístup?",
               "Podíl osob, které možnost označily.", None, [
        o("Ano, používám web nebo aplikaci pro čtení", "Web/app pro čtení"),
        o("Ano, používám web nebo aplikaci pro poslouchání audia", "Web/app pro audio"),
        o("Přístup využívá někdo z rodiny/přátel", "Sdílí rodina/přátelé"),
        o("Nevyužívám", "Nevyužívám digitál"),
    ])),
    ("digital", ("ctedrive", "Četl/a jste dříve tištěný časopis?",
                 "Podíl z těch, kdo odpověděli.", None, _dist_items("ctedrive"))),
    ("digital", ("changeform", "Uvažujete o změně formy čtení Respektu?",
                 "Rozdělení z těch, kdo odpověděli. Součet ≈ 100 %.", None, _dist_items("changeform"))),
    ("podcasty", ("podplat", "Na jaké platformě podcasty posloucháte?",
                  "Rozdělení z těch, kdo poslouchají. Součet ≈ 100 %.", None, _dist_items("podplat"))),
    ("podcasty", ("podfreq", "Jak často oblíbený pořad posloucháte? (zapojení)",
                  "Rozdělení z těch, kdo mají oblíbený pořad. Součet ≈ 100 %.", None, _dist_items("podfreq"))),
    ("podcasty", ("podlisten", "Posloucháte podcasty Respektu?",
                  "Rozdělení z těch, kdo odpověděli. Součet ≈ 100 %.", None, _dist_items("podlisten"))),
    ("bariery", ("doruc", "Spokojenost s doručováním tištěného Respektu",
                 "Rozdělení 1–5 z odběratelů tisku, kdo odpověděli. Součet ≈ 100 %.", None, _dist_items("doruc"))),
    ("procplati", ("predpl", "Jak dlouho si předplácíte Respekt?",
                   "Rozdělení délky předplatného. Součet = 100 %.", None, _dist_items("predpl"))),
    ("bariery", ("zruseni", "Uvažoval/a jste v poslední době o zrušení předplatného?",
                 "Rozdělení odpovědí. Součet = 100 %.", None, _dist_items("zruseni"))),
    ("bariery", ("setrvani", "Jak pravděpodobné je, že zůstanete předplatitelem/kou?",
                 "Rozdělení odpovědí. Součet = 100 %.", None, _dist_items("setrvani"))),
]
for _after_key, _grp in _EXTRA:
    _idx = next(i for i, g in enumerate(GROUPS) if g[0] == _after_key)
    GROUPS.insert(_idx + 1, _grp)


# --- Typ vykreslení panelu + barvy kategorií ---------------------------------
# "bars"   = vícevýběr (dnešní podíly osob); "dist" = jeden naskládaný pruh
# (kategorie = metriky); "matrix" = víc řádků, každý jako naskládaný pruh.
def _dist_cats(sid):
    return list(zip([lab for _, lab in _dist_opts(sid)], DIST_PALETTE[sid]))


PANEL_RENDER = {
    "spok": {"render": "matrix", "cats": SPOK_CATS,
             "rows": matrix_rows("spok", SPOK_AREAS, SPOK_CATS)},
    "delkapref": {"render": "matrix", "cats": LEN_CATS,
                  "rows": matrix_rows("len", LEN_FMT, LEN_CATS)},
    "freqweb": {"render": "dist", "cats": list(zip(
        ["Každý den", "Několikrát za týden", "Každý týden",
         "Několikrát za měsíc", "Nepoužívám"], DIST_PALETTE["freq"]))},
    "freqapp": {"render": "dist", "cats": list(zip(
        ["Každý den", "Několikrát za týden", "Každý týden",
         "Několikrát za měsíc", "Nepoužívám"], DIST_PALETTE["freq"]))},
}
for _sid in ("ctedrive", "changeform", "podplat", "podfreq", "podlisten",
             "doruc", "predpl", "zruseni", "setrvani"):
    PANEL_RENDER[_sid] = {"render": "dist", "cats": _dist_cats(_sid)}

# Pořadí panelů = pořadí otázek v dotazníku (demografie zůstává jen jako filtr).
PANEL_ORDER = [
    "predpl", "styk", "konv", "hleda", "procplati", "forma", "ctedrive",
    "digital", "digiaccess", "homepage", "freqweb", "freqapp", "apprado",
    "appchybi", "changeform", "situace", "zajmy", "delkapref", "spok",
    "bariery", "doruc", "zruseni", "setrvani", "podlisten", "podcasty",
    "podfreq", "podplat", "q153", "q154", "q155", "q156",
]


# --- Latentní segmentace (PCA + k-means, kanálová, k=6) ----------------------
# Shluky vznikají ze VŠECH proměnných; dominuje distribuční kanál. Rozšíření
# o platformu/intenzitu poslechu (k=7) jsme zkoušeli, ale není robustní –
# tříští tištěné publikum na redundantní skupiny a „bridge" segment je artefakt
# jednoho běhu. Stabilní a interpretovatelná je tahle kanálová šestka.
# Pořadí názvů = pořadí tlačítek; přiřazení názvu deterministické (profil kanálu).
CLUSTER_NAMES = [
    "Tištění senioři", "Uživatelé aplikace", "Tištění s digitálním přesahem",
    "Mladá audio generace", "Weboví čtenáři", "Podcastoví posluchači",
]
_CL_META = {"ID", "Started on", "Last updated on", "Status", "Collector",
            "Language", "IP address", "Device", "{mwg_rnd}", "{url}", "{userid}"}


def _kmeans(Z, k, iters=120, restarts=12):
    best = None
    for _ in range(restarts):
        cen = [Z[np.random.randint(len(Z))]]
        for _ in range(k - 1):
            d = np.min([((Z - c) ** 2).sum(1) for c in cen], axis=0)
            cen.append(Z[np.random.choice(len(Z), p=d / d.sum())])
        C = np.array(cen)
        for _ in range(iters):
            lab = ((Z[:, None] - C[None]) ** 2).sum(2).argmin(1)
            nC = np.array([Z[lab == j].mean(0) if (lab == j).any() else C[j]
                           for j in range(k)])
            if np.allclose(nC, C):
                C = nC
                break
            C = nC
        inertia = ((Z - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, lab)
    return best[1]


def compute_channel_clusters(rows):
    """Vrátí (labels v pořadí CLUSTER_NAMES, velikosti). Reprodukovatelné (seed)."""
    np.random.seed(42)
    header = list(rows[0].keys())
    kinds = {}
    for c in header:
        if c in _CL_META:
            continue
        vals = set(r[c] for r in rows if r[c] != "")
        if vals and vals <= {"x", "X"}:
            kinds[c] = "bx"
        elif vals and vals <= {"True", "False"}:
            kinds[c] = "tf"
    for c in header:
        if c in _CL_META or c in kinds:
            continue
        if c.endswith("_ord") or c.endswith("_dir") or c.startswith("spok_"):
            kinds[c] = "ord"

    def _f(s):
        try:
            return float(s)
        except ValueError:
            return np.nan

    def num(c):
        k = kinds[c]
        if k == "bx":
            return np.array([1.0 if r[c] in ("x", "X") else 0.0 for r in rows])
        if k == "tf":
            return np.array([1.0 if r[c] == "True" else 0.0 for r in rows])
        x = np.array([_f(r[c]) for r in rows])
        if c.endswith("_dir"):
            x = (x + 1) / 2
        med = np.nanmedian(x)
        med = med if np.isfinite(med) else 0.0
        x = np.where(np.isnan(x), med, x)
        lo, hi = x.min(), x.max()
        return (x - lo) / (hi - lo) if hi > lo else x * 0.0

    meanv, mat = {}, []
    for c in kinds:
        v = num(c)
        meanv[c] = v
        if kinds[c] != "ord" and (v.mean() < 0.02 or v.mean() > 0.98):
            continue
        if v.std() == 0:
            continue
        mat.append(v)
    X = np.array(mat).T
    Xc = X - X.mean(0)
    U, S, _ = np.linalg.svd(Xc, full_matrices=False)
    Z = U[:, :20] * S[:20]
    raw = _kmeans(Z, 6)

    # deterministické přiřazení názvů podle profilu kanálu
    SIG = {"print": "Papírové vydání", "web": "Web Respekt.cz",
           "app": "Mobilní aplikace.1", "podc": "Podcastové aplikace",
           "audiocl": "Audiočlánky", "age": "vek_ord"}
    sig = {k: {j: meanv[col][raw == j].mean() for j in range(6)}
           for k, col in SIG.items()}
    rem, name_of = set(range(6)), {}

    def take(metric):
        j = max(rem, key=lambda j: sig[metric][j])
        rem.discard(j)
        return j
    name_of[take("podc")] = "Podcastoví posluchači"
    name_of[take("audiocl")] = "Mladá audio generace"
    name_of[take("app")] = "Uživatelé aplikace"
    name_of[take("web")] = "Weboví čtenáři"
    name_of[take("age")] = "Tištění senioři"
    name_of[rem.pop()] = "Tištění s digitálním přesahem"

    display = np.array([CLUSTER_NAMES.index(name_of[l]) for l in raw])
    sizes = [int((display == i).sum()) for i in range(len(CLUSTER_NAMES))]
    return display, sizes


def parse(kind, v):
    s = (v or "").strip()
    if kind == "check":
        return 1 if s in ("x", "X") else 0
    if kind == "bool":
        if s in ("True", "1", "1.0"):
            return 1
        if s in ("False", "0", "0.0"):
            return 0
        return None
    if kind == "spok":
        if s == "1.0":
            return 1
        if s == "0.0":
            return 0
        return None
    if kind == "thresh2":
        if s == "":
            return None
        try:
            return 1 if float(s) >= 2 else 0
        except ValueError:
            return None
    if kind == "dirpos":
        if s in ("1.0", "1"):
            return 1
        if s in ("-1.0", "-1"):
            return 0
        return None
    raise ValueError(kind)


# --- Presety „podle vztahu / zapojení" (filtrové, AND; cons = ordinální min/max) -
# Definice mezí labely z FILTERS["order"]; OR podmínky model neumí → churn jako proxy.
BEHAVIOR_PRESETS = [
    ("Ohrožení odchodem", {"zruseni": ("Spíše ano", "Ano")}),
    ("Loajální ambasadoři", {"delka": ("11–15 let", "21+ let"),
                             "setrvani": ("Velmi vysoká", "Velmi vysoká"),
                             "zruseni": ("Ne", "Ne")}),
    ("Noví předplatitelé (1. rok)", {"delka": ("< 1 rok", "< 1 rok")}),
    ("Digitální jádro (aktivní app)", {"frekv_app": ("Několikrát/týden", "Každý den")}),
    ("Pasivní digitál", {"frekv_app": ("Nepoužívá", "Několikrát/měsíc"),
                         "frekv_web": ("Nepoužívá", "Několikrát/měsíc")}),
    ("Mladí ohrožení", {"vek": ("18–24", "35–44"), "zruseni": ("Spíše ano", "Ano")}),
]


def _truthy_any(v):
    return (v or "").strip() in ("x", "X", "True", "1", "1.0")


# --- Kohortové heatmapy (věk × pohlaví) --------------------------------------
HEAT_INTERESTS = [
    ("Politické", "Politické"), ("Reportáže", "Reportáže"),
    ("Komentáře k aktuálnímu dění", "Komentáře"), ("Rozhovory", "Rozhovory"),
    ("Kulturní", "Kulturní"),
    ("Překlady zahraničních médií (The Atlantic, NYT, Die Zeit)", "Překlady zahraničí"),
    ("Ekonomické", "Ekonomické"), ("Podcasty/videa", "Podcasty / videa"),
    ("O rodině a vztazích", "Rodina a vztahy"),
]
HEAT_BARRIERS = [
    ("audio_umele_vc_text", "Audio zní uměle"),
    ("Problémy s uživatelským rozhraním (špatné ovládání aplikace, nepřehledný web)", "UX / ovládání"),
    ("cas_delka_vc_text", "Články moc dlouhé"),
    ("doruceni_vc_text", "Nepřišlo včas"),
    ("tech_problemy_vc_text", "Technické problémy"),
    ("bariera_vyhledavani", "Vyhledávání"),
    ("Rušivé reklamy", "Rušivé reklamy"),
]


def compute_heatmaps(rows, metric_grids=None):
    ya = ("18–24", "25–34", "35–44")
    oa = ("45–54", "55–64", "65 a více")
    vek = lambda r: (r.get("Jaký je váš věk?") or "")
    gen = lambda r: (r.get("Jaké je vaše pohlaví?") or "")
    cohdefs = [("mladší muž", ya, "Muž"), ("mladší žena", ya, "Žena"),
               ("starší muž", oa, "Muž"), ("starší žena", oa, "Žena")]
    cohrows = [[r for r in rows if vek(r) in ages and gen(r) == g]
               for _, ages, g in cohdefs]
    cohorts = [{"label": lab, "n": len(cohrows[i])}
               for i, (lab, _, _) in enumerate(cohdefs)]

    def pct(sub, fn):
        return round(100 * sum(1 for r in sub if fn(r)) / len(sub), 1) if sub else 0.0

    def grid(rowspec, fn):
        out = []
        for key, lab in rowspec:
            out.append({"label": lab, "vals": [pct(sub, lambda r: fn(r, key))
                                               for sub in cohrows]})
        return out

    def minmax(rs):
        flat = [v for r in rs for v in r["vals"]]
        return (min(flat), max(flat)) if flat else (0, 100)

    heatmaps = []
    # spokojenost (% spokojených mimo Nevím)
    srows = []
    for sid, src, lab in SPOK_AREAS:
        vals = []
        for sub in cohrows:
            sp = sum(1 for r in sub if (r.get(src) or "").strip() == "Spokojen/a")
            ne = sum(1 for r in sub if (r.get(src) or "").strip() == "Nespokojen/a")
            vals.append(round(100 * sp / (sp + ne), 1) if (sp + ne) else 0.0)
        srows.append({"label": lab, "vals": vals})
    vmn, vmx = minmax(srows)
    heatmaps.append({"title": "Spokojenost s atributy", "mode": "good_high",
                     "hint": "% spokojených z těch, kdo měli názor (mimo „Nevím“).",
                     "cohorts": cohorts, "rows": srows, "vmin": vmn, "vmax": vmx})
    # zájmy o obsah
    zr = grid(HEAT_INTERESTS, lambda r, k: _truthy_any(r.get(k)))
    vmn, vmx = minmax(zr)
    heatmaps.append({"title": "Zájem o okruhy obsahu", "mode": "seq",
                     "hint": "% osob v kohortě, které okruh označily.",
                     "cohorts": cohorts, "rows": zr, "vmin": 0, "vmax": vmx})
    # churn / setrvání
    cr = [
        {"label": "Uvažuje o zrušení", "vals": [pct(sub, lambda r:
            (r.get("uvazoval_zruseni_ord") or "").strip() in ("1.0", "2.0"))
            for sub in cohrows]},
        {"label": "Nízké setrvání (≤ Střední)", "vals": [pct(sub, lambda r:
            (r.get("pravdep_setrvani_ord") or "").strip() in ("1.0", "2.0", "3.0"))
            for sub in cohrows]},
    ]
    vmn, vmx = minmax(cr)
    heatmaps.append({"title": "Riziko odchodu", "mode": "bad_high",
                     "hint": "% osob v kohortě (vyšší = větší riziko).",
                     "cohorts": cohorts, "rows": cr, "vmin": 0, "vmax": vmx})
    # bariéry
    br = grid(HEAT_BARRIERS, lambda r, k: _truthy_any(r.get(k)))
    vmn, vmx = minmax(br)
    heatmaps.append({"title": "Bariéry při čtení/poslechu", "mode": "bad_high",
                     "hint": "% osob v kohortě, které na bariéru narazily.",
                     "cohorts": cohorts, "rows": br, "vmin": 0, "vmax": vmx})
    # heatmapy z metrik panelů (konv, q156) – předané z main()
    for spec in (metric_grids or []):
        gr = grid(spec["rowspec"], lambda r, k: _truthy_any(r.get(k)))
        _, vmx = minmax(gr)
        heatmaps.append({"title": spec["title"], "mode": spec.get("mode", "seq"),
                         "hint": spec["hint"], "cohorts": cohorts, "rows": gr,
                         "vmin": 0, "vmax": vmx})
    return heatmaps


def main():
    with open(SRC, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # shluky počítáme z PŮVODNÍCH sloupců (před injektáží odvozených)
    cl_labels, cl_sizes = compute_channel_clusters(rows)

    # rozbal frekvenční škálu na úrovně (True/False/'' = neodpověděl) –
    # syntetické sloupce, ať se ukáže celé rozdělení, ne jen „alespoň týdně"
    for r in rows:
        for ch, src in (("web", "frekvence_web_ord"), ("app", "frekvence_app_ord")):
            raw = (r.get(src) or "").strip()
            try:
                val = int(float(raw))
            except ValueError:
                val = None
            for lv, _ in FREQ_LEVELS:
                r[f"freq_{ch}_lvl{lv}"] = "" if val is None else (
                    "True" if val == lv else "False")
        # matice vnímání: 3 vzájemně výlučné kategorie na oblast (jmenovatel = kdo hodnotil)
        for sid, src, _ in SPOK_AREAS:
            v = (r.get(src) or "").strip()
            answered = v in SPOK_VALS
            for ci, cval in enumerate(SPOK_VALS):
                r[f"mx_spok_{sid}_{ci}"] = ("True" if v == cval else
                                            ("False" if answered else ""))
        # matice délky formátu: 3 kategorie na formát (jmenovatel vč. „Nevím")
        for fid, src, _ in LEN_FMT:
            v = (r.get(src) or "").strip()
            answered = v in LEN_VALS
            for ci, cval in enumerate(LEN_VALS):
                r[f"mx_len_{fid}_{ci}"] = ("True" if v == cval else
                                           ("False" if answered else ""))
        # jednovýběrové/škálové otázky → rozdělení (jmenovatel = kdo odpověděl)
        for sid, src, opts in DIST_SPECS:
            v = (r.get(src) or "").strip()
            answered = v in [val for val, _ in opts]
            for i, (val, _) in enumerate(opts):
                r[f"dist_{sid}_{i}"] = ("True" if v == val else
                                        ("False" if answered else ""))

    header = set(rows[0].keys())

    needed = [fl["col"] for fl in FILTERS] + list(RESPOND_COLS.values())
    needed += [c for c, _ in TEXTCOLS.values()]
    for *_, items in [(g[0], g[-1]) for g in GROUPS]:
        needed += [it[0] for it in items]
        needed += [it[5] for it in items if it[5]]
    missing = [c for c in needed if c not in header]
    if missing:
        raise SystemExit("Chybí sloupce v CSV:\n  " + "\n  ".join(missing))

    filters_out = [{"key": f["key"], "label": f["label"], "type": f["type"],
                    "categories": f["order"]} for f in FILTERS]

    def detect_cap(checkbox_cols):
        """Vrátí strop výběru (max možností), pokud otázka měla tvrdý limit.
        Heuristika: nikdo nepřekročil maxsel < počet možností a velká část
        respondujících sedí přesně na maxsel (pile-up = designovaný strop)."""
        if len(checkbox_cols) < 2:
            return None
        sel = [sum(1 for c in checkbox_cols
                   if (r.get(c) or "").strip() in ("x", "X")) for r in rows]
        picked = [s for s in sel if s > 0]
        if not picked:
            return None
        mx = max(picked)
        if mx >= len(checkbox_cols):
            return None  # nikdo neomezený / vybral vše → bez stropu
        share_at_max = sum(1 for s in picked if s == mx) / len(picked)
        return mx if share_at_max >= 0.2 else None

    metric_keys, metric_labels, kinds = [], {}, {}
    metric_origin, metric_textkey, enr_origcol = {}, {}, {}
    groups_out = []
    for gk, label, hint, respond, items in GROUPS:
        for col, lab, kind, origin, tk, origcol in items:
            metric_keys.append(col)
            metric_labels[col] = lab
            kinds[col] = kind
            metric_origin[col] = origin
            if tk:
                metric_textkey[col] = tk
            if origin == "enr":
                enr_origcol[col] = origcol
        # původní zaškrtávací sloupce otázky (orig + původní pole obohacených)
        checkbox_cols = [it[0] for it in items if it[3] == "orig" and it[2] == "check"]
        checkbox_cols += [it[5] for it in items if it[3] == "enr"]
        rspec = PANEL_RENDER.get(gk, {"render": "bars"})
        g_out = {
            "key": gk, "label": label, "hint": hint, "respond": respond,
            "allnew": all(it[3] == "new" for it in items),
            "cap": detect_cap(checkbox_cols) if rspec["render"] == "bars" else None,
            "metrics": [it[0] for it in items],
            "render": rspec["render"],
        }
        if rspec["render"] in ("dist", "matrix"):
            g_out["cats"] = [{"label": cl, "color": cc} for cl, cc in rspec["cats"]]
        if rspec["render"] == "matrix":
            g_out["rows"] = [{"label": rl, "cols": rc} for rl, rc in rspec["rows"]]
        groups_out.append(g_out)

    # pořadí panelů = pořadí otázek v dotazníku (PANEL_ORDER); zbytek na konec
    _ord = {k: i for i, k in enumerate(PANEL_ORDER)}
    groups_out.sort(key=lambda g: _ord.get(g["key"], len(_ord)))

    # přírůstky obohacených možností (enr): enriched − původní zaškrtávátko
    metric_increment = {}
    for col, origcol in enr_origcol.items():
        e = sum(1 for r in rows if (r.get(col) or "").strip() in ("True", "1", "1.0"))
        ob = sum(1 for r in rows if (r.get(origcol) or "").strip() in ("x", "X"))
        metric_increment[col] = e - ob

    # kanál (forma) – multibool (bitmaska kanálů) + latentní segment (kategoriální)
    filters_out.append({"key": "forma_ch", "label": "Kanál (forma)",
                        "type": "multibool",
                        "categories": [lab for _, lab in FORMA_CHANNELS]})
    filters_out.append({"key": "cluster", "label": "Latentní segment",
                        "type": "categorical", "categories": CLUSTER_NAMES})

    F = len(filters_out)               # demo + frekv/poslech/platforma + forma + cluster
    M = len(metric_keys)
    respond_keys = list(RESPOND_COLS.keys())
    respond_index = {k: F + M + i for i, k in enumerate(respond_keys)}

    out_rows, out_texts = [], []
    for i, r in enumerate(rows):
        row = []
        for fl in FILTERS:
            raw = (r.get(fl["col"]) or "").strip()
            if "map" in fl:
                raw = fl["map"].get(raw, "")
            row.append(fl["order"].index(raw) if raw in fl["order"] else None)
        mask = 0                        # forma jako bitmaska kanálů
        for bit, (col, _) in enumerate(FORMA_CHANNELS):
            if (r.get(col) or "").strip() in ("x", "X"):
                mask |= (1 << bit)
        row.append(mask)
        row.append(int(cl_labels[i]))  # cluster
        for k in metric_keys:
            row.append(parse(kinds[k], r.get(k)))
        for rk in respond_keys:
            row.append(1 if (r.get(RESPOND_COLS[rk]) or "").strip() else 0)
        out_rows.append(row)
        t = {}
        for tk, (col, _) in TEXTCOLS.items():
            v = (r.get(col) or "").strip()
            if v:
                t[tk] = v
        out_texts.append(t)

    # presety „podle vztahu/zapojení" → cons (ordinální min/max) + velikost
    fkey_idx = {f["key"]: j for j, f in enumerate(filters_out)}
    fkey_cats = {f["key"]: f["categories"] for f in filters_out}
    behavior_presets = []
    for name, spec in BEHAVIOR_PRESETS:
        cons = {k: {"min": fkey_cats[k].index(lo), "max": fkey_cats[k].index(hi)}
                for k, (lo, hi) in spec.items()}
        size = 0
        for row in out_rows:
            if all((row[fkey_idx[k]] is not None
                    and c["min"] <= row[fkey_idx[k]] <= c["max"])
                   for k, c in cons.items()):
                size += 1
        behavior_presets.append({"name": name, "size": size, "cons": cons})

    # heatmapy z metrik panelů: „co přimělo k předplatnému" + „co vám vadí"
    def _grid_from_group(gkey):
        g = next((x for x in groups_out if x["key"] == gkey), None)
        return [(k, metric_labels[k]) for k in g["metrics"]] if g else []
    metric_grids = [
        {"title": "Co přimělo k předplatnému", "mode": "seq",
         "hint": "% osob v kohortě, které důvod uvedly.",
         "rowspec": _grid_from_group("konv")},
        {"title": "Co vám na Respektu vadí", "mode": "seq",
         "hint": "% osob v kohortě, které téma zmínily (otevřená otázka).",
         "rowspec": _grid_from_group("q156")},
    ]
    heatmaps = compute_heatmaps(rows, metric_grids)

    data = {
        "n": len(out_rows),
        "filters": filters_out,
        "behavior_presets": behavior_presets,
        "heatmaps": heatmaps,
        "metric_groups": groups_out,
        "metric_keys": metric_keys,
        "metric_labels": metric_labels,
        "metric_origin": metric_origin,
        "metric_increment": metric_increment,
        "metric_textkey": metric_textkey,
        "text_labels": {tk: lab for tk, (_, lab) in TEXTCOLS.items()},
        "respond": respond_index,
        "clusters": [{"id": i, "name": CLUSTER_NAMES[i], "size": cl_sizes[i]}
                     for i in range(len(CLUSTER_NAMES))],
        "rows": out_rows,
        "texts": out_texts,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    kb = os.path.getsize(OUT) / 1024
    n_new = sum(1 for v in metric_origin.values() if v == "new")
    n_enr = sum(1 for v in metric_origin.values() if v == "enr")
    print(f"Zapsáno {OUT}")
    print(f"  {len(out_rows)} řádků · {F} filtrů · {M} metrik "
          f"({n_new}× ＋nové, {n_enr}× obohacené) · {len(groups_out)} panelů · {kb:.0f} kB")


if __name__ == "__main__":
    main()
