# Design system TEA Formation — tokens

**Esqueleto do Porto Seguro, pele das cartilhas.** Este documento explica cada token de
`design/tokens.json`, de onde ele saiu e o que foi decidido quando as fontes divergiram.

Como as cartilhas são exportações rasterizadas do Photoshop, os valores **não** foram lidos de
metadados: cada página foi renderizada a 100 dpi (2428×3445 px) e amostrada em pixel. A escala
usada é **11.562 px/mm** sobre A4. Onde aparece "medido", há um número atrás; onde aparece
"derivado", há uma fórmula.

## Três regras que valem para todo material

1. **Paleta institucional por padrão** — azul, branco, bege e navy. As cores do
   Universo TEAnimal são para público infantil e só entram com `tema: teanimal`.
2. **Nenhum personagem por padrão** — personagem do TEAnimal só aparece quando o
   material pede, por `personagem:` no cabeçalho ou por `:::voz <nome>`.
3. **Supervisão técnica é dado fixo** — Ingrid Ceron, CRP 12/15726, Especialista
   em autismo (TEA) e em Terapia ABA. Vem de `tokens.json`, não de digitação.

As três estão em `design/tokens.json` → `regras_do_material`, e cada uma tem uma
verificação no QA.

---

## 1. Cores

O sistema tem **dois temas**. O padrão é o institucional; o do Universo TEAnimal
só entra quando o material pede `tema: teanimal` no cabeçalho.

### Tema institucional — o padrão

Azul, branco, bege e navy. É a cara da TEA Formation: material técnico, para
famílias e clínicas, sem o registro infantil.

| Papel | Valor | O que é |
|---|---|---|
| `fundo_palco` | `#F9F4E5` | creme institucional. Fundo de toda página |
| `fundo_bloco` | `#FFFFFF` | card branco. Medido: o card da CARTILHA_01 p4 é branco puro |
| `fundo_bloco_secundario` | `#F1E9D5` | creme escurecido 4%. Zebra de tabela, bloco de apoio |
| `texto_corpo` / `texto_titulo` | `#1F2D3D` | navy do manual. 12.72:1 sobre creme |
| `texto_secundario` | `#5A6675` | navy clareado até 5.32:1. Rodapé e notas |
| `linha_divisoria` | `#E5DCC3` | creme escurecido 10%. Filete e divisória |
| `destaque_pedagogico` | `#0193C8` | azul institucional. Objetivo e princípio |
| `destaque_pedagogico_texto` | `#016E96` | azul escurecido até 5.72:1. Rótulos |
| `destaque_pedagogico_wash` | `#E6F4FA` | azul a 10%. Fundo do par pedagógico |
| `acento_material` | `#016E96` | tarja da capa e número da ficha, com texto branco |
| `divisoria_fundo` | `#1F2D3D` | página de abertura de bloco, inteira em navy |
| `atencao_fundo` / `atencao_texto` | `#1F2D3D` / `#FFFFFF` | caixa de atenção é card escuro: o sinal mais forte do material |
| `facil_filete` / `desafiador_filete` | `#39A6D8` / `#1F2D3D` | claro para o mais fácil, navy para o mais desafiador |
| `logo_azul` | `#39A6D8` | peça do logo. Medido no arquivo e nas 4 cartilhas |

A lógica: **azul é pedagógico, bege é apoio, navy é crítico.** Você lê a página e
sabe o que é o quê sem precisar do rótulo.

### Tema TEAnimal — a pedido

Re-aponta só os papéis de acento; estrutura, grid e tipografia não mudam.

| Papel | Institucional | TEAnimal |
|---|---|---|
| `acento_material` | `#016E96` azul escuro | `#FF7345` coral |
| `divisoria_fundo` | `#1F2D3D` navy | `#FF7345` coral |
| `atencao_fundo` | `#1F2D3D` navy | `#FDF5E9` amarelo a 12% |
| `facil` / `desafiador` | azul claro / navy | `#00AB6F` verde / `#FF8573` coral claro |
| `linha_divisoria` | `#E5DCC3` bege | `#E0BC95` pelo da Mamãe Urso |
| `voz_fundo` | `#F1E9D5` bege | `#FFF1EC` coral a 10% |

Os tons dos habitantes continuam medidos e disponíveis no tema lúdico: pelo claro
`#E0BC95`, blusa `#C89D67`, pelo escuro `#9B6838`, canguru `#D88C4A`, juba do Leo
`#D25E38` (todos da CARTILHA_04 p1).

### As três regras de cor que o sistema aplica sozinho

1. **Coral nunca é cor de texto.** `#FF7345` sobre branco dá 2.70:1 — reprova em
   qualquer tamanho. É preenchimento, com navy por cima (5.19:1).
2. **Azul institucional com texto branco só em display.** 3.49:1 serve para ≥18pt.
   Para corpo, o wash claro com navy, ou o azul escurecido `#016E96` (5.72:1).
3. **Cor de um universo não entra em material do outro.** O QA avisa e diz como
   pedir o tema certo.

Os 32 pares de texto de corpo × fundo, nos dois temas, ficam ≥ 4.5:1. Isso é
verificado a cada geração.

---

## 2. Tipografia

| Papel | Família | Onde vai | Especificação medida |
|---|---|---|---|
| Display | **Poppins Bold** | Título de capa, H1, número de bloco e de ficha | Omnes Huggies foi **descartada por decisão do fundador**. O `@font-face` continua declarado em `base.css`: para retomar, basta colocar os `.otf` em `assets/fontes/` e trocar o nome da família em `tokens.json`. |
| Título / interface | **Poppins** | H2, H3, rótulos, rodapé, campos de formulário | Medido: o corpo e os rótulos das cartilhas são Poppins ("a" de um andar, geométrica, terminais retos). |
| Leitura | **Manrope** | Todo texto corrido | Manual, seção 5: face de leitura e elo de coerência da marca. |

### Escala (pt sobre A4)

| Nível | pt / entrelinha | Origem |
|---|---|---|
| `capa_titulo` | 46 / 1.05, navy com contorno 0.075em coral | Medido 62pt/1.22 e contorno ~0.08em na CARTILHA_04 p1 → **reduzido a 46pt** (decisão T1), em Poppins Bold. O contorno é feito em SVG, com uma passada de traço e outra de preenchimento — WeasyPrint não implementa `text-stroke` nem `text-shadow`. |
| `capa_subtitulo` | 15 / 1.3, navy sobre pill coral | Medido: pill de 16.4 × 140.6mm, raio 3.9mm (CARTILHA_04 p1). Texto virou navy (decisão T3). |
| `h1` | 28 / 1.12 | Escala derivada do título de capa por passo de ~1.35. |
| `h2` | 16.5 / 1.25 | idem |
| `h3` | 12.5 / 1.3 | idem |
| `rotulo` | 8.5 / 1.2, caixa alta, tracking 0.08em | Estrutura do Porto Seguro p7 (`OBJETIVO TERAPÊUTICO`); caixa e cor das cartilhas. |
| **`corpo`** | **11.5 / 1.52 (= 17.5pt)** | **Medido: o card coral da CARTILHA_01 p4 tem avanço de linha de 17.2–18.1pt.** O e-book herda o ritmo vertical exato do material aprovado (decisão T2). |
| `corpo_pequeno` | 10 / 1.5 | Notas e rodapés de ficha. |
| `nota` | 9.5 / 1.5 | Observações e legendas. |
| `rodape` | 7.5 / 1.2 | Rodapé de página. |

### A ressalva de tradução de medium

Cartilha é narrativa ilustrada: os balões da CARTILHA_02 p5 medem **~30pt de altura de glifo com
39.7pt de avanço** — escala de quadrinho, para ler em pé, quatro páginas. E-book é 30–50 páginas
de leitura longa; reproduzir aquilo em CSS daria um material infantilizado e cansativo.

O que foi feito: **os balões foram descartados como escala e mantidos como conceito** (card
arredondado, respiro generoso). O corpo de texto não foi inventado — foi tirado do **outro**
lugar da cartilha onde há texto de leitura de verdade, o card informativo da p4, que mede
11.5–12pt com 17.5pt de entrelinha. Ou seja: o ritmo vertical do e-book é literalmente o da
cartilha, medido; o que mudou foi qual elemento da cartilha serviu de referência.

Medida de linha: 152mm a 11.5pt Manrope ≈ **72 caracteres** por linha (a cartilha, com card mais
estreito, roda a ~61). Dentro da faixa confortável para leitura longa.

---

## 3. Grid

| Token | Valor | Origem |
|---|---|---|
| Página | A4, 210 × 297mm | Porto_Seguro.pdf mede 595.28 × 841.89pt; cartilhas na mesma proporção A. |
| Margem lateral | 29mm | **Medido**: o bloco de conteúdo das cartilhas tem 151.4mm com 29.3mm de cada lado — idêntico nas 4. |
| Largura de conteúdo | 152mm | idem |
| Margem topo / base | 22 / 20mm | Derivado: base maior que o rodapé (logo a 12mm) e cabeça alinhada ao ritmo. |
| Base vertical | 6.2mm | = 17.5pt, o avanço de linha do corpo. Toda a escala de espaço é múltipla disso: 3.1 / 6.2 / 9.3 / 12.4 / 18.6mm. |
| Padding de card | 9.3mm | 1.5× a base. |

## 4. Elementos gráficos

| Token | Valor | Origem |
|---|---|---|
| `raio_card` | 8mm | **Medido**: cards de conteúdo das cartilhas têm r ≈ 8.2mm (95px). |
| `raio_pill` | 4mm | **Medido**: pill de subtítulo r ≈ 3.9mm (45px). |
| `faixa_rodape` | 13mm na borda, 26mm no ápice | **Medido**: o arco branco de sangria das capas/contracapas. Assinatura gráfica da marca; usado na capa e na página final. |
| `sombra_card` | `0 1.5mm 4mm rgba(31,45,61,.10)` | Derivado — as cartilhas têm sombra suave, o valor exato não foi medido. |
| `filete` | 1.2mm | Filete lateral de `caixa_atencao` e de abertura de bloco. |
| Logo de rodapé | 4.6mm de altura, 12mm da base, à direita | ⚠️ **reconstruído** em Poppins ("TEA" 700 + "Formation" 400) com a peça real. Pendente o lockup oficial. |

---

## 5. Divergências entre manual e cartilha

O manual manda; abaixo o que ele venceu e o que isso custou.

| # | Manual | Cartilha (medido) | Decisão |
|---|---|---|---|
| **D1** | Coral TEAnimal `#FF7345` | `#ED724A` nas 4 cartilhas e no logo | **Manual.** A diferença é sutil (o coral da cartilha é 7% mais escuro e menos saturado); adotar o token do manual mantém a paleta fechada. |
| **D2** | Azul institucional `#0193C8`; o texto da seção 6 cita `#3BA6DA` como par | `#38A6D7` no card da CARTILHA_03 e em todo logo | **Ambos, com papéis separados**: `#0193C8` = destaque pedagógico; `#39A6D8` = azul do logo. O manual já previa os dois. |
| **D3** | Texto `#1F2D3D` (navy) | Preto quase puro (`#050606`) nos balões e cards | **Manual.** Navy é mais suave em leitura longa e é o token da marca. |
| **D4** | — | Lockup "TEAnimal + TEAFormation" no rodapé | Reconstruído tipograficamente até chegar o arquivo oficial. |
| **D5** | — | "Realização" em coral sobre branco (2.70:1) | **Não replicado**: coral virou cor de preenchimento. Onde a cartilha usa coral como texto, o e-book usa navy. |

### O título de capa: por que navy e não branco

A cartilha escreve o título em **branco com contorno coral**, e funciona porque
atrás dele existe uma ilustração de sangria. O e-book tem fundo creme: branco
sobre creme desaparece, sobra só o contorno oco — testado, e a capa morre na
miniatura de uma página de vendas. O tratamento foi mantido (mesma fonte, mesmo
contorno coral, mesma espessura medida) e só o preenchimento virou navy
(**decisão T4**). Comparação das três opções em `diagramador/amostras/`.

## 6. Melhorias propostas (mantendo a marca reconhecível)

1. **Texto navy dentro dos cards coloridos, no lugar do branco.** A cartilha usa branco sobre
   coral (2.70:1) e sobre azul (3.49:1). Trocando só a cor do texto, o mesmo card passa a
   5.19:1 sem mexer em uma gota da tinta da marca. A alternativa seria escurecer o coral até
   `#BF5633` para o branco funcionar — mas aí seria uma cor que não existe no manual.
   **Recomendo a troca do texto.**
2. **Cor plena com orçamento.** O e-book tem 30–50 páginas: repetir o card coral cheio a cada
   página viraria ruído. A cor plena fica reservada ao par objetivo/princípio e às aberturas de
   bloco; o miolo trabalha em wash (10% da mesma cor). É a regra 60-30-10 aplicada à extensão
   real do material.
3. **A linha divisória sai do pelo do urso.** Em vez de um cinza neutro, o filete usa
   `habitante_tan #E0BC95`. Custa nada e faz a página parecer da mesma família das ilustrações.

## 7. Pendências (bloqueiam "100% fiel", não bloqueiam a construção)

| Item | Estado | Efeito |
|---|---|---|
| Omnes Huggies | **descartada** por decisão do fundador em 18/08/2026 | Display é Poppins Bold. O `@font-face` segue declarado: colocar os `.otf` em `assets/fontes/` e trocar o nome em `tokens.json` retoma a face original sem mexer em layout |
| Ilustrações dos personagens | **resolvido** — 8 personagens em `assets/ilustracoes/` com fundo transparente | Mamãe Urso, Leo, Jojo, Cora, Pipo, Marcos, Professora Canguru, Sr. Miau |
| Lockup oficial TEAFormation / TEAnimal (PNG ou SVG) | Só existe rasterizado dentro das cartilhas | Rodapé reconstruído em tipografia + peça real |
| `Identidade Visual.pdf` completo (91 MB) | No Drive; grande demais para esta sessão | Trabalhando com o Resumo de Identidade, que cobre paleta, tipografia e simbolismo |
