# Diagramador de e-books — TEA Formation

Web app que recebe um markdown e devolve um PDF diagramado no padrão visual da
TEA Formation, pronto para vender. Feito para usar do navegador do tablet.

**Subir o markdown → esperar → olhar o preview → baixar.** Sem parada no meio.

- Como escrever o markdown: [`../FORMATO.md`](../FORMATO.md)
- Como colocar no ar: [`../DEPLOY.md`](../DEPLOY.md)
- De onde veio cada decisão visual: [`../design/tokens.md`](../design/tokens.md)

## O princípio

**Renderizador determinístico, não gerador de design.**

- O design system foi descoberto uma vez, medido em pixel nas cartilhas
  aprovadas, e congelado em `../design/tokens.json`.
- Em produção o LLM tem **uma** função: escolher o rótulo do bloco para os
  trechos que a estrutura do markdown não tipou. Ele não escolhe cor, fonte,
  espaçamento, margem nem hierarquia. Nunca.
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
   ├─ classificador.py .... só os trechos sem diretiva; devolve um rótulo, nada mais
   ├─ conversao.py ........ troca de tipo preservando o conteúdo (LLM e interface)
   ├─ renderizador.py ..... blocos → HTML → PDF (sumário em 2 passadas, encaixe de ficha)
   ├─ qa.py ............... 15 verificações sobre o PDF, o layout e o markdown
   └─ pipeline.py ......... amarra tudo e reporta progresso
                              │
                         principal.py (FastAPI) + estatico/ (a interface)
```

| Arquivo | O que faz |
|---|---|
| `app/catalogo.py` | os 14 tipos de bloco, seus campos e qual diretiva os produz |
| `app/marcacao.py` | leitura do markdown; escapa HTML do autor antes de qualquer coisa |
| `app/classificador.py` | chamada ao Claude, restrita a rótulos do catálogo |
| `app/conversao.py` | converte um bloco em outro tipo sem perder texto |
| `app/titulo.py` | título de capa com contorno, em SVG, com encaixe por medida real |
| `app/renderizador.py` | montagem, sumário com página real, encaixe de ficha longa |
| `app/qa.py` | o relatório que substitui a revisão detalhada |
| `app/seguranca.py` | senha e cookie assinado |
| `tema/tokens.css` | **gerado** de `design/tokens.json` — não editar à mão |
| `tema/base.css`, `tema/blocos.css` | layout, escrito à mão e versionado |

## Rodar na máquina

```bash
pip install -r ../requirements.txt
export SENHA_APP=umasenha
export ANTHROPIC_API_KEY=sk-ant-...       # opcional: sem ela o app funciona igual
uvicorn diagramador.app.principal:app --reload --port 8000
```

## Testes

```bash
python3 diagramador/testes/test_diagramador.py      # sem pytest
python3 -m pytest diagramador/testes -q             # com pytest
```

O teste de ponta a ponta gera o e-book de exemplo inteiro e exige QA sem falha.

## Ferramentas

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py       # tokens.json → tokens.css
python3 diagramador/ferramentas/verificar_fontes.py       # roda também no build
python3 diagramador/ferramentas/preparar_ilustracoes.py <pasta>   # JPG → PNG recortado
python3 diagramador/ferramentas/amostra_ficha.py          # amostra da ficha
```

## O que o QA verifica

Texto dentro da mancha · ficha inteira em uma página · órfãs e viúvas · fontes
embutidas · contraste ≥ 4.5:1 no corpo · **nenhuma cor fora dos tokens** · logo em
toda página na mesma posição · fundamentação científica literal exatamente duas
vezes · disclaimer legal · nenhum placeholder · sumário com página real · todo o
texto do markdown presente · linguagem da marca · ilustrações resolvidas ·
classificação sem caso pendente.

Verde é o que passou. O que falhou diz **qual página** e **o quê**.
