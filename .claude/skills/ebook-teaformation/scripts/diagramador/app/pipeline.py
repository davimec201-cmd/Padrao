"""Pipeline: markdown → PDF diagramado + relatório de QA.

Uma função, cinco etapas, sem checkpoint no meio:

    ler o markdown → classificar o que ficou ambíguo → diagramar → conferir → entregar

A classificação é a única etapa que precisa de um modelo, e ela vem de fora: quem
chama passa os rótulos já decididos em `classificacoes`. É assim que o trabalho
acontece dentro de uma sessão, sem chave de API. `usar_api=True` existe para
automação sem ninguém na sala.
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
    classificacoes: list[dict] | None = None,
    usar_api: bool = False,
    especialidade: str = "",
    progresso=lambda *_: None,
) -> Entrega:
    """Do markdown ao PDF, sem parar no meio.

    `classificacoes` são os rótulos já decididos (na sessão ou por outro meio);
    `blocos_prontos` + `correcoes` servem à regeração, reaproveitando a lista já
    classificada e trocando só o tipo dos blocos corrigidos.

    Sem nenhum dos dois, os trechos sem diretiva ficam genéricos e o relatório
    lista cada um. O PDF sai igual — o que muda é quanto dele foi decidido.
    """
    progresso("Lendo o markdown", 0.05)
    meta, blocos = ler(fonte_markdown)
    if psicologa.strip():
        meta.psicologa = _html.escape(psicologa.strip(), quote=False)
    if crp.strip():
        meta.crp = _html.escape(crp.strip(), quote=False)
    if especialidade.strip():
        meta.especialidade = _html.escape(especialidade.strip(), quote=False)

    for indice, bloco in enumerate(blocos):
        bloco.indice_fonte = indice

    resultado_classificador = None
    if blocos_prontos is not None:
        blocos = [Bloco.de_json(b.para_json()) for b in blocos_prontos]
    elif classificacoes is not None:
        progresso("Aplicando a classificação", 0.2)
        resultado_classificador = classificador.aplicar(blocos, classificacoes)
    elif usar_api:
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
