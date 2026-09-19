const CACHE = "mapea-españa-madrid-carabanchel-94da1e08c5";
const ASSETS = ["./", "./index.html", "./manifest.webmanifest", "./apple-touch-icon.png",
                "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // La pagina, siempre de la red: con cache-primero un cambio no se veia hasta
  // la SEGUNDA recarga. La cache solo entra si no hay conexion.
  if (e.request.mode === "navigate") {
    // cache:"reload" salta la cache HTTP del navegador. GitHub Pages sirve el
    // index con max-age=600, asi que sin esto una recarga dentro de los diez
    // minutos siguientes devolvia la version anterior aunque pidieramos red.
    e.respondWith(
      fetch(new Request(e.request.url, {cache: "reload", credentials: "same-origin"}))
        .then(r => {
        if (r && r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        return r;
      }).catch(() => caches.match("./index.html", {ignoreSearch: true}))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request, {ignoreSearch: true}).then(hit => {
      if (hit) {
        fetch(e.request).then(r => {
          if (r && r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        }).catch(() => {});
        return hit;
      }
      return fetch(e.request).catch(() => caches.match("./index.html"));
    })
  );
});
