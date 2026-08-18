"""Leitura do markdown: front matter, diretivas ::: e markdown padrão.

Devolve uma lista de `Bloco` já tipada. Só usa o classificador (LLM) para o que
sobra ambíguo — e sobra pouco: diretiva é explícita e estrutura de markdown é
determinística.

Nada de estilo entra por aqui: HTML inline no markdown é escapado, não
interpretado. O único HTML que sai desta camada é o de formatação inline gerada
por nós (negrito, itálico, código), a partir do markdown do autor.
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass

from .catalogo import CATALOGO, POR_DIRETIVA, Bloco

# ----------------------------------------------------------------- inline

_NEGRITO = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_ITALICO = re.compile(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)")
_CODIGO = re.compile(r"`([^`\n]+?)`")


def inline(texto: str) -> str:
    """Formatação inline segura: escapa tudo, depois aplica negrito/itálico."""
    seguro = html.escape(texto.strip(), quote=False)
    seguro = _CODIGO.sub(r"<code>\1</code>", seguro)
    seguro = _NEGRITO.sub(r"<strong>\1</strong>", seguro)
    seguro = _ITALICO.sub(r"<em>\1</em>", seguro)
    return seguro


_LINHA_FORM = re.compile(r"_{2,}")
_CAIXA_FORM = re.compile(r"\(\s*\)")


def campo_de_formulario(texto: str) -> str:
    """`___` vira linha para escrever; `( )` vira caixinha para marcar.

    O autor escreve com o teclado do tablet; o PDF sai com filete e quadradinho
    de verdade, não com underscore.
    """
    marcado = inline(texto)
    marcado = _CAIXA_FORM.sub('<span class="caixinha"></span>', marcado)

    def linha(casa: re.Match) -> str:
        classe = "linha total" if len(casa.group(0)) >= 12 else (
            "linha longa" if len(casa.group(0)) >= 6 else "linha"
        )
        return f'<span class="{classe}"></span>'

    return _LINHA_FORM.sub(linha, marcado)


def normalizar(texto: str) -> str:
    """Texto comparável: sem acento, sem caixa, espaço colapsado."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


# ------------------------------------------------------------- front matter


@dataclass
class Metadados:
    titulo: str = ""
    subtitulo: str = ""
    personagem: str = ""
    psicologa: str = ""
    crp: str = ""
    especialidade: str = ""

    def faltando(self) -> list[str]:
        return [campo for campo in ("titulo", "subtitulo") if not getattr(self, campo)]


def ler_front_matter(fonte: str) -> tuple[Metadados, str, int]:
    """Lê o bloco `---` do topo. Devolve metadados, resto e linha inicial do resto."""
    linhas = fonte.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return Metadados(), fonte, 1

    meta = Metadados()
    for indice in range(1, len(linhas)):
        atual = linhas[indice].strip()
        if atual == "---":
            resto = "\n".join(linhas[indice + 1 :])
            return meta, resto, indice + 2
        if not atual or atual.startswith("#"):
            continue
        if ":" in atual:
            chave, _, valor = atual.partition(":")
            chave = chave.strip().lower()
            valor = valor.strip()
            if hasattr(meta, chave):
                setattr(meta, chave, html.escape(valor, quote=False))
    return meta, "", len(linhas) + 1


# ---------------------------------------------------------------- diretivas

_ABRE = re.compile(r"^:::\s*([a-zç-]+)\s*(.*)$")
_FECHA = re.compile(r"^:::\s*$")


@dataclass
class Pedaco:
    """Trecho cru do markdown: ou uma diretiva, ou markdown solto."""

    diretiva: str | None
    argumento: str
    texto: str
    linha: int


def separar_pedacos(corpo: str, linha_inicial: int) -> list[Pedaco]:
    pedacos: list[Pedaco] = []
    solto: list[str] = []
    solto_linha = linha_inicial

    linhas = corpo.splitlines()
    indice = 0
    while indice < len(linhas):
        abertura = _ABRE.match(linhas[indice].rstrip())
        if abertura:
            if any(l.strip() for l in solto):
                pedacos.append(Pedaco(None, "", "\n".join(solto), solto_linha))
            solto, solto_linha = [], linha_inicial + indice + 1

            nome = abertura.group(1).lower()
            argumento = abertura.group(2).strip()
            dentro: list[str] = []
            indice += 1
            while indice < len(linhas) and not _FECHA.match(linhas[indice].rstrip()):
                dentro.append(linhas[indice])
                indice += 1
            indice += 1  # consome o ::: de fechamento
            pedacos.append(
                Pedaco(nome, argumento, "\n".join(dentro), solto_linha)
            )
            solto_linha = linha_inicial + indice
            continue

        if not solto:
            solto_linha = linha_inicial + indice
        solto.append(linhas[indice])
        indice += 1

    if any(l.strip() for l in solto):
        pedacos.append(Pedaco(None, "", "\n".join(solto), solto_linha))
    return pedacos


def campos_e_corpo(texto: str, chaves: set[str]) -> tuple[dict[str, str], str]:
    """Separa linhas `chave: valor` (das chaves conhecidas) do resto do texto.

    Uma chave pode ter valor em várias linhas: continua até a próxima chave
    conhecida ou até uma linha vazia seguida de outra chave.
    """
    campos: dict[str, list[str]] = {}
    sobra: list[str] = []
    chave_atual: str | None = None

    for linha in texto.splitlines():
        possivel = re.match(r"^\s*([a-zç_]+)\s*:\s*(.*)$", linha)
        if possivel and possivel.group(1).lower() in chaves:
            chave_atual = possivel.group(1).lower()
            campos[chave_atual] = [possivel.group(2)]
            continue
        if chave_atual is not None:
            if linha.strip() == "":
                chave_atual = None
                continue
            campos[chave_atual].append(linha)
            continue
        sobra.append(linha)

    juntos = {chave: "\n".join(valor).strip() for chave, valor in campos.items()}
    return juntos, "\n".join(sobra).strip()


# ------------------------------------------------- markdown solto → estrutura

_CABECALHO = re.compile(r"^(#{1,4})\s+(.*)$")
_ITEM_LISTA = re.compile(r"^\s*[-*+]\s+(.*)$")
_ITEM_NUMERO = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
_LINHA_TABELA = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARADOR_TABELA = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_CITACAO = re.compile(r"^\s*>\s?(.*)$")


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def markdown_para_conteudo(texto: str) -> list[dict]:
    """Converte markdown solto em uma lista de elementos de conteúdo.

    Elementos: {'tipo': 'titulo'|'subtitulo'|'paragrafo'|'lista'|'lista_numerada'
    |'tabela'|'citacao', ...} com HTML inline já resolvido.
    """
    elementos: list[dict] = []
    linhas = texto.splitlines()
    indice = 0

    while indice < len(linhas):
        linha = linhas[indice]
        cru = linha.strip()

        if not cru:
            indice += 1
            continue

        cabecalho = _CABECALHO.match(cru)
        if cabecalho:
            nivel = len(cabecalho.group(1))
            tipo = "titulo" if nivel <= 2 else "subtitulo"
            elementos.append({"tipo": tipo, "texto": inline(cabecalho.group(2))})
            indice += 1
            continue

        if _LINHA_TABELA.match(cru):
            bruto = []
            while indice < len(linhas) and _LINHA_TABELA.match(linhas[indice].strip()):
                bruto.append(linhas[indice])
                indice += 1
            cabecalhos: list[str] = []
            corpo: list[list[str]] = []
            for numero, linha_tabela in enumerate(bruto):
                if _SEPARADOR_TABELA.match(linha_tabela.strip()):
                    continue
                celulas = [inline(c) for c in _celulas(linha_tabela)]
                if numero == 0:
                    cabecalhos = celulas
                else:
                    corpo.append(celulas)
            elementos.append({"tipo": "tabela", "cabecalhos": cabecalhos, "linhas": corpo})
            continue

        if _CITACAO.match(cru):
            partes = []
            while indice < len(linhas) and _CITACAO.match(linhas[indice].strip()):
                partes.append(_CITACAO.match(linhas[indice].strip()).group(1))
                indice += 1
            elementos.append({"tipo": "citacao", "texto": inline(" ".join(partes))})
            continue

        if _ITEM_LISTA.match(linha) or _ITEM_NUMERO.match(linha):
            numerada = bool(_ITEM_NUMERO.match(linha))
            itens: list[str] = []
            while indice < len(linhas):
                atual = linhas[indice]
                casa = _ITEM_NUMERO.match(atual) if numerada else _ITEM_LISTA.match(atual)
                if casa:
                    itens.append(casa.group(2) if numerada else casa.group(1))
                    indice += 1
                    continue
                # continuação recuada do item anterior
                if itens and atual.startswith(("  ", "\t")) and atual.strip():
                    itens[-1] += " " + atual.strip()
                    indice += 1
                    continue
                break
            elementos.append(
                {
                    "tipo": "lista_numerada" if numerada else "lista",
                    "itens": [inline(i) for i in itens],
                }
            )
            continue

        paragrafo = []
        while indice < len(linhas) and linhas[indice].strip():
            atual = linhas[indice].strip()
            if (
                _CABECALHO.match(atual)
                or _LINHA_TABELA.match(atual)
                or _ITEM_LISTA.match(linhas[indice])
                or _ITEM_NUMERO.match(linhas[indice])
                or _CITACAO.match(atual)
            ):
                break
            paragrafo.append(atual)
            indice += 1
        if paragrafo:
            elementos.append({"tipo": "paragrafo", "texto": inline(" ".join(paragrafo))})

    return elementos


def texto_puro(elementos: list[dict]) -> str:
    """Texto sem marcação, para conferência de conteúdo no QA."""
    partes: list[str] = []
    for elemento in elementos:
        if "texto" in elemento:
            partes.append(elemento["texto"])
        for item in elemento.get("itens", []):
            partes.append(item)
        for celula in elemento.get("cabecalhos", []):
            partes.append(celula)
        for linha in elemento.get("linhas", []):
            partes.extend(linha)
    juntos = " ".join(partes)
    return re.sub(r"<[^>]+>", "", juntos)


# ------------------------------------------------------- pedaço → bloco

def _dividir_titulo(elementos: list[dict], aceitar_subtitulo: bool = True) -> tuple[str, list[dict]]:
    """Tira o título de abertura da lista de elementos.

    Dentro de uma diretiva o autor escreve o título com `###` (que vira
    'subtitulo'), porque `##` já significa 'seção nova' no texto solto.
    """
    aceitos = {"titulo", "subtitulo"} if aceitar_subtitulo else {"titulo"}
    if elementos and elementos[0]["tipo"] in aceitos:
        return elementos[0]["texto"], elementos[1:]
    return "", elementos


def _pos_formulario(texto_com_inline: str) -> str:
    """Aplica as marcas de formulário em texto que já passou por inline()."""
    marcado = _CAIXA_FORM.sub('<span class="caixinha"></span>', texto_com_inline)

    def linha(casa: re.Match) -> str:
        classe = "linha total" if len(casa.group(0)) >= 12 else (
            "linha longa" if len(casa.group(0)) >= 6 else "linha"
        )
        return f'<span class="{classe}"></span>'

    return _LINHA_FORM.sub(linha, marcado)


def bloco_de_diretiva(pedaco: Pedaco) -> Bloco:
    tipo = POR_DIRETIVA[pedaco.diretiva]
    especificacao = CATALOGO[tipo]
    chaves = set(especificacao.campos)

    if tipo == "ficha_atividade":
        campos, sobra = campos_e_corpo(pedaco.texto, chaves - {"numero", "nome", "passos"})
        elementos = markdown_para_conteudo(sobra)
        nome, resto = _dividir_titulo(elementos)
        if not nome:
            nome, resto = (resto[0]["texto"], resto[1:]) if resto else ("", resto)
        passos: list[str] = []
        outros: list[dict] = []
        for elemento in resto:
            if elemento["tipo"] == "lista_numerada" and not passos:
                passos = elemento["itens"]
            elif elemento["tipo"] == "subtitulo" and normalizar(elemento["texto"]).startswith("passo"):
                continue
            else:
                outros.append(elemento)
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={
                "numero": pedaco.argumento,
                "nome": nome,
                "objetivo": inline(campos.get("objetivo", "")),
                "principio": inline(campos.get("principio", "")),
                "materiais": inline(campos.get("materiais", "")),
                "passos": passos,
                "facil": inline(campos.get("facil", "")),
                "desafiador": inline(campos.get("desafiador", "")),
                "observar": inline(campos.get("observar", "")),
                "extra": outros,
            },
        )

    if tipo == "abertura_bloco":
        elementos = markdown_para_conteudo(pedaco.texto)
        nome, resto = _dividir_titulo(elementos)
        if not nome and resto:
            nome, resto = resto[0].get("texto", ""), resto[1:]
        frase = " ".join(e.get("texto", "") for e in resto).strip()
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={"numero": pedaco.argumento, "nome": nome, "frase": frase},
        )

    if tipo == "formulario_imprimivel":
        campos, sobra = campos_e_corpo(pedaco.texto, {"instrucao", "repeticoes"})
        elementos = markdown_para_conteudo(sobra)
        titulo, resto = _dividir_titulo(elementos)
        campos_lista: list[str] = []
        for elemento in resto:
            if elemento["tipo"] in {"lista", "lista_numerada"}:
                campos_lista.extend(elemento["itens"])
            elif elemento["tipo"] == "paragrafo":
                campos_lista.append(elemento["texto"])
        campos_lista = [_pos_formulario(c) for c in campos_lista]
        repeticoes = campos.get("repeticoes", "1")
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={
                "titulo": titulo or pedaco.argumento,
                "instrucao": inline(campos.get("instrucao", "")),
                "campos": campos_lista,
                "repeticoes": int(repeticoes) if str(repeticoes).isdigit() else 1,
            },
        )

    if tipo == "dicas_praticas":
        elementos = markdown_para_conteudo(pedaco.texto)
        titulo = ""
        resto = elementos
        cabecalhos = {"titulo", "subtitulo"}
        # título do bloco é um cabeçalho seguido direto por outro cabeçalho
        if (
            len(elementos) >= 2
            and elementos[0]["tipo"] in cabecalhos
            and elementos[1]["tipo"] in cabecalhos
        ):
            titulo, resto = elementos[0]["texto"], elementos[1:]
        dicas: list[dict] = []
        for elemento in resto:
            if elemento["tipo"] in {"subtitulo", "titulo"}:
                dicas.append({"titulo": elemento["texto"], "corpo": []})
            elif dicas:
                dicas[-1]["corpo"].append(elemento)
            else:
                dicas.append({"titulo": "", "corpo": [elemento]})
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={"titulo": titulo or pedaco.argumento, "dicas": dicas},
        )

    if tipo == "roda_conversa":
        elementos = markdown_para_conteudo(pedaco.texto)
        titulo, resto = _dividir_titulo(elementos)
        perguntas: list[str] = []
        for elemento in resto:
            if elemento["tipo"] in {"lista", "lista_numerada"}:
                perguntas.extend(elemento["itens"])
            elif elemento["tipo"] == "paragrafo":
                perguntas.append(elemento["texto"])
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={"titulo": titulo or pedaco.argumento or "Roda de conversa", "perguntas": perguntas},
        )

    if tipo == "voz_personagem":
        elementos = markdown_para_conteudo(pedaco.texto)
        titulo, resto = _dividir_titulo(elementos)
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={"personagem": pedaco.argumento, "titulo": titulo, "corpo": resto},
        )

    if tipo == "carta_abertura":
        corpo, _, assinatura = pedaco.texto.partition("\n--\n")
        # na assinatura, cada linha é uma linha: "Com carinho," e o nome não
        # podem virar um parágrafo corrido
        linhas_assinatura = [
            {"tipo": "paragrafo", "texto": inline(linha)}
            for linha in assinatura.splitlines()
            if linha.strip()
        ]
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={
                "corpo": markdown_para_conteudo(corpo),
                "assinatura": linhas_assinatura,
            },
        )

    if tipo == "caixa_atencao":
        elementos = markdown_para_conteudo(pedaco.texto)
        titulo, resto = _dividir_titulo(elementos)
        return Bloco(
            tipo=tipo,
            procedencia="diretiva",
            origem_linha=pedaco.linha,
            dados={"rotulo": titulo or pedaco.argumento or "Ponto de atenção", "corpo": resto},
        )

    # secao_encerramento e qualquer outra diretiva de texto corrido
    elementos = markdown_para_conteudo(pedaco.texto)
    titulo, resto = _dividir_titulo(elementos)
    return Bloco(
        tipo=tipo,
        procedencia="diretiva",
        origem_linha=pedaco.linha,
        dados={"titulo": titulo or pedaco.argumento, "corpo": resto},
    )


def blocos_de_markdown_solto(pedaco: Pedaco) -> list[Bloco]:
    """Quebra markdown solto em blocos por título de nível 1–2.

    Tabela vira `tabela_comparativa` quando tem exatamente duas colunas — é o
    padrão 'Birra × Crise' do material. Com três ou mais colunas, fica dentro da
    seção como tabela comum.
    """
    elementos = markdown_para_conteudo(pedaco.texto)
    blocos: list[Bloco] = []
    atual: list[dict] = []
    titulo = ""

    def fechar() -> None:
        nonlocal atual, titulo
        if titulo or atual:
            blocos.append(
                Bloco(
                    tipo="secao_conceitual",
                    procedencia="estrutura",
                    origem_linha=pedaco.linha,
                    dados={"titulo": titulo, "corpo": atual},
                )
            )
        atual, titulo = [], ""

    for elemento in elementos:
        if elemento["tipo"] == "titulo":
            fechar()
            titulo = elemento["texto"]
            continue
        if elemento["tipo"] == "tabela" and len(elemento["cabecalhos"]) == 2:
            fechar()
            blocos.append(
                Bloco(
                    tipo="tabela_comparativa",
                    procedencia="estrutura",
                    origem_linha=pedaco.linha,
                    dados={"cabecalhos": elemento["cabecalhos"], "linhas": elemento["linhas"]},
                )
            )
            continue
        atual.append(elemento)

    fechar()
    return blocos


def ler(fonte: str) -> tuple[Metadados, list[Bloco]]:
    """Ponto de entrada: markdown → metadados + blocos tipados."""
    meta, corpo, linha_inicial = ler_front_matter(fonte)
    blocos: list[Bloco] = []

    for pedaco in separar_pedacos(corpo, linha_inicial):
        if pedaco.diretiva:
            if pedaco.diretiva in POR_DIRETIVA:
                blocos.append(bloco_de_diretiva(pedaco))
            else:
                # diretiva desconhecida: vira o bloco genérico e é registrada
                elementos = markdown_para_conteudo(pedaco.texto)
                titulo, resto = _dividir_titulo(elementos)
                blocos.append(
                    Bloco(
                        tipo="secao_conceitual",
                        procedencia="fallback",
                        origem_linha=pedaco.linha,
                        dados={"titulo": titulo, "corpo": resto},
                        observacao=f"diretiva ':::{pedaco.diretiva}' não existe no catálogo",
                    )
                )
            continue
        blocos.extend(blocos_de_markdown_solto(pedaco))

    return meta, blocos
