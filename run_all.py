# -*- coding: utf-8 -*-
"""Spusti celou pipeline: prekodovani uzavrenych otazek + kodovani otevrenych.
Pouziti:  python run_all.py
Vstup:    nejnovejsi data/raw/SurveyHeroResponses*.csv
Vystup:   data/processed/"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ['src/prekodovani.py', 'src/koduj_otevrene.py']

for s in STEPS:
    print(f'\n>>> {s}')
    subprocess.run([sys.executable, str(ROOT / s)], check=True)

print('\nHotovo. Vystupy najdes v data/processed/:')
for f in sorted((ROOT / 'data' / 'processed').glob('*')):
    print('  -', f.name)
