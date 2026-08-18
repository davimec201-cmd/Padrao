# Design system TEA Formation — tokens da Fase 0

**Esqueleto do Porto Seguro, pele das cartilhas.** Este documento explica cada token de
`design/tokens.json`, de onde ele saiu e o que foi decidido quando as fontes divergiram.

Como as cartilhas são exportações rasterizadas do Photoshop, os valores **não** foram lidos de
metadados: cada página foi renderizada a 100 dpi (2428×3445 px) e amostrada em pixel. A escala
usada é **11.562 px/mm** sobre A4. Onde aparece "medido", há um número atrás; onde aparece
"derivado", há uma fórmula; onde aparece "pendente", falta arquivo.

---

## 1. Cores

### Banda 60 — fundos dessaturados

| Token | Valor | De onde veio |
|---|---|---|
| `fundo_palco` | `#F9F4E5` | Manual, seção 4 (Paleta.png mede `#F8F3E4` — arredondamento de PNG). Fundo de toda página do e-book. |
| `fundo_bloco` | `#FFFFFF` | Medido: card branco da CARTILHA_01 p4 é 100% `#FFFFFF` puro, sem tinta. |
| `fundo_bloco_secundario` | `#F1E9D5` | Derivado: `fundo_palco` escurecido ~4% em L\*. Zebra de tabela e bloco aninhado sobre branco. |
| `destaque_pedagogico_wash` | `#E6F4FA` | Derivado: azul institucional a 10% sobre branco. Fundo do par objetivo/princípio. |
| `acento_material_wash` | `#FFF1EC` | Derivado: coral a 10% sobre branco. |
| `facil_wash` | `#E6F7F1` | Derivado: verde TEAplay a 10% sobre branco. Coluna "Mais fácil". |
| `desafiador_wash` | `#FFF3F1` | Derivado: coral secundário a 10% sobre branco. Coluna "Mais desafiador". |
| `atencao_fundo` | `#FDF5E9` | Derivado: amarelo TEAbook a 12% sobre branco. Fundo da `caixa_atencao`. |

### Banda 30 — tons terrosos dos habitantes e texto

| Token | Valor | De onde veio |
|---|---|---|
| `texto_corpo` | `#1F2D3D` | Manual, seção 4 ("Seriedade"). 12.72:1 sobre creme. |
| `texto_secundario` | `#5A6675` | Derivado: `texto_corpo` clareado até 5.32:1 sobre creme. Rodapé e notas. |
| `linha_divisoria` | `#E0BC95` | **Medido no pelo da Mamãe Urso** (CARTILHA_04 p1, testa). A linha divisória vem de um habitante, não de um cinza inventado. |
| `habitante_tan` | `#E0BC95` | Medido: pelo claro da Mamãe Urso, CARTILHA_04 p1. |
| `habitante_caramelo` | `#C89D67` | Medido: blusa da Mamãe Urso, CARTILHA_04 p1. |
| `habitante_marrom` | `#9B6838` | Medido: pelo escuro da Mamãe Urso, CARTILHA_04 p1. |
| `habitante_ocre` | `#D88C4A` | Medido: pelo da Professora Canguru, CARTILHA_04 p1. |
| `habitante_terracota` | `#D25E38` | Medido: juba do Leo, CARTILHA_04 p1. |

Esses cinco tons não estão no manual — eles estão nos personagens, e é deles que sai o
calor da página sem gastar a cota de cor plena.

### Banda 10 — cor plena, reservada ao pedagógico

| Token | Valor | De onde veio |
|---|---|---|
| `destaque_pedagogico` | `#0193C8` | Manual, seção 4. Só preenchimento e filete. |
| `destaque_pedagogico_texto` | `#016E96` | Derivado: azul escurecido até 5.72:1 sobre branco. É a cor dos rótulos `OBJETIVO TERAPÊUTICO` / `PRINCÍPIO ABA-TCC`. |
| `acento_material` | `#FF7345` | Manual (TEAnimal). Pill da capa, disco do número da ficha, abertura de bloco. |
| `logo_azul` | `#39A6D8` | Medido em `simbolo_peca_transparente.png` e nos rodapés das 4 cartilhas (`#38A6D7`). É **outro** azul, não o institucional. |
| `taxonomia_teabook` `teagame` `teaplay` `secundario` | `#EDAF47` `#5E3D93` `#00AB6F` `#FF8573` | Manual, seção 4/6. Só taxonomia e marcadores. |

### As duas regras de cor que o sistema aplica sozinho

1. **Coral nunca é cor de texto.** `#FF7345` sobre branco dá 2.70:1 — reprova para qualquer
   tamanho. Coral é preenchimento; o texto por cima é navy (**5.19:1**, aprova até corpo).
2. **Azul institucional com texto branco só em display.** `#FFFFFF` sobre `#0193C8` dá 3.49:1:
   serve para texto ≥18pt (ou ≥14pt bold), não para corpo. Corpo sobre azul usa o wash claro
   com texto navy (12.45:1).

Isso mantém a paleta exata do manual e ainda assim entrega 4.5:1 em todo texto de corpo — as
duas exigências, sem escolher entre elas.

---

## 2. Tipografia

| Papel | Família | Onde vai | Especificação medida |
|---|---|---|---|
| Display | **Omnes Huggies Bold** | Título de capa, H1, número de bloco e de ficha | ⚠️ **pendente** — arquivo proprietário. Substituto declarado: Poppins Bold, sinalizado no QA. |
| Título / interface | **Poppins** | H2, H3, rótulos, rodapé, campos de formulário | Medido: o corpo e os rótulos das cartilhas são Poppins ("a" de um andar, geométrica, terminais retos). |
| Leitura | **Manrope** | Todo texto corrido | Manual, seção 5: face de leitura e elo de coerência da marca. |

### Escala (pt sobre A4)

| Nível | pt / entrelinha | Origem |
|---|---|---|
| `capa_titulo` | 46 / 1.05, contorno 0.075em coral | Medido 62pt/1.22 e contorno ~0.08em na CARTILHA_04 p1 → **reduzido a 46pt** (decisão T1). |
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

| Item | Estado | Efeito enquanto faltar |
|---|---|---|
| `Omnes_Huggies-Bold.otf` e `-Medium.otf` | No Drive; não baixável por esta sessão | Títulos saem em Poppins Bold e o QA emite alerta em toda geração |
| Lockup oficial TEAFormation / TEAnimal (PNG ou SVG) | Só existe rasterizado dentro das cartilhas | Rodapé reconstruído em tipografia + peça real |
| Ilustrações dos personagens com fundo transparente | No Drive como JPG com fundo | Capa usa `ilustracao_padrao` (peça do quebra-cabeça) |
| `Identidade Visual.pdf` completo (91 MB) | No Drive; grande demais para esta sessão | Trabalhando com o Resumo de Identidade, que cobre paleta, tipografia e simbolismo |
