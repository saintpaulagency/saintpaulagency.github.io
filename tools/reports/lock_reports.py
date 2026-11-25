"""Lock report pages with the SPA Dashboards password (same envelope lock as saintpaulagency.github.io).
Usage: HUB_DATA_KEY=... HUB_WRAPPED_KEY='{"iv","ct"}' python3 -I lock_reports.py HUB_BUILD_PY LOCK_JSON IN.html OUT.html
The page is AES-256-GCM encrypted with the hub data key; that key is stored only wrapped with the SPA Dashboards key.
The visible lock screen names no client."""
import base64, importlib.util, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
HUB, LOCKJ, IN, OUT = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('hubbuild', HUB); hb = importlib.util.module_from_spec(spec)
src = open(HUB).read(); tpl = src[src.index('LOCK_PAGE = """') + 15: src.index('"""\n\nFORWARD')]
lock = json.load(open(LOCKJ))
key = base64.b64decode(os.environ['HUB_DATA_KEY']); wrap = json.loads(os.environ['HUB_WRAPPED_KEY'])
logo = base64.b64encode(open(os.path.join(os.path.dirname(HUB), 'logo.webp'), 'rb').read()).decode()
html = open(IN, encoding='utf-8').read()
iv = os.urandom(12); data = {'iv': base64.b64encode(iv).decode(), 'ct': base64.b64encode(AESGCM(key).encrypt(iv, html.encode(), None)).decode()}
page = (tpl.replace('__TITLE__', 'Saint Paul Agency').replace('__HEADING__', 'Saint Paul Agency report')
        .replace('__BLURB__', 'This report is locked.').replace('__LOGO__', logo)
        .replace('__CFG__', json.dumps({'salt': lock['salt'], 'iterations': int(lock['iterations'])}))
        .replace('__WRAP__', json.dumps({'iv': wrap['iv'], 'ct': wrap['ct']})).replace('__DATA__', json.dumps(data)))
plain = re.sub(r'"ct": "[A-Za-z0-9+/=]{200,}"', '', page)
for w in ('Borton', 'Carlson', 'Dahl', 'Honda', 'Volvo', 'Toyota', 'VFV', 'WFW', 'Veterans', 'Wishes', 'Donation', 'donation', 'Microsoft'):
    assert w not in plain, 'client word outside the encrypted part: ' + w
os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, 'w', encoding='utf-8').write(page)
print(OUT, len(page), 'bytes')
