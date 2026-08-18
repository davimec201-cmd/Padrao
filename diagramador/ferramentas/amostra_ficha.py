"""Renderiza uma ficha_atividade de amostra para aprovação visual da Fase 0.

Conteúdo real, tirado da Atividade 5 do Porto Seguro (estrutura), com a pele
dos tokens medidos nas cartilhas.

Uso:  python3 diagramador/ferramentas/amostra_ficha.py
Saída: diagramador/amostras/ficha_atividade.pdf (+ PNG das páginas)
"""

from __future__ import annotations

from pathlib import Path

from weasyprint import CSS, HTML

RAIZ = Path(__file__).resolve().parents[2]
TEMA = RAIZ / "diagramador" / "tema"
SAIDA = RAIZ / "diagramador" / "amostras"

HTML_AMOSTRA = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Amostra — ficha de atividade</title></head>
<body>

<div class="marca-rodape">
  <img src="../../assets/marca/peca.png" alt="">
  <span><span class="marca-tea">TEA</span><span class="marca-formation">Formation</span></span>
  <span class="pagina"></span>
</div>
<div class="rodape-titulo">Porto Seguro</div>

<section class="ficha">
  <header class="ficha-cabecalho">
    <div class="ficha-numero">5</div>
    <div class="ficha-titulo">
      <span class="rotulo">Atividade</span>
      <h2>O Abraço de Urso</h2>
    </div>
  </header>

  <div class="ficha-par">
    <div>
      <span class="rotulo">Objetivo terapêutico</span>
      <p>Oferecer regulação por pressão profunda, respeitando integralmente o
      consentimento da criança.</p>
    </div>
    <div>
      <span class="rotulo">Princípio ABA-TCC</span>
      <p>Regulação sensorial proprioceptiva + pareamento com segurança: o corpo
      se organiza antes da mente.</p>
    </div>
  </div>

  <div class="ficha-materiais">
    <p><span class="personagem">Com a Mamãe Urso:</span> apenas vocês dois — e, se a
    criança preferir, um cobertor pesadinho ou almofadas. O tradicional abraço de urso
    da Mamãe Urso é famoso no Vale: firme, demorado e sempre oferecido, nunca imposto.</p>
  </div>

  <div class="ficha-passos">
    <h3>Passo a passo</h3>
    <ol class="passos">
      <li>SEMPRE pergunte ou sinalize antes: “Quer um abraço de urso?” Braços abertos,
      espere a criança vir. Se ela não vier, respeite — ofereça o cobertor como
      alternativa.</li>
      <li>Se ela aceitar, abrace com pressão firme e constante (pressão profunda acalma;
      toque leve pode irritar). Sem balançar, sem falar muito.</li>
      <li>Conte mentalmente até 10-20 segundos. Algumas crianças pedem “mais apertado”
      — atenda dentro do confortável.</li>
      <li>Para crianças que não gostam de abraço: enrole no cobertor como um “burrito”,
      ou faça uma “prensa de almofadas” nas costas e pernas, sempre em tom de
      brincadeira e com consentimento.</li>
    </ol>
  </div>

  <div class="ficha-niveis">
    <div class="facil">
      <span class="rotulo">Mais fácil</span>
      <p>Substitua o abraço por pressão nas mãos ou nos ombros, ou pelo cobertor pesado
      sozinho.</p>
    </div>
    <div class="desafiador">
      <span class="rotulo">Mais desafiador</span>
      <p>Ensine a criança a PEDIR o abraço quando sentir o “amarelo” — apontando o
      termômetro ou usando um gesto combinado.</p>
    </div>
  </div>

  <footer class="ficha-observar">
    <span class="rotulo">O que observar</span>
    <p>O corpo da criança relaxa durante a pressão (ombros baixam, respiração
    desacelera)? Ou ela se esquiva? Toque nunca é neutro no espectro — mapeie e
    registre as preferências dela.</p>
  </footer>
</section>

</body>
</html>
"""


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    pdf = SAIDA / "ficha_atividade.pdf"

    documento = HTML(string=HTML_AMOSTRA, base_url=str(TEMA / "amostra.html"))
    documento.write_pdf(
        pdf,
        stylesheets=[
            CSS(filename=str(TEMA / "tokens.css")),
            CSS(filename=str(TEMA / "base.css")),
            CSS(filename=str(TEMA / "blocos.css")),
        ],
    )
    print(f"escrito: {pdf.relative_to(RAIZ)}")

    import pymupdf

    doc = pymupdf.open(pdf)
    print(f"páginas: {doc.page_count}")
    for pagina in doc:
        png = SAIDA / f"ficha_atividade_p{pagina.number + 1}.png"
        pagina.get_pixmap(dpi=150).save(png)
        print(f"escrito: {png.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
