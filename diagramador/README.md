# Diagramador de e-books — TEA Formation

Aplicação web que recebe um markdown e devolve um PDF diagramado no padrão visual da
TEA Formation. **Estado: Fase 0 concluída, aguardando aprovação.**

## Princípio

Renderizador determinístico, não gerador de design.

- O design system foi descoberto uma vez (Fase 0), medido nas cartilhas aprovadas e
  congelado em `design/tokens.json`.
- Em produção o LLM tem **uma** função: classificar cada trecho do markdown em um tipo
  de bloco do catálogo. Ele não escolhe cor, fonte, espaçamento, margem ou hierarquia.
- Todo layout vem de CSS escrito à mão: `tema/base.css` e `tema/blocos.css`.
- Trecho que não encaixa em nenhum bloco vira o bloco genérico mais próximo e **entra no
  relatório** — o sistema nunca inventa layout.

## O que já existe

| Caminho | O que é |
|---|---|
| `../design/tokens.json` | tokens medidos, fonte única dos valores |
| `../design/tokens.md` | de onde veio cada token, divergências e decisões |
| `tema/tokens.css` | gerado de tokens.json por `ferramentas/gerar_tokens_css.py` |
| `tema/base.css` | página, fontes embutidas, mobília de rodapé — escrito à mão |
| `tema/blocos.css` | catálogo de blocos — escrito à mão |
| `ferramentas/amostra_ficha.py` | renderiza a ficha de amostra da Fase 0 |
| `amostras/` | ficha aprovada + comparação lado a lado com a cartilha |

## Rodar a amostra

```
pip install weasyprint pymupdf
python3 ferramentas/gerar_tokens_css.py
python3 ferramentas/amostra_ficha.py
```
