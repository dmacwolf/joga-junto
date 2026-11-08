#!/usr/bin/env python3
"""Converte source/artifact.html (formato do artefato do Claude) em web/index.html (página independente).

Uso: python3 tools/make_web.py
"""
import pathlib
import re
import sys


import urllib.parse
_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 108 108"><rect width="108" height="108" rx="22" fill="#080913"/>'
        '<g fill="none" stroke-width="8" stroke-linecap="round"><path d="M48,42V62Q48,76 36,76" stroke="#22E6FF"/>'
        '<path d="M72,42V62Q72,76 60,76" stroke="#FF2F7D"/></g><circle cx="48" cy="30" r="7.5" fill="#22E6FF"/>'
        '<circle cx="72" cy="30" r="7.5" fill="#FF2F7D"/></svg>')
FAVICON = urllib.parse.quote(_svg, safe='')

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'source' / 'artifact.html').read_text(encoding='utf-8')

src = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', src)

marker = '<div class="fx"'
if src.count(marker) != 1:
    sys.exit('marcador do corpo da página não encontrado')
head, body = src.split(marker, 1)
body = marker + body

head_base = (
    '<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<meta name="theme-color" content="#080913">\n'
    '<link rel="icon" href="data:image/svg+xml,' + FAVICON + '">\n'
    '<style>html{background:#080913;color-scheme:dark;-webkit-text-size-adjust:100%}'
    '[hidden]{display:none!important}img{max-width:100%}</style>\n'
)
sw = (
    "<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){"
    "navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>"
)

html = head_base + head + '</head>\n<body>\n' + body.rstrip() + '\n' + sw + '\n</body>\n</html>\n'
(root / 'web').mkdir(exist_ok=True)
(root / 'web' / 'index.html').write_text(html, encoding='utf-8')
print('web/index.html gerado (%d bytes)' % len(html))
