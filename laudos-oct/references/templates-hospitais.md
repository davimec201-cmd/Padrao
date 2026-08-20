# Templates dos hospitais e schema do laudo

Tudo aqui foi extraído dos **laudos reais** enviados pela clínica. Quando houver
dúvida entre este documento e sua intuição de redação, este documento vence.

## 1. Identifique o hospital primeiro

Errar de hospital troca o layout inteiro. Confirme pela barra de título do AnyDesk,
pelo nome da unidade na tela ou pelo cabeçalho do exame. Ambíguo → **pergunte**.

| `hospital` | Unidade | Template | Aparência |
|---|---|---|---|
| `farroupilha` | Hospital Farroupilha / BONAVITA | `bonavita` | sem cabeçalho, título centralizado, marca de água, faixa navy no rodapé |
| `nova_prata` | Hospital Nova Prata / Centro Regional de Oftalmologia | `cro` | logo + endereço no topo, título à esquerda, rodapé de horários e contatos |

## 2. Médico signatário — **um por hospital**

**Não existe campo `medico` a preencher.** O signatário é derivado do `hospital`,
sempre. Escrever `medico` no JSON só serve para uma coisa: se contradisser o
hospital, o script **recusa** — é a trava contra assinar o laudo de um hospital
com o médico do outro.

| Hospital | Nome impresso | Registros |
|---|---|---|
| `farroupilha` | `Dr. Cassiano Ricardo Goulart` | `CRM-RS 30.544 RQE 25.730` |
| `nova_prata` | `Dr Vinícius L Maeta` | `CRM-SC 23632 RQE 14403`<br>`CRM-RS 40608 RQE 30002` |

**A grafia é a dos laudos reais e não se uniformiza:**

- Farroupilha escreve **`Dr.`** com ponto; Nova Prata escreve **`Dr`** sem ponto.
- Farroupilha usa ponto de milhar (`30.544`, `25.730`); Nova Prata não (`23632`).
- Nova Prata imprime **as duas** inscrições, **SC antes de RS**, uma por linha.
- O nome sai abreviado: `Dr Vinícius L Maeta`, nunca "Vinicius Lotto Maeta".

Se algum dia entrar outro médico, ele é adicionado em `ASSINANTES` no
`scripts/laudo_pdf.py`, ligado ao hospital — nunca escrito à mão no laudo.

## 3. Um laudo por tipo de exame

Mácula e nervo óptico são **documentos separados**, nunca no mesmo PDF. `exame` é
`"macula"` **ou** `"nervo"`. Paciente com os dois exames gera dois PDFs:

```
Laudo_<SIGLA>_<Nome>_MAC_<AO|OD|OE>_<data>.pdf
Laudo_<SIGLA>_<Nome>_NO_<AO|OD|OE>_<data>.pdf
```

`SIGLA` é `FARROUPILHA` ou `NOVA_PRATA`; `<data>` é o `data_exame` normalizado.
A data está no nome de propósito: sem ela, o exame de acompanhamento do mesmo
paciente e do mesmo olho sobrescreveria o laudo anterior em silêncio.

## 4. Estilo da casa — copie exatamente

Estas escolhas vêm dos laudos reais. Não "melhore" nenhuma delas.

| Item | Como é | Como **não** é |
|---|---|---|
| Título | `TOMOGRAFIA DE COERÊNCIA ÓPTICA (OCT) DE NERVO ÓPTICO` | não use "LAUDO DE..." |
| Área da papila | `2,69 mm2` | não `mm²` |
| CFN média | `98` — **sem unidade** | não `98 µm` |
| Escavação | `0,73 (v) x 0,80 (h)` — razão | não em mm |
| Decimal | vírgula: `0,52` — converta se o aparelho mostrar ponto | não `0.52` |
| Conclusão | começa com `AMBOS OS OLHOS`, `OLHO DIREITO` ou `OLHO ESQUERDO` em caixa alta | — |
| Sugestão | **primeira pessoa**: `Sugiro correlação clínica.` | não "Sugere-se" |
| Camadas da mácula | rótulo em minúscula, texto emenda: `interface vítreo-retiniana dentro da normalidade.` | — |

A classificação de normalidade sai como **pílula colorida** ao lado do valor, igual ao
original: vermelho `#B10202` para fora, verde `#11734B` para dentro.

## 4b. Onde o estilo da casa sobrepõe a base científica

A base científica em `base/` define um registro acadêmico que **não é** o dos laudos
desta clínica. Nestes cinco pontos, o estilo da casa vence — sempre:

| Ponto | Base científica diz | Esta clínica faz |
|---|---|---|
| **Voz do fechamento** | "nunca primeira pessoa"; `Sugere-se correlação clínica` | **`Sugiro correlação clínica`** — primeira pessoa |
| **Unidades** | "medida sempre acompanhada de unidade" | papila em `mm2`, **CFN sem unidade** (`98`), escavação como razão |
| **Formato do nervo** | frases em prosa descrevendo margem, contorno e perfil | **lista de 4 parâmetros**, um por linha, sem prosa |
| **Lateralidade** | "lateralidade em toda descrição" | vem do cabeçalho `OLHO DIREITO` / `OLHO ESQUERDO`, não se repete em cada linha |
| **Achado ausente** | "sem fluido intrarretiniano ou sub-retiniano identificável" | **`aparentemente dentro da normalidade.`** nos dois hospitais (decisão 1.2) |
| **Fluido** | `fluido intrarretiniano`, `fluido sub-retiniano` | **`líquido`** intrarretiniano / sub-retiniano |
| **Formato da data** | — | é do **hospital**, não da tela: Farroupilha `22-07-2026`, CRO `8 de julho de 2026` |

Use a base para **escolher a palavra certa** ao descrever um achado — é para isso que
ela serve, e é onde ela é insubstituível. Não a use para escolher o formato, a unidade
ou a voz do laudo.

Consequência prática no nervo óptico: as "frases prontas" de `base/02-nervo.md` são
prosa e **não entram no corpo do laudo de nervo**, que é lista de parâmetros. Elas
servem para redigir o campo `conclusoes`, e só quando houver achado que a lista não
expresse.

## 5. Schema do `laudo.json`

Grave em `~/Laudos_OCT/<Hospital>/<Paciente>/`. Campo vazio some do PDF — não invente
conteúdo para preencher.

```json
{
  "hospital": "farroupilha",
  "medico": "maeta",
  "exame": "nervo",
  "paciente": { "nome": "Nome Completo", "nascimento": "dd/mm/aaaa" },
  "data_exame": "22-07-2026",
  "olhos": "AO",

  "nervo": {
    "OD": { "area_papila": "2,69 mm2",
            "rel_esc_papila": "0,52",
            "rel_classificacao": "fora",
            "escavacao_v": "0,73", "escavacao_h": "0,80",
            "cfn_media": "98",
            "cfn_classificacao": "dentro" },
    "OE": { "...": "..." }
  },

  "conclusoes": ["AMBOS OS OLHOS com relação escavação/papila (área) fora da curva de normalidade e espessura média da camada de fibras nervosas dentro da curva de normalidade."],
  "sugestao": "Sugiro correlação clínica e acompanhamento com exames periódicos para comparação dos parâmetros."
}
```

Para mácula, troque o bloco `nervo` por:

```json
  "macula": {
    "OD": { "interface_vitreo_retiniana": "dentro da normalidade.",
            "camadas_internas": "com área de líquido intrarretiniano em quadrante temporal (edema) laminar.",
            "epr_cfr": "dentro da normalidade." },
    "OE": { "...": "..." }
  }
```

**Classificação** (`rel_classificacao`, `cfn_classificacao`):

| valor | pílula gerada |
|---|---|
| `"dentro"` | verde — "dentro da curva de normalidade" (tela verde ou branca) |
| `"fora"` | vermelha — "fora da curva de normalidade" (tela **amarela ou vermelha**) |
| texto livre | pílula cinza com o texto que você escreveu |
| ausente / `[VERIFICAR]` | sem pílula; o campo é marcado como pendente |

Só existem esses dois valores de classificação. `"limitrofe"` **não é aceito** —
amarelo é `"fora"`.

**Campo não confirmado:** ponha `[VERIFICAR]` no **valor** e use o campo de
classificação para o **motivo** — sem repetir a marca:

```json
"rel_esc_papila": "[VERIFICAR]",
"rel_classificacao": "dupla leitura divergente (0,52 / 0,62)"
```

Sai como: `relação escavação/papila (área): [VERIFICAR] — dupla leitura divergente
(0,52 / 0,62)`, com a marca em vermelho, banner no topo do laudo e cópia em
`_PENDENTES/`.

**Data:** o formato pertence ao **template do hospital**, não à tela. Leia a data da
tela (é o dado) e escreva-a no formato da unidade:

| Hospital | Formato | Exemplo |
|---|---|---|
| Farroupilha | numérico com hífen | `22-07-2026` |
| Nova Prata | escrito | `8 de julho de 2026` |

Tela do CRO mostrando `19-08-2026` vira `19 de agosto de 2026` no laudo. O que nunca
muda é **o dia, o mês e o ano** — só a forma de escrevê-los.

**Conclusões** aceita string única ou lista — cada item vira um bullet.

**`observacoes`** (opcional, dentro do bloco de cada olho) vira um bullet extra ao fim
daquele olho. Use para o achado que a lista não expressa, para a limitação técnica, e
para o **segundo motivo** quando um mesmo parâmetro tiver dois problemas.

**Não existe campo `qualidade`.** Decisão 3.3: sem limiar numérico e sem índice de
qualidade no fluxo. Exame ruim é laudado assim mesmo, descrevendo o que dá para ver;
quando a avaliação for impossível, use a frase aprovada de §7 em `observacoes`.

**O gerador avisa** no stderr sobre campo desconhecido e sobre campo que ele não
imprime. Nada documentado é ignorado em silêncio. Não existe campo `descricao`.

**E o gerador RECUSA**, sem emitir PDF, quando falta campo obrigatório:
`paciente.nome`, `data_exame`, `hospital`, `olhos`, `conclusoes`, ou quando
nenhum olho está preenchido, ou quando `olhos` declara um olho e os dados são de
outro. Campo que você não conseguiu extrair não fica em branco: vira
`[VERIFICAR]` ou `[RECAPTURAR]` no valor.

### Os dois marcadores

| Marcador | Significa | Ação de quem revisa |
|---|---|---|
| `[VERIFICAR]` | valor lido, mas não confirmado (dupla leitura divergente, dígito ilegível) | conferir o número na estação |
| `[RECAPTURAR]` | estrutura não coberta pela captura | voltar ao exame e capturar o corte completo |

Os dois marcam o laudo e mandam cópia para `_PENDENTES/`, com banner distinto. Um laudo
cheio de `[RECAPTURAR]` **não** quer dizer exame alterado — quer dizer captura curta.

**Onde colocar:** no nervo, `[VERIFICAR]` vai no **valor** e o motivo no campo de
classificação. Na mácula não há campo de classificação, então o marcador vai **no fim
da frase da camada**, e o motivo em `observacoes`.

## 6. Gerar

```bash
python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py --json ~/Laudos_OCT/Farroupilha/Nome/laudo.json
```

O PDF sai sempre com o **espaço da assinatura em branco** e o nome e registros do
médico impressos abaixo — pronto para ele assinar. **A clínica não usa assinatura
digitalizada:** nunca aplique nenhuma, nem sugira aplicar.

Exemplos funcionais dos quatro casos em `assets/`:
`exemplo_nervo_farroupilha.json`, `exemplo_macula_farroupilha.json`,
`exemplo_nervo_nova_prata.json`, `exemplo_macula_nova_prata.json`.

## 7. Biblioteca de frases

Cada frase leva a procedência. **`[modelo]`** = copiada dos laudos reais que a clínica
enviou; pode usar sem pensar. **`[proposta]`** = composta por mim, nunca apareceu num
laudo assinado pelo Dr. Maeta. Se você usar uma `[proposta]`, **diga isso ao usuário no
relatório final** — o médico vai assinar uma frase nova e precisa saber.

Precisando de frase que não existe aqui, componha a partir do vocabulário de
`base/01-vocabulario.md`, marque como nova no relatório, e não a adicione a este
arquivo por conta própria.

### Conclusões — nervo óptico

- `[aprovado]` AMBOS OS OLHOS com **relação escavação/papila (área)** fora da curva de
  normalidade e espessura média da camada de fibras nervosas dentro da curva de
  normalidade.
- `[aprovado]` OLHO [DIREITO/ESQUERDO] com relação escavação/papila fora da curva de
  normalidade e espessura média da camada de fibras nervosas [dentro/fora] da curva.

> **A imprecisão do original foi corrigida** (decisão 1.4, 20/08/2026). Os laudos
> reais diziam "área da escavação" na conclusão enquanto o corpo media "relação
> escavação/papila (área)" — grandezas diferentes. Agora corpo e conclusão usam a
> mesma. **Não existe mais nenhuma ocorrência de "área da escavação" na biblioteca.**

> **Nervo inteiramente dentro da curva não tem conclusão aprovada.** A frase
> proposta para esse caso foi **reprovada** pelo Dr. Maeta ("espessura média da CFN
> já é um dos parâmetros, ficaria ambíguo") e ele não escreveu substituta. Então:
> monte o corpo normalmente, deixe `conclusoes` **vazio**, e diga ao usuário no
> relatório final que a conclusão daquele caso é do médico. O script aceita
> `conclusoes` vazio **só** nesse caso e imprime um aviso no lugar. Não componha
> frase por analogia, não reaproveite a de outro laudo, não deixe como pendência.

### Exame de qualidade ruim

**Não existe limiar numérico e não existe campo de índice de qualidade.** Palavras
do Dr. Maeta: *"mesmo com qualidade ruim eu tento ao máximo observar as alterações"*.
O padrão é **laudar assim mesmo**, descrevendo o que dá para ver. Quando a avaliação
for de fato impossível, a frase é literal, escrita por ele:

- `[aprovado]` impossível avaliar detalhes por possível artefato ou opacidade de meios

O alerta do próprio aparelho e a presença de artefato **sinalizam ao médico**; nunca
reprovam o exame.

### Conclusões — mácula

- `[aprovado]` AMBOS OS OLHOS com máculas aparentemente dentro da normalidade.
- `[aprovado]` OLHO DIREITO com achados sugestivos de líquido intrarretiniano em mácula
  temporal.
- `[aprovado]` OLHO ESQUERDO com achados sugestivos de descolamento drusenoide em mácula
  central.

> A frase de "exame tecnicamente limitado" ficou **sem marcação** no formulário e
> por isso **não entra na biblioteca**. Para exame ruim, o caminho aprovado é a
> frase de qualidade acima.

**Ordem dos bullets de conclusão:** OD primeiro, OE depois. Conclusão que vale para os
dois olhos vira um bullet único abrindo com `AMBOS OS OLHOS`.

### Sugestões

- `[aprovado]` Sugiro correlação clínica.
- `[aprovado]` Sugiro correlação clínica e acompanhamento com exames periódicos para
  comparação dos parâmetros.
- `[aprovado]` Sugiro correlação clínica para indicação de tratamento.

**Duas saíram da biblioteca** (Bloco 2, 20/08/2026) e não voltam:

- ~~Sugiro correlação clínica, aferição da pressão intraocular e campimetria visual
  computadorizada.~~ — *"já é subentendido na correlação clínica esses outros exames"*
- ~~Sugiro repetição do exame para adequada avaliação de [estrutura].~~ — *"pessoal
  de lá não gostou pq na operação deles se torna custoso refazer toda vez que os
  pacientes não conseguem colaborar"*

**Atenção:** o que saiu foi a frase longa, **não a sugestão de correlação clínica**.
As três de cima estão em todos os laudos reais assinados e continuam obrigatórias.

### Qual sugestão para qual achado

| Situação | Sugestão |
|---|---|
| tudo dentro da curva / mácula normal | `Sugiro correlação clínica.` |
| nervo com qualquer parâmetro **fora** da curva | `Sugiro correlação clínica e acompanhamento com exames periódicos para comparação dos parâmetros.` |
| mácula com achado que pede tratamento (fluido, membrana neovascular) | `Sugiro correlação clínica para indicação de tratamento.` |
| exame ruim, mas avaliável | lauda normalmente; a sugestão é a do achado |
| avaliação de fato impossível | `Sugiro correlação clínica.` + a frase de qualidade em `observacoes` |
| campo `[VERIFICAR]` ou `[RECAPTURAR]` no laudo | a sugestão descreve a pendência; o laudo não é liberado |

Combinar duas situações é permitido — junte as duas frases numa só, na ordem em que
aparecem na tabela.

## 8. Decisões fechadas pelo Dr. Maeta em 20/08/2026

Nenhuma destas está mais em aberto. Não reabra, não peça confirmação, não proponha
alternativa.

| Questão | Decisão | Onde aparece |
|---|---|---|
| **1.1** Reserva diagnóstica | **Incluir em todo laudo de nervo óptico**, dos dois hospitais. Nunca em mácula. | parágrafo próprio, depois da sugestão, antes da assinatura |
| **1.2** Frase de normalidade da mácula | **`aparentemente dentro da normalidade`** nos dois hospitais. A forma sem "aparentemente" saiu da biblioteca. | §7, corpo dos laudos de mácula |
| **1.3** Nascimento em Nova Prata | **Imprimir quando houver**, em linha própria. Sem o dado, a linha não é impressa — sem rótulo vazio. | §5, layout do CRO |
| **1.4** "área da escavação" | **Corrigido para `relação escavação/papila (área)`**, em toda a biblioteca e nos dois hospitais. | §7 |
| **3.3** Índice de qualidade | **Sem limiar numérico e sem campo.** Laudar mesmo com qualidade ruim; frase própria quando for impossível avaliar. | §7 |
| **3.4** Cores | **Verde e branco = dentro. Amarelo e vermelho = fora**, com a mesma redação. | abaixo |
| **3.1/3.2** Aparelho | **Irrelevante** — a imagem que ele lauda é sempre a mesma. Não existe campo de equipamento. | — |

### A tabela de cores, fechada

| Cor na tela | O que vai para o laudo |
|---|---|
| verde ou branco | `dentro da curva de normalidade` |
| **amarelo** | `fora da curva de normalidade` |
| vermelho | `fora da curva de normalidade` |

**Não existe categoria "limítrofe" neste sistema.** Amarelo e vermelho produzem
exatamente a mesma redação. Não crie faixa intermediária, não gere frase de
*borderline*, não sinalize divergência com convenção de fabricante.

**"Parâmetro sinalizado"** significa qualquer valor classificado como **fora** da
curva — não importa se a tela o mostrou em amarelo ou em vermelho.
