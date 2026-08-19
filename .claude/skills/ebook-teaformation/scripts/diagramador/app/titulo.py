"""Título de capa com contorno, no tratamento medido nas cartilhas.

WeasyPrint não implementa `-webkit-text-stroke` nem `text-shadow`, então o
contorno é feito em SVG: uma passada só de traço, outra só de preenchimento (o
`paint-order` também não é honrado, daí as duas passadas).

O tamanho não é escolhido em runtime: começa no token `capa_titulo` (46pt) e só
diminui, em passos de 2pt, se o título não couber na largura de conteúdo. A
largura é medida de verdade, com as métricas da fonte.
"""

from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont

RAIZ = Path(__file__).resolve().parents[2]
TOKENS = json.loads((RAIZ / "design" / "tokens.json").read_text(encoding="utf-8"))
FONTE = RAIZ / "assets" / "fontes" / "Poppins-Bold.ttf"

ESCALA = TOKENS["tipografia"]["escala"]["capa_titulo"]
TAMANHO_MAXIMO = float(ESCALA["pt"])
ENTRELINHA = float(ESCALA["altura_linha"])
TRACKING = float(ESCALA.get("tracking_em", 0))
CONTORNO_EM = float(ESCALA["contorno"]["largura_em"])
TAMANHO_MINIMO = 24.0
MAXIMO_DE_LINHAS = 3

MM_EM_PT = 72 / 25.4


@lru_cache(maxsize=1)
def _metricas() -> tuple[dict[int, int], int]:
    fonte = TTFont(str(FONTE))
    cmap = fonte.getBestCmap()
    hmtx = fonte["hmtx"]
    upem = fonte["head"].unitsPerEm
    larguras: dict[int, int] = {}
    for codigo, nome in cmap.items():
        larguras[codigo] = hmtx[nome][0]
    return larguras, upem


def largura_em_pt(texto: str, tamanho: float) -> float:
    larguras, upem = _metricas()
    padrao = larguras.get(ord("n"), upem // 2)
    total = sum(larguras.get(ord(c), padrao) for c in texto)
    avanco = total / upem * tamanho
    return avanco + TRACKING * tamanho * max(len(texto) - 1, 0)


def quebrar(texto: str, tamanho: float, largura_pt: float) -> list[str]:
    """Quebra em até MAXIMO_DE_LINHAS linhas, sem estourar a largura."""
    palavras = texto.split()
    linhas: list[str] = []
    atual = ""
    for palavra in palavras:
        tentativa = f"{atual} {palavra}".strip()
        if atual and largura_em_pt(tentativa, tamanho) > largura_pt:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    if atual:
        linhas.append(atual)
    return linhas


def montar(texto: str, largura_mm: float, cor_contorno: str, cor_preenchimento: str) -> str:
    """SVG do título já ajustado à largura disponível."""
    texto = " ".join(texto.split())
    if not texto:
        return ""

    largura_pt = largura_mm * MM_EM_PT
    tamanho = TAMANHO_MAXIMO
    linhas = quebrar(texto, tamanho, largura_pt)

    while tamanho > TAMANHO_MINIMO and (
        len(linhas) > MAXIMO_DE_LINHAS
        or max(largura_em_pt(linha, tamanho) for linha in linhas) > largura_pt
    ):
        tamanho -= 2
        linhas = quebrar(texto, tamanho, largura_pt)

    traco = tamanho * CONTORNO_EM
    avanco = tamanho * ENTRELINHA
    altura = avanco * len(linhas) + traco * 2
    linha_base = tamanho * 0.78 + traco

    def textos(atributos: str) -> str:
        return "\n".join(
            f'    <text x="{largura_pt / 2:.2f}" y="{linha_base + indice * avanco:.2f}" {atributos}>'
            f"{html.escape(linha)}</text>"
            for indice, linha in enumerate(linhas)
        )

    letra = f'letter-spacing="{TRACKING * tamanho:.2f}"' if TRACKING else ""
    grupo = (
        f'font-family="Poppins" font-weight="700" font-size="{tamanho:.1f}" '
        f'text-anchor="middle" {letra}'
    )
    atributos_traco = (
        f'fill="none" stroke="{cor_contorno}" stroke-width="{traco:.2f}" stroke-linejoin="round"'
    )
    atributos_fill = f'fill="{cor_preenchimento}"'

    return "\n".join(
        [
            f'<svg class="capa-titulo-svg" viewBox="0 0 {largura_pt:.2f} {altura:.2f}"'
            f' width="{largura_mm:.2f}mm" height="{altura / MM_EM_PT:.2f}mm"'
            f' xmlns="http://www.w3.org/2000/svg">',
            f"  <g {grupo}>",
            textos(atributos_traco),
            textos(atributos_fill),
            "  </g>",
            "</svg>",
        ]
    )
