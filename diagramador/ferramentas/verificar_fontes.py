"""Confere que as fontes da marca chegam embutidas no PDF.

Roda no build da imagem. O WeasyPrint ignora `@font-face` em silêncio quando a
configuração de fonte não é passada explicitamente — o material sai inteiro, só
que na fonte do sistema. Isso já aconteceu uma vez; este script é o que impede
que aconteça de novo sem ninguém ver.

Uso: python3 diagramador/ferramentas/verificar_fontes.py
Sai com código 1 se alguma família da marca não estiver embutida.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "diagramador"))

import pymupdf  # noqa: E402
from weasyprint import HTML  # noqa: E402

from app.renderizador import _FONTES, _folhas  # noqa: E402

ESPERADAS = {"Poppins", "Manrope"}

PROVA = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"></head><body>
<p style="font-family: var(--fonte-leitura)">Leitura em Manrope: ação, coração, três.</p>
<p style="font-family: var(--fonte-titulo); font-weight: 600">Título em Poppins</p>
<p style="font-family: var(--fonte-display); font-weight: 700">Display</p>
</body></html>"""


def main() -> int:
    pdf = HTML(string=PROVA, base_url=str(RAIZ)).write_pdf(
        stylesheets=_folhas(), font_config=_FONTES
    )
    documento = pymupdf.open(stream=pdf, filetype="pdf")
    encontradas = {fonte[3] for pagina in documento for fonte in pagina.get_fonts()}
    documento.close()

    faltando = [
        familia
        for familia in ESPERADAS
        if not any(familia.lower() in nome.lower() for nome in encontradas)
    ]

    if faltando:
        print(f"FALHA: fontes da marca não embutidas: {', '.join(faltando)}", file=sys.stderr)
        print(f"       o PDF saiu com: {', '.join(sorted(encontradas)) or 'nenhuma'}", file=sys.stderr)
        return 1

    print(f"fontes embutidas: {', '.join(sorted(encontradas))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
