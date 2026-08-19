# O diagramador — como o sistema funciona e como mexer nele

Programa em Python que recebe markdown e devolve PDF diagramado. Roda dentro da
skill (`scripts/`) e também no repositório `Padrao`, com o mesmo código: o
layout de `scripts/` espelha a raiz do repositório de propósito, para que os
caminhos resolvam igual nos dois lugares.

## O caminho de um material

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
                           cli.py (a linha de comando) ← diagramar.py
```

Um e-book de 20 páginas leva ~4 segundos, do markdown ao relatório.

## Onde mexer em quê

| Precisa mudar | Vá em |
|---|---|
| cor, medida, tipografia | `design/tokens.json`, depois rode o gerador de CSS |
| como um bloco é desenhado | `diagramador/tema/blocos.css` |
| como o markdown é lido | `diagramador/app/marcacao.py` |
| o que o QA verifica | `diagramador/app/qa.py` |
| as opções da linha de comando | `diagramador/app/cli.py` |
| a convenção de escrita | `FORMATO.md` |

No repositório, depois de mexer em qualquer coisa:

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py    # se mexeu em tokens.json
python3 diagramador/testes/test_diagramador.py         # tem que dar 0 falhas
python3 diagramador/ferramentas/empacotar_skill.py     # leva a mudança para a skill
```

A skill carrega uma cópia do runtime porque precisa rodar sem o repositório por
perto. O empacotador é a única direção permitida (repositório → skill), e o
teste `test_skill_esta_em_dia` falha se alguém esquecer de rodá-lo. Nunca edite
`.claude/skills/ebook-teaformation/scripts/` à mão: a próxima execução do
empacotador apaga a edição.

## O papel do modelo, e por que ele é tão pequeno

Quem classifica é o modelo que está conduzindo a sessão — não há chamada de API
no caminho normal. Ele recebe só os trechos que a estrutura do markdown não
tipou com certeza e devolve **um rótulo do catálogo**. Nada além disso.

As salvaguardas moram todas em `classificador.aplicar()`, e é por isso que os
dois caminhos (sessão e API) passam por lá:

- só blocos genéricos são candidatos; o que veio de uma diretiva `:::` é decisão
  explícita do autor e não se toca;
- rótulo fora do catálogo é descartado;
- promoção só vale com confiança alta — na dúvida, fica genérico e o caso entra
  no relatório;
- trecho sem resposta continua genérico e aparece no relatório como pendência.

`--usar-api` existe para automação sem ninguém na sala: chama `claude-opus-5`
com `output_config.effort: low` e saída em JSON Schema. Não passe `temperature`
— os modelos da geração 5 rejeitam com 400.

## O endereço de um bloco

O relatório e `--correcoes` falam a mesma língua: o **índice na lista escrita
pelo autor**, antes de capa, sumário e página final entrarem. É o campo
`indice_fonte`. O índice depois da montagem não serve de endereço para ninguém e
não aparece em lugar nenhum.

## O que o QA verifica

O relatório é o que substitui a revisão detalhada, então ele precisa ser
confiável a ponto de o PDF ser baixado só olhando o verde:

Texto dentro da mancha · ficha inteira em uma página · órfãs e viúvas · fontes
embutidas · contraste ≥ 4.5:1 no corpo (nos dois temas) · **nenhuma cor fora dos
tokens do tema ativo** · logo em toda página na mesma posição · fundamentação
científica literal exatamente duas vezes · disclaimer legal · nenhum placeholder ·
sumário com página real · todo o texto do markdown presente · linguagem da marca ·
**nenhum personagem sem pedido** · ilustração pedida que existe · **supervisão
técnica igual à registrada** · classificação sem caso pendente.

Verde é o que passou. O que falhou diz **qual página** e **o quê**. Falha
crítica devolve código de saída 2.

## Armadilhas que já custaram caro

Estas são reais, aconteceram durante a construção, e todas passariam
despercebidas sem o QA:

- **WeasyPrint ignora `@font-face` em silêncio** se você não passar uma
  `FontConfiguration` explícita para `CSS(...)` **e** para `render()`. O material
  sai inteiro, só que na fonte do sistema. `diagramador/ferramentas/verificar_fontes.py`
  existe para pegar isso.
- **`text-stroke` e `text-shadow` não existem no WeasyPrint.** O título de capa
  com contorno é feito em SVG, com duas passadas de `<text>`: uma só de traço,
  outra só de preenchimento (`paint-order` também não é honrado).
- **`gap` de flex dentro de caixa de margem `@page`** soma um vão sobrando à
  direita — o rodapé passava 2mm da mancha. Use margem nos filhos.
- **Número de página junto da marca faz o logo dançar** entre páginas de 1 e 2
  dígitos. O número foi para a esquerda; a marca ficou fixa.
- **`body { background }` cobre a cor da `@page`** — a página divisória perdia o
  fundo. O fundo é da `@page`, só.
- **Antialiasing não é cor nova.** O guardião da paleta aceita mistura de dois
  tokens; o que ele reprova é um terceiro tom.
- **Jinja2 com `autoescape` ligado escapa duas vezes.** O texto do autor já foi
  escapado em `marcacao.inline()`; o ambiente é criado com `autoescape=False` de
  propósito.

## Encaixe de ficha longa

Uma ficha ocupa uma página inteira. Se não couber, o pipeline reduz a escala em
passos (100 → 96 → 92 → 88%) e **registra a redução**. Isso é ajuste numérico de
encaixe, não decisão de layout — é a única coisa que muda em runtime. Se nem a
88% couber, o QA falha dizendo para encurtar o texto ou dividir em duas
atividades, em vez de quebrar a ficha calado.

## Dependências

`weasyprint`, `pymupdf`, `jinja2`, `fonttools`, `numpy` — a lista fixada está em
`scripts/requirements.txt`. O WeasyPrint precisa de Pango, Cairo e fontconfig no
sistema. Nada é gravado fora da pasta onde o material foi gerado, e nada sai
para a rede.
