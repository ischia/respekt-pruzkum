/**
 * Čtecí klient pro REMP Mailer (mailer.respekt.cz).
 *
 * BEZPEČNOST – tenhle modul smí mailer jen číst:
 *   • naviguje se výhradně přes URL, nikdy klikáním do tabulky (mazací ikona
 *     je v UI hned vedle ikony statistik),
 *   • route guard zruší každý požadavek, který není GET (výjimkou je jediné
 *     přihlášení), a každou URL s Nette signálem `do=` nebo se slovem
 *     delete/duplicate/remove v cestě.
 * Když se guard spustí, je to chyba v kódu – proto se to hlásí na stderr.
 */

import { chromium } from "playwright";

import { MAILER_BASE, isAllowedRequest } from "./guard.js";

export { MAILER_BASE };

const SIGN_IN_URL = `${MAILER_BASE}/mailer/sign/in`;

async function installGuard(page, state) {
  await page.route("**/*", (route, request) => {
    const url = request.url();
    const method = request.method();
    if (isAllowedRequest({ url, method }, state)) return route.continue();
    process.stderr.write(`[guard] blokováno: ${method} ${url}\n`);
    return route.abort();
  });
}

/** Otevře prohlížeč, přihlásí se a vrátí { page, close }. */
export async function openMailer({ email, password, headless = true } = {}) {
  const user = email ?? process.env.MAILER_EMAIL;
  const pass = password ?? process.env.MAILER_PASSWORD;
  if (!user || !pass) throw new Error("Chybí MAILER_EMAIL / MAILER_PASSWORD v prostředí.");

  const browser = await chromium.launch({ headless });
  const context = await browser.newContext();
  const page = await context.newPage();
  const state = { loginAllowed: true };
  await installGuard(page, state);

  await page.goto(SIGN_IN_URL, { waitUntil: "domcontentloaded" });
  await page.getByLabel("Email Address").fill(user);
  await page.getByLabel("Password").fill(pass);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForLoadState("networkidle");
  state.loginAllowed = false;

  if (page.url().includes("/sign/in")) {
    await browser.close();
    throw new Error("Přihlášení do maileru selhalo – zkontroluj MAILER_EMAIL / MAILER_PASSWORD.");
  }

  return { page, close: () => browser.close() };
}

/** Stáhne přehled listů (DataTables JSON, bez signálů). */
export async function fetchListsJson(page) {
  const response = await page.goto(`${MAILER_BASE}/mailer/list/default-json-data`, {
    waitUntil: "domcontentloaded",
  });
  if (!response || !response.ok()) throw new Error(`Přehled listů se nenačetl (HTTP ${response?.status()}).`);
  return response.json();
}

/**
 * Denní řady sent/opened/clicked/unsubscribed pro jeden list.
 * Stránka si data vykresluje serverem do globálních proměnných (snippet exportData),
 * takže je stačí přečíst; AJAX dotaz, který stránka pouští po načtení, guard zablokuje
 * a server-rendered hodnoty tím zůstanou nedotčené.
 */
export async function fetchDailyStats(page, listId, { from, to, tz = "Europe/Prague" }) {
  const url = new URL(`${MAILER_BASE}/mailer/list/sent-emails-detail/${listId}`);
  url.searchParams.set("published_from", from);
  url.searchParams.set("published_to", to);
  url.searchParams.set("group_by", "day");
  url.searchParams.set("tz", tz);

  await page.goto(url.toString(), { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => typeof window.labels !== "undefined", null, { timeout: 30000 });

  return page.evaluate(() => ({
    labels: window.labels ?? [],
    sent: window.sentDataSet?.data ?? [],
    opened: window.openedDataSet?.data ?? [],
    clicked: window.clickedDataSet?.data ?? [],
    unsubscribed: window.unsubscribedDataSet?.data ?? [],
  }));
}

/** 30denní historie počtu odběratelů z grafu na list/show/{id}. */
export async function fetchSubscriberChart(page, listId) {
  await page.goto(`${MAILER_BASE}/mailer/list/show/${listId}`, { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => typeof window.myLineChart !== "undefined", null, { timeout: 30000 });

  return page.evaluate(() => ({
    labels: window.myLineChart?.data?.labels ?? [],
    datasets: (window.myLineChart?.data?.datasets ?? []).map((set) => ({ data: set.data })),
  }));
}
