#!/usr/bin/env python3
"""Converte source/artifact.html (formato do artefato do Claude) em web/index.html (página independente).

Uso: python3 tools/make_web.py
"""
import hashlib
import json
import pathlib
import re
import sys


import urllib.parse
_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="100" fill="#080913"/>'
        '<g fill="none" stroke-width="66" transform="translate(46 46) scale(.82)">'
        '<path d="M112 92H280M196 92V318A92 92 0 0 1 104 410H74" stroke="#22E6FF"/>'
        '<path d="M400 420H232M316 420V194A92 92 0 0 1 408 102H438" stroke="#FF2F7D"/></g></svg>')
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

# Ao voltar para o app já aberto, confere se há versão nova e recarrega (nunca com alguém digitando).
atualizar = r"""<script>(function(){
var atual=document.querySelector('meta[name="jj-versao"]').content,ult=0;
function checa(){
  if(document.visibilityState!=='visible'||Date.now()-ult<30000)return;
  var a=document.activeElement;if(a&&/INPUT|TEXTAREA/.test(a.tagName))return;
  ult=Date.now();
  fetch(location.pathname,{cache:'no-store'}).then(function(r){return r.text();}).then(function(t){
    var m=t.match(/name="jj-versao" content="([0-9a-f]+)"/);
    if(m&&m[1]!==atual)location.reload();
  }).catch(function(){});
}
document.addEventListener('visibilitychange',checa);
setInterval(checa,300000);
})();</script>"""

# A frase de source/novidade.txt é o que o aviso no celular mostra. Trocar a frase também conta como versão nova.
arquivo_novidade = root / 'source' / 'novidade.txt'
novidade = arquivo_novidade.read_text(encoding='utf-8').strip() if arquivo_novidade.exists() else ''
novidade = novidade or 'O Joga Junto foi atualizado.'

versao = hashlib.sha256((head + body + novidade).encode('utf-8')).hexdigest()[:12]
head_base += '<meta name="jj-versao" content="' + versao + '">\n'

html = head_base + head + '</head>\n<body>\n' + body.rstrip() + '\n' + sw + '\n' + atualizar + '\n</body>\n</html>\n'
(root / 'web').mkdir(exist_ok=True)
(root / 'web' / 'index.html').write_text(html, encoding='utf-8')
(root / 'web' / 'versao.json').write_text(json.dumps({'versao': versao, 'mensagem': novidade}, ensure_ascii=False) + '\n', encoding='utf-8')
print('web/index.html gerado (%d bytes)' % len(html))
