"""Pipeline: markdown → PDF diagramado + relatório de QA.

Uma função, cinco etapas, sem checkpoint no meio:

    ler o markdown → classificar o que ficou ambíguo → diagramar → conferir → entregar

O progresso é reportado por callback para a barra da interface.
"""

from __future__ import annotations

import html as _html
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from . import classificador, qa
from .catalogo import Bloco
from .conversao import converter
from .marcacao import Metadados, ler
from .renderizador import ResultadoRender, renderizar

MINIATURA_DPI = 42


@dataclass
class Entrega:
    pdf: bytes
    paginas: int
    relatorio: qa.Relatorio
    blocos: list[Bloco]
    pagina_por_bloco: dict[int, int]
    miniaturas: list[bytes] = field(default_factory=list)
    meta: Metadados | None = None
    aviso_de_revisao: str = (
        "Antes de publicar, este material precisa de validação profissional. "
        "O diagramador cuida da forma; a revisão clínica é sua e da equipe técnica."
    )


def _miniaturas(pdf: bytes) -> list[bytes]:
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    imagens = [pagina.get_pixmap(dpi=MINIATURA_DPI).tobytes("png") for pagina in doc]
    doc.close()
    return imagens


def gerar(
    fonte_markdown: str,
    psicologa: str,
    crp: str,
    correcoes: dict[int, str] | None = None,
    blocos_prontos: list[Bloco] | None = None,
    progresso=lambda *_: None,
) -> Entrega:
    """Do markdown ao PDF, sem parar no meio.

    `blocos_prontos` + `correcoes` servem à regeração: em vez de reclassificar,
    reaproveita a lista já classificada e troca só o tipo dos blocos corrigidos.
    """
    progresso("Lendo o markdown", 0.05)
    meta, blocos = ler(fonte_markdown)
    meta.psicologa = _html.escape(psicologa.strip(), quote=False)
    meta.crp = _html.escape(crp.strip(), quote=False)

    resultado_classificador = None
    if blocos_prontos is not None:
        blocos = [Bloco.de_json(b.para_json()) for b in blocos_prontos]
    else:
        progresso("Classificando os trechos", 0.2)
        resultado_classificador = classificador.classificar(blocos)

    for indice, tipo in (correcoes or {}).items():
        if 0 <= indice < len(blocos):
            blocos[indice] = converter(blocos[indice], tipo, procedencia="correcao_manual")
            blocos[indice].observacao = f"tipo trocado por você para {blocos[indice].rotulo}"

    progresso("Diagramando as páginas", 0.45)
    resultado: ResultadoRender = renderizar(meta, blocos, progresso=progresso)

    progresso("Conferindo o resultado", 0.9)
    relatorio = qa.verificar(
        resultado,
        fonte_markdown,
        documento_layout=resultado.documento,
        resultado_classificador=resultado_classificador,
        meta=meta,
        progresso=progresso,
    )

    progresso("Gerando as miniaturas", 0.99)
    return Entrega(
        pdf=resultado.pdf,
        paginas=resultado.paginas,
        relatorio=relatorio,
        blocos=resultado.blocos,
        pagina_por_bloco=resultado.pagina_por_bloco,
        miniaturas=_miniaturas(resultado.pdf),
        meta=meta,
    )
