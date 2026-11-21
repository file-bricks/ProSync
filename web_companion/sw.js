const CACHE_NAME = "prosync-web-companion-v3";
// Inhalts-Hash aller APP_SHELL-Dateien inkl. Manifest und Icons (web_companion/tests/sw_asset_hash.test.mjs prueft ihn):
// aendert sich eine davon, CACHE_NAME erhoehen, sonst behalten installierte PWAs den alten Code.
const ASSET_HASH = '356dcace9f48'; // eslint-disable-line no-unused-vars
const APP_SHELL = [
  "./",
  "./index.html",
  "./app.css",
  "./app.js",
  "./library.js",
  "./manifest.webmanifest",
  "./icon.svg",
  "./apple-touch-icon-180.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key)),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }

  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });
        return response;
      });
    }).catch(() => new Response("Offline", { status: 503, statusText: "Service Unavailable" })),
  );
});
