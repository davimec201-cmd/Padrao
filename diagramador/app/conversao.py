"""Conversão entre tipos de bloco.

Serve a dois caminhos: o classificador, que às vezes promove uma seção genérica
para um tipo mais específico, e o seletor da interface, quando você discorda da
classificação e troca o tipo na miniatura.

A conversão passa sempre por uma forma canônica — título + lista de elementos de
conteúdo — e reconstrói os campos do tipo de destino a partir dela. Nada de
layout é decidido aqui: só qual campo recebe qual texto.
"""

from __future__ import annotations

import re

from .catalogo import CATALOGO, Bloco
from .marcacao import normalizar

_SEM_TAG = re.compile(r"<[^>]+>")


def _texto(elemento: dict) -> str:
    if "texto" in elemento:
        return elemento["texto"]
    if elemento.get("itens"):
        return " ".join(elemento["itens"])
    return ""


def desmontar(bloco: Bloco) -> tuple[str, list[dict]]:
    """Qualquer bloco → (título, elementos de conteúdo)."""
    dados = bloco.dados
    tipo = bloco.tipo

    if tipo in {"secao_conceitual", "secao_encerramento", "voz_personagem"}:
        return dados.get("titulo", ""), list(dados.get("corpo", []))

    if tipo == "caixa_atencao":
        return dados.get("rotulo", ""), list(dados.get("corpo", []))

    if tipo == "carta_abertura":
        return "", list(dados.get("corpo", [])) + list(dados.get("assinatura", []))

    if tipo == "dicas_praticas":
        elementos: list[dict] = []
        for dica in dados.get("dicas", []):
            if dica.get("titulo"):
                elementos.append({"tipo": "subtitulo", "texto": dica["titulo"]})
            elementos.extend(dica.get("corpo", []))
        return dados.get("titulo", ""), elementos

    if tipo == "roda_conversa":
        return dados.get("titulo", ""), [
            {"tipo": "lista_numerada", "itens": list(dados.get("perguntas", []))}
        ]

    if tipo == "tabela_comparativa":
        return "", [
            {
                "tipo": "tabela",
                "cabecalhos": list(dados.get("cabecalhos", [])),
                "linhas": [list(l) for l in dados.get("linhas", [])],
            }
        ]

    if tipo == "abertura_bloco":
        elementos = []
        if dados.get("frase"):
            elementos.append({"tipo": "paragrafo", "texto": dados["frase"]})
        return dados.get("nome", ""), elementos

    if tipo == "ficha_atividade":
        elementos = []
        for chave, rotulo in (
            ("objetivo", "Objetivo terapêutico"),
            ("principio", "Princípio ABA-TCC"),
            ("materiais", "Materiais"),
        ):
            if dados.get(chave):
                elementos.append({"tipo": "subtitulo", "texto": rotulo})
                elementos.append({"tipo": "paragrafo", "texto": dados[chave]})
        if dados.get("passos"):
            elementos.append({"tipo": "lista_numerada", "itens": list(dados["passos"])})
        for chave, rotulo in (
            ("facil", "Mais fácil"),
            ("desafiador", "Mais desafiador"),
            ("observar", "O que observar"),
        ):
            if dados.get(chave):
                elementos.append({"tipo": "subtitulo", "texto": rotulo})
                elementos.append({"tipo": "paragrafo", "texto": dados[chave]})
        elementos.extend(dados.get("extra", []))
        return dados.get("nome", ""), elementos

    if tipo == "formulario_imprimivel":
        return dados.get("titulo", ""), (
            [{"tipo": "paragrafo", "texto": dados["instrucao"]}] if dados.get("instrucao") else []
        ) + [{"tipo": "lista", "itens": list(dados.get("campos", []))}]

    return dados.get("titulo", ""), list(dados.get("corpo", []))


def _primeiro_paragrafo(elementos: list[dict]) -> str:
    for elemento in elementos:
        if elemento["tipo"] == "paragrafo":
            return elemento["texto"]
    return ""


def montar(tipo: str, titulo: str, elementos: list[dict], origem: Bloco) -> dict:
    """(título, elementos) → campos do tipo de destino."""
    if tipo in {"secao_conceitual", "secao_encerramento"}:
        return {"titulo": titulo, "corpo": elementos}

    if tipo == "caixa_atencao":
        return {"rotulo": titulo or "Ponto de atenção", "corpo": elementos}

    if tipo == "carta_abertura":
        # a assinatura é o último parágrafo curto, se houver
        corpo = list(elementos)
        assinatura: list[dict] = []
        if corpo and corpo[-1]["tipo"] == "paragrafo" and len(_SEM_TAG.sub("", corpo[-1]["texto"])) < 160:
            assinatura = [corpo.pop()]
        return {"corpo": corpo, "assinatura": assinatura}

    if tipo == "voz_personagem":
        return {
            "personagem": origem.dados.get("personagem", ""),
            "titulo": titulo,
            "corpo": elementos,
        }

    if tipo == "dicas_praticas":
        dicas: list[dict] = []
        for elemento in elementos:
            if elemento["tipo"] in {"titulo", "subtitulo"}:
                dicas.append({"titulo": elemento["texto"], "corpo": []})
            elif dicas:
                dicas[-1]["corpo"].append(elemento)
            else:
                dicas.append({"titulo": "", "corpo": [elemento]})
        return {"titulo": titulo, "dicas": dicas}

    if tipo == "roda_conversa":
        perguntas: list[str] = []
        for elemento in elementos:
            if elemento["tipo"] in {"lista", "lista_numerada"}:
                perguntas.extend(elemento["itens"])
            elif elemento["tipo"] == "paragrafo":
                perguntas.append(elemento["texto"])
        return {"titulo": titulo or "Roda de conversa", "perguntas": perguntas}

    if tipo == "tabela_comparativa":
        for elemento in elementos:
            if elemento["tipo"] == "tabela":
                return {"cabecalhos": elemento["cabecalhos"], "linhas": elemento["linhas"]}
        # sem tabela no conteúdo: devolve duas colunas vazias, e o QA registra
        return {"cabecalhos": [titulo or "—", "—"], "linhas": []}

    if tipo == "abertura_bloco":
        return {
            "numero": origem.dados.get("numero", ""),
            "nome": titulo,
            "frase": _primeiro_paragrafo(elementos),
        }

    if tipo == "ficha_atividade":
        passos: list[str] = []
        campos: dict[str, str] = {}
        sobra: list[dict] = []
        rotulo_atual = ""
        mapa = {
            "objetivo terapeutico": "objetivo",
            "objetivo": "objetivo",
            "principio aba-tcc": "principio",
            "principio": "principio",
            "materiais": "materiais",
            "mais facil": "facil",
            "mais desafiador": "desafiador",
            "o que observar": "observar",
        }
        for elemento in elementos:
            if elemento["tipo"] in {"titulo", "subtitulo"}:
                rotulo_atual = mapa.get(normalizar(_SEM_TAG.sub("", elemento["texto"])), "")
                continue
            if elemento["tipo"] == "lista_numerada" and not passos:
                passos = elemento["itens"]
                continue
            if rotulo_atual and elemento["tipo"] == "paragrafo" and rotulo_atual not in campos:
                campos[rotulo_atual] = elemento["texto"]
                continue
            sobra.append(elemento)
        return {
            "numero": origem.dados.get("numero", ""),
            "nome": titulo,
            "objetivo": campos.get("objetivo", ""),
            "principio": campos.get("principio", ""),
            "materiais": campos.get("materiais", ""),
            "passos": passos,
            "facil": campos.get("facil", ""),
            "desafiador": campos.get("desafiador", ""),
            "observar": campos.get("observar", ""),
            "extra": sobra,
        }

    if tipo == "formulario_imprimivel":
        campos_lista: list[str] = []
        instrucao = ""
        for elemento in elementos:
            if elemento["tipo"] in {"lista", "lista_numerada"}:
                campos_lista.extend(elemento["itens"])
            elif elemento["tipo"] == "paragrafo" and not instrucao:
                instrucao = elemento["texto"]
            elif elemento["tipo"] == "paragrafo":
                campos_lista.append(elemento["texto"])
        return {
            "titulo": titulo,
            "instrucao": instrucao,
            "campos": campos_lista,
            "repeticoes": int(origem.dados.get("repeticoes", 1) or 1),
        }

    return {"titulo": titulo, "corpo": elementos}


def converter(bloco: Bloco, tipo_destino: str, procedencia: str) -> Bloco:
    """Troca o tipo de um bloco preservando o conteúdo."""
    if tipo_destino not in CATALOGO:
        return bloco
    if tipo_destino == bloco.tipo:
        return bloco

    titulo, elementos = desmontar(bloco)
    return Bloco(
        tipo=tipo_destino,
        dados=montar(tipo_destino, titulo, elementos, bloco),
        origem_linha=bloco.origem_linha,
        procedencia=procedencia,
        observacao=bloco.observacao,
    )
