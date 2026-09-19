/* MAPEA - boton en el anuncio.
   Corre DENTRO de la pagina del anuncio, que es el unico sitio desde el que se
   puede leer: al servidor le devuelve 403 y al navegador se lo impide CORS.
   Lee lo que el anuncio ya ensena y abre el lote en MAPEA. */
(function () {
  var SITIO = "https://sebastianortizdezevallos.com/mapea-app/";
  var DISTRITOS = {"Barranco": "peru-lima-barranco", "Carabanchel": "españa-madrid-carabanchel"};

  function T(s) { var e = document.querySelector(s); return e ? e.innerText.trim() : ""; }
  function L(s) {
    return Array.prototype.map.call(document.querySelectorAll(s),
      function (e) { return e.innerText.trim(); });
  }
  function N(t) { return (t || "").replace(/[^0-9]/g, ""); }

  function leer() {
    /* La lista del cabecero del mapa es la fuente limpia: calle con numero,
       barrio, distrito y municipio, cada uno en su linea. El h1 es el plan B. */
    var l = L("#headerMap li"), dir = l[0] || "", dist = "", barrio = "";
    l.forEach(function (x) {
      if (/^Distrito /i.test(x)) dist = x.slice(9);
      if (/^Barrio /i.test(x)) barrio = x.slice(7);
    });
    var h1 = T("h1");
    var m = h1.match(/^(.+?)\s+en\s+(?:venta|alquiler)\s+en\s+(.+)$/i);
    if (!dir && m) dir = m[2];
    var sup = "";
    L(".info-features span").forEach(function (x) {
      if (!sup && /m\u00b2/.test(x)) sup = N(x);
    });
    return {
      dir: dir, dist: dist, barrio: barrio,
      tipo: m ? m[1] : "",
      precio: N(T(".info-data-price")),
      m2: sup
    };
  }

  function destino() {
    var d = leer();
    var slug = DISTRITOS[d.dist];
    // sin distrito conocido se abre la portada: alli elige el usuario el mapa
    var base = SITIO + (slug ? encodeURIComponent(slug) + "/" : "");
    return base + "?anuncio=" + encodeURIComponent(location.href) +
      "&dir=" + encodeURIComponent(d.dir) +
      "&tipo=" + encodeURIComponent(d.tipo) +
      "&dist=" + encodeURIComponent(d.dist) +
      "&barrio=" + encodeURIComponent(d.barrio) +
      "&precio=" + d.precio + "&m2=" + d.m2 +
      "&t=" + encodeURIComponent(document.title);
  }

  if (document.getElementById("mapea-boton")) return;
  var b = document.createElement("button");
  b.id = "mapea-boton";
  b.type = "button";
  b.textContent = "Ver el lote en MAPEA";
  b.setAttribute("style", [
    "position:fixed", "right:18px", "bottom:18px", "z-index:2147483647",
    "padding:11px 16px", "border:0", "border-radius:22px",
    "background:#1B54E0", "color:#EAE4D9",
    "font:600 14px/1 Archivo,system-ui,sans-serif", "cursor:pointer",
    "box-shadow:0 4px 14px rgba(0,0,0,.35)"
  ].join(";"));
  b.addEventListener("click", function () { window.open(destino(), "_blank"); });
  document.body.appendChild(b);
})();
