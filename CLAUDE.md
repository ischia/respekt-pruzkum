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
src/prekodovani.py      # uzavřené otázky → 59 nových sloupců
src/koduj_otevrene.py   # 4 otevřené otázky → taxonomie + bool příznaky
src/spoj_dataset.py     # spojí obohaceno + kódování otevřených přes ID → respekt_analyticky.csv
run_all.py              # spouštěč všech tří skriptů
```

## Větvení – co patří kam

Každá větev má vlastní konverzaci. Na začátku konverzace vždy ověř větev: `git branch`.

| Větev | Účel | Klíčový výstup |
|---|---|---|
| `main` | Stabilní pipeline + dashboard; merge cíl ostatních větví | `dashboard/`, `src/` |
| `deck-zjisteni` | Klíčová zjištění pro management | `ZJISTENI.md` (delší deck + 1stránkové shrnutí) |
| `rice-audit` | Dopracování RICE tabulky, scenáře, komentáře | `dashboard/RICE_vstupy.md` + `.csv` |

### Instrukce pro novou konverzaci na dané větvi

**`deck-zjisteni`** – cíl: napsat `ZJISTENI.md` s 10 stěžejními zjištěními ve formátu:
headline → evidence (čísla z průzkumu) → „co s tím" (doporučení).
Výsledek = dvě části: delší analytický deck + 1stránkové exekutivní shrnutí.
Data z: `data/processed/respekt_analyticky.csv` (není v gitu) a `dashboard/data.json`.

**`rice-audit`** – cíl: doplnit/zpřesnit `dashboard/RICE_vstupy.md`.
Tabulka 20 iniciativ už existuje; zbývá: Effort + Impact od týmu, finální RICE skóre,
případně nové iniciativy nebo úprava váhy signálů.
Spustit přegenerování: `python3 dashboard/build_rice.py`.

## Aktuální stav (export 2026-06-20)

- N = 2 139 dokončených odpovědí, 162 původních sloupců → 221 po obohacení
- Spojený analytický dataset: `respekt_analyticky.csv` (2 139 × 294) = obohaceno + kódování otevřených otázek přes `ID` (základ pro křížové analýzy)
- Taxonomie: 13 témat v Q155, 16 v Q156, 10 v Q153, 10 zdrojů + 10 typů v Q154 – **retax všech 4 hotový**
- Další krok: křížové analýzy přes `respekt_analyticky.csv` pro předplatné/redakci/aplikaci (souhrny v `SOUHRNY.md`)
- `koduj_otevrene.py` umí téma jako dvojici `(include, exclude)` = MECE odečet užšího tématu od širšího koše
