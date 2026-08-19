#!/usr/bin/env node
/**
 * Z lokální historie (data/history.json) postaví podklad pro dashboard
 * (dashboard/data.json). Nic nestahuje – jen počítá.
 *
 *   node apps/newslettery/src/build.js
 */

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import { deriveSignups } from "./parse.js";
import { readHistory, dashboardDataPath, historyPath } from "./storage.js";

/** Systémové a transakční listy – v přehledu newsletterů jen matou, ale nezahazujeme je. */
const SYSTEM_CATEGORY = /systém|system/i;

export function buildPayload(history) {
  const lists = Object.values(history.lists ?? {}).map((list) => {
    const key = String(list.id);
    const daily = history.daily?.[key] ?? {};
    const subscribers = history.subscribers?.[key] ?? {};
    const signupsByDate = deriveSignups(subscribers, mapValues(daily, (row) => row.unsubscribed ?? 0));

    const dates = [...new Set([...Object.keys(daily), ...Object.keys(subscribers)])].sort();
    const rows = dates.map((date) => {
      const stats = daily[date] ?? {};
      const signup = signupsByDate[date];
      return {
        date,
        sent: stats.sent ?? 0,
        opened: stats.opened ?? 0,
        clicked: stats.clicked ?? 0,
        unsubscribed: stats.unsubscribed ?? 0,
        subscribers: subscribers[date] ?? null,
        signups: signup ? signup.signups : null,
        signupsSpanDays: signup ? signup.spanDays : null,
      };
    });

    const withData = rows.filter((row) => row.sent > 0 || row.unsubscribed > 0 || row.subscribers !== null);
    const lastSend = [...withData].reverse().find((row) => row.sent > 0) ?? null;

    return {
      id: list.id,
      title: list.title,
      code: list.code,
      category: list.category,
      isSystem: SYSTEM_CATEGORY.test(list.category ?? ""),
      locked: Boolean(list.locked),
      publicListing: Boolean(list.publicListing),
      subscribers: list.subscribed ?? null,
      lastSendDate: lastSend?.date ?? null,
      dates: withData.map((row) => row.date),
      sent: withData.map((row) => row.sent),
      opened: withData.map((row) => row.opened),
      clicked: withData.map((row) => row.clicked),
      unsubscribed: withData.map((row) => row.unsubscribed),
      subscribersSeries: withData.map((row) => row.subscribers),
      signups: withData.map((row) => row.signups),
      signupsSpanDays: withData.map((row) => row.signupsSpanDays),
    };
  });

  lists.sort((a, b) => (b.subscribers ?? 0) - (a.subscribers ?? 0));

  const allDates = lists.flatMap((list) => list.dates);
  const subscriberDates = lists.flatMap((list) =>
    list.dates.filter((_, index) => list.subscribersSeries[index] !== null)
  );

  return {
    generatedAt: new Date().toISOString(),
    collectedAt: history.updatedAt ?? null,
    range: {
      from: allDates.length ? allDates.reduce(min) : null,
      to: allDates.length ? allDates.reduce(max) : null,
      subscribersFrom: subscriberDates.length ? subscriberDates.reduce(min) : null,
    },
    lists,
  };
}

const min = (a, b) => (b < a ? b : a);
const max = (a, b) => (b > a ? b : a);

function mapValues(object, fn) {
  return Object.fromEntries(Object.entries(object).map(([key, value]) => [key, fn(value)]));
}

function main() {
  const history = readHistory();
  if (!history) {
    process.stderr.write(`[chyba] Chybí ${historyPath()} – spusť nejdřív collect.js.\n`);
    process.exitCode = 1;
    return;
  }

  const payload = buildPayload(history);
  const target = dashboardDataPath();
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, `${JSON.stringify(payload)}\n`);

  const days = payload.lists.reduce((sum, list) => sum + list.dates.length, 0);
  process.stdout.write(
    `[hotovo] ${target} – ${payload.lists.length} listů, ${days} denních řádků, ` +
      `období ${payload.range.from ?? "?"} → ${payload.range.to ?? "?"}\n`
  );
}

if (process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]))) main();
