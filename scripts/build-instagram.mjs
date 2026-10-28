// Prepara las imágenes de la cola de Instagram en public/instagram/<post>/NN.jpg
// para que el sitio las sirva y Instagram las pueda bajar por URL.
//
// Instagram solo acepta JPEG, entre 4:5 (vertical) y 1.91:1 (apaisado), y en
// un carrusel recorta todas a la proporción de la primera. Así que todas las de
// un post se llevan a la proporción de la primera (limitada a ese rango) y lo
// que falta se rellena con fondo, nunca se recorta: un plano cortado no sirve.
import { promises as fs } from "node:fs";
import path from "node:path";
import sharp from "sharp";
import { ROOT, readQueue } from "./instagram-posts.mjs";

const OUT = path.join(ROOT, "public", "instagram");
const WIDTH = 1440;
const MIN_RATIO = 4 / 5;
const MAX_RATIO = 1.91;
const BACKGROUND = { r: 255, g: 255, b: 255 };

async function main() {
  const posts = await readQueue();
  await fs.rm(OUT, { recursive: true, force: true });

  for (const post of posts) {
    const dir = path.join(OUT, post.name);
    await fs.mkdir(dir, { recursive: true });

    const first = await sharp(post.sources[0]).rotate().metadata();
    const [w0, h0] = first.orientation >= 5 ? [first.height, first.width] : [first.width, first.height];
    const ratio = Math.min(MAX_RATIO, Math.max(MIN_RATIO, w0 / h0));
    const width = WIDTH;
    const height = Math.round(WIDTH / ratio);

    for (let k = 0; k < post.sources.length; k++) {
      await sharp(post.sources[k]).rotate()
        .resize(width, height, { fit: "contain", background: BACKGROUND })
        .flatten({ background: BACKGROUND })
        .jpeg({ quality: 90, mozjpeg: true })
        .toFile(path.join(dir, post.files[k]));
    }
    console.log(`  instagram ${post.name} (${post.sources.length} imágenes, ${width}×${height})`);
  }
}

main().catch((err) => { console.error(err.message || err); process.exit(1); });
