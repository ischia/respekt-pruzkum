# Newslettery

Report newsletterů z **mailer.respekt.cz** (REMP Mailer): kolik lidí je odebírá,
jaký mají open rate a click rate a jak se srovnávají nové přihlášky
s odhlášeními.

Živý dashboard: <https://ischia.github.io/respekt-pruzkum/newslettery/dashboard/>
(heslo stejné jako u [dashboardu průzkumu](../dashboard/)).

## Jak to funguje

`.github/workflows/newslettery.yml` jednou denně:

1. stáhne data z maileru (`src/collect.js`) – přihlašovací údaje jsou
   repo secrets `MAILER_EMAIL` a `MAILER_PASSWORD`,
2. sestaví `dashboard/data.json` (`src/build.js`) a **commitne ho na `main`**
   – z toho GitHub Pages servíruje živý report,
3. syrovou historii (`data/history.json`, needá se do `main`) uloží do
   samostatné větve `newslettery-data` (jediný přepisovaný commit), aby
   přežila mezi jednotlivými sběry – mailer sám zpětně ukazuje počty
   odběratelů jen 30 dní, tahle větev drží delší řadu.

## Lokální spuštění

```bash
cd newslettery
npm install
npx playwright install chromium

export MAILER_EMAIL="…"
export MAILER_PASSWORD="…"

npm run collect   # 2 roky historie, cca 2 minuty
npm run build
npm run serve     # http://localhost:8732/
```

## Bezpečnost: do maileru se smí jen číst

V mailer UI je mazací ikona hned vedle ikony statistik, proto se do UI
nikdy neklikáme:

- `src/collect.js` naviguje výhradně přes URL,
- `src/guard.js` zruší každý požadavek, který není `GET` (výjimkou je
  jediné přihlášení), každou URL s Nette signálem `?do=…` (mazání je
  právě signál) a každou cestu se slovem delete/duplicate/import/(un)subscribe.

## Nastavení repa (jednorázově)

V **Settings → Secrets and variables → Actions** přidat:

- `MAILER_EMAIL`
- `MAILER_PASSWORD`

(stejné přihlašovací údaje jako do `mailer.respekt.cz`).
