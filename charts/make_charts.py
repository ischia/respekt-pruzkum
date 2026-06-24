#!/usr/bin/env python3
"""Generuje PNG grafy pro ZJISTENI.md z dashboard/data.json.
Spuštění:  python3 charts/make_charts.py  → zapíše charts/*.png
Heatmapy bere hotové z data.json["heatmaps"]; churn/délku dopočítá z řádků.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "dashboard", "data.json")))
OUT = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.edgecolor": "#cccccc", "svg.fonttype": "none"})
RED, GRAY, GREEN, BLUE = "#c0392b", "#b9b9b6", "#1f8a4c", "#2f6db0"

F = {f["key"]: i for i, f in enumerate(DATA["filters"])}
MK = {k: i for i, k in enumerate(DATA["metric_keys"])}
OFFM = len(DATA["filters"])
rows = DATA["rows"]


def vi(r, k):
    return r[F[k]]


def mv(r, mk):
    return r[OFFM + MK[mk]] if mk in MK else None


def churn(r):
    return vi(r, "zruseni") in (1, 2)


def rate(pred):
    sub = [r for r in rows if pred(r)]
    return 100 * sum(1 for r in sub if churn(r)) / len(sub) if sub else 0


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  ", name)


# ---------- 1. churn podle délky předplatného ----------
def chart_churn_tenure():
    order = DATA["filters"][F["delka"]]["categories"]
    vals = [rate(lambda r, i=i: vi(r, "delka") == i) for i in range(len(order))]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    colors = [RED if v >= 15 else GRAY for v in vals]
    bars = ax.bar(order, vals, color=colors, width=0.66)
    ax.axhline(12.8, color="#888", ls="--", lw=1)
    ax.text(len(order) - 0.5, 13.4, "průměr 12,8 %", ha="right", color="#666", fontsize=9.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.0f} %", ha="center", fontsize=10)
    ax.set_ylim(0, max(vals) + 3)
    ax.set_ylabel("uvažuje o zrušení")
    ax.set_title("Churn podle délky předplatného — láme se v prvním roce", fontsize=12.5, loc="left", pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "churn_tenure.png")


# ---------- 2. churn podle segmentu (srovnání) ----------
def chart_churn_segments():
    items = [
        ("Pasivní digitál", rate(lambda r: vi(r, "frekv_app") in (0, 1) and vi(r, "frekv_web") in (0, 1))),
        ("Mladší muži (18–44)", rate(lambda r: vi(r, "vek") in (1, 2, 3) and vi(r, "pohlavi") == _g("Muž"))),
        ("Noví (< 1 rok)", rate(lambda r: vi(r, "delka") == 0)),
        ("CELEK", 12.8),
        ("Digitální jádro (aktivní app)", rate(lambda r: vi(r, "frekv_app") in (3, 4))),
        ("Dlouholetí (16–20 let)", rate(lambda r: vi(r, "delka") == 4)),
    ]
    items.sort(key=lambda x: x[1])
    labels = [a for a, _ in items]
    vals = [b for _, b in items]
    colors = ["#7a7a7a" if l == "CELEK" else (RED if v >= 12.8 else GREEN) for l, v in zip(labels, vals)]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    bars = ax.barh(labels, vals, color=colors, height=0.64)
    for b, v in zip(bars, vals):
        ax.text(v + 0.3, b.get_y() + b.get_height() / 2, f"{v:.0f} %", va="center", fontsize=10)
    ax.set_xlim(0, max(vals) + 3)
    ax.set_xlabel("uvažuje o zrušení")
    ax.set_title("Zapojení a kohorta předpovídají churn", fontsize=12.5, loc="left", pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "churn_segments.png")


def _g(label):
    cats = DATA["filters"][F["pohlavi"]]["categories"]
    return cats.index(label) if label in cats else -1


# ---------- 3. preference délky obsahu ----------
def chart_delka_preference():
    fmts = [("texty", "Texty"), ("audioclanky", "Audioverze"), ("podcasty", "Podcasty"), ("videa", "Videa")]
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    yp = range(len(fmts))
    longer, shorter, dunno = [], [], []
    for key, _ in fmts:
        c = [sum(1 for r in rows if mv(r, f"mx_len_{key}_{i}") == 1) for i in range(3)]
        tot = sum(c) or 1
        longer.append(100 * c[0] / tot)
        shorter.append(100 * c[1] / tot)
        dunno.append(100 * c[2] / tot)
    ax.barh(yp, longer, color=GREEN, height=0.6, label="Spíše delší")
    ax.barh(yp, shorter, left=longer, color=BLUE, height=0.6, label="Spíše kratší")
    ax.barh(yp, dunno, left=[a + b for a, b in zip(longer, shorter)], color=GRAY, height=0.6, label="Nevím")
    for i, (lo, sh) in enumerate(zip(longer, shorter)):
        ax.text(lo / 2, i, f"{lo:.0f} %", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        if sh > 7:
            ax.text(lo + sh / 2, i, f"{sh:.0f} %", ha="center", va="center", color="white", fontsize=9)
    ax.set_yticks(list(yp))
    ax.set_yticklabels([lab for _, lab in fmts])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("% z těch, kdo formát hodnotili")
    ax.set_title("Publikum chce spíše delší obsah (zvlášť texty)", fontsize=12.5, loc="left", pad=10)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3, frameon=False, fontsize=9.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    save(fig, "delka_preference.png")


# ---------- 4. kohortové heatmapy (z data.json) ----------
RdYlGn = plt.get_cmap("RdYlGn")
RdYlGn_r = plt.get_cmap("RdYlGn_r")
Blues = LinearSegmentedColormap.from_list("b", ["#f7fbff", "#08306b"])


def chart_heatmap(title_match, fname, figsize):
    h = next(x for x in DATA["heatmaps"] if x["title"] == title_match)
    cmap = {"good_high": RdYlGn, "bad_high": RdYlGn_r}.get(h["mode"], Blues)
    rlabs = [r["label"] for r in h["rows"]]
    mat = [r["vals"] for r in h["rows"]]
    clabs = [f"{c['label']}\n(n={c['n']})" for c in h["cohorts"]]
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(mat, cmap=cmap, vmin=h["vmin"], vmax=h["vmax"], aspect="auto")
    ax.set_xticks(range(len(clabs)))
    ax.set_xticklabels(clabs, fontsize=9.5)
    ax.set_yticks(range(len(rlabs)))
    ax.set_yticklabels(rlabs, fontsize=10)
    rng = (h["vmax"] - h["vmin"]) or 1
    for i, row in enumerate(mat):
        for j, v in enumerate(row):
            t = (v - h["vmin"]) / rng
            light = 0.30 < t < 0.78 if h["mode"] != "seq" else t < 0.55
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9.5,
                    color="#1a1a1a" if light else "white")
    ax.set_title(h["title"] + "  (% v kohortě)", fontsize=12, loc="left", pad=10)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, fname)


# ---------- pomocné: počty osob u metrik skupiny ----------
def group_items(gkey, top=None, drop=()):
    g = next(x for x in DATA["metric_groups"] if x["key"] == gkey)
    items = []
    for mk in g["metrics"]:
        lab = DATA["metric_labels"][mk]
        if any(s in lab for s in drop):
            continue
        n = sum(1 for r in rows if mv(r, mk) == 1)
        items.append((lab, n))
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top] if top else items


def hbar(items, title, color, fname, figsize, unit="osob", xlabelmax=34):
    labels = [a if len(a) <= xlabelmax else a[:xlabelmax - 1] + "…" for a, _ in items][::-1]
    vals = [b for _, b in items][::-1]
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(labels, vals, color=color, height=0.7)
    for b, v in zip(bars, vals):
        ax.text(v + max(vals) * 0.012, b.get_y() + b.get_height() / 2, f"{v}",
                va="center", fontsize=9.5)
    ax.set_xlim(0, max(vals) * 1.12)
    ax.set_xlabel(f"počet {unit}")
    ax.set_title(title, fontsize=12.5, loc="left", pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, fname)


# ---------- chvála Q155 / výtky Q156 / zdroje Q154 / digitál / app ----------
def chart_chvala():
    hbar(group_items("q155", top=10), "V čem je Respekt výjimečný (Q155, chvála)",
         GREEN, "chvala.png", (7.2, 4.2))


def chart_vytky():
    items = group_items("q156", drop=("Nic nevadí",))
    hbar(items, "Co předplatitelům nejvíce vadí (Q156) — cena je až na dně",
         "#d98a3d", "vytky.png", (7.2, 5.6))


def chart_zdroje():
    hbar(group_items("q154", top=10), "Jaké jiné zdroje sledují (Q154) — konkurence",
         "#2f6db0", "zdroje.png", (7.2, 4.2))


def chart_digital():
    hbar(group_items("digital", top=8), "Co přimělo přejít na digitál (Q60)",
         "#5a7d9a", "digital_drivers.png", (7.2, 3.6))


def chart_app_prani():
    items = group_items("appchybi", top=9, drop=("nic nechybí", "Nic ",))
    hbar(items, "Co nejvíce chybí v aplikaci (přání)", "#7a6da8",
         "app_prani.png", (7.2, 4.0))


# ---------- churneři vs celek: over-index výtek (#13) ----------
def chart_churneri_overindex():
    g = next(x for x in DATA["metric_groups"] if x["key"] == "q156")
    pick = ["Jednostrannost", "Délka", "Kulturní", "Audio", "Tón", "Aplikace"]
    sel = []
    for want in pick:
        mk = next((k for k in g["metrics"] if want in DATA["metric_labels"][k]), None)
        if mk:
            sel.append((DATA["metric_labels"][mk], mk))
    ch = [r for r in rows if churn(r)]

    def pc(sub, mk):
        return 100 * sum(1 for r in sub if mv(r, mk) == 1) / len(sub)

    labs = [a.split(" /")[0].split(" (")[0] for a, _ in sel]
    cv = [pc(ch, mk) for _, mk in sel]
    av = [pc(rows, mk) for _, mk in sel]
    import numpy as np
    y = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.barh(y + 0.2, av, height=0.36, color=GRAY, label="celek")
    ax.barh(y - 0.2, cv, height=0.36, color=RED, label="uvažují o zrušení")
    for i, (c, a) in enumerate(zip(cv, av)):
        ax.text(c + 0.15, i - 0.2, f"{c:.0f} %", va="center", fontsize=9)
        ax.text(a + 0.15, i + 0.2, f"{a:.0f} %", va="center", fontsize=9, color="#777")
    ax.set_yticks(y)
    ax.set_yticklabels(labs)
    ax.invert_yaxis()
    ax.set_xlim(0, max(cv) * 1.25)
    ax.set_xlabel("% skupiny, které téma zmínilo")
    ax.set_title("Kdo odchází, vadí mu víc jednostrannost a tón", fontsize=12.5, loc="left", pad=10)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "churneri_overindex.png")


if __name__ == "__main__":
    print("Generuji grafy do charts/:")
    chart_churn_tenure()
    chart_churn_segments()
    chart_delka_preference()
    chart_heatmap("Spokojenost s atributy", "heat_spokojenost.png", (6.6, 3.6))
    chart_heatmap("Zájem o okruhy obsahu", "heat_zajmy.png", (6.6, 4.2))
    chart_heatmap("Riziko odchodu", "heat_riziko.png", (6.6, 2.0))
    chart_heatmap("Co přimělo k předplatnému", "heat_konv.png", (6.6, 5.2))
    chart_chvala()
    chart_vytky()
    chart_churneri_overindex()
    chart_zdroje()
    chart_digital()
    chart_app_prani()
    print("Hotovo.")
