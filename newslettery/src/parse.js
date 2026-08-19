/**
 * Čisté funkce pro převod odpovědí REMP Maileru na náš datový model.
 * Nic zde nesmí sahat na síť ani na disk – aby to šlo testovat bez maileru.
 */

/** Z odkazu typu /mailer/list/show/18 vytáhne ID listu. */
export function listIdFromUrl(url) {
  const match = /\/(\d+)(?:[/?#]|$)/.exec(String(url ?? ""));
  return match ? Number(match[1]) : null;
}

/**
 * Převede odpověď /mailer/list/default-json-data (DataTables formát) na pole listů.
 * Řádek je PHP pole s číselnými klíči + klíčem "actions", takže v JSONu je to objekt.
 */
export function parseLists(json) {
  const rows = Array.isArray(json?.data) ? json.data : [];
  const lists = [];

  for (const row of rows) {
    const id = listIdFromUrl(row?.actions?.show);
    if (id === null) continue;

    const titleCell = row["1"];
    lists.push({
      id,
      title: typeof titleCell === "object" ? String(titleCell?.text ?? "") : String(titleCell ?? ""),
      code: row["2"] == null ? "" : String(row["2"]),
      category: row["0"] == null ? "" : String(row["0"]),
      subscribed: toNumber(row["3"]),
      autoSubscribe: Boolean(row["4"]),
      locked: Boolean(row["5"]),
      publicListing: Boolean(row["6"]),
    });
  }

  lists.sort((a, b) => a.id - b.id);
  return lists;
}

/** "5,736" i 5736 → 5736; cokoli nečíselného → null. */
export function toNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  const cleaned = String(value).replace(/[\s ,]/g, "");
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? parsed : null;
}

/**
 * Chart.js proměnné ze stránky sent-emails-detail (group_by=day) → denní řádky.
 * Labels jsou ve formátu YYYY-MM-DD; ostatní pole jsou paralelní pole hodnot.
 */
export function parseDailyStats(vars) {
  const labels = Array.isArray(vars?.labels) ? vars.labels : [];
  const sent = vars?.sent ?? [];
  const opened = vars?.opened ?? [];
  const clicked = vars?.clicked ?? [];
  const unsubscribed = vars?.unsubscribed ?? [];

  const rows = [];
  labels.forEach((label, index) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(label))) return;
    rows.push({
      date: String(label),
      sent: toNumber(sent[index]) ?? 0,
      opened: toNumber(opened[index]) ?? 0,
      clicked: toNumber(clicked[index]) ?? 0,
      unsubscribed: toNumber(unsubscribed[index]) ?? 0,
    });
  });
  return rows;
}

/**
 * Graf "Subscribed users" ze stránky list/show/{id} → denní počty odběratelů.
 * Nula znamená "ten den se počet nezaznamenal", ne "nula odběratelů" – zahazujeme ji.
 */
export function parseSubscriberSeries(chartData) {
  const labels = Array.isArray(chartData?.labels) ? chartData.labels : [];
  const values = chartData?.datasets?.[0]?.data ?? [];

  const rows = [];
  labels.forEach((label, index) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(label))) return;
    const count = toNumber(values[index]);
    if (count === null || count === 0) return;
    rows.push({ date: String(label), subscribers: count });
  });
  return rows;
}

/** Prázdná historie ve tvaru, který čte i zapisuje collect.js. */
export function emptyHistory() {
  return { version: 1, updatedAt: null, lists: {}, daily: {}, subscribers: {} };
}

/**
 * Zapíše nový sběr do historie (idempotentně – klíčem je datum).
 * Novější sběr přepisuje starší hodnoty pro stejný den, protože mailer čísla
 * dopočítává (otevření a prokliky ještě několik dní po rozeslání přibývají).
 */
export function mergeSnapshot(history, snapshot) {
  const merged = {
    ...emptyHistory(),
    ...history,
    lists: { ...(history?.lists ?? {}) },
    daily: { ...(history?.daily ?? {}) },
    subscribers: { ...(history?.subscribers ?? {}) },
  };

  for (const list of snapshot.lists ?? []) {
    const key = String(list.id);
    merged.lists[key] = {
      id: list.id,
      title: list.title,
      code: list.code,
      category: list.category,
      autoSubscribe: list.autoSubscribe,
      locked: list.locked,
      publicListing: list.publicListing,
      subscribed: list.subscribed,
    };

    // živý počet z přehledu listů je záložní měření pro dnešek; pokud mailer
    // pro tenhle den má vlastní denní záznam, přepíše ho níž (jedna řada = jeden zdroj)
    if (list.subscribed !== null && snapshot.date) {
      merged.subscribers[key] = { ...(merged.subscribers[key] ?? {}), [snapshot.date]: list.subscribed };
    }
  }

  for (const [listId, rows] of Object.entries(snapshot.daily ?? {})) {
    const target = { ...(merged.daily[listId] ?? {}) };
    for (const row of rows) {
      target[row.date] = {
        sent: row.sent,
        opened: row.opened,
        clicked: row.clicked,
        unsubscribed: row.unsubscribed,
      };
    }
    merged.daily[listId] = target;
  }

  for (const [listId, rows] of Object.entries(snapshot.subscribers ?? {})) {
    const target = { ...(merged.subscribers[listId] ?? {}) };
    for (const row of rows) target[row.date] = row.subscribers;
    merged.subscribers[listId] = target;
  }

  merged.updatedAt = snapshot.collectedAt ?? merged.updatedAt;
  return merged;
}

/**
 * Dopočítá nové přihlášky. Mailer je nikde neeviduje, ale platí:
 *   noví ≈ (odběratelů dnes − odběratelů minule) + odhlášení mezitím
 * Funguje jen mezi dny, kdy známe počet odběratelů; jinak vrací null.
 */
export function deriveSignups(subscribersByDate, unsubscribedByDate) {
  const dates = Object.keys(subscribersByDate ?? {}).sort();
  const result = {};

  for (let i = 1; i < dates.length; i += 1) {
    const previous = dates[i - 1];
    const current = dates[i];
    const delta = subscribersByDate[current] - subscribersByDate[previous];

    let unsubscribed = 0;
    for (const [date, count] of Object.entries(unsubscribedByDate ?? {})) {
      if (date > previous && date <= current) unsubscribed += count;
    }

    result[current] = {
      from: previous,
      unsubscribed,
      signups: Math.max(0, delta + unsubscribed),
      net: delta,
      // víc než den = odhad rozpočítaný na delší interval, ať to dashboard umí označit
      spanDays: daysBetween(previous, current),
    };
  }

  return result;
}

export function daysBetween(fromDate, toDate) {
  const from = Date.parse(`${fromDate}T00:00:00Z`);
  const to = Date.parse(`${toDate}T00:00:00Z`);
  if (!Number.isFinite(from) || !Number.isFinite(to)) return null;
  return Math.round((to - from) / 86400000);
}
