---
name: ebook-teaformation
description: Diagrama e-books, cartilhas e materiais da TEA Formation (Universo TEAnimal, Vale da Harmonia) — recebe um markdown e devolve o PDF pronto para vender, com relatório de QA. Traz também o design system medido, o formato de escrita e as regras de marca. Use sempre que aparecer TEA Formation, TEAnimal, Vale da Harmonia, Mamãe Urso, Porto Seguro, diagramador, ficha de atividade, e-book terapêutico ou material para criança autista — e principalmente quando pedirem para diagramar, gerar o PDF, montar o e-book, rodar o diagramador, ou quando colarem/anexarem um markdown de material da marca. Vale também para escrever o conteúdo, escolher cor, fonte, capa, layout, ou conferir supervisão técnica e CRP.
---

# E-books da TEA Formation

Esta skill faz duas coisas, e a primeira é a que costuma ser pedida:

1. **Diagrama** — recebe um markdown e roda o diagramador, que devolve o PDF no
   padrão visual da marca, um relatório de QA e a imagem de cada página.
2. **Ensina o padrão** — o design system medido, o formato de escrita e as
   regras de marca, para escrever material novo ou revisar o que já existe.

**A ideia central: isto é um renderizador determinístico, não um gerador de
design.** O design foi decidido uma vez, medido nas cartilhas aprovadas e
congelado em tokens. Cor, fonte, espaçamento, margem e hierarquia já estão
resolvidos no CSS — você não escolhe nenhum deles. Material com cara de IA
acontece quando o modelo decide layout na hora; aqui ele nunca decide.

Sua única decisão é **classificar cada trecho em um tipo de bloco do catálogo**.
Trecho que não encaixa vira o bloco genérico e entra no relatório, em vez de
virar layout inventado.

## Diagramar um material

O script vive em `scripts/diagramar.py` e roda com Python 3.11+. Ele não usa
rede nem chave de API: quem classifica é você, aqui na sessão.

### 1. Salve o markdown em um arquivo

Se o material veio colado na conversa, grave como `.md` antes de rodar. Se veio
como arquivo, use o caminho dele.

### 2. Veja o que precisa de rótulo

```bash
python3 scripts/diagramar.py material.md --trechos
```

Sai um JSON com os trechos que o markdown não tipou sozinho — os que não têm
diretiva `:::`. Lista vazia significa que não há nada a decidir; pule para o
passo 4.

### 3. Decida um rótulo para cada trecho

Leia cada `resumo` e escolha **um** tipo, usando as regras da próxima seção.
Grave assim, um objeto por trecho:

```json
{"classificacoes": [
  {"indice": 1, "tipo": "secao_conceitual", "confianca": "alta",
   "motivo": "explica o que é uma crise: conceito e mecanismo"},
  {"indice": 4, "tipo": "dicas_praticas", "confianca": "alta",
   "motivo": "cinco títulos imperativos, um parágrafo cada"}
]}
```

`confianca: "alta"` aplica o rótulo. `"baixa"` mantém o trecho genérico e
registra o caso no relatório — e é a resposta certa quando você hesita.
Responda para **todos** os trechos, inclusive os que continuam
`secao_conceitual`: confirmar também é decidir, e o que ficar sem resposta
aparece no relatório como pendência.

### 4. Gere

```bash
python3 scripts/diagramar.py material.md --classificacao classificacao.json
```

Um material de 20 páginas leva cerca de 4 segundos. Saem, ao lado do markdown:

- `material.pdf` — o material diagramado;
- `material-qa.md` — o relatório completo;
- `material-paginas/p01.png…` — cada página como imagem.

Código de saída 0 quer dizer que passou; **2 quer dizer que o PDF saiu mas o QA
achou falha crítica** — nesse caso resolva antes de entregar.

### 5. Confira e entregue

Leia o resumo do QA. Se houver falha ou aviso, olhe a imagem da página citada
antes de decidir — o relatório diz *o quê* e *onde*, a imagem diz se incomoda.
Entregue o PDF e diga em uma linha o que o QA achou.

O material não está pronto para publicar só porque o QA ficou verde: o
diagramador cuida da forma, a revisão clínica é da equipe técnica. Diga isso ao
entregar.

### Trocar o tipo de um bloco depois

Quando o fundador olhar o PDF e disser "essa página devia ser uma caixa de
atenção", não edite o markdown nem o CSS — troque o tipo do bloco pelo número
que o relatório mostra:

```bash
echo '{"7": "caixa_atencao"}' > correcoes.json
python3 scripts/diagramar.py material.md --classificacao classificacao.json --correcoes correcoes.json
```

Outras opções: `--saida` (caminho do PDF), `--sem-miniaturas`, `--json`
(relatório em JSON), `--blocos` (lista dos blocos com a página de cada um).

## Como escolher o rótulo

Sete tipos entram nessa decisão. Todos os outros vêm de diretiva `:::` explícita
no markdown ou são automáticos, e não se toca neles.

| Tipo | A forma característica |
|---|---|
| `secao_conceitual` | explicação, conceito, mecanismo — **é o padrão** |
| `carta_abertura` | texto em segunda pessoa dirigido a quem lê, com despedida ou assinatura; costuma abrir o material |
| `caixa_atencao` | aviso curto, ressalva clínica, ponto crítico; poucas linhas |
| `dicas_praticas` | vários títulos curtos imperativos, cada um com um parágrafo |
| `roda_conversa` | lista de perguntas para fazer à criança |
| `voz_personagem` | fala de um personagem do Vale da Harmonia, em tom afetivo |
| `secao_encerramento` | fecho do material: o que observar daqui para frente, quando buscar ajuda |

Na dúvida responda `secao_conceitual` com confiança baixa. Não é desistir: é o
comportamento correto do sistema, porque um trecho genérico bem diagramado é
melhor que um bloco errado, e o caso fica registrado para revisão humana.

Você escolhe só o rótulo. Não reescreva o texto, não reordene os trechos, não
crie tipo novo, não mexa no CSS.

## As quatro regras que não se quebram

Vêm do fundador e valem para qualquer material. Errar nelas custa mais caro que
qualquer detalhe visual — e o QA confere todas.

### 1. Supervisão técnica é dado fixo

| Campo | Valor |
|---|---|
| Nome | **Ingrid Ceron** |
| CRP | **12/15726** |
| Especialidade | **Especialista em autismo (TEA) e em Terapia ABA** |

Está em `scripts/design/tokens.json` e o script preenche sozinho. Nunca invente
outro nome, outro CRP ou outra especialidade — nem em exemplo, nem em rascunho,
nem em teste. Se o material for de outra profissional, o usuário diz
explicitamente; sem isso, é a Ingrid.

### 2. Personagem só quando pedirem

Material **não leva personagem do TEAnimal** por padrão. Nem na capa, nem no
miolo, nem como ilustração de reserva. Os personagens (Mamãe Urso, Leo, Jojo,
Cora, Pipo, Marcos, Professora Canguru, Sr. Miau) entram só quando o material
pede — `personagem: mamae_urso` no cabeçalho, ou `:::voz mamae_urso` num bloco.

Sem pedido, a capa é tipográfica com a peça do quebra-cabeça da marca.

### 3. Cor institucional é o padrão

A paleta padrão é a da **TEA Formation**: azul `#0193C8`, branco, bege `#F9F4E5`,
navy `#1F2D3D` no texto. As cores do **Universo TEAnimal** (coral, verde,
amarelo, roxo, tons dos habitantes) são do braço infantil e só entram quando o
material pede `tema: teanimal`.

A lógica do tema institucional, que ajuda a decidir rápido: **azul é pedagógico,
bege é apoio, navy é crítico.**

### 4. Textos obrigatórios, literais

A fundamentação científica aparece **exatamente duas vezes** — capa e página
final — com este texto, sem variação:

> Conteúdo fundamentado em Análise do Comportamento Aplicada (ABA) e Terapia
> Cognitivo-Comportamental (TCC), abordagens com evidência científica. Nenhuma
> técnica apresentada aqui é inventada.

E o disclaimer, na página final:

> Este material educativo não substitui avaliação, diagnóstico ou acompanhamento
> terapêutico individualizado. Supervisão técnica: {nome}, CRP {crp}.

## Linguagem da marca

Use: **criança autista**, **no espectro**, **crise (meltdown)**.

Nunca use: *portador*, *sofre de*, *anjo azul*, *superpoderes*, *doente*,
*criança normal*. Se um desses aparecer no texto que te deram, **sinalize e não
corrija sozinho** — a palavra é decisão de quem escreveu, e trocar por conta
própria muda o sentido clínico sem a pessoa saber. O QA também pega, e também
só avisa.

O tom: um especialista em desenvolvimento infantil que também acolhe. Nem
panfleto clínico, nem fofura genérica. Evite clichê de IA — "descubra o mundo
de", "jornada mágica", "conexão profunda" são proibidos pelo manual da marca.

## Quando algo dá errado

**`faltam dependências`** — o script diz o que instalar. Ele precisa de
`weasyprint`, `pymupdf`, `jinja2`, `fonttools`, `numpy` e das bibliotecas de
sistema do WeasyPrint (Pango, Cairo, fontconfig). Em ambiente sem Python nem
terminal, a skill ainda serve para escrever e revisar — só não gera o PDF.

**Ficha de atividade não cabe em uma página** — o sistema já tentou reduzir a
escala até 88%. Não quebre a ficha nem invente layout: peça para encurtar o
texto ou dividir em duas atividades. É o que o relatório manda fazer.

**Cor fora da paleta do tema** — alguma cor entrou que não é token. Não ajuste
o CSS para acomodar: descubra de onde veio (quase sempre uma imagem nova ou o
tema errado no cabeçalho).

**Personagem sem pedido** — falha crítica por definição. Tire o personagem ou
confirme com o fundador que ele foi pedido.

## Para ir mais fundo

**Escrever o conteúdo** → `references/formato-markdown.md`: cabeçalho, as nove
marcações `:::` e o que o sistema preenche sozinho. Comece de
`assets/modelo-ebook.md`. Um material completo de verdade, com quase todos os
blocos, está em `assets/exemplo-porto-seguro.md`.

**Mexer no sistema** → `references/diagramador.md`: as peças do código, o que o
QA verifica e as armadilhas que já custaram caro.

**Escolher cor, medida, tipografia — ou criar peça fora do e-book** →
`references/design-system.md`: paleta com procedência, escala tipográfica, grid
e os dois temas. Se você estiver prestes a escolher um valor "no olho", pare e
pegue o token de lá: existe valor medido para quase tudo, e usar outro é o que
faz o material parecer de outra marca.
