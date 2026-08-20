# Extração de dados da tela

Este arquivo trata de **como ler a tela do aparelho**. O que escrever no laudo está em
`base/` (vocabulário e descrição) e em `templates-hospitais.md` (formato e redação).
Não há conteúdo clínico duplicado aqui — de propósito.

## 1. Regra mestra

**A classificação de normalidade é transcrita, nunca calculada.** O aparelho já
comparou este paciente com a base normativa dele. Você copia o resultado.

Ordem de preferência para obter a classificação:

1. **Rótulo em texto** impresso pelo aparelho (`Within Normal Limits`, `Borderline`,
   `Outside Normal Limits`, ou equivalente em português). É a fonte mais confiável —
   cor em stream comprimido de AnyDesk engana.
2. **Cor**, traduzida pela tabela do fabricante em `base/05-aparelhos.md`.
3. Se `base/05-aparelhos.md` estiver `[PREENCHER]` para aquele fabricante e a tela só
   trouxer cor: **`[VERIFICAR]` no campo, e pare.** Não pergunte a convenção ao
   operador de viva-voz — memória de técnico não é fonte, e a própria base chama esse
   dado de "ponto de maior risco de afirmação plausível e errada em todo o guia".
   O desbloqueio é preencher `base/05-aparelhos.md` **a partir do manual do
   equipamento**, uma vez, e isso é tarefa de humano fora da sessão.

Esta ordem é a mesma da regra inviolável 3 do `SKILL.md`, e nenhuma das duas
autoriza deduzir a classificação a partir da cor sem a tabela do fabricante.
Hoje a tabela de `base/05-aparelhos.md` está `[PREENCHER]` para **todos** os
fabricantes: na prática, tela que só traz cor vira `[VERIFICAR]`.

**Nunca escreva percentil no laudo.** O laudo diz "dentro" / "fora" / "limítrofe" —
nunca "p < 1%".

Mapeamento para o campo do JSON:

**Lateralidade:** `OD`/`RE`/`Right` → `OD`. `OS`/`LE`/`Left` → `OE`. Os dois exames
presentes → `olhos: "AO"`, **mesmo que um dos olhos saia como não avaliável** — `olhos`
diz o que foi examinado, não o que foi conclusivo.

| O que o aparelho diz | `rel_classificacao` / `cfn_classificacao` |
|---|---|
| dentro dos limites normais | `dentro` |
| limítrofe / borderline | `limitrofe` |
| fora dos limites normais | `fora` |

## 2. Campos a extrair — nervo óptico

| Campo do JSON | Rótulos comuns na tela |
|---|---|
| `area_papila` | `Disc Area`, `Área do Disco`, `Optic Disc Area` |
| `rel_esc_papila` | `Cup/Disc Area Ratio`, `C/D Area Ratio`, `Relação E/P (área)` |
| `escavacao_v` / `escavacao_h` | `Vertical/Horizontal Cup`, `Escavação V/H`, `Vertical C/D` + `Horizontal C/D` |
| `cfn_media` | `RNFL Thickness Average`, `Espessura média da CFNR`, `CFN Média` |

Formato de saída: ver a tabela de estilo em `templates-hospitais.md`. Resumo:
papila com `mm2`, CFN **sem unidade**, escavação como razão `v (v) x h (h)`, vírgula
decimal.

## 3. Campos a extrair — mácula

Um bloco de texto por camada, por olho: `interface_vitreo_retiniana`,
`camadas_internas`, `epr_cfr`. O vocabulário e as frases estão em `base/03-macula.md`.
Se a tela mostrar espessura central ou mapa ETDRS e o achado justificar citá-los,
transcreva com dupla leitura, como qualquer número.

## 4. Dupla leitura — obrigatória para todo número

1. `shot --roi` cercando a tabela, com ~10 px de folga.
2. Anote os valores.
3. `shot --roi` **de novo, com enquadramento diferente** — mais largo, ou dividido em
   duas metades. Leia sem consultar a primeira anotação.
4. Bateram → valor confirmado. Divergiram ou algum ilegível → `[VERIFICAR]` no valor
   e o motivo no campo de classificação.

Fonte pequena demais: aumente o zoom **dentro do sistema remoto** e recapture. Nunca
"amplie mentalmente" um dígito borrado.

## 5. Armadilhas — cada uma já custou laudo errado

1. **Ordem das colunas.** Não presuma que a esquerda é OD. Leia o cabeçalho
   (`OD`/`OS`/`RE`/`LE`/`Right`/`Left`) **na mesma captura** em que lê os valores.
   Alguns aparelhos exibem OS à esquerda para espelhar a visão do examinador.
2. **Vírgula e ponto.** Os **dígitos** são transcritos exatamente; o **separador segue
   o estilo da casa, que é vírgula**. Aparelho em inglês mostra `1.95` → no laudo vai
   `1,95`. O que nunca pode acontecer é perder o separador: `2.04` e `2,04` são o mesmo
   número, `204` não é. Não acrescente nem remova casas decimais.
3. **Dígito comprimido.** `0.62` ↔ `0.82`, `78` ↔ `76`, `8` ↔ `6`, `1` ↔ `7`. É a
   razão da dupla leitura existir.
4. **Qualidade do sinal.** Vai no campo `qualidade` do olho, que é registrado no
   `extracao.json` e **não é impresso no corpo do laudo** — o corpo é a lista de 4
   parâmetros (nervo) ou as 3 camadas (mácula). Se o exame estiver limitado, aí sim
   a limitação entra em `observacoes`, como prosa.
   **Não existe limiar mínimo de sinal definido nesta skill** (`base/07-lacunas.md`).
   Índice baixo, por si só, não reprova o exame. O que reprova é o **aparelho
   sinalizar** qualidade insuficiente, ou haver **artefato na área de interesse** —
   aí a estrutura afetada é "não avaliável", nunca "normal".

8. **Estrutura fora da captura.** Camada que a captura não cobriu não é "normal" nem
   "não avaliável": é `[RECAPTURAR]`. Volte e capture o corte completo. Em produção
   isso quase não acontece (você vê o corte inteiro); acontece quando o enquadramento
   do ROI foi curto. `[RECAPTURAR]` e `[VERIFICAR]` são coisas diferentes e o laudo
   os distingue no banner.
5. **Erro de segmentação.** Linha de delimitação visivelmente fora da anatomia
   invalida os números derivados dela. `base/04-artefatos.md` tem o catálogo e as
   frases de exame limitado.
6. **Paciente e data.** Confira nome, data e olho na mesma captura dos valores — não
   numa captura anterior.
7. **Fabricante diferente entre exames.** Medidas de CFNR não são comparáveis entre
   plataformas (`base/05-aparelhos.md`). Não calcule variação evolutiva nesse caso.

## 6. Quando escalar para a auditoria sênior

Isole o recorte e abra o subagente de Oftalmologista Sênior quando houver artefato ou
erro de segmentação na área de interesse, achado que você não consiga nomear com o
vocabulário de `base/`, ou elevação retiniana cujo plano de separação não seja
determinável.

- Sênior firmou → siga com a redação dele.
- Sênior não firmou → `[VERIFICAR]` e `_PENDENTES/`.
- **Não foi possível abrir o subagente** (sem suporte a subagente na sessão, erro,
  ambiente de teste) → **não decida sozinho no lugar dele**. Trate como se ele não
  tivesse firmado: `[VERIFICAR]`, `_PENDENTES/`, e **diga no relatório final que a
  escalada não pôde ser feita**. Pular a escalada em silêncio é o pior desfecho.
