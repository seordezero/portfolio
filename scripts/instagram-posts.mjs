// Lee la cola de Instagram de content/instagram/<post>/. Lo usan el build
// (build-instagram.mjs, que prepara las imágenes) y la publicación
// (publicar-instagram.mjs, que las sube). No importa sharp a propósito: la
// publicación corre sin instalar dependencias.
//
// Formato documentado en content/instagram/README.md.
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const QUEUE = path.join(ROOT, "content", "instagram");
export const PROJECTS = path.join(ROOT, "content", "projects");
export const PUBLISHED_JSON = path.join(QUEUE, "publicado.json");
export const SITE = "https://sebastianortizdezevallos.com";

const IMG_EXT = new Set([".jpg", ".jpeg", ".png"]);
const MAX_ITEMS = 10;            // tope de un carrusel
const MAX_CAPTION = 2200;
const MAX_HASHTAGS = 30;

// post.txt: cabecera "Clave: valor" hasta la primera línea en blanco, y el
// resto es el pie de foto tal cual.
function parsePostTxt(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const meta = {};
  const keyRe = /^([A-Za-zÁÉÍÓÚáéíóú][A-Za-zÁÉÍÓÚáéíóú ]*?):\s*(.*)$/;
  let i = 0;
  while (i < lines.length) {
    if (lines[i].trim() === "") { i++; break; }
    const m = keyRe.exec(lines[i]);
    if (!m) break;
    const key = m[1].trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    meta[key] = m[2].trim();
    i++;
  }
  return { meta, caption: lines.slice(i).join("\n").trim() };
}

async function imagesIn(folder) {
  const names = (await fs.readdir(folder)).filter((n) => IMG_EXT.has(path.extname(n).toLowerCase()));
  return names.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())).map((n) => path.join(folder, n));
}

// Devuelve los posts listos para publicar, en orden de carpeta. Las carpetas que
// empiezan por "_" son borradores y no salen.
export async function readQueue() {
  let dirs;
  try {
    dirs = (await fs.readdir(QUEUE, { withFileTypes: true }))
      .filter((d) => d.isDirectory() && !d.name.startsWith("_")).map((d) => d.name).sort();
  } catch { return []; }

  const posts = [];
  for (const name of dirs) {
    const folder = path.join(QUEUE, name);
    let raw;
    try { raw = await fs.readFile(path.join(folder, "post.txt"), "utf-8"); } catch {
      throw new Error(`${name}: falta post.txt`);
    }
    const { meta, caption } = parsePostTxt(raw);

    // Imágenes propias de la carpeta; si no hay, las del proyecto que nombre.
    let sources = await imagesIn(folder);
    if (sources.length === 0 && meta.proyecto) {
      const all = await imagesIn(path.join(PROJECTS, meta.proyecto));
      if (meta.imagenes) {
        const picks = meta.imagenes.split(",").map((s) => parseInt(s, 10)).filter(Boolean);
        sources = picks.map((n) => {
          if (!all[n - 1]) throw new Error(`${name}: ${meta.proyecto} no tiene imagen ${n}`);
          return all[n - 1];
        });
      } else sources = all;
    }

    if (sources.length === 0) throw new Error(`${name}: sin imágenes`);
    if (sources.length > MAX_ITEMS) throw new Error(`${name}: ${sources.length} imágenes, el máximo es ${MAX_ITEMS}`);
    if (caption.length > MAX_CAPTION) throw new Error(`${name}: el texto pasa de ${MAX_CAPTION} caracteres`);
    const tags = (caption.match(/#[\p{L}\p{N}_]+/gu) || []).length;
    if (tags > MAX_HASHTAGS) throw new Error(`${name}: ${tags} hashtags, el máximo es ${MAX_HASHTAGS}`);

    posts.push({
      name,
      caption,
      sources,
      // Dónde las deja el build y desde dónde las baja Instagram.
      files: sources.map((_, k) => `${String(k + 1).padStart(2, "0")}.jpg`),
      urls: sources.map((_, k) => `${SITE}/instagram/${name}/${String(k + 1).padStart(2, "0")}.jpg`),
    });
  }
  return posts;
}

export async function readPublished() {
  try { return JSON.parse(await fs.readFile(PUBLISHED_JSON, "utf-8")); } catch { return {}; }
}
