"""Testes do diagramador.

Rodar: python3 -m pytest diagramador/testes -q
(ou: python3 diagramador/testes/test_diagramador.py, sem pytest)

Cobrem o que quebra em silêncio: leitura do markdown, conversão de tipo,
salvaguardas do classificador, fonte embutida, e o e-book de exemplo inteiro
passando no QA.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "diagramador"))

from app import qa  # noqa: E402
from app.catalogo import CATALOGO, escolhiveis  # noqa: E402
from app.classificador import candidatos, classificar  # noqa: E402
from app.conversao import converter  # noqa: E402
from app.marcacao import ler  # noqa: E402
from app.pipeline import gerar  # noqa: E402

EXEMPLO = (RAIZ / "exemplo" / "porto_seguro.md").read_text(encoding="utf-8")


# ------------------------------------------------------------------ marcação


def test_front_matter_e_blocos():
    meta, blocos = ler(EXEMPLO)
    assert meta.titulo == "Porto Seguro"
    assert meta.personagem == "mamae_urso"
    assert meta.faltando() == []
    tipos = [bloco.tipo for bloco in blocos]
    assert tipos[0] == "carta_abertura"
    assert tipos.count("ficha_atividade") == 6
    assert tipos.count("abertura_bloco") == 3
    assert "tabela_comparativa" in tipos
    assert "formulario_imprimivel" in tipos


def test_ficha_tem_todos_os_campos():
    _, blocos = ler(EXEMPLO)
    ficha = next(b for b in blocos if b.tipo == "ficha_atividade")
    for campo in ("numero", "nome", "objetivo", "principio", "materiais", "passos",
                  "facil", "desafiador", "observar"):
        assert ficha.dados.get(campo), f"campo vazio na ficha: {campo}"
    assert len(ficha.dados["passos"]) == 4


def test_markdown_sem_diretiva_vira_secao():
    _, blocos = ler("## Um título\n\nUm parágrafo qualquer com bastante texto aqui.")
    assert [b.tipo for b in blocos] == ["secao_conceitual"]
    assert blocos[0].procedencia == "estrutura"


def test_diretiva_desconhecida_cai_no_generico_e_registra():
    _, blocos = ler(":::inventada\nTexto solto qualquer.\n:::")
    assert blocos[0].tipo == "secao_conceitual"
    assert blocos[0].procedencia == "fallback"
    assert "não existe no catálogo" in blocos[0].observacao


def test_html_do_autor_e_escapado():
    _, blocos = ler("Texto com <script>alert(1)</script> no meio dele, veja só.")
    corpo = blocos[0].dados["corpo"][0]["texto"]
    assert "<script>" not in corpo
    assert "&lt;script&gt;" in corpo


def test_campo_de_formulario_vira_linha_e_caixinha():
    _, blocos = ler(":::formulario\n### Modelo\n\n- Data: ___ ( ) opção\n:::")
    campo = blocos[0].dados["campos"][0]
    assert 'class="linha' in campo
    assert 'class="caixinha"' in campo


# ----------------------------------------------------------------- conversão


def test_conversao_cobre_todos_os_tipos_escolhiveis():
    _, blocos = ler(EXEMPLO)
    origem = next(b for b in blocos if b.tipo == "secao_conceitual")
    for tipo in escolhiveis():
        novo = converter(origem, tipo.nome, "correcao_manual")
        assert novo.tipo == tipo.nome
        esperados = set(CATALOGO[tipo.nome].campos)
        assert esperados.issubset(set(novo.dados) | {"extra"})


def test_conversao_preserva_o_texto():
    _, blocos = ler("## Dicas\n\nPrimeiro parágrafo com conteúdo suficiente para valer.")
    virou = converter(blocos[0], "caixa_atencao", "correcao_manual")
    assert "Primeiro parágrafo" in virou.dados["corpo"][0]["texto"]


# -------------------------------------------------------------- classificador


class _RespostaFalsa:
    stop_reason = "end_turn"

    def __init__(self, texto: str):
        self.content = [type("B", (), {"type": "text", "text": texto})()]


class _ClienteFalso:
    def __init__(self, texto: str):
        corpo = self

        class _Mensagens:
            def create(self, **_):
                return _RespostaFalsa(corpo.texto)

        self.texto = texto
        self.beta = type("Beta", (), {"messages": _Mensagens()})()


def test_classificador_promove_so_com_confianca_alta():
    _, blocos = ler(EXEMPLO)
    alvos = candidatos(blocos)
    assert alvos, "o exemplo precisa ter trecho sem diretiva"
    resposta = (
        '{"classificacoes": ['
        f'{{"indice": {alvos[0]}, "tipo": "caixa_atencao", "confianca": "alta", "motivo": "teste"}},'
        f'{{"indice": {alvos[1]}, "tipo": "roda_conversa", "confianca": "baixa", "motivo": "na dúvida"}}'
        "]}"
    )
    resultado = classificar(blocos, cliente=_ClienteFalso(resposta))
    assert resultado.rodou and resultado.aplicadas == 1
    assert blocos[alvos[0]].tipo == "caixa_atencao"
    assert blocos[alvos[1]].tipo == "secao_conceitual"
    assert "confiança baixa" in blocos[alvos[1]].observacao


def test_classificador_ignora_rotulo_fora_do_catalogo():
    _, blocos = ler(EXEMPLO)
    alvo = candidatos(blocos)[0]
    resposta = (
        '{"classificacoes": [{"indice": %d, "tipo": "capa", "confianca": "alta", "motivo": "x"}]}'
        % alvo
    )
    classificar(blocos, cliente=_ClienteFalso(resposta))
    assert blocos[alvo].tipo == "secao_conceitual"


def test_classificador_nao_encosta_em_bloco_de_diretiva():
    _, blocos = ler(EXEMPLO)
    for indice in candidatos(blocos):
        assert blocos[indice].procedencia == "estrutura"


def test_sem_credencial_o_pdf_sai_do_mesmo_jeito(monkeypatch=None):
    _, blocos = ler(EXEMPLO)
    resultado = classificar(blocos, cliente=None)
    # neste ambiente não há chave: precisa degradar sem exceção
    assert resultado.aplicadas == 0
    assert all(b.tipo in CATALOGO for b in blocos)


# ---------------------------------------------------------- ponta a ponta


def test_ebook_de_exemplo_passa_no_qa():
    entrega = gerar(EXEMPLO, "Ana Paula Ribeiro", "12/34567")
    relatorio = entrega.relatorio

    assert entrega.paginas >= 15
    assert len(entrega.miniaturas) == entrega.paginas
    assert entrega.pdf[:4] == b"%PDF"

    criticas = [a for a in relatorio.falhas]
    assert not criticas, "falhas de QA: " + "; ".join(
        f"{a.verificacao}: {a.resumo}" for a in criticas
    )

    por_nome = {a.verificacao: a for a in relatorio.achados}
    for verificacao in (
        "Texto dentro da mancha",
        "Fichas inteiras",
        "Fontes embutidas",
        "Cores da paleta",
        "Logo em toda página",
        "Fundamentação científica",
        "Disclaimer legal",
        "Placeholders preenchidos",
        "Sumário",
        "Texto completo",
        "Contraste",
    ):
        assert por_nome[verificacao].estado == qa.OK, (
            f"{verificacao}: {por_nome[verificacao].resumo}"
        )


def test_qa_pega_termo_de_linguagem_proibida():
    fonte = EXEMPLO.replace(
        "objetivo: Aumentar a previsibilidade do dia",
        "objetivo: Ajudar a criança portadora de autismo",
    )
    assert "portadora" in fonte
    entrega = gerar(fonte, "Ana Paula Ribeiro", "12/34567")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Linguagem")
    assert achado.estado == qa.AVISO
    assert any("portador" in d for d in achado.detalhes)


def test_qa_pega_placeholder_nao_preenchido():
    fonte = EXEMPLO.replace("Com carinho,", "Com carinho, [nome]")
    entrega = gerar(fonte, "Ana Paula Ribeiro", "12/34567")
    achado = next(
        a for a in entrega.relatorio.achados if a.verificacao == "Placeholders preenchidos"
    )
    assert achado.estado == qa.CRITICO


def test_personagem_inexistente_usa_ilustracao_padrao():
    fonte = EXEMPLO.replace("personagem: mamae_urso", "personagem: dragao_roxo")
    entrega = gerar(fonte, "Ana Paula Ribeiro", "12/34567")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Ilustrações")
    assert achado.estado == qa.AVISO
    assert entrega.pdf[:4] == b"%PDF"


def _ficha_de_teste(recheio: str, passos: int = 3) -> str:
    numerados = "\n".join(f"{n}. {recheio}" for n in range(1, passos + 1))
    return f"""---
titulo: Teste de encaixe
subtitulo: Ficha longa
---

:::ficha 1
### Uma ficha comprida

objetivo: {recheio}
principio: {recheio}
materiais: {recheio}

{numerados}

facil: {recheio}
desafiador: {recheio}
observar: {recheio}
:::
"""


def test_ficha_longa_cabe_reduzindo_a_escala():
    # ~1.4x a maior ficha real: precisa caber em uma página só, com redução
    recheio = " ".join(["Uma frase de tamanho médio para encher a ficha de teste."] * 4)
    entrega = gerar(_ficha_de_teste(recheio), "Ana Paula Ribeiro", "12/34567")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Fichas inteiras")
    assert achado.estado != qa.CRITICO, achado.detalhes


def test_ficha_impossivel_e_reportada_em_vez_de_quebrar_calada():
    # conteúdo que não cabe em uma página em escala nenhuma: o sistema não
    # inventa layout — ele reduz até o limite e depois avisa, com o que fazer
    recheio = " ".join(["Uma frase de tamanho médio para encher a ficha de teste."] * 14)
    entrega = gerar(_ficha_de_teste(recheio), "Ana Paula Ribeiro", "12/34567")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Fichas inteiras")
    assert achado.estado == qa.CRITICO
    assert any("encurte o texto" in d for d in achado.detalhes)


if __name__ == "__main__":
    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not nome.startswith("test_"):
            continue
        try:
            funcao()
            print(f"  ok    {nome}")
        except AssertionError as erro:
            falhas += 1
            print(f"  FALHA {nome}: {erro}")
        except Exception as erro:  # noqa: BLE001
            falhas += 1
            print(f"  ERRO  {nome}: {type(erro).__name__}: {erro}")
    print(f"\n{falhas} falha(s)")
    raise SystemExit(1 if falhas else 0)
