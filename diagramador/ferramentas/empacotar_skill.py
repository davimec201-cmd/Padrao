#!/usr/bin/env python3
"""Monta a skill `ebook-teaformation` a partir das fontes canônicas.

A skill precisa rodar sozinha, em qualquer sessão, sem o repositório por perto —
por isso ela carrega uma cópia do runtime, das fontes, das ilustrações e dos
tokens. Cópia é dívida: duas verdades acabam divergindo. Este script paga a
dívida mantendo uma direção só, do repositório para a skill, e o teste
`test_skill_esta_em_dia` reclama se alguém esquecer de rodar.

    python3 diagramador/ferramentas/empacotar_skill.py            # atualiza
    python3 diagramador/ferramentas/empacotar_skill.py --conferir # só verifica
    python3 diagramador/ferramentas/empacotar_skill.py --zip      # e empacota

O layout de `scripts/` espelha a raiz do repositório de propósito: assim
`RAIZ = Path(__file__).parents[2]` resolve para o lugar certo nos dois casos, e
o código não precisa saber onde está rodando.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SKILL = RAIZ / ".claude" / "skills" / "ebook-teaformation"
SCRIPTS = SKILL / "scripts"

sys.path.insert(0, str(RAIZ / "diagramador"))
from app.catalogo import CATALOGO  # noqa: E402

# de onde, para onde (dentro de scripts/)
ARQUIVOS = [
    ("diagramar.py", "diagramar.py"),
    ("requirements.txt", "requirements.txt"),
    ("design/tokens.json", "design/tokens.json"),
]
PASTAS = [
    ("assets/fontes", "assets/fontes", "*.ttf"),
    ("assets/ilustracoes", "assets/ilustracoes", "*.png"),
    ("assets/marca", "assets/marca", "*.png"),
    ("diagramador/tema", "diagramador/tema", "*.css"),
    ("diagramador/app", "diagramador/app", "*.py"),
    ("diagramador/app/templates", "diagramador/app/templates", "*.html"),
    ("diagramador/app/templates/blocos", "diagramador/app/templates/blocos", "*.html"),
]
# markdown de exemplo que vai junto, para a skill ter o que mostrar
EXEMPLOS = [("exemplo/porto_seguro.md", "assets/exemplo-porto-seguro.md")]


def _explicacao(dados: dict) -> str:
    """A linha que explica um token, em ordem de utilidade para quem lê."""
    for campo in ("nota", "uso", "reservado_para", "formula"):
        if dados.get(campo):
            return dados[campo]
    return ""


def _tokens() -> dict:
    return json.loads((RAIZ / "design" / "tokens.json").read_text(encoding="utf-8"))


# ------------------------------------------------- referência gerada do tokens


def design_system_md() -> str:
    t = _tokens()
    override = t["temas"]["teanimal"]["cor"]
    linhas: list[str] = []
    esc = linhas.append

    esc("# Design system — valores congelados")
    esc("")
    esc("Fonte de verdade: `design/tokens.json`. Esta página é gerada a partir dele")
    esc("por `diagramador/ferramentas/empacotar_skill.py` — não edite à mão, edite o")
    esc("tokens e rode o empacotador.")
    esc("")
    esc("Todo valor aqui é **medido** nas cartilhas aprovadas, veio do **manual** de")
    esc("identidade, ou é **derivado** por fórmula de um dos dois. Não há valor escolhido")
    esc("no olho — e é isso que faz o material novo parecer da mesma família do antigo.")
    esc("")
    esc("## Paleta")
    esc("")
    esc("### Institucional — o padrão de todo material")
    esc("")
    esc("| Cor | Valor | Significado / uso |")
    esc("|---|---|---|")
    for nome, dados in t["paleta"]["institucional"].items():
        esc(f"| `{nome}` | `{dados['valor']}` | {_explicacao(dados)} |")
    esc("")
    esc("### TEAnimal — só com `tema: teanimal`")
    esc("")
    esc("| Cor | Valor | Significado / uso |")
    esc("|---|---|---|")
    for nome, dados in t["paleta"]["teanimal"].items():
        esc(f"| `{nome}` | `{dados['valor']}` | {_explicacao(dados)} |")
    esc("")
    esc("## Papéis de cor")
    esc("")
    esc("Não use a paleta direto: use o papel. É o que permite trocar de tema sem")
    esc("rediagramar, e o que impede o coral de virar cor de texto por engano.")
    esc("")
    esc("| Papel | Institucional | TEAnimal | Para quê |")
    esc("|---|---|---|---|")
    for papel, dados in t["cor"].items():
        outro = override.get(papel)
        esc(
            f"| `{papel}` | `{dados['valor']}` | "
            f"{'`' + outro + '`' if outro else '—'} | {_explicacao(dados)} |"
        )
    esc("")
    esc("### As três regras de cor")
    esc("")
    esc("1. **Coral nunca é cor de texto.** `#FF7345` sobre branco dá 2.70:1 — reprova em")
    esc("   qualquer tamanho. Coral é preenchimento, com navy por cima (5.19:1). Foi assim")
    esc("   que se manteve a paleta exata do manual entregando 4.5:1 no corpo, em vez de")
    esc("   escolher entre as duas coisas.")
    esc("2. **Azul institucional com texto branco só em display.** `#FFFFFF` sobre")
    esc("   `#0193C8` dá 3.49:1: serve para ≥18pt. Para corpo, use o wash claro com navy")
    esc("   (12.45:1) ou o azul escurecido `#016E96` (5.72:1).")
    esc("3. **Cor de um universo não entra em material do outro.** Se precisar da paleta")
    esc("   lúdica, peça o tema; não misture.")
    esc("")
    esc("Todo texto de corpo (≤13pt) fica ≥ 4.5:1 nos dois temas. São 32 pares conferidos")
    esc("a cada geração, pelo QA.")
    esc("")
    esc("## Tipografia")
    esc("")
    papeis = {
        "display": "Display e títulos de capa",
        "titulo": "Títulos, rótulos e rodapé",
        "leitura": "Leitura longa (o corpo do texto)",
    }
    for papel, descricao in papeis.items():
        familia = t["tipografia"]["familia"].get(papel)
        if familia:
            pesos = ", ".join(
                a.split("-")[-1].removesuffix(".ttf") for a in familia["arquivos"]
            )
            esc(f"- **{descricao}:** {familia['nome']} ({pesos})")
    esc("")
    esc("Omnes Huggies (a face arredondada das capas de cartilha) foi **descartada por")
    esc("decisão do fundador**. O papel de display ficou com Poppins Bold.")
    esc("")
    esc("| Nível | pt | Entrelinha | Peso | Observação |")
    esc("|---|---|---|---|---|")
    for nome, dados in t["tipografia"]["escala"].items():
        origem = (dados.get("origem", "") or "").split(" (decisão")[0][:110]
        esc(
            f"| `{nome}` | {dados['pt']} | {dados['altura_linha']} | "
            f"{dados['peso']} | {origem} |"
        )
    esc("")
    esc("O corpo de **11.5pt com 17.5pt de entrelinha** não foi inventado: é o avanço de")
    esc("linha medido no card informativo da CARTILHA_01 p4. O e-book herda o ritmo")
    esc("vertical do material aprovado.")
    esc("")
    g = t["grid"]
    esc("## Grid")
    esc("")
    esc(f"- Página: **{g['pagina']['formato']}**, "
        f"{g['pagina']['largura_mm']} × {g['pagina']['altura_mm']}mm")
    esc(f"- Margens: topo {g['margem_topo_mm']}mm, base {g['margem_base_mm']}mm, "
        f"laterais **{g['margem_lateral_mm']}mm**")
    esc(f"- Largura de conteúdo: **{g['largura_conteudo_mm']}mm** — medido, idêntico nas 4 cartilhas")
    esc(f"- Medida de linha: ~{g['medida_texto_caracteres']} caracteres")
    esc(f"- Base vertical: **{g['base_vertical_mm']}mm** (= 17.5pt, o avanço do corpo). "
        "Toda a escala de espaço é múltipla dela: "
        + " / ".join(f"{v}mm" for v in g["espaco"].values()))
    esc(f"- Padding de card: {g['padding_card_mm']}mm")
    esc("")
    f = t["forma"]
    esc("## Formas")
    esc("")
    esc(f"- Raio de card: **{f['raio_card_mm']}mm** (medido: 8.2mm nas cartilhas)")
    esc(f"- Raio de pill: **{f['raio_pill_mm']}mm** (medido: 3.9mm)")
    esc(f"- Filete: {f['filete_mm']}mm · fio: {f['hairline_mm']}mm")
    esc(f"- Faixa em arco do rodapé de capa: {f['faixa_rodape']['altura_borda_mm']}mm na borda, "
        f"{f['faixa_rodape']['altura_apice_mm']}mm no ápice — assinatura gráfica da marca")
    esc(f"- Sombra de card: `{f['sombra_card']['valor']}`")
    esc("")
    esc("## Catálogo de blocos")
    esc("")
    esc("Todo material se monta com estes tipos. Nenhum outro é inventado em runtime.")
    esc("")
    esc("| Bloco | Diretiva | O que é |")
    esc("|---|---|---|")
    for tipo in CATALOGO.values():
        diretiva = f"`:::{tipo.diretiva}`" if tipo.diretiva else "— automático"
        esc(f"| **{tipo.rotulo}** | {diretiva} | {tipo.descricao} |")
    esc("")
    esc("A **ficha de atividade** é o bloco mais importante e ocupa uma página inteira:")
    esc("número + nome, par lado a lado objetivo/princípio, parágrafo de materiais, passo")
    esc("a passo numerado, par mais fácil/mais desafiador, e o rodapé “o que observar”.")
    esc("Uma ficha nunca quebra entre páginas.")
    esc("")
    return "\n".join(linhas)


def formato_markdown_md() -> str:
    """A convenção de escrita é a mesma do repositório; só o cabeçalho muda."""
    corpo = (RAIZ / "FORMATO.md").read_text(encoding="utf-8")
    primeira, resto = corpo.split("\n", 1)
    assert primeira.startswith("# "), "FORMATO.md precisa começar com o título"
    return (
        "# Formato do markdown de um e-book\n"
        "\n"
        "> Cópia da convenção de escrita do projeto `Padrao` (`FORMATO.md`). Se você\n"
        "> tiver o repositório, ele é a versão viva.\n"
        + resto
    )


# ------------------------------------------------------------------- espelhar


def _plano() -> list[tuple[Path, Path]]:
    par: list[tuple[Path, Path]] = []
    for origem, destino in ARQUIVOS:
        par.append((RAIZ / origem, SCRIPTS / destino))
    for origem, destino in EXEMPLOS:
        par.append((RAIZ / origem, SKILL / destino))
    for origem, destino, padrao in PASTAS:
        for arquivo in sorted((RAIZ / origem).glob(padrao)):
            par.append((arquivo, SCRIPTS / destino / arquivo.name))
    return par


def espelhar(conferir: bool) -> list[str]:
    """Copia (ou confere) tudo. Devolve a lista do que está fora do lugar."""
    pendencias: list[str] = []
    plano = _plano()
    esperados = {destino.resolve() for _, destino in plano}

    for origem, destino in plano:
        igual = destino.exists() and filecmp.cmp(origem, destino, shallow=False)
        if igual:
            continue
        pendencias.append(str(destino.relative_to(SKILL)))
        if not conferir:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)

    # arquivo que sobrou de uma versão anterior é ruído que engana quem lê
    if SCRIPTS.exists():
        for existente in SCRIPTS.rglob("*"):
            if existente.is_dir() or "__pycache__" in existente.parts:
                continue
            if existente.resolve() not in esperados:
                pendencias.append(f"sobrando: {existente.relative_to(SKILL)}")
                if not conferir:
                    existente.unlink()

    for nome, conteudo in (
        ("design-system.md", design_system_md()),
        ("formato-markdown.md", formato_markdown_md()),
    ):
        referencia = SKILL / "references" / nome
        atual = referencia.read_text(encoding="utf-8") if referencia.exists() else None
        if atual != conteudo:
            pendencias.append(f"references/{nome}")
            if not conferir:
                referencia.parent.mkdir(parents=True, exist_ok=True)
                referencia.write_text(conteudo, encoding="utf-8")

    return pendencias


def empacotar() -> Path:
    alvo = RAIZ / "ebook-teaformation.skill"
    with zipfile.ZipFile(alvo, "w", zipfile.ZIP_DEFLATED) as zip_:
        for arquivo in sorted(SKILL.rglob("*")):
            if arquivo.is_dir() or "__pycache__" in arquivo.parts:
                continue
            zip_.write(arquivo, Path("ebook-teaformation") / arquivo.relative_to(SKILL))
    return alvo


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--conferir", action="store_true", help="não escreve nada")
    analisador.add_argument("--zip", action="store_true", help="gera o .skill")
    opcoes = analisador.parse_args(argumentos)

    pendencias = espelhar(opcoes.conferir)

    if opcoes.conferir:
        if pendencias:
            print("a skill está desatualizada:")
            for item in pendencias:
                print(f"  - {item}")
            print("\nrode: python3 diagramador/ferramentas/empacotar_skill.py")
            return 1
        print("skill em dia")
        return 0

    if pendencias:
        print(f"atualizados {len(pendencias)} arquivo(s):")
        for item in pendencias[:20]:
            print(f"  - {item}")
        if len(pendencias) > 20:
            print(f"  - (+{len(pendencias) - 20})")
    else:
        print("nada a atualizar")

    if opcoes.zip:
        alvo = empacotar()
        tamanho = alvo.stat().st_size / 1024
        print(f"\n{alvo.name} — {tamanho:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
