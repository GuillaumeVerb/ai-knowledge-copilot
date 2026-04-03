import { createReadStream, existsSync, readFileSync } from "node:fs";
import { stat } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.join(__dirname, "dist");
const indexPath = path.join(distDir, "index.html");
const host = "0.0.0.0";
const port = Number.parseInt(process.env.PORT || "4173", 10);
const runtimeConfig = {
  apiBaseUrl: process.env.VITE_API_BASE_URL || "",
};

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

function safePathname(url) {
  const pathname = new URL(url, "http://localhost").pathname;
  const normalized = path.normalize(decodeURIComponent(pathname)).replace(/^(\.\.[/\\])+/, "");
  return normalized === path.sep ? "/index.html" : normalized;
}

function sendFile(response, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  response.writeHead(200, { "Content-Type": contentTypes[ext] || "application/octet-stream" });
  createReadStream(filePath).pipe(response);
}

function sendIndex(response) {
  const html = readFileSync(indexPath, "utf-8");
  const injectedConfig = `<script>window.__APP_CONFIG__ = ${JSON.stringify(runtimeConfig)};</script>`;
  const payload = html.includes("</head>")
    ? html.replace("</head>", `${injectedConfig}</head>`)
    : `${injectedConfig}${html}`;
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(payload);
}

const server = http.createServer(async (request, response) => {
  const pathname = safePathname(request.url || "/");
  const requestedPath = path.join(distDir, pathname.replace(/^[/\\]+/, ""));

  try {
    const fileStats = await stat(requestedPath);
    if (fileStats.isFile()) {
      sendFile(response, requestedPath);
      return;
    }
  } catch {}

  if (!existsSync(indexPath)) {
    response.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Frontend build artifacts are missing.");
    return;
  }

  sendIndex(response);
});

server.listen(port, host, () => {
  console.log(`Static frontend listening on http://${host}:${port}`);
});
