// Builds the site content from content/projects/<slug>/ folders.
// Runs locally AND on the Cloudflare build (see package.json "build"), so
// uploading a new project/image and pushing is enough — the deploy resizes
// the images and regenerates src/data/content.json automatically.
//
// Folder format is documented in content/README.md.
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CONTENT = path.join(ROOT, "content", "projects");
const OUT_IMAGES = path.join(ROOT, "public", "images");
const DATA_JSON = path.join(ROOT, "src", "data", "content.json");
const ASSIGN_JSON = path.join(ROOT, "content", "assignments.json");

const IMG_EXT = new Set([".jpg", ".jpeg", ".png"]);
const VIDEO_EXT = new Set([".mp4", ".webm", ".mov", ".m4v"]);
const CATEGORIES = new Set(["Architecture", "Design", "Parametric", "Audiovisual", "Research"]);
const THUMB = 512;
const FULL_MAX = 2200;

// Colours reserved for the three main pages (never given to a project).
const RESERVED = new Set(["#e2231a", "#f2b705", "#1b2ed6", "#111110", "#3d1e8a", "#6f8a00"]);

// Ordered pool of [square, backdrop] pairs. First nine match the originals;
// the rest are spares for new projects. Each square is handed out at most once.
const POOL = [
  ["#6a1b9a", "#f2b705"], ["#0d8a8a", "#ff4d8d"], ["#f25c05", "#1b2ed6"],
  ["#0f8a3d", "#f4f1ea"], ["#ff4d8d", "#0d8a8a"], ["#3d1e8a", "#f25c05"],
  ["#b5d400", "#6a1b9a"], ["#111110", "#e2231a"], ["#f4f1ea", "#0f8a3d"],
  ["#d81e5b", "#16161f"], ["#00897b", "#ffd166"], ["#5e35b1", "#c5e063"],
  ["#ef6c00", "#00485f"], ["#c2185b", "#e6e2d3"], ["#1565c0", "#ff8a65"],
  ["#6d4c41", "#b2dfdb"], ["#7b1fa2", "#dce775"], ["#e64a19", "#0d3b66"],
];

function readableInk(hex) {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.58 ? "#111110" : "#ffffff";
}

function parseProjectTxt(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const meta = {};
  const keyRe = /^([A-Za-z][A-Za-z ]*?):\s*(.*)$/;
  let i = 0;
  while (i < lines.length) {
    if (lines[i].trim() === "") { i++; break; }
    const m = keyRe.exec(lines[i]);
    if (!m) break;
    meta[m[1].trim().toLowerCase()] = m[2].trim();
    i++;
  }
  const body = [];
  const bodyText = lines.slice(i).join("\n").trim();
  for (const raw of bodyText.split(/\n\s*\n/)) {
    const block = raw.trim();
    if (!block) continue;
    if (block.startsWith("# ")) body.push({ type: "h2", text: block.slice(2).trim() });
    else body.push({ type: "p", text: block.split("\n").join(" ").trim() });
  }
  return { meta, body };
}

function parseImageTxt(text) {
  const parts = text.replace(/\r\n/g, "\n").trim().split("\n");
  return { title: (parts[0] || "").trim(), desc: parts.slice(1).join(" ").trim() };
}

async function processImage(src, slug, n) {
  const nn = String(n).padStart(2, "0");
  let ext = path.extname(src).toLowerCase();
  if (ext === ".jpeg") ext = ".jpg";
  const thumbDir = path.join(OUT_IMAGES, slug, "thumb");
  const fullDir = path.join(OUT_IMAGES, slug, "full");
  await fs.mkdir(thumbDir, { recursive: true });
  await fs.mkdir(fullDir, { recursive: true });

  await sharp(src).rotate().resize(THUMB, THUMB, { fit: "cover" })
    .jpeg({ quality: 85 }).toFile(path.join(thumbDir, `${nn}.jpg`));

  const fullName = `${nn}${ext}`;
  const pipeline = sharp(src).rotate().resize(FULL_MAX, FULL_MAX, { fit: "inside", withoutEnlargement: true });
  await (ext === ".png" ? pipeline.png({ compressionLevel: 9 }) : pipeline.jpeg({ quality: 88 }))
    .toFile(path.join(fullDir, fullName));
  return fullName;
}

async function processVideo(src, poster, slug, n) {
  const nn = String(n).padStart(2, "0");
  let ext = path.extname(src).toLowerCase();
  if (ext === ".m4v") ext = ".mp4";
  const thumbDir = path.join(OUT_IMAGES, slug, "thumb");
  const fullDir = path.join(OUT_IMAGES, slug, "full");
  await fs.mkdir(thumbDir, { recursive: true });
  await fs.mkdir(fullDir, { recursive: true });

  const fullName = `${nn}${ext}`;
  await fs.copyFile(src, path.join(fullDir, fullName));

  if (poster) {
    await sharp(poster).rotate().resize(THUMB, THUMB, { fit: "cover" })
      .jpeg({ quality: 85 }).toFile(path.join(thumbDir, `${nn}.jpg`));
  } else {
    console.warn(`  ! ${slug}/${path.basename(src)} has no poster image; using a placeholder`);
    await sharp({ create: { width: THUMB, height: THUMB, channels: 3, background: { r: 20, g: 20, b: 19 } } })
      .jpeg({ quality: 85 }).toFile(path.join(thumbDir, `${nn}.jpg`));
  }
  return fullName;
}

function assignColors(slug, assignments) {
  if (assignments[slug]) return assignments[slug];
  const usedSquares = new Set([...Object.values(assignments).map((p) => p[0]), ...RESERVED]);
  for (const [square, backdrop] of POOL) {
    if (!usedSquares.has(square)) { assignments[slug] = [square, backdrop]; return assignments[slug]; }
  }
  console.warn(`  ! palette exhausted, reusing a colour for ${slug}`);
  assignments[slug] = POOL[Object.keys(assignments).length % POOL.length];
  return assignments[slug];
}

async function readJson(file, fallback) {
  try { return JSON.parse(await fs.readFile(file, "utf-8")); } catch { return fallback; }
}

async function main() {
  let dirs;
  try {
    dirs = (await fs.readdir(CONTENT, { withFileTypes: true }))
      .filter((d) => d.isDirectory()).map((d) => d.name).sort();
  } catch {
    console.error(`No content folder at ${CONTENT}`);
    process.exit(1);
  }

  const assignments = await readJson(ASSIGN_JSON, {});
  const projects = [];

  for (const slug of dirs) {
    const folder = path.join(CONTENT, slug);
    const projTxt = path.join(folder, "project.txt");
    let projRaw;
    try { projRaw = await fs.readFile(projTxt, "utf-8"); } catch {
      console.warn(`  skip ${slug} (no project.txt)`);
      continue;
    }
    const { meta, body } = parseProjectTxt(projRaw);
    let category = (meta.category || "Architecture");
    category = category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
    if (!CATEGORIES.has(category)) category = "Architecture";

    const entries = await fs.readdir(folder, { withFileTypes: true });
    const groups = new Map();
    for (const e of entries) {
      if (!e.isFile()) continue;
      const ext = path.extname(e.name).toLowerCase();
      const stem = path.basename(e.name, path.extname(e.name));
      if (!VIDEO_EXT.has(ext) && !IMG_EXT.has(ext)) continue;
      if (!groups.has(stem)) groups.set(stem, {});
      if (VIDEO_EXT.has(ext)) groups.get(stem).video = path.join(folder, e.name);
      else groups.get(stem).image = path.join(folder, e.name);
    }

    const stems = [...groups.keys()].sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    const images = [];
    let n = 0;
    for (const stem of stems) {
      n += 1;
      const group = groups.get(stem);
      let file, type;
      if (group.video) { file = await processVideo(group.video, group.image, slug, n); type = "video"; }
      else { file = await processImage(group.image, slug, n); type = "image"; }
      let title = `Plate ${String(n).padStart(2, "0")}`, desc = "";
      try { ({ title, desc } = parseImageTxt(await fs.readFile(path.join(folder, `${stem}.txt`), "utf-8"))); } catch {}
      images.push({ file, type, title, desc });
    }

    const [square, backdrop] = assignColors(slug, assignments);
    const collaborators = (meta.collaborators || "").split(",").map((c) => c.trim()).filter(Boolean);
    const cover = parseInt(meta.cover || "1", 10) || 1;

    projects.push({
      slug,
      title: meta.title || slug,
      subtitle: meta.subtitle || "",
      year: parseInt(meta.year || "0", 10) || 0,
      category,
      cover,
      link: meta.link || "",
      square, backdrop, ink: readableInk(square), inkBackdrop: readableInk(backdrop),
      collaborators, body, images,
    });
    console.log(`  built ${slug} (${images.length} media)`);
  }

  projects.sort((a, b) => b.year - a.year || a.title.toLowerCase().localeCompare(b.title.toLowerCase()));

  await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
  await fs.writeFile(DATA_JSON, JSON.stringify({ projects }, null, 2));
  await fs.writeFile(ASSIGN_JSON, JSON.stringify(assignments, null, 2));
  console.log(`Wrote ${path.relative(ROOT, DATA_JSON)} (${projects.length} projects)`);
}

main().catch((err) => { console.error(err); process.exit(1); });
