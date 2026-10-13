import json

rows = [
["VESTÍBULO","1.1","PERCHERO","Perchero Gaillech","NUEVO","1","0.63","0.11","0.07","KAVE","https://kavehome.com/es/es/p/perchero-gaillech-de-madera-maciza-de-teca","19.99"],
["","1.2","MUEBLE BAJO","Mueble vintage para vinilos 113 cm Ronda, nogal","NUEVO","1","1.13","0.48","1.02","LA REDOUTE INTERIEURS","https://www.laredoute.es/ppdp/prod-350269827.aspx","343.20"],
["COMEDOR","2.1","MESA COMEDOR","Mesa Core 140","NUEVO","1","2.30","0.90","0.75","MARLOT BAUS","https://marlotbaus.com/en/products/core-dining-table","1599.00"],
["","2.2","LÁMPARA COMEDOR","Frisbi","EXISTENTE","1","1.18","0.76","1.14","FLOS","https://www.muebleslluesma.com/lamparas-colgantes/15680-lampara-suspension-frisbi-flos.html",""],
["","2.3","MUEBLE BAJO","Aparador metálico modular Steel blanco","NUEVO","1","1.53","0.38","0.75","SINGULAR MARKET","https://www.singularmarket.com/vitrinas-alacenas-y-armarios-de-diseno/1878-aparador-metalico-modular-steel-blanco.html","999.99"],
["","2.5","SILLA COMEDOR","Silla de madera de roble Jane","NUEVO","6","0.48","0.50","0.81","NORTHDECO","https://northdeco.com/collections/sillas-de-madera/products/silla-de-madera-jane?variant=56712562901378","99.00"],
["","2.6","ESTOR","Estor plegable translúcido Namib lino 216x246","NUEVO","1","2.16","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd","335.41"],
["","2.7","ESPEJO","Espejo de pie efecto envejecido","NUEVO","1","0.90","0.02","1.50","ZARA HOME","https://www.zarahome.com/es/espejo-pie-efecto-envejecido-l42349106?colorId=817","279.00"],
["SALON","3.1","ALFOMBRA SALÓN","Alfombra Line","NUEVO","1","2.00","3.00","0.00","TOM DIXON","https://www.nordicnest.es/marcas/tom-dixon/alfombra-line/?variantId=642048-01","409.00"],
["","3.2","BUTACAS","Silla de caña negra Thisted","NUEVO","2","0.66","0.74","0.74","PIB","https://www.pib.eu/ES-es/silla-de-cana-negra-thisted--0642998","370.00"],
["","3.3","MESA DE CENTRO","Mesa de centro existente","EXISTENTE","1","1.10","0.60","0.43","","",""],
["","3.4","LÁMPARA SALÓN","Pantalla Paper Shade elipse","NUEVO","1","0.70","0.70","0.48","HAY","https://www.nordicnest.es/marcas/hay/pantalla-de-lampara-rice-paper-elipse/","65.00"],
["","3.5","BOMBILLA INTELIGENTE","Bombilla inteligente LED E27","NUEVO","1","","","","LEROY MERLIN","https://www.leroymerlin.es/productos/bombilla-inteligente-led-e27-rgb-de-9-w-con-wifi-y-control-remoto-por-aplicacion-compatible-con-alexa-y-google-assistant-76802430.html","19.99"],
["","3.6","MESA AUXILIAR","Tranered mesa auxiliar, negro","NUEVO","1","0.44","0.44","0.75","IKEA","https://www.ikea.com/es/es/p/tranered-mesa-auxiliar-negro-30609001/","79.99"],
["","3.8","LÁMPARA DE MESA","Bella, réplica Nesso","NUEVO","1","0.32","0.32","0.22","VIBE HAUS","https://vibehausliving.com/es/products/bella-nesso-replica-lampara","70.95"],
["","3.9","MÓVIL PARA TV","Moon TV","NUEVO","1","0.93","0.99","1.10","PEDESTAL","https://es.pedestal.com/products/moon-rollin-charcoal","340.00"],
["","3.10","SOFÁ","Sofá chaise longue existente","EXISTENTE","1","2.77","1.58","0.90","","",""],
["","3.11","MESA AUXILIAR SOFÁ","Mesa auxiliar Aluret, mármol verde","NUEVO","1","0.35","0.35","0.50","SKLUM","https://www.sklum.com/es/comprar-mesas-bajas-y-auxiliares/207192-mesa-auxiliar-cuadrada-35x35-cm-en-mdf-y-piedra-natural-aluret.html?id_c=685390","154.95"],
["","3.12","MUEBLE TOCADISCOS","Mueble para vinilos 51 cm Ronda","NUEVO","1","0.51","0.48","0.81","LA REDOUTE INTERIEURS","https://www.laredoute.es/ppdp/prod-350269828.aspx","152.15"],
["","3.13","ESTOR VENTANA","Estor plegable translúcido Namib lino 216x246","NUEVO","1","2.16","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd","335.41"],
["","3.14","ESTOR TERRAZA","Estor plegable translúcido Namib lino 216x246","NUEVO","1","2.16","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd","335.41"],
["ESTUDIO","4.1","SILLÓN","Sillón Togo negro","NUEVO","2","","","","SINGULAR MARKET","https://www.singularmarket.com/sillones-y-butacas-de-diseno/1701-sillon-togo-negro.html","450.00"],
["","4.4","ALFOMBRA ESTUDIO","Alfombra Empuries verde 160x230","NUEVO","1","1.60","2.30","0.00","KAVE","","199.00"],
["","4.5","PLAFÓN","Plafón de porcelana Dani","NUEVO","1","0.10","0.10","0.12","ZANGRA","https://zangra.com/es_ES/products/aplique-plafon-porcelana-marron-dani-g9-ip54-pantalla-luz-vidrio","50.00"],
["","4.7","SILLA ESCRITORIO","Think","EXISTENTE","1","0.74","0.58","0.98","STEELCASE","https://es.steelcase.com/products/think?variant=41727594463430",""],
["","4.8","ESCRITORIO","Escritorio existente","EXISTENTE","1","1.40","0.77","0.90","","https://www.ikea.com/es/es/p/nackanas-mesa-acacia-40511056/",""],
["","4.9","SILLAS","Sandsberg","EXISTENTE","4","0.48","0.43","0.78","IKEA","https://www.ikea.com/es/es/p/sandsberg-silla-marron-rojizo-60605426/",""],
["","4.10","MESA DE CENTRO","Mesa de centro redonda Fleksa","NUEVO","1","0.72","0.72","0.36","KAVE","https://kavehome.com/es/es/p/mesa-de-centro-redonda-fleksa-de-metal-mostaza-o-72-cm","199.00"],
["","4.11","ESTOR","Estor plegable translúcido Namib lino 218x246","NUEVO","1","2.18","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd",""],
["DORMITORIO","5.1","APLIQUE PARED","Aplique LED circular luz indirecta","NUEVO","2","0.25","0.00","0.25","ILUMINIA","https://www.ilumnia.es/productos-led/1134-3399-aplique-pared-led-12w-circular-luz-indirecta-aluminio.html","49.90"],
["","5.2","MESA DE NOCHE","Mesita de noche Shantay","NUEVO","2","0.35","0.40","0.50","KAVE","https://kavehome.com/es/es/p/mesita-de-noche-shantay-acero-con-acabado-negro-40-x-50-cm","159.00"],
["","5.3","MUEBLE BAJO","Mueble TV Shantay","NUEVO","1","1.50","0.35","0.50","KAVE","https://kavehome.com/es/es/p/mueble-tv-shantay-1-puerta-y-1-cajon-de-metal-con-acabado-pintado-negro-150-x-50-cm","399.00"],
["","5.4","ESTOR DORMITORIO","Estor plegable translúcido Namib lino 158x246","NUEVO","1","1.58","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd",""],
["","5.5","ESTOR DORMITORIO 2","Estor plegable translúcido Namib lino 208x246","NUEVO","1","2.08","0.07","2.46","KAATEN","https://kaaten.com/products/estor-plegable-translucido-namib-lino-amd",""],
["TERRAZA","6.1","MESA EXTERIOR","Mesa de exterior cuadrada 70x70 Zoilo","NUEVO","1","0.70","0.70","0.73","THE MASIE","https://www.themasie.com/es/comprar-mesas-de-exterior/241712-mesa-de-exterior-cuadrada-70x70-cm-de-metal-zoilo.html","119.95"],
]

room_map = {"VESTÍBULO": "ENTRADA", "COMEDOR": "COMEDOR", "SALON": "SALÓN",
            "ESTUDIO": "ESTUDIO", "DORMITORIO": "DORMITORIO", "TERRAZA": "TERRAZA"}
items, amb = [], ""
for r in rows:
    amb = r[0] or amb
    dims = r[6:9]
    items.append({
        "room": room_map[amb], "code": r[1], "item": r[2], "name": r[3], "estado": r[4],
        "cant": int(r[5] or 1), "dims": dims if any(dims) else None, "tienda": r[9],
        "url": r[10], "precio": float(r[11] or 0),
        # alternativas: [{"id","label","name","tienda","url","precio","model"}]; la base es la opción "actual"
        "options": [],
    })

# alternativas por código (la fila del spreadsheet es siempre la opción "actual")
OPTIONS = {
    "2.1": [{"id": "namara", "label": "Namara", "name": "Mesa redonda Namara Ø140, cemento beige", "tienda": "SKLUM",
             "url": "https://www.sklum.com/es/comprar-mesas-comedor/184223-mesa-de-comedor-redonda-en-cemento-namara.html?id_c=527312",
             "precio": 749.95, "dims": ["1.40", "1.40", "0.76"], "img": "2.1-namara"}],
    "2.3": [{"id": "doric", "label": "Doric", "name": "Aparador Doric 3P3C blanco", "tienda": "TEULAT",
             "url": "https://www.mobler.es/teulat/aparador-doric-3p3c/",
             "precio": 804, "dims": ["1.48", "0.48", "0.70"], "img": "2.3-doric"},
            {"id": "punto", "label": "Punto · otra pared", "name": "Auxiliar Punto 2P4C blanco, en la otra pared (espejo vertical)",
             "tienda": "TEULAT", "url": "https://www.mobler.es/teulat/auxiliar-punto-2p4c/",
             "precio": 600, "dims": ["0.93", "0.45", "1.30"], "img": "2.3-punto"}],
}
for it in items:
    it["options"] = OPTIONS.get(it["code"], [])

data = {"rooms": ["ENTRADA", "COMEDOR", "SALÓN", "ESTUDIO", "DORMITORIO", "TERRAZA"], "items": items}
with open("D:/Website/portfolio/public/goya58/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(len(items), round(sum(i["precio"] * i["cant"] for i in items), 2))
