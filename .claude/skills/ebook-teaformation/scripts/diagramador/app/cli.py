"""Linha de comando do diagramador: markdown → PDF + relatório.

É por aqui que o trabalho acontece dentro de uma sessão. O fluxo tem dois
passos, e o segundo é o único obrigatório:

    1. python3 diagramar.py material.md --trechos
       Lista, em JSON, os trechos que o markdown não tipou sozinho. Quem está
       na sessão lê, decide um rótulo do catálogo para cada um e grava o JSON
       da resposta.

    2. python3 diagramar.py material.md --classificacao classificacao.json
       Diagrama, confere e entrega: PDF, relatório de QA e miniaturas.

Sem o passo 1 o PDF sai igual — os trechos sem diretiva ficam na seção genérica
e cada caso entra no relatório. O que muda é quanto do material foi decidido.

Código de saída: 0 se passou, 2 se o PDF saiu mas o QA achou falha crítica.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SUPERVISAO = json.loads(
    (RAIZ / "design" / "tokens.json").read_text(encoding="utf-8")
)["regras_do_material"]["supervisao_tecnica"]

MINIATURA_DPI = 90  # dá para ler o título de uma página nesta escala

SINAL = {"ok": "ok   ", "aviso": "aviso", "falha": "FALHA"}


def _sem_dependencias() -> str | None:
    faltando = []
    for modulo, pacote in (
        ("weasyprint", "weasyprint"),
        ("pymupdf", "pymupdf"),
        ("jinja2", "jinja2"),
        ("fontTools", "fonttools"),
        ("numpy", "numpy"),
    ):
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(pacote)
    if not faltando:
        return None
    return (
        "faltam dependências: " + ", ".join(faltando) + "\n\n"
        "  pip install " + " ".join(faltando) + "\n\n"
        "O WeasyPrint também precisa de bibliotecas de sistema (Pango, Cairo,\n"
        "fontconfig). No Debian/Ubuntu:\n\n"
        "  apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libcairo2 "
        "libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info"
    )


def _relatorio_em_markdown(entrega, meta, origem: Path) -> str:
    relatorio = entrega.relatorio
    linhas = [
        f"# QA — {meta.titulo or origem.stem}",
        "",
        f"- Origem: `{origem.name}`",
        f"- Páginas: {entrega.paginas}",
        f"- Tema: {meta.tema_valido}",
        f"- Personagem: {meta.personagem if meta.pediu_personagem else 'nenhum (padrão)'}",
        f"- Supervisão: {meta.psicologa} · CRP {meta.crp}",
        "",
        f"**{len(relatorio.achados) - len(relatorio.falhas) - len(relatorio.avisos)} ok · "
        f"{len(relatorio.avisos)} aviso(s) · {len(relatorio.falhas)} falha(s)**",
        "",
    ]
    if relatorio.tem_critico:
        linhas += ["> Há falha crítica. Não publique sem resolver.", ""]

    for achado in relatorio.achados:
        marca = {"ok": "ok", "aviso": "aviso", "falha": "falha"}[achado.estado]
        titulo = f"## {achado.verificacao} — {marca}"
        if achado.critico:
            titulo += " (crítico)"
        linhas += [titulo, "", achado.resumo, ""]
        if achado.paginas:
            paginas = ", ".join(str(p) for p in sorted(set(achado.paginas))[:40])
            linhas += [f"Páginas: {paginas}", ""]
        for detalhe in achado.detalhes[:40]:
            linhas.append(f"- {detalhe}")
        if achado.detalhes:
            linhas.append("")

    linhas += ["---", "", entrega.aviso_de_revisao, ""]
    return "\n".join(linhas)


def _resumo_no_terminal(entrega, meta, origem, saidas: dict[str, str]) -> None:
    relatorio = entrega.relatorio
    personagem = meta.personagem if meta.pediu_personagem else "sem personagem"
    print(
        f"\n{meta.titulo or origem.stem} — {entrega.paginas} páginas, "
        f"tema {meta.tema_valido}, {personagem}"
    )
    for rotulo, caminho in saidas.items():
        print(f"  {rotulo:<12} {caminho}")

    verdes = len(relatorio.achados) - len(relatorio.falhas) - len(relatorio.avisos)
    print(
        f"\nQA: {verdes} ok · {len(relatorio.avisos)} aviso(s) · "
        f"{len(relatorio.falhas)} falha(s)"
    )
    for achado in relatorio.falhas + relatorio.avisos:
        extra = " (crítico)" if achado.critico else ""
        print(f"  {SINAL[achado.estado]} {achado.verificacao}{extra} — {achado.resumo}")
        for detalhe in achado.detalhes[:6]:
            print(f"         · {detalhe}")
        if len(achado.detalhes) > 6:
            print(f"         · (+{len(achado.detalhes) - 6} no relatório)")

    print(f"\n{entrega.aviso_de_revisao}")


def _ler_json(caminho: str | None):
    if not caminho:
        return None
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def _classificacoes(bruto) -> list[dict]:
    """Aceita a lista direta ou o objeto `{"classificacoes": [...]}`."""
    if isinstance(bruto, dict):
        return bruto.get("classificacoes", [])
    return bruto or []


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(
        prog="diagramar.py",
        description="Diagrama um markdown no padrão TEA Formation.",
    )
    analisador.add_argument("markdown", help="arquivo .md do material")
    analisador.add_argument(
        "--trechos",
        action="store_true",
        help="lista em JSON os trechos que precisam de rótulo, e sai sem renderizar",
    )
    analisador.add_argument(
        "--classificacao", help="JSON com os rótulos decididos na sessão"
    )
    analisador.add_argument(
        "--correcoes",
        help='JSON {"7": "caixa_atencao"} para trocar o tipo de um bloco à mão',
    )
    analisador.add_argument("--saida", help="caminho do PDF (padrão: ao lado do .md)")
    analisador.add_argument(
        "--supervisao", default="", help=f"nome (padrão: {SUPERVISAO['nome']})"
    )
    analisador.add_argument(
        "--crp", default="", help=f"CRP (padrão: {SUPERVISAO['crp']})"
    )
    analisador.add_argument(
        "--sem-miniaturas", action="store_true", help="não gravar as imagens das páginas"
    )
    analisador.add_argument(
        "--blocos", action="store_true", help="gravar também a lista de blocos em JSON"
    )
    analisador.add_argument(
        "--json", action="store_true", help="gravar o relatório também em JSON"
    )
    analisador.add_argument(
        "--usar-api",
        action="store_true",
        help="classificar chamando a API (para automação; na sessão não precisa)",
    )
    opcoes = analisador.parse_args(argumentos)

    problema = _sem_dependencias()
    if problema:
        print(problema, file=sys.stderr)
        return 1

    origem = Path(opcoes.markdown)
    if not origem.is_file():
        print(f"não encontrei {origem}", file=sys.stderr)
        return 1
    fonte = origem.read_text(encoding="utf-8")

    from .classificador import pedido
    from .marcacao import ler
    from .pipeline import gerar

    if opcoes.trechos:
        _, blocos = ler(fonte)
        bruto = pedido(blocos)
        print(
            json.dumps(
                {
                    "trechos": bruto["trechos"],
                    "tipos_permitidos": bruto["tipos_permitidos"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    correcoes = {int(k): v for k, v in (_ler_json(opcoes.correcoes) or {}).items()}
    classificacoes = (
        _classificacoes(_ler_json(opcoes.classificacao))
        if opcoes.classificacao
        else None
    )

    entrega = gerar(
        fonte,
        opcoes.supervisao or SUPERVISAO["nome"],
        opcoes.crp or SUPERVISAO["crp"],
        correcoes=correcoes,
        classificacoes=classificacoes,
        usar_api=opcoes.usar_api,
        especialidade=SUPERVISAO["especialidade"],
    )

    pdf = Path(opcoes.saida) if opcoes.saida else origem.with_suffix(".pdf")
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(entrega.pdf)

    relatorio_md = pdf.with_name(f"{pdf.stem}-qa.md")
    relatorio_md.write_text(
        _relatorio_em_markdown(entrega, entrega.meta, origem), encoding="utf-8"
    )

    saidas = {"PDF": str(pdf), "Relatório": str(relatorio_md)}

    if not opcoes.sem_miniaturas:
        pasta = pdf.with_name(f"{pdf.stem}-paginas")
        pasta.mkdir(exist_ok=True)
        for antiga in pasta.glob("p*.png"):
            antiga.unlink()
        for numero, imagem in enumerate(_miniaturas(entrega.pdf), start=1):
            (pasta / f"p{numero:02d}.png").write_bytes(imagem)
        saidas["Miniaturas"] = f"{pasta}/ ({entrega.paginas} imagens)"

    if opcoes.json:
        alvo = pdf.with_name(f"{pdf.stem}-qa.json")
        alvo.write_text(
            json.dumps(entrega.relatorio.para_json(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        saidas["QA em JSON"] = str(alvo)

    if opcoes.blocos:
        alvo = pdf.with_name(f"{pdf.stem}-blocos.json")
        alvo.write_text(
            json.dumps(
                [
                    dict(b.para_json(), pagina=entrega.pagina_por_bloco.get(i))
                    for i, b in enumerate(entrega.blocos)
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        saidas["Blocos"] = str(alvo)

    _resumo_no_terminal(entrega, entrega.meta, origem, saidas)
    return 2 if entrega.relatorio.tem_critico else 0


def _miniaturas(pdf: bytes) -> list[bytes]:
    import pymupdf

    doc = pymupdf.open(stream=pdf, filetype="pdf")
    imagens = [pagina.get_pixmap(dpi=MINIATURA_DPI).tobytes("png") for pagina in doc]
    doc.close()
    return imagens
