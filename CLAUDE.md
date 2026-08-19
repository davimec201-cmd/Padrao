# Regras do repositório

Instruções permanentes para quem mexe aqui — pessoa ou modelo. Valem em qualquer
sessão, sem precisar ser repetidas.

## Diagramador de e-books (TEA Formation)

### 1. Supervisão técnica — dado fixo, nunca inventar

| Campo | Valor |
|---|---|
| Nome | **Ingrid Ceron** |
| CRP | **12/15726** |
| Especialidade | **Especialista em autismo (TEA) e em Terapia ABA** |

Está registrado em `design/tokens.json` → `regras_do_material.supervisao_tecnica`,
e é de lá que a interface preenche o formulário. Nunca escreva outro nome, outro
CRP nem outra especialidade em exemplo, teste, documentação ou material gerado.
O QA compara e avisa quando divergir.

### 2. Personagens do Universo TEAnimal — só a pedido

Material **não leva personagem** por padrão. Nenhum: nem na capa, nem no miolo,
nem como ilustração de reserva.

O personagem só entra quando o material pede, de duas formas:

- `personagem: mamae_urso` no cabeçalho do markdown → capa com o personagem;
- `:::voz mamae_urso` → aquele bloco com o personagem ao lado da fala.

Sem pedido, a capa é tipográfica com a peça da marca. Verificado pelo QA
("Personagens"), que falha se um personagem aparecer sem ter sido pedido.

### 3. Cores — institucional é o padrão

A paleta padrão é a da **TEA Formation**: azul (`#0193C8`), branco, bege
(`#F9F4E5`) e navy (`#1F2D3D`) no texto.

As cores do **Universo TEAnimal** (coral, verde, amarelo, roxo, tons dos
habitantes) são para público infantil e **só entram quando o material pede**
`tema: teanimal` no cabeçalho.

Os dois temas vivem em `design/tokens.json`: os papéis de cor em `cor` são o
institucional, e `temas.teanimal` re-aponta os papéis de acento. Trocar de tema
não muda estrutura, grid nem tipografia. O QA avisa quando encontra cor de um
universo em material do outro.

### 4. O sistema é uma skill, não um app

O jeito de usar é: colar o markdown na sessão e pedir para diagramar. A skill
`ebook-teaformation` roda `scripts/diagramar.py`, e sai PDF + relatório de QA +
imagem de cada página. Não há servidor, senha, deploy nem chave de API — quem
classifica os trechos é o modelo que está conduzindo a conversa.

O app web (FastAPI, Render, Docker) foi descartado por decisão do fundador em
2026-08-19. O código está no histórico do git; não ressuscite sem pedido.

### 5. O sistema é um renderizador determinístico

- Design descoberto uma vez, medido nas cartilhas, congelado em tokens.
- Em produção o LLM só **classifica trecho em tipo de bloco**. Não escolhe cor,
  fonte, espaçamento, margem nem hierarquia.
- Layout é CSS escrito à mão em `diagramador/tema/`.
- Trecho que não encaixa vira o bloco genérico e **entra no relatório**. Nunca
  invente layout novo em runtime.

### 6. Antes de dar por pronto

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py   # se mexeu em tokens.json
python3 diagramador/testes/test_diagramador.py        # tem que dar 0 falhas
python3 diagramador/ferramentas/empacotar_skill.py    # leva a mudança para a skill
```

O e-book de exemplo (`exemplo/porto_seguro.md`) precisa sair com QA sem
nenhuma falha crítica.

A skill carrega uma cópia do runtime porque precisa rodar sem o repositório por
perto. A direção é só uma — repositório → skill — e o empacotador é quem a
percorre. Nunca edite `.claude/skills/ebook-teaformation/scripts/` à mão;
`test_skill_esta_em_dia` falha quando o empacotador é esquecido.

### 7. Levar estas regras para outra conversa

Duas formas, conforme o caso:

- **`.claude/skills/ebook-teaformation/`** — a skill. Vale em qualquer sessão
  neste repositório, e o `.skill` empacotado instala no perfil para valer também
  no Cowork e no claude.ai. É o caminho para *usar* o sistema.
- **`PROMPT_MESTRE.md`** — o pedido inteiro, corrigido pela realidade da
  construção. É o caminho para *reconstruir* o sistema em outro lugar.

Se mexer nas regras aqui, atualize os dois — eles são cópia, não referência.

### 8. Onde as coisas estão

| Precisa mexer em | Vá em |
|---|---|
| cor, medida, tipografia | `design/tokens.json` (e rode o gerador) |
| como um bloco é desenhado | `diagramador/tema/blocos.css` |
| como o markdown é lido | `diagramador/app/marcacao.py` |
| o que o QA verifica | `diagramador/app/qa.py` |
| as opções da linha de comando | `diagramador/app/cli.py` |
| como a skill é montada | `diagramador/ferramentas/empacotar_skill.py` |
| a convenção de escrita | `FORMATO.md` |
