# Base científica para laudos de OCT — mácula e nervo óptico

```
VERSÃO: 1.0-rascunho
DATA: 20/08/2026
REVISADO POR: PENDENTE — não colocar em produção antes da revisão
```

> **Estado deste arquivo.** Todo conteúdo clínico abaixo foi extraído de duas obras
> (ver `## Referências`). As frases de laudo são composição minha, em registro
> neutro, e **não** foram calibradas contra laudos reais da clínica. Os campos
> marcados `[PREENCHER]` são lacunas reais das fontes — não devem ser completados
> por inferência. Trocar o campo `REVISADO POR` só depois da revisão assinada.

## Índice

1. [Vocabulário descritivo](#vocabulário-descritivo)
2. [Nervo óptico — estruturas e parâmetros](#nervo-óptico--estruturas-e-parâmetros)
3. [Mácula — camadas e achados](#mácula--camadas-e-achados)
4. [Artefatos e limitações de aquisição](#artefatos-e-limitações-de-aquisição)
5. [Diferenças entre aparelhos](#diferenças-entre-aparelhos)
6. [Referências](#referências)

Convenção de fonte: cada afirmação clínica leva uma etiqueta curta — `[BCSC-12 2022]`,
`[Atlas 2024]`, `[IN·OCT 2014]`, `[IVTS 2013]` etc. — expandida na seção 6.

---

## Vocabulário descritivo

Esta seção define o registro. As seções 2 e 3 trazem a frase pronta de cada achado.

### Regras de registro

- Voz impessoal, tempo presente: "observa-se", "identifica-se", "nota-se". Nunca
  primeira pessoa.
- O laudo de OCT **descreve morfologia**. Não conclui etiologia, não gradua função
  visual, não indica conduta.
- Achado ausente escreve-se como ausência explícita, não como silêncio:
  "sem fluido intrarretiniano ou sub-retiniano identificável".
- Estrutura não avaliável **nunca** vira estrutura normal. Escrever
  "não avaliável neste exame por [motivo]".
- Medida sempre acompanhada de unidade, protocolo e aparelho.
- Lateralidade em toda descrição (OD / OE).

### Léxico de refletividade

Usar exclusivamente estes termos; não usar "branco", "escuro", "brilhante":

| Termo | Uso |
|---|---|
| hiper-refletivo | sinal acima do tecido de referência adjacente |
| hiporrefletivo | sinal abaixo do tecido de referência adjacente |
| isorrefletivo | sinal equivalente ao tecido de referência |
| sombreamento (posterior) | atenuação do sinal abaixo de estrutura que bloqueia a luz |
| hipertransmissão | aumento do sinal abaixo do EPR por perda das estruturas absorventes `[Atlas 2024]` |
| bloqueio de sinal | interrupção da penetração da luz por lesão sobrejacente `[Atlas 2024]` |

### Léxico de topografia

- Eixo antero-posterior: **interno / externo** (não "superficial / profundo" para camadas).
- Plano do corte: **horizontal / vertical**, **superior / inferior**, **nasal / temporal**.
- Referência ao centro: **subfoveal**, **foveal**, **parafoveal**, **perifoveal**,
  **peripapilar**.
- Extensão: **focal**, **multifocal**, **difuso**, **setorial**.
- Contorno: **regular**, **irregular**, **ondulado**, **corrugado**, **em cúpula**,
  **abrupto**.

### Esqueletos de frase

Preencher os colchetes; manter a ordem dos elementos.

- Achado presente:
  `Observa-se [achado] [localização], [qualificador de extensão].`
- Achado com medida:
  `Identifica-se [achado] medindo [valor] µm em [eixo/protocolo].`
- Integridade preservada:
  `[Estrutura] contínua/preservada em toda a extensão do corte.`
- Integridade perdida:
  `Observa-se [interrupção/atenuação/perda] de [estrutura] em região [localização].`
- Estrutura não avaliável:
  `[Estrutura] não avaliável neste exame em razão de [motivo].`
- Comparação evolutiva (só com mesmo aparelho e mesmo protocolo):
  `Em comparação ao exame de [data], realizado no mesmo equipamento e protocolo,
  observa-se [redução/aumento/estabilidade] de [achado].`

### Fechamento padrão

O laudo termina em correlação, nunca em conduta.

- `Achados a serem correlacionados com o quadro clínico e demais exames complementares.`
- `Sugere-se correlação clínica e acompanhamento evolutivo com o mesmo equipamento e protocolo.`
- Quando houver limitação técnica:
  `Exame com limitação técnica conforme descrito; sugere-se repetição para adequada avaliação de [estrutura].`

---

## Nervo óptico — estruturas e parâmetros

> **Advertência de escopo.** As duas fontes deste guia são obras de retina e vítreo.
> Elas cobrem a **aquisição** e as **definições estruturais** do nervo óptico, mas
> **não** trazem valores de referência para área de disco, área de rima, volume de
> escavação ou relação escavação/disco, nem faixas percentílicas de CFNR. Este guia,
> por decisão de projeto e por limitação das fontes, **não** contém regra de corte —
> a comparação normativa é a da base do próprio aparelho.

### Anatomia no corte

- **Cabeça do nervo óptico (CNO):** região de convergência dos axônios das células
  ganglionares. No B-scan, descrever margem do disco, contorno da superfície e
  presença ou ausência de elevação. `[Atlas 2024]`
- **CFNR (camada de fibras nervosas da retina):** medida como a distância entre a
  membrana limitante interna e a face externa da camada de fibras nervosas. `[Atlas 2024]`
- **CCG / complexo de células ganglionares:** soma de três camadas internas — camada
  de fibras nervosas, camada de células ganglionares e camada plexiforme interna. A
  varredura deve estar centrada na fóvea, e o resultado é apresentado como mapa
  codificado por cores contra base normativa do fabricante. `[Atlas 2024]`
- **Membrana de Bruch e sua abertura:** referência anatômica para delimitação da
  margem do disco nos algoritmos de volume. `[Atlas 2024]`

### Protocolos de aquisição

- **Volume scan** — conjunto volumétrico centrado na CNO. Delimita a margem e o
  contorno da superfície do disco e é segmentado para obter os limites da camada de
  fibras nervosas. `[Atlas 2024]`
- **Line scan** — B-scans isolados ou em série, de alta resolução, para estrutura e
  anomalias anatômicas da cabeça do nervo. `[Atlas 2024]`
- **OCTA de disco** — avalia vasculatura do disco e densidade vascular peripapilar. `[Atlas 2024]`

### Parâmetros calculados pelos aparelhos

Os equipamentos SD-OCT calculam diâmetro, área, escavação e rima do nervo óptico. Cada
medida varia com **idade** e **etnia**. `[Atlas 2024; Cavallotti 2002; Girkin 2008]`

Dado populacional disponível: espessura média de CFNR de **100,1 µm** em população
normal; CFNR mais fina em idades mais avançadas; caucasianos com CFNR discretamente
mais fina que hispânicos e asiáticos; áreas de disco menores associadas a CFNR mais
fina. `[Budenz 2007, via Atlas 2024]`

Este número é **descritivo populacional**, não limiar de decisão. Não usar para
classificar um exame individual.

### Como reportar — e o que não afirmar

**Reportar:**
- O valor numérico exato, com unidade, setor e protocolo.
- A classificação de cor **exatamente como o aparelho a apresenta**, nomeando o
  fabricante e a base normativa.
- A morfologia observada no corte: contorno do disco, continuidade do perfil de CFNR,
  simetria entre olhos.

**Não afirmar:**
- Que uma relação escavação/disco é normal ou alterada por critério próprio.
- Que um valor de CFNR é normal, limítrofe ou alterado por critério próprio.
- Diagnóstico de glaucoma ou de neuropatia óptica. OCT estrutural não fecha esse
  diagnóstico sem clínica, pressão intraocular e campo visual.
- Progressão a partir de exames de fabricantes diferentes (ver seção 5).

### Frases prontas — nervo óptico

- Sem alteração estrutural:
  `Margem do disco delimitável em toda a circunferência. Contorno da superfície regular. Perfil de espessura da camada de fibras nervosas peripapilar contínuo, sem defeito setorial identificável. Análise normativa do equipamento sem setores sinalizados.`
- Defeito setorial:
  `Observa-se redução setorial da espessura da camada de fibras nervosas peripapilar em quadrante [superior/inferior/nasal/temporal] do [OD/OE], sinalizada como [cor] pela base normativa do equipamento [fabricante].`
- Assimetria:
  `Nota-se assimetria da espessura da camada de fibras nervosas peripapilar entre os olhos, com valores médios de [X] µm no OD e [Y] µm no OE, no mesmo equipamento e protocolo.`
- CCG:
  `Mapa de complexo de células ganglionares centrado na fóvea, com [ausência de setores sinalizados / setor(es) [localização] sinalizado(s) como [cor]] pela base normativa do equipamento.`
- Elevação de disco:
  `Observa-se elevação do contorno da superfície do disco óptico, com [presença/ausência] de fluido peripapilar associado.`
- Fibras de mielina — achado que simula espessamento:
  `Observa-se hiper-refletividade acentuada da camada retiniana superficial com sombreamento posterior proporcional à sua espessura, sem afinamento retiniano associado, compatível com fibras de mielina.` `[Atlas 2024]`
- Reserva obrigatória quando houver setor sinalizado:
  `Os achados estruturais isoladamente não estabelecem diagnóstico; sugere-se correlação com quadro clínico, pressão intraocular e campo visual.`

---

## Mácula — camadas e achados

### Sequência de camadas em OCT

Nomenclatura do consenso internacional, da interna para a externa, seguindo o trajeto
da luz incidente `[IN·OCT 2014, via BCSC-12 2022]`:

1. MLI — membrana limitante interna
2. CFN — camada de fibras nervosas
3. CCG — camada de células ganglionares
4. CPI — camada plexiforme interna
5. CNI — camada nuclear interna
6. CPE — camada plexiforme externa (camada de fibras de Henle na região parafoveal)
7. CNE — camada nuclear externa
8. MLE — membrana limitante externa
9. ZE — zona elipsoide
10. EPR — epitélio pigmentar da retina
11. Coroide

Estruturas adjacentes com nome próprio: membrana de Bruch, coriocapilar, camada de
Sattler (vasos médios), camada de Haller (vasos calibrosos), interface coroide-esclera.

### Topografia macular

| Estrutura | Dimensão | Fonte |
|---|---|---|
| Mácula (polo posterior) | 5,5 mm de diâmetro | `[BCSC-12 2022]` |
| Fóvea | 1,5 mm (≈ 1 diâmetro de disco) | `[BCSC-12 2022]` |
| Fovéola | 0,35 mm | `[BCSC-12 2022]` |
| Umbo | 150–200 µm | `[BCSC-12 2022]` |
| Zona avascular foveal | 250–600 µm ou mais | `[BCSC-12 2022]` |
| Parafóvea | anel de 0,5 mm ao redor da fóvea | `[BCSC-12 2022]` |
| Perifóvea | anel de 1,5 mm ao redor da parafóvea | `[BCSC-12 2022]` |

Na parafóvea, CCG, CNI e CPE são as camadas mais espessas — é o ponto de maior
espessura retiniana. `[BCSC-12 2022]`

Valores descritivos de referência, **não** limiares: espessura foveal central média em
SD-OCT de 225,1 ± 17,1 µm, com variação por idade e estado retiniano `[Atlas 2024]`;
resolução axial típica de 5–7 µm `[BCSC-12 2022]`; coroide subfoveal de
aproximadamente 287 µm em voluntários sadios com média de 50 anos, afinando com idade
e miopia `[BCSC-12 2022]`.

### Interface vítreo-retiniana

Achados **fisiológicos** que não devem ser descritos como doença `[Atlas 2024]`:
vítreo cortical posterior (hialoide posterior), espaço retro-hialoideo após
descolamento do vítreo posterior, bursa pré-macular (espaço líquido sobre a mácula por
liquefação vítrea), e aderência vitreomacular sem distorção do contorno.

| Achado | Como identificar | Frase pronta |
|---|---|---|
| **Aderência vitreomacular** | Hialoide aderida à mácula com perfil foveal preservado; focal ≤ 1500 µm, ampla > 1500 µm `[IVTS 2013]` | `Observa-se aderência vitreomacular [focal/ampla], sem distorção do contorno foveal.` |
| **Tração vitreomacular** | Aderência focal com **disrupção do contorno macular** sob inserção vítrea `[Atlas 2024]` | `Observa-se tração vitreomacular [focal/ampla], com distorção do contorno foveal [e espaços císticos associados].` |
| **Membrana epirretiniana** | Membrana hiper-refletiva espessada sobre a superfície interna, contorno corrugado ou ondulado `[Atlas 2024]` | `Observa-se membrana epirretiniana hiper-refletiva sobre a superfície interna da mácula, com [contorno corrugado / estrias da limitante interna / espessamento retiniano associado].` |
| **Buraco macular de espessura total** | Defeito de espessura total; medir a **largura mínima do orifício no ponto mais estreito da retina média** `[Atlas 2024; IVTS 2013]` | `Observa-se defeito retiniano de espessura total, medindo [X] µm em sua largura mínima, [com/sem] tração vitreomacular associada.` |
| **Buraco macular lamelar** | Contorno foveal irregular, defeito da fóvea interna, separação entre camadas internas e externas, **sem** defeito de espessura total `[Witkin 2006, via Atlas 2024]` | `Observa-se contorno foveal irregular com defeito da fóvea interna e separação entre camadas retinianas internas e externas, sem defeito de espessura total.` |
| **DVP, estágios 1–4** | 1: perifoveal com aderência vitreofoveal intacta; 2: macular isolado com aderência vitreopapilar; 3: periférico com aderência vitreopapilar; 4: completo, cavidade vítrea homogênea e hiporrefletiva `[Johnson 2005, via Atlas 2024]` | `Hialoide posterior [descolada da região macular com aderência vitreopapilar residual / completamente descolada], compatível com descolamento do vítreo posterior estágio [N].` |

**Nota sobre as medidas do IVTS.** Os estratos de 250 µm e 400 µm são **definições
dimensionais** consagradas que determinam a terminologia descritiva ("pequeno",
"médio", "grande"), não comparação normativa. São diferentes em natureza de uma regra
do tipo "E/P > 0,6 = anormal", e por isso permanecem no guia. Se a revisão preferir
apenas o valor medido sem o adjetivo, é só suprimir a coluna de estrato.

### Camadas internas

| Achado | Como identificar | Frase pronta |
|---|---|---|
| **Fluido intrarretiniano** | Espaços císticos hiporrefletivos na neurorretina | `Observa-se fluido intrarretiniano em [localização], sob a forma de espaços císticos hiporrefletivos.` |
| **Edema macular cístico** | Espessamento macular com cistos amplos predominantemente na CPE, podendo envolver CPI e nucleares; casos graves com extravasamento para o espaço sub-retiniano `[Atlas 2024]` | `Observa-se espessamento macular com espaços císticos hiporrefletivos, predominantemente na camada plexiforme externa.` |
| **Focos hiper-refletivos intrarretinianos** | Pontos hiper-refletivos na retina; correspondem a migração pigmentar `[Atlas 2024]` | `Notam-se focos hiper-refletivos intrarretinianos em [localização].` |
| **Exsudatos duros** | Aglomerados hiper-refletivos intrarretinianos com sombreamento `[Atlas 2024]` | `Observam-se aglomerados hiper-refletivos intrarretinianos com sombreamento posterior.` |
| **Hiper-refletividade e espessamento das camadas internas** | Padrão isquêmico agudo, com sombreamento das camadas externas `[Atlas 2024]` | `Observa-se hiper-refletividade e espessamento das camadas retinianas internas em [setor], com sombreamento das camadas externas subjacentes.` |
| **Hiper-refletividade da camada nuclear interna (PAMM)** | Banda hiper-refletiva no nível da CNI `[Atlas 2024]` | `Observa-se banda hiper-refletiva no nível da camada nuclear interna.` |
| **Atrofia das camadas internas** | Afinamento das camadas internas e da CFN com preservação de CNE e complexo fotorreceptor/EPR `[Atlas 2024]` | `Observa-se afinamento das camadas retinianas internas com preservação da camada nuclear externa e do complexo fotorreceptor/epitélio pigmentar.` |
| **Esquise retiniana** | Separação **dentro** da retina, sempre restando camadas externas sobre o EPR; traves conectantes `[Atlas 2024]` | `Observa-se separação intrarretiniana entre camadas internas e externas, com traves conectantes, permanecendo camadas retinianas externas sobre o epitélio pigmentar.` |

### Retina externa, EPR e membrana de Bruch

| Achado | Como identificar | Frase pronta |
|---|---|---|
| **Interrupção da zona elipsoide** | Descontinuidade, atenuação ou perda focal da ZE `[Atlas 2024]` | `Observa-se [interrupção/atenuação] da zona elipsoide em região [localização].` |
| **Interrupção da MLE** | Perda da continuidade da linha da MLE `[Atlas 2024]` | `Observa-se descontinuidade da membrana limitante externa em [localização].` |
| **Fluido sub-retiniano** | Espaço hiporrefletivo homogêneo entre neurorretina e EPR `[Atlas 2024]` | `Observa-se fluido sub-retiniano em [localização], sob a forma de espaço hiporrefletivo homogêneo.` |
| **Descolamento seroso da neurorretina** | Elevação da neurorretina, EPR aderido e de contorno liso `[Atlas 2024]` | `Observa-se descolamento seroso da retina neurossensorial, com epitélio pigmentar aderido e de contorno regular.` |
| **Drusas** | Elevações nodulares sub-EPR com ausência notável de fluido; pequenas < 63 µm, intermediárias 63–124 µm, grandes ≥ 125 µm; duras, moles ou confluentes `[BCSC-12 2022]` | `Observam-se elevações nodulares sub-epiteliais [esparsas/confluentes], sem fluido intrarretiniano ou sub-retiniano associado.` |
| **Pseudodrusas reticulares / SDD** | Depósitos **acima** do EPR, abaixo da ZE, em arranjo reticular, aspecto em pico ou ondulado `[BCSC-12 2022]` | `Observam-se depósitos drusenoides sub-retinianos, situados acima do epitélio pigmentar.` |
| **DEP seroso** | Elevação abrupta do EPR, em cúpula, refletividade interna vazia, tipicamente sem fluido associado `[BCSC-12 2022]` | `Observa-se descolamento do epitélio pigmentar de aspecto seroso, com elevação abrupta em cúpula e conteúdo interno hiporrefletivo.` |
| **DEP fibrovascular** | Elevação com material hiper-refletivo rendilhado ou polipoide na face inferior do EPR; formas crônicas com aspecto multilaminado `[BCSC-12 2022]` | `Observa-se descolamento do epitélio pigmentar com material hiper-refletivo irregular em sua face inferior.` |
| **DEP drusenoide** | Coalescência de drusas grandes confluentes, diâmetro > 350 µm `[BCSC-12 2022]` | `Observa-se elevação do epitélio pigmentar por coalescência de drusas confluentes.` |
| **Material hiper-refletivo sub-retiniano (SHRM)** | Material hiper-refletivo entre retina e EPR `[BCSC-12 2022]` | `Observa-se material hiper-refletivo sub-retiniano em [localização].` |
| **Hemorragia sub-retiniana** | Material hiper-refletivo sob a neurorretina com sombreamento posterior `[Atlas 2024]` | `Observa-se material hiper-refletivo sub-retiniano com sombreamento posterior.` |
| **Hipertransmissão coroidea** | Aumento do sinal abaixo do nível do EPR `[Atlas 2024]` | `Nota-se hipertransmissão do sinal para a coroide subjacente, em extensão aproximada de [X] µm.` |
| **Atrofia do EPR e da retina externa** | Perda de CNE, MLE, ZE, fotorreceptores, EPR e coriocapilar, com hipertransmissão; subsidência de CNI e CPE `[Atlas 2024; Sadda 2018; Guymer 2020]` | `Observa-se perda das camadas retinianas externas e do epitélio pigmentar em região [localização], com hipertransmissão do sinal para a coroide e subsidência das camadas nucleares e plexiforme.` |
| **Tubulação retiniana externa** | Estruturas ovoides/circulares hiporrefletivas com **bordas hiper-refletivas**, na CNE; rearranjo de fotorreceptores degenerados `[BCSC-12 2022]` | `Observam-se estruturas ovoides hiporrefletivas com bordas hiper-refletivas na camada nuclear externa, compatíveis com tubulação retiniana externa.` |
| **Rotura do EPR** | Tecido hiper-refletivo enrolado sob a neurorretina, adjacente a área de perda completa do EPR `[Atlas 2024]` | `Observa-se tecido hiper-refletivo enrolado sob a retina neurossensorial, adjacente a área de ausência do epitélio pigmentar.` |
| **Sinal de dupla camada** | DEP raso e irregular `[BCSC-12 2022]` | `Observa-se elevação rasa e irregular do epitélio pigmentar (sinal de dupla camada).` |

**Duas armadilhas que as próprias fontes registram** — descrever a morfologia, sem
nomear o mecanismo:

- Tubulação retiniana externa **pode ser confundida com fluido exsudativo** `[BCSC-12 2022]`.
  As bordas hiper-refletivas e a localização na CNE são o discriminante.
- Sinal de dupla camada **pode ser confundido com drusas confluentes ou DEP
  drusenoide** `[BCSC-12 2022]`.

### Coroide

- Dividida em coriocapilar, camada de Sattler (vasos menores) e camada de Haller
  (vasos calibrosos). `[Atlas 2024]`
- EDI aproxima a linha de atraso zero da coroide e permite melhor visualização da
  interface coroide-esclera e medida mais precisa da espessura. `[Atlas 2024]`
- Estudos de espessura coroidal em normais e em doentes mostram **ampla variação** de
  medidas. `[Fujiwara 2012; Margolis & Spaide 2009, via Atlas 2024]` Descrever como
  qualitativo (espessada / afinada / compatível com a faixa etária), com o valor entre
  parênteses.
- Frase pronta: `Coroide com espessura subfoveal de [X] µm ao modo EDI, com interface coroide-esclera [identificável/não identificável].`

### Elevação retiniana — discriminante obrigatório

Antes de nomear qualquer elevação, aplicar o critério de plano de separação `[Atlas 2024]`:

- **Esquise:** separação **dentro** da retina, entre camadas internas e externas,
  **sempre restando camadas externas sobre o EPR**.
- **Descolamento:** plano de separação **entre o EPR e a retina neurossensorial**.

Se o plano não for determinável com segurança, descrever como
`elevação retiniana cujo plano de separação não é determinável neste corte` e não
escolher entre os dois termos.

---

## Artefatos e limitações de aquisição

Fonte de toda esta seção: `[Atlas 2024, cap. 5.1 e 5.2]`.

### Catálogo — OCT estrutural

| Artefato | Como reconhecer | Causa |
|---|---|---|
| **Artefato de espelho** | Imagem invertida; ocorre só em SD-OCT | Área de interesse cruza a linha de atraso zero: aparelho muito próximo ao olho, ou curvatura retiniana em retinosquise, descolamento, lesão coroidea elevada, alta miopia |
| **Vinhetagem** | Perda de sinal em um dos lados da imagem | Íris bloqueia parte do feixe |
| **Descentralização (misalignment)** | Fóvea não centrada no volume | Fixação ruim do paciente ou posicionamento incorreto do alvo pelo operador. A grade ETDRS geralmente pode ser reposicionada para obter medida acurada |
| **Falha de segmentação (software breakdown)** | Linhas de segmentação traçadas fora dos limites reais | Doença da interface vitreomacular quebra a linha interna; doença da retina externa e do EPR quebra a linha externa |
| **Artefato de piscada** | Barras horizontais pretas ou brancas; perda de dados | Piscada durante a aquisição |
| **Artefato de movimento** | Distorção, duplo escaneamento, vasos desalinhados, fóvea duplicada | Movimento ocular durante a aquisição; menos frequente com rastreamento ocular atual |
| **Erro de fora de faixa** | Porção do corte cortada, tipicamente retina externa e coroide | B-scan não centrado na tela de pré-visualização |
| **Bloqueio / sombreamento** | Perda focal de sinal | Catarata, opacidade corneana, inflamação, hemorragia vítrea, flutuadores, hemorragia intra ou sub-retiniana, DEP, drusas grandes |

### Catálogo — OCTA

Artefatos são muito frequentes em OCTA e sua identificação é indispensável para a
interpretação: bloqueio; linhas brancas por movimento transversal; fluxo falso-positivo
por pulsação arterial; defeito em colcha (*quilting*) por sacadas múltiplas; fluxo
falso-negativo por fluxo abaixo do limiar de detecção; artefato de projeção (vasos
superficiais aparecendo em planos profundos); duplicação de vasos; erro de segmentação
por DEP ou edema; sombreamento na coriocapilar; artefatos específicos de campo amplo.

### Sinal fraco

O Atlas usa a intensidade de sinal como indicador de qualidade e de atividade
inflamatória — cita um exame com sinal 4/10 por inflamação vítrea difusa, evoluindo
para 6/10 após tratamento. **Nenhuma das fontes estabelece um valor mínimo aceitável
de intensidade de sinal.** `[PREENCHER]` — definir o limiar interno de aceitação por
aparelho, junto com a revisão clínica, e registrar aqui.

### Frases prontas — exame limitado

- Sinal fraco:
  `Exame realizado com intensidade de sinal reduzida ([valor], equipamento [fabricante]), com prejuízo da resolução das camadas [externas/internas].`
- Opacidade de meios:
  `Observa-se atenuação difusa do sinal por opacidade de meios, com limitação da avaliação de [estrutura].`
- Falha de segmentação:
  `As linhas de segmentação automática apresentam-se incorretamente traçadas em razão de [alteração]; os valores quantitativos de espessura não devem ser considerados neste exame.`
- Descentralização:
  `Volume adquirido com descentralização em relação à fóvea; os valores por subcampo devem ser interpretados com reserva.`
- Movimento / piscada:
  `Exame com artefato de [movimento/piscada], resultando em [distorção/perda de dados] em região [localização].`
- Artefato de espelho:
  `Observa-se inversão de segmento da imagem por cruzamento da linha de atraso zero, sem correspondência anatômica real.`
- Fecho para exame limitado:
  `Exame com limitação técnica conforme descrito; sugere-se repetição para adequada avaliação de [estrutura].`

**Regra dura:** com qualquer artefato acima presente na área de interesse, o laudo não
afirma normalidade da estrutura afetada. Escreve "não avaliável".

---

## Diferenças entre aparelhos

### O que está documentado nas fontes

Geometria de amostragem peripapilar `[Atlas 2024]`:

| Fabricante / equipamento | Padrão de amostragem |
|---|---|
| Zeiss — Cirrus HD-OCT | Identifica o centro do disco e cria um círculo de **3,46 mm** nessa localização |
| Heidelberg — Spectralis | Volume cilíndrico de **3,4 mm** de diâmetro através e ao redor da cabeça do nervo |
| Optovue — RTVue | Grade com varreduras circulares e radiais, volume de **4 mm × 4 mm** |

**Regra de não-comparabilidade.** Como os aparelhos usam círculos de diâmetros
diferentes ao redor do centro da CNO, **as medidas de CFNR não são comparáveis entre
máquinas** `[Atlas 2024]`. O laudo nunca calcula variação evolutiva entre exames de
fabricantes distintos; nesse caso escreve:
`Exame prévio realizado em equipamento de fabricante distinto; medidas não comparáveis entre plataformas, não sendo possível quantificar variação.`

Tecnologias e implicação prática `[BCSC-12 2022]`:

- **SD-OCT** — melhor resolução axial, menor custo. A coroide é bem avaliada com EDI.
- **SS-OCT** — aquisição geralmente mais rápida, faixas de varredura mais amplas,
  melhor imagem simultânea de vítreo a coroide, melhor penetração através de opacidades.
- **TD-OCT** — tecnologia anterior, amplamente substituída na prática clínica.
- O artefato de espelho ocorre **apenas em SD-OCT** `[Atlas 2024]`.

### Campos a preencher — não inferir

As duas fontes deste guia **não** contêm nomes comerciais de parâmetros, unidades nem
convenção de cor por fabricante. Topcon e Nidek **não aparecem** em nenhuma das obras.
Preencher a tabela abaixo a partir do manual de cada equipamento e da tela de saída
real, não de memória.

| Fabricante | Nome do relatório de nervo | Nome do relatório de mácula | Parâmetros e unidades | Convenção de cor | Base normativa |
|---|---|---|---|---|---|
| Zeiss (Cirrus) | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |
| Heidelberg (Spectralis) | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |
| Topcon | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |
| Nidek | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` | `[PREENCHER]` |

Campos mínimos a levantar por aparelho:

- Nome exato do relatório impresso (é o que a skill vai ler na imagem).
- Nome de cada parâmetro como aparece na tela, em português e em inglês.
- Unidade de cada parâmetro e casas decimais exibidas.
- Significado de cada faixa de cor e o percentil correspondente, **conforme o manual**.
- Nome e composição da base normativa (faixa etária, etnias incluídas).
- Índice de qualidade: nome, escala e valor mínimo recomendado pelo fabricante.
- Diâmetro do círculo peripapilar, se diferir do que está tabelado acima.

> Este é o ponto de maior risco de afirmação plausível e errada em todo o guia. Nome de
> parâmetro e percentil de cor são exatamente o tipo de detalhe que um modelo preenche
> com fluência e sem base. Deixar `[PREENCHER]` é a conduta correta até alguém conferir
> na tela.

---

## Referências

Todas as afirmações clínicas deste guia derivam das duas obras primárias abaixo. As
demais entradas são referências citadas **dentro** dessas obras, listadas para permitir
rastrear a origem de cada dado.

**Obras-fonte**

- `[BCSC-12 2022]` American Academy of Ophthalmology. *Basic and Clinical Science
  Course, Section 12: Retina and Vitreous*, 2022–2023.
- `[Atlas 2024]` Desai SJ, Goldman DR, Waheed NK, Duker JS. *Atlas of Retinal OCT:
  Optical Coherence Tomography*, 2ª ed. Elsevier, 2024.

**Referências primárias citadas nas obras-fonte**

- `[IN·OCT 2014]` Staurenghi G, Sadda S, Chakravarthy U, Spaide RF; International
  Nomenclature for OCT Panel. Proposed lexicon for anatomic landmarks in normal
  posterior segment spectral-domain OCT. *Ophthalmology.* 2014;121(8):1572–1578.
- `[IVTS 2013]` Duker JS, Kaiser PK, Binder S, et al. The International Vitreomacular
  Traction Study Group classification of vitreomacular adhesion, traction, and macular
  hole. *Ophthalmology.* 2013;120(12):2611–2619.
- `[Budenz 2007]` Budenz DL, Anderson DR, Varma R, et al. Determinants of normal
  retinal nerve fiber layer thickness measured by Stratus OCT. *Ophthalmology.*
  2007;114(6):1046–1052.
- `[Johnson 2005]` Johnson MW. Perifoveal vitreous detachment and its macular
  complications. *Trans Am Ophthalmol Soc.* 2005;103:537–567.
- `[Witkin 2006]` Witkin AJ, Ko TH, Fujimoto JG, et al. Redefining lamellar holes and
  the vitreomacular interface. *Ophthalmology.* 2006;113(3):388–397.
- `[Sadda 2018]` Sadda SR, Guymer R, Holz FG, et al. Consensus definition for atrophy
  associated with age-related macular degeneration on OCT: Classification of Atrophy
  Report 3. *Ophthalmology.* 2018;125(4):537–548.
- `[Guymer 2020]` Guymer RH, Rosenfeld PJ, Curcio CA, et al. Incomplete retinal pigment
  epithelial and outer retinal atrophy in age-related macular degeneration:
  Classification of Atrophy Meeting Report 4. *Ophthalmology.* 2020;127:394–409.
- `[Marmor 2016]` Marmor MF, Kellner U, Lai TYY, Melles RB, Mieler WF; American Academy
  of Ophthalmology. Recommendations on screening for chloroquine and hydroxychloroquine
  retinopathy. *Ophthalmology.* 2016;123(6):1386–1394.
- `[Mrejen 2013]` Mrejen S, Sarraf D, Mukkamala SK, Freund KB. Multimodal imaging of
  pigment epithelial detachment: a guide to evaluation. *Retina.* 2013;33(9):1735–1762.
- `[Margolis & Spaide 2009]` Margolis R, Spaide RF. A pilot study of enhanced depth
  imaging OCT of the choroid in normal eyes. *Am J Ophthalmol.* 2009;147(5):811–815.
- `[Fujiwara 2012]` Fujiwara A, Shiragami C, Shirakata Y, et al. EDI spectral-domain OCT
  of subfoveal choroidal thickness in normal Japanese eyes. *Jpn J Ophthalmol.*
  2012;56(3):230–235.
- `[Cavallotti 2002]` Cavallotti C, Pacella E, Pescosolido N, et al. Age-related changes
  in the human optic nerve. *Can J Ophthalmol.* 2002;37(7):389–394.
- `[Girkin 2008]` Girkin CA. Differences in optic nerve structure between individuals of
  predominantly African and European ancestry. *Clin Ophthalmol.* 2008;2(1):65–69.
- `[Duker 2014]` Duker JS, Waheed NK, Goldman DR. *Handbook of Retinal OCT.* Elsevier,
  2014. (princípios de varredura e artefatos)

---

## Registro de lacunas

Itens que a skill deve responder como "não disponível na base científica":

- Valores de referência de área de disco, área de rima, volume de escavação e relação
  escavação/disco.
- Faixas percentílicas de CFNR e de CCG, e o percentil correspondente a cada cor.
- Critérios de progressão glaucomatosa.
- Limiar de espessura macular por aparelho — o BCSC-12 registra que os limiares do
  subcampo central de 1 mm variam conforme o equipamento e são, em média, maiores em
  homens que em mulheres.
- Nomes comerciais de parâmetros e relatórios de Topcon e Nidek.
- Valor mínimo aceitável de intensidade de sinal por aparelho.
- Correlação estrutura-função com campo visual.
