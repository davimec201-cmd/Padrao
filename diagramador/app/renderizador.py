"""Renderização: blocos → HTML → PDF.

Três coisas acontecem aqui, todas determinísticas:

1. **Montagem** — capa, sumário e página final entram automaticamente; o resto
   vem da lista de blocos já classificada.
2. **Sumário com página real** — duas passadas: a primeira descobre em que
   página cada seção caiu, a segunda escreve os números.
3. **Encaixe de ficha longa** — se uma ficha não couber em uma página, ela é
   re-renderizada com escala menor (100 → 96 → 92 → 88). É ajuste numérico, não
   decisão de layout, e toda redução é registrada para o relatório.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

from . import titulo as titulo_svg
from .catalogo import CATALOGO, Bloco
from .marcacao import Metadados

RAIZ = Path(__file__).resolve().parents[2]
TEMA = RAIZ / "diagramador" / "tema"
TEMPLATES = Path(__file__).resolve().parent / "templates"
ASSETS = RAIZ / "assets"
TOKENS = json.loads((RAIZ / "design" / "tokens.json").read_text(encoding="utf-8"))

FUNDAMENTACAO = TOKENS["texto_fixo"]["fundamentacao_cientifica"]
DISCLAIMER = TOKENS["texto_fixo"]["disclaimer_legal"]
ESCALAS = ("", "escala-96", "escala-92", "escala-88")

# blocos que entram no sumário e como
NO_SUMARIO = {
    "secao_conceitual": "item",
    "abertura_bloco": "grupo",
    "ficha_atividade": "item",
    "formulario_imprimivel": "item",
    "dicas_praticas": "item",
    "roda_conversa": "item",
    "secao_encerramento": "item",
}


@dataclass
class ResultadoRender:
    pdf: bytes
    paginas: int
    blocos: list[Bloco]
    pagina_por_bloco: dict[int, int]
    fichas_reduzidas: dict[int, str] = field(default_factory=dict)
    documento_html: str = ""
    # documento já paginado do WeasyPrint: o QA usa para saber o que quebrou onde
    documento: object | None = None


def _ambiente() -> Environment:
    # autoescape desligado de propósito: todo texto de autor já passou por
    # marcacao.inline(), que escapa antes de aplicar negrito/itálico. Ligar aqui
    # escaparia duas vezes. Metadados e campos da interface são escapados na
    # entrada, em marcacao.ler_front_matter e em pipeline.
    return Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)


def caminho_ilustracao(personagem: str) -> tuple[str, bool]:
    """Devolve (caminho, existe). Sem o personagem, cai na ilustração padrão."""
    if personagem:
        arquivo = ASSETS / "ilustracoes" / f"{personagem}.png"
        if arquivo.exists():
            return arquivo.as_uri(), True
    return (ASSETS / "ilustracoes" / "_padrao.png").as_uri(), not personagem


def montar_blocos(meta: Metadados, blocos: list[Bloco]) -> list[Bloco]:
    """Insere capa, sumário e página final na lista escrita pelo autor."""
    ilustracao, _ = caminho_ilustracao(meta.personagem)

    # quem fala na "voz do personagem" aparece ao lado da própria fala
    for bloco in blocos:
        if bloco.tipo == "voz_personagem":
            quem = bloco.dados.get("personagem") or meta.personagem
            arquivo = ASSETS / "ilustracoes" / f"{quem}.png"
            bloco.dados["ilustracao"] = arquivo.as_uri() if arquivo.exists() else ""

    capa = Bloco(
        tipo="capa",
        procedencia="automatico",
        dados={
            "titulo": meta.titulo,
            "titulo_svg": titulo_svg.montar(
                meta.titulo,
                float(TOKENS["grid"]["largura_conteudo_mm"]),
                TOKENS["cor"][TOKENS["tipografia"]["escala"]["capa_titulo"]["contorno"]["cor"]]["valor"],
                TOKENS["cor"][TOKENS["tipografia"]["escala"]["capa_titulo"]["cor"]]["valor"],
            ),
            "subtitulo": meta.subtitulo,
            "personagem": meta.personagem,
            "ilustracao": ilustracao,
            "psicologa": meta.psicologa,
            "crp": meta.crp,
            "especialidade": meta.especialidade,
        },
    )

    itens = [
        {
            "texto": _texto_de_sumario(bloco),
            "grupo": NO_SUMARIO[bloco.tipo] == "grupo",
            "indice": None,  # preenchido depois, com o índice final
            "pagina": None,
        }
        for bloco in blocos
        if bloco.tipo in NO_SUMARIO and _texto_de_sumario(bloco)
    ]
    sumario = Bloco(
        tipo="sumario",
        procedencia="automatico",
        dados={"titulo": "O que você vai encontrar", "itens": itens},
    )

    final = Bloco(
        tipo="pagina_final",
        procedencia="automatico",
        dados={
            "psicologa": meta.psicologa,
            "crp": meta.crp,
            "disclaimer": DISCLAIMER.replace("{nome}", meta.psicologa).replace("{crp}", meta.crp),
        },
    )

    montados: list[Bloco] = [capa]
    resto = list(blocos)
    # o sumário entra depois da carta de abertura, se houver
    if resto and resto[0].tipo == "carta_abertura":
        montados.append(resto.pop(0))
    if itens:
        montados.append(sumario)
    montados.extend(resto)
    montados.append(final)

    # liga cada item do sumário ao índice do bloco correspondente
    posicao = 0
    for indice, bloco in enumerate(montados):
        if bloco.tipo in NO_SUMARIO and _texto_de_sumario(bloco):
            if posicao < len(itens):
                itens[posicao]["indice"] = indice
                posicao += 1
    return montados


def _texto_de_sumario(bloco: Bloco) -> str:
    dados = bloco.dados
    if bloco.tipo == "ficha_atividade":
        numero = dados.get("numero")
        nome = dados.get("nome", "")
        return f"{numero}. {nome}" if numero else nome
    if bloco.tipo == "abertura_bloco":
        numero = dados.get("numero")
        nome = dados.get("nome", "")
        return f"BLOCO {numero} — {nome}" if numero else nome
    return dados.get("titulo", "")


def preencher_placeholders(blocos: list[Bloco], meta: Metadados) -> None:
    """Troca {psicologa} e {crp} pelo que veio da interface, em todo texto."""
    trocas = {"{psicologa}": meta.psicologa, "{crp}": f"CRP {meta.crp}" if meta.crp else ""}

    def trocar(valor):
        if isinstance(valor, str):
            for chave, novo in trocas.items():
                valor = valor.replace(chave, novo)
            return valor
        if isinstance(valor, list):
            return [trocar(v) for v in valor]
        if isinstance(valor, dict):
            return {k: trocar(v) for k, v in valor.items()}
        return valor

    for bloco in blocos:
        bloco.dados = trocar(bloco.dados)


def gerar_html(
    meta: Metadados,
    blocos: list[Bloco],
    escalas: dict[int, str] | None = None,
) -> str:
    ambiente = _ambiente()
    template = ambiente.get_template("documento.html")
    escalas = escalas or {}

    corpo: list[str] = []
    for indice, bloco in enumerate(blocos):
        parcial = ambiente.get_template(f"blocos/{bloco.tipo}.html")
        corpo.append(
            parcial.render(
                bloco=bloco,
                indice=indice,
                marca=(ASSETS / "marca" / "peca.png").as_uri(),
                fundamentacao=FUNDAMENTACAO,
                escala_ficha=escalas.get(indice, ""),
            )
        )

    return template.render(
        meta=meta,
        blocos=blocos,
        corpo="\n".join(corpo),
        marca=(ASSETS / "marca" / "peca.png").as_uri(),
        fundamentacao=FUNDAMENTACAO,
        corpo_pronto=True,
    )


# Sem uma FontConfiguration explícita, o WeasyPrint ignora @font-face em
# silêncio e cai na fonte do sistema. O QA pega isso ("Fontes embutidas"), mas o
# lugar de resolver é aqui: uma configuração compartilhada por todas as folhas e
# pela renderização.
_FONTES = FontConfiguration()


def _folhas() -> list[CSS]:
    return [
        CSS(filename=str(TEMA / "tokens.css"), font_config=_FONTES),
        CSS(filename=str(TEMA / "base.css"), font_config=_FONTES),
        CSS(filename=str(TEMA / "blocos.css"), font_config=_FONTES),
    ]


def _percorrer(caixa, visita) -> None:
    visita(caixa)
    for filha in getattr(caixa, "children", []):
        _percorrer(filha, visita)


def paginas_por_id(documento) -> dict[str, list[int]]:
    """Em que páginas cada elemento com id aparece (1-based)."""
    encontrados: dict[str, list[int]] = {}

    for numero, pagina in enumerate(documento.pages, start=1):
        def visita(caixa, numero=numero):
            elemento = getattr(caixa, "element", None)
            if elemento is None or not hasattr(elemento, "get"):
                return
            identificador = elemento.get("id")
            if not identificador:
                return
            paginas = encontrados.setdefault(identificador, [])
            if numero not in paginas:
                paginas.append(numero)

        _percorrer(pagina._page_box, visita)

    return encontrados


def renderizar(
    meta: Metadados,
    blocos: list[Bloco],
    progresso=lambda *_: None,
) -> ResultadoRender:
    """Renderiza o documento inteiro, resolvendo sumário e encaixe de fichas."""
    montados = montar_blocos(meta, blocos)
    preencher_placeholders(montados, meta)

    escalas: dict[int, str] = {}
    fichas_reduzidas: dict[int, str] = {}

    for tentativa in range(len(ESCALAS)):
        progresso("Diagramando as páginas", 0.55 + 0.05 * tentativa)
        html = gerar_html(meta, montados, escalas)
        documento = HTML(string=html, base_url=str(TEMPLATES)).render(
            stylesheets=_folhas(), font_config=_FONTES
        )
        localizacao = paginas_por_id(documento)

        # fichas quebradas em mais de uma página
        quebradas = [
            indice
            for indice, bloco in enumerate(montados)
            if bloco.tipo == "ficha_atividade" and len(localizacao.get(f"b{indice}", [])) > 1
        ]
        if not quebradas:
            break

        avancou = False
        for indice in quebradas:
            atual = ESCALAS.index(escalas.get(indice, ""))
            if atual + 1 < len(ESCALAS):
                escalas[indice] = ESCALAS[atual + 1]
                fichas_reduzidas[indice] = ESCALAS[atual + 1]
                avancou = True
        if not avancou:
            break

    # sumário: agora sabemos a página de cada bloco
    pagina_por_bloco = {
        int(chave[1:]): paginas[0]
        for chave, paginas in localizacao.items()
        if chave.startswith("b") and chave[1:].isdigit()
    }

    sumario = next((bloco for bloco in montados if bloco.tipo == "sumario"), None)
    if sumario is not None:
        for item in sumario.dados["itens"]:
            item["pagina"] = pagina_por_bloco.get(item["indice"])
        progresso("Numerando o sumário", 0.75)
        html = gerar_html(meta, montados, escalas)
        documento = HTML(string=html, base_url=str(TEMPLATES)).render(
            stylesheets=_folhas(), font_config=_FONTES
        )
        localizacao = paginas_por_id(documento)
        pagina_por_bloco = {
            int(chave[1:]): paginas[0]
            for chave, paginas in localizacao.items()
            if chave.startswith("b") and chave[1:].isdigit()
        }
        # a segunda passada pode empurrar conteúdo: reconfere e corrige uma vez
        mudou = False
        for item in sumario.dados["itens"]:
            real = pagina_por_bloco.get(item["indice"])
            if real and real != item["pagina"]:
                item["pagina"] = real
                mudou = True
        if mudou:
            html = gerar_html(meta, montados, escalas)
            documento = HTML(string=html, base_url=str(TEMPLATES)).render(
            stylesheets=_folhas(), font_config=_FONTES
        )
            localizacao = paginas_por_id(documento)
            pagina_por_bloco = {
                int(chave[1:]): paginas[0]
                for chave, paginas in localizacao.items()
                if chave.startswith("b") and chave[1:].isdigit()
            }

    progresso("Escrevendo o PDF", 0.85)
    pdf = documento.write_pdf()

    return ResultadoRender(
        pdf=pdf,
        paginas=len(documento.pages),
        blocos=montados,
        pagina_por_bloco=pagina_por_bloco,
        fichas_reduzidas=fichas_reduzidas,
        documento_html=html,
        documento=documento,
    )
