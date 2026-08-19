# Prompt mestre — Diagramador de e-books TEA Formation

Este arquivo é o pedido inteiro, do jeito que ele ficou depois de construído e
corrigido. Serve para dois usos:

- **reconstruir o sistema** em outro lugar (Cowork, outra sessão, outro
  repositório) — cole daqui para baixo como primeira mensagem;
- **encomendar um material novo** dentro do sistema que já existe — nesse caso
  use a skill `ebook-teaformation`, que é mais curta e já vem carregada.

O que está aqui embaixo não é o pedido original: é o pedido **corrigido pela
realidade da construção**. Cada decisão que custou caro para descobrir já vem
resolvida, com o motivo junto.

---

## O que eu quero

Sou fundador da TEA Formation, startup brasileira de materiais terapêuticos e
educacionais para crianças autistas (Universo TEAnimal / Vale da Harmonia). Vendo
e-books direto ao consumidor e distribuo para clínicas.

Quero um **aplicativo web** em que eu envio um arquivo markdown com o conteúdo de
um e-book e recebo de volta um PDF diagramado no padrão visual da TEA Formation,
pronto para vender. Uso pelo navegador — **tablet e computador**.

**Automatize o máximo possível.** Meu envolvimento deve ser: subir o markdown,
esperar, olhar o resultado, baixar. Uma revisão rápida no final e pronto. Não me
faça editar JSON, ajustar layout ou responder perguntas no meio do processo.

---

## Princípio arquitetural inegociável

**O sistema é um renderizador determinístico, não um gerador de design.**

- O design system é descoberto uma vez, congelado em tokens versionados, e nunca
  improvisado em runtime.
- Em produção o LLM tem **uma** função: classificar cada trecho do markdown em um
  tipo de bloco do catálogo. Ele não escolhe cor, fonte, espaçamento, margem ou
  hierarquia. Nunca.
- Se um trecho não encaixa em nenhum bloco, o sistema usa o bloco genérico mais
  próximo e **registra o caso no relatório**, em vez de inventar layout.
- Todo layout vem de CSS escrito à mão, versionado, revisável.

Material com cara de IA acontece quando o modelo decide layout na hora. Aqui ele
nunca decide.

---

## As quatro regras de marca

Estas valem para todo material gerado e têm verificação automática.

### 1. Supervisão técnica é dado fixo

Ingrid Ceron · CRP 12/15726 · Especialista em autismo (TEA) e em Terapia ABA.

Fica em `tokens.json`, chega preenchida na interface, e o QA avisa se o material
sair com outro nome ou CRP.

### 2. Personagem só a pedido

Material não leva personagem do TEAnimal por padrão — nem na capa, nem no miolo,
nem como ilustração de reserva. Entra com `personagem:` no cabeçalho ou
`:::voz <nome>`. Sem pedido, a capa é tipográfica com a peça da marca. O QA
**falha** se um personagem aparecer sem ter sido pedido.

### 3. Paleta institucional por padrão

Azul `#0193C8`, branco, bege `#F9F4E5`, navy `#1F2D3D`. As cores do Universo
TEAnimal (coral, verde, amarelo, roxo) só entram com `tema: teanimal`. Trocar de
tema re-aponta papéis de cor; estrutura, grid e tipografia não mudam.

No tema institucional: **azul é pedagógico, bege é apoio, navy é crítico.**

### 4. Textos obrigatórios, literais

Logo discreto no rodapé de toda página, mesma posição, exceto na capa.

Fundamentação científica exatamente duas vezes — capa e página final:

> Conteúdo fundamentado em Análise do Comportamento Aplicada (ABA) e Terapia
> Cognitivo-Comportamental (TCC), abordagens com evidência científica. Nenhuma
> técnica apresentada aqui é inventada.

Disclaimer na página final:

> Este material educativo não substitui avaliação, diagnóstico ou acompanhamento
> terapêutico individualizado. Supervisão técnica: [nome], CRP [número].

Linguagem: "criança autista", "no espectro", "crise (meltdown)". Nunca
"portador", "sofre de", "anjo azul", "superpoderes". Termo proibido no markdown
de entrada é **sinalizado no relatório, não corrigido sozinho**.

---

## Descoberta do design system

Se estiver reconstruindo do zero, esta é a primeira fase e é o coração do
projeto. Coloque em `referencias/`: as cartilhas aprovadas (a identidade visual),
os materiais de apoio (como o conteúdo pedagógico se organiza), o manual de
identidade (fonte canônica), e um e-book existente **apenas como referência de
estrutura, não de visual**.

Em uma frase: **esqueleto do e-book existente, pele das cartilhas.**

As cartilhas vêm do Photoshop com texto rasterizado — extração de texto devolve
lixo. Renderize cada página como imagem a 100+ dpi e **analise visualmente**:
amostre cores direto dos pixels, meça proporções e respiro.

Entregue `design/tokens.json` com valores medidos, não estimados, e
`design/tokens.md` explicando cada token em uma linha e de qual página de qual
arquivo ele veio. Cor nomeada por função (`fundo_palco`, `destaque_pedagogico`,
`linha_divisoria`), respeitando a regra 60-30-10: 60% fundos dessaturados, 30%
tons de apoio e texto, 10% cor plena reservada ao objetivo pedagógico.

**Ressalva de tradução de medium:** cartilha é narrativa ilustrada de 4 páginas
com balão de 30pt; e-book é leitura longa de 30–50 páginas. Não reproduza
quadrinho em CSS. Tire o corpo de texto do lugar da cartilha onde há leitura de
verdade (o card informativo), não dos balões — e documente essa decisão.

---

## Catálogo de blocos

Cada bloco é um componente CSS isolado, com campos declarados:

capa · carta de abertura · sumário (gerado, com página real) · seção conceitual ·
tabela comparativa (duas colunas, padrão "Birra × Crise") · caixa de atenção ·
abertura de bloco (página divisória) · **ficha de atividade** · formulário
imprimível · dicas práticas · roda de conversa · voz do personagem ·
encerramento · página final.

A **ficha de atividade** é o mais importante e ocupa uma página inteira: número +
nome, par lado a lado "Objetivo terapêutico" / "Princípio ABA-TCC", parágrafo de
materiais, passo a passo numerado, par "Mais fácil" / "Mais desafiador", rodapé
"O que observar".

---

## Formato do markdown

Markdown padrão sempre que possível; diretivas explícitas só onde ele não dá
conta. Nove marcações: `:::ficha`, `:::bloco`, `:::atencao`, `:::carta`,
`:::dicas`, `:::conversa`, `:::voz`, `:::formulario`, `:::encerramento`.

Duas regras: **nada de estilo no markdown** (sem cor, tamanho ou HTML inline — só
estrutura e conteúdo), e **escrevível por humano sem consultar manual**. Se ficar
complicado, simplifique.

Capa, sumário, rodapé, textos obrigatórios e numeração o sistema faz sozinho.
Comentário `<!-- -->` não vai para o PDF.

---

## O aplicativo

Python + FastAPI. Parse próprio do markdown com diretivas. Renderização em HTML +
CSS Paged Media via **WeasyPrint**. Fontes embutidas via `@font-face` com os
arquivos locais — nunca CDN, nunca fonte substituta. Front-end em HTML/CSS/JS
simples, sem framework.

Interface mobile-first com alvos de toque grandes, e layout de duas colunas a
partir de 1024px para o computador. Fluxo: upload do `.md` (ou colar o texto) →
campos de supervisão já preenchidos → botão Gerar → barra de progresso com a
etapa atual → miniaturas das páginas → relatório de QA → download.

**Sem checkpoint intermediário.** A revisão acontece uma vez, no final.

**Correção de exceção:** na miniatura de cada página, um seletor para trocar o
tipo de bloco e um botão de regerar. Sem editar JSON.

Senha simples (o app não fica aberto na internet) e chave de API em variável de
ambiente. Deploy no Render com `Dockerfile` (WeasyPrint precisa de libs de
sistema) e `render.yaml`, com passo a passo executável pelo tablet.

---

## QA automático

É o que substitui a revisão detalhada, então precisa ser confiável a ponto de o
PDF ser baixado só olhando o verde. Verifique:

margem · ficha inteira em uma página · órfãs e viúvas · fontes efetivamente
embutidas · contraste ≥ 4.5:1 em todo texto de corpo · **nenhuma cor fora dos
tokens do tema ativo** · logo em toda página na mesma posição · fundamentação
científica literal exatamente duas vezes · disclaimer · nenhum placeholder ·
sumário com números batendo · todo o texto do markdown presente no PDF ·
linguagem proibida · **nenhum personagem sem pedido** · supervisão técnica igual
à registrada.

Relatório legível em tela pequena: verde quando passou; quando falhar, **qual
página** e **o quê**. Falha crítica avisa antes do download.

---

## Armadilhas já descobertas (não repita)

Estas custaram tempo real e todas passariam despercebidas sem o QA:

1. **WeasyPrint ignora `@font-face` em silêncio** sem uma `FontConfiguration`
   explícita passada para `CSS(...)` **e** para `render()`. O material sai
   inteiro, na fonte errada. Ponha uma verificação de fonte embutida no build.
2. **`text-stroke` e `text-shadow` não existem no WeasyPrint.** Título com
   contorno se faz em SVG, com duas passadas de `<text>`: uma de traço, outra de
   preenchimento (`paint-order` também não é honrado).
3. **`gap` de flex dentro de caixa de margem `@page`** soma vão sobrando à
   direita. Use margem nos filhos.
4. **Número de página junto da marca faz o logo dançar** entre páginas de 1 e 2
   dígitos. Separe: número de um lado, marca do outro.
5. **`body { background }` cobre a cor da `@page`.** Fundo é da `@page`.
6. **Antialiasing não é cor nova:** o guardião da paleta deve aceitar mistura de
   dois tokens e reprovar só um terceiro tom.
7. **Contraste × identidade:** as cartilhas usam branco sobre coral (2.70:1). Não
   escureça a cor da marca — troque o texto para navy (5.19:1). Mantém a paleta
   exata e passa em AA.
8. **Modelos Claude da geração 5 rejeitam `temperature`** com 400. Para
   classificação use `output_config: {effort: "low"}` e saída em JSON Schema.

---

## Como trabalhar comigo

Pare para eu aprovar **uma vez só**: quando os tokens estiverem extraídos e você
tiver renderizado uma ficha de atividade de exemplo. Depois disso, construa o
resto inteiro sem me interromper.

Antes de começar, me diga em lista curta: o que está ambíguo ou faltando nas
referências, quais arquivos adicionais você quer, e se algum ponto do pedido está
contraditório ou inviável.

## Fora de escopo

Geração de ilustração ou arte (o sistema consome de `assets/ilustracoes/`, não
cria). Redação, correção ou reescrita de conteúdo — o texto entra como está.
Revisão clínica: todo material continua passando por validação profissional, e o
app deve exibir esse lembrete na tela de download. EPUB, versão web, slides.
