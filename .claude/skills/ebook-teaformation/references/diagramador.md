# O diagramador — como o sistema funciona e como mexer nele

Aplicação web que recebe markdown e devolve PDF diagramado. Vive em
`diagramador/` no repositório `Padrao`. Roda no Render; uso pelo navegador do
tablet ou do computador.

## O caminho de um material

```
markdown
   │
   ├─ marcacao.py ......... front matter, diretivas ::: e markdown padrão → blocos
   ├─ classificador.py .... só os trechos sem diretiva; devolve um rótulo, nada mais
   ├─ conversao.py ........ troca de tipo preservando o conteúdo
   ├─ renderizador.py ..... blocos → HTML → PDF (sumário em 2 passadas, encaixe de ficha)
   ├─ qa.py ............... 17 verificações sobre o PDF, o layout e o markdown
   └─ pipeline.py ......... amarra tudo e reporta progresso
                              │
                         principal.py (FastAPI) + estatico/ (a interface)
```

Um e-book de 20 páginas leva ~4 segundos, do markdown ao relatório.

## Onde mexer em quê

| Precisa mudar | Vá em |
|---|---|
| cor, medida, tipografia | `design/tokens.json`, depois rode o gerador |
| como um bloco é desenhado | `diagramador/tema/blocos.css` |
| como o markdown é lido | `diagramador/app/marcacao.py` |
| o que o QA verifica | `diagramador/app/qa.py` |
| a interface | `diagramador/app/estatico/` |
| a convenção de escrita | `FORMATO.md` |

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py   # tokens.json → tokens.css
python3 diagramador/testes/test_diagramador.py        # tem que dar 0 falhas
uvicorn diagramador.app.principal:app --reload        # com SENHA_APP definida
```

## O papel do LLM, e por que ele é tão pequeno

O classificador recebe só os trechos que a estrutura do markdown não tipou com
certeza, e devolve **um rótulo do catálogo**. Nada além disso. As salvaguardas
existem porque um classificador solto vira gerador de layout sem ninguém
perceber:

- só blocos genéricos são candidatos; o que veio de uma diretiva `:::` é decisão
  explícita do autor e não se toca;
- rótulo fora do catálogo é descartado;
- promoção só vale com confiança alta — na dúvida, fica genérico e o caso entra
  no relatório;
- sem chave de API, sem rede ou com erro, o PDF sai igual e o relatório diz que a
  classificação não rodou.

Modelo: `claude-opus-5`, com `output_config.effort: low` e saída em JSON Schema.
Não passe `temperature` — os modelos da geração 5 rejeitam com 400.

## O que o QA verifica

O relatório é o que substitui a revisão detalhada, então ele precisa ser
confiável a ponto de você baixar o PDF só olhando o verde:

Texto dentro da mancha · ficha inteira em uma página · órfãs e viúvas · fontes
embutidas · contraste ≥ 4.5:1 no corpo (nos dois temas) · **nenhuma cor fora dos
tokens do tema ativo** · logo em toda página na mesma posição · fundamentação
científica literal exatamente duas vezes · disclaimer legal · nenhum placeholder ·
sumário com página real · todo o texto do markdown presente · linguagem da marca ·
**nenhum personagem sem pedido** · ilustração pedida que existe · **supervisão
técnica igual à registrada** · classificação sem caso pendente.

Verde é o que passou. O que falhou diz **qual página** e **o quê**.

## Armadilhas que já custaram caro

Estas são reais, aconteceram durante a construção, e todas passariam
despercebidas sem o QA:

- **WeasyPrint ignora `@font-face` em silêncio** se você não passar uma
  `FontConfiguration` explícita para `CSS(...)` **e** para `render()`. O material
  sai inteiro, só que na fonte do sistema. Hoje há uma verificação no build da
  imagem que derruba o deploy se as fontes da marca não estiverem embutidas.
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

## Encaixe de ficha longa

Uma ficha ocupa uma página inteira. Se não couber, o pipeline reduz a escala em
passos (100 → 96 → 92 → 88%) e **registra a redução**. Isso é ajuste numérico de
encaixe, não decisão de layout — é a única coisa que muda em runtime. Se nem a
88% couber, o QA falha dizendo para encurtar o texto ou dividir em duas
atividades, em vez de quebrar a ficha calado.

## Deploy

Render, via `render.yaml` (blueprint) e `Dockerfile`. Duas variáveis: `SENHA_APP`
(entrar no app) e `ANTHROPIC_API_KEY` (classificação). `CHAVE_SESSAO` o Render
gera. O passo a passo executável só pelo tablet está em `DEPLOY.md`.

Nada do conteúdo é gravado em disco: markdown, PDF e miniaturas ficam em memória
por até 6 horas.
