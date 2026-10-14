// Goya 58: publishes the plain web copy behind a password.
// usage: node scripts/goya58_lock.mjs "<plain folder>" public/goya58 "<password>"
//
// The plain copy (index.html, visor/index.html, data.json, model.bin, img/, renders/, proceso/)
// lives outside this public repo.
// index.html becomes a password page that decrypts the real page in the browser
// (AES-GCM, key from PBKDF2-SHA256, same scheme as lock-page.js). data.json and
// model.bin are published only as <file>.enc (12-byte IV + ciphertext, same key); the
// page reads the key the password page leaves in sessionStorage/localStorage.
// Product photos in img/ are copied as they are; renders/ and proceso/ go encrypted.
import fs from 'node:fs';
import path from 'node:path';
import { webcrypto as c } from 'node:crypto';

const [, , src, out, pass] = process.argv;
if (!src || !out || !pass) { console.error('usage: node scripts/goya58_lock.mjs <plain folder> <out folder> <password>'); process.exit(1); }

const ITER = 310000;
const salt = c.getRandomValues(new Uint8Array(16));
const base = await c.subtle.importKey('raw', new TextEncoder().encode(pass.trim().toLowerCase()), 'PBKDF2', false, ['deriveKey']);
const key = await c.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, true, ['encrypt']);
const enc = async bytes => {
  const iv = c.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await c.subtle.encrypt({ name: 'AES-GCM', iv }, key, bytes));
  return Buffer.concat([Buffer.from(iv), Buffer.from(ct)]);
};
const b64 = a => Buffer.from(a).toString('base64');

// fresh output: never leave a plain data.json/model.bin behind
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
for (const f of ['data.json', 'model.bin', 'oscar.glb'].filter(f => fs.existsSync(path.join(src, f)))) fs.writeFileSync(path.join(out, f + '.enc'), await enc(fs.readFileSync(path.join(src, f))));
fs.cpSync(path.join(src, 'img'), path.join(out, 'img'), { recursive: true });
// room renders and process images: client material, published only encrypted
for (const dir of ['renders', 'proceso']) {
  if (!fs.existsSync(path.join(src, dir))) continue;
  fs.mkdirSync(path.join(out, dir), { recursive: true });
  for (const f of fs.readdirSync(path.join(src, dir)))
    fs.writeFileSync(path.join(out, dir, f + '.enc'), await enc(fs.readFileSync(path.join(src, dir, f))));
}

// two pages, same key: index.html (title and process) and visor/index.html (the 3D viewer).
// Opening one leaves the key in sessionStorage, so the other opens without asking again.
for (const [rel, title] of [['index.html', 'Goya 58'], ['visor/index.html', 'Goya 58 · Visor']]) {
const page = await enc(fs.readFileSync(path.join(src, rel)));
const iv = page.subarray(0, 12), ct = page.subarray(12);
fs.mkdirSync(path.dirname(path.join(out, rel)), { recursive: true });
fs.writeFileSync(path.join(out, rel), `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>${title}</title>
<style>
:root{--bg:#121212;--fg:#ecebe7;--mut:#8e8b85;--line:#3a3a38}
html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--fg);font:15px/1.45 Inter,"Segoe UI",system-ui,sans-serif;display:grid;place-items:center;padding:16px;box-sizing:border-box}
form{display:flex;flex-direction:column;gap:12px;width:min(320px,100%)}
h1{font-size:24px;margin:0;font-weight:600}
p{margin:0;color:var(--mut);font-size:13px}
#f input,#f button{font:inherit;padding:10px 12px;border-radius:0;border:1px solid var(--line);box-sizing:border-box;width:100%}
#f input{background:#000;color:var(--fg)}
#f button{background:var(--fg);color:#000;border-color:var(--fg);cursor:pointer}
#f input:focus-visible,#f button:focus-visible{outline:1px solid var(--fg);outline-offset:2px}
#f label{display:flex;gap:8px;align-items:center;font-size:13px;color:var(--mut)}
#f label input{width:auto}
#msg{min-height:1.2em;color:#e0705a}
</style></head><body>
<form id="f">
  <h1>Goya 58</h1>
  <p>Proyecto privado. Introduce la contraseña.</p>
  <input id="pw" type="password" autocomplete="current-password" placeholder="Contraseña" aria-label="Contraseña" autofocus>
  <label><input id="keep" type="checkbox" checked> Recordar en este dispositivo</label>
  <button type="submit">Entrar</button>
  <p id="msg" role="alert"></p>
</form>
<script>
const SALT="${b64(salt)}",IV="${b64(iv)}",ITER=${ITER},DATA="${b64(ct)}",K="goya58-key",STAMP="${b64(salt).slice(0, 8)}";
const u8=s=>Uint8Array.from(atob(s),ch=>ch.charCodeAt(0));
async function open(raw){
  const key=await crypto.subtle.importKey("raw",raw,"AES-GCM",false,["decrypt"]);
  const html=new TextDecoder().decode(await crypto.subtle.decrypt({name:"AES-GCM",iv:u8(IV)},key,u8(DATA)));
  try{sessionStorage.setItem(K,btoa(String.fromCharCode(...raw)))}catch(_){}
  if(document.readyState!=="complete")await new Promise(r=>addEventListener("load",r,{once:true}));
  document.open();document.write(html);document.close();
}
async function derive(pw){
  const base=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw.trim().toLowerCase()),"PBKDF2",false,["deriveKey"]);
  const k=await crypto.subtle.deriveKey({name:"PBKDF2",salt:u8(SALT),iterations:ITER,hash:"SHA-256"},base,{name:"AES-GCM",length:256},true,["decrypt"]);
  return new Uint8Array(await crypto.subtle.exportKey("raw",k));
}
// a key from this session (the other page) or a remembered one; it only works for this build,
// since the salt changes on every publish
(async()=>{try{const s=sessionStorage.getItem(K);if(s){await open(u8(s));return;}}catch(e){}
  try{const s=localStorage.getItem(K),st=localStorage.getItem(K+"-stamp");if(s&&st===STAMP){await open(u8(s));return;}}catch(e){}
  try{localStorage.removeItem(K)}catch(_){}})();
document.getElementById("f").onsubmit=async e=>{
  e.preventDefault();const msg=document.getElementById("msg");msg.textContent="Abriendo…";
  try{
    const raw=await derive(document.getElementById("pw").value);
    if(document.getElementById("keep").checked){try{localStorage.setItem(K,btoa(String.fromCharCode(...raw)));localStorage.setItem(K+"-stamp",STAMP)}catch(_){}}
    await open(raw);
  }catch(err){msg.textContent="Contraseña incorrecta.";}
};
</script></body></html>
`);
}
console.log('locked ->', out);
