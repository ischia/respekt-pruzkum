# CLAUDE.md – rychlý kontext pro Claude Code

Kompletní dokumentace je v **README.md** (datový model, výstupy, taxonomie)
a **TODO.md** (co refaktorovat a proč).

## Co tento projekt dělá

Pipeline zpracovává export předplatitelského průzkumu Respektu (SurveyHero CSV).
Vstup: `data/raw/SurveyHeroResponses*.csv` (necommituje se).
Výstupy: `data/processed/` (necommituje se).
Spouštění: `python3 run_all.py` – vezme nejnovější raw CSV a zapíše všechny výstupy.

## Klíčové principy (porušení = chyba)

- **Nenadhodnocovat** – každý příznak je boolean na úrovni osoby (logické NEBO); odpověď se
  nezapočítá víckrát jen proto, že zaškrtla i napsala totéž.
- **Odečítat překryv** – u obohacení existujících checkboxů (`_vc_text`) se přičítá jen text,
  který *není* pokrytý zaškrtnutým polem.
- **Oddělit valenci** – chvála (Q155) a výtky (Q156) jsou samostatné taxonomie; témata se
  nekódují dohromady.
- **Poziční indexy sloupců** – skripty adresují sloupce indexem, ne názvem. Po novém exportu
  ověřit, zda se pořadí nezměnilo.
- **Čeština genericky neutrální** – výstupní popisy bez generického maskulina; původní znění
  odpovědí se zachovává doslovně.

## Struktura

```
src/prekodovani.py      # uzavřené otázky → 57 nových sloupců
src/koduj_otevrene.py   # 4 otevřené otázky → taxonomie + bool příznaky
run_all.py              # spouštěč obou skriptů
```

## Aktuální stav (export 2026-06-20)

- N = 2 139 dokončených odpovědí, 162 původních sloupců → 219 po obohacení
- Taxonomie: 11 témat v Q155, 14 v Q156, 10 v Q153, 10 zdrojových entit + 10 typů v Q154
- Prioritní TODO: rozdělit příliš široká témata v Q155 a Q156 (detail v TODO.md § 1a)
