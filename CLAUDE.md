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

### 4. O sistema é um renderizador determinístico

- Design descoberto uma vez, medido nas cartilhas, congelado em tokens.
- Em produção o LLM só **classifica trecho em tipo de bloco**. Não escolhe cor,
  fonte, espaçamento, margem nem hierarquia.
- Layout é CSS escrito à mão em `diagramador/tema/`.
- Trecho que não encaixa vira o bloco genérico e **entra no relatório**. Nunca
  invente layout novo em runtime.

### 5. Antes de dar por pronto

```bash
python3 diagramador/ferramentas/gerar_tokens_css.py   # se mexeu em tokens.json
python3 diagramador/testes/test_diagramador.py        # tem que dar 0 falhas
```

O e-book de exemplo (`exemplo/porto_seguro.md`) precisa sair com QA sem
nenhuma falha crítica.

### 6. Onde as coisas estão

| Precisa mexer em | Vá em |
|---|---|
| cor, medida, tipografia | `design/tokens.json` (e rode o gerador) |
| como um bloco é desenhado | `diagramador/tema/blocos.css` |
| como o markdown é lido | `diagramador/app/marcacao.py` |
| o que o QA verifica | `diagramador/app/qa.py` |
| a interface | `diagramador/app/estatico/` |
| a convenção de escrita | `FORMATO.md` |
