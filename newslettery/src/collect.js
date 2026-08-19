#!/usr/bin/env node
/**
 * Stáhne z maileru statistiky newsletterů a uloží je do lokální historie.
 *
 *   node apps/newslettery/src/collect.js                 # celá historie (2 roky zpět)
 *   node apps/newslettery/src/collect.js --from 2021-01-01
 *   node apps/newslettery/src/collect.js --only dnesni_respekt,vzkaz_z_respektu
 *
 * Přihlašovací údaje: MAILER_EMAIL, MAILER_PASSWORD (např. v .env, který se necommituje).
 * Data se ukládají mimo Git do apps/newslettery/data/history.json
 * (jinam přes NEWSLETTERY_DATA_DIR).
 */

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import { openMailer, fetchListsJson, fetchDailyStats, fetchSubscriberChart } from "./mailer.js";
import { parseLists, parseDailyStats, parseSubscriberSeries, mergeSnapshot, emptyHistory } from "./parse.js";
import { dataDir, historyPath, readHistory, writeHistory, today } from "./storage.js";

function parseArgs(argv) {
  const args = { from: null, to: "now", only: null, skipDetail: false, headed: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--from") args.from = argv[++i];
    else if (arg === "--to") args.to = argv[++i];
    else if (arg === "--only") args.only = argv[++i].split(",").map((v) => v.trim()).filter(Boolean);
    else if (arg === "--skip-detail") args.skipDetail = true;
    else if (arg === "--headed") args.headed = true;
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error(`Neznámý přepínač: ${arg}`);
  }
  return args;
}

function defaultFrom() {
  const date = new Date();
  date.setUTCFullYear(date.getUTCFullYear() - 2);
  return date.toISOString().slice(0, 10);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write("Použití: collect.js [--from YYYY-MM-DD] [--to YYYY-MM-DD|now] [--only kód,kód] [--skip-detail] [--headed]\n");
    return;
  }

  const from = args.from ?? defaultFrom();
  const to = args.to ?? "now";
  const collectedAt = new Date().toISOString();
  const date = today();

  process.stdout.write(`[info] sbírám ${from} → ${to}, data v ${dataDir()}\n`);

  const { page, close } = await openMailer({ headless: !args.headed });
  const snapshot = { date, collectedAt, lists: [], daily: {}, subscribers: {} };

  try {
    const lists = parseLists(await fetchListsJson(page));
    const selected = args.only
      ? lists.filter((list) => args.only.includes(list.code) || args.only.includes(String(list.id)))
      : lists;

    snapshot.lists = selected;
    process.stdout.write(`[info] listů: ${lists.length}, sbírám detail pro ${selected.length}\n`);

    for (const list of selected) {
      if (args.skipDetail) continue;
      const daily = parseDailyStats(await fetchDailyStats(page, list.id, { from, to }));
      const subscribers = parseSubscriberSeries(await fetchSubscriberChart(page, list.id));

      snapshot.daily[String(list.id)] = daily;
      snapshot.subscribers[String(list.id)] = subscribers;

      const sent = daily.reduce((sum, row) => sum + row.sent, 0);
      process.stdout.write(
        `[list ${String(list.id).padStart(2)}] ${list.title} – odběratelů ${list.subscribed}, ` +
          `dnů s daty ${daily.filter((row) => row.sent > 0).length}, rozesláno ${sent}\n`
      );
    }
  } finally {
    await close();
  }

  const history = mergeSnapshot(readHistory() ?? emptyHistory(), snapshot);
  writeHistory(history);

  const days = Object.values(history.daily).reduce((sum, rows) => sum + Object.keys(rows).length, 0);
  process.stdout.write(`[hotovo] ${historyPath()} – ${Object.keys(history.lists).length} listů, ${days} denních záznamů\n`);
}

main().catch((error) => {
  process.stderr.write(`[chyba] ${error.message}\n`);
  process.exitCode = 1;
});
