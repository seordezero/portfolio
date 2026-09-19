/* MAPEA - el anuncio, en el mapa.
   Corre DENTRO de la pagina del anuncio, que es el unico sitio desde el que se
   puede leer: al servidor le devuelve 403 y al navegador se lo impide CORS.

   Cada portal escribe la direccion a su manera, asi que hay un lector por
   portal y, para los demas, los datos estructurados de schema.org, que muchos
   publican. La zona se reconoce por distrito O por barrio: fotocasa no dice
   "Carabanchel", dice "Comillas". */
(function () {
  var SITIO = "https://sebastianortizdezevallos.com/mapea-app/";
  var ZONAS = {"barranco": "peru-lima-barranco", "carabanchel": "españa-madrid-carabanchel", "comillas": "españa-madrid-carabanchel", "opanel": "españa-madrid-carabanchel", "san isidro": "españa-madrid-carabanchel", "vista alegre": "españa-madrid-carabanchel", "puerta bonita": "españa-madrid-carabanchel", "buenavista": "españa-madrid-carabanchel", "abrantes": "españa-madrid-carabanchel"};

  function T(s) { var e = document.querySelector(s); return e ? e.innerText.trim() : ""; }
  function L(s) {
    return Array.prototype.map.call(document.querySelectorAll(s),
      function (e) { return e.innerText.trim(); });
  }
  function N(t) { return (t || "").replace(/[^0-9]/g, ""); }
  function llano(t) {
    return (t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .toLowerCase().trim();
  }
  function tipoDe(h1) {
    var m = (h1 || "").match(/^(.+?)\s+en\s+(?:venta|alquiler)\s+en\s+(.+)$/i);
    return m ? {tipo: m[1], dir: m[2]} : {tipo: "", dir: ""};
  }

  /* idealista: la lista del cabecero del mapa es la fuente limpia. Calle con
     numero, barrio, distrito y municipio, cada uno en su linea. */
  function leerIdealista() {
    var l = L("#headerMap li"), dir = l[0] || "", dist = "", barrio = "";
    l.forEach(function (x) {
      if (/^Distrito /i.test(x)) dist = x.slice(9);
      if (/^Barrio /i.test(x)) barrio = x.slice(7);
    });
    var t = tipoDe(T("h1"));
    if (!dir) dir = t.dir;
    var sup = "";
    L(".info-features span").forEach(function (x) {
      if (!sup && /m\u00b2/.test(x)) sup = N(x);
    });
    return {dir: dir, dist: dist, barrio: barrio, tipo: t.tipo,
            precio: N(T(".info-data-price")), m2: sup};
  }

  /* fotocasa: el h1 da calle y barrio -casi nunca el numero-, y las migas de pan
     dan el municipio. El distrito no aparece: se deduce del barrio. */
  function leerFotocasa() {
    var t = tipoDe(T("h1"));
    var trozos = t.dir.split(",").map(function (x) { return x.trim(); });
    var sup = "";
    L("[class*='features'] span, [class*='Features'] span").forEach(function (x) {
      if (!sup && /m\u00b2/.test(x)) sup = N(x);
    });
    return {dir: trozos[0] || "", dist: "", barrio: trozos[1] || "",
            tipo: t.tipo, precio: N(T("[class*='price']")), m2: sup};
  }

  /* Cualquier otro portal que publique schema.org. No siempre trae el numero,
     pero trae calle y barrio, que es con lo que se puede trabajar. */
  function leerEstructurado() {
    var out = {dir: "", dist: "", barrio: "", tipo: "", precio: "", m2: ""};
    L("script[type='application/ld+json']");
    var nodos = document.querySelectorAll("script[type='application/ld+json']");
    for (var i = 0; i < nodos.length; i++) {
      var d;
      try { d = JSON.parse(nodos[i].textContent); } catch (e) { continue; }
      var arr = [].concat(d, d && d["@graph"] ? d["@graph"] : []);
      for (var k = 0; k < arr.length; k++) {
        var o = arr[k];
        if (!o || !o.address) continue;
        out.dir = o.address.streetAddress || "";
        out.barrio = o.address.addressLocality || "";
        if (o.offers && o.offers.price) out.precio = N(String(o.offers.price));
        break;
      }
    }
    if (!out.dir) { var t = tipoDe(T("h1")); out.dir = t.dir; out.tipo = t.tipo; }
    return out;
  }

  var LECTORES = [
    [/(^|\.)idealista\.com$/, leerIdealista],
    [/(^|\.)fotocasa\.es$/, leerFotocasa]
  ];
  function leer() {
    for (var i = 0; i < LECTORES.length; i++) {
      if (LECTORES[i][0].test(location.hostname)) return LECTORES[i][1]();
    }
    return leerEstructurado();
  }

  // el distrito manda; si el portal no lo da, se prueba con el barrio
  function ciudadDe(d) {
    return ZONAS[llano(d.dist)] || ZONAS[llano(d.barrio)] || null;
  }

  function destino(d, slug) {
    return SITIO + encodeURIComponent(slug) + "/?anuncio=" +
      encodeURIComponent(location.href) +
      "&dir=" + encodeURIComponent(d.dir) +
      "&tipo=" + encodeURIComponent(d.tipo) +
      "&dist=" + encodeURIComponent(d.dist || d.barrio) +
      "&barrio=" + encodeURIComponent(d.barrio) +
      "&precio=" + d.precio + "&m2=" + d.m2 +
      "&t=" + encodeURIComponent(document.title);
  }

  function pinta(texto, color, alPulsar) {
    if (document.getElementById("mapea-boton")) return;
    var b = document.createElement("button");
    b.id = "mapea-boton";
    b.type = "button";
    b.textContent = texto;
    b.setAttribute("style", [
      "position:fixed", "right:18px", "bottom:18px", "z-index:2147483647",
      "padding:11px 16px", "border:0", "border-radius:22px",
      "background:" + color, "color:#EAE4D9",
      "font:600 14px/1 system-ui,sans-serif",
      alPulsar ? "cursor:pointer" : "cursor:default",
      "box-shadow:0 4px 14px rgba(0,0,0,.35)", "max-width:280px",
      "text-align:left", "line-height:1.35"
    ].join(";"));
    if (alPulsar) b.addEventListener("click", alPulsar);
    document.body.appendChild(b);
  }

  function arranca() {
    var d = leer();
    if (!d.dir && !d.barrio && !d.dist) return;   // no parece un anuncio
    var slug = ciudadDe(d);
    if (!slug) {
      pinta("MAPEA todav\u00eda no ha desarrollado esta zona", "#3A3A3A", null);
      return;
    }
    pinta("Ver el lote en MAPEA", "#1B54E0", function () {
      window.open(destino(d, slug), "_blank");
    });
  }

  arranca();
  /* Los portales cambian de anuncio sin recargar la pagina: si cambia la
     direccion, se vuelve a mirar. */
  var ultima = location.href;
  setInterval(function () {
    if (location.href === ultima) return;
    ultima = location.href;
    var v = document.getElementById("mapea-boton");
    if (v) v.remove();
    setTimeout(arranca, 900);
  }, 1000);
})();
