#!/usr/bin/env python3
"""encrypt-tool.py — Lisää uusi salattu työkalu tähän Vercel-projektiin."""
import argparse, base64, os, re, sys
from pathlib import Path
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    print("Asenna cryptography: pip install cryptography", file=sys.stderr); sys.exit(1)

PASSWORD = "Menestys2026!"
ITER = 100000

NAV_CSS = """<style id="be-nav-style">
  .be-tools-nav { background:#111827; color:white; position:sticky; top:0; z-index:100; box-shadow:0 2px 4px rgba(0,0,0,0.1); }
  .be-tools-nav .nav-inner { max-width:1400px; margin:0 auto; padding:0 24px; display:flex; align-items:center; gap:24px; height:48px; }
  .be-tools-nav .brand { color:white; text-decoration:none; font-weight:700; font-size:14px; display:flex; align-items:center; gap:8px; }
  .be-tools-nav .brand::before { content:""; width:8px; height:8px; background:#60a5fa; border-radius:50%; }
  .be-tools-nav .links { display:flex; gap:4px; flex:1; flex-wrap:wrap; }
  .be-tools-nav .links a { color:#9ca3af; text-decoration:none; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:500; }
  .be-tools-nav .links a:hover { background:#1f2937; color:white; }
  .be-tools-nav .links a.active { background:#1E40AF; color:white; }
  .be-tools-nav .lock-btn { background:transparent; color:#9ca3af; border:1px solid #374151; padding:5px 12px; border-radius:6px; font-size:12px; cursor:pointer; }
  .be-tools-nav .lock-btn:hover { background:#1f2937; color:white; }
</style>"""

EXISTING_TOOLS = [
    {"slug": "esimerkki", "label": "Esimerkki"}
]

def make_nav(active_slug, all_tools):
    links = ""
    for t in all_tools:
        cls = "active" if t["slug"] == active_slug else ""
        links += f'    <a href="/{t["slug"]}" class="{cls}">{t["label"]}</a>\n'
    return f"""<nav class="be-tools-nav"><div class="nav-inner">
  <a href="/" class="brand">Elämys Internal Tools</a>
  <div class="links">
{links}  </div>
  <button class="lock-btn" onclick="sessionStorage.removeItem('tools_pw');location.href='/';">🔒 Lukitse</button>
</div></nav>"""

def inject_nav(html, active_slug, all_tools):
    html = html.replace("</head>", NAV_CSS + "\n</head>", 1)
    html = re.sub(r"(<body[^>]*>)", r"\1" + make_nav(active_slug, all_tools), html, count=1)
    return html

def encrypt(plain):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(PASSWORD.encode())
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plain.encode(), None)
    return base64.b64encode(salt).decode(), base64.b64encode(nonce).decode(), base64.b64encode(ct).decode()

def wrap(title, plain):
    s, n, c = encrypt(plain)
    return f"""<!DOCTYPE html><html lang="fi"><head>
<meta charset="UTF-8"><title>{title}</title>
<style>body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1E3A8A 0%,#1E40AF 100%);color:white;font-family:Arial,sans-serif;}}</style></head><body>
<div>Avataan…</div>
<script>
const S = "{s}", N = "{n}", C = "{c}", ITER = {ITER};
function b(x){{const s=atob(x);const a=new Uint8Array(s.length);for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a;}}
async function dk(p,salt){{const k=await crypto.subtle.importKey("raw",new TextEncoder().encode(p),"PBKDF2",false,["deriveKey"]);return crypto.subtle.deriveKey({{name:"PBKDF2",salt,iterations:ITER,hash:"SHA-256"}},k,{{name:"AES-GCM",length:256}},false,["decrypt"]);}}
(async()=>{{
  const pw=sessionStorage.getItem("tools_pw");
  if(!pw){{location.href="/?return="+encodeURIComponent(location.pathname);return;}}
  try{{const key=await dk(pw,b(S));const plain=await crypto.subtle.decrypt({{name:"AES-GCM",iv:b(N)}},key,b(C));document.open();document.write(new TextDecoder().decode(plain));document.close();}}
  catch(e){{sessionStorage.removeItem("tools_pw");location.href="/?error=1&return="+encodeURIComponent(location.pathname);}}
}})();
</script></body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("slug")
    ap.add_argument("title")
    ap.add_argument("description")
    args = ap.parse_args()
    src = Path(args.source)
    if not src.exists():
        print(f"Ei löydy: {src}", file=sys.stderr); sys.exit(1)
    plain = src.read_text(encoding="utf-8")
    all_tools = list(EXISTING_TOOLS)
    if not any(t["slug"] == args.slug for t in all_tools):
        all_tools.append({"slug": args.slug, "label": args.title})
    plain = inject_nav(plain, args.slug, all_tools)
    out = Path("tools") / f"{args.slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(wrap(f"Elämys Internal Tools - {args.title}", plain), encoding="utf-8")
    print(f"OK: {out}")

if __name__ == "__main__":
    main()
