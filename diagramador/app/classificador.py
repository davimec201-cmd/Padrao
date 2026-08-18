"""Classificador — a única coisa que o LLM faz neste sistema.

Ele recebe trechos que a estrutura do markdown não tipou com certeza e devolve
**um rótulo do catálogo** para cada um. Não escolhe cor, fonte, espaçamento,
margem, hierarquia ou ordem. Não reescreve texto. Não cria bloco novo.

Salvaguardas:

* só blocos genéricos (`procedencia == "estrutura"`) são candidatos — o que veio
  de uma diretiva `:::` é decisão explícita do autor e não se toca;
* rótulo fora do catálogo é descartado;
* promoção só vale com `confianca == "alta"`; qualquer hesitação mantém o bloco
  genérico e registra o caso;
* sem chave de API, sem rede ou com erro, tudo continua genérico e o relatório
  diz que a classificação não rodou. O PDF sai de qualquer forma.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

from .catalogo import CLASSIFICAVEIS, FALLBACK, CATALOGO, Bloco
from .conversao import converter

MODELO = "claude-opus-5"
MAX_TOKENS = 4000
LIMITE_DE_TRECHO = 700  # caracteres enviados por bloco
_SEM_TAG = re.compile(r"<[^>]+>")

ESQUEMA = {
    "type": "object",
    "properties": {
        "classificacoes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "indice": {"type": "integer"},
                    "tipo": {"type": "string", "enum": list(CLASSIFICAVEIS)},
                    "confianca": {"type": "string", "enum": ["alta", "baixa"]},
                    "motivo": {"type": "string"},
                },
                "required": ["indice", "tipo", "confianca", "motivo"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["classificacoes"],
    "additionalProperties": False,
}

INSTRUCOES = """Você classifica trechos de um e-book terapêutico infantil da TEA Formation.

Sua única tarefa: para cada trecho, escolher UM tipo de bloco do catálogo. Você não
decide layout, cor, fonte, tamanho, espaçamento nem ordem — nada disso. Só o rótulo.

Catálogo:
{catalogo}

Regras:
- Na dúvida, responda "secao_conceitual" com confianca "baixa". É o comportamento
  correto: o sistema mantém o bloco genérico e registra o caso para revisão humana.
- Só use confianca "alta" quando o trecho tiver a forma característica do tipo.
- "carta_abertura": texto em segunda pessoa dirigido a quem lê, com despedida ou
  assinatura. Costuma ser o primeiro trecho do material.
- "dicas_praticas": vários títulos curtos imperativos, cada um com um parágrafo.
- "roda_conversa": lista de perguntas para fazer à criança.
- "voz_personagem": fala de um personagem do Vale da Harmonia (Mamãe Urso, Leo,
  Jojo, Cora, Pipo, Marcos, Professora Canguru, Sr. Miau) em tom afetivo.
- "caixa_atencao": aviso curto, ressalva clínica, ponto crítico. Poucas linhas.
- "secao_encerramento": fecho do material, quando buscar ajuda, última palavra.
- "secao_conceitual": explicação, conceito, mecanismo. É o padrão.

Responda apenas o JSON do esquema, com uma entrada por trecho recebido."""


@dataclass
class Resultado:
    aplicadas: int = 0
    rodou: bool = False
    motivo_de_nao_rodar: str = ""
    registros: list[dict] = field(default_factory=list)


def _resumo(bloco: Bloco) -> str:
    titulo, _, corpo = "", "", ""
    dados = bloco.dados
    titulo = _SEM_TAG.sub("", dados.get("titulo", "") or dados.get("rotulo", ""))
    partes: list[str] = []
    for elemento in dados.get("corpo", []):
        if elemento.get("texto"):
            partes.append(_SEM_TAG.sub("", elemento["texto"]))
        for item in elemento.get("itens", []):
            partes.append("- " + _SEM_TAG.sub("", item))
    corpo = "\n".join(partes)
    cabecalho = f"TÍTULO: {titulo}\n" if titulo else "SEM TÍTULO\n"
    return (cabecalho + corpo)[:LIMITE_DE_TRECHO]


def candidatos(blocos: list[Bloco]) -> list[int]:
    return [
        indice
        for indice, bloco in enumerate(blocos)
        if bloco.procedencia == "estrutura" and bloco.tipo == FALLBACK
    ]


def _credenciais_disponiveis() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    # perfil gravado por `ant auth login`
    from pathlib import Path

    return (Path.home() / ".config" / "anthropic").exists()


def classificar(blocos: list[Bloco], cliente=None) -> Resultado:
    """Classifica os blocos genéricos in-place. Devolve o que foi feito.

    `cliente` existe para teste: recebe um objeto com a mesma interface de
    `anthropic.Anthropic()`.
    """
    resultado = Resultado()
    indices = candidatos(blocos)
    if not indices:
        resultado.rodou = True
        return resultado

    if cliente is None:
        if not _credenciais_disponiveis():
            resultado.motivo_de_nao_rodar = (
                "sem credencial da API (ANTHROPIC_API_KEY) — todos os trechos sem "
                "diretiva ficaram como seção de texto comum"
            )
            return resultado
        try:
            import anthropic
        except ImportError:  # pragma: no cover
            resultado.motivo_de_nao_rodar = "pacote anthropic não instalado"
            return resultado

    catalogo = "\n".join(
        f"- {nome}: {CATALOGO[nome].descricao}" for nome in CLASSIFICAVEIS
    )
    trechos = "\n\n".join(
        f"### trecho {indice}\n{_resumo(blocos[indice])}" for indice in indices
    )

    try:
        if cliente is None:
            cliente = anthropic.Anthropic()
        resposta = cliente.beta.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=INSTRUCOES.format(catalogo=catalogo),
            output_config={
                "effort": "low",
                "format": {"type": "json_schema", "schema": ESQUEMA},
            },
            messages=[{"role": "user", "content": trechos}],
        )
        if resposta.stop_reason == "refusal":
            resultado.motivo_de_nao_rodar = "o modelo recusou classificar este material"
            return resultado
        bruto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text")
        dados = json.loads(bruto)
    except Exception as erro:  # rede, cota, JSON inválido: o PDF sai igual
        resultado.motivo_de_nao_rodar = f"{type(erro).__name__}: {erro}"[:200]
        return resultado

    resultado.rodou = True
    validos = set(indices)

    for entrada in dados.get("classificacoes", []):
        indice = entrada.get("indice")
        tipo = entrada.get("tipo")
        confianca = entrada.get("confianca")
        motivo = (entrada.get("motivo") or "")[:160]

        if indice not in validos or tipo not in CLASSIFICAVEIS:
            continue
        if tipo == blocos[indice].tipo:
            continue
        if confianca != "alta":
            blocos[indice].observacao = (
                f"o classificador considerou '{CATALOGO[tipo].rotulo}' com confiança baixa; "
                f"ficou como seção de texto comum — {motivo}"
            )
            resultado.registros.append(
                {"indice": indice, "tipo": tipo, "aplicado": False, "motivo": motivo}
            )
            continue

        blocos[indice] = converter(blocos[indice], tipo, procedencia="classificador")
        blocos[indice].observacao = f"classificado como {CATALOGO[tipo].rotulo} — {motivo}"
        resultado.aplicadas += 1
        resultado.registros.append(
            {"indice": indice, "tipo": tipo, "aplicado": True, "motivo": motivo}
        )

    return resultado
