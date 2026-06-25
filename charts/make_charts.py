#!/usr/bin/env python3
"""Generuje PNG grafy pro ZJISTENI.md / prezentaci z dashboard/data.json.
Styl: Respekt design systém (Adelle Sans, brand barvy, zaoblené sloupce a buňky).
Spuštění:  python3 charts/make_charts.py
"""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib import font_manager as fm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "dashboard", "data.json")))
OUT = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(ROOT, "prezentace", "fonts")

for fp in glob.glob(os.path.join(FONTDIR, "AdelleSans-*.otf")):
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
try:
    ADELLE = fm.FontProperties(fname=os.path.join(FONTDIR, "AdelleSans-Regular.otf")).get_name()
except Exception:
    ADELLE = "DejaVu Sans"
plt.rcParams.update({"font.family": ADELLE, "font.size": 12,
                     "text.color": "#181D27", "axes.labelcolor": "#494E56",
                     "xtick.color": "#868D98", "ytick.color": "#494E56"})

INK, GRAPHITE, GRAY = "#181D27", "#494E56", "#868D98"
GRAYBAR = "#C2C7CE"
RED = "#CE0B24"
GREEN, AMBER, BLUE, PURPLE = "#178D4D", "#F2A43A", "#1756AC", "#9747FF"
HAIRLINE = "#E0E4E9"
CMAP_GR = LinearSegmentedColormap.from_list("gr", ["#CE0B24", "#E8784E", "#F4D27A", "#7FBF6A", "#178D4D"])
CMAP_GR_R = CMAP_GR.reversed()
CMAP_BLUE = LinearSegmentedColormap.from_list("bl", ["#EAF1FB", "#9DBDE6", "#1756AC"])

F = {f["key"]: i for i, f in enumerate(DATA["filters"])}
MK = {k: i for i, k in enumerate(DATA["metric_keys"])}
OFFM = len(DATA["filters"])
rows = DATA["rows"]


def vi(r, k): return r[F[k]]
def mv(r, mk): return r[OFFM + MK[mk]] if mk in MK else None
def churn(r): return vi(r, "zruseni") in (1, 2)
def rate(pred):
    sub = [r for r in rows if pred(r)]
    return 100 * sum(1 for r in sub if churn(r)) / len(sub) if sub else 0
def _g(label):
    cats = DATA["filters"][F["pohlavi"]]["categories"]
    return cats.index(label) if label in cats else -1


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight",
                pad_inches=0.34, facecolor="white")
    plt.close(fig)
    print("  ", name)


def style_ax(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.spines["bottom"].set_color(HAIRLINE)


def title(ax, t):
    ax.set_title(t, fontsize=14.5, fontweight="bold", color=INK, loc="left", pad=14)


def round_rect(ax, x, y, w, h, color, corners="tl,tr,br,bl", R=8, z=2):
    pos = ax.get_position()
    fw, fh = ax.figure.get_size_inches(); dpi = ax.figure.dpi
    xr = ax.get_xlim(); yr = ax.get_ylim()
    ppx = (pos.width * fw * dpi) / (xr[1] - xr[0])
    ppy = (pos.height * fh * dpi) / (yr[1] - yr[0])
    rx = min(R / abs(ppx), abs(w) / 2); ry = min(R / abs(ppy), abs(h) / 2)
    c = set(s for s in corners.split(",") if s)
    x1, y1, x2, y2 = x, y, x + w, y + h
    P, C = [], []
    def mv(p): P.append(p); C.append(Path.MOVETO)
    def ln(p): P.append(p); C.append(Path.LINETO)
    def cv(ct, en): P.extend([ct, en]); C.extend([Path.CURVE3, Path.CURVE3])
    mv((x1 + (rx if "bl" in c else 0), y1))
    ln((x2 - (rx if "br" in c else 0), y1))
    if "br" in c: cv((x2, y1), (x2, y1 + ry))
    ln((x2, y2 - (ry if "tr" in c else 0)))
    if "tr" in c: cv((x2, y2), (x2 - rx, y2))
    ln((x1 + (rx if "tl" in c else 0), y2))
    if "tl" in c: cv((x1, y2), (x1, y2 - ry))
    ln((x1, y1 + (ry if "bl" in c else 0)))
    if "bl" in c: cv((x1, y1), (x1 + rx, y1))
    P.append(P[0]); C.append(Path.CLOSEPOLY)
    ax.add_patch(PathPatch(Path(P, C), fc=color, ec="none", clip_on=False, zorder=z))


# ---------- 1. churn podle tenury (svislé) ----------
def chart_churn_tenure():
    order = DATA["filters"][F["delka"]]["categories"]
    vals = [rate(lambda r, i=i: vi(r, "delka") == i) for i in range(len(order))]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.set_xlim(-0.6, len(order) - 0.4); ax.set_ylim(0, max(vals) + 3)
    th = 0.6
    for i, v in enumerate(vals):
        round_rect(ax, i - th / 2, 0, th, v, RED if v >= 15 else GRAYBAR, corners="tl,tr", R=9)
        ax.text(i, v + 0.5, f"{v:.0f} %", ha="center", fontsize=11, color=INK, fontweight="bold")
    ax.axhline(12.8, color=GRAPHITE, ls=(0, (4, 4)), lw=1)
    ax.text(len(order) - 0.5, 13.3, "průměr 12,8 %", ha="right", color=GRAPHITE, fontsize=9.5)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, fontsize=10.5)
    ax.set_ylabel("uvažuje o zrušení", fontsize=10.5)
    style_ax(ax)
    title(ax, "Churn podle délky předplatného — láme se v prvním roce")
    save(fig, "churn_tenure.png")


# ---------- 2. churn podle segmentu (vodorovné) ----------
def chart_churn_segments():
    items = [
        ("Pasivní digitál ¹", rate(lambda r: vi(r, "frekv_app") in (0, 1) and vi(r, "frekv_web") in (0, 1))),
        ("Mladší muži (18–44)", rate(lambda r: vi(r, "vek") in (1, 2, 3) and vi(r, "pohlavi") == _g("Muž"))),
        ("Noví (< 1 rok)", rate(lambda r: vi(r, "delka") == 0)),
        ("CELEK", 12.8),
        ("Tisk + digitál", rate(lambda r: mv(r, "cte_tisk_i_digital") == 1)),
        ("Digitální jádro (aktivní app)", rate(lambda r: vi(r, "frekv_app") in (3, 4))),
        ("Dlouholetí (16–20 let)", rate(lambda r: vi(r, "delka") == 4)),
    ]
    items.sort(key=lambda x: x[1])
    labels = [a for a, _ in items]; vals = [b for _, b in items]
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    ax.set_xlim(0, max(vals) + 3); ax.set_ylim(-0.6, len(labels) - 0.4)
    th = 0.58
    for i, (l, v) in enumerate(zip(labels, vals)):
        c = GRAPHITE if l == "CELEK" else (RED if v >= 12.8 else GREEN)
        round_rect(ax, 0, i - th / 2, v, th, c, corners="tr,br", R=9)
        ax.text(v + 0.3, i, f"{v:.0f} %", va="center", fontsize=11, color=INK, fontweight="bold")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("uvažuje o zrušení", fontsize=10.5)
    ax.annotate("¹ web i app max několikrát/měsíc", xy=(0, -0.55), xycoords="data",
                fontsize=8.5, color=GRAY, ha="left")
    style_ax(ax)
    title(ax, "Zapojení a kohorta předpovídají churn")
    save(fig, "churn_segments.png")


# ---------- 3. preference délky (stacked) ----------
def chart_delka_preference():
    fmts = [("texty", "Texty"), ("audioclanky", "Audioverze"), ("podcasty", "Podcasty"), ("videa", "Videa")]
    fig, ax = plt.subplots(figsize=(7.8, 3.3))
    ax.set_xlim(0, 100); ax.set_ylim(len(fmts) - 0.4, -0.6)
    th = 0.56
    cols = [GREEN, BLUE, GRAYBAR]
    for i, (key, _) in enumerate(fmts):
        cnt = [sum(1 for r in rows if mv(r, f"mx_len_{key}_{j}") == 1) for j in range(3)]
        tot = sum(cnt) or 1
        seg = [100 * x / tot for x in cnt]
        present = [k for k in range(3) if seg[k] > 0.6]
        xs = 0
        for k in range(3):
            if seg[k] > 0.6:
                cr = ""
                if k == present[0]: cr += "tl,bl"
                if k == present[-1]: cr += (",tr,br" if cr else "tr,br")
                round_rect(ax, xs, i - th / 2, seg[k], th, cols[k], corners=cr, R=7)
            xs += seg[k]
        ax.text(seg[0] / 2, i, f"{seg[0]:.0f} %", ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")
        if seg[1] > 8:
            ax.text(seg[0] + seg[1] / 2, i, f"{seg[1]:.0f} %", ha="center", va="center", color="white", fontsize=9.5)
    ax.set_yticks(range(len(fmts))); ax.set_yticklabels([l for _, l in fmts], fontsize=11)
    ax.set_xlabel("% z těch, kdo formát hodnotili", fontsize=10.5)
    style_ax(ax)
    leg = [mp.Patch(color=GREEN, label="Spíše delší"), mp.Patch(color=BLUE, label="Spíše kratší"),
           mp.Patch(color=GRAYBAR, label="Nevím")]
    ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.34), ncol=3, frameon=False, fontsize=9.5)
    title(ax, "Publikum chce spíše delší obsah (zvlášť texty)")
    save(fig, "delka_preference.png")


# ---------- vodorovné bary z metrik skupiny ----------
def group_items(gkey, top=None, drop=()):
    g = next(x for x in DATA["metric_groups"] if x["key"] == gkey)
    items = []
    for mk in g["metrics"]:
        lab = DATA["metric_labels"][mk]
        if any(s in lab for s in drop):
            continue
        items.append((lab, sum(1 for r in rows if mv(r, mk) == 1)))
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top] if top else items


def hbar(items, ttl, color, fname, figsize, xlabelmax=34):
    labels = [a if len(a) <= xlabelmax else a[:xlabelmax - 1] + "…" for a, _ in items][::-1]
    vals = [b for _, b in items][::-1]
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, max(vals) * 1.13); ax.set_ylim(-0.6, len(labels) - 0.4)
    th = 0.64
    for i, v in enumerate(vals):
        round_rect(ax, 0, i - th / 2, v, th, color, corners="tr,br", R=8)
        ax.text(v + max(vals) * 0.014, i, f"{v}", va="center", fontsize=10, color=INK)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("počet osob", fontsize=10.5)
    style_ax(ax)
    title(ax, ttl)
    save(fig, fname)


def chart_chvala():
    hbar(group_items("q155", top=10), "V čem je Respekt výjimečný (Q155, chvála)", GREEN, "chvala.png", (7.6, 4.3))
def chart_vytky():
    hbar(group_items("q156", drop=("Nic nevadí",)), "Co předplatitelům nejvíce vadí (Q156) — cena je až na dně", AMBER, "vytky.png", (7.6, 5.6))
def chart_zdroje():
    hbar(group_items("q154", top=10), "Jaké jiné zdroje sledují (Q154) — konkurence", BLUE, "zdroje.png", (7.6, 4.3))
def chart_digital():
    g = next(x for x in DATA["metric_groups"] if x["key"] == "digital")
    keep = ["Pohodlnost", "Audio", "Praktické", "Ekologické", "Cena"]
    items = []
    for mk in g["metrics"]:
        lab = DATA["metric_labels"][mk]
        if any(k in lab for k in keep):
            cnt = sum(1 for r in rows if mv(r, mk) == 1)
            display = lab.replace("Praktické důvody (bydlím v zahraničí, nestíhám číst fyzicky)",
                                  "Praktické (v zahraničí, nestíhám číst fyzicky)")
            items.append((display, cnt))
    items.sort(key=lambda x: x[1], reverse=True)
    hbar(items, "Co přimělo přejít na digitál", GRAPHITE, "digital_drivers.png", (7.8, 2.8))
def chart_app_prani():
    hbar(group_items("appchybi", top=9, drop=("nic nechybí", "Nic ")), "Co nejvíce chybí v aplikaci (přání)", PURPLE, "app_prani.png", (7.6, 4.1))
def chart_poslech_app():
    hbar(group_items("q153", top=8), "Proč ne aplikace pro poslech (Q153)", BLUE, "poslech_app.png", (7.4, 3.5))
def chart_vyhledavani():
    hbar([("Přání: vyhledávání v aplikaci", 229), ("Výtka „chybí vyhledávání“ (Q156)", 32), ("Nevyžádaně v poli bariéry", 13)],
         "Poptávka po vyhledávání se objevuje všude", BLUE, "vyhledavani.png", (7.4, 2.6))
def chart_tisk_ritual():
    hbar([
        ("Dříve četl/a tiskové vydání (Q)", 1330),
        ("Spokojenost s doručováním 4–5/5", 1086),
        ("Čte tisk i digitál souběžně", 94),
        ("Digitál jen jako doplněk (text)", 20),
        ("Aktivně preferuje tisk (text)", 15),
        ("Tištěné posílá rodině (text)", 12),
    ], "Tisk: tradice, rituál, kotva — podloženo uzavřenými i textem", GRAPHITE, "tisk_ritual.png", (7.8, 3.4))


def chart_churneri_overindex():
    g = next(x for x in DATA["metric_groups"] if x["key"] == "q156")
    pick = ["Jednostrannost", "Délka", "Kulturní", "Audio", "Tón", "Aplikace"]
    sel = []
    for want in pick:
        mk = next((k for k in g["metrics"] if want in DATA["metric_labels"][k]), None)
        if mk:
            sel.append((DATA["metric_labels"][mk], mk))
    ch = [r for r in rows if churn(r)]
    def pc(sub, mk): return 100 * sum(1 for r in sub if mv(r, mk) == 1) / len(sub)
    labs = [a.split(" /")[0].split(" (")[0] for a, _ in sel]
    cv = [pc(ch, mk) for _, mk in sel]; av = [pc(rows, mk) for _, mk in sel]
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    ax.set_xlim(0, max(cv) * 1.25); ax.set_ylim(len(labs) - 0.5, -0.5)
    th = 0.34
    for i in range(len(labs)):
        round_rect(ax, 0, i + 0.19 - th / 2, av[i], th, GRAYBAR, corners="tr,br", R=7)
        round_rect(ax, 0, i - 0.19 - th / 2, cv[i], th, RED, corners="tr,br", R=7)
        ax.text(cv[i] + 0.15, i - 0.19, f"{cv[i]:.0f} %", va="center", fontsize=9, color=INK)
        ax.text(av[i] + 0.15, i + 0.19, f"{av[i]:.0f} %", va="center", fontsize=9, color=GRAY)
    ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs, fontsize=11)
    ax.set_xlabel("% skupiny, které téma zmínilo", fontsize=10.5)
    ax.legend(handles=[mp.Patch(color=RED, label="uvažují o zrušení"), mp.Patch(color=GRAYBAR, label="celek")],
              loc="lower right", frameon=False, fontsize=9.5)
    style_ax(ax)
    title(ax, "Kdo odchází, vadí mu víc jednostrannost a tón")
    save(fig, "churneri_overindex.png")


# ---------- heatmapy: zaoblené buňky s mezerami ----------
def chart_heatmap(title_match, fname, figsize, top_n=None):
    h = next(x for x in DATA["heatmaps"] if x["title"] == title_match)
    cmap = {"good_high": CMAP_GR, "bad_high": CMAP_GR_R}.get(h["mode"], CMAP_BLUE)
    hrows = h["rows"][:top_n] if top_n else h["rows"]
    rlabs = [r["label"] for r in hrows]
    mat = [r["vals"] for r in hrows]
    clabs = h["cohorts"]
    nC, nR = len(clabs), len(rlabs)
    vmin, vmax = h["vmin"], h["vmax"]; rng = (vmax - vmin) or 1
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, nC); ax.set_ylim(0, nR); ax.invert_yaxis()
    gap = 0.11
    for i, row in enumerate(mat):
        for j, v in enumerate(row):
            col = cmap((v - vmin) / rng)
            lum = 0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2]
            tc = INK if lum > 0.62 else "white"
            ax.add_patch(FancyBboxPatch((j + gap / 2, i + gap / 2), 1 - gap, 1 - gap,
                         boxstyle="round,pad=0,rounding_size=0.12", mutation_aspect=1,
                         fc=col, ec="none"))
            ax.text(j + 0.5, i + 0.5, f"{v:.0f}" if (v >= 10 or v == 0) else f"{v:.1f}",
                    ha="center", va="center", color=tc, fontsize=11)
    ax.set_xticks([j + 0.5 for j in range(nC)])
    ax.set_xticklabels([f"{c['label']}\nn={c['n']:,}".replace(",", " ") for c in clabs], fontsize=10)
    ax.xaxis.set_ticks_position("top"); ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", pad=6)
    ax.set_yticks([i + 0.5 for i in range(nR)]); ax.set_yticklabels(rlabs, fontsize=10.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(h["title"], fontsize=14, fontweight="bold", color=INK, loc="left", pad=44)
    save(fig, fname)


def chart_churn_korelace():
    import pandas as pd, numpy as np
    df = pd.read_csv(os.path.join(ROOT, "data", "processed", "respekt_analyticky.csv"), dtype=str)
    N = len(df)
    churn_mask = df["uvazoval_zruseni_ord"].isin(["1.0", "2.0"])
    df_c = df[churn_mask]; df_nc = df[~churn_mask]

    def pct(sub, mask): return 100 * mask[sub.index].astype(float).mean()

    items = [
        ("Výběr témat — nespokojenost",    df["spok_vyber_temat"].astype(str) == "0.0"),
        ("Vyváženost — nespokojenost",      df["spok_vyvazenost"].astype(str) == "0.0"),
        ("Délka — články moc dlouhé",       df.iloc[:, 132].str.strip().str.lower() == "x"),
        ("Audio zní uměle (bariéra)",       df.iloc[:, 131].str.strip().str.lower() == "x"),
        ("Kvalita audia — nespokojenost",   df["spok_kvalita_nacteni_audioc"].astype(str) == "0.0"),
        ("UX / ovládání (bariéra)",         df.iloc[:, 130].str.strip().str.lower() == "x"),
        ("Přehlednost — nespokojenost",     df["spok_prehlednost"].astype(str) == "0.0"),
        ("Tisk nepřišel včas",              df.iloc[:, 135].str.strip().str.lower() == "x"),
        ("Jednostrannost / bias (výtka)",   df["156_jednostrannost_bias_aktivism"].astype(str).str.lower() == "true"),
    ]
    items_data = []
    for label, mask in items:
        pc = pct(df_c, mask); pnc = pct(df_nc, mask)
        items_data.append((label, pc, pnc, pc - pnc))
    items_data.sort(key=lambda x: x[3])

    labels = [a for a, *_ in items_data]
    cv = [b for _, b, *_ in items_data]
    av = [c for _, _, c, *_ in items_data]
    diff = [d for *_, d in items_data]

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.set_xlim(0, max(cv) * 1.28); ax.set_ylim(-0.6, len(labels) - 0.4)
    th = 0.33
    for i in range(len(labels)):
        round_rect(ax, 0, i + 0.19 - th / 2, av[i], th, GRAYBAR, corners="tr,br", R=7)
        round_rect(ax, 0, i - 0.19 - th / 2, cv[i], th, RED, corners="tr,br", R=7)
        ax.text(cv[i] + 0.2, i - 0.19, f"{cv[i]:.1f} %", va="center", fontsize=9, color=INK, fontweight="bold")
        ax.text(av[i] + 0.2, i + 0.19, f"{av[i]:.1f} %", va="center", fontsize=9, color=GRAY)
        ax.text(max(cv) * 1.22, i, f"+{diff[i]:.1f} pp", va="center", ha="right",
                fontsize=8.5, color=RED, fontweight="bold")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=10.5)
    ax.set_xlabel("% skupiny", fontsize=10.5)
    ax.legend(handles=[mp.Patch(color=RED, label="zvažuje zrušení (n=274)"),
                       mp.Patch(color=GRAYBAR, label="nezwažuje (n=1 865)")],
              loc="lower right", frameon=False, fontsize=9.5)
    style_ax(ax)
    title(ax, "Koreláty rizika odchodu — co předpovídá zrušení")
    save(fig, "churn_korelace.png")


def chart_reklama():
    items = [
        ("Spokojeni s množstvím reklamy", 1510),
        ("Bariéra: rušivé reklamy (checkbox)", 90),
        ("Nespokojenost (škála)", 72),
        ('Q156 výtka „reklamy“', 21),
        ("Vyskakovací / self-promo (text)", 5),
    ]
    labels = [a for a, _ in items][::-1]
    vals = [b for _, b in items][::-1]
    cols = [GREEN] + [AMBER] * 3 + [RED]
    cols = cols[::-1]
    fig, ax = plt.subplots(figsize=(7.6, 3.1))
    ax.set_xlim(0, max(vals) * 1.18); ax.set_ylim(-0.6, len(labels) - 0.4)
    th = 0.58
    for i, (v, c) in enumerate(zip(vals, cols)):
        round_rect(ax, 0, i - th / 2, v, th, c, corners="tr,br", R=8)
        ax.text(v + max(vals) * 0.013, i, f"{v}", va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=10.5)
    ax.set_xlabel("počet osob", fontsize=10.5)
    style_ax(ax)
    title(ax, "Reklama: menšinový, ale konkrétní problém předplatitelů")
    save(fig, "reklama.png")


def chart_chyby_textu():
    items = [
        ("Kvalita psaní / jazyk chválena (Q155)", 370),
        ("Audio chyby výslovnosti / AI hlas (Q156)", 102),
        ("Gramatika / překlepy v textu (Q156)", 4),
    ]
    labels = [a for a, _ in items][::-1]
    vals = [b for _, b in items][::-1]
    cols = [AMBER, AMBER, GREEN]
    fig, ax = plt.subplots(figsize=(7.6, 2.5))
    ax.set_xlim(0, max(vals) * 1.2); ax.set_ylim(-0.6, len(labels) - 0.4)
    th = 0.58
    for i, (v, c) in enumerate(zip(vals, cols)):
        round_rect(ax, 0, i - th / 2, v, th, c, corners="tr,br", R=8)
        ax.text(v + max(vals) * 0.013, i, f"{v}×", va="center", fontsize=11, color=INK, fontweight="bold")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=10.5)
    ax.set_xlabel("počet zmínek", fontsize=10.5)
    style_ax(ax)
    title(ax, "Chyby v textech: chválíme psaní, chybí korektura audia")
    save(fig, "chyby_textu.png")


if __name__ == "__main__":
    print("Generuji grafy do charts/:")
    chart_churn_tenure(); chart_churn_segments(); chart_delka_preference()
    chart_heatmap("Spokojenost s atributy", "heat_spokojenost.png", (7.0, 3.8))
    chart_heatmap("Zájem o okruhy obsahu", "heat_zajmy.png", (7.0, 4.4))
    chart_heatmap("Riziko odchodu", "heat_riziko.png", (7.0, 2.5))
    chart_heatmap("Co přimělo k předplatnému", "heat_konv.png", (7.0, 5.2))
    chart_heatmap("Co vám na Respektu vadí", "heat_vytky_kohort.png", (7.0, 5.8), top_n=10)
    chart_heatmap("Bariéry při čtení/poslechu", "heat_bariera.png", (7.0, 3.4))
    chart_chvala(); chart_vytky(); chart_zdroje(); chart_digital(); chart_app_prani()
    chart_poslech_app(); chart_vyhledavani(); chart_tisk_ritual(); chart_churneri_overindex()
    chart_churn_korelace(); chart_reklama(); chart_chyby_textu()
    print("Hotovo.")
