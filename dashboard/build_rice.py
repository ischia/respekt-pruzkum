#!/usr/bin/env python3
"""Vstupy pro RICE audit z průzkumu předplatitelů.

Survey dodá Reach + Impact-signály + Confidence; Effort a finální RICE skóre
doplní produkt/eng tým. Princip: každý příznak je bool na úrovni osoby (OR),
nenadhodnocujeme. Cíle (váží Impact): akvizice/konverze, návyk/zapojení,
ARPU/retence — proto impact-signály: churn-lift a mladší-lift.

Dva typy položek:
  • měřené – {"init", "cols": [...]} – Reach a lifty se počítají z dat;
  • textové – {"init", "text": True, "reach": int|None, "note"} – pocházejí
    z volného textu / doporučení, nemají vlastní položku v dotazníku, takže je
    survey neumí vyčíslit; Reach je ruční odhad (n zmínek) nebo „—", lifty se
    nepočítají, Confidence = nízká. V tabulce značeny †.

Výstup: dashboard/RICE_vstupy.md (čitelné) + RICE_vstupy.csv (pro tým).
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "processed", "respekt_analyticky.csv")
OUTMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RICE_vstupy.md")
OUTCSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RICE_vstupy.csv")
OUTHTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RICE_vstupy.html")
OUTJSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rice.json")

INIT = [
    {"init": "Vyhledávání (v appce / archiv)",
     "cols": ["Vyhledávání", "156_vyhledavani", "bariera_vyhledavani"]},
    {"init": "Přehlednost / navigace UI",
     "cols": ["app_prehlednost", "156_prehlednost_archiv_orientace", "156_web_navigace",
              "Problémy s uživatelským rozhraním (špatné ovládání aplikace, nepřehledný web)"]},
    {"init": "Výraznější odlišení přečteného",
     "cols": ["Výraznější odlišení přečteného/poslouchaného", "app_odliseni_tisk"]},
    {"init": "Výkon / stabilita appky",
     "cols": ["app_vykon", "tech_problemy_vc_text"]},
    {"init": "Přístupnost (velikost písma)",
     "cols": ["app_pristupnost"]},
    {"init": "Notifikace – automatizace, podcasty/témata/autoři",
     "cols": ["app_personalizace", "Častější notifikace (autoři, rubriky)"]},
    {"init": "Deeplinky (otevírat články z odkazů v appce)",
     "cols": ["Možnost otevírat články Respektu ze sociálních sítí rovnou v aplikaci"]},
    {"init": "Lepší offline režim",
     "cols": ["Lepší offline režim"]},
    {"init": "Audio: playlist / ovládání",
     "cols": ["Možnost sestavit si vlastní audio playlist", "app_audio_ovladani"]},
    {"init": "CarPlay / Android Auto",
     "cols": ["Podpora pro Carplay/Android Auto", "153_carplay_auto_bluetooth"]},
    {"init": "Souhrny / kratší verze článků",
     "cols": ["156_delka_clanku_moc_dlouhe", "cas_delka_vc_text"]},
    {"init": "Audiočlánky ladění (kvalita / AI hlas)",
     "cols": ["156_audio_ai_hlas_smisene", "audio_umele_vc_text"]},
    {"init": "Vypnout self-promo bannery pro přihlášené",
     "cols": ["156_reklamy"],
     "note": "měřeno přes výtku „reklamy“ (Q156); ~5 zmínek explicitně self-promo, low-effort"},
    # --- textové položky (z volného textu / doporučení; survey nevyčísluje) ---
    {"init": "Příznak „vyjde v tištěném vydání“", "text": True, "reach": 5,
     "note": "5 zmínek v textu (Q153) – aby čtenáři článek nečetli digitálně dřív"},
    {"init": "Kopírování textu", "text": True, "reach": None,
     "note": "z volného textu (Q156), počet zmínek nevyčíslen"},
    {"init": "Landing page pro Instagram", "text": True, "reach": None,
     "note": "doporučení (slide 12 decku), survey nevyčísluje"},
    {"init": "Připomínací newslettery (zvýšení frekvence návštěv)", "text": True, "reach": None,
     "note": "doporučení z chování segmentů (reaktivace pasivních), survey nevyčísluje"},
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
    for it in INIT:
        if it.get("text"):
            out.append({"init": it["init"], "text": True, "n": it.get("reach"),
                        "pct": None, "churn_lift": None, "young_lift": None,
                        "conf": "nízká", "src": 0, "note": it.get("note", "")})
            continue
        cols = it["cols"]
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
        out.append({"init": it["init"], "text": False, "n": n, "pct": pct,
                    "churn_lift": cl, "young_lift": yl, "conf": conf,
                    "src": len(cols), "note": it.get("note", "")})

    # měřené (dle Reach) první, textové na konci (dle ručního Reach)
    out.sort(key=lambda x: (x["text"], -(x["n"] or 0)))

    # --- CSV pro tým (s prázdnými sloupci Effort / RICE) ---
    with open(OUTCSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Iniciativa", "Reach_n", "Reach_%",
                    "Churn_lift", "Mladsi_lift", "Confidence", "Zdroju",
                    "Effort_TBD", "Impact_TBD", "RICE_skore_TBD", "Pozn"])
        for o in out:
            if o["text"]:
                w.writerow([o["init"], o["n"] if o["n"] is not None else "",
                            "", "", "", o["conf"], "", "", "", "", o["note"]])
            else:
                w.writerow([o["init"], o["n"], f"{o['pct']:.1f}",
                            f"{o['churn_lift']:.2f}", f"{o['young_lift']:.2f}",
                            o["conf"], o["src"], "", "", "", ""])

    # --- Markdown ---
    L = []
    L.append("# RICE audit – vstupy z průzkumu předplatitelů\n")
    L.append(f"Vygenerováno z `respekt_analyticky.csv` · N = {N} · "
             f"mladší <44 = {nY} · uvažovali o zrušení = {nC}.\n")
    L.append("**Co survey dodává:** Reach (kolik osob chce/trápí, na úrovni osoby, "
             "OR napříč zdroji) + dva Impact-signály + Confidence. "
             "**Effort, finální Impact a RICE skóre doplní produkt/eng tým** "
             "(survey je neumí).\n")
    L.append("**Impact-signály (lift vůči celku, >1 = nadprůměr):**")
    L.append("- **Churn-lift** – jak moc téma řeší ti, kdo *uvažovali o zrušení* → retence/ARPU.")
    L.append("- **Mladší-lift** – jak moc ho řeší <44 → akvizice/konverze + návyk.\n")
    def info(note):
        """Poznámku schová za hover „ⓘ" (link s title); prázdné = nic."""
        if not note:
            return ""
        return f' [ⓘ](# "{note.strip()}")'

    L.append("| # | Iniciativa | Reach (n / %) | Churn-lift | Mladší-lift | Conf. |")
    L.append("|---|---|---|---|---|---|")
    for i, o in enumerate(out, 1):
        if o["text"]:
            name = o["init"] + " †"
            reach = f"~{o['n']}" if o["n"] is not None else "—"
            cl = yl = "—"
        else:
            name = o["init"]
            reach = f"{o['n']} / {o['pct']:.0f} %"
            cl = f"**{o['churn_lift']:.1f}×**" if o["churn_lift"] >= 1.2 else f"{o['churn_lift']:.1f}×"
            yl = f"**{o['young_lift']:.1f}×**" if o["young_lift"] >= 1.2 else f"{o['young_lift']:.1f}×"
        L.append(f"| {i} | {name}{info(o['note'])} | {reach} | {cl} | {yl} | {o['conf']} |")
    L.append("\n**†** = z volného textu / doporučení, survey nevyčísluje "
             "(*Reach* = ruční odhad počtu zmínek, nebo „—“). "
             "**ⓘ** = detail po najetí myší. Reach i Effort doplní tým.\n")
    L.append("## Jak to číst dál (RICE)\n")
    L.append("1. **Reach** = berte `Reach_n` (počet osob za rok, případně škálujte na celou bázi předplatitelů).")
    L.append("2. **Impact** = zvažte podle cíle: retence → váha na churn-lift; akvizice/návyk → na mladší-lift.")
    L.append("3. **Confidence** = sloupec výše (velikost vzorku + shoda víc zdrojů). Pozn.: čísla z textu jsou přibližná.")
    L.append("4. **Effort** = doplní eng/produkt; pak `RICE = Reach × Impact × Confidence / Effort`.")
    L.append("\n**Pozn. k Reach:** některé položky měly v dotazníku strop 2 voleb → jsou to spíš "
             "*top-2 priority*, ne plný zájem; Reach je tedy konzervativní spodní odhad.\n")
    open(OUTMD, "w", encoding="utf-8").write("\n".join(L))

    # --- Samostatná brandovaná HTML stránka (pro localhost, mimo deck) ---
    def lift_cell(v):
        if v is None:
            return '<td class="num">—</td>'
        s = f"{v:.1f}×".replace(".", ",")
        cls = "num lift-hi" if v >= 1.2 else "num"
        return f'<td class="{cls}">{s}</td>'

    pill_cls = {"vysoká": "hi", "střední": "mid", "nízká": "lo"}

    def info_html(note):
        if not note:
            return ""
        safe = (note.replace("&", "&amp;").replace('"', "&quot;")
                .replace("<", "&lt;").replace(">", "&gt;"))
        return f'<abbr title="{safe}">ⓘ</abbr>'

    def rows_html(items):
        r = []
        for o in items:
            if o["text"]:
                reach = f'~{o["n"]}' if o["n"] is not None else "—"
                lifts = '<td class="num">—</td><td class="num">—</td>'
                name = f'{o["init"]} <span class="dagger">†</span>'
            else:
                reach = f'{o["n"]} / {o["pct"]:.0f} %'
                lifts = lift_cell(o["churn_lift"]) + lift_cell(o["young_lift"])
                name = o["init"]
            r.append(f'<tr><td class="init">{name}{info_html(o["note"])}</td>'
                     f'<td class="num">{reach}</td>{lifts}'
                     f'<td class="conf"><span class="pill pill-{pill_cls[o["conf"]]}">'
                     f'{o["conf"]}</span></td></tr>')
        return "\n".join(r)

    measured = [o for o in out if not o["text"]]
    textove = [o for o in out if o["text"]]
    head = ('<thead><tr><th>Iniciativa</th><th class="num">{}</th>'
            '<th class="num">Churn-lift</th><th class="num">Mladší-lift</th>'
            '<th class="num">Conf.</th></tr></thead>')
    html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RICE audit — vstupy z průzkumu</title>
<style>
@font-face{{font-family:'Adelle Sans';src:url('/prezentace/fonts/AdelleSans-Regular.otf') format('opentype');font-weight:400;}}
@font-face{{font-family:'Adelle Sans';src:url('/prezentace/fonts/AdelleSans-Bold.otf') format('opentype');font-weight:700;}}
@font-face{{font-family:'Adelle Sans';src:url('/prezentace/fonts/AdelleSans-Extrabold.otf') format('opentype');font-weight:800;}}
@font-face{{font-family:'Adelle';src:url('/prezentace/fonts/Adelle-Regular.otf') format('opentype');font-weight:400;}}
:root{{--paper:#fff;--ink:#181D27;--graphite:#494E56;--gray:#868D98;--hairline:#E0E4E9;
--surface:#ECEFF2;--red:#CE0B24;--amber:#F2A43A;--wash-amber:#FBEFD6;--radius:6px;
--sans:'Adelle Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;--serif:'Adelle',Georgia,serif;}}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--surface);color:var(--ink);font-family:var(--sans);line-height:1.45;padding:48px 24px;}}
.wrap{{max-width:980px;margin:0 auto;}}
h1{{font-weight:800;font-size:30px;letter-spacing:-.015em;margin:0 0 6px;}}
.meta{{color:var(--gray);font-size:14px;margin:0 0 22px;}}
.meta code{{color:var(--graphite);}}
.lead{{font-family:var(--serif);font-size:17px;color:var(--graphite);margin:0 0 10px;}}
.lead strong{{color:var(--ink);}}
.legend{{font-size:14px;color:var(--graphite);margin:0 0 8px;padding-left:18px;}}
.legend li{{margin:2px 0;}}
h2{{font-weight:800;font-size:18px;margin:30px 0 10px;padding-bottom:8px;border-bottom:1.5px solid #CFD4DA;}}
table{{width:100%;border-collapse:collapse;background:var(--paper);border-radius:8px;overflow:hidden;
box-shadow:0 6px 20px rgba(24,29,39,.07);font-size:15px;}}
thead th{{background:var(--ink);color:#fff;font-weight:700;font-size:11px;text-transform:uppercase;
letter-spacing:.04em;padding:10px 12px;text-align:left;}}
thead th.num{{text-align:center;}}
tbody td{{padding:8px 12px;border-bottom:1px solid var(--hairline);color:var(--graphite);}}
tbody tr:last-child td{{border-bottom:none;}}
td.init{{color:var(--ink);font-weight:600;}}
td.num{{text-align:center;white-space:nowrap;}}
td.conf{{text-align:center;}}
.lift-hi{{color:var(--red);font-weight:700;}}
abbr[title]{{color:var(--red);cursor:help;text-decoration:none;font-weight:800;margin-left:4px;}}
.dagger{{color:var(--red);font-weight:800;}}
.pill{{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:999px;}}
.pill-hi{{background:var(--ink);color:#fff;}}
.pill-mid{{background:#DFE3E8;color:var(--graphite);}}
.pill-lo{{background:#EEF1F4;color:var(--gray);}}
.note{{font-family:var(--serif);font-size:14px;color:var(--graphite);margin:10px 0 0;}}
.howto{{background:var(--wash-amber);border-radius:var(--radius);padding:16px 20px;margin:26px 0 0;}}
.howto::before{{content:"JAK TO ČÍST DÁL (RICE)";display:block;color:var(--red);font-weight:700;
font-size:12px;letter-spacing:.06em;margin-bottom:8px;}}
.howto ol{{margin:0;padding-left:20px;font-family:var(--serif);font-size:15px;color:var(--ink);}}
.howto li{{margin:4px 0;}}
.howto code{{font-size:13px;}}
.foot{{color:var(--gray);font-size:12px;margin:30px 0 0;}}
</style>
</head>
<body>
<div class="wrap">
<h1>RICE audit — vstupy z průzkumu předplatitelů</h1>
<p class="meta">Z <code>respekt_analyticky.csv</code> · N = {N} · mladší &lt;44 = {nY} · uvažovali o zrušení = {nC} · generuje <code>build_rice.py</code></p>
<p class="lead"><strong>Co survey dodává:</strong> Reach (osoby, OR napříč zdroji) + dva Impact-signály + Confidence. <strong>Effort, finální Impact a RICE skóre doplní produkt/eng tým.</strong></p>
<ul class="legend">
<li><strong>Churn-lift</strong> – jak moc téma řeší ti, kdo uvažovali o zrušení → retence/ARPU (&gt;1× = nadprůměr).</li>
<li><strong>Mladší-lift</strong> – jak moc ho řeší &lt;44 → akvizice/konverze + návyk.</li>
</ul>

<h2>Měřené produktové iniciativy</h2>
<table>
{head.format("Reach (n / %)")}
<tbody>
{rows_html(measured)}
</tbody>
</table>
<p class="note">Reach = osoby (logické NEBO napříč zdroji). Lift &gt;1× = nadprůměr vůči celku.</p>

<h2>Z volného textu a doporučení <span class="dagger">†</span></h2>
<table>
{head.format("Reach")}
<tbody>
{rows_html(textove)}
</tbody>
</table>
<p class="note"><span class="dagger">†</span> Položky z volného textu / doporučení — nemají vlastní otázku v dotazníku, survey je nevyčísluje; <em>Reach</em> = ruční odhad počtu zmínek nebo „—". Najetím na <abbr title="zdroj odhadu">ⓘ</abbr> se zobrazí zdroj. Reach i Effort doplní tým.</p>

<div class="howto">
<ol>
<li><strong>Reach</strong> = počet osob za rok (případně škálovat na celou bázi předplatitelů).</li>
<li><strong>Impact</strong> = dle cíle: retence → churn-lift; akvizice/návyk → mladší-lift.</li>
<li><strong>Confidence</strong> = velikost vzorku + shoda víc zdrojů; čísla z textu jsou přibližná.</li>
<li><strong>Effort</strong> = doplní tým; pak <code>RICE = Reach × Impact × Confidence / Effort</code>.</li>
</ol>
</div>
<p class="foot">Pozn.: část baterií měla strop 2 voleb → Reach je konzervativní spodní odhad (top-2 priority). Stránka se generuje z dat (<code>build_rice.py</code>), needituj ji ručně.</p>
</div>
</body>
</html>
"""
    open(OUTHTML, "w", encoding="utf-8").write(html)

    # --- rice.json pro RICE tab v dashboardu (jen agregáty, bez volného textu) ---
    payload = {
        "N": N, "nY": nY, "nC": nC,
        "items": [{"init": o["init"], "text": o["text"], "n": o["n"],
                   "pct": round(o["pct"], 1) if o["pct"] is not None else None,
                   "churn_lift": round(o["churn_lift"], 2) if o["churn_lift"] is not None else None,
                   "young_lift": round(o["young_lift"], 2) if o["young_lift"] is not None else None,
                   "conf": o["conf"], "note": o["note"]} for o in out],
    }
    with open(OUTJSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print(f"Zapsáno {OUTMD}, {OUTCSV}, {OUTHTML} a {OUTJSON} – {len(out)} iniciativ.")
    for o in out:
        if o["text"]:
            print(f"     {('~'+str(o['n'])) if o['n'] is not None else '—':>5}  "
                  f"[{o['conf']}] † {o['init']}")
        else:
            print(f"  {o['n']:4d} ({o['pct']:4.0f}%) churn×{o['churn_lift']:.1f} "
                  f"mladší×{o['young_lift']:.1f} [{o['conf']}] {o['init']}")


if __name__ == "__main__":
    main()
