# Padrão

Ferramentas pessoais. Feitas sob medida, sem anúncio, sem conta, sem ninguém
decidindo por mim como as coisas devem funcionar.

## Projetos

### `laudos-oct/`

Claude Skill que emite laudos de OCT de mácula e nervo óptico operando o AnyDesk
sozinha no macOS ou no Windows: captura a tela, lê os valores com dupla leitura,
redige no template do hospital e salva o PDF. Não assina, não publica e é
somente-leitura no sistema do hospital.

Instalação e uso em `laudos-oct/INSTALACAO.md`; travas e endurecimento em
`SEGURANCA.md`. `REVISAO-2026-08-20.md` é a auditoria de código que originou a
versão atual, e `PENDENCIAS.md` diz o que ainda espera o médico responsável.

**A base científica ainda não passou por revisão médica, e o gerador recusa
emitir laudo enquanto não passar.** É trava de programa, não recomendação.

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
| **Ciclos** | Nome, início e fim previsto. Todo bloco entra automaticamente no ciclo ativo. Ao encerrar, as estatísticas congelam e o ciclo vai para a Estante. |
| **Assunto** | Campo com autocompletar pelos assuntos do ciclo atual e atalho para os 5 últimos. Fica visível durante o bloco. |
| **Histórico** | Hoje, últimos 7 dias em barras, lista completa com opção de corrigir o assunto ou apagar o registro, exportar e importar tudo em JSON. |
| **Cartas** | Flashcards com prazo: escada de 1, 2, 4, 8 e 16 dias, teto pela data da prova e reta final nos últimos 3 dias. Travei / Quase / Mandei bem, lacunas com `{{chaves}}`, revisão livre fora da fila e edição de qualquer campo, inclusive degrau e data. Ao encerrar o ciclo, o baralho é guardado junto com ele. |
| **Progresso** | Mapa de calor anual, estante de ciclos, comparação em tempo real com o ciclo anterior, contador vitalício de horas com marcos de 100/250/500/1000h, recordes pessoais e os números do baralho do ciclo. |
| **Tabela** | Campeonato com os amigos: classificação por horas copadas no ciclo (1 hora = 1 ponto, empate no desempate por dias ativos), campeão congelado quando o ciclo fecha, sala de troféus e campeão geral por número de títulos. Quem termina em primeiro ganha acabamento dourado no objeto da Estante. |

Sem meta de horas, sem barra de ciclo, sem moeda, loja, ponto ou nível. Nada
murcha nem cobra por dia parado: o app só registra e mostra o que foi feito.

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
