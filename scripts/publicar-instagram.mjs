// Publica en Instagram el primer post de la cola que aún no esté en
// content/instagram/publicado.json, y lo apunta ahí.
//
// Usa la API de Instagram con inicio de sesión de Instagram (graph.instagram.com):
// cuenta profesional (Business o Creator), sin página de Facebook. Necesita dos
// variables de entorno, que en GitHub son secretos del repositorio:
//   IG_USER_ID       el id de la cuenta de Instagram
//   IG_ACCESS_TOKEN  token de larga duración (dura 60 días)
//
// Las imágenes se bajan de la web publicada: el post tiene que haber llegado al
// sitio (push a main y despliegue terminado) antes de publicarse.
//
//   node scripts/publicar-instagram.mjs            publica el siguiente
//   node scripts/publicar-instagram.mjs --prueba   dice cuál sería, sin publicar
import { promises as fs } from "node:fs";
import { PUBLISHED_JSON, readQueue, readPublished } from "./instagram-posts.mjs";

const API = "https://graph.instagram.com";
const DRY = process.argv.includes("--prueba");

async function call(method, endpoint, params) {
  const url = new URL(`${API}/${endpoint}`);
  const body = new URLSearchParams({ ...params, access_token: process.env.IG_ACCESS_TOKEN });
  const res = method === "GET"
    ? await fetch(`${url}?${body}`)
    : await fetch(url, { method, body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    throw new Error(`${endpoint}: ${data.error?.message || res.status} (${JSON.stringify(data.error || {})})`);
  }
  return data;
}

// Instagram procesa el contenedor en segundo plano; publicar antes de que esté
// FINISHED da error.
async function waitReady(id) {
  for (let i = 0; i < 30; i++) {
    const { status_code } = await call("GET", id, { fields: "status_code" });
    if (status_code === "FINISHED") return;
    if (status_code === "ERROR" || status_code === "EXPIRED") throw new Error(`contenedor ${id}: ${status_code}`);
    await new Promise((r) => setTimeout(r, 5000));
  }
  throw new Error(`contenedor ${id}: no terminó de procesarse`);
}

async function main() {
  const published = await readPublished();
  const next = (await readQueue()).find((p) => !published[p.name]);
  if (!next) { console.log("Cola vacía: no hay nada que publicar."); return; }

  console.log(`Siguiente: ${next.name} (${next.urls.length} imágenes)`);
  for (const url of next.urls) {
    const res = await fetch(url, { method: "HEAD" }).catch((err) => { throw new Error(`${url}: ${err.cause?.code || err.message}`); });
    if (!res.ok) throw new Error(`${url} devuelve ${res.status}: el sitio aún no tiene este post desplegado`);
  }
  if (DRY) { console.log(next.urls.join("\n")); console.log("---\n" + next.caption); return; }

  const user = process.env.IG_USER_ID;
  if (!user || !process.env.IG_ACCESS_TOKEN) throw new Error("faltan IG_USER_ID o IG_ACCESS_TOKEN");

  let container;
  if (next.urls.length === 1) {
    container = (await call("POST", `${user}/media`, { image_url: next.urls[0], caption: next.caption })).id;
  } else {
    const children = [];
    for (const url of next.urls) {
      children.push((await call("POST", `${user}/media`, { image_url: url, is_carousel_item: "true" })).id);
    }
    for (const id of children) await waitReady(id);
    container = (await call("POST", `${user}/media`, {
      media_type: "CAROUSEL", children: children.join(","), caption: next.caption,
    })).id;
  }
  await waitReady(container);

  const { id } = await call("POST", `${user}/media_publish`, { creation_id: container });
  const { permalink } = await call("GET", id, { fields: "permalink" }).catch(() => ({}));

  published[next.name] = { id, permalink: permalink || "", fecha: new Date().toISOString() };
  await fs.writeFile(PUBLISHED_JSON, JSON.stringify(published, null, 2) + "\n");
  console.log(`Publicado: ${permalink || id}`);
}

main().catch((err) => { console.error(err.message || err); process.exit(1); });
