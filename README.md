# Padrão

Ferramentas pessoais. Feitas sob medida, sem anúncio, sem conta, sem ninguém
decidindo por mim como as coisas devem funcionar.

## Projetos

### `um-de-cada-vez/`

Ferramenta de estudo para medicina. Um arquivo HTML só — abre no navegador,
funciona offline, guarda tudo no próprio aparelho. Sem build, sem servidor,
sem dependência.

#### O fluxo de estudo

| Passo | O que acontece |
|---|---|
| **Transcrever** | Tela dividida: o resumo importado de um lado, o seu texto do outro. A divisória arrasta. |
| **Explicar** | O texto some. Você explica em voz alta, sem olhar. |
| **Avaliar** | Travei / Quase / Mandei bem — define quando o assunto volta. |
| **Ler** | O resumo cru vira página formatada: hierarquia, setas, alertas, tabelas. |

Revisão espaçada: 1, 3, 7, 16, 35, 70 dias. "Travei" volta pro começo,
"Quase" mantém, "Mandei bem" avança.

#### Ciclos do semestre

O curso tem 3 ciclos por semestre, cada um com conteúdo próprio e uma prova
(PA1, PA2, PA3; PA4 é recuperação). A fila de hoje mostra **só o ciclo em
curso** — estudar conteúdo do ciclo passado achando que está revisando pra
próxima prova é o desperdício que isso evita. O material dos ciclos anteriores
não some: fica a um toque de distância, pra revisar antes do PA4.

Datas de `calendarioPadrao()`, lidas do calendário acadêmico Uniarp 2026
(seção Medicina), semestre 2026/2:

| Ciclo | Período | Prova |
|---|---|---|
| 1 | 20/07 – 28/08 | PA1, 24–28/08 |
| 2 | 31/08 – 09/10 | PA2, 05–09/10 |
| 3 | 12/10 – 27/11 | PA3, 23–27/11 *(estimado)* |
| — | — | PA4, 01–04/12 |

**A semana de prova do PA3 não consta no calendário** — só o prazo de
fechamento, 30/11. A data está marcada como estimada e é editável em Ajustes.

#### Formatador do modo leitura

Regras, não interpretação — não há IA dentro da página. Você escreve solto;
estas marcas viram elementos visuais:

```
## Título grande
Título de seção:        (linha terminando em dois-pontos)
- item                  (tópico)
1. item                 (lista numerada)
A -> B -> C             (fluxo com setas)
! atenção               (bloco de alerta)
> definição             (citação)
| a | b |               (tabela)
**negrito**  ==destaque==
```

Texto sem marca nenhuma vira parágrafo normal. Há também uma heurística: linha
curta sem pontuação final, seguida de tópico, é tratada como título.

#### Banco de questões

O app **não gera** questões — ele guarda e treina as suas. O importador aceita
o formato que um LLM costuma devolver: numeração (`1.` / `Questão 1`),
alternativas (`a)` `A)` `a.`), gabarito (`Resposta:` / `Gabarito:`) e
comentário (`Comentário:` / `Explicação:`). Confira a prévia antes de importar.
Questão errada volta amanhã; acertada vai espaçando.

#### Pomodoro

Ciclos de foco e pausa com o disco de identidade como cronômetro. Bip
sintetizado (sem arquivo de áudio). **A pausa nunca é obrigatória** — quando o
foco fecha, dá pra seguir direto: se você está embalado, parar custa mais caro
que continuar.

#### Decisões que não são estéticas

- Uma decisão por tela. Lista longa trava, então a tela inicial não tem lista.
- Zero contador de atraso. Atrasado é só o que vem primeiro na fila.
- Sessão com começo e fim visíveis; a meta diária não gera cobrança.
- Sair no meio não perde o que foi escrito.
- O cronômetro atualiza só o disco, nunca a tela inteira — senão o cursor
  saltaria do texto a cada segundo.

#### Identidade visual

Segue a identidade da TEA Formation (Drive > 01_Marca e Design > Identidade
Visual). As cores carregam o significado que o próprio manual atribui a elas:

| Cor | Significado no manual | Uso no app |
|---|---|---|
| `#0193C8` | confiança, cuidado, estabilidade, técnica | ação principal, foco, dados |
| `#F9F4E5` | leveza, acolhimento, acessibilidade | fundo |
| `#1F2D3D` | seriedade | texto; vira superfície no tema escuro |
| `#FF7345` | alegria | pausa do pomodoro, alerta no modo leitura |
| `#00AB6F` | desenvolvimento | acerto em questões |
| `#EDAF47` | curiosidade | realce (marca-texto) |
| `#FF8573` | coral | erro em questões |

Tipografia: **Poppins** nos títulos e na interface, **Manrope** na leitura —
ambas carregadas do Google Fonts, que é o único host de fontes permitido pela
política de conteúdo da página publicada. Omnes é a fonte do logo e não é
usada em interface.

O tema claro é o da marca. O tema escuro deriva do `#1F2D3D` — mesma marca,
para quem estuda de madrugada. O azul `#0193C8` foi validado como cor de dado
nos **dois** temas (faixa de luminosidade, piso de croma e contraste ≥ 3:1),
então os gráficos usam a cor da marca sem variação inventada.

Série única, tom único: o comprimento da barra já mostra a grandeza, e a
identidade vem do rótulo.

#### Onde os dados ficam

No navegador daquele aparelho (`localStorage`), com fallback em memória se o
navegador bloquear gravação. Limpar os dados do navegador apaga tudo. Backup e
restauração em JSON pelos Ajustes — é também assim que os resumos vão pra
outro aparelho.

**Rodar:** abrir `um-de-cada-vez/index.html` no navegador.

---

### `copeiro/`

Pomodoro de estudo, PWA instalável, feito para o tablet Android. Nenhuma
dependência: `index.html` (HTML + CSS + JS embutidos), `manifest.webmanifest`,
`service-worker.js`, os dois ícones PNG, os temas em `temas/`, o fundo da tela
de Foco em `assets/` e os protocolos do Performance em
`performance-protocols.js` — que fica de fora do `index.html` de propósito, pra
o conteúdo poder ser trocado sem mexer no motor do app. Depois de instalado,
funciona 100% offline.

#### Como se navega

Cinco posições fixas na barra, sem rolagem lateral:

```
Foco | Cartas | Progresso | Álbum | Mais
```

**Foco** e **Mais** nunca saem e nunca se movem. As três do meio são do Davi:
`Mais → Organizar abas` troca e reordena (arrastando pelo punho, ou com as
setas, que também respondem ao teclado), salva na hora e nunca aceita duas abas
iguais. As candidatas são Cartas, Progresso, Álbum, Copeiro Performance,
Estante, Histórico e Campeonato.

**Mais** é aba de verdade, não menu escondido: lista vertical com nome,
descrição de uma linha e a linha inteira clicável, agrupada em Performance,
Estudos, Campanha e Aplicativo. Nada fica inacessível por sair da barra — o que
sai, aparece ali. O Performance é a única exceção ao avesso: continua listado em
Mais mesmo quando está na barra, porque é dali que se ativa e se desativa. Na barra, "Campeonato" vira **Tabela**: cinco fatias iguais a
320 px não comportam a palavra inteira, e cortar rótulo está fora de questão.

Quem já usava o app vê uma vez, ancorada na aba Mais, a dica de onde as coisas
foram. Instalação nova nasce sem ela — não há nada pra migrar.

Um ponto discreto sobre um módulo avisa que ele tem algo pedindo ação: pacote
fechado no Álbum (com o número), fila de cartas do dia, capítulo esperando a
taça. Se o módulo está na barra o ponto fica nele; se está em Mais, sobe pra
Mais e se repete na linha de dentro. Ele some quando a **função** é visitada,
não quando Mais é aberto — e a assinatura é monotônica ou datada de propósito:
contagem de saldo voltaria ao valor antigo e o aviso sumiria pra sempre no caso
mais comum.

#### A tela de Foco

Uma partida vista do meio-campo. O cronômetro **é** o círculo central, e todo o
resto do painel é atmosfera: linha do meio, laterais do gramado, arcos de
escanteio, silhueta de arquibancada no rodapé e dois refletores apagados nos
cantos. Tudo em CSS, tudo com `aria-hidden`, e **nada se mexe** — a única
animação da tela são os refletores acendendo por 1 segundo quando o bloco fecha.

```
 faixa fina com as cores do time
          PARTIDA DE FOCO

   [Estudo livre]      [30 min]

        ───────────┼───────────
                 30:00
        ───────────┼───────────

          [Entrar em campo]
        [Aquecimento · 10 min]

        O próximo bloco já conta.
─────────────────────────────────────
 Pausas e intervalo          Ajustar
 Pausa 5 min · Intervalo 15 min ·
 após 3 blocos
```

O painel ocupa de 60% a 75% da primeira dobra: o vazio se resolve por
composição e escala, não por mais números. Assunto e duração ficam atrás de um
toque, cada um abrindo uma folha que fecha na escolha. O assunto nunca é
obrigatório e o padrão é "Estudo livre". A duração escolhida vira o novo padrão,
e **Aquecimento · 10 min** é uma entrada curta que não mexe nesse padrão.
**Sequência de dias seguidos saiu da tela principal** — ela vive no Progresso,
sem ameaça de perda.

Os botões dizem o que fazem e só existem quando fazem alguma coisa:

| Estado | Título | Principal | Secundário |
|---|---|---|---|
| Pronto | Partida de foco | Entrar em campo | — |
| Foco rodando | Em campo | Pausar | Encerrar bloco |
| Foco pausado | Foco pausado | Retomar | Encerrar bloco |
| Pausa rodando | Pausa / Intervalo | Voltar ao foco | Pausar descanso / intervalo |
| Pausa parada | Pausa parada / Intervalo parado | Retomar descanso / intervalo | Voltar ao foco |

Nada de "Zerar" e "Pular" apagados ocupando lugar. **Encerrar bloco** registra
o tempo realmente estudado: "Bloco encerrado: 0h18". Bloco de menos de um minuto
sai sem cerimônia e sem registro — é o toque acidental. Apagar registro segue no
Histórico. Bloco cumprido fecha em "Bloco concluído: 0h40", com três saídas:
iniciar a pausa, começar outro bloco ou ver o progresso.

O cabeçalho é compacto: `Copa 1 — Cardio · dia 8 de 40`. Sem campanha, ele diz
"Estudo livre" — ausência de Copa não é pendência nem erro.

##### Pausas e intervalo, na própria tela

Pausa curta, intervalo e blocos até o intervalo são ajuste de todo dia, então
moram embaixo do painel — não dentro de Configurações. O cartão nasce compacto,
com o resumo numa linha, e **Ajustar** abre os três controles ali mesmo. No
tablet deitado eles ficam lado a lado; em pé e no celular, empilhados.

| Ajuste | Faixa | Passo |
|---|---|---|
| Pausa curta | 1 a 30 min | 1 |
| Intervalo | 5 a 60 min | 5 |
| Blocos até o intervalo | 2 a 8 | 1 |

Salva no toque, sem botão "Salvar". O botão que não muda nada fica desligado, e
o resumo se atualiza na hora. Começar um bloco recolhe o cartão sem alterar
valor nenhum, e o resumo continua visível durante o foco. **Mudança não mexe em
pausa já iniciada**: o timer guarda a própria duração ao começar, então o ajuste
vale da próxima em diante — e o app diz isso numa confirmação discreta. Os
mesmos valores continuam espelhados em Configurações.

##### Progresso do dia: discreto por padrão

A tela de ação não cobra nada antes do estudo. Em `Mais → Configurações → Foco e
pausas`:

| Modo | O que a tela de Foco mostra |
|---|---|
| **Discreto** (padrão) | "O próximo bloco já conta." — e, depois do primeiro bloco, "Você já entrou em campo hoje." Nenhum número. |
| Oculto | Nada sobre o dia. |
| Completo | `Hoje: 3h40 · 5 blocos`. |

Em nenhum modo aparece comparação com recorde, meta ou com ontem.

#### Todo tempo acumulado é hora

Uma função só formata **todo** tempo que representa acúmulo, estatística ou
resultado — total do dia, da semana, vitalício, recordes, mapa anual, figurinhas
de registro, Estante, Campeonato e relatórios:

```javascript
formataTempoAcumulado(0)     // "0h"
formataTempoAcumulado(40)    // "0h40"
formataTempoAcumulado(60)    // "1h"
formataTempoAcumulado(185)   // "3h05"
formataTempoAcumulado(7580)  // "126h20"
```

A hora vem sempre na frente, inclusive abaixo de uma hora: "0h40" diz de cara
que é pouco tempo, enquanto "40min" obriga a converter de cabeça toda vez que
aparece ao lado de "3h40". Hora cheia sai sem os minutos. Nada de `220 min` nem
de `3,7h`. `descreveTempoAcumulado` devolve o mesmo tempo por extenso — "3 horas
e 40 minutos" — para o leitor de tela.

Ficam de fora, porque são **configuração ou contagem regressiva**, não acúmulo:
o cronômetro (`30:00`), a duração escolhida do bloco (`30 min`), a entrada curta
(`10 min`), a pausa (`5 min`), o intervalo (`15 min`) e os controles que somam ou
subtraem esses valores.

O armazenamento não mudou: continua em minutos inteiros, e só a camada de
apresentação foi trocada. `testesDeFormatacao()` roda na abertura e reclama no
console se zero, menos de uma hora, hora exata, minuto de um dígito ou total
grande sair do combinado.

#### Configurações

Tudo que é permanente saiu da tela de Foco e virou `Mais → Configurações`, em
cinco categorias que abrem uma por vez: **Foco e pausas** (duração padrão, o
espelho das pausas e o progresso na tela de Foco), **Avisos e concentração**,
**Aparência e identidade** (inclusive como o app te chama — as frases dos temas
usam `{nome}`), **Navegação** e **Dados** (backup, que saiu do Histórico).

#### O que ele faz

| Parte | Como funciona |
|---|---|
| **Timer** | Foco de 15, 25, 30 ou 50 min (padrão 30), mais a entrada curta de 10 min. Pausa curta e intervalo com duração editável **na própria tela de Foco**, e um contador de blocos que decide qual das duas entra — por padrão 5 min de pausa, 15 min de intervalo a cada 3 blocos. Toda pausa é livre. Iniciar, pausar, retomar, zerar, pular. |
| **Relógio real** | O tempo vem de `Date.now()`, nunca de contagem de ticks: com a tela apagada ou o app em segundo plano o bloco não atrasa, e um bloco que terminou com o app fechado é fechado na volta com o horário certo. |
| **Alarme** | Gerado sem arquivo de som: toque de gol no fim do foco, apito de árbitro começando o jogo no fim da pausa. Para avisar com o app fora da tela, o toque vai **gravado dentro de uma trilha silenciosa**, que o tocador de mídia leva até o fim mesmo com a página congelada. Três modos: desligado (música intacta), só nos 2 minutos finais (padrão) ou o bloco inteiro. O bloco aparece na barra de notificação, uma notificação avisa no fim, vibra quando o aparelho tem vibração, e o Wake Lock mantém a tela acesa durante o bloco, onde houver suporte. |
| **Bloquear o que distrai** | Antes de cada bloco o app pergunta se o Modo Foco do Android está ligado — bloquear aplicativo é coisa que só o sistema faz, e nenhuma página da web consegue. O lembrete tem três saídas: começar, sair pra ligar, ou nunca mais perguntar. |
| **Temporadas e Copas** | Uma Temporada é o álbum inteiro; cada **Copa** dentro dela é um capítulo. Nome, início e fim previsto são os únicos dados obrigatórios. Todo bloco entra automaticamente na Copa de hoje. Ao encerrar, as estatísticas congelam e a Copa vai para a Estante. |
| **Álbum da Copa** | Um caderno de figurinhas folheado página a página, duas por vez no tablet deitado: 18 figurinhas na Mini Copa, 30 na Copa padrão, todas visíveis com número, nome e critério desde o primeiro dia. Pacotes de 2, sem repetidas, liberados por estudo **e** por passagem do tempo. Ver abaixo. |
| **Assunto** | Campo com autocompletar pelos assuntos do ciclo atual e atalho para os 5 últimos. Fica visível durante o bloco. |
| **Histórico** | Hoje, últimos 7 dias em barras, lista completa com opção de corrigir o assunto ou apagar o registro, exportar e importar tudo em JSON. |
| **Cartas** | Flashcards com prazo: escada de 1, 2, 4, 8 e 16 dias, teto pela data da prova e reta final nos últimos 3 dias. Travei / Quase / Mandei bem, lacunas com `{{chaves}}`, revisão livre fora da fila e edição de qualquer campo, inclusive degrau e data. Ao encerrar o ciclo, o baralho é guardado junto com ele. |
| **Progresso** | Mapa de calor anual, estante de ciclos, comparação em tempo real com o ciclo anterior, contador vitalício de horas com marcos de 100/250/500/1000h, recordes pessoais e os números do baralho do ciclo. |
| **Tabela** | Campeonato com os amigos: classificação por horas copadas no ciclo (1 hora = 1 ponto, empate no desempate por dias ativos), campeão congelado quando o ciclo fecha, sala de troféus e campeão geral por número de títulos. Quem termina em primeiro ganha acabamento dourado no objeto da Estante. |
| **Performance** | Opcional e desligado por padrão. Ligado, o fim do bloco oferece um **intervalo inteligente** de 2, 5 ou 10 min — seis protocolos leves, filtrados por silêncio, espaço, suor e treino — sem nunca tirar a pausa normal do caminho. Registro de atividade sem calorias nem peso, e um painel cumulativo de estudo + movimento. Os protocolos são piloto, com aviso na tela até a revisão de um profissional de Educação Física. Ver abaixo. |

Sem meta de horas, sem barra de ciclo, sem moeda, loja, ponto ou nível. Nada
murcha nem cobra por dia parado: o app só registra e mostra o que foi feito.

#### Acessibilidade e tela

A barra cabe sem rolagem lateral a partir de 320 px (cinco fatias iguais, fonte
que encolhe antes de qualquer corte) e a primeira dobra da tela de Foco entrega
relógio, assunto, duração e o botão **Entrar em campo** sem rolar num 320×568.
Campo, estádio e refletores são decoração declarada (`aria-hidden`) e nenhum
dado depende deles. Cada figurinha anuncia número, nome, estado e condição; a
página aberta do caderno é anunciada ao virar; as setas dizem "Página anterior"
e "Próxima página"; os controles de pausa têm rótulo completo com o passo ("em
5 minutos"); e todo tempo compacto carrega a leitura por extenso ("3 horas e 40
minutos"). A aba ativa
tem `aria-current="page"`, cápsula preenchida, peso de fonte e uma barra em
`currentColor` — que sobrevive ao contraste forçado do sistema. Foco de teclado
visível em todo controle, com halo claro pra o anel nunca cair contra o próprio
fundo. Esc e o Voltar do Android fecham a camada de cima em vez de sair do app,
e a navegação empilha história: `Configurações → Mais → Foco`. `inert` tira o
fundo da ordem de tabulação enquanto uma folha está aberta. A cor primária
ganhou duas derivadas (`--primaria-texto`, `--primaria-forte`) porque a pura dá
4,32:1 sobre branco no tema tricolor: passa em texto grande e reprova em texto
normal.

#### O Álbum da Copa

O sistema de recompensa do Copeiro. Ele celebra **estudo feito**, não tempo
gasto navegando no app.

O laço é: começar o bloco → estudar com o app no bolso → o bloco fecha →
ganhar progresso ou pacote → voltar quando quiser → abrir → ver o próximo
marco.

##### É um caderno, não um painel

A temporada inteira é **um caderno de figurinhas**, folheado página a página.
No tablet deitado abre em duas páginas com a dobra no meio; no tablet em pé e
no celular, uma página de cada vez.

```
┌────────────────────────┬────────────────────────┐
│      PALCO DA COPA     │     NOSSA TORCIDA      │
│                        │                        │
│    [1]   [2]   [3]     │    [6]   [7]   [8]     │
│    [4]   [5]           │    [9]   [10]          │
│                        │                        │
│ página 4               │              página 5  │
└────────────────────────┴────────────────────────┘
                         ↑
                   dobra central
```

A ordem das folhas é a de um álbum de banca:

| # | Folha | Guarda figurinha? |
|---|---|---|
| 1 | Capa da Temporada | não |
| 2 | Índice das Copas | não |
| 3 | Divisória da Copa | não |
| 4–9 | as seis páginas do capítulo | sim |
| 10 | Encerramento da Copa (a taça) | sim |
| … | divisória e páginas da Copa seguinte | |
| fim | Retrospectiva da Temporada | não |

A **capa** traz nome da temporada, apelido do Davi, período, número da edição,
o selo do Copeiro e o preenchimento do álbum inteiro — mas ninguém é obrigado a
passar por ela: o caderno **abre na última página visitada**, guardada por
temporada. Capa e Índice estão a um toque na barra de navegação.

O **índice** lista as Copas com estado, período e a contagem no positivo —
`24 de 30`, nunca "6 perdidas" —, e um toque cai direto na divisória do
capítulo. A **divisória** abre o capítulo com o número, o período, a fase, a
barra de preenchimento e o próximo marco. O **encerramento** guarda a taça com
os números do capítulo, e a **retrospectiva** fecha a temporada somando todas as
Copas.

Vira-se a página por gesto horizontal, pelas setas (alvo de 56 px), pelas setas
do teclado ou pelo índice. A virada dura 220 ms e é uma folha leve, sem
simulação 3D; com `prefers-reduced-motion` ou animações desligadas, a folha só
troca. Só a folha aberta é montada — nada de trinta páginas no DOM.

O papel é marfim, nunca branco estourado, com textura de 2% a 4% de contraste;
a dobra é sombra interna, não faixa preta; as cores do time aparecem em
títulos, filetes, números e bordas, e o interior fica em torno de 80% de
superfície neutra. Nenhuma informação depende de enxergar papel, dobra ou
sombra.

##### O estado de cada espaço

- **Vazio** parece **impresso na folha**: contorno fino tracejado, número da
  figurinha, silhueta em baixa opacidade, nome curto e o critério em letra
  miúda. Sem cadeado, sem cinza de punição, sem "perdida" e sem vermelho.
- **No pacote** mantém o espaço impresso e diz que a figurinha já é do Davi,
  esperando abertura — a arte continua escondida até abrir.
- **Colada** tem arte cheia, borda de papel impresso, sombra curta e uma
  inclinação mínima em parte das figurinhas: colada na mão nunca sai reta, mas
  o caderno não pode virar bagunça.
- **Em jogo** e **Resultado final** são os registros, com o valor grande.

Um toque em qualquer espaço abre a figurinha ampliada sem sair da página, com o
número, a página onde mora, a data da conquista ou a condição por extenso. Nos
especiais e na taça o brilho holográfico acontece **na revelação**, e acaba
nela: nada fica piscando no álbum.

##### A coleção é fixa e visível desde o primeiro dia

Cada Copa é um capítulo com seis páginas, sempre as mesmas — dá pra comparar
uma Copa com a outra:

| Página | Copa padrão (28–56 dias) | Mini Copa (7–27 dias) |
|---|---|---|
| Palco da Copa | 5 colecionáveis | 3 |
| Nossa Torcida | 5 colecionáveis | 3 |
| Dia de Jogo | 5 colecionáveis | 2 |
| Símbolos da Campanha | 5 colecionáveis | 2 |
| Números da Copa | 6 registros | 4 |
| Momentos Decisivos | 3 especiais + a taça | idem |
| **total** | **30 figurinhas** | **18** |

A taça é contada nas seis páginas, mas **mora na folha de Encerramento** — é o
lugar dela na estrutura do caderno.

Todo espaço aparece desde o dia 1 com silhueta, nome e o critério de como se
preenche. Nada é surpresa; a única coisa que varia é a **ordem** em que as
colecionáveis chegam.

##### Os quatro tipos de figurinha

- **Colecionáveis** vêm em pacotes de 2 e nunca repetem. O baralho de cada
  Copa é embaralhado com uma semente derivada do id da Copa, e o próximo
  pacote sempre traz as duas primeiras que ainda não foram coladas — por isso
  não existe repetida e não existe número guardado pra dessincronizar.
- **Registros** se preenchem sozinhos com os dados reais da Copa (melhor dia,
  dias ativos, blocos, tempo total e, na Copa padrão, melhor rodada e assunto
  mais estudado). Depois do primeiro dia ativo ficam **Em jogo** e se
  atualizam a cada recorde; no fechamento recebem o selo **Resultado final** e
  congelam. Quem não informa assunto vê "Estudo livre" — o álbum funciona sem
  matéria, sem meta e sem ciclo acadêmico.
- **Especiais** têm condição pública e atingível sem precisar falhar de
  propósito: **Estreia** (primeiro dia ativo), **Ritmo de Jogo** (estudar em 3
  dias diferentes dentro de qualquer janela de 7) e **Até o Apito** (um dia
  ativo nos 20% finais).
- **A taça** é criada no fechamento com nome, período, tempo, dias ativos,
  blocos e o percentual do capítulo. Nunca vem em pacote. Um toque nela abre o
  cartão com os seis dados — é a peça que se mostra pra alguém.

##### Dia ativo

Um dia conta quando soma **10 minutos ou mais** de foco, no fuso do aparelho.
Os minutos podem vir de um bloco ou de vários. Bloco fechado com o app em
segundo plano conta igual, e encerrar antes do previsto não apaga o que foi
estudado de verdade.

##### O motor de entrega de pacotes

Esforço e tempo, os dois. Nenhuma maratona libera o álbum no começo da Copa.

```
D = dias da Copa (início e fim inclusive)
P = pacotes: 5 na Mini Copa, 10 na Copa padrão
A = dias ativos esperados = min(D, max(P, ceil(45% de D)))

pacote i sai quando as DUAS valem:
  dias ativos     >= ceil(i × A ÷ P)
  dias decorridos >= ceil(i × 80% de D ÷ P)
```

Cerca de 45% dos dias precisam ser ativos, o último pacote sai por volta de
80% da duração, e os 20% finais sobram como folga natural. Estudar muito num
dia só melhora recorde, mas não substitui presença em dias diferentes.

Quando só uma das duas condições foi cumprida, a tela diz **exatamente** a
outra: "Você já fez sua parte. Este pacote entra em campo em 2 dias." ou "O
calendário já liberou este pacote. Falta estudar em 1 dia diferente."

A conta é toda inteira de propósito: com `0,80` e `0,45` em ponto flutuante,
`ceil(3 × 0,80 × 25 ÷ 5)` dava 13 em vez de 12 e o pacote atrasava um dia
inteiro em toda Copa de 25 e de 50 dias.

##### Prorrogação

Passado o fim oficial, abre uma prorrogação de 7 dias. Os números oficiais da
Copa ficam congelados; cada dia ativo ainda traz um pacote do capítulo, até 2
na Mini Copa e 3 na Copa padrão. O mesmo estudo conta pra prorrogação e pra
Copa nova. No fim, espaço não conquistado fica vazio — sem mensagem de culpa e
sem perder nada do que já era teu.

O crédito é **retroativo**: quem estudou na prorrogação e só abriu o app duas
semanas depois recebe igual. O álbum é varrido do histórico inteiro a cada
passada, nunca "o que aconteceu hoje".

##### Nada conquistado se perde

Pacote ganho, figurinha colada, especial conquistada e dia gasto na
prorrogação são **catracas**: só sobem. Disso saem as regras seguintes.

- Mexer nas datas de uma Copa em andamento recalcula só os próximos marcos.
- O **formato** do capítulo (Mini ou padrão) trava na primeira conquista.
  Enquanto o álbum está vazio as datas mandam; depois disso, encurtar uma Copa
  padrão não pode fazer dez figurinhas coladas sumirem da tela.
- "Colado" é decidido pelo registro da colagem, nunca pela posição no baralho.
- O teto de pacotes do tipo nunca corta o que já foi conquistado: se um dado
  antigo deixar a catraca acima do teto, quem cede é o teto.
- Apagar bloco do histórico, trocar o fuso ou o relógio voltar no tempo não
  revoga nada.
- A janela oficial da Copa só **cresce** pra cobrir dia que o álbum já
  reconheceu — arrastar o início pra frente não zera os seis registros.
- O selo automático do capítulo é reversível. Ele é cache de valor calculado,
  não conquista: se o relógio estava adiantado ou o fim previsto for esticado,
  a Copa volta a jogar sem perder nada. Só a taça levantada à mão é
  definitiva.
- Abrir pacote continua possível depois do fechamento, e o percentual guardado
  na taça acompanha.

Restaurar um backup é a única coisa que substitui o álbum, porque substitui o
histórico inteiro — o app avisa isso na confirmação antes de importar.

##### A revelação

O pacote é concedido depois do estudo, sem interromper a sessão: aparece um
selo discreto na aba Álbum e uma linha no aviso de bloco concluído. Abrir é
quando o Davi quiser.

A abertura dura no máximo 5 segundos, tem "Pular" sempre à mão, revela as duas
figurinhas com número, nome e página, oferece "Colar todas" num toque e fecha
mostrando o progresso e o requisito exato do próximo pacote. **Ver no Álbum**
abre o caderno já na página da primeira figurinha do pacote, pra não ter que
procurar onde ela foi parar. As figurinhas são
coladas e salvas **antes** de qualquer animação: sair no meio, o app morrer, o
tablet dormir — nada custa pacote. Som, vibração e animação são desligáveis na
tela Foco, e a tela respeita `prefers-reduced-motion`. Esc e o botão Voltar do
Android fecham a sobreposição, não o app.

O fim de um bloco tem prioridade sobre a revelação, e o som do pacote não toca
enquanto o alarme do bloco está agendado na trilha: o alarme é a razão de o
app existir e não divide canal com comemoração.

##### Modelos de temporada

| Modelo | O que cria |
|---|---|
| Ciclos PBL | três Copas de 40 dias em sequência |
| Prova próxima | uma Copa daqui até o dia da prova |
| Semestre | o semestre fatiado em Copas de ~6 semanas |
| Concurso ou vestibular | N Copas mensais sucessivas |
| Modo livre | 90 dias em três Copas de 30 |
| Personalizada | Copa por Copa, no formulário da Estante |

Copa abaixo de 7 dias ou acima de 56 nunca é recusada: o app explica o que
muda e oferece dividir em capítulos, e o Davi decide. Copa nova já vem com a
data do dia seguinte à anterior, pra dia ativo não cair em buraco entre Copas.

##### O que o Álbum não faz

Não vende pacote, não tem moeda nem loja, não deixa pagar pra completar, não
usa repetida, não tem roleta, baú, brilho permanente nem falsa escassez. Não
pune ausência, não tem sequência frágil, não tem contagem regressiva
ameaçadora e nenhuma mensagem de culpa. E **não vai pra rede**: figurinha,
pacote, percentual e registro não entram no boletim do campeonato nem em
requisição nenhuma — a liga continua publicando só nome, minutos, dias ativos
e blocos.

#### Tema como dado

As cores e as frases não estão no código: moram em `copeiro/temas/<id>.json`.
O CSS não tem nenhuma cor de identidade escrita — tudo é `var(--…)`, e o
carregador de tema escreve as variáveis no `:root`. Trocar de tema não recarrega
a página e vale na hora, inclusive nos gráficos, no mapa de calor e nas faixas
diagonais.

O tema declara nove cores base e três faixas; o resto (bordas, sombra, escala do
mapa de calor, fundos suaves) é calculado a partir delas. As frases do app vêm
do mesmo arquivo, com um conjunto de reserva embutido para o caso de o JSON não
carregar.

| Arquivo | O que é |
|---|---|
| `temas/indice.json` | lista dos temas disponíveis, lida pelo seletor |
| `temas/gremio.json` | cores tricolores e as 136 frases de arquibancada |
| `temas/neutro.json` | cores sóbrias e frases de futebol sem clube |

Regras de conteúdo dos temas: **sem escudo, brasão ou logotipo** — a identidade
vem das cores e das faixas — e **sem letra de canto de torcida**. Apelido do
clube, gíria de arquibancada e bordão curto original, mínimo de cinco frases por
categoria.

#### O campeonato

A tabela é a única parte do app que fala com a rede. Usa o **Realtime Database
do Firebase pela API REST**, com `fetch` puro — sem SDK, porque a biblioteca do
Firebase vem de CDN e baixar biblioteca quebraria o funcionamento offline. Se a
rede falhar, o resto do app não muda e a última tabela baixada continua na tela.

O endereço do banco não fica no código: cada jogador entra uma vez pelo link de
convite, e o **código da liga funciona como senha do grupo** — quem não recebeu
o convite não acha a tabela. O app publica só quatro números por jogador: nome,
minutos do ciclo, dias ativos e blocos. Nenhum assunto de estudo sai do aparelho.

**Criar a liga** (uma vez, quem for o dono):

1. `console.firebase.google.com` → **Adicionar projeto** (plano Spark, grátis,
   sem cartão) → pode desligar o Google Analytics.
2. No menu, **Realtime Database** → **Criar banco de dados** → região mais
   próxima → começar em **modo de teste**.
3. Em **Regras**, colar e publicar:

   ```json
   {
     "rules": {
       "ligas": {
         "$liga": {
           ".read": true,
           ".write": true
         }
       }
     }
   }
   ```

   Leitura e escrita liberadas dentro de `ligas`, e nada fora dela. Sem conta
   para ninguém; a proteção é o código da liga ser secreto. É campeonato entre
   amigos, na confiança: qualquer participante consegue editar a própria linha.
4. Copiar o endereço do banco (algo como
   `https://seu-projeto-default-rtdb.firebaseio.com`).
5. No app: aba **Tabela** → **Preencher na mão** → colar o endereço, escolher um
   código de liga e o nome do campeonato → **Criar a liga**.
6. **Convidar o grupo** gera o link que configura o app de quem receber.

O plano grátis dá 20 mil escritas por dia; um grupo de amigos usa algumas
dezenas. Não há como cair na cobrança sem trocar de plano de propósito.

#### Copeiro Performance

Módulo opcional que liga o fim de um bloco a uma pausa de movimento. Nasce
desligado: a tela mostra um convite com duas saídas — **Ativar Performance** ou
**Agora não** — e quem recusa continua com o app inteiro, sem nenhuma função a
menos. Desativar depois devolve exatamente o mesmo estado.

Ligado, o fim do bloco troca os três botões de sempre por **Intervalo
inteligente**, **Pausa normal** e **Próximo bloco** — a pausa comum nunca deixa
de estar a um toque. O intervalo pergunta o tempo disponível (2, 5 ou 10 min, já
pré-selecionado pelo que mais se aproxima da pausa que entraria agora) e filtra
os protocolos por **Silencioso**, **Sem suar**, **Pouco espaço**, **Posso
caminhar**, **Antes do treino** e **Depois do treino**. A sugestão pode ser
recusada em qualquer ponto: *Prefiro pausa normal* antes, pular durante.

Cada protocolo roda passo a passo, com barra de progresso e uma instrução por
vez. São seis, todos de intensidade leve ou muito leve, e vivem sozinhos em
`performance-protocols.js` — separados do motor do app justamente para poderem
ser trocados depois da revisão profissional sem tocar em mais nada. **Todos
carregam o aviso de piloto na tela, em toda exibição:** nome, CREF ou aprovação
não entram aqui antes de um profissional de Educação Física revisar objetivo,
intensidade, ambientes e cada instrução. Isso está pendente, e o aviso sai só
depois.

Existe ainda um **contexto** opcional (onde estuda, se pode levantar, se precisa
de silêncio, se quer evitar suor, relação entre estudo e academia, atividades
preferidas e dias de treino) e um **registro de atividade** simples — o que foi,
quantos minutos, a data e uma observação de até 160 caracteres. Sem calorias,
sem peso, sem comparação com ninguém.

O painel **Estudo + movimento** é cumulativo e nada nele zera: horas de foco,
blocos, intervalos concluídos, atividades registradas, dias com foco *e*
movimento, e a resposta mais frequente à pergunta do fim do intervalo (*Mais
desperto*, *Igual* ou *Não ajudou*, perguntada no primeiro intervalo e a cada
três). Os marcos são de acontecimento, não de meta — inclusive "retorno depois
de um período sem atividade", que só existe pra registrar volta, nunca cobrança
por ausência.

Os dados ficam no mesmo `copeiro.v1` do resto do app, entram no backup JSON e
não saem do aparelho. Os eventos guardam nome estável e horário, ficam limitados
aos 500 mais recentes e não incluem nome, observações nem qualquer outro
identificador pessoal. A coleção bônus "Preparação Física" no Álbum ficou
deliberadamente de fora desta entrega: quando vier, tem de ser opcional e fora
da porcentagem, pra quem mantém o Performance desligado nunca ver coleção
obrigatória incompleta.

#### Onde os dados ficam

No `localStorage` daquele aparelho, com aviso e fallback em memória se o
navegador bloquear ou a cota encher. Na abertura o app chama
`navigator.storage.persist()`, para o sistema não descartar os dados quando o
aparelho ficar sem espaço. Backup e restauração em JSON pela aba Histórico.

**Rodar:** abrir `copeiro/index.html` no navegador, ou instalar pelo GitHub
Pages (passo a passo abaixo).

#### Publicar no GitHub Pages

1. `Settings` → `Pages` → em **Build and deployment**, *Source*: `Deploy from
   a branch`; *Branch*: `main` e pasta `/ (root)`. Salvar.
2. Esperar o deploy (aba `Actions` mostra o progresso).
3. O app fica em `https://<usuário>.github.io/<repositório>/copeiro/`.

O service worker exige HTTPS — o GitHub Pages já serve em HTTPS, então nada a
configurar. Todos os caminhos são relativos: funciona em qualquer subpasta.

Publicar é só mesclar na `main` e trocar o número em `VERSAO`, no
`service-worker.js`. Sem isso o app instalado continua servindo o cache antigo,
por mais que o repositório esteja atualizado.

#### Como a versão nova chega no aparelho

O cache é *offline-first*: o app abre do disco e só olha a rede quando falta
arquivo. Isso é o que faz ele funcionar no ônibus, e é também o que faria uma
publicação nova demorar a aparecer. O caminho é este:

1. Ao voltar pro app — no máximo uma vez a cada 15 minutos — a tela pergunta se
   tem versão nova. Sem isso, um PWA que vive em segundo plano poderia passar
   semanas na versão de antes.
2. Achando, o worker novo **baixa tudo e espera**. Ele não assume na hora de
   propósito: a ativação apaga o cache antigo, e uma tela ainda rodando o
   código velho passaria a receber arquivo da versão nova — frase com `{nome}`
   cru, arte que a função antiga não sabe desenhar.
3. Quem escolhe a hora é a tela. Com o app em segundo plano e nada em
   andamento, a troca acontece sozinha e a próxima abertura já é a nova. Com o
   app na frente, aparece o ponto na aba **Mais** e a linha *Atualizar o
   Copeiro*, que troca no toque.
4. **Bloco rodando não troca**, nem sozinho nem no toque: o alarme depende de
   um áudio que já está tocando, e depois de recarregar o navegador só libera
   som com um toque — o fim do bloco chegaria mudo. A linha aparece assim que o
   bloco acaba. Camada aberta também segura, pra não sumir com o que o Davi
   está fazendo.

Telas publicadas **antes** desta versão não sabem conversar com o worker novo.
Para elas existem dez segundos de cortesia: se ninguém se apresentar, o worker
assume mesmo assim, e a atualização aparece na abertura seguinte. É o preço de
uma única troca — a partir desta versão, a conversa acontece.

#### Instalar no tablet Android

1. Abrir o endereço acima no **Chrome** do tablet.
2. Menu `⋮` → **Adicionar à tela inicial** (ou **Instalar app**) → confirmar.
3. Abrir pelo ícone da tela inicial: abre em tela cheia, sem barra do
   navegador, e a partir daí funciona sem internet.
