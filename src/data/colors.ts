// Per-page color assignment.
// Every palette color is used exactly once as a square fill and once as a
// backdrop, so no two pages share a square color or a backdrop color.
// Text is only ever black or white, chosen for contrast against the square.

export interface PageColors {
  square: string;
  backdrop: string;
  ink: string;        // readable on the square fill
  inkBackdrop: string; // readable on the backdrop (used by the corner header)
}

// [square, backdrop] per page index. Both columns are a permutation of the
// same 12-color palette (strong + weird: purple, gold, violet, chartreuse…).
const pairs: [string, string][] = [
  ["#e2231a", "#111110"], // 0  index          red      on near-black
  ["#f2b705", "#3d1e8a"], // 1  about          gold     on deep violet
  ["#1b2ed6", "#6f8a00"], // 2  contact        blue     on darker green
  ["#6a1b9a", "#f2b705"], // 3  secciones      purple   on gold
  ["#0d8a8a", "#ff4d8d"], // 4  cph            teal     on hot pink
  ["#f25c05", "#1b2ed6"], // 5  master         orange   on blue
  ["#0f8a3d", "#f4f1ea"], // 6  algoritmia     green    on off-white
  ["#ff4d8d", "#0d8a8a"], // 7  la-bienvenida  pink     on teal
  ["#3d1e8a", "#f25c05"], // 8  jiron          violet   on orange
  ["#b5d400", "#6a1b9a"], // 9  foldable       chartreuse on purple
  ["#111110", "#e2231a"], // 10 fable          near-black on red
  ["#f4f1ea", "#0f8a3d"], // 11 workshop       off-white  on green
];

function readableInk(hex: string): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const L = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return L > 0.58 ? "#111110" : "#ffffff";
}

export function pageColors(index: number): PageColors {
  const [square, backdrop] = pairs[((index % pairs.length) + pairs.length) % pairs.length];
  return { square, backdrop, ink: readableInk(square), inkBackdrop: readableInk(backdrop) };
}
