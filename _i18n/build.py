#!/usr/bin/env python3
"""Build en/zh/ko versions of the RÊVE DOJO and Backspin Tokyo sites.

Usage: python3 build.py <reve_out_dir> <bst_out_dir>
Japanese source pages are read from /home/claude/site and /home/claude/bst_site.
Japanese pages in the output dirs get the language switcher; translated pages
are written to <out>/<lang>/.
"""
import re, sys, os, glob
from seg import JP

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['ja', 'en', 'zh', 'ko']
HTML_LANG = {'ja': 'ja', 'en': 'en', 'zh': 'zh-Hans', 'ko': 'ko'}
LABEL = {'ja': '日本語', 'en': 'English', 'zh': '简体中文', 'ko': '한국어'}
SHORT = {'ja': 'JA', 'en': 'EN', 'zh': '中文', 'ko': '한국어'}
FONT = {'zh': ('SC', 'SC'), 'ko': ('KR', 'KR')}

def load(files):
    d = {}
    for f in files:
        cur = None
        for line in open(os.path.join(HERE, f), encoding='utf-8'):
            line = line.rstrip('\n')
            if line.startswith('= '):
                cur = line[2:]; d[cur] = {}
            elif cur is not None and line[:4] in ('en: ', 'zh: ', 'ko: '):
                d[cur][line[:2]] = line[4:]
    return d

SEG = re.compile(r"[^<>'\"`\n]+")

def translate(text, tr, lang, missing):
    out = []
    for line in text.split('\n'):
        if 'JSON.stringify({' in line:   # keep FormSubmit field names / subject in Japanese
            out.append(line); continue
        def rep(m):
            s = m.group(0)
            core = s.strip()
            if not core or not JP.search(core):
                return s
            t = tr.get(core, {}).get(lang)
            if t is None:
                missing.add(core); return s
            lead = s[:len(s) - len(s.lstrip())]
            trail = s[len(s.rstrip()):]
            return lead + t + trail
        out.append(SEG.sub(rep, line))
    return '\n'.join(out)

def page_href(cur, target, page):
    name = '' if page == 'index.html' else page
    if cur == 'ja':
        return (name or './') if target == 'ja' else f'{target}/{name}'
    return (f'../{name}' if name else '../') if target == 'ja' else f'../{target}/{name}'

SWITCH_CSS = """<style id="lsw-css">
.lsw{position:relative;font:500 12px/1 "Inter",system-ui,sans-serif;letter-spacing:.06em}
.lsw summary{list-style:none;display:flex;align-items:center;gap:6px;height:40px;padding:0 12px;border:1px solid rgba(255,255,255,.32);color:inherit;cursor:pointer;border-radius:2px;white-space:nowrap}
.lsw summary::-webkit-details-marker{display:none}
.lsw summary:hover{border-color:rgba(255,255,255,.7)}
.lsw summary svg{width:15px;height:15px;flex:none}
.lsw ul{position:absolute;right:0;top:calc(100% + 6px);margin:0;padding:6px 0;list-style:none;background:#fff;min-width:150px;box-shadow:0 12px 32px rgba(0,0,0,.22);border-radius:2px;z-index:200}
.lsw li a{display:block;padding:10px 16px;color:#1a1a1a;text-decoration:none;font-size:14px;letter-spacing:.02em}
.lsw li a:hover{background:#f2f2f2}
.lsw li a[aria-current]{font-weight:700;color:#B91C1C}
@media(max-width:520px){.lsw summary{padding:0 9px}.lsw .lsw-t{display:none}}
</style>"""

def switcher(cur, page):
    items = ''.join(
        f'<li><a href="{page_href(cur, l, page)}" hreflang="{HTML_LANG[l]}" lang="{HTML_LANG[l]}"'
        + (' aria-current="true"' if l == cur else '') + f'>{LABEL[l]}</a></li>' for l in LANGS)
    globe = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'
             '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>')
    return (f'<details class="lsw"><summary aria-label="Language / 言語">{globe}'
            f'<span class="lsw-t">{SHORT[cur]}</span></summary><ul>{items}</ul></details>')

def head_extra(cur, page, base):
    name = '' if page == 'index.html' else page
    alts = ''.join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}{"" if l == "ja" else l + "/"}{name}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{base}{name}">'
    extra = alts + SWITCH_CSS
    if cur != 'ja':
        extra += ('<style>nav.main a,.hd-cta,.logo small{white-space:nowrap}nav.main{gap:18px}.prices div{column-gap:10px}'
                  '@media(max-width:1280px){nav.main{display:none}#menuBtn{display:grid;place-items:center}}</style>')
    if cur == 'ko':
        extra += '<style>body{word-break:keep-all;overflow-wrap:anywhere}</style>'
    if cur == 'en':
        extra += '<style>.card .en,.coach .en{display:none}</style>'
    if cur in FONT:
        s, _ = FONT[cur]
        extra += (f'<style>:root{{--serif:"Cormorant Garamond","Noto Serif {s}",serif;'
                  f'--jserif:"Noto Serif {s}",serif;--sans:"Inter","Noto Sans {s}",sans-serif}}'
                  f'body{{font-family:"Inter","Noto Sans {s}",sans-serif}}</style>')
    # close <details> when clicking elsewhere
    extra += ('<script>document.addEventListener("click",function(e){document.querySelectorAll("details.lsw[open]")'
              '.forEach(function(d){if(!d.contains(e.target))d.removeAttribute("open")})});</script>')
    return extra

def localize(html, cur, site):
    if cur == 'ja':
        return html
    html = re.sub(r'<html lang="ja"', f'<html lang="{HTML_LANG[cur]}"', html, count=1)
    html = re.sub(r'(?<![\w/.:-])(images|css)/', r'../\1/', html)
    if cur in FONT:
        s, _ = FONT[cur]
        html = html.replace('Noto+Serif+JP', f'Noto+Serif+{s}').replace('Noto+Sans+JP', f'Noto+Sans+{s}')
        html = html.replace('"Noto Sans JP"', f'"Noto Sans {s}"').replace("'Noto Sans JP'", f"'Noto Sans {s}'")
        html = html.replace('"Noto Serif JP"', f'"Noto Serif {s}"').replace("'Noto Serif JP'", f"'Noto Serif {s}'")
    if site == 'reve':
        html = html.replace('https://backspin-tokyo.com/', f'https://backspin-tokyo.com/{cur}/')
    else:
        html = html.replace('https://revedojo.github.io/yoyaku/', '@@YOYAKU@@')
        html = html.replace('https://revedojo.github.io/', f'https://revedojo.github.io/{cur}/')
        html = html.replace('@@YOYAKU@@', 'https://revedojo.github.io/yoyaku/')
    return html

def insert_switcher(html, cur, page, site, base):
    sw = switcher(cur, page)
    if site == 'reve':
        html, n = re.subn(r'(<a class="btn btn-red hd-cta")', sw + r'\1', html, count=1)
    else:
        html, n = re.subn(r'(<a href="#reserve" class="bg-amberPub)', sw + r'\1', html, count=1)
        # logo + nav + Day/Night switch + language + book do not fit in the 1280px container:
        # keep the nav in the menu drawer at every width
        html = html.replace('class="hidden xl:flex items-center gap-6', 'class="hidden items-center gap-6', 1)
        html = html.replace('class="xl:hidden p-2 border', 'class="p-2 border', 1)
        html = html.replace('class="hidden xl:hidden bg-pubWarm', 'class="hidden bg-pubWarm', 1)
        html = html.replace('</head>', '<style>#btnDayMode,#btnNightMode,header nav a{white-space:nowrap}@media(max-width:480px){header a.group .leading-tight>div:nth-child(2){display:none}header .lsw+a[href="#reserve"]{display:none}}</style></head>', 1)
    assert n == 1, (site, page, 'switcher anchor not found')
    html = html.replace('</head>', head_extra(cur, page, base) + '\n</head>', 1)
    return html

SITES = {
    'reve': dict(src='/home/claude/site', pages=['index.html', 'results.html', 'shop.html', 'supporters.html', 'tokushoho.html'],
                 tr=['tr_reve_index.txt', 'tr_reve_results.txt', 'tr_reve_other.txt'], base='https://revedojo.net/'),
    'bst': dict(src='/home/claude/bst_site', pages=['index.html'], tr=['tr_bst.txt'], base='https://backspin-tokyo.com/'),
}

def build(site, out):
    cfg = SITES[site]
    tr = load(cfg['tr'])
    missing = {}
    for page in cfg['pages']:
        src = open(os.path.join(cfg['src'], page), encoding='utf-8').read()
        for lang in LANGS:
            miss = set()
            html = src if lang == 'ja' else translate(src, tr, lang, miss)
            html = localize(html, lang, site)
            html = insert_switcher(html, lang, page, site, cfg['base'])
            d = out if lang == 'ja' else os.path.join(out, lang)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, page), 'w', encoding='utf-8').write(html)
            if miss: missing.setdefault(lang, set()).update(miss)
    return missing

if __name__ == '__main__':
    for site, out in zip(['reve', 'bst'], sys.argv[1:3]):
        m = build(site, out)
        for lang, segs in m.items():
            print(site, lang, 'untranslated:', len(segs))
            for s in sorted(segs): print('   ', s[:80])
