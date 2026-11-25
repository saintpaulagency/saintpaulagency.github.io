"""Standalone copy of a Claude Dashboard-type artifact: page files + current datasets + d3 + fonts/logo + a stand-in
for the dash runtime, in one HTML file (same approach as the CDF dash_build.py, generalised by client).
Usage: python3 -I rep_build.py CLIENT_DIR BRAND_DIR BRANDMAP.json CLIENT OUT.html
"""
import base64, glob, json, os, re, sys
C, B, BM, CLIENT, OUT = sys.argv[1:6]
def doc(p):
    d = json.load(open(p)); return d.get('data', d)
MIME = {'.webp': 'image/webp', '.woff2': 'font/woff2'}
brand = {os.path.basename(p).split('.')[0]: p for p in glob.glob(os.path.join(B, '*'))}
bmap = json.load(open(BM))[CLIENT]
page = doc(os.path.join(C, 'docs/files/index.html.json'))['text']
def blob(m):
    k = m.group(1)
    if k not in bmap: raise SystemExit('unknown asset in page: ' + k)
    p = brand[bmap[k]]
    return 'data:%s;base64,%s' % (MIME[os.path.splitext(p)[1]], base64.b64encode(open(p, 'rb').read()).decode())
page = re.sub(r'/_blob/([0-9a-f]{32})', blob, page)
assert '/_blob/' not in page
order = re.findall(r'<script src="([a-z_]+\.js)"></script>', page)
assert order == ['core.js', 'charts.js', 'timeline.js', 'calcs.js', 'next_calcs.js', 'next.js', 'pages.js'], order
safe = lambda s: s.replace('</script', '<\\/script')
for f in order:
    page = page.replace('<script src="%s"></script>' % f, '<script>\n' + safe(doc(os.path.join(C, 'docs/files', f + '.json'))['text']) + '\n</script>')
have = {os.path.basename(p).split('.')[0]: p for p in glob.glob(os.path.join(C, 'assets', '*'))}
data = {}
for p in sorted(glob.glob(os.path.join(C, 'docs/datasets/*.json'))):
    n = os.path.basename(p)[:-5]
    if n == 'camp_settings': continue
    aid = re.search(r'[0-9a-f]{32}', doc(p)['source']['url']).group(0)
    if aid not in have: raise SystemExit('dataset file not downloaded: %s %s' % (n, aid))
    data[n] = json.load(open(have[aid], encoding='utf-8-sig'))
params = {k: v for k, v in doc(os.path.join(C, 'docs/dash/params.json')).items() if not k.startswith('_')}
title = doc(os.path.join(C, 'docs/dash/meta.json')).get('title', 'Saint Paul Agency report')
runtime = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runtime.js')).read().replace('%PARAMS%', json.dumps(params))
through = max(r['date'] for r in data['daily'])
d3 = open(glob.glob(os.path.join(B, '41ed33ab7e5ddacceca2f9455c81b9d6.*'))[0], encoding='utf-8').read()
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>' + title + '</title>\n<meta name="robots" content="noindex, nofollow">\n<style>\n'
        ':root { --color-fg: #1f1e1d; --color-bg: #faf9f5; --color-panel: #ffffff; --color-border-line: #e5e2da; --color-fg-muted: #6b6a68; --cds-dur-slow: 240ms; --cds-ease-out: cubic-bezier(.2,.8,.2,1); }\n'
        '@media (prefers-color-scheme: dark) { :root { --color-fg: #f2f1ee; --color-bg: #262624; --color-panel: #30302e; --color-border-line: #444; --color-fg-muted: #a3a29f; } }\n'
        'html, body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: system-ui, sans-serif; }\n'
        '#dash-root { padding-inline: var(--dash-gutter, 24px); }\n@media (max-width: 599px) { #dash-root { padding-inline: 12px; } }\n'
        '.dash-skeleton { background: #ccc4; border-radius: 6px; }\n</style>\n'
        '<script>\n' + safe(d3) + '\n</script>\n'
        '<script>\nwindow.__DASH_DATA = ' + safe(json.dumps(data, separators=(',', ':'))) + ';\nwindow.__DASH_BUILT = ' + json.dumps({'through': through}) + ';\n</script>\n'
        '<script>\n' + runtime + '\n</script>\n</head>\n<body>\n<div id="dash-root" data-appifact-content>\n' + page + '\n</div>\n</body>\n</html>\n')
open(OUT, 'w', encoding='utf-8').write(html)
print(CLIENT, OUT, len(html.encode()), 'bytes |', len(data), 'datasets | through', through, '|', title)
