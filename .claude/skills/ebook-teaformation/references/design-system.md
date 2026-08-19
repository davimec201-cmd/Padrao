# Design system — valores congelados

Fonte de verdade: `design/tokens.json`. Esta página é gerada a partir dele
por `diagramador/ferramentas/empacotar_skill.py` — não edite à mão, edite o
tokens e rode o empacotador.

Todo valor aqui é **medido** nas cartilhas aprovadas, veio do **manual** de
identidade, ou é **derivado** por fórmula de um dos dois. Não há valor escolhido
no olho — e é isso que faz o material novo parecer da mesma família do antigo.

## Paleta

### Institucional — o padrão de todo material

| Cor | Valor | Significado / uso |
|---|---|---|
| `azul` | `#0193C8` | confiança, cuidado, estabilidade, técnica |
| `azul_escuro` | `#016E96` | azul escurecido até 4.5:1 com branco |
| `azul_logo` | `#39A6D8` | peça do logo e cards da CARTILHA_03 |
| `azul_wash` | `#E6F4FA` | azul a 10% sobre branco |
| `creme` | `#F9F4E5` | leveza, acolhimento, acessibilidade |
| `creme_escuro` | `#F1E9D5` | creme escurecido ~4% em L* |
| `bege_linha` | `#E5DCC3` | filete e divisória do tema institucional |
| `branco` | `#FFFFFF` |  |
| `navy` | `#1F2D3D` | seriedade |
| `navy_claro` | `#5A6675` | navy clareado até 5.3:1 sobre creme |

### TEAnimal — só com `tema: teanimal`

| Cor | Valor | Significado / uso |
|---|---|---|
| `coral` | `#FF7345` | TEAnimal · alegria; cartilhas medem #ED724A |
| `coral_wash` | `#FFF1EC` | coral a 10% sobre branco |
| `coral_claro` | `#FF8573` | tom secundário |
| `coral_claro_wash` | `#FFF3F1` |  |
| `amarelo` | `#EDAF47` | TEAbook · curiosidade |
| `amarelo_wash` | `#FDF5E9` | amarelo a 12% sobre branco |
| `verde` | `#00AB6F` | TEAplay · desenvolvimento |
| `verde_wash` | `#E6F7F1` |  |
| `roxo` | `#5E3D93` | TEAgame · imaginação |
| `habitante_tan` | `#E0BC95` | pelo claro da Mamãe Urso |
| `habitante_caramelo` | `#C89D67` | blusa da Mamãe Urso |
| `habitante_marrom` | `#9B6838` | pelo escuro da Mamãe Urso |
| `habitante_ocre` | `#D88C4A` | pelo da Professora Canguru |
| `habitante_terracota` | `#D25E38` | juba do Leo |

## Papéis de cor

Não use a paleta direto: use o papel. É o que permite trocar de tema sem
rediagramar, e o que impede o coral de virar cor de texto por engano.

| Papel | Institucional | TEAnimal | Para quê |
|---|---|---|---|
| `fundo_palco` | `#F9F4E5` | — |  |
| `fundo_bloco` | `#FFFFFF` | — |  |
| `fundo_bloco_ficha` | `#FFFFFF` | — |  |
| `fundo_bloco_secundario` | `#F1E9D5` | — |  |
| `texto_corpo` | `#1F2D3D` | — |  |
| `texto_titulo` | `#1F2D3D` | — |  |
| `texto_secundario` | `#5A6675` | — |  |
| `texto_sobre_cor` | `#FFFFFF` | — |  |
| `linha_divisoria` | `#E5DCC3` | `#E0BC95` | no tema TEAnimal vira o tom de pelo da Mamãe Urso |
| `destaque_pedagogico` | `#0193C8` | — | objetivo terapêutico e princípio ABA-TCC |
| `destaque_pedagogico_texto` | `#016E96` | — |  |
| `destaque_pedagogico_wash` | `#E6F4FA` | — |  |
| `acento_material` | `#016E96` | `#FF7345` | preenchimento do pill de capa e do número da ficha; texto branco por cima |
| `acento_material_texto` | `#FFFFFF` | `#1F2D3D` | texto sobre acento_material |
| `acento_material_wash` | `#F1E9D5` | `#FFF1EC` |  |
| `divisoria_fundo` | `#1F2D3D` | `#FF7345` | página de abertura de bloco, inteira |
| `divisoria_texto` | `#FFFFFF` | `#1F2D3D` |  |
| `facil_wash` | `#F1E9D5` | `#E6F7F1` |  |
| `facil_filete` | `#39A6D8` | `#00AB6F` |  |
| `desafiador_wash` | `#F1E9D5` | `#FFF3F1` |  |
| `desafiador_filete` | `#1F2D3D` | `#FF8573` |  |
| `observar_fundo` | `#FFFFFF` | `#F1E9D5` |  |
| `observar_filete` | `#0193C8` | `#C89D67` |  |
| `atencao_fundo` | `#1F2D3D` | `#FDF5E9` | caixa de atenção: card escuro, o sinal mais forte do material |
| `atencao_filete` | `#0193C8` | `#EDAF47` | filete da caixa de atenção |
| `voz_fundo` | `#F1E9D5` | `#FFF1EC` |  |
| `voz_filete` | `#0193C8` | `#FF7345` |  |
| `capa_contorno` | `#39A6D8` | `#FF7345` | contorno do título de capa |
| `logo_azul` | `#39A6D8` | — |  |
| `atencao_texto` | `#FFFFFF` | `#1F2D3D` |  |

### As três regras de cor

1. **Coral nunca é cor de texto.** `#FF7345` sobre branco dá 2.70:1 — reprova em
   qualquer tamanho. Coral é preenchimento, com navy por cima (5.19:1). Foi assim
   que se manteve a paleta exata do manual entregando 4.5:1 no corpo, em vez de
   escolher entre as duas coisas.
2. **Azul institucional com texto branco só em display.** `#FFFFFF` sobre
   `#0193C8` dá 3.49:1: serve para ≥18pt. Para corpo, use o wash claro com navy
   (12.45:1) ou o azul escurecido `#016E96` (5.72:1).
3. **Cor de um universo não entra em material do outro.** Se precisar da paleta
   lúdica, peça o tema; não misture.

Todo texto de corpo (≤13pt) fica ≥ 4.5:1 nos dois temas. São 32 pares conferidos
a cada geração, pelo QA.

## Tipografia

- **Display e títulos de capa:** Poppins (Bold, SemiBold)
- **Títulos, rótulos e rodapé:** Poppins (Regular, Medium, SemiBold, Bold, Italic)
- **Leitura longa (o corpo do texto):** Manrope (Regular, Medium, SemiBold, Bold, ExtraBold)

Omnes Huggies (a face arredondada das capas de cartilha) foi **descartada por
decisão do fundador**. O papel de display ficou com Poppins Bold.

| Nível | pt | Entrelinha | Peso | Observação |
|---|---|---|---|---|
| `capa_titulo` | 46 | 1.05 | 700 | medido 62pt/1.22 e contorno ~0.08em na CARTILHA_04 p1; reduzido a 46pt com ajuste automático de encaixe |
| `capa_subtitulo` | 15 | 1.3 | 600 | medido — pill de 16.4mm × 140.6mm, r 3.9mm, CARTILHA_04 p1; texto virou navy por contraste |
| `capa_assinatura` | 9.5 | 1.45 | 500 |  |
| `h1` | 28 | 1.12 | 700 |  |
| `h2` | 16.5 | 1.25 | 600 |  |
| `h3` | 12.5 | 1.3 | 600 |  |
| `rotulo` | 8.5 | 1.2 | 600 | estrutura do Porto Seguro; cor e caixa vindas das cartilhas |
| `corpo` | 11.5 | 1.52 | 400 | medido: avanço de linha 17.2–18.1pt no card coral da CARTILHA_01 p4 → 11.5pt × 1.52 = 17.5pt |
| `corpo_destaque` | 11.5 | 1.52 | 700 |  |
| `corpo_pequeno` | 10 | 1.5 | 400 |  |
| `nota` | 9.5 | 1.5 | 400 |  |
| `numero_ficha` | 26 | 1 | 700 |  |
| `numero_bloco` | 64 | 1 | 700 |  |
| `rodape` | 7.5 | 1.2 | 500 |  |
| `sumario_item` | 11 | 1.9 | 500 |  |
| `formulario_campo` | 10 | 2.4 | 500 |  |

O corpo de **11.5pt com 17.5pt de entrelinha** não foi inventado: é o avanço de
linha medido no card informativo da CARTILHA_01 p4. O e-book herda o ritmo
vertical do material aprovado.

## Grid

- Página: **A4**, 210 × 297mm
- Margens: topo 22mm, base 20mm, laterais **29mm**
- Largura de conteúdo: **152mm** — medido, idêntico nas 4 cartilhas
- Medida de linha: ~72 caracteres
- Base vertical: **6.2mm** (= 17.5pt, o avanço do corpo). Toda a escala de espaço é múltipla dela: 3.1mm / 6.2mm / 9.3mm / 12.4mm / 18.6mm
- Padding de card: 9.3mm

## Formas

- Raio de card: **8mm** (medido: 8.2mm nas cartilhas)
- Raio de pill: **4mm** (medido: 3.9mm)
- Filete: 1.2mm · fio: 0.35mm
- Faixa em arco do rodapé de capa: 13mm na borda, 26mm no ápice — assinatura gráfica da marca
- Sombra de card: `0 1.5mm 4mm rgba(31,45,61,0.10)`

## Catálogo de blocos

Todo material se monta com estes tipos. Nenhum outro é inventado em runtime.

| Bloco | Diretiva | O que é |
|---|---|---|
| **Capa** | — automático | Capa do material: título, subtítulo curto, marca e supervisão técnica. Ilustração de personagem só quando o material pede. |
| **Carta de abertura** | `:::carta` | Carta em primeira pessoa para quem vai ler, em texto corrido, terminando com assinatura. |
| **Sumário** | — automático | Lista do que o material contém, com número de página real. |
| **Seção conceitual** | — automático | Texto explicativo com título e subtítulos: conceito, mecanismo, contexto técnico. É o bloco genérico de fallback. |
| **Tabela comparativa** | — automático | Duas colunas que contrastam dois conceitos, no padrão 'Birra × Crise'. |
| **Caixa de atenção** | `:::atencao` | Destaque curto de um ponto crítico, ressalva clínica ou aviso que o leitor não pode perder. |
| **Abertura de bloco** | `:::bloco` | Página divisória que abre um bloco de atividades: número, nome e uma frase. |
| **Ficha de atividade** | `:::ficha` | Atividade completa: número e nome, objetivo terapêutico, princípio ABA-TCC, materiais, passo a passo, versão mais fácil e mais desafiadora, e o que observar. |
| **Formulário imprimível** | `:::formulario` | Página para preencher à mão: campos com linhas e opções para marcar. |
| **Dicas práticas** | `:::dicas` | Série de dicas curtas para o adulto, cada uma com título imperativo e um parágrafo. |
| **Roda de conversa** | `:::conversa` | Perguntas numeradas para ler junto com a criança depois da história. |
| **Voz do personagem** | `:::voz` | Fala do personagem do Vale da Harmonia, em tom afetivo, fechando uma ideia. |
| **Encerramento** | `:::encerramento` | Fecho do material: o que observar daqui para frente, quando buscar ajuda, última palavra. |
| **Página final** | — automático | Fundamentação científica literal, disclaimer legal com nome e CRP, e marca. |

A **ficha de atividade** é o bloco mais importante e ocupa uma página inteira:
número + nome, par lado a lado objetivo/princípio, parágrafo de materiais, passo
a passo numerado, par mais fácil/mais desafiador, e o rodapé “o que observar”.
Uma ficha nunca quebra entre páginas.
