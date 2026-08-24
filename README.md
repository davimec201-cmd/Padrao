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

Pomodoro de estudo, PWA instalável, feito para o tablet Android. Quatro
arquivos, nenhuma dependência: `index.html` (HTML + CSS + JS embutidos),
`manifest.webmanifest`, `service-worker.js` e os dois ícones PNG. Depois de
instalado, funciona 100% offline.

#### O que ele faz

| Parte | Como funciona |
|---|---|
| **Timer** | Foco de 15, 25, 30 ou 50 min (padrão 30). Pausa curta e intervalo com duração editável, e um contador de focos que decide qual das duas entra — por padrão 5 min de pausa, 15 min de intervalo a cada 3 focos. Toda pausa é livre. Iniciar, pausar, retomar, zerar, pular. |
| **Relógio real** | O tempo vem de `Date.now()`, nunca de contagem de ticks: com a tela apagada ou o app em segundo plano o bloco não atrasa, e um bloco que terminou com o app fechado é fechado na volta com o horário certo. |
| **Alarme** | Gerado sem arquivo de som: toque de gol no fim do foco, apito de árbitro começando o jogo no fim da pausa. Para avisar com o app fora da tela, o toque vai **gravado dentro de uma trilha silenciosa**, que o tocador de mídia leva até o fim mesmo com a página congelada. Três modos: desligado (música intacta), só nos 2 minutos finais (padrão) ou o bloco inteiro. O bloco aparece na barra de notificação, uma notificação avisa no fim, vibra quando o aparelho tem vibração, e o Wake Lock mantém a tela acesa durante o bloco, onde houver suporte. |
| **Bloquear o que distrai** | Antes de cada bloco o app pergunta se o Modo Foco do Android está ligado — bloquear aplicativo é coisa que só o sistema faz, e nenhuma página da web consegue. O lembrete tem três saídas: começar, sair pra ligar, ou nunca mais perguntar. |
| **Temporadas e Copas** | Uma Temporada é o álbum inteiro; cada **Copa** dentro dela é um capítulo. Nome, início e fim previsto são os únicos dados obrigatórios. Todo bloco entra automaticamente na Copa de hoje. Ao encerrar, as estatísticas congelam e a Copa vai para a Estante. |
| **Álbum da Copa** | A coleção da temporada: 18 figurinhas na Mini Copa, 30 na Copa padrão, todas visíveis com nome e critério desde o primeiro dia. Pacotes de 2, sem repetidas, liberados por estudo **e** por passagem do tempo. Ver abaixo. |
| **Assunto** | Campo com autocompletar pelos assuntos do ciclo atual e atalho para os 5 últimos. Fica visível durante o bloco. |
| **Histórico** | Hoje, últimos 7 dias em barras, lista completa com opção de corrigir o assunto ou apagar o registro, exportar e importar tudo em JSON. |
| **Cartas** | Flashcards com prazo: escada de 1, 2, 4, 8 e 16 dias, teto pela data da prova e reta final nos últimos 3 dias. Travei / Quase / Mandei bem, lacunas com `{{chaves}}`, revisão livre fora da fila e edição de qualquer campo, inclusive degrau e data. Ao encerrar o ciclo, o baralho é guardado junto com ele. |
| **Progresso** | Mapa de calor anual, estante de ciclos, comparação em tempo real com o ciclo anterior, contador vitalício de horas com marcos de 100/250/500/1000h, recordes pessoais e os números do baralho do ciclo. |
| **Tabela** | Campeonato com os amigos: classificação por horas copadas no ciclo (1 hora = 1 ponto, empate no desempate por dias ativos), campeão congelado quando o ciclo fecha, sala de troféus e campeão geral por número de títulos. Quem termina em primeiro ganha acabamento dourado no objeto da Estante. |

Sem meta de horas, sem barra de ciclo, sem moeda, loja, ponto ou nível. Nada
murcha nem cobra por dia parado: o app só registra e mostra o que foi feito.

#### O Álbum da Copa

O sistema de recompensa do Copeiro. Ele celebra **estudo feito**, não tempo
gasto navegando no app.

O laço é: começar o bloco → estudar com o app no bolso → o bloco fecha →
ganhar progresso ou pacote → voltar quando quiser → abrir → ver o próximo
marco.

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
figurinhas com nome e página, oferece "Colar todas" num toque e fecha
mostrando o progresso e o requisito exato do próximo pacote. As figurinhas são
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

#### Instalar no tablet Android

1. Abrir o endereço acima no **Chrome** do tablet.
2. Menu `⋮` → **Adicionar à tela inicial** (ou **Instalar app**) → confirmar.
3. Abrir pelo ícone da tela inicial: abre em tela cheia, sem barra do
   navegador, e a partir daí funciona sem internet.
