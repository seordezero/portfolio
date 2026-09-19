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

## Retorno estimado

No es solo lo que queda por construir. Tres sumandos, y puede ser **negativo**:

```
margen  = (venta − obra) ÷ (valor actual + obra) × 100
          venta = potencial×valor_m² + construido×valor_m²×plusvalía_reforma
          obra  = potencial×coste   + construido×coste×0,30
prima   = (media de los 4 índices ÷ 100 − 0,5) × 14        puntos
ajustes = −4 normativa pendiente · −9 fuera de ordenación · −3 sin determinar
```

La plusvalía de reformar depende de la **edad**: nula por debajo de 10 años,
máxima (22 % del valor) a partir de 70. Sin año de construcción se supone 60.
Fuera de ordenación además anula el potencial: no se puede levantar.

Un retorno negativo **no** dice «no se puede construir». Dice que ese lote no va
a valer mañana más de lo que vale hoy. En Carabanchel: 1.873 de 9.979 negativos,
ninguno exactamente cero, mediana +6,8 %, rango −17,7 % a +138 %.

Los coeficientes viven en `RET` dentro de `logic.js`, una ciudad puede pisarlos
desde `C.retorno`, y están escritos íntegros en la ficha que abre la «i» del
gráfico. Son un **borrador con criterio**, no una calibración contra ventas
reales: cuando haya serie de transacciones cambian los números, no la forma.

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
