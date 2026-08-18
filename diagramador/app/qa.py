"""QA automático — é o que substitui a revisão detalhada.

Cada verificação devolve um `Achado` com estado (`ok`, `aviso`, `falha`), a
página e o que aconteceu. Falha crítica avisa antes do download.

As verificações olham três coisas: o PDF final (texto, fontes, imagens, pixels),
a árvore de layout (para saber o que quebrou onde) e o markdown de origem
(para conferir que nada se perdeu no caminho).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from .marcacao import normalizar
from .renderizador import FUNDAMENTACAO, ResultadoRender

RAIZ = Path(__file__).resolve().parents[2]
TOKENS = json.loads((RAIZ / "design" / "tokens.json").read_text(encoding="utf-8"))

CRITICO = "falha"
AVISO = "aviso"
OK = "ok"

def _cores_do_tema(tema: str) -> set[str]:
    """Valores de cor válidos num tema: os papéis resolvidos + a paleta base."""
    valores = {
        (TOKENS.get("temas", {}).get(tema, {}).get("cor", {}).get(papel) or dados["valor"]).upper()
        for papel, dados in TOKENS["cor"].items()
    }
    familia = "teanimal" if tema == "teanimal" else "institucional"
    for grupo in ("institucional", familia):
        valores |= {c["valor"].upper() for c in TOKENS["paleta"][grupo].values()}
    return valores | {"#FFFFFF", "#000000"}


PALETA_POR_TEMA = {tema: _cores_do_tema(tema) for tema in ("institucional", "teanimal")}
PALETA = PALETA_POR_TEMA["institucional"] | PALETA_POR_TEMA["teanimal"]
SUPERVISAO = TOKENS["regras_do_material"]["supervisao_tecnica"]
PROIBIDOS = TOKENS["linguagem"]["proibido"]
FAMILIAS_ESPERADAS = ("Poppins", "Manrope")

PLACEHOLDERS = (
    re.compile(r"\[nome\]|\[Nome[^\]]*\]|\[_+\]|CRP \[|\{nome\}|\{crp\}|\{psicologa\}|Lorem ipsum", re.IGNORECASE),
    # TODO e FIXME só em caixa alta: "todo" é palavra comum em português
    re.compile(r"\bTODO\b|\bFIXME\b"),
)

# tolerância de margem: 1mm em pt
FOLGA = 1 * 72 / 25.4


@dataclass
class Achado:
    verificacao: str
    estado: str
    resumo: str
    detalhes: list[str] = field(default_factory=list)
    paginas: list[int] = field(default_factory=list)
    critico: bool = False

    def para_json(self) -> dict:
        return {
            "verificacao": self.verificacao,
            "estado": self.estado,
            "resumo": self.resumo,
            "detalhes": self.detalhes[:40],
            "paginas": sorted(set(self.paginas))[:40],
            "critico": self.critico,
        }


@dataclass
class Relatorio:
    achados: list[Achado] = field(default_factory=list)
    paginas: int = 0

    @property
    def falhas(self) -> list[Achado]:
        return [a for a in self.achados if a.estado == CRITICO]

    @property
    def avisos(self) -> list[Achado]:
        return [a for a in self.achados if a.estado == AVISO]

    @property
    def verde(self) -> bool:
        return not self.falhas and not self.avisos

    @property
    def tem_critico(self) -> bool:
        return any(a.critico for a in self.falhas)

    def para_json(self) -> dict:
        return {
            "verde": self.verde,
            "tem_critico": self.tem_critico,
            "paginas": self.paginas,
            "total": len(self.achados),
            "falhas": len(self.falhas),
            "avisos": len(self.avisos),
            "achados": [a.para_json() for a in self.achados],
        }


# ------------------------------------------------------------------ auxiliares


def _texto_por_pagina(doc: pymupdf.Document) -> list[str]:
    return [pagina.get_text() for pagina in doc]


def _sem_marca(html_ou_texto: str) -> str:
    return re.sub(r"<[^>]+>", " ", html_ou_texto)


def _colado(texto: str) -> str:
    """Normaliza e remove todo espaço.

    O PDF quebra linha dentro de palavra hifenizada ("Cognitivo-\nComportamental"),
    e aí a comparação literal falharia por um espaço que o leitor nem vê.
    """
    return re.sub(r"\s+", "", normalizar(texto))


def _hex(cor: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % cor


def _rgb(hexa: str) -> tuple[int, int, int]:
    return int(hexa[1:3], 16), int(hexa[3:5], 16), int(hexa[5:7], 16)


_PALETA_RGB = [_rgb(h) for h in sorted(PALETA)]


def _mais_proximo(cor: tuple[int, int, int], entre: set[str] | None = None) -> tuple[str, float]:
    melhor, distancia = "", 10**9
    for alvo in sorted(entre if entre is not None else PALETA):
        r, g, b = _rgb(alvo)
        d = (cor[0] - r) ** 2 + (cor[1] - g) ** 2 + (cor[2] - b) ** 2
        if d < distancia:
            melhor, distancia = alvo, d
    return melhor, distancia**0.5


def _e_mistura_de_tokens(
    cor: tuple[int, int, int], tolerancia: float, entre: set[str] | None = None
) -> bool:
    """A cor está na reta entre duas cores da paleta?

    Serrilhado de borda e sobreposição translúcida produzem exatamente isso: a
    mistura de dois tokens. Misturar dois tokens não cria cor nova — inventar um
    terceiro tom, sim. É essa a diferença que o guardião da paleta precisa ver.
    """
    lista = [_rgb(h) for h in sorted(entre)] if entre is not None else _PALETA_RGB
    for indice, primeira in enumerate(lista):
        for segunda in lista[indice + 1 :]:
            direcao = tuple(b - a for a, b in zip(primeira, segunda))
            tamanho = sum(componente * componente for componente in direcao)
            if not tamanho:
                continue
            projecao = sum(
                (c - a) * d for c, a, d in zip(cor, primeira, direcao)
            ) / tamanho
            if not 0 <= projecao <= 1:
                continue
            ponto = tuple(a + projecao * d for a, d in zip(primeira, direcao))
            if sum((c - p) ** 2 for c, p in zip(cor, ponto)) ** 0.5 <= tolerancia:
                return True
    return False


def _percorrer(caixa, visita):
    visita(caixa)
    for filha in getattr(caixa, "children", []):
        _percorrer(filha, visita)


# ---------------------------------------------------------------- verificações


def texto_dentro_da_mancha(doc: pymupdf.Document) -> Achado:
    margem = TOKENS["grid"]
    esquerda = margem["margem_lateral_mm"] * 72 / 25.4
    topo = margem["margem_topo_mm"] * 72 / 25.4
    detalhes: list[str] = []
    paginas: list[int] = []

    for numero, pagina in enumerate(doc, start=1):
        largura, altura = pagina.rect.width, pagina.rect.height
        direita = largura - esquerda
        base = altura - 8 * 72 / 25.4  # rodapé fica abaixo da mancha
        for bloco in pagina.get_text("blocks"):
            x0, y0, x1, y1, texto = bloco[0], bloco[1], bloco[2], bloco[3], bloco[4]
            if not texto.strip():
                continue
            if numero == 1:
                continue  # a capa é sangria por desenho
            estoura = []
            if x0 < esquerda - FOLGA:
                estoura.append(f"passa {(esquerda - x0) / 72 * 25.4:.1f}mm à esquerda")
            if x1 > direita + FOLGA:
                estoura.append(f"passa {(x1 - direita) / 72 * 25.4:.1f}mm à direita")
            if y0 < topo - 6 * 72 / 25.4:
                estoura.append("passa a margem de cima")
            if y1 > base + FOLGA:
                estoura.append(f"passa {(y1 - base) / 72 * 25.4:.1f}mm embaixo")
            if estoura:
                paginas.append(numero)
                detalhes.append(
                    f"pág. {numero}: “{texto.strip()[:60]}” — {', '.join(estoura)}"
                )

    if detalhes:
        return Achado(
            "Texto dentro da mancha",
            CRITICO,
            f"{len(detalhes)} trecho(s) passando da margem",
            detalhes,
            paginas,
            critico=True,
        )
    return Achado("Texto dentro da mancha", OK, "nenhum texto passa da margem")


def orfas_e_viuvas(resultado: ResultadoRender, documento) -> Achado:
    """Parágrafo partido deixando uma linha sozinha no fim ou no começo da página.

    O sinal vem do próprio WeasyPrint: quando um bloco é fragmentado, ele marca em
    `remove_decoration_sides` qual lado foi cortado — 'bottom' significa "continua
    na próxima página", 'top' significa "vem da anterior".
    """
    detalhes: list[str] = []
    paginas: list[int] = []

    for numero, pagina in enumerate(documento.pages, start=1):
        def visita(caixa, numero=numero):
            elemento = getattr(caixa, "element", None)
            if elemento is None or getattr(elemento, "tag", "") not in {"p", "li"}:
                return
            linhas = [
                filha
                for filha in getattr(caixa, "children", [])
                if type(filha).__name__ == "LineBox"
            ]
            if len(linhas) != 1:
                return
            cortes = set(getattr(caixa, "remove_decoration_sides", ()) or ())
            if "bottom" in cortes:
                detalhes.append(f"pág. {numero}: linha órfã no fim da página")
                paginas.append(numero)
            elif "top" in cortes:
                detalhes.append(f"pág. {numero}: linha viúva no começo da página")
                paginas.append(numero)

        _percorrer(pagina._page_box, visita)

    if detalhes:
        return Achado("Órfãs e viúvas", AVISO, f"{len(detalhes)} linha(s) solta(s)", detalhes, paginas)
    return Achado("Órfãs e viúvas", OK, "nenhuma linha solta")


def fichas_inteiras(resultado: ResultadoRender, documento) -> Achado:
    """Nenhuma ficha de atividade quebrada entre páginas."""
    quebradas: list[str] = []
    paginas: list[int] = []
    ocorrencias: dict[str, list[int]] = {}

    for numero, pagina in enumerate(documento.pages, start=1):
        def visita(caixa, numero=numero):
            elemento = getattr(caixa, "element", None)
            if elemento is None or not hasattr(elemento, "get"):
                return
            classe = elemento.get("class", "") or ""
            identificador = elemento.get("id", "") or ""
            if "ficha" in classe.split() and identificador:
                ocorrencias.setdefault(identificador, [])
                if numero not in ocorrencias[identificador]:
                    ocorrencias[identificador].append(numero)

        _percorrer(pagina._page_box, visita)

    for identificador, onde in ocorrencias.items():
        if len(onde) > 1:
            indice = int(identificador[1:]) if identificador[1:].isdigit() else -1
            nome = ""
            if 0 <= indice < len(resultado.blocos):
                nome = resultado.blocos[indice].dados.get("nome", "")
            escala = resultado.fichas_reduzidas.get(indice, "")
            fim = (
                " — já foi reduzida ao mínimo (88%): encurte o texto ou divida em "
                "duas atividades"
                if escala == "escala-88"
                else ""
            )
            quebradas.append(
                f"“{nome}” ocupa as páginas {', '.join(map(str, onde))}{fim}"
            )
            paginas.extend(onde)

    reduzidas = [
        f"“{resultado.blocos[indice].dados.get('nome', '')}” reduzida para "
        f"{escala.replace('escala-', '')}%"
        for indice, escala in resultado.fichas_reduzidas.items()
    ]

    if quebradas:
        return Achado(
            "Fichas inteiras",
            CRITICO,
            f"{len(quebradas)} ficha(s) quebrada(s) entre páginas",
            quebradas + reduzidas,
            paginas,
            critico=True,
        )
    if reduzidas:
        return Achado(
            "Fichas inteiras",
            AVISO,
            f"{len(reduzidas)} ficha(s) couberam com redução de escala",
            reduzidas,
        )
    return Achado("Fichas inteiras", OK, "nenhuma ficha quebrada entre páginas")


def fontes_embutidas(doc: pymupdf.Document) -> Achado:
    encontradas: dict[str, bool] = {}
    for pagina in doc:
        for fonte in pagina.get_fonts(full=False):
            nome = fonte[3]
            embutida = bool(fonte[1]) or "+" in nome
            encontradas[nome] = encontradas.get(nome, False) or embutida

    if not encontradas:
        return Achado("Fontes embutidas", AVISO, "nenhuma fonte encontrada no PDF")

    faltando = [nome for nome, ok in encontradas.items() if not ok]
    estranhas = [
        nome
        for nome in encontradas
        if not any(familia.lower() in nome.lower() for familia in FAMILIAS_ESPERADAS)
    ]
    if faltando:
        return Achado(
            "Fontes embutidas",
            CRITICO,
            f"{len(faltando)} fonte(s) não embutida(s)",
            faltando,
            critico=True,
        )
    if estranhas:
        return Achado(
            "Fontes embutidas",
            AVISO,
            "há fonte fora das famílias da marca",
            estranhas,
        )
    return Achado(
        "Fontes embutidas",
        OK,
        f"{len(encontradas)} fonte(s) embutida(s): {', '.join(sorted(encontradas))}",
    )


def cores_da_paleta(doc: pymupdf.Document, tema: str = "institucional", tolerancia: int = 12) -> Achado:
    """Nenhuma cor fora da paleta — o guardião do padrão de marca.

    As áreas de ilustração ficam de fora: são arte aprovada, com paleta própria, e
    o sistema consome ilustração sem julgar cor. Mistura de dois tokens (serrilhado
    de borda, sobreposição translúcida) também passa: não é cor nova.
    """
    import numpy as np

    permitidas = PALETA_POR_TEMA.get(tema, PALETA_POR_TEMA["institucional"])
    fora: dict[str, int] = {}
    de_outro_tema: dict[str, int] = {}
    paginas: list[int] = []

    for numero, pagina in enumerate(doc, start=1):
        pixmap = pagina.get_pixmap(dpi=60)
        quadro = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height, pixmap.width, pixmap.n
        )[:, :, :3]
        escala = pixmap.width / pagina.rect.width

        # tira as ilustrações da conta
        considerar = np.ones(quadro.shape[:2], dtype=bool)
        for info in pagina.get_image_info():
            x0, y0, x1, y1 = info["bbox"]
            considerar[
                max(int(y0 * escala) - 1, 0) : int(y1 * escala) + 2,
                max(int(x0 * escala) - 1, 0) : int(x1 * escala) + 2,
            ] = False

        pixels = quadro[considerar]
        if not pixels.size:
            continue

        empacotado = (
            pixels[:, 0].astype(np.uint32) << 16
            | pixels[:, 1].astype(np.uint32) << 8
            | pixels[:, 2].astype(np.uint32)
        )
        valores, quantidades = np.unique(empacotado, return_counts=True)
        total = int(quantidades.sum()) or 1

        for valor, quantos in zip(valores.tolist(), quantidades.tolist()):
            if quantos / total < 0.004:  # serrilhado e sombra ficam de fora
                continue
            cor = ((valor >> 16) & 255, (valor >> 8) & 255, valor & 255)
            _, distancia = _mais_proximo(cor, permitidas)
            if distancia <= tolerancia or _e_mistura_de_tokens(cor, tolerancia, permitidas):
                continue
            chave = f"pág. {numero}: {_hex(cor)} ({quantos / total:.1%} da página)"
            # cor da marca, mas do outro universo: é desvio de tema, não de paleta
            _, distancia_marca = _mais_proximo(cor)
            if distancia_marca <= tolerancia or _e_mistura_de_tokens(cor, tolerancia):
                de_outro_tema[chave] = quantos
            else:
                fora[chave] = quantos
            paginas.append(numero)

    if fora:
        return Achado(
            "Cores da paleta",
            CRITICO,
            f"{len(fora)} cor(es) fora dos tokens",
            sorted(fora, key=lambda c: -fora[c]),
            paginas,
            critico=True,
        )
    if de_outro_tema:
        outro = "TEAnimal" if tema == "institucional" else "institucional"
        return Achado(
            "Cores da paleta",
            AVISO,
            f"{len(de_outro_tema)} cor(es) do universo {outro} em material {tema}",
            sorted(de_outro_tema, key=lambda c: -de_outro_tema[c])
            + [f"para usar essa paleta, escreva `tema: {outro.lower()}` no cabeçalho"],
            paginas,
        )
    return Achado("Cores da paleta", OK, f"toda cor vem dos tokens do tema {tema}")


def logo_em_toda_pagina(doc: pymupdf.Document) -> Achado:
    posicoes: dict[int, tuple[float, float]] = {}
    sem_logo: list[int] = []

    for numero, pagina in enumerate(doc, start=1):
        marcas = [
            pymupdf.Rect(info["bbox"])
            for info in pagina.get_image_info()
            if info["bbox"][3] > pagina.rect.height * 0.85
        ]
        if not marcas:
            sem_logo.append(numero)
            continue
        alvo = min(marcas, key=lambda r: r.y1)
        posicoes[numero] = (round(alvo.x0, 1), round(alvo.y0, 1))

    if sem_logo:
        return Achado(
            "Logo em toda página",
            CRITICO,
            f"{len(sem_logo)} página(s) sem logo no rodapé",
            [f"pág. {numero}" for numero in sem_logo],
            sem_logo,
            critico=True,
        )

    # a capa tem tratamento próprio; o resto precisa da mesma posição
    miolo = {numero: posicao for numero, posicao in posicoes.items() if numero > 1}
    if miolo:
        referencia = next(iter(miolo.values()))
        desalinhadas = [
            numero
            for numero, posicao in miolo.items()
            if abs(posicao[0] - referencia[0]) > 1.5 or abs(posicao[1] - referencia[1]) > 1.5
        ]
        if desalinhadas:
            return Achado(
                "Logo em toda página",
                AVISO,
                "logo em posição diferente em algumas páginas",
                [f"pág. {numero}" for numero in desalinhadas],
                desalinhadas,
            )
    return Achado("Logo em toda página", OK, "logo presente e na mesma posição")


def fundamentacao_literal(textos: list[str]) -> Achado:
    alvo = _colado(FUNDAMENTACAO)
    onde = [numero for numero, texto in enumerate(textos, start=1) if alvo in _colado(texto)]

    if len(onde) == 2 and onde[0] == 1 and onde[1] == len(textos):
        return Achado(
            "Fundamentação científica",
            OK,
            "presente na capa e na página final, literal",
            paginas=onde,
        )
    if not onde:
        return Achado(
            "Fundamentação científica",
            CRITICO,
            "texto de fundamentação não encontrado no PDF",
            critico=True,
        )
    return Achado(
        "Fundamentação científica",
        CRITICO,
        f"deveria aparecer 2 vezes (capa e página final); aparece {len(onde)}",
        [f"pág. {numero}" for numero in onde],
        onde,
        critico=True,
    )


def disclaimer_presente(textos: list[str]) -> Achado:
    alvo = _colado("não substitui avaliação, diagnóstico ou acompanhamento terapêutico")
    onde = [numero for numero, texto in enumerate(textos, start=1) if alvo in _colado(texto)]
    if onde:
        return Achado("Disclaimer legal", OK, f"presente na pág. {onde[-1]}", paginas=onde)
    return Achado(
        "Disclaimer legal",
        CRITICO,
        "disclaimer legal ausente da página final",
        critico=True,
    )


def sem_placeholders(textos: list[str]) -> Achado:
    detalhes: list[str] = []
    paginas: list[int] = []
    for numero, texto in enumerate(textos, start=1):
        for padrao in PLACEHOLDERS:
            for casa in padrao.finditer(texto):
                detalhes.append(f"pág. {numero}: “{casa.group(0)}”")
                paginas.append(numero)
    if detalhes:
        return Achado(
            "Placeholders preenchidos",
            CRITICO,
            f"{len(detalhes)} placeholder(s) sem preencher",
            detalhes,
            paginas,
            critico=True,
        )
    return Achado("Placeholders preenchidos", OK, "nenhum placeholder sobrou")


def sumario_confere(resultado: ResultadoRender, textos: list[str]) -> Achado:
    sumario = next((b for b in resultado.blocos if b.tipo == "sumario"), None)
    if sumario is None:
        return Achado("Sumário", OK, "material sem sumário")

    erradas: list[str] = []
    for item in sumario.dados["itens"]:
        indice, pagina = item.get("indice"), item.get("pagina")
        real = resultado.pagina_por_bloco.get(indice)
        if pagina is None:
            erradas.append(f"“{_sem_marca(item['texto'])}” sem número de página")
        elif real and real != pagina:
            erradas.append(f"“{_sem_marca(item['texto'])}”: sumário diz {pagina}, está na {real}")

    if erradas:
        return Achado(
            "Sumário",
            CRITICO,
            f"{len(erradas)} item(ns) com página errada",
            erradas,
            critico=True,
        )
    return Achado(
        "Sumário",
        OK,
        f"{len(sumario.dados['itens'])} itens com número de página conferido",
    )


def texto_completo(fonte: str, textos: list[str], meta=None) -> Achado:
    """Todo texto do markdown está no PDF.

    Compara por linha e por prefixo de seis palavras: o PDF requebra as linhas e
    separa os blocos, então frase inteira e vizinhança não servem de âncora.
    """
    do_pdf = _colado(" ".join(textos))

    limpo = re.sub(r"<!--.*?-->", " ", fonte, flags=re.S)  # comentários do autor
    limpo = re.sub(r"^---.*?^---", "", limpo, flags=re.S | re.M)  # front matter
    limpo = re.sub(r"^:::.*$", "", limpo, flags=re.M)  # linhas de diretiva
    if meta is not None:
        limpo = limpo.replace("{psicologa}", meta.psicologa or "")
        limpo = limpo.replace("{crp}", f"CRP {meta.crp}" if meta.crp else "")
    limpo = re.sub(r"^\s*(objetivo|principio|materiais|facil|desafiador|observar|instrucao|repeticoes)\s*:\s*",
                   "", limpo, flags=re.M | re.I)
    limpo = re.sub(r"^\s{0,3}#{1,4}\s+", "", limpo, flags=re.M)  # marca de título
    limpo = re.sub(r"^\s*[-*+]\s+", "", limpo, flags=re.M)  # marca de item
    limpo = re.sub(r"^\s*\d+[.)]\s+", "", limpo, flags=re.M)  # marca de item numerado
    limpo = limpo.replace("**", "").replace("|", " ")
    # marcas de formulário viram filete e quadradinho no PDF: não são texto
    limpo = re.sub(r"_{2,}", " ", limpo)
    limpo = re.sub(r"\(\s*\)", " ", limpo)

    faltando: list[str] = []
    for linha in limpo.splitlines():
        linha = linha.strip()
        if len(linha) < 25:
            continue
        alvo = _colado(linha)
        if not alvo or alvo in do_pdf:
            continue
        # a linha pode ter sido requebrada em dois blocos: confere o começo
        comeco = _colado(" ".join(linha.split()[:6]))
        if comeco and comeco in do_pdf:
            continue
        faltando.append(linha[:70])

    if faltando:
        return Achado(
            "Texto completo",
            CRITICO,
            f"{len(faltando)} trecho(s) do markdown não estão no PDF",
            faltando,
            critico=True,
        )
    return Achado("Texto completo", OK, "todo o texto do markdown está no PDF")


def linguagem(fonte: str, textos: list[str]) -> Achado:
    detalhes: list[str] = []
    paginas: list[int] = []
    normalizados = [normalizar(t) for t in textos]

    for termo in PROIBIDOS:
        alvo = normalizar(termo)
        for numero, texto in enumerate(normalizados, start=1):
            if re.search(rf"\b{re.escape(alvo)}", texto):
                detalhes.append(f"pág. {numero}: “{termo}”")
                paginas.append(numero)

    if detalhes:
        return Achado(
            "Linguagem",
            AVISO,
            f"{len(detalhes)} uso(s) de termo que a marca não usa",
            detalhes + ["o sistema não corrige texto: a troca é decisão sua"],
            paginas,
        )
    return Achado("Linguagem", OK, "nenhum termo proibido")


def contraste_dos_tokens() -> Achado:
    """Contraste do texto de corpo, calculado sobre os tokens congelados.

    Roda nos dois temas: trocar de tema não pode baixar a legibilidade.
    """

    def luminancia(hexa: str) -> float:
        def canal(valor: int) -> float:
            proporcao = valor / 255
            return proporcao / 12.92 if proporcao <= 0.04045 else ((proporcao + 0.055) / 1.055) ** 2.4

        r, g, b = (int(hexa[i : i + 2], 16) for i in (1, 3, 5))
        return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)

    def razao(frente: str, fundo: str) -> float:
        a, b = luminancia(frente), luminancia(fundo)
        return (max(a, b) + 0.05) / (min(a, b) + 0.05)

    # (texto, fundo) por papel — o texto de corpo de cada bloco sobre o seu fundo
    pares = [
        ("texto_corpo", "fundo_palco"),
        ("texto_corpo", "fundo_bloco"),
        ("texto_corpo", "fundo_bloco_secundario"),
        ("texto_corpo", "destaque_pedagogico_wash"),
        ("texto_corpo", "acento_material_wash"),
        ("texto_corpo", "facil_wash"),
        ("texto_corpo", "desafiador_wash"),
        ("texto_corpo", "observar_fundo"),
        ("texto_corpo", "voz_fundo"),
        ("atencao_texto", "atencao_fundo"),
        ("acento_material_texto", "acento_material"),
        ("divisoria_texto", "divisoria_fundo"),
        ("texto_secundario", "fundo_palco"),
        ("destaque_pedagogico_texto", "fundo_bloco"),
        ("destaque_pedagogico_texto", "destaque_pedagogico_wash"),
        ("texto_sobre_cor", "destaque_pedagogico_texto"),
    ]

    reprovados = []
    conferidos = 0
    for tema in ("institucional", "teanimal"):
        override = TOKENS.get("temas", {}).get(tema, {}).get("cor", {})

        def cor(papel: str, override=override) -> str:
            return override.get(papel) or TOKENS["cor"][papel]["valor"]

        for frente, fundo in pares:
            valor = razao(cor(frente), cor(fundo))
            conferidos += 1
            if valor < 4.5:
                reprovados.append(f"[{tema}] {frente} sobre {fundo}: {valor:.2f}:1")

    if reprovados:
        return Achado(
            "Contraste",
            CRITICO,
            f"{len(reprovados)} par(es) de cor abaixo de 4.5:1",
            reprovados,
            critico=True,
        )
    return Achado("Contraste", OK, f"{conferidos} pares de texto de corpo ≥ 4.5:1 nos dois temas")


def personagens(resultado: ResultadoRender, meta) -> Achado:
    """Personagem do Universo TEAnimal só aparece quando o material pede.

    É regra de marca, não preferência: sem `personagem:` no cabeçalho e sem
    `:::voz <nome>`, o material sai sem nenhum personagem.
    """
    usados: list[str] = []
    for bloco in resultado.blocos:
        if bloco.dados.get("ilustracao"):
            quem = bloco.dados.get("personagem", "") or "?"
            onde = "capa" if bloco.tipo == "capa" else bloco.rotulo.lower()
            usados.append(f"{quem} na {onde}")

    pedidos = bool(meta and meta.pediu_personagem) or any(
        bloco.tipo == "voz_personagem" and bloco.dados.get("personagem")
        for bloco in resultado.blocos
    )

    if usados and not pedidos:
        return Achado(
            "Personagens",
            CRITICO,
            "personagem apareceu sem o material pedir",
            usados,
            critico=True,
        )
    if usados:
        return Achado("Personagens", OK, "usados a pedido: " + ", ".join(usados))
    return Achado("Personagens", OK, "nenhum personagem — o padrão da marca")


def supervisao_tecnica(textos: list[str], meta) -> Achado:
    """O nome e o CRP registrados são os que devem sair no material."""
    nome, crp = (meta.psicologa if meta else ""), (meta.crp if meta else "")
    divergencias = []
    if normalizar(nome) != normalizar(SUPERVISAO["nome"]):
        divergencias.append(f"nome: “{nome}” — o registrado é “{SUPERVISAO['nome']}”")
    if crp.strip() != SUPERVISAO["crp"]:
        divergencias.append(f"CRP: “{crp}” — o registrado é “{SUPERVISAO['crp']}”")

    juntos = _colado(" ".join(textos))
    if nome and _colado(nome) not in juntos:
        divergencias.append("o nome não aparece no PDF")
    if crp and _colado(crp) not in juntos:
        divergencias.append("o CRP não aparece no PDF")

    if divergencias:
        return Achado(
            "Supervisão técnica",
            AVISO,
            "confira: a supervisão não é a registrada",
            divergencias,
        )
    return Achado(
        "Supervisão técnica",
        OK,
        f"{SUPERVISAO['nome']} — CRP {SUPERVISAO['crp']}, como registrado",
    )


def ilustracoes(resultado: ResultadoRender) -> Achado:
    faltando: list[str] = []
    for bloco in resultado.blocos:
        personagem = (bloco.dados.get("personagem") or "").strip()
        if not personagem or bloco.tipo not in {"capa", "voz_personagem"}:
            continue
        if not (RAIZ / "assets" / "ilustracoes" / f"{personagem}.png").exists():
            faltando.append(
                f"“{personagem}” não existe em assets/ilustracoes — o material saiu "
                "sem essa ilustração"
            )
    if faltando:
        return Achado("Ilustrações", AVISO, "ilustração pedida não existe", faltando)
    return Achado("Ilustrações", OK, "ilustrações resolvidas")


def classificacao(resultado_classificador, blocos) -> Achado:
    detalhes: list[str] = []
    for indice, bloco in enumerate(blocos):
        if bloco.observacao:
            detalhes.append(f"bloco {indice} ({bloco.rotulo}): {bloco.observacao}")
        elif bloco.procedencia == "fallback":
            detalhes.append(f"bloco {indice}: caiu no bloco genérico")

    if resultado_classificador is not None and not resultado_classificador.rodou:
        return Achado(
            "Classificação",
            AVISO,
            "o classificador não rodou",
            [resultado_classificador.motivo_de_nao_rodar] + detalhes,
        )
    if detalhes:
        return Achado("Classificação", AVISO, f"{len(detalhes)} caso(s) para conferir", detalhes)
    return Achado("Classificação", OK, "todo trecho encaixou em um bloco do catálogo")


# ------------------------------------------------------------------ orquestra


def verificar(
    resultado: ResultadoRender,
    fonte_markdown: str,
    documento_layout=None,
    resultado_classificador=None,
    meta=None,
    progresso=lambda *_: None,
) -> Relatorio:
    doc = pymupdf.open(stream=resultado.pdf, filetype="pdf")
    textos = _texto_por_pagina(doc)
    relatorio = Relatorio(paginas=doc.page_count)

    passos = [
        ("Conferindo margens", lambda: texto_dentro_da_mancha(doc)),
        ("Conferindo fichas", lambda: fichas_inteiras(resultado, documento_layout)),
        ("Conferindo linhas soltas", lambda: orfas_e_viuvas(resultado, documento_layout)),
        ("Conferindo fontes", lambda: fontes_embutidas(doc)),
        ("Conferindo contraste", contraste_dos_tokens),
        ("Conferindo a paleta", lambda: cores_da_paleta(doc, meta.tema_valido if meta else "institucional")),
        ("Conferindo o logo", lambda: logo_em_toda_pagina(doc)),
        ("Conferindo a fundamentação", lambda: fundamentacao_literal(textos)),
        ("Conferindo o disclaimer", lambda: disclaimer_presente(textos)),
        ("Conferindo placeholders", lambda: sem_placeholders(textos)),
        ("Conferindo o sumário", lambda: sumario_confere(resultado, textos)),
        ("Conferindo o texto completo", lambda: texto_completo(fonte_markdown, textos, meta)),
        ("Conferindo a linguagem", lambda: linguagem(fonte_markdown, textos)),
        ("Conferindo personagens", lambda: personagens(resultado, meta)),
        ("Conferindo ilustrações", lambda: ilustracoes(resultado)),
        ("Conferindo a supervisão técnica", lambda: supervisao_tecnica(textos, meta)),
        ("Conferindo a classificação", lambda: classificacao(resultado_classificador, resultado.blocos)),
    ]

    for numero, (rotulo, funcao) in enumerate(passos, start=1):
        progresso(rotulo, 0.88 + 0.11 * numero / len(passos))
        if documento_layout is None and funcao.__name__ == "<lambda>" and "documento_layout" in str(funcao):
            continue
        try:
            relatorio.achados.append(funcao())
        except Exception as erro:  # uma verificação com defeito não derruba o resto
            relatorio.achados.append(
                Achado(rotulo.replace("Conferindo ", "").capitalize(), AVISO,
                       f"a verificação falhou: {type(erro).__name__}: {erro}"[:160])
            )

    doc.close()
    return relatorio
