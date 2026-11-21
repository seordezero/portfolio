// Prepara la imagen de cada post de la cola en public/instagram/<post>.jpg para
// que el sitio la sirva e Instagram la pueda bajar por URL.
//
// Instagram solo acepta JPEG entre 4:5 (vertical) y 1.91:1 (apaisado). Si la
// imagen se sale de ese rango se rellena con fondo hasta entrar, nunca se
// recorta: un plano cortado no sirve.
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
  await fs.mkdir(OUT, { recursive: true });

  for (const post of posts) {
    const meta = await sharp(post.source).metadata();
    const [w, h] = meta.orientation >= 5 ? [meta.height, meta.width] : [meta.width, meta.height];
    const ratio = Math.min(MAX_RATIO, Math.max(MIN_RATIO, w / h));
    const height = Math.round(WIDTH / ratio);

    await sharp(post.source).rotate()
      .resize(WIDTH, height, { fit: "contain", background: BACKGROUND })
      .flatten({ background: BACKGROUND })
      .jpeg({ quality: 90, mozjpeg: true })
      .toFile(path.join(OUT, `${post.name}.jpg`));
    console.log(`  instagram ${post.name} (${WIDTH}×${height})`);
  }
}

main().catch((err) => { console.error(err.message || err); process.exit(1); });
