#!/usr/bin/env node
/**
 * Mini server pro lokální dashboard: servíruje apps/newslettery/dashboard.
 *   node apps/newslettery/src/serve.js   → http://localhost:8732/
 */

import fs from "node:fs";
import http from "node:http";
import path from "node:path";

import { appDir } from "./storage.js";

const ROOT = path.join(appDir(), "dashboard");
const PORT = Number(process.env.PORT ?? 8732);
const TYPES = { ".html": "text/html; charset=utf-8", ".json": "application/json; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".svg": "image/svg+xml" };

http
  .createServer((request, response) => {
    const urlPath = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    const file = path.join(ROOT, urlPath === "/" ? "index.html" : urlPath);

    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
      response.end("Nenalezeno");
      return;
    }

    response.writeHead(200, { "content-type": TYPES[path.extname(file)] ?? "application/octet-stream" });
    fs.createReadStream(file).pipe(response);
  })
  .listen(PORT, () => process.stdout.write(`Dashboard běží na http://localhost:${PORT}/\n`));
