# FORMATO.md — como escrever o markdown de um e-book

Tudo aqui é markdown comum. Só existem **nove** marcações especiais, e cada uma
tem a cara do que ela faz. Escreva no editor de texto do tablet e mande no app.

Duas regras que valem para o arquivo inteiro:

1. **Nada de estilo.** Não escreva cor, tamanho, alinhamento nem HTML. Se você
   quiser dar destaque, use `**negrito**` — o resto o sistema resolve.
2. **Se está difícil, provavelmente é mais simples do que você pensa.** Título é
   `##`, lista é `-`, ficha é `:::ficha`. Não tem mais nada para decorar.

---

## 1. O cabeçalho do arquivo

Comece com isto (as linhas entre `---`):

```
---
titulo: Porto Seguro
subtitulo: 12 atividades de regulação emocional para prevenir e atravessar crises
personagem: mamae_urso
especialidade: Psicóloga especialista em Análise do Comportamento Aplicada (ABA)
---
```

| Campo | Obrigatório | O que é |
|---|---|---|
| `titulo` | sim | Título grande da capa |
| `subtitulo` | sim | Uma linha, curta. Aparece na tarja colorida |
| `personagem` | não | Quem ilustra a capa (lista abaixo). Sem isso, entra a peça do quebra-cabeça |
| `especialidade` | não | Vai embaixo do nome da psicóloga na capa |

**Nome da psicóloga e CRP você não escreve aqui** — o app pergunta e preenche
sozinho, na capa, na carta e na página final.

Personagens disponíveis: `mamae_urso`, `leo`, `jojo`, `cora`, `pipo`, `marcos`,
`professora_canguru`, `sr_miau`.

---

## 2. Texto normal

Escreva markdown:

```
## O que é uma crise (e o que ela não é)

No espectro autista, a crise (às vezes chamada de meltdown) é uma resposta
involuntária a uma **sobrecarga** — sensorial, emocional ou de comunicação.

### Por que isso importa tanto?

Porque a resposta do adulto muda completamente dependendo da leitura que ele faz.

- Primeiro item
- Segundo item
```

- `##` abre uma seção nova (vira o título da página).
- `###` é subtítulo dentro da seção.
- `-` faz lista; `1.` faz lista numerada.
- `**negrito**` e `*itálico*` funcionam.

## 3. Tabela de duas colunas

Duas colunas viram automaticamente a tabela comparativa da marca (o padrão
"Birra × Crise"):

```
| BIRRA | CRISE |
|---|---|
| Tem um objetivo | Não tem objetivo — é transbordamento |
| Cessa quando consegue o que quer | Segue seu curso mesmo se ceder |
```

Com três colunas ou mais, o sistema usa a tabela comum dentro da seção.

---

## 4. As nove marcações especiais

Toda marcação abre com `:::nome` e fecha com `:::` numa linha sozinha.

### `:::ficha` — a ficha de atividade

A mais importante. Uma ficha ocupa uma página inteira.

```
:::ficha 5
### O Abraço de Urso

objetivo: Oferecer regulação por pressão profunda, respeitando integralmente o
consentimento da criança.
principio: Regulação sensorial proprioceptiva + pareamento com segurança.
materiais: **Com a Mamãe Urso:** apenas vocês dois — e, se a criança preferir,
um cobertor pesadinho.

1. SEMPRE pergunte antes: "Quer um abraço de urso?"
2. Se ela aceitar, abrace com pressão firme e constante.
3. Conte mentalmente até 10-20 segundos.

facil: Substitua o abraço por pressão nas mãos ou nos ombros.
desafiador: Ensine a criança a PEDIR o abraço quando sentir o "amarelo".
observar: O corpo da criança relaxa durante a pressão? Ou ela se esquiva?
:::
```

- O número vem depois de `:::ficha`.
- O nome da atividade é o `###`.
- `objetivo`, `principio`, `materiais`, `facil`, `desafiador`, `observar`: uma
  linha `chave: valor` cada, e o valor pode continuar nas linhas seguintes.
- A lista numerada é o passo a passo. Não precisa escrever "Passo a passo".

### `:::bloco` — página divisória

```
:::bloco 1
### PREVENIR
Previsibilidade que protege. Quatro atividades para reduzir gatilhos antes que
eles virem tempestade.
:::
```

### `:::atencao` — ponto crítico

```
:::atencao
### Ponto de atenção
Na dúvida entre birra e crise, trate como crise. Acolher uma birra por engano
custa pouco; tratar uma crise como birra custa muito.
:::
```

O `###` é opcional — sem ele, o rótulo é "Ponto de atenção".

### `:::carta` — carta de abertura

O `--` numa linha sozinha separa o texto da assinatura:

```
:::carta
Se você abriu este material, é provável que já tenha vivido aquele momento.

Respire. Você não está sozinho.
--
Com carinho,
{psicologa}
{crp}
:::
```

`{psicologa}` e `{crp}` são preenchidos pelo app.

### `:::dicas` — dicas para o adulto

Cada `###` é uma dica:

```
:::dicas
### Como agir no dia a dia

### Narrem o toque
Antes de tocar, anuncie o que você vai fazer.

### Pergunte sempre
Transforme o consentimento em hábito — e aceite o "não" com um sorriso.
:::
```

O primeiro `###` (antes de qualquer dica) vira o título do bloco.

### `:::conversa` — roda de conversa

```
:::conversa
### Para conversar depois da história
1. O que a Mamãe Urso queria dar para o Leo no início?
2. Por que o Leo não queria um abraço naquele momento?
:::
```

### `:::voz` — fala do personagem

```
:::voz mamae_urso
### Uma última palavra da Mamãe Urso
No Vale da Harmonia, ninguém precisa ser sol o tempo todo.
:::
```

### `:::formulario` — página para preencher à mão

Cada item da lista é um campo. Use `___` onde entra a linha para escrever e
`( )` onde entra a caixinha para marcar:

```
:::formulario
### Modelo do Diário do Detetive
instrucao: Fotocopie esta página. Preencha depois que tudo passar.
repeticoes: 2

- Data: ___ Horário: ___ Local: ___
- ANTES: ( ) mudança de rotina ( ) barulho ( ) transição ( ) outro: ___
- Observações: ___
:::
```

`repeticoes: 2` imprime o formulário duas vezes na mesma página.

### `:::encerramento` — fecho do material

```
:::encerramento
### O que observar — e quando buscar ajuda
Estas atividades fortalecem a família, mas há sinais de que é hora de envolver o
acompanhamento profissional.

- Crises muito frequentes, sem melhora após semanas de rotina estruturada.
- Comportamentos que machucam a própria criança ou outras pessoas.
:::
```

---

## 5. O que o sistema faz sozinho

Você **não** escreve nada disso:

| O quê | Quando |
|---|---|
| Capa | Do cabeçalho do arquivo |
| Sumário com número de página real | Depois da carta, se o material tiver seções |
| Logo no rodapé de toda página | Sempre, mesma posição |
| Fundamentação científica | Na capa e na página final, literal, exatamente duas vezes |
| Disclaimer legal com nome e CRP | Na página final |
| Numeração de página | Sempre |

## 6. Linguagem

O sistema **avisa** (não corrige) se encontrar: "portador", "sofre de",
"anjo azul", "superpoderes", "doente", "criança normal". A marca usa
**criança autista**, **no espectro**, **crise (meltdown)**.

## 7. Se algo não encaixar

Trecho que não é nenhuma das nove marcações vira seção de texto comum e **aparece
no relatório** com a linha do arquivo. O sistema não inventa layout: ele te conta
o que fez. Se você discordar, troque o tipo na miniatura da página e clique em
regerar.
