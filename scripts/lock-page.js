// Encrypts the standalone tool into a password page (AES-GCM, key from PBKDF2-SHA256).
// usage: node lock.js <in.html> <out.html> "<password>"
const fs = require('fs'), { webcrypto: c } = require('crypto');
const [, , inFile, outFile, pass] = process.argv;
(async () => {
  const salt = c.getRandomValues(new Uint8Array(16)), iv = c.getRandomValues(new Uint8Array(12)), ITER = 310000;
  const base = await c.subtle.importKey('raw', new TextEncoder().encode(pass.trim().toLowerCase()), 'PBKDF2', false, ['deriveKey']);
  const key = await c.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, true, ['encrypt']);
  const ct = new Uint8Array(await c.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(fs.readFileSync(inFile, 'utf8'))));
  const b64 = a => Buffer.from(a).toString('base64');
  fs.writeFileSync(outFile, `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Telar Generator by Ale</title>
<style>
:root{--bg:#F1F0EB;--fg:#26221C;--mut:#756E63;--line:#DDD8CE;--acc:#B8841A}
@media (prefers-color-scheme:dark){:root{--bg:#1B1A17;--fg:#EDE8DE;--mut:#A0998D;--line:#3A3630;--acc:#D9A93A}}
html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--fg);font:15px/1.45 "Segoe UI",system-ui,sans-serif;display:grid;place-items:center;padding:16px;box-sizing:border-box}
form{display:flex;flex-direction:column;gap:12px;width:min(340px,100%)}
h1{font-size:24px;margin:0}
p{margin:0;color:var(--mut);font-size:13px}
input,button{font:inherit;padding:9px 12px;border-radius:7px;border:1px solid var(--line);box-sizing:border-box;width:100%}
input{background:transparent;color:var(--fg)}
button{background:var(--fg);color:var(--bg);border-color:var(--fg);cursor:pointer}
input:focus-visible,button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
label{display:flex;gap:8px;align-items:center;font-size:13px;color:var(--mut)}
label input{width:auto}
#msg{min-height:1.2em;color:#C0392B}
</style></head><body>
<form id="f">
  <h1>Telar Generator <span style="font-weight:400;color:var(--mut)">by Ale</span></h1>
  <p>This tool is private. Enter the password to open it.</p>
  <input id="pw" type="password" autocomplete="current-password" placeholder="Password" aria-label="Password" autofocus>
  <label><input id="keep" type="checkbox" checked> Remember on this device</label>
  <button type="submit">Open</button>
  <p id="msg" role="alert"></p>
</form>
<script>
const SALT="${b64(salt)}",IV="${b64(iv)}",ITER=${ITER},DATA="${b64(ct)}",KEY="telar-gate-${b64(salt).slice(0, 8)}";
const u8=s=>Uint8Array.from(atob(s),ch=>ch.charCodeAt(0));
async function open(raw){
  const key=await crypto.subtle.importKey("raw",raw,"AES-GCM",false,["decrypt"]);
  const html=new TextDecoder().decode(await crypto.subtle.decrypt({name:"AES-GCM",iv:u8(IV)},key,u8(DATA)));
  document.open();document.write(html);document.close();
}
async function derive(pw){
  const base=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw.trim().toLowerCase()),"PBKDF2",false,["deriveKey"]);
  const k=await crypto.subtle.deriveKey({name:"PBKDF2",salt:u8(SALT),iterations:ITER,hash:"SHA-256"},base,{name:"AES-GCM",length:256},true,["decrypt"]);
  return new Uint8Array(await crypto.subtle.exportKey("raw",k));
}
(async()=>{try{const s=localStorage.getItem(KEY);if(s){await open(u8(s));return;}}catch(e){try{localStorage.removeItem(KEY)}catch(_){}}})();
document.getElementById("f").onsubmit=async e=>{
  e.preventDefault();const msg=document.getElementById("msg");msg.textContent="Opening…";
  try{
    const raw=await derive(document.getElementById("pw").value);
    if(document.getElementById("keep").checked){try{localStorage.setItem(KEY,btoa(String.fromCharCode(...raw)))}catch(_){}}
    await open(raw);
  }catch(err){msg.textContent="Wrong password. Try again.";}
};
</script></body></html>
`);
})();
