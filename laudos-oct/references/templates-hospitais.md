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

## 2. Médico signatário

**Sempre `"medico": "maeta"`** — Dr Vinícius L Maeta, nos dois hospitais. O campo
pode até ser omitido: é o padrão.

| chave | Nome impresso | Registros |
|---|---|---|
| `maeta` | Dr Vinícius L Maeta | CRM-SC 23632 RQE 14403 / CRM-RS 40608 RQE 30002 |

É o **único** signatário cadastrado, nos dois hospitais, por confirmação da clínica.
Não existe outra chave. Se algum dia entrar outro médico, ele é adicionado em
`MEDICOS` no `scripts/laudo_pdf.py` — nunca escrito à mão no laudo.

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
| **Achado ausente** | "sem fluido intrarretiniano ou sub-retiniano identificável" | `dentro da normalidade.` / `aparentemente dentro da normalidade.` — **varia por hospital**, ver §8 |
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

  "conclusoes": ["AMBOS OS OLHOS com área da escavação fora da curva de normalidade e espessura média da camada de fibras nervosas dentro da curva de normalidade."],
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
| `"dentro"` | verde — "dentro da curva de normalidade" |
| `"fora"` | vermelha — "fora da curva de normalidade" |
| `"limitrofe"` | âmbar — "limítrofe" |
| texto livre | pílula cinza com o texto que você escreveu |
| ausente / `[VERIFICAR]` | sem pílula; o campo é marcado como pendente |

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

**`qualidade`** (opcional, por olho) guarda o índice de sinal como o aparelho o exibe.
É registrado no JSON e **não é impresso no corpo** — o corpo é a lista de 4 parâmetros
ou as 3 camadas. Se o exame estiver limitado, a limitação vai em `observacoes`.

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

- `[modelo]` AMBOS OS OLHOS com área da escavação fora da curva de normalidade e
  espessura média da camada de fibras nervosas dentro da curva de normalidade.
- `[proposta]` AMBOS OS OLHOS com parâmetros do disco óptico e espessura média da
  camada de fibras nervosas dentro da curva de normalidade.
- `[proposta]` OLHO [DIREITO/ESQUERDO] com relação escavação/papila fora da curva de
  normalidade e espessura média da camada de fibras nervosas [dentro/fora] da curva.

> **Imprecisão no original, mantida de propósito.** O modelo da clínica diz "área da
> escavação" na conclusão, enquanto o corpo mede "relação escavação/papila (área)".
> São grandezas diferentes. Copiei como está porque vem do laudo real — **não corrija
> sozinho**. Se o Dr. Maeta quiser ajustar, é decisão dele.

### Conclusões — mácula

- `[modelo]` AMBOS OS OLHOS com máculas aparentemente dentro da normalidade.
- `[modelo]` OLHO DIREITO com achados sugestivos de líquido intrarretiniano em mácula
  temporal.
- `[modelo]` OLHO ESQUERDO com achados sugestivos de descolamento drusenoide em mácula
  central.
- `[proposta]` OLHO [DIREITO/ESQUERDO] com exame tecnicamente limitado, sem avaliação
  adequada das camadas retinianas.

**Ordem dos bullets de conclusão:** OD primeiro, OE depois. Conclusão que vale para os
dois olhos vira um bullet único abrindo com `AMBOS OS OLHOS`.

### Sugestões

- `[modelo]` Sugiro correlação clínica.
- `[modelo]` Sugiro correlação clínica e acompanhamento com exames periódicos para
  comparação dos parâmetros.
- `[modelo]` Sugiro correlação clínica para indicação de tratamento.
- `[proposta]` Sugiro correlação clínica, aferição da pressão intraocular e campimetria
  visual computadorizada.
- `[proposta]` Sugiro repetição do exame para adequada avaliação de [estrutura].

### Qual sugestão para qual achado

| Situação | Sugestão |
|---|---|
| tudo dentro da curva / mácula normal | `Sugiro correlação clínica.` |
| nervo com qualquer parâmetro fora ou limítrofe | `Sugiro correlação clínica e acompanhamento com exames periódicos para comparação dos parâmetros.` |
| mácula com achado que pede tratamento (fluido, membrana neovascular) | `Sugiro correlação clínica para indicação de tratamento.` |
| exame limitado por artefato, sinal ou segmentação | `Sugiro repetição do exame para adequada avaliação de [estrutura].` |
| campo `[VERIFICAR]` ou `[RECAPTURAR]` no laudo | a sugestão descreve a pendência; o laudo não é liberado |

Combinar duas situações é permitido — junte as duas frases numa só, na ordem em que
aparecem na tabela.

## 8. Decisões que a clínica ainda não fechou

Enquanto estiverem abertas, siga a coluna "padrão atual" e **avise no relatório final**
sempre que uma delas afetar um laudo.

> As três estão no formulário `Maeta_decisoes_e_equipamentos.docx`, Bloco 1, junto
> com a imprecisão de §7 (item 1.4). Quando o formulário voltar preenchido, esta
> tabela some e vira regra. Ver `PENDENCIAS.md`.

| Questão | Padrão atual | Por que está aberta |
|---|---|---|
| Reserva diagnóstica quando há parâmetro sinalizado (`base/02-nervo.md` a chama de obrigatória) | **não incluir** — nenhum laudo real da clínica a traz | A base exige, o modelo não usa. Decisão do Dr. Maeta. |
| "aparentemente dentro da normalidade" vs "dentro da normalidade" | por hospital: **Farroupilha usa "aparentemente"**, **Nova Prata usa "dentro"** — é o que os dois modelos mostram | Pode ser hábito de quem digitou, não regra. |
| `nascimento` no laudo do CRO | **imprimir quando houver** (o modelo original não tem) | Sem ele, homônimos ficam indistinguíveis no documento assinado. |

**"Parâmetro sinalizado"** significa qualquer valor que o aparelho tenha classificado
como limítrofe ou fora da curva — média ou setor, não importa.
