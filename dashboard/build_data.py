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

# --- Panely = skutečné otázky dotazníku --------------------------------------
GROUPS = [
    ("spok", "Jak vnímáte Respekt? (% spokojených)",
     "Podíl spokojených z těch, kdo položku hodnotili.", None, [
        o("spok_vyber_temat", "Výběr témat", "spok"),
        o("spok_mnozstvi_clanku", "Množství článků", "spok"),
        o("spok_delka_clanku", "Délka článků", "spok"),
        o("spok_vyvazenost", "Vyváženost", "spok"),
        o("spok_prehlednost", "Přehlednost", "spok"),
        o("spok_mnozstvi_reklamy", "Množství reklamy", "spok"),
        o("spok_kvalita_nacteni_audioc", "Kvalita načtení audia", "spok"),
     ]),

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

    ("frekvence", "Jak často navštěvujete web nebo aplikaci Respektu?",
     "Podíl těch, kdo kanál navštěvují alespoň týdně (z uživatelů kanálu).", None, [
        o("frekvence_web_ord", "Web – alespoň týdně", "thresh2"),
        o("frekvence_app_ord", "Aplikace – alespoň týdně", "thresh2"),
     ]),

    ("delkapref", "Která kombinace délky formátů vám vyhovuje?",
     "Podíl těch, kdo preferují delší formáty (z hodnotících daný formát).", None, [
        o("delka_texty_kratsi_zpravy_ko_dir", "Texty – delší formáty", "dirpos"),
        o("delka_audioclanky_kratsi_zpr_dir", "Audiočlánky – delší", "dirpos"),
        o("delka_podcasty_souhrny_a_glo_dir", "Podcasty – delší", "dirpos"),
        o("delka_videa_souhrny_a_glosy__dir", "Videa – delší", "dirpos"),
     ]),

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


def main():
    with open(SRC, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
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
        groups_out.append({
            "key": gk, "label": label, "hint": hint, "respond": respond,
            "allnew": all(it[3] == "new" for it in items),
            "cap": detect_cap(checkbox_cols),
            "metrics": [it[0] for it in items],
        })

    # přírůstky obohacených možností (enr): enriched − původní zaškrtávátko
    metric_increment = {}
    for col, origcol in enr_origcol.items():
        e = sum(1 for r in rows if (r.get(col) or "").strip() in ("True", "1", "1.0"))
        ob = sum(1 for r in rows if (r.get(origcol) or "").strip() in ("x", "X"))
        metric_increment[col] = e - ob

    F = len(FILTERS)
    M = len(metric_keys)
    respond_keys = list(RESPOND_COLS.keys())
    respond_index = {k: F + M + i for i, k in enumerate(respond_keys)}

    out_rows, out_texts = [], []
    for r in rows:
        row = []
        for fl in FILTERS:
            raw = (r.get(fl["col"]) or "").strip()
            if "map" in fl:
                raw = fl["map"].get(raw, "")
            row.append(fl["order"].index(raw) if raw in fl["order"] else None)
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

    data = {
        "n": len(out_rows),
        "filters": filters_out,
        "metric_groups": groups_out,
        "metric_keys": metric_keys,
        "metric_labels": metric_labels,
        "metric_origin": metric_origin,
        "metric_increment": metric_increment,
        "metric_textkey": metric_textkey,
        "text_labels": {tk: lab for tk, (_, lab) in TEXTCOLS.items()},
        "respond": respond_index,
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
