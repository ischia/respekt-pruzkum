# -*- coding: utf-8 -*-
"""
Respekt - predplatitelsky pruzkum (export 2026-06-20)
Prekodovani: normalizace znecistenych uzavrenych otazek, nove binarni priznaky
z volneho textu (s de-duplikaci na urovni osoby), obohaceni existujicich moznosti
(puvodni zachovane + varianta _vc_text) a ordinalni -> numericke promenne.

Ridici pravidlo: kazda priznakova promenna = (zaskrtnuto NEBO zmineno v textu),
boolean na urovni respondujici osoby. Osoba se zapocita nejvyse jednou.
"""
import pandas as pd, numpy as np, unicodedata, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'data' / 'raw'
OUT_DIR = ROOT / 'data' / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def newest_export():
    files = sorted(RAW_DIR.glob('SurveyHeroResponses*.csv'))
    if not files:
        raise SystemExit(f'Zadny export v {RAW_DIR}/ (ocekavam SurveyHeroResponses*.csv)')
    return files[-1]

SRC = newest_export()
print(f'Vstup: {SRC.name}')
df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
df = df[df['Status'] == 'Completed'].reset_index(drop=True)
N = len(df)

def norm(s):
    s = str(s).strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s)

def ticked(ci):
    return df.iloc[:, ci].str.strip().str.lower().eq('x')

def txt(ci):
    return df.iloc[:, ci].map(norm)

def text_hit(cols, pattern):
    pat = re.compile(pattern)
    hit = pd.Series(False, index=df.index)
    for ci in cols:
        hit = hit | txt(ci).str.contains(pat)
    return hit

new = pd.DataFrame(index=df.index)
log = []

# ===================================================================
# A) NORMALIZACE ZNECISTENYCH "UZAVRENYCH" OTAZEK
# ===================================================================

# --- A1: pracovni_status_clean (col 160) ---
CLEAN = {
    'zamestnanecky pomer': 'Zamestnanecky pomer',
    'podnikatel/ka / osvc': 'OSVC / podnikani',
    'duchodce/kyne': 'Duchod (nepracujici)',
    'v domacnosti / na rodicovske': 'V domacnosti / na rodicovske',
    'student/ka': 'Student/ka',
    'nezamestnany/a': 'Nezamestnany/a',
}
WP = re.compile(r'prduch|prac\w*\s*(penzist|duchod|senior)|prac\.?\s*duchod'
                r'|(duchod|penzist|senior)\w*[\s,+./-]*\w*[\s,+./-]*(osvc|prac|zamest|podnik|obcasn|cast|pomer)'
                r'|(osvc|prac|zamest|podnik|obcasn|pomer)\w*[\s,+./-]*\w*[\s,+./-]*(duchod|penzist|senior)'
                r'|senior\w*[\s,]*\w*[\s,]*(prac|zamest|pozic|projekt|extern)'
                r'|invalidn\w*[\s,]*\w*[\s,]*(zamest|prac)')
RETIRE = re.compile(r'duchod|penz|senior|prduch|predduch')
WORK = re.compile(r'osvc|podnik|zivnost|volne noze|zamest|\bprac|uvazek|brigad|jednatel|redite|manaz'
                  r'|manager|starost|lekar|hudebnik|projektant|doktorand|stipend|statutar|spolumajitel'
                  r'|umelec|prekladatel|psychoterap|diplomat|pozic')
FIRST = [('zamest','Zamestnanecky pomer'),('osvc','OSVC / podnikani'),('podnik','OSVC / podnikani'),
         ('zivnost','OSVC / podnikani'),('volne noze','OSVC / podnikani'),
         ('student','Student/ka'),('studuj','Student/ka'),('doktorand','Student/ka'),
         ('rodicov','V domacnosti / na rodicovske'),('matersk','V domacnosti / na rodicovske'),
         ('domacnost','V domacnosti / na rodicovske'),('pestoun','V domacnosti / na rodicovske'),
         ('pece o','V domacnosti / na rodicovske'),('nezamest','Nezamestnany/a')]

def classify_status(raw):
    s = raw.strip()
    if s == '':
        return np.nan
    n = norm(s)
    if n in {'---', '-', 'jine', 'funkce', 'bez odpovedi', 'prac'}:
        return 'Neuvedeno / jine'
    if n in CLEAN:
        return CLEAN[n]
    if WP.search(n):
        return 'Pracujici duchod'
    hr, hw = bool(RETIRE.search(n)), bool(WORK.search(n))
    if hr and hw:
        return 'Pracujici duchod'
    if hr:
        return 'Duchod (nepracujici)'
    pos = sorted((n.find(tok), cat) for tok, cat in FIRST if tok in n)
    if pos:
        return pos[0][1]
    if hw:
        return 'Zamestnanecky pomer'
    return 'Neuvedeno / jine'

new['pracovni_status_clean'] = df.iloc[:, 160].map(classify_status)
new['duchodce'] = new['pracovni_status_clean'].isin(['Duchod (nepracujici)', 'Pracujici duchod'])

# --- A2: podcast_platforma_clean (col 152) ---
MULTI = re.compile(r'mix|strid|nebo vase|cca na stejno|nahodn|web a aplikace|podle (toho|moznosti)|vse krome|vseho')
THIRD = re.compile(r'antennapod|antena pod|anthenapod|antenna pod|pocket ?cast|pocketcast|podcast addict'
                   r'|\baddict|podbean|overcast|castbox|podcast ?guru|podcastguru|player fm|pocket podcast|\brss|nosic')
VAGUE = re.compile(r'jina (podcast|aplikace)|jine aplikace|^aplikace$|podcasts?$|nejak|free podcast|socialni|^site$')

def classify_platform(raw):
    s = raw.strip()
    if s == '':
        return np.nan
    n = norm(s)
    if 'audiotek' in n: return 'Audioteka'
    if 'aplikace respektu' in n: return 'Aplikace Respektu'
    if 'web respektu' in n: return 'Web Respektu'
    if MULTI.search(n): return 'Vice platforem / dle situace'
    if 'spotify' in n: return 'Spotify'
    if 'apple' in n: return 'Apple Podcasts'
    if 'youtube' in n: return 'YouTube'
    if THIRD.search(n): return 'Jina podcastova aplikace'
    if VAGUE.search(n): return 'Jina podcastova aplikace'
    return 'Neuvedeno'

new['podcast_platforma_clean'] = df.iloc[:, 152].map(classify_platform)

# ===================================================================
# B) NOVE BINARNI PRIZNAKY Z TEXTU (de-dup napric poli = boolean/osoba)
# ===================================================================
DAR = r'\bdar(?:ek|ku|kem|em|oval|ovan|kova)|jako dar|dostal\w*\s\w*\s?dar|darem'
NEPRESEL = (r'nepres|mam oboj|ctu oboj|\boboje\b|\boboji\b|i tisten|stale.{0,12}tisten'
            r'|porad.{0,12}tisten|tistenou.{0,8}verzi|neprejdu|nechci.{0,12}(?:digital|papir|tisk)'
            r'|odebiram i tisten|kombinuji')
JIDLO = r'snidan|\bjidl|\bobed|svacin|u jidla|pri jidle'
CEKANI = r'cekan|cekam|nekde cek|\bcekat'
RODINA = r'rodin|znam[e]|\bznam[yaei]|pratel|kamarad|manzel|partner|svagr'
PROCHAZKA = r'prochazk|se psem|\bvenku|venceni|na zahrad'
KAVARNA = r'kavarn'
KRIZOVKA = r'krizovk'
NIC = r'^nic\b|nic mi nechyb|nechybi nic|jsem spokoj|vse (?:ok|funguje)|vyhovuje mi vse|nic me nenapad|^nic$'

new['pouziva_audioteku']      = text_hit([52,152,104,153,60], r'audiotek')
new['predplatne_darek']       = text_hit([28,19,44], DAR)
new['cte_tisk_i_digital']     = text_hit([60], NEPRESEL)
new['situace_jidlo']          = text_hit([104], JIDLO)
new['situace_cekani']         = text_hit([104], CEKANI)
new['situace_prochazka']      = text_hit([104], PROCHAZKA)
new['situace_kavarna']        = text_hit([104], KAVARNA)
new['styk_pres_zname_rodinu'] = text_hit([19], RODINA)
new['zajem_krizovka']         = text_hit([28,35,95,137,52,44], KRIZOVKA)
new['aplikace_nic_nechybi']   = text_hit([95], NIC)

# ===================================================================
# B2) KONVERZNI MOTIVY (col 28 "Co vas primelo poridit predplatne" - volny text)
# Temata, ktera v baterii (cols 21-27) NEMAJI checkbox: kvalita/obsah, zvyk/
# dlouholety vztah, duvera, prehled, pohodli doruceni, zivot v zahranici.
# => cisty pridavek, zadny prekryv k odecteni. Darek pokryva predplatne_darek.
# Boolean na osobu, jen z col 28 (motiv patri k teto otazce).
# ===================================================================
KONV_KVALITA = (r'kvalit|novinarin|novinarsk|zurnalist|profesional|urovn|poctiv|seriozn'
                r'|pestrost|rozmanit|mix temat|spektrum|zajimav|skvel\w* obsah|dobr\w* obsah|obsah')
KONV_ZVYK    = (r'od (?:jeho )?(?:zacatku|vzniku|pocatku|sameho)|od 9\d|od devadesat|od roku'
                r'|leta (?:ctu|ho ctu)|ctu (?:uz |ho )?od|cetl\w* (?:uz )?od|kupoval|kupovala'
                r'|(?:ve|na) stanku|zvykl|prirozen|dlouholet|dlouhodobe (?:ctu|cteme|odebir)'
                r'|odebir\w* od|jiz od|znam\w* respekt|ma\w* (?:ho )?rad|mel\w* (?:respekt |ho )?rad'
                r'|laska k respekt|odedavna|vzdycky')
KONV_DUVERA  = (r'duver|verohodn|overen|spolehliv|nezkreslen|pravdiv|necenzur|nezauja'
                r'|objektiv|nestrann|spravn\w* informac|\bfakta')
KONV_PREHLED = (r'prehled|souhrn|shrn\w+|byt v obraze|v obraze|informovan'
                r'|prisun.{0,18}informac|pravideln\w* prisun|tydenik|tydenni')
KONV_POHODLI = (r'do schrank|ve schrance|nemus\w* (?:myslet|shanet|kupovat)'
                r'|nemuset (?:myslet|shanet|kupovat)|nechtelo se mi.{0,18}kupovat|neshanet'
                r'|jistota.{0,18}(?:dostane|schrank)|prakticte|kazdy tyden.{0,15}schrank')
KONV_ZAHRANICI = r'zahranic|nebydlim v cr|ziji v (?:zahranic|cizin)|mimo cr|v cizine|nezij\w* v cr'

new['konv_kvalita_obsah']     = text_hit([28], KONV_KVALITA)
new['konv_dlouholety_ctenar'] = text_hit([28], KONV_ZVYK)
new['konv_duvera']            = text_hit([28], KONV_DUVERA)
new['konv_prehled']           = text_hit([28], KONV_PREHLED)
new['konv_pohodli']           = text_hit([28], KONV_POHODLI)
new['konv_zahranici']         = text_hit([28], KONV_ZAHRANICI)

# ===================================================================
# B3) BARIEROVE VLAJKY (col 137 "Setkal/a jste se s barierami" - volny text)
# Temata, ktera v baterii barier (cols 129-135) NEMAJI checkbox => ciste vlajky.
# (Audio/tech/doruceni/cas se resi obohacenim boxu nize.) Boolean na osobu, jen col 137.
# ===================================================================
BAR_VYHLEDAVANI = (r'vyhledav|dohleda|(?:najit|hledat|vyhled)\w*.{0,15}star|starsi clan'
                   r'|chyb\w* archiv|v archivu')
BAR_OBSAH       = (r'kultur|hudb|\bvegan|jednostran|malo (?:clank|o )|vic (?:clank|o )'
                   r'|chybi (?:mi )?tema|zrusili|vynechal|moc o |prilis (?:social|politik)'
                   r'|povzbud|pozitivn')
BAR_EPUB        = r'epub|kindle|ctecka|amazon'

new['bariera_vyhledavani'] = text_hit([137], BAR_VYHLEDAVANI)
new['bariera_obsah']       = text_hit([137], BAR_OBSAH)
new['bariera_epub']        = text_hit([137], BAR_EPUB)

# ===================================================================
# B4) PRECHOD NA DIGITAL (col 60 "Co vas primelo prejit na digital" - volny text)
# Pole dominuji lide, kteri NEPRESLI (ctou tisk/oboji) = uz pokryva cte_tisk_i_digital.
# Nove kodujeme DUVODY a zpusob uziti, ktere checkbox baterie nema. Boolean, jen col 60.
# ===================================================================
PREF_TISK = (r'radeji.{0,12}(?:papir|tisten|casopis)|preferuj\w*.{0,12}(?:papir|tisten)'
             r'|prednost.{0,14}(?:papir|tisten)|nechci se.{0,14}vzdat|nechci.{0,10}vzdat'
             r'|fyzicky v ruce|\bv ruce|od (?:displeje|obrazovky)|odpocin\w*.{0,14}(?:displej|obrazov)'
             r'|aniz bych.{0,14}(?:telefon|tablet)|ritual|kafe a respekt'
             r'|milu\w*.{0,14}(?:papir|tisten|casopis|rano)|haptik|vyhybat.{0,12}digital|koukani do comp')
DIGITAL_DOPLNEK = (r'doplnek|doplnkov|jako bonus|bonus navic|navic k (?:papir|tisten)'
                   r'|rozsiren\w* tisten|na cestach|na ceste|s sebou|sebou mam|kdyz nejsem doma'
                   r'|mimo domov|prolistuj|v praci|o prestavk')
TISK_RODINA = (r'posila\w*|rodicum|mamince|manzel\w*|partner\w*|pritelkyn\w*|deti.{0,8}okupuj'
               r'|sdil\w*.{0,18}(?:rodin|pritel|manzel|partner|rodic)')

new['preferuje_tisk']   = text_hit([60], PREF_TISK)
new['digital_doplnek']  = text_hit([60], DIGITAL_DOPLNEK)
new['tisk_pro_rodinu']  = text_hit([60], TISK_RODINA)

# ===================================================================
# B5) CO CHYBI V APLIKACI (col 95 "Co vam nejvice chybi v mobilni aplikaci" - text)
# Temata bez checkboxu v baterii (cols 88-94). "Nic nechybi" pokryva
# aplikace_nic_nechybi; vyhledavani uz JE checkbox (box 88, +2 navic) -> nekodujeme
# znovu. Boolean na osobu, jen col 95.
# ===================================================================
APP_PREHLED = (r'neprehledn|prehledn|\bui\b|uzivatelsk\w* rozhrani|\bmenu|navigac|orientac'
               r'|tridit|usporad|\blista|ovladaci prvk|vraceni|zpet (?:mus|na)|titulni stran'
               r'|amatersk|predelat')
APP_PRISTUP = (r'zvets\w*|velikost (?:pism|font|text)|\bfont|pism\w* (?:moc )?mal|vetsi pism'
               r'|\bzoom|priblizit|posouvat (?:obraz|foto|fot)|popis\w*.{0,10}(?:fot|obraz)'
               r'|brejl|bryl|kontrastnejs')
APP_VYKON   = (r'pomal|trhan|\bseka|zasek|stabilit|spadne|plynul|\bcach|prodlev|spotreb\w* dat'
               r'|\bbug|nestabil|dlouho (?:se )?nacit|nacit\w* (?:dlouho|pomal)')
APP_AUDIO   = (r'autoplay|automatick\w* (?:spust|prehr)|\bpauz|cele vydani (?:naj|nelze|chyb)'
               r'|nelze pustit cele|po jednom clanku|nerozjede|skok\w* (?:vzad|vpred)|po skoku'
               r'|nepamatuje|mazat staz|stazene cisl|celkov\w* delk|jak daleko')
APP_PERSON  = r'personaliz|filtr|rubrik|\bsekc|neprecten\w* nad|synchroniz|vlastni (?:playlist|vyber)'
APP_TISKWEB = (r'(?:vyjde|bude|je) v tisten|v tistene|nen\w* v tisten|jen\w* na webu|jenom na webu'
               r'|nemam i clanky|ktere jsou (?:jen )?(?:mimo|na webu)')

new['app_prehlednost']    = text_hit([95], APP_PREHLED)
new['app_pristupnost']    = text_hit([95], APP_PRISTUP)
new['app_vykon']          = text_hit([95], APP_VYKON)
new['app_audio_ovladani'] = text_hit([95], APP_AUDIO)
new['app_personalizace']  = text_hit([95], APP_PERSON)
new['app_odliseni_tisk']  = text_hit([95], APP_TISKWEB)

# ===================================================================
# B6) CIL NA HOMEPAGE (col 73 "S jakym cilem na homepage prichazite" - text)
# Klicove zjisteni: homepage casto NENI vstupni bod. Temata bez checkboxu.
# Boolean na osobu, jen col 73.
# ===================================================================
HP_VSTUP = (r'newsletter|\bmail\b|mailov|emailu|e-mail|z mailu|do e-mailu|facebook|\bfb\b|\big\b'
            r'|instagram|socialn|na sitich|ze (?:soc|site)|na sit\b|promovan|\brss|qr kod')
HP_NECHODI = (r'nechodim|nechodi\b|temer nechodim|nepouzivam|vyuzivam malo|jen kdyz nemam'
              r'|spise doplnkov|moc tam nechodim')

new['homepage_vstup_odkaz'] = text_hit([73], HP_VSTUP)
new['homepage_nechodi']     = text_hit([73], HP_NECHODI)

# ===================================================================
# C) OBOHACENI EXISTUJICICH MOZNOSTI (puvodni box zachovan; pridavame _vc_text)
# ===================================================================
AIAUDIO = (r'\bai\b|umel|nadech|robot|strojov|neprirozen|namluv|\bhlas|vyslovnost'
           r'|predcitani|prizvuk|chybne cteni|cte (?:spatne|chybne)')
TECH = (r'zamrz|nefunguj|nenacita|spadne|chyb\w* aplikac|technick|nejde|nelze'
        r'|zasekne|nespusti|prestane (?:hrat|prehrav)|token|prihlas|nevypocitateln')
SOC = r'bluesky|mastodon|facebook|twitter|instagram|socialn|\bsit'
DORUCENI = (r'doruc|schrank|\bposta|\bpozde|nedosl|nepris\w*.{0,12}(?:cas|schrank)|obal|promoc'
            r'|urgov|zpozd|chodi.{0,18}(?:pozde|stred|ctvrt|nepravid)|opozd|dodani|dosla')
CASDELKA = (r'moc dlouh|prilis dlouh|(?:clank|text|reportaz|cislo|podcast|vydani)\w*.{0,12}dlouh'
            r'|dlouh\w*.{0,12}(?:clank|text|reportaz|podcast)|nestih|nedostatek casu|nemam cas'
            r'|mnozstv|moc (?:textu|obsahu|clanku|casto)|casove bariery')

def enrich(name, box_col, cols, pattern):
    orig = ticked(box_col)
    enr = orig | text_hit(cols, pattern)
    new[name] = enr
    log.append((name, df.columns[box_col][:34],
                f'orig {int(orig.sum())} -> obohaceno {int(enr.sum())} (+{int(enr.sum()-orig.sum())})'))

enrich('audio_umele_vc_text', 131, [137], AIAUDIO)
enrich('tech_problemy_vc_text', 129, [137], TECH)
enrich('styk_soc_site_vc_text', 17, [19], SOC)
enrich('doruceni_vc_text', 135, [137], DORUCENI)
enrich('cas_delka_vc_text', 132, [137], CASDELKA)

# ===================================================================
# D) ORDINALNI -> NUMERICKE
# ===================================================================
def kn(s):  # klicova normalizace: bez diakritiky + en/em-dash -> pomlcka
    return norm(s).replace('\u2013', '-').replace('\u2014', '-')

def cmap(ci, mapping, name):
    m = {kn(k): v for k, v in mapping.items()}
    new[name] = df.iloc[:, ci].map(lambda v: m.get(kn(v), np.nan))

cmap(11, {'Kratsi dobu nez rok':0,'1-5 let':1,'6-10 let':2,'11-15 let':3,'16-20 let':4,'21 a vice let':5}, 'delka_predplatneho_ord')
cmap(157,{'Mene nez 18':0,'18-24':1,'25-34':2,'35-44':3,'45-54':4,'55-64':5,'65 a vice':6}, 'vek_ord')
cmap(159,{'Zakladni':0,'Vyucen / SS bez maturity':1,'SS s maturitou':2,'Vysokoskolske':3}, 'vzdelani_ord')
cmap(161,{'Do 40 000 Kc':0,'40 001-70 000 Kc':1,'70 001-100 000 Kc':2,'Nad 100 000 Kc':3,'Nechci odpovidat':np.nan}, 'prijem_ord')
freq = {'Nepouzivam':0,'Nekolikrat za mesic':1,'Kazdy tyden':2,'Nekolikrat za tyden':3,'Kazdy den':4}
cmap(75, freq, 'frekvence_web_ord')
cmap(76, freq, 'frekvence_app_ord')
cmap(138,{'1':1,'2':2,'3':3,'4':4,'5':5}, 'doruceni_ord')
cmap(140,{'1':1,'2':2,'3':3,'4':4,'5':5}, 'pravdep_setrvani_ord')
cmap(139,{'Ne':0,'Ano, kratce':1,'Ano, vazne':2}, 'uvazoval_zruseni_ord')
cmap(141,{'Nevim o nich':0,'Vim o nich, ale neposloucham':1,'Zkousel/a jsem, ale prestal/a':2,'Ano, obcas':3,'Ano, pravidelne':4}, 'podcasty_zapojeni_ord')

def slug(s):
    s = norm(s); s = re.sub(r'[^a-z0-9]+','_',s); return s.strip('_')[:22]
SPOK = {'Spokojen/a':1,'Nespokojen/a':0,'Nevim':np.nan,'':np.nan}
DELKA = {'Spise delsi':1,'Spise kratsi':-1,'Nevim':np.nan,'':np.nan}
for ci in range(121,128):
    nm = 'spok_'+slug(df.columns[ci])
    m = {kn(k): v for k, v in SPOK.items()}
    new[nm] = df.iloc[:, ci].map(lambda v: m.get(kn(v), np.nan))
for ci in range(116,120):
    nm = 'delka_'+slug(df.columns[ci])+'_dir'
    m = {kn(k): v for k, v in DELKA.items()}
    new[nm] = df.iloc[:, ci].map(lambda v: m.get(kn(v), np.nan))

# ===================================================================
# VYSTUP + VALIDACE
# ===================================================================
out = pd.concat([df, new], axis=1)
out.to_csv(OUT_DIR / 'respekt_obohaceno.csv', index=False)

# --- codebook novych promennych ---
GROUP = {}
for c in ['pracovni_status_clean','duchodce','podcast_platforma_clean']: GROUP[c]='A_normalizace'
for c in ['pouziva_audioteku','predplatne_darek','cte_tisk_i_digital','situace_jidlo','situace_cekani',
          'situace_prochazka','situace_kavarna','styk_pres_zname_rodinu','zajem_krizovka','aplikace_nic_nechybi']:
    GROUP[c]='B_priznak_text'
for c in ['konv_kvalita_obsah','konv_dlouholety_ctenar','konv_duvera','konv_prehled','konv_pohodli','konv_zahranici']:
    GROUP[c]='B2_konverze_col28'
for c in ['bariera_vyhledavani','bariera_obsah','bariera_epub']:
    GROUP[c]='B3_bariery_col137'
for c in ['preferuje_tisk','digital_doplnek','tisk_pro_rodinu']:
    GROUP[c]='B4_digital_col60'
for c in ['app_prehlednost','app_pristupnost','app_vykon','app_audio_ovladani','app_personalizace','app_odliseni_tisk']:
    GROUP[c]='B5_aplikace_col95'
for c in ['homepage_vstup_odkaz','homepage_nechodi']:
    GROUP[c]='B6_homepage_col73'
for c in ['audio_umele_vc_text','tech_problemy_vc_text','styk_soc_site_vc_text','doruceni_vc_text','cas_delka_vc_text']: GROUP[c]='C_obohaceni'
cb = []
for c in new.columns:
    s = new[c]
    typ = 'bool' if s.dropna().isin([True,False]).all() and s.dtype==bool else ('num' if pd.api.types.is_numeric_dtype(s) else 'kat')
    nvalid = int(s.notna().sum())
    ntrue = int(s.sum()) if s.dtype==bool else ''
    cb.append({'promenna':c,'skupina':GROUP.get(c,'D_ordinaly'),'typ':typ,'n_valid':nvalid,'n_true':ntrue})
pd.DataFrame(cb).to_csv(OUT_DIR / 'respekt_codebook_nove.csv', index=False)

print(f'N (Completed) = {N}\n')
print('===== A) NORMALIZACE =====')
print('pracovni_status_clean:')
print(new['pracovni_status_clean'].value_counts(dropna=False).to_string())
print(f'  duchodce (flag) = {int(new["duchodce"].sum())}')
print('\npodcast_platforma_clean (jen vyplneni):')
print(new['podcast_platforma_clean'].value_counts(dropna=True).to_string())

print('\n===== B) NOVE PRIZNAKY (pocet osob = TRUE) =====')
for c in ['pouziva_audioteku','predplatne_darek','cte_tisk_i_digital','situace_jidlo',
          'situace_cekani','situace_prochazka','situace_kavarna','styk_pres_zname_rodinu',
          'zajem_krizovka','aplikace_nic_nechybi']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== B2) KONVERZNI MOTIVY col 28 (pocet osob = TRUE) =====')
for c in ['konv_kvalita_obsah','konv_dlouholety_ctenar','konv_duvera','konv_prehled','konv_pohodli','konv_zahranici']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== B3) BARIEROVE VLAJKY col 137 (pocet osob = TRUE) =====')
for c in ['bariera_vyhledavani','bariera_obsah','bariera_epub']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== B4) PRECHOD NA DIGITAL col 60 (pocet osob = TRUE) =====')
for c in ['preferuje_tisk','digital_doplnek','tisk_pro_rodinu']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== B5) CO CHYBI V APLIKACI col 95 (pocet osob = TRUE) =====')
for c in ['app_prehlednost','app_pristupnost','app_vykon','app_audio_ovladani','app_personalizace','app_odliseni_tisk']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== B6) CIL NA HOMEPAGE col 73 (pocet osob = TRUE) =====')
for c in ['homepage_vstup_odkaz','homepage_nechodi']:
    print(f'  {c:26s} = {int(new[c].sum())}')

print('\n===== C) OBOHACENI (de-dup overeni) =====')
for nm, src, detail in log:
    print(f'  {nm:24s} | {detail}')

print('\n===== D) ORDINALY (pocet validnich / prumer) =====')
for c in ['delka_predplatneho_ord','vek_ord','vzdelani_ord','prijem_ord','frekvence_web_ord',
          'frekvence_app_ord','doruceni_ord','pravdep_setrvani_ord','uvazoval_zruseni_ord','podcasty_zapojeni_ord']:
    s = pd.to_numeric(new[c], errors='coerce')
    print(f'  {c:26s} | n={int(s.notna().sum()):4d} | mean={s.mean():.2f}')
print(f'\nCelkem novych sloupcu: {new.shape[1]}')
print('Ulozeno: respekt_obohaceno.csv', out.shape)
