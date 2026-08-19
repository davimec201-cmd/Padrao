---
name: ebook-teaformation
description: Design system e regras de marca da TEA Formation (Universo TEAnimal, Vale da Harmonia) para produzir e-books, cartilhas, materiais de apoio e qualquer peça da marca. Use sempre que aparecer TEA Formation, TEAnimal, Vale da Harmonia, Mamãe Urso, Porto Seguro, diagramador, ficha de atividade, e-book terapêutico, material para crianças autistas, ou quando pedirem cor, fonte, capa, layout, markdown de e-book, supervisão técnica ou CRP de material da marca — mesmo que não citem "TEA Formation" pelo nome, se o contexto for material para criança autista dessa marca. Traz a paleta medida, a tipografia, o catálogo de blocos, o formato do markdown e as regras que não podem ser quebradas.
---

# Materiais da TEA Formation

Este é o design system da TEA Formation / Universo TEAnimal, descoberto medindo em
pixel as cartilhas aprovadas e congelado em tokens. Ele existe para que material
novo saia igual ao que já foi aprovado — sem reinventar cor, medida ou hierarquia
a cada peça.

**A ideia central: isto é um renderizador determinístico, não um gerador de
design.** O design foi decidido uma vez. Em produção o modelo só classifica um
trecho em um tipo de bloco do catálogo; ele não escolhe cor, fonte, espaçamento,
margem nem hierarquia. Material com cara de IA acontece quando o modelo decide
layout na hora — aqui ele nunca decide. Trecho que não encaixa em nenhum bloco
vira o bloco genérico e **entra no relatório**, em vez de virar layout inventado.

## As quatro regras que não se quebram

Estas vêm do fundador e valem para qualquer material. Errar nelas custa mais caro
que qualquer detalhe visual.

### 1. Supervisão técnica é dado fixo

| Campo | Valor |
|---|---|
| Nome | **Ingrid Ceron** |
| CRP | **12/15726** |
| Especialidade | **Especialista em autismo (TEA) e em Terapia ABA** |

Nunca invente outro nome, outro CRP ou outra especialidade — nem em exemplo, nem
em rascunho, nem em teste. Se o material for de outra profissional, o usuário diz
explicitamente; sem isso, é a Ingrid.

### 2. Personagem só quando pedirem

Material **não leva personagem do TEAnimal** por padrão. Nem na capa, nem no
miolo, nem como ilustração de reserva. Os personagens (Mamãe Urso, Leo, Jojo,
Cora, Pipo, Marcos, Professora Canguru, Sr. Miau) entram só quando o material
pede — `personagem: mamae_urso` no cabeçalho, ou `:::voz mamae_urso` num bloco.

Sem pedido, a capa é tipográfica com a peça do quebra-cabeça da marca.

### 3. Cor institucional é o padrão

A paleta padrão é a da **TEA Formation**: azul `#0193C8`, branco, bege `#F9F4E5`,
navy `#1F2D3D` no texto. As cores do **Universo TEAnimal** (coral, verde, amarelo,
roxo, tons dos habitantes) são do braço infantil e só entram quando o material
pede `tema: teanimal`.

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
> terapêutico individualizado. Supervisão técnica: [nome], CRP [número].

## Linguagem da marca

Use: **criança autista**, **no espectro**, **crise (meltdown)**.

Nunca use: *portador*, *sofre de*, *anjo azul*, *superpoderes*, *doente*,
*criança normal*. Se um desses aparecer no texto que te deram, **sinalize e não
corrija sozinho** — a palavra é decisão de quem escreveu, e trocar por conta
própria muda o sentido clínico sem a pessoa saber.

O tom: um especialista em desenvolvimento infantil que também acolhe. Nem
panfleto clínico, nem fofura genérica. Evite clichê de IA — "descubra o mundo
de", "jornada mágica", "conexão profunda" são proibidos pelo manual da marca.

## O que fazer, conforme o pedido

**Escrever o conteúdo de um e-book ou material** → leia
`references/formato-markdown.md`. É a convenção de escrita: cabeçalho, nove
marcações `:::`, e o que o sistema preenche sozinho. Comece de
`assets/modelo-ebook.md`, que já tem a estrutura montada.

**Diagramar, gerar o PDF, mexer no app** → leia `references/diagramador.md`. Diz
como rodar, o que o QA verifica e onde fica cada peça do código.

**Escolher cor, tamanho, medida — ou criar uma peça nova fora do e-book** → leia
`references/design-system.md`. Tem a paleta com procedência, a escala
tipográfica, o grid e os dois temas. Se você estiver prestes a escolher um valor
de cor ou de espaçamento "no olho", pare e pegue o token de lá: existe um valor
medido para quase tudo, e usar outro é o que faz o material parecer de outra
marca.

**Revisar um material pronto** → confira nesta ordem, que é a mesma do QA
automático: textos obrigatórios literais, supervisão técnica correta, nenhum
personagem sem pedido, nenhuma cor fora do tema ativo, contraste de corpo
≥ 4.5:1, e nenhum termo de linguagem proibida.

## Se você tiver o repositório em mãos

Quando o projeto `Padrao` estiver disponível, o sistema completo já existe em
`diagramador/` e a fonte de verdade dos valores é `design/tokens.json` — leia de
lá em vez de copiar números desta skill, porque o arquivo pode ter evoluído.
Rode `python3 diagramador/testes/test_diagramador.py` antes de dar qualquer
coisa por pronta.

Sem o repositório, esta skill se sustenta sozinha: os valores nas referências
são os mesmos, congelados.

## Onde os números foram medidos

Vale saber para não desconfiar deles: as quatro cartilhas aprovadas foram
rasterizadas a 100 dpi (2428×3445 px, escala 11.562 px/mm sobre A4) e amostradas
em pixel. Daí saíram a largura do bloco de conteúdo (151.4mm, idêntica nas
quatro), o raio dos cards (8.2mm), o avanço de linha do corpo (17.2–18.1pt) e até
os tons de pelo dos personagens. Onde a skill diz "medido", há um número atrás;
onde diz "derivado", há uma fórmula.

Uma ressalva que evita erro comum: cartilha é narrativa ilustrada de 4 páginas,
com balão de 30pt. E-book é leitura longa de 30–50 páginas. **Não reproduza
quadrinho em tipografia de leitura** — o corpo de 11.5pt/17.5pt saiu do card
informativo da cartilha, que é o único lugar dela com texto de leitura de
verdade, não dos balões.
