# Diagramador de e-books — TEA Formation

Recebe um markdown e devolve um PDF diagramado no padrão visual da TEA
Formation, pronto para vender. Roda por linha de comando, dentro de uma sessão:

```bash
python3 diagramar.py material.md --trechos                        # o que falta decidir
python3 diagramar.py material.md --classificacao classificacao.json
```

Saem o PDF, o relatório de QA em markdown e a imagem de cada página. Um material
de 20 páginas leva ~4 segundos. Sem servidor, sem senha, sem chave de API.

- Como escrever o markdown: [`../FORMATO.md`](../FORMATO.md)
- Como usar dentro de uma sessão: [`../.claude/skills/ebook-teaformation/SKILL.md`](../.claude/skills/ebook-teaformation/SKILL.md)
- De onde veio cada decisão visual: [`../design/tokens.md`](../design/tokens.md)

## Três regras de marca que o sistema garante

1. **Personagem só a pedido.** Sem `personagem:` no cabeçalho ou `:::voz <nome>`,
   o material sai sem nenhum personagem do TEAnimal — a capa fica tipográfica.
2. **Paleta institucional por padrão.** Azul, branco e bege. As cores lúdicas
   entram com `tema: teanimal`.
3. **Supervisão técnica registrada.** Ingrid Ceron, CRP 12/15726 — vem de
   `design/tokens.json` e o diagramador preenche sozinho.

As três têm verificação no QA. Detalhes em [`../CLAUDE.md`](../CLAUDE.md).

## O princípio

**Renderizador determinístico, não gerador de design.**

- O design system foi descoberto uma vez, medido em pixel nas cartilhas
  aprovadas, e congelado em `../design/tokens.json`.
- O modelo tem **uma** função: escolher o rótulo do bloco para os trechos que a
  estrutura do markdown não tipou. Ele não escolhe cor, fonte, espaçamento,
  margem nem hierarquia. Nunca.
- Todo layout vem de CSS escrito à mão: `tema/base.css` e `tema/blocos.css`.
- Trecho que não encaixa em nenhum bloco vira o genérico mais próximo e **entra
  no relatório** — o sistema não inventa layout.

Material com cara de IA acontece quando o modelo decide layout na hora. Aqui ele
nunca decide.

## Como as peças se encaixam

```
markdown
   │
   ├─ marcacao.py ......... front matter, diretivas ::: e markdown padrão → blocos
   ├─ classificador.py .... pedido() monta o que falta decidir; aplicar() recebe
   │                        a resposta e impõe as salvaguardas
   ├─ conversao.py ........ troca de tipo preservando o conteúdo
   ├─ renderizador.py ..... blocos → HTML → PDF (sumário em 2 passadas, encaixe de ficha)
   ├─ qa.py ............... 17 verificações sobre o PDF, o layout e o markdown
   └─ pipeline.py ......... amarra tudo
                              │
                           cli.py ← ../diagramar.py
```

| Arquivo | O que faz |
|---|---|
| `app/catalogo.py` | os 14 tipos de bloco, seus campos e qual diretiva os produz |
| `app/marcacao.py` | leitura do markdown; escapa HTML do autor antes de qualquer coisa |
| `app/classificador.py` | monta o pedido de rótulos e aplica a resposta, restrita ao catálogo |
| `app/conversao.py` | converte um bloco em outro tipo sem perder texto |
| `app/titulo.py` | título de capa com contorno, em SVG, com encaixe por medida real |
| `app/renderizador.py` | montagem, sumário com página real, encaixe de ficha longa |
| `app/qa.py` | o relatório que substitui a revisão detalhada |
| `app/cli.py` | a linha de comando: `--trechos`, `--classificacao`, `--correcoes` |
| `tema/tokens.css` | **gerado** de `design/tokens.json` — não editar à mão |
| `tema/base.css`, `tema/blocos.css` | layout, escrito à mão e versionado |

## Rodar na máquina

```bash
pip install -r ../requirements.txt
python3 diagramar.py exemplo/porto_seguro.md --saida /tmp/porto.pdf
```

O WeasyPrint precisa de Pango, Cairo e fontconfig no sistema. Código de saída 0
quer dizer que passou; 2 quer dizer que o PDF saiu com falha crítica no QA.

Quem classifica os trechos é o modelo que está conduzindo a sessão. Para
automação sem ninguém na sala existe `--usar-api`, que precisa de
`ANTHROPIC_API_KEY` e do pacote `anthropic` (está em
`requirements-ferramentas.txt`, não no runtime).

## Testes

```bash
python3 diagramador/testes/test_diagramador.py      # sem pytest
python3 -m pytest diagramador/testes -q             # com pytest
```

O teste de ponta a ponta gera o e-book de exemplo inteiro e exige QA sem falha.

## Ferramentas

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py       # tokens.json → tokens.css
python3 diagramador/ferramentas/verificar_fontes.py       # confere @font-face embutida
python3 diagramador/ferramentas/preparar_ilustracoes.py <pasta>   # JPG → PNG recortado
python3 diagramador/ferramentas/amostra_ficha.py          # amostra da ficha
python3 diagramador/ferramentas/empacotar_skill.py --zip  # atualiza e empacota a skill
```

## O que o QA verifica

Texto dentro da mancha · ficha inteira em uma página · órfãs e viúvas · fontes
embutidas · contraste ≥ 4.5:1 no corpo (nos dois temas) · **nenhuma cor fora dos
tokens do tema ativo** · logo em toda página na mesma posição · fundamentação
científica literal exatamente duas vezes · disclaimer legal · nenhum placeholder ·
sumário com página real · todo o texto do markdown presente · linguagem da marca ·
**nenhum personagem sem pedido** · ilustrações resolvidas · **supervisão técnica
igual à registrada** · classificação sem caso pendente.

Verde é o que passou. O que falhou diz **qual página** e **o quê**.
