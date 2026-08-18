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
