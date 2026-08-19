"""Testes do diagramador.

Rodar: python3 -m pytest diagramador/testes -q
(ou: python3 diagramador/testes/test_diagramador.py, sem pytest)

Cobrem o que quebra em silêncio: leitura do markdown, conversão de tipo,
salvaguardas do classificador, fonte embutida, a linha de comando de ponta a
ponta, a skill em dia com o repositório, e o e-book de exemplo inteiro passando
no QA.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "diagramador"))

from app import qa  # noqa: E402
from app.catalogo import CATALOGO, escolhiveis  # noqa: E402
from app.renderizador import TOKENS  # noqa: E402
from app.classificador import aplicar, candidatos, classificar, pedido  # noqa: E402
from app.conversao import converter  # noqa: E402
from app.marcacao import ler  # noqa: E402
from app.pipeline import gerar  # noqa: E402

EXEMPLO = (RAIZ / "exemplo" / "porto_seguro.md").read_text(encoding="utf-8")
SUPERVISAO = TOKENS["regras_do_material"]["supervisao_tecnica"]
NOME, CRP = SUPERVISAO["nome"], SUPERVISAO["crp"]


# ------------------------------------------------------------------ marcação


def test_front_matter_e_blocos():
    meta, blocos = ler(EXEMPLO)
    assert meta.titulo == "Porto Seguro"
    assert meta.faltando() == []
    # o exemplo é o modelo que o fundador copia: sai institucional e sem personagem
    assert not meta.pediu_personagem
    assert meta.tema_valido == "institucional"
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


# ------------------------------------------------------ regras da marca


def test_supervisao_registrada_e_a_da_marca():
    assert NOME == "Ingrid Ceron"
    assert CRP == "12/15726"
    assert "autismo" in SUPERVISAO["especialidade"] and "ABA" in SUPERVISAO["especialidade"]


def test_sem_pedido_nenhum_personagem_aparece():
    entrega = gerar(EXEMPLO, NOME, CRP)
    assert all(not b.dados.get("ilustracao") for b in entrega.blocos)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Personagens")
    assert achado.estado == qa.OK
    assert "nenhum personagem" in achado.resumo


def test_personagem_entra_quando_pedido():
    fonte = EXEMPLO.replace("subtitulo:", "personagem: mamae_urso\nsubtitulo:", 1)
    entrega = gerar(fonte, NOME, CRP)
    capa = next(b for b in entrega.blocos if b.tipo == "capa")
    assert capa.dados["ilustracao"].endswith("mamae_urso.png")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Personagens")
    assert achado.estado == qa.OK and "a pedido" in achado.resumo


def test_voz_sem_nome_nao_traz_ilustracao():
    _, blocos = ler(":::voz\n### Uma palavra\nTexto da fala do personagem aqui.\n:::")
    assert blocos[0].dados.get("personagem", "") == ""


def test_tema_padrao_e_institucional_sem_cor_do_teanimal():
    entrega = gerar(EXEMPLO, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Cores da paleta")
    assert achado.estado == qa.OK, achado.detalhes
    assert "institucional" in achado.resumo


def test_tema_teanimal_so_quando_pedido():
    fonte = EXEMPLO.replace("subtitulo:", "tema: teanimal\nsubtitulo:", 1)
    meta, _ = ler(fonte)
    assert meta.tema_valido == "teanimal"
    entrega = gerar(fonte, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Cores da paleta")
    assert achado.estado == qa.OK, achado.detalhes
    assert "teanimal" in achado.resumo


def test_tema_desconhecido_cai_no_institucional():
    meta, _ = ler("---\ntitulo: X\nsubtitulo: Y\ntema: arco_iris\n---\n\n## Seção\n\nTexto.")
    assert meta.tema_valido == "institucional"


def test_qa_avisa_quando_a_supervisao_nao_e_a_registrada():
    entrega = gerar(EXEMPLO, "Outra Pessoa", "99/99999")
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Supervisão técnica")
    assert achado.estado == qa.AVISO
    assert any("Ingrid Ceron" in d for d in achado.detalhes)


def test_comentario_do_autor_nao_vai_para_o_pdf():
    fonte = EXEMPLO.replace("## O que é uma crise", "<!-- nota interna secreta -->\n\n## O que é uma crise")
    entrega = gerar(fonte, NOME, CRP)
    import pymupdf

    documento = pymupdf.open(stream=entrega.pdf, filetype="pdf")
    texto = "".join(pagina.get_text() for pagina in documento)
    assert "nota interna" not in texto


# --------------------------------------------- classificação feita na sessão


def test_pedido_traz_so_os_trechos_sem_diretiva():
    _, blocos = ler(EXEMPLO)
    bruto = pedido(blocos)
    indices = [t["indice"] for t in bruto["trechos"]]

    assert indices == candidatos(blocos)
    assert all(blocos[i].procedencia == "estrutura" for i in indices)
    assert all(t["resumo"].strip() for t in bruto["trechos"])


def test_aplicar_impoe_as_mesmas_salvaguardas_da_api():
    _, blocos = ler(EXEMPLO)
    alvos = candidatos(blocos)
    assert len(alvos) >= 2, "o exemplo precisa ter trecho sem diretiva"

    resultado = aplicar(blocos, [
        {"indice": alvos[0], "tipo": "caixa_atencao", "confianca": "alta", "motivo": "x"},
        {"indice": alvos[1], "tipo": "roda_conversa", "confianca": "baixa", "motivo": "na dúvida"},
        {"indice": alvos[0], "tipo": "capa", "confianca": "alta", "motivo": "fora do catálogo"},
        {"indice": 9999, "tipo": "caixa_atencao", "confianca": "alta", "motivo": "índice inválido"},
    ])

    assert resultado.rodou and resultado.aplicadas == 1
    assert blocos[alvos[0]].tipo == "caixa_atencao"
    assert blocos[alvos[1]].tipo == "secao_conceitual"
    assert "confiança baixa" in blocos[alvos[1]].observacao


def test_confirmar_o_generico_com_confianca_alta_encerra_o_caso():
    # o material está classificado: nenhum trecho pode continuar "por conferir"
    _, blocos = ler(EXEMPLO)
    alvos = candidatos(blocos)
    aplicar(blocos, [
        {"indice": i, "tipo": "secao_conceitual", "confianca": "alta", "motivo": "explicação"}
        for i in alvos
    ])
    assert candidatos(blocos) == []


def test_sem_classificacao_o_relatorio_lista_cada_trecho_pendente():
    entrega = gerar(EXEMPLO, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Classificação")
    assert achado.estado == qa.AVISO
    assert "não passaram por classificação" in achado.resumo


def test_relatorio_endereca_o_bloco_pelo_indice_que_correcoes_usa():
    # o número que o relatório mostra tem que ser o mesmo que --trechos lista e
    # que --correcoes aceita; senão a correção cai no bloco errado
    _, blocos = ler(EXEMPLO)
    alvo = candidatos(blocos)[0]

    entrega = gerar(EXEMPLO, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Classificação")
    assert any(d.startswith(f"bloco {alvo}:") for d in achado.detalhes), achado.detalhes

    corrigida = gerar(EXEMPLO, NOME, CRP, correcoes={alvo: "caixa_atencao"})
    trocado = [b for b in corrigida.blocos if b.indice_fonte == alvo]
    assert len(trocado) == 1 and trocado[0].tipo == "caixa_atencao"


# ----------------------------------------------------- linha de comando e skill


def test_cli_do_markdown_ao_pdf():
    import json
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as pasta:
        pasta = Path(pasta)
        material = pasta / "material.md"
        material.write_text(EXEMPLO, encoding="utf-8")

        listagem = subprocess.run(
            [sys.executable, str(RAIZ / "diagramar.py"), str(material), "--trechos"],
            capture_output=True, text=True, check=True,
        )
        trechos = json.loads(listagem.stdout)["trechos"]
        assert trechos, "o exemplo precisa ter trecho para classificar"

        decisao = pasta / "classificacao.json"
        decisao.write_text(json.dumps({"classificacoes": [
            {"indice": t["indice"], "tipo": "secao_conceitual",
             "confianca": "alta", "motivo": "explicação"}
            for t in trechos
        ]}), encoding="utf-8")

        geracao = subprocess.run(
            [sys.executable, str(RAIZ / "diagramar.py"), str(material),
             "--classificacao", str(decisao), "--sem-miniaturas"],
            capture_output=True, text=True,
        )
        assert geracao.returncode == 0, geracao.stdout + geracao.stderr
        assert (pasta / "material.pdf").read_bytes()[:4] == b"%PDF"

        relatorio = (pasta / "material-qa.md").read_text(encoding="utf-8")
        assert "0 falha(s)" in relatorio
        assert SUPERVISAO["crp"] in relatorio


def test_skill_esta_em_dia():
    # a skill carrega uma cópia do runtime para rodar sem o repositório; se
    # alguém mexeu no original e esqueceu o empacotador, é aqui que aparece
    import subprocess

    conferencia = subprocess.run(
        [sys.executable, str(RAIZ / "diagramador" / "ferramentas" / "empacotar_skill.py"),
         "--conferir"],
        capture_output=True, text=True,
    )
    assert conferencia.returncode == 0, conferencia.stdout


def test_skill_repete_a_supervisao_e_a_fundamentacao_sem_variar():
    skill = (RAIZ / ".claude" / "skills" / "ebook-teaformation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert SUPERVISAO["nome"] in skill and SUPERVISAO["crp"] in skill
    assert SUPERVISAO["especialidade"] in skill
    # a citação vem em bloco de citação e quebrada em várias linhas: comparar
    # sem marcador nem espaço é o que pega troca de palavra de verdade
    sem_citacao = "\n".join(
        linha[2:] if linha.startswith("> ") else linha for linha in skill.splitlines()
    )
    for literal in ("fundamentacao_cientifica", "disclaimer_legal"):
        texto = TOKENS["texto_fixo"][literal]
        assert "".join(texto.split()) in "".join(sem_citacao.split()), literal


# ---------------------------------------------------------- ponta a ponta


def test_ebook_de_exemplo_passa_no_qa():
    entrega = gerar(EXEMPLO, NOME, CRP)
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
        "Personagens",
        "Supervisão técnica",
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
    entrega = gerar(fonte, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Linguagem")
    assert achado.estado == qa.AVISO
    assert any("portador" in d for d in achado.detalhes)


def test_qa_pega_placeholder_nao_preenchido():
    fonte = EXEMPLO.replace("Com carinho,", "Com carinho, [nome]")
    entrega = gerar(fonte, NOME, CRP)
    achado = next(
        a for a in entrega.relatorio.achados if a.verificacao == "Placeholders preenchidos"
    )
    assert achado.estado == qa.CRITICO


def test_personagem_inexistente_sai_sem_ilustracao_e_avisa():
    fonte = EXEMPLO.replace("subtitulo:", "personagem: dragao_roxo\nsubtitulo:", 1)
    entrega = gerar(fonte, NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Ilustrações")
    assert achado.estado == qa.AVISO
    capa = next(b for b in entrega.blocos if b.tipo == "capa")
    assert capa.dados["ilustracao"] == ""
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
    entrega = gerar(_ficha_de_teste(recheio), NOME, CRP)
    achado = next(a for a in entrega.relatorio.achados if a.verificacao == "Fichas inteiras")
    assert achado.estado != qa.CRITICO, achado.detalhes


def test_ficha_impossivel_e_reportada_em_vez_de_quebrar_calada():
    # conteúdo que não cabe em uma página em escala nenhuma: o sistema não
    # inventa layout — ele reduz até o limite e depois avisa, com o que fazer
    recheio = " ".join(["Uma frase de tamanho médio para encher a ficha de teste."] * 14)
    entrega = gerar(_ficha_de_teste(recheio), NOME, CRP)
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
