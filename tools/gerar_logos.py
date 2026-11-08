#!/usr/bin/env python3
"""Gera as propostas de logo em web/propostas/logo-*.svg.

Uso: python tools/gerar_logos.py
"""
import pathlib

C, M, V = '#22E6FF', '#FF2F7D', '#8A5CFF'
SAIDA = pathlib.Path(__file__).resolve().parent.parent / 'web' / 'propostas'

# Letra J (Russo One) em curvas, 190 de altura e 104,4 de largura.
J = ('M104.4 139.2C104.4 156.6 100.3 169.5 92.1 177.7C83.8 185.9 71.2 190 54.1 190'
     'C37.1 190 19.1 189.1 0 187.3V151.2C13.9 152.1 28.2 152.5 42.8 152.5'
     'C46.9 152.5 50.1 151.4 52.5 149.1C54.9 146.6 56.2 143.3 56.2 139.2V37.5H21.4V0H104.4Z')


def stops(lista):
    saida = []
    for s in lista:
        op = f' stop-opacity="{s[2]}"' if len(s) > 2 else ''
        saida.append(f'<stop offset="{s[0]}" stop-color="{s[1]}"{op}/>')
    return ''.join(saida)


def lin(nome, x1, y1, x2, y2, *lista):
    return (f'<linearGradient id="{nome}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'{stops(lista)}</linearGradient>')


def rad(nome, cx, cy, r, *lista):
    return (f'<radialGradient id="{nome}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}">'
            f'{stops(lista)}</radialGradient>')


def mistura(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(ca, cb))


def svg(defs, corpo):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" fill="none">'
            f'<defs>{defs}</defs>{corpo}</svg>\n')


def letra(x, y, escala, frente, perto, longe, passos=10, dx=1.0, dy=1.5):
    """Letra em bloco: camadas deslocadas formam a lateral, a frente vai por cima."""
    partes = []
    for i in range(passos, 0, -1):
        cor = mistura(perto, longe, (i - 1) / max(passos - 1, 1))
        partes.append(f'<path fill="{cor}" transform="translate({x + dx * i:.1f} {y + dy * i:.1f}) scale({escala})" d="{J}"/>')
    partes.append(f'<path fill="url(#{frente})" stroke="#fff" stroke-opacity=".35" stroke-width="1.5" '
                  f'transform="translate({x} {y}) scale({escala})" d="{J}"/>')
    return ''.join(partes)


def tubo(base, meio, brilho, d_base, d_meio, d_brilho):
    """Tubo com volume: faixa escura embaixo, cor no meio e brilho do lado da luz."""
    return (f'<g stroke-linecap="round"><path stroke="{base}" stroke-width="56" d="{d_base}"/>'
            f'<path stroke="{meio}" stroke-width="40" d="{d_meio}"/>'
            f'<path stroke="{brilho}" stroke-width="10" d="{d_brilho}"/></g>')


def alavanca():
    defs = (lin('rim', 56, 0, 456, 0, (0, C), (.5, V), (1, M))
            + lin('topo', 0, 332, 0, 452, (0, '#343884'), (1, '#15173F'))
            + lin('lado', 56, 0, 456, 0, (0, '#0B7AA3'), (.5, '#3A2A8F'), (1, '#A01358'))
            + lin('bola', 172, 0, 340, 0, (0, C), (.5, V), (1, M))
            + lin('gola', 186, 0, 326, 0, (0, '#0C9BD0'), (.5, '#5A3BD0'), (1, '#C21560'))
            + rad('luz', 226, 88, 190, (0, '#fff', .9), (.16, '#fff', .4), (.48, '#fff', 0), (.78, '#000', .22), (1, '#000', .55)))
    ciano_b = 'M224 224V316A72 72 0 0 1 152 388H122'
    rosa_b = 'M288 224V316A72 72 0 0 0 360 388H390'
    corpo = (
        '<g transform="translate(0 -8)">'
        '<path fill="url(#lado)" d="M56 392V428A200 60 0 0 0 456 428V392Z"/>'
        '<ellipse cx="256" cy="392" rx="200" ry="60" fill="url(#topo)" stroke="url(#rim)" stroke-width="6"/>'
        '<ellipse cx="256" cy="392" rx="158" ry="45" stroke="#fff" stroke-opacity=".08" stroke-width="3"/>'
        f'<g stroke="#05061A" stroke-opacity=".6" stroke-width="56" stroke-linecap="round" transform="translate(0 12)"><path d="{ciano_b}"/><path d="{rosa_b}"/></g>'
        + tubo('#0C9BD0', C, '#D4FCFF', ciano_b, 'M221 228V313A72 72 0 0 1 149 385H126', 'M211 232V305A72 72 0 0 1 139 377H128')
        + tubo('#C21560', M, '#FFD0E2', rosa_b, 'M285 228V313A72 72 0 0 0 357 385H386', 'M275 232V305A72 72 0 0 0 347 377H380')
        + '<ellipse cx="256" cy="214" rx="72" ry="19" fill="#090A20"/>'
        '<ellipse cx="256" cy="206" rx="72" ry="19" fill="url(#gola)"/>'
        '<circle cx="256" cy="118" r="86" fill="url(#bola)"/>'
        '<circle cx="256" cy="118" r="86" fill="url(#luz)"/>'
        '<ellipse cx="222" cy="82" rx="26" ry="15" fill="#fff" fill-opacity=".85" transform="rotate(-32 222 82)"/>'
        '</g>')
    return svg(defs, corpo)


def direcional():
    cruz = ('M158 48Q158 30 176 30H336Q354 30 354 48V138H444Q462 138 462 156V316Q462 334 444 334H354V424'
            'Q354 442 336 442H176Q158 442 158 424V334H68Q50 334 50 316V156Q50 138 68 138H158Z')
    defs = (lin('rim', 50, 30, 462, 442, (0, C), (.5, V), (1, M))
            + lin('topo', 0, 30, 0, 442, (0, '#383D8E'), (1, '#15173F'))
            + lin('lado', 50, 0, 462, 0, (0, '#0B7AA3'), (.5, '#3A2A8F'), (1, '#A01358'))
            + lin('fc', 0, 0, 0, 190, (0, '#CFFAFF'), (.42, C), (1, '#0FA6D8'))
            + lin('fm', 0, 0, 0, 190, (0, '#FFD0E2'), (.42, M), (1, '#C4135C')))
    lados = ''.join(f'<path fill="url(#lado)" transform="translate(0 {i})" d="{cruz}"/>' for i in range(34, 0, -2))
    setas = ''
    for ponta, cor in (('M256 58 284 94H228Z', C), ('M78 236 114 208V264Z', C), ('M434 236 398 264V208Z', M), ('M256 414 228 378H284Z', M)):
        setas += f'<path fill="#090A20" fill-opacity=".7" transform="translate(0 3)" d="{ponta}"/><path fill="{cor}" d="{ponta}"/>'
    corpo = (
        '<g transform="translate(0 4)">'
        f'{lados}<path fill="url(#topo)" stroke="url(#rim)" stroke-width="6" stroke-linejoin="round" d="{cruz}"/>'
        f'{setas}'
        + letra(157, 160, .895, 'fc', '#0B6C96', '#07395C')
        + letra(263, 136, .895, 'fm', '#A01358', '#560A33')
        + '</g>')
    return svg(defs, corpo)


def controle():
    corpo_d = ('M150 136H362C420 136 452 176 470 260C488 342 478 396 436 396C404 396 392 366 372 336H140'
               'C120 366 108 396 76 396C34 396 24 342 42 260C60 176 92 136 150 136Z')
    defs = (lin('rim', 30, 0, 482, 0, (0, C), (.5, V), (1, M))
            + lin('topo', 0, 136, 0, 396, (0, '#383D8E'), (1, '#15173F'))
            + lin('lado', 30, 0, 482, 0, (0, '#0B7AA3'), (.5, '#3A2A8F'), (1, '#A01358'))
            + rad('dc', 150, 208, 112, (0, '#E2FDFF'), (.3, C), (1, '#0B86B8'))
            + rad('dm', 306, 208, 112, (0, '#FFE0EC'), (.3, M), (1, '#B01055')))
    lados = ''.join(f'<path fill="url(#lado)" transform="translate(0 {i})" d="{corpo_d}"/>' for i in range(36, 0, -2))
    ombros = ('<rect x="104" y="108" width="104" height="48" rx="16" fill="#0C9BD0"/>'
              '<rect x="304" y="108" width="104" height="48" rx="16" fill="#C21560"/>')

    def analogico(cx, cy, cor_lado, gradiente, letra_x):
        camadas = ''.join(f'<circle cx="{cx}" cy="{cy + i}" r="70" fill="{cor_lado}"/>' for i in range(14, 0, -2))
        return (f'<ellipse cx="{cx}" cy="{cy + 12}" rx="80" ry="78" fill="#090A20"/>{camadas}'
                f'<circle cx="{cx}" cy="{cy}" r="70" fill="url(#{gradiente})"/>'
                f'<path fill="#fff" fill-opacity=".45" transform="translate({letra_x} {cy - 48 + 2}) scale(.505)" d="{J}"/>'
                f'<path fill="#090A20" transform="translate({letra_x} {cy - 48}) scale(.505)" d="{J}"/>')

    corpo = (
        '<g transform="translate(0 -22)">'
        f'{ombros}{lados}<path fill="url(#topo)" stroke="url(#rim)" stroke-width="8" stroke-linejoin="round" d="{corpo_d}"/>'
        + analogico(176, 232, '#0B6C96', 'dc', 150)
        + analogico(336, 232, '#A01358', 'dm', 310)
        + '</g>')
    return svg(defs, corpo)


# Opções anteriores: ficam guardadas de propósito, a pedido do dono do projeto.
def g3(nome, x1, y1, x2, y2):
    return lin(nome, x1, y1, x2, y2, (0, C), (.5, V), (1, M))


def eco():
    return svg('', f'<g stroke-width="64"><path stroke="{M}" d="M346 40V262A176 176 0 0 1 170 438H130"/>'
                   f'<path stroke="{C}" d="M236 40V262A66 66 0 0 1 170 328H130"/></g>')


def emblema():
    return svg(g3('g', 58, 28, 454, 484),
               '<path stroke="url(#g)" stroke-width="18" d="M256 28 454 142V370L256 484 58 370V142Z"/>'
               '<g transform="translate(256 256) scale(.94) translate(-239 -252)">'
               f'<path fill="{C}" d="M156 166 228 146V338L178 388H100V336H140L156 320Z"/>'
               f'<path fill="{M}" d="M306 136 378 116V308L328 358H250V306H290L306 290Z"/></g>')


def ligadura():
    return svg(g3('b', 118, 0, 420, 0),
               '<g transform="translate(53 0) skewX(-12)" stroke-width="64">'
               '<rect x="118" y="56" width="300" height="62" fill="url(#b)"/>'
               f'<path stroke="{C}" d="M190 118V300A72 72 0 0 1 118 372H92"/>'
               f'<path stroke="{M}" d="M350 118V362A96 96 0 0 1 254 458H150"/></g>')


def giro():
    d = 'M112 92H280M196 92V318A92 92 0 0 1 104 410H74'
    return svg('', f'<g stroke-width="66"><path stroke="{C}" d="{d}"/>'
                   f'<path stroke="{M}" transform="rotate(180 256 256)" d="{d}"/></g>')


def alavanca_plana():
    return svg(g3('h', 182, 0, 330, 0),
               '<circle cx="256" cy="112" r="74" fill="url(#h)"/>'
               f'<path stroke="{C}" stroke-width="56" d="M224 170V352A72 72 0 0 1 152 424H96"/>'
               f'<path stroke="{M}" stroke-width="56" d="M288 170V352A72 72 0 0 0 360 424H416"/>')


def direcional_plano():
    return svg(g3('g', 40, 40, 472, 472),
               '<path stroke="url(#g)" stroke-width="18" d="M166 40H346L472 166V346L346 472H166L40 346V166Z"/>'
               f'<path fill="{C}" d="M256 72 284 108H228Z"/><path fill="{C}" d="M72 256 108 228V284Z"/>'
               f'<path fill="{M}" d="M440 256 404 284V228Z"/><path fill="{M}" d="M256 440 228 404H284Z"/>'
               f'<path fill="{C}" transform="translate(146.6 175)" d="{J}"/>'
               f'<path fill="{M}" transform="translate(261 147)" d="{J}"/>')


def controle_plano():
    return svg(g3('g', 40, 40, 472, 472),
               '<path stroke="url(#g)" stroke-width="20" stroke-linejoin="round" d="M150 136H362C420 136 452 176 470 260'
               'C488 342 478 396 436 396C404 396 392 366 372 336H140C120 366 108 396 76 396C34 396 24 342 42 260C60 176 92 136 150 136Z"/>'
               f'<circle cx="178" cy="246" r="62" fill="{C}"/><circle cx="334" cy="246" r="62" fill="{M}"/>'
               f'<path fill="#080913" transform="translate(154.9 204) scale(.442)" d="{J}"/>'
               f'<path fill="#080913" transform="translate(310.9 204) scale(.442)" d="{J}"/>')


# Segunda rodada, a partir do comentário do cliente na Eco: mais jovem e longe da estrutura do logo da Juventus
# (J alto, traços retos e paralelos, pontas cortadas). Aqui tudo é baixo, largo e de ponta redonda.
def sorriso():
    fora = 'M366 118V250C366 336 300 392 222 392C170 392 130 366 112 322'
    dentro = 'M238 118V220C238 262 212 286 180 286C160 286 146 278 136 262'
    return svg('', '<g stroke-width="58" stroke-linecap="round" transform="rotate(-8 256 256)">'
                   f'<path stroke="{M}" d="{fora}"/><path stroke="{C}" d="{dentro}"/></g>')


def encostados():
    frente = 'M346 150V318A78 78 0 0 1 268 396H232'
    giro_f = 'rotate(10 340 260)'
    defs = ('<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">'
            '<rect width="512" height="512" fill="#fff"/>'
            f'<path stroke="#000" stroke-width="112" stroke-linecap="round" transform="{giro_f}" d="{frente}"/></mask>')
    return svg(defs, '<g stroke-width="84" stroke-linecap="round">'
                     f'<path stroke="{C}" mask="url(#m)" d="M206 118V292A78 78 0 0 1 128 370H116"/>'
                     f'<path stroke="{M}" transform="{giro_f}" d="{frente}"/></g>')


def ponto():
    fora = ('M378 80C392 80 402 90 402 104C404 290 322 440 170 440C152 440 140 428 140 412'
            'C140 396 152 384 170 384C262 380 352 284 354 104C354 90 364 80 378 80Z')
    return svg('', f'<path fill="{M}" d="{fora}"/>'
                   f'<path stroke="{C}" stroke-width="56" stroke-linecap="round" d="M270 110C270 200 250 276 196 300"/>'
                   f'<circle cx="128" cy="312" r="34" fill="{C}"/>')


# Aprovada pelo cliente em 08/11/2026: a Giro, um J e outro J de cabeça para baixo.
NOVAS = (('logo-aprovada', giro),)
DESCARTADAS = (('logo-1', alavanca), ('logo-2', direcional), ('logo-3', controle),
               ('logo-4', eco), ('logo-5', emblema), ('logo-6', ligadura),
               ('nova-sorriso', sorriso), ('nova-encostados', encostados), ('nova-ponto', ponto),
               ('anterior-alavanca-plana', alavanca_plana),
               ('anterior-direcional-plano', direcional_plano), ('anterior-controle-plano', controle_plano))

(SAIDA / 'descartadas').mkdir(parents=True, exist_ok=True)
for pasta, lista in ((SAIDA, NOVAS), (SAIDA / 'descartadas', DESCARTADAS)):
    for nome, funcao in lista:
        texto = funcao()
        (pasta / f'{nome}.svg').write_text(texto, encoding='utf-8', newline='\n')
        print(pasta.name, nome, len(texto), 'bytes')
