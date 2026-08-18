"""Gera tema/tokens.css a partir de design/tokens.json.

O JSON é a única fonte de verdade dos VALORES (cor, pt, mm). O layout continua
em CSS escrito à mão, em tema/base.css e tema/blocos.css — este gerador não
inventa regra nenhuma, só declara variáveis.

Uso:  python3 diagramador/ferramentas/gerar_tokens_css.py
"""

from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TOKENS = RAIZ / "design" / "tokens.json"
SAIDA = RAIZ / "diagramador" / "tema" / "tokens.css"


def var(nome: str) -> str:
    return nome.replace("_", "-")


def gerar(tokens: dict) -> str:
    linhas: list[str] = [
        "/* GERADO por diagramador/ferramentas/gerar_tokens_css.py — não editar à mão.",
        f"   Fonte: design/tokens.json v{tokens['versao']} */",
        "",
        ":root {",
        "  /* ---- cor ---- */",
    ]

    for nome, dados in tokens["cor"].items():
        linhas.append(f"  --cor-{var(nome)}: {dados['valor']};")

    linhas += ["", "  /* ---- tipografia: famílias ---- */"]
    familia = tokens["tipografia"]["familia"]
    linhas.append(
        "  --fonte-display: "
        f"'{familia['display']['nome']}', '{familia['titulo']['nome']}', sans-serif;"
    )
    linhas.append(f"  --fonte-titulo: '{familia['titulo']['nome']}', sans-serif;")
    linhas.append(f"  --fonte-leitura: '{familia['leitura']['nome']}', sans-serif;")

    linhas += ["", "  /* ---- tipografia: escala ---- */"]
    for nome, e in tokens["tipografia"]["escala"].items():
        n = var(nome)
        linhas.append(f"  --{n}-tamanho: {e['pt']}pt;")
        linhas.append(f"  --{n}-entrelinha: {e['altura_linha']};")
        linhas.append(f"  --{n}-peso: {e['peso']};")
        if "tracking_em" in e:
            linhas.append(f"  --{n}-tracking: {e['tracking_em']}em;")

    g = tokens["grid"]
    linhas += [
        "",
        "  /* ---- grid ---- */",
        f"  --pagina-largura: {g['pagina']['largura_mm']}mm;",
        f"  --pagina-altura: {g['pagina']['altura_mm']}mm;",
        f"  --margem-topo: {g['margem_topo_mm']}mm;",
        f"  --margem-base: {g['margem_base_mm']}mm;",
        f"  --margem-lateral: {g['margem_lateral_mm']}mm;",
        f"  --largura-conteudo: {g['largura_conteudo_mm']}mm;",
        f"  --base-vertical: {g['base_vertical_mm']}mm;",
        f"  --padding-card: {g['padding_card_mm']}mm;",
        f"  --gap-colunas: {g['coluna_dupla_gap_mm']}mm;",
    ]
    for chave, valor in g["espaco"].items():
        linhas.append(f"  --esp-{chave.replace('_mm', '')}: {valor}mm;")

    f = tokens["forma"]
    linhas += [
        "",
        "  /* ---- forma ---- */",
        f"  --raio-card: {f['raio_card_mm']}mm;",
        f"  --raio-pill: {f['raio_pill_mm']}mm;",
        f"  --raio-mini: {f['raio_mini_mm']}mm;",
        f"  --sombra-card: {f['sombra_card']['valor']};",
        f"  --filete: {f['filete_mm']}mm;",
        f"  --hairline: {f['hairline_mm']}mm;",
        f"  --faixa-borda: {f['faixa_rodape']['altura_borda_mm']}mm;",
        f"  --faixa-apice: {f['faixa_rodape']['altura_apice_mm']}mm;",
        "",
        "  /* ---- marca ---- */",
        f"  --logo-altura: {tokens['marca']['logo_rodape']['altura_mm']}mm;",
        f"  --logo-base: {tokens['marca']['logo_rodape']['distancia_base_mm']}mm;",
        f"  --capa-contorno: {tokens['tipografia']['escala']['capa_titulo']['contorno']['largura_em']}em;",
        "}",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(gerar(tokens), encoding="utf-8")
    print(f"escrito: {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
