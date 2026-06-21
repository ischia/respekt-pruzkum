# -*- coding: utf-8 -*-
"""Spoji obohaceny dataset (uzavrene otazky + nove promenne) s kodovanim
otevrenych otazek do JEDNOHO analytickeho souboru: 1 radek = 1 respondent,
join pres ID. Diky tomu jdou krizit demografie/churn s tematy ze vsech otazek.

Vstup:  data/processed/respekt_obohaceno.csv
        data/processed/respekt_otevrene_kodovano.csv
Vystup: data/processed/respekt_analyticky.csv
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'

f_ob = PROC / 'respekt_obohaceno.csv'
f_ko = PROC / 'respekt_otevrene_kodovano.csv'
for f in (f_ob, f_ko):
    if not f.exists():
        raise SystemExit(f'Chybi {f.name} – nejdriv spust prekodovani.py a koduj_otevrene.py')

ob = pd.read_csv(f_ob, dtype=str, keep_default_na=False)
ko = pd.read_csv(f_ko, dtype=str, keep_default_na=False)

# kontroly: unikatni a shodne ID, zadny prekryv sloupcu krome ID
assert ob['ID'].is_unique and ko['ID'].is_unique, 'ID nejsou unikatni'
assert set(ob['ID']) == set(ko['ID']), 'Sady ID se mezi soubory neshoduji'
shared = (set(ob.columns) & set(ko.columns)) - {'ID'}
assert not shared, f'Necekany prekryv nazvu sloupcu: {sorted(shared)}'

merged = ob.merge(ko, on='ID', how='left', validate='one_to_one')
merged.to_csv(PROC / 'respekt_analyticky.csv', index=False)

print(f'Spojeno pres ID: {ob.shape[1]} sloupcu (obohaceny) '
      f'+ {ko.shape[1]-1} tematickych priznaku (otevrene otazky)')
print(f'Ulozeno: respekt_analyticky.csv {merged.shape}')
