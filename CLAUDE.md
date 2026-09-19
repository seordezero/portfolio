# MAPEA App — reglas de ESTE proyecto

Solo de MAPEA. No son preferencias generales del usuario ni valen para otros
proyectos: este fichero se lee unicamente cuando se trabaja en `D:\Website`, que
hoy es donde vive MAPEA. Para cualquier otra cosa, ignorar.

Si algo de aqui choca con lo que pida el usuario en el momento, manda el usuario;
pero no se puede olvidar sin decirlo.

Contexto y visión: `portfolio/docs/mapea-brief.md`.

---

## Reglas duras de interfaz

**NADA SE DESPLAZA.** El armazón de cada página — portada, navegador, comparador
y cabida — cabe en la ventana. Siempre, en cualquier formato. Lo único que puede
desplazarse es el **contenido de un panel, por dentro**: los resultados y los
guardados del navegador, los parámetros, y la columna de fichas de la cabida en
el teléfono en vertical. La página nunca.

Corolario: cuando algo no cabe, el sitio sale de otro panel, no de la regla. En
la cabida el dibujo manda y las fichas se desplazan por dentro; en el navegador
en vertical el visor es un cuadrado centrado (`1fr / 100vw / 1fr`) y los dos
paneles se reparten el resto y se desplazan por dentro.

**Y el documento se clava.** `height:100dvh` en el contenedor NO basta: la caja
encaja pero el documento sigue siendo desplazable, y en un teléfono eso ya es el
fallo — el navegador deja arrastrar la página para plegar su barra. El `body` va
`position:fixed; inset:0; overflow:hidden` y el `html` con `height:100%;
overflow:hidden`. Al imprimir se sueltan los dos, que la hoja necesita fluir.

Comprobación antes de dar algo por hecho, con la página abierta:

```js
document.documentElement.scrollWidth + "/" + innerWidth + "  " +
document.documentElement.scrollHeight + "/" + innerHeight
```

Los dos pares tienen que ser iguales. Un scroll horizontal no es un aviso de que
hay mucho contenido: es un fallo.

**Colores reservados.** La gama de crema (`#E4DBC6`) a índigo (`#1B54E0`) es de
la interfaz y de los mapas de calor. No se reparte nunca entre lotes. El amarillo
`#FFF200` es solo de la selección. La paleta de lotes evita los tres.

**La esquina superior derecha es la misma en las tres páginas:** sesión, salir, y
los botones de la página. Flotando, sin barra que los sostenga.

---

## Los 12 valores por lote

Son los únicos. No se añaden campos "por si acaso"; si entra uno nuevo, sale otro.

| grupo | valores |
|---|---|
| Oficial | Área · Zonificación · Plantas construidas · Plantas permitidas · Restricción |
| Externo | En venta |
| Predictivo | Valor estimado por m² · Potencial |
| Urbano | Exposición natural · Servicios · Vida social · Movilidad ligera |

La referencia catastral y la dirección son identidad, no valores.

**Los cuatro índices urbanos son lo que diferencia a MAPEA.** Cada uno lleva su
página de definición: qué entra, con qué umbral, y dónde falla.

---

## Rentabilidad

**Qué mide:** cuánto más puede valer el lote dentro de **5 años**, en % sobre el
capital que hay que poner hoy (compra + obra). Horizonte fijo e igual para todos:
un porcentaje sin periodo no significa nada.

```
inversión = compra + obra nueva + reforma
futuro    = (valor + lo que añade la obra + lo que añade la reforma)
            × (1 + subida anual)^5 × (1 − lastre fuera de ordenación)
rentab.   = (futuro − inversión) ÷ inversión × 100
```

**Mercado.** Base **3,5 %/año** (media de ciclo largo en Madrid), que el sitio
mueve **±1,5 pp** según los cuatro índices, ancla en 50. El +15/+20 % interanual
de Carabanchel en 2026 es un año caliente, no una serie.

**Construir.** Cada m² levantado aporta `valor − coste`, no su precio de venta.
Donde la norma permite más de lo que el mercado paga, construir **resta**. Obra
nueva Madrid 2026: **2.100 €/m²** (ejecución 1.750–1.950 + 8–15 % de licencias,
proyecto y dirección). Del potencial se descuenta lo que no se sabe: normativa
pendiente 60 %, restricción sin determinar 80 %, fuera de ordenación 0 % y −15 %
al valor futuro.

**Reformar.** Plusvalía hasta **35 %** (un piso reformado frente a uno «para
reformar»), proporcional a la edad: nula bajo 10 años, plena a partir de 70. Y
**solo si compensa**: si la plusvalía por m² no llega a los **800 €/m²** de una
reforma integral de gama media, no se reforma. El corte cae en los edificios
anteriores a los setenta.

**Distribución en Carabanchel** (9.979 lotes, 1.347 sin valor por m²):
mediana **+31,5 % a 5 años** (5,6 %/año) · q10 19,9 · q25 24,6 · q75 38,8 ·
q90 49,8 · máx 145,8 · **9 negativos** · ninguno exactamente 0. 6.009 lotes
(60 %) entran en el supuesto de reforma.

Va en euros corrientes, sin descontar inflación. **El eje del gráfico va clavado
de 0 a 100**, con la raya del 50: es un porcentaje, y con la escala abierta a los
datos la misma barra cambiaba de altura según con quién se comparara. Por encima
de 100 la barra llega arriba; un negativo se dibuja a cero, en rojo, con su cifra.

Los coeficientes viven en `RET` dentro de `logic.js`, una ciudad puede pisarlos
desde `C.retorno`, y están escritos íntegros en la ficha que abre la «i» del
gráfico. Son un **borrador con criterio de mercado**, no una calibración contra
ventas reales: cuando haya serie de transacciones cambian los números, no la
forma.

## En venta: la extensión

Rascar los portales choca con sus condiciones y, sobre todo, con el cruce: un
anuncio de particular no publica el número de la calle. Al revés sí funciona, y
la **extensión de navegador es la única puerta** — en la app no hay botón de
«marcar en venta», porque eso era pedirle al usuario que repitiera un trabajo
que la extensión ya ha hecho.

La extensión corre **dentro** de la página del anuncio, que es el único sitio
desde el que se puede leer: al servidor le devuelve 403 y al navegador se lo
impide CORS. Los guiones de contenido están además exentos de la CSP del portal,
que es lo que tumbaba al marcador.

- Un lector por portal (idealista, fotocasa) y, para los demás, los datos
  estructurados de schema.org.
- La zona se reconoce por **distrito o por barrio**: fotocasa no dice
  «Carabanchel», dice «Comillas». La tabla sale de `CIUDADES` más los barrios.
- Zona no cubierta → lo dice en la propia página, no abre un mapa inútil.

Al llegar a MAPEA, el anuncio **se guarda solo**: en `localStorage` siempre —es
igual de «mi data» y hace que funcione sin servidor— y además en Supabase si hay
sesión, y entonces lo ve todo el mundo. El pin va en el centro de la parcela, que
es lo más cerca que se puede estar sin inventarse un número que el portal no
publica.

**Un anuncio marca que algo está en venta y NADA MÁS.** No entra en el valor por
m² ni en la rentabilidad. Un precio pedido no es un precio pagado: el valor se
apoya en ventas consumadas, y los módulos del Catastro —calculados con todas las
compraventas ante notario— son la fuente para eso, no los portales.

## Reglas de los índices

- **Escala absoluta 0–100**, nunca relativa al distrito. Un 80 significa lo mismo
  en Carabanchel que en Barranco. Un barrio malo tiene que verse malo.
- **Umbrales que saturan**, no densidades abiertas. Con tope, una fuente rica y
  una pobre coinciden; sin tope, se acaba midiendo el dato en vez de la ciudad.
- **El anclaje se justifica fuera del dato** (norma citable o criterio explícito),
  nunca con el percentil del propio distrito: eso es escala relativa disfrazada.
- **Todo sale de OpenStreetMap.** El dato municipal afina posiciones, no añade
  categorías, o se rompe la comparación entre ciudades.

---

## Datos y arquitectura

- La app es **una sola base de código**. `logic.js` y `shell.html` no nombran
  ninguna ciudad. Todo lo que cambia entre ciudades vive en `DATOS.cfg` y en
  `CIUDADES` de `publicar_mapea.py`. Si hay que tocar `logic.js` para añadir una
  ciudad o un índice, el diseño está mal.
- Ciudades: `peru-lima-barranco` (EPSG:32718) y `españa-madrid-carabanchel`
  (EPSG:25830). El `id` interno de Carabanchel sigue siendo
  `spain-madrid-carabanchel`: es la clave de localStorage y renombrarlo borraría
  lo guardado de los usuarios.
- Scripts en `J:\My Drive\00_Proyectos\12_MAPEA APP\SCRIPTS`. La web en
  `D:\Website\portfolio` (ese es el repo git; `D:\Website` no lo es).
- Publicar: `py -3 publicar_mapea.py`, luego commit y push en `portfolio`.
  GitHub Pages reconstruye solo.

### Trampas ya pisadas, no repetir

- **GeoPackage:** los `UPDATE` sobre una capa con geometría NO se pueden hacer con
  `sqlite3` pelado — hay disparadores que llaman a `ST_IsEmpty`, que solo existe
  si abre GDAL. Van por `ogrinfo -sql`, y una sentencia por llamada.
- **Alturas:** comparar plantas a cornisa con las totales del Catastro daba un 60 %
  de edificios "ilegales". Se comparan totales con totales (`PISOS_ACT` contra
  `PISOS_TOP`). Prueba de cordura: los que exceden deben ser mayoritariamente
  anteriores a 1997.
- **No saber no es cero.** 1.998 parcelas sin altura permitida fijada quedan en
  blanco, no en "libre".
- **Overpass** exige un User-Agent que nombre el programa; con uno de navegador
  contesta 406. El portal del BOE al revés: falla si le mandas `sort_field`.
- **Service worker:** el HTML va a red primero y con `cache:"reload"`. El registro
  usa ruta absoluta, porque en `/compara/` un `sw.js` relativo da 404 y deja la
  página clavada en una versión vieja para siempre.
- **QGIS:** `reloadData()` refresca filas pero no el esquema. Si el gpkg tiene
  columnas nuevas hay que quitar y volver a poner la capa.
- **La Y se invierte.** El lienzo crece hacia abajo y la Y del CRS crece hacia
  el norte. El mapa 2D lo hace en `sy()`; la axonometría de la cabida no lo
  hacía y salía en espejo, con el norte abajo. Se invierte UNA vez, al armar
  el paquete, y todo lo de abajo queda coherente.
- **Las dos anclas.** La marca (arriba a la izquierda) y el círculo de sesión
  (arriba a la derecha) comparten centro vertical en las cuatro páginas: 28 px
  en pantalla normal, 18 px en apaisado de teléfono. Se leen como pareja.
- **La portada Y la plantilla de la aplicación** se componen con formato `%`: un
  `%` literal en su CSS o su JavaScript hay que doblarlo (`100%%`), o sacar el
  dato del DOM. Solo la de la cabida usa `.replace()`. Y `publicar_mapea.py`
  nunca se ejecuta con la salida de error silenciada: un fallo de formato deja
  el sitio publicado en la versión anterior sin decir nada.
- No abrir instancias nuevas de QGIS; trabajar sobre la que el usuario tenga
  abierta.

---

## Cómo trabajar con Sebastián

Respuestas cortas y al grano. Nada de respuestas largas de varias secciones.
Cuando algo no se puede hacer con el dato que hay, decirlo y no rellenarlo.
