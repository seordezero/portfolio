#!/usr/bin/env python3
"""
Build the site content from plain folders.

Drop a folder per project in  content/projects/<slug>/  containing:

  project.txt          metadata + body (see format below)
  <name>.jpg/png/jpeg  one or more images
  <name>.txt           (optional) caption for the image with the same name:
                         first line  = image title
                         rest        = image description

project.txt format — "Key: value" lines at the top, then the body:

  Year: 2021
  Category: Research          (Architecture|Design|Parametric|Audiovisual|Research)
  Title: Algoritmia
  Subtitle: Final year project, PUCP
  Cover: 1                    (optional, 1-based index of the catalog thumbnail)
  Collaborators: Ada Lovelace, Alan Turing   (optional, comma separated)

  First paragraph of the description...

  # Site                     (a line starting with "# " is a chapter heading)
  Another paragraph...

Run:  python scripts/build_content.py
It regenerates  public/images/<slug>/{thumb,full}  and  src/data/content.json,
and persists colour assignments in  content/assignments.json  so existing
projects never change colour and new ones get the next free palette pair.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "projects"
OUT_IMAGES = ROOT / "public" / "images"
DATA_JSON = ROOT / "src" / "data" / "content.json"
ASSIGN_JSON = ROOT / "content" / "assignments.json"

IMG_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v"}
CATEGORIES = {"Architecture", "Design", "Parametric", "Audiovisual", "Research"}
HAS_FFMPEG = shutil.which("ffmpeg") is not None

THUMB = 512
FULL_MAX = 2200

# Colours reserved for the three main pages (never given to a project).
RESERVED = {"#e2231a", "#f2b705", "#1b2ed6", "#111110", "#3d1e8a", "#6f8a00"}

# Ordered pool of [square, backdrop] pairs for projects. The first nine match
# the original hand-tuned colours; the rest are spares for new projects. Each
# square colour is handed out at most once.
POOL = [
    ["#6a1b9a", "#f2b705"],  # purple on gold
    ["#0d8a8a", "#ff4d8d"],  # teal on hot pink
    ["#f25c05", "#1b2ed6"],  # orange on blue
    ["#0f8a3d", "#f4f1ea"],  # green on off-white
    ["#ff4d8d", "#0d8a8a"],  # pink on teal
    ["#3d1e8a", "#f25c05"],  # violet on orange
    ["#b5d400", "#6a1b9a"],  # chartreuse on purple
    ["#111110", "#e2231a"],  # near-black on red
    ["#f4f1ea", "#0f8a3d"],  # off-white on green
    ["#d81e5b", "#16161f"],  # crimson on midnight
    ["#00897b", "#ffd166"],  # teal-green on amber
    ["#5e35b1", "#c5e063"],  # deep purple on lime
    ["#ef6c00", "#00485f"],  # orange on deep teal
    ["#c2185b", "#e6e2d3"],  # magenta on bone
    ["#1565c0", "#ff8a65"],  # blue on coral
    ["#6d4c41", "#b2dfdb"],  # brown on mint
    ["#7b1fa2", "#dce775"],  # purple on pale lime
    ["#e64a19", "#0d3b66"],  # vermilion on navy
]


def readable_ink(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#111110" if luminance > 0.58 else "#ffffff"


def parse_project_txt(text: str):
    lines = text.replace("\r\n", "\n").split("\n")
    meta = {}
    i = 0
    key_re = re.compile(r"^([A-Za-z][A-Za-z ]*?):\s*(.*)$")
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            break
        m = key_re.match(line)
        if not m:
            break
        meta[m.group(1).strip().lower()] = m.group(2).strip()
        i += 1

    body_text = "\n".join(lines[i:]).strip()
    body = []
    for block in re.split(r"\n\s*\n", body_text):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            body.append({"type": "h2", "text": block[2:].strip()})
        else:
            body.append({"type": "p", "text": " ".join(block.split("\n")).strip()})
    return meta, body


def parse_image_txt(text: str):
    parts = text.replace("\r\n", "\n").strip().split("\n", 1)
    title = parts[0].strip() if parts else ""
    desc = parts[1].strip().replace("\n", " ") if len(parts) > 1 else ""
    return title, desc


def process_image(src: Path, slug: str, n: int):
    nn = f"{n:02d}"
    ext = src.suffix.lower()
    if ext == ".jpeg":
        ext = ".jpg"
    thumb_dir = OUT_IMAGES / slug / "thumb"
    full_dir = OUT_IMAGES / slug / "full"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    full_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)

        thumb = ImageOps.fit(im.convert("RGB"), (THUMB, THUMB), Image.LANCZOS)
        thumb.save(thumb_dir / f"{nn}.jpg", "JPEG", quality=85)

        full = im.copy()
        full.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        full_name = f"{nn}{ext}"
        if ext == ".png":
            full.save(full_dir / full_name, "PNG", optimize=True)
        else:
            full.convert("RGB").save(full_dir / full_name, "JPEG", quality=88)
    return full_name


def save_thumb_from_image(im, slug: str, n: int):
    nn = f"{n:02d}"
    thumb_dir = OUT_IMAGES / slug / "thumb"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb = ImageOps.fit(im.convert("RGB"), (THUMB, THUMB), Image.LANCZOS)
    thumb.save(thumb_dir / f"{nn}.jpg", "JPEG", quality=85)


def process_video(src: Path, poster: Path, slug: str, n: int):
    """Copy the video to full/ and build a 512 poster thumbnail."""
    nn = f"{n:02d}"
    ext = src.suffix.lower()
    if ext == ".m4v":
        ext = ".mp4"
    full_dir = OUT_IMAGES / slug / "full"
    full_dir.mkdir(parents=True, exist_ok=True)
    full_name = f"{nn}{ext}"
    shutil.copyfile(src, full_dir / full_name)

    if poster is not None:
        with Image.open(poster) as im:
            save_thumb_from_image(ImageOps.exif_transpose(im), slug, n)
    elif HAS_FFMPEG:
        with tempfile.TemporaryDirectory() as tmp:
            frame = Path(tmp) / "frame.png"
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "1", "-i", str(src), "-frames:v", "1", str(frame)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if frame.exists():
                with Image.open(frame) as im:
                    save_thumb_from_image(im, slug, n)
            else:
                Image.new("RGB", (THUMB, THUMB), (20, 20, 19)).save(
                    OUT_IMAGES / slug / "thumb" / f"{nn}.jpg", "JPEG", quality=85)
    else:
        (OUT_IMAGES / slug / "thumb").mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (THUMB, THUMB), (20, 20, 19)).save(
            OUT_IMAGES / slug / "thumb" / f"{nn}.jpg", "JPEG", quality=85)
    return full_name


def load_assignments():
    if ASSIGN_JSON.exists():
        return json.loads(ASSIGN_JSON.read_text(encoding="utf-8"))
    return {}


def assign_colors(slug: str, assignments: dict):
    if slug in assignments:
        return assignments[slug]
    used_squares = {pair[0] for pair in assignments.values()} | RESERVED
    for square, backdrop in POOL:
        if square not in used_squares:
            assignments[slug] = [square, backdrop]
            return assignments[slug]
    # Palette exhausted — reuse from the pool start (warn).
    print(f"  ! palette exhausted, reusing a colour for {slug}", file=sys.stderr)
    assignments[slug] = POOL[len(assignments) % len(POOL)]
    return assignments[slug]


def main():
    if not CONTENT.exists():
        print(f"No content folder at {CONTENT}", file=sys.stderr)
        sys.exit(1)

    assignments = load_assignments()
    projects = []

    slugs = sorted(p.name for p in CONTENT.iterdir() if p.is_dir())
    for slug in slugs:
        folder = CONTENT / slug
        proj_txt = folder / "project.txt"
        if not proj_txt.exists():
            print(f"  skip {slug} (no project.txt)", file=sys.stderr)
            continue

        meta, body = parse_project_txt(proj_txt.read_text(encoding="utf-8"))
        category = meta.get("category", "Architecture").title()
        if category not in CATEGORIES:
            category = "Architecture"

        # Group media by stem so a video can share a name with its poster
        # image and its caption (01.mp4 + 01.jpg + 01.txt -> one video item).
        groups = {}
        for f in folder.iterdir():
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext in VIDEO_EXT:
                groups.setdefault(f.stem, {})["video"] = f
            elif ext in IMG_EXT:
                groups.setdefault(f.stem, {})["image"] = f

        image_data = []
        for n, (stem, group) in enumerate(sorted(groups.items(), key=lambda kv: kv[0].lower()), start=1):
            if "video" in group:
                full_name = process_video(group["video"], group.get("image"), slug, n)
                media_type = "video"
            else:
                full_name = process_image(group["image"], slug, n)
                media_type = "image"
            cap_file = folder / f"{stem}.txt"
            if cap_file.exists():
                title, desc = parse_image_txt(cap_file.read_text(encoding="utf-8"))
            else:
                title, desc = f"Plate {n:02d}", ""
            image_data.append({"file": full_name, "type": media_type, "title": title, "desc": desc})

        square, backdrop = assign_colors(slug, assignments)
        collaborators = [
            c.strip() for c in meta.get("collaborators", "").split(",") if c.strip()
        ]
        try:
            cover = int(meta.get("cover", "1"))
        except ValueError:
            cover = 1

        projects.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "subtitle": meta.get("subtitle", ""),
            "year": int(meta.get("year", "0") or 0),
            "category": category,
            "cover": cover,
            "link": meta.get("link", ""),
            "square": square,
            "backdrop": backdrop,
            "ink": readable_ink(square),
            "inkBackdrop": readable_ink(backdrop),
            "collaborators": collaborators,
            "body": body,
            "images": image_data,
        })
        print(f"  built {slug} ({len(image_data)} images)")

    projects.sort(key=lambda p: (-p["year"], p["title"].lower()))

    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(json.dumps({"projects": projects}, indent=2, ensure_ascii=False), encoding="utf-8")
    ASSIGN_JSON.parent.mkdir(parents=True, exist_ok=True)
    ASSIGN_JSON.write_text(json.dumps(assignments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {DATA_JSON.relative_to(ROOT)} ({len(projects)} projects)")


if __name__ == "__main__":
    main()
