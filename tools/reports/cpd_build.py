"""Standalone copy of the WFW + CW CPD Levers Claude dashboard (connector loaders + page-drawn charts).
Usage: python3 -I cpd_build.py CPD_DIR SHEETS.json BRAND_DIR OUT.html"""
import glob, json, os, re, sys
C, SH, B, OUT = sys.argv[1:5]
doc = lambda p: (lambda d: d.get('data', d))(json.load(open(p)))
page = doc(os.path.join(C, 'docs/files/index.html.json'))['text']
assert '/_blob/' not in page and '<script src' not in page
sheets = json.load(open(SH)); have = {os.path.basename(p).split('.')[0]: p for p in glob.glob(os.path.join(C, 'assets/*'))}
files, answers = {}, {}
for p in sorted(glob.glob(os.path.join(C, 'docs/datasets/*.json'))):
    n = os.path.basename(p)[:-5]; src = doc(p)['source']
    if src['kind'] == 'file':
        files[n] = json.load(open(have[re.search(r'[0-9a-f]{32}', src['url']).group(0)]))
    else:
        answers[n] = sheets[src['args']['range']]
title = doc(os.path.join(C, 'docs/dash/meta.json'))['title']
safe = lambda s: s.replace('</script', '<\\/script')
d3 = open(glob.glob(os.path.join(B, '41ed33ab7e5ddacceca2f9455c81b9d6.*'))[0]).read()
rt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runtime_draw.js')).read()
through = max(r[0] for r in answers['donations']['values'][1:])
tokens = """
:root { --color-fg:#14181f; --color-bg:#f6f7f9; --color-panel:#ffffff; --color-border-line:#dfe3ea; --color-fg-muted:#5b6472; --color-ok:#0B7A3B; --color-bad:#C42B1C; --color-warn:#9a6200;
  --cds-text-secondary:#5b6472; --cds-border:#dfe3ea; --cds-chart-axis:#8a93a3; --cds-chart-grid:#e9ecf1; --cds-chart-muted:#b7bec9; --cds-chart-reference:#8a93a3;
  --cds-surface-popover:#ffffff; --cds-shadow-popover:0 6px 24px rgba(14,24,48,.14); --cds-radius:12px;
  --cds-font-size-title:34px; --cds-font-size-heading:22px; --cds-font-size-body:17px; --cds-font-size-caption:14px; --cds-font-weight-medium:600;
  --cds-gap-xs:4px; --cds-gap-sm:8px; --cds-gap-md:14px; --cds-gap-xl:32px; --cds-pad-sm:8px; --cds-pad-md:14px; --cds-pad-lg:20px;
  --font-anthropic-sans: system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; --font-anthropic-serif: Georgia,"Times New Roman",serif; --cds-dur-slow:240ms; --cds-ease-out:cubic-bezier(.2,.8,.2,1); color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --color-fg:#eef1f6; --color-bg:#10141b; --color-panel:#181d26; --color-border-line:#2b3240; --color-fg-muted:#a4adbb; --color-ok:#5fd08f; --color-bad:#ff7a6b; --color-warn:#f2b34c;
  --cds-text-secondary:#a4adbb; --cds-border:#2b3240; --cds-chart-axis:#7d8696; --cds-chart-grid:#252c38; --cds-chart-muted:#5a6272; --cds-chart-reference:#7d8696; --cds-surface-popover:#1d2330; color-scheme: dark; } }
html, body { margin:0; background:var(--color-bg); color:var(--color-fg); font-family:var(--font-anthropic-sans); }
#dash-root { max-width:1100px; margin:0 auto; padding:24px max(16px, env(safe-area-inset-left,0px)) 48px max(16px, env(safe-area-inset-right,0px)); }
.dash-skeleton { background:#ccc4; border-radius:6px; }
"""
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>' + title + '</title>\n<meta name="robots" content="noindex, nofollow">\n<style>' + tokens + '</style>\n'
        '<script>\n' + safe(d3) + '\n</script>\n<script>\nwindow.__DASH_FILES = ' + safe(json.dumps(files, separators=(',', ':'))) + ';\nwindow.__DASH_ANSWERS = ' + safe(json.dumps(answers, separators=(',', ':'))) + ';\nwindow.__DASH_BUILT = ' + json.dumps({'through': through}) + ';\n</script>\n'
        '<script>\n' + rt + '\n</script>\n</head>\n<body>\n<div id="dash-root">\n' + page + '\n</div>\n</body>\n</html>\n')
open(OUT, 'w').write(html); print(OUT, len(html), 'bytes | donations through', through, '| files', sorted(files), '| sheets', sorted(answers))
