/** Kde leží lokální data (mimo Git) a jak se čtou/zapisují. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));

export function appDir() {
  return path.resolve(here, "..");
}

export function dataDir() {
  return process.env.NEWSLETTERY_DATA_DIR
    ? path.resolve(process.env.NEWSLETTERY_DATA_DIR)
    : path.join(appDir(), "data");
}

export function historyPath() {
  return path.join(dataDir(), "history.json");
}

export function dashboardDataPath() {
  return path.join(appDir(), "dashboard", "data.json");
}

export function readHistory() {
  const file = historyPath();
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

export function writeHistory(history) {
  fs.mkdirSync(dataDir(), { recursive: true });
  fs.writeFileSync(historyPath(), `${JSON.stringify(history, null, 2)}\n`);
}

/** Dnešní datum v Praze ve tvaru YYYY-MM-DD. */
export function today(now = new Date()) {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Prague" }).format(now);
}
