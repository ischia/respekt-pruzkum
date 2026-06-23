#!/usr/bin/env python3
"""Vstupy pro RICE audit z průzkumu předplatitelů.

Survey dodá Reach + Impact-signály + Confidence; Effort a finální RICE skóre
doplní produkt/eng tým. Princip: každý příznak je bool na úrovni osoby (OR),
nenadhodnocujeme. Cíle (váží Impact): akvizice/konverze, návyk/zapojení,
ARPU/retence — proto tři impact-signály: churn-lift, mladší-lift, zapojení.

Výstup: dashboard/RICE_vstupy.md (čitelné) + RICE_vstupy.csv (pro tým).
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "processed", "respekt_analyticky.csv")
OUTMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RICE_vstupy.md")
OUTCSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RICE_vstupy.csv")

# (název iniciativy, kategorie, [zdrojové sloupce], typ)
INIT = [
    ("Vyhledávání (v appce / archiv)", "App/UX",
     ["Vyhledávání", "156_vyhledavani", "bariera_vyhledavani"], "oprava"),
    ("Přehlednost / navigace UI", "App/UX",
     ["app_prehlednost", "156_prehlednost_archiv_orientace", "156_web_navigace",
      "Problémy s uživatelským rozhraním (špatné ovládání aplikace, nepřehledný web)"], "oprava"),
    ("Výraznější odlišení přečteného", "App/UX",
     ["Výraznější odlišení přečteného/poslouchaného", "app_odliseni_tisk"], "hodnota"),
    ("Výkon / stabilita appky", "App/UX",
     ["app_vykon", "tech_problemy_vc_text"], "oprava"),
    ("Přístupnost (velikost písma)", "App/UX",
     ["app_pristupnost"], "oprava"),
    ("Personalizace rubrik / notifikace", "App/UX",
     ["app_personalizace", "Častější notifikace (autoři, rubriky)"], "hodnota"),
    ("Otevírat články ze soc. sítí v appce", "App/UX",
     ["Možnost otevírat články Respektu ze sociálních sítí rovnou v aplikaci"], "hodnota"),
    ("Lepší offline režim", "App/UX",
     ["Lepší offline režim"], "hodnota"),
    ("Audio: kvalita / AI hlas", "Audio",
     ["156_audio_ai_hlas_smisene", "audio_umele_vc_text"], "oprava"),
    ("Audio: playlist / ovládání", "Audio",
     ["Možnost sestavit si vlastní audio playlist", "app_audio_ovladani"], "hodnota"),
    ("CarPlay / Android Auto", "Audio",
     ["Podpora pro Carplay/Android Auto", "153_carplay_auto_bluetooth"], "hodnota"),
    ("Souhrny / kratší verze článků", "Obsah",
     ["156_delka_clanku_moc_dlouhe", "cas_delka_vc_text"], "hodnota"),
    ("Kulturní rubrika", "Obsah",
     ["156_kulturni_rubrika"], "oprava"),
    ("Vnímaná jednostrannost / bias", "Obsah",
     ["156_jednostrannost_bias_aktivism"], "oprava"),
    ("Tón / víc pozitivního", "Obsah",
     ["156_ton_vice_pozitivniho"], "hodnota"),
    ("Chybějící oblasti (ekonomika, region…)", "Obsah",
     ["156_chybejici_oblasti"], "hodnota"),
    ("Grafika / obálka / ilustrace", "Obsah",
     ["156_grafika_obalka_ilustrace"], "hodnota"),
    ("Doručení tisku (kvalita/včasnost)", "Distribuce",
     ["doruceni_vc_text", "156_doruceni_tisku"], "oprava"),
    ("Cena / paywall (vč. audio-only)", "Pricing",
     ["156_cena_paywall"], "oprava"),
    ("Reklamy", "Pricing",
     ["156_reklamy"], "oprava"),
]


def truthy(v):
    return (v or "").strip() in ("x", "X", "True", "1", "1.0")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    N = len(rows)
    young = [r for r in rows if (r.get("Jaký je váš věk?") or "") in
             ("18–24", "25–34", "35–44")]
    churn = [r for r in rows if (r.get("uvazoval_zruseni_ord") or "").strip()
             in ("1.0", "2.0")]
    nY, nC = len(young), len(churn)

    def prev(rs, cols):
        return sum(1 for r in rs if any(truthy(r.get(c)) for c in cols))

    out = []
    for name, cat, cols, typ in INIT:
        miss = [c for c in cols if c not in rows[0]]
        if miss:
            raise SystemExit(f"Chybí sloupce: {miss}")
        n = prev(rows, cols)
        pct = 100 * n / N
        base = n / N
        cl = (prev(churn, cols) / nC) / base if base > 0 else 0   # churn-lift
        yl = (prev(young, cols) / nY) / base if base > 0 else 0   # mladší-lift
        conf = ("vysoká" if n >= 200 else "střední" if n >= 80 else "nízká")
        if len(cols) >= 3 and n >= 80:
            conf = "vysoká"
        out.append({"init": name, "cat": cat, "typ": typ, "n": n, "pct": pct,
                    "churn_lift": cl, "young_lift": yl, "conf": conf,
                    "src": len(cols)})

    out.sort(key=lambda x: -x["n"])

    # --- CSV pro tým (s prázdnými sloupci Effort / RICE) ---
    with open(OUTCSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Iniciativa", "Kategorie", "Typ", "Reach_n", "Reach_%",
                    "Churn_lift", "Mladsi_lift", "Confidence", "Zdroju",
                    "Effort_TBD", "Impact_TBD", "RICE_skore_TBD"])
        for o in out:
            w.writerow([o["init"], o["cat"], o["typ"], o["n"],
                        f"{o['pct']:.1f}", f"{o['churn_lift']:.2f}",
                        f"{o['young_lift']:.2f}", o["conf"], o["src"], "", "", ""])

    # --- Markdown ---
    L = []
    L.append("# RICE audit – vstupy z průzkumu předplatitelů\n")
    L.append(f"Vygenerováno z `respekt_analyticky.csv` · N = {N} · "
             f"mladší <44 = {nY} · uvažovali o zrušení = {nC}.\n")
    L.append("**Co survey dodává:** Reach (kolik osob chce/trápí, na úrovni osoby, "
             "OR napříč zdroji) + tři Impact-signály + Confidence. "
             "**Effort, finální Impact a RICE skóre doplní produkt/eng tým** "
             "(survey je neumí).\n")
    L.append("**Impact-signály (lift vůči celku, >1 = nadprůměr):**")
    L.append("- **Churn-lift** – jak moc téma řeší ti, kdo *uvažovali o zrušení* → retence/ARPU.")
    L.append("- **Mladší-lift** – jak moc ho řeší <44 → akvizice/konverze + návyk.")
    L.append("- **Typ** – *oprava* (odstranění bolesti) vs *hodnota* (nová přidaná hodnota).\n")
    L.append("| # | Iniciativa | Kat. | Reach (n / %) | Churn-lift | Mladší-lift | Conf. | Typ |")
    L.append("|---|---|---|---|---|---|---|---|")
    for i, o in enumerate(out, 1):
        cl = f"**{o['churn_lift']:.1f}×**" if o["churn_lift"] >= 1.2 else f"{o['churn_lift']:.1f}×"
        yl = f"**{o['young_lift']:.1f}×**" if o["young_lift"] >= 1.2 else f"{o['young_lift']:.1f}×"
        L.append(f"| {i} | {o['init']} | {o['cat']} | {o['n']} / {o['pct']:.0f} % "
                 f"| {cl} | {yl} | {o['conf']} | {o['typ']} |")
    L.append("\n## Jak to číst dál (RICE)\n")
    L.append("1. **Reach** = berte `Reach_n` (počet osob za rok, případně škálujte na celou bázi předplatitelů).")
    L.append("2. **Impact** = zvažte podle cíle: retence → váha na churn-lift; akvizice/návyk → na mladší-lift; "
             "u *oprav* spíš obrana churnu, u *hodnoty* spíš zapojení/akvizice.")
    L.append("3. **Confidence** = sloupec výše (velikost vzorku + shoda víc zdrojů). Pozn.: čísla z textu jsou přibližná.")
    L.append("4. **Effort** = doplní eng/produkt; pak `RICE = Reach × Impact × Confidence / Effort`.")
    L.append("\n**Pozn. k Reach:** některé položky měly v dotazníku strop 2 voleb → jsou to spíš "
             "*top-2 priority*, ne plný zájem; Reach je tedy konzervativní spodní odhad.\n")
    open(OUTMD, "w", encoding="utf-8").write("\n".join(L))
    print(f"Zapsáno {OUTMD} a {OUTCSV} – {len(out)} iniciativ.")
    for o in out[:6]:
        print(f"  {o['n']:4d} ({o['pct']:4.0f}%) churn×{o['churn_lift']:.1f} "
              f"mladší×{o['young_lift']:.1f} [{o['conf']}] {o['init']}")


if __name__ == "__main__":
    main()
