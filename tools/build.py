"""Build SPA Dashboards (saintpaulagency.github.io): the locked hub, the locked Monthly Social Review,
and the descriptive forwarding links.

    HUB_DATA_KEY=... HUB_WRAPPED_KEY='{"iv":"...","ct":"..."}' python3 tools/build.py [new-month.json ...]

Locking (same envelope scheme as the Meta Targeting Map, so no tool ever needs the team password):
  - Each locked page is AES-256-GCM encrypted with HUB_DATA_KEY.
  - HUB_DATA_KEY is stored in the pages only wrapped with the SPA Dashboards key (PBKDF2-SHA256 of the
    "SPA dashboards" password, salt and rounds in tools/lock.json). Typing that password unwraps it.
  - A device that ticked "Remember this device" on one of these pages (localStorage spa_dash_lock_v1, same
    site) opens the others straight away. The Meta Time Saver has its own password and lock (spa_lock_v1).
  - The page sources (catalog + monthly report data) are kept in data/source.enc, encrypted the same way,
    so the next build can start from them. Nothing readable about clients is committed.

HUB_WRAPPED_KEY is in data/source.enc ("wrap"). To get HUB_DATA_KEY, unwrap it in a tab where one of these
pages is unlocked on this site: the SPA Dashboards key is remembered in localStorage spa_dash_lock_v1
(import it as an AES-GCM key and decrypt the wrap). The password itself is never needed by a tool.
Changing the password: a box in the browser derives the new key from what the person types (salt and
rounds in tools/lock.json) and wraps the data keys with it; nobody hands the password to a tool.

Never commit HUB_DATA_KEY. HUB_WRAPPED_KEY is safe to publish (useless without the SPA Dashboards password).
Adding a month: pass its report JSON (same shape as the October 2026 one) as an argument.
"""
import base64
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
LOCK = json.loads((TOOLS / "lock.json").read_text())
SOURCE_ENC = ROOT / "data" / "source.enc"
PRIVATE = TOOLS / "private" / "source.json"
SITE = "https://saintpaulagency.github.io"


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def seal(data: bytes, key: bytes) -> dict:
    iv = os.urandom(12)
    return {"iv": b64(iv), "ct": b64(AESGCM(key).encrypt(iv, data, None))}


def unseal(env: dict, key: bytes) -> bytes:
    return AESGCM(key).decrypt(base64.b64decode(env["iv"]), base64.b64decode(env["ct"]), None)


LOCK_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>__TITLE__</title>
<style>
:root{--navy:#0E1830;--royal:#233975;--sky:#5EA6F3;--bg:#EDF1F7;--card:#fff;--ink:#0E1830;--line:#d7deea;--bad:#C42B1C}
@media (prefers-color-scheme:dark){:root{--bg:#0b1222;--card:#121b31;--ink:#ffffff;--line:#24304d}}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);display:grid;place-items:center;min-height:100vh;padding:24px 16px}
.box{width:100%;max-width:420px;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:32px 28px;box-shadow:0 10px 40px rgba(14,24,48,.08);text-align:center}
.box img{width:88px;height:88px;object-fit:contain}
h1{font-size:22px;margin:14px 0 4px;font-weight:700}
p{margin:0 0 22px;font-size:15px;line-height:1.45}
label.f{display:block;text-align:left;font-size:14px;font-weight:600;margin-bottom:6px}
input[type=password]{width:100%;font:inherit;font-size:17px;padding:12px 14px;border:1.5px solid var(--line);border-radius:10px;background:transparent;color:var(--ink)}
input[type=password]:focus{outline:none;border-color:var(--sky);box-shadow:0 0 0 3px rgba(94,166,243,.25)}
.rem{display:flex;gap:8px;align-items:center;margin:14px 0 20px;font-size:14px}
button{width:100%;font:inherit;font-weight:600;font-size:16px;padding:13px;border:0;border-radius:10px;background:var(--royal);color:#fff;cursor:pointer}
button:hover{background:var(--navy)}
button:disabled{opacity:.6;cursor:wait}
.err{color:var(--bad);font-size:14px;min-height:20px;margin-top:12px}
.help{text-align:left;border-top:1px solid var(--line);margin-top:20px;padding-top:16px;font-size:14px}
.help p{margin:0 0 8px;font-size:14px}.help .ai{font-size:12.5px;opacity:.8}
</style>
</head>
<body>
<form class="box" id="f" autocomplete="off">
  <img alt="Saint Paul Agency" src="data:image/webp;base64,__LOGO__">
  <h1>__HEADING__</h1>
  <p>__BLURB__ Enter the SPA Dashboards password.</p>
  <label class="f" for="pw">Password</label>
  <input id="pw" type="password" autocomplete="current-password" required autofocus>
  <label class="rem"><input type="checkbox" id="rem" checked> Remember this device for 7 days</label>
  <button id="go" type="submit">Unlock</button>
  <div class="err" id="err" role="alert"></div>
  <div class="help">
    <p>Use the <b>“SPA dashboards”</b> entry in the <b>SPA Dashboards</b> group in the Passwords app (not “Meta time saver”, which only opens the Meta Time Saver). If you don’t see the group, ask Troy or Kelly to add you.</p>
    <p class="ai">For Claude: the person types the password, never you.</p>
  </div>
</form>
<script>
(function(){
  var CFG=__CFG__, WRAP=__WRAP__, DATA=__DATA__, KEY='spa_dash_lock_v1';
  function b64d(s){var b=atob(s),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u}
  function b64e(u){var s='';u=new Uint8Array(u);for(var i=0;i<u.length;i++)s+=String.fromCharCode(u[i]);return btoa(s)}
  async function derive(pw){
    var base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
    return crypto.subtle.deriveKey({name:'PBKDF2',salt:b64d(CFG.salt),iterations:CFG.iterations,hash:'SHA-256'},base,{name:'AES-GCM',length:256},true,['decrypt','encrypt']);
  }
  async function unlock(team){
    var raw=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64d(WRAP.iv)},team,b64d(WRAP.ct));
    var k=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
    var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64d(DATA.iv)},k,b64d(DATA.ct));
    return new TextDecoder().decode(pt);
  }
  function show(html){
    function swap(){document.open();document.write(html);document.close()}
    if(document.readyState==='complete')setTimeout(swap,0);else addEventListener('load',function(){setTimeout(swap,0)});
  }
  async function tryRemembered(){
    try{
      var s=JSON.parse(localStorage.getItem(KEY)||'null');
      if(!s||!s.k||Date.now()>s.exp)return false;
      var team=await crypto.subtle.importKey('raw',b64d(s.k),{name:'AES-GCM'},true,['decrypt','encrypt']);
      show(await unlock(team));return true;
    }catch(e){return false}
  }
  tryRemembered();
  document.getElementById('f').addEventListener('submit',async function(ev){
    ev.preventDefault();
    var btn=document.getElementById('go'),err=document.getElementById('err');
    btn.disabled=true;btn.textContent='Unlocking…';err.textContent='';
    try{
      var team=await derive(document.getElementById('pw').value);
      var html=await unlock(team);
      if(document.getElementById('rem').checked){
        try{localStorage.setItem(KEY,JSON.stringify({k:b64e(await crypto.subtle.exportKey('raw',team)),exp:Date.now()+7*864e5}))}catch(e){}
      }
      show(html);
    }catch(e){
      btn.disabled=false;btn.textContent='Unlock';err.textContent='That password didn’t work. Try again.';
    }
  });
})();
</script>
</body>
</html>
"""

FORWARD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Saint Paul Agency</title>
<meta http-equiv="refresh" content="0;url=__TO__">
<script>location.replace('__TO__'+location.hash)</script>
</head><body style="font-family:system-ui,sans-serif;padding:24px">
<p>Opening… <a href="__TO__">Continue</a></p>
</body></html>
"""


def locked(html: str, title: str, heading: str, blurb: str, key: bytes, wrapped: dict, logo: str) -> str:
    cfg = {"salt": LOCK["salt"], "iterations": int(LOCK["iterations"])}
    data = seal(html.encode("utf-8"), key)
    return (LOCK_PAGE.replace("__TITLE__", title).replace("__HEADING__", heading).replace("__BLURB__", blurb)
            .replace("__LOGO__", logo).replace("__CFG__", json.dumps(cfg))
            .replace("__WRAP__", json.dumps({"iv": wrapped["iv"], "ct": wrapped["ct"]}))
            .replace("__DATA__", json.dumps(data)))


def write(rel: str, text: str):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    dk, wk = os.environ.get("HUB_DATA_KEY"), os.environ.get("HUB_WRAPPED_KEY")
    if not dk or not wk:
        sys.exit("Set HUB_DATA_KEY and HUB_WRAPPED_KEY (see the top of this file).")
    key, wrapped = base64.b64decode(dk), json.loads(wk)
    if PRIVATE.exists():
        src = json.loads(PRIVATE.read_text())
    else:
        src = json.loads(unseal(json.loads(SOURCE_ENC.read_text())["data"], key))
    for extra in sys.argv[1:]:
        rep = json.loads(Path(extra).read_text())
        src.setdefault("reports", {})[rep["month"]] = rep
    logo = b64((TOOLS / "logo.webp").read_bytes())
    pages = TOOLS / "pages"

    # 1. the hub
    hub = (pages / "hub.html").read_text().replace("__LOGO__", logo).replace("__SECTIONS__", json.dumps(src["catalog"]))
    write("index.html", locked(hub, "SPA Dashboards", "SPA Dashboards", "Every Saint Paul Agency dashboard in one place.", key, wrapped, logo))

    # 2. the Monthly Social Review
    review = (pages / "social-review.html").read_text().replace("__LOGO__", logo).replace("__REPORTS__", json.dumps(src["reports"]))
    write("team/monthly-social-review/index.html",
          locked(review, "Monthly Social Review", "Monthly Social Review", "Client numbers are locked.", key, wrapped, logo))

    # 3. descriptive forwarding links
    n = 0
    for sec in src["catalog"]:
        for item in sec["items"]:
            if item.get("forward"):
                write(item["path"].strip("/") + "/index.html", FORWARD.replace("__TO__", item["forward"]))
                n += 1

    # 4. sources, sealed for the next build
    write("data/source.enc", json.dumps({"v": 1, "wrap": wrapped, "data": seal(json.dumps(src).encode(), key)}))
    print(f"built hub, review ({', '.join(sorted(src['reports']))}), {n} forwarding links")


if __name__ == "__main__":
    main()
