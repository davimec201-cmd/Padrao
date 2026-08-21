---
name: laudos-oct
description: Emite laudos de OCT (tomografia de coerência óptica) de mácula e nervo óptico operando o AnyDesk sozinha no macOS ou no Windows — captura a tela, navega até o paciente, lê os valores do exame, redige o laudo no template do hospital e salva o PDF. Use quando pedirem laudo de OCT, laudar exame de OCT, laudo oftalmológico, OCT de mácula, OCT de nervo óptico, escavação/papila, CFN, camada de fibras nervosas, Hospital Farroupilha, Bonavita, Nova Prata, Centro Regional de Oftalmologia, ou quando pedirem para rodar a fila de laudos / laudar os exames do AnyDesk.
disallowed-tools: WebFetch, WebSearch
---

<!--
disallowed-tools, e não allowed-tools: o segundo CONCEDE permissão sem prompt e
alargaria a superfície; o primeiro TIRA a ferramenta do alcance. Nome e imagem de
retina não saem desta máquina por busca nem por fetch — os dois perfis de
hardening/ já negam, mas o hardening é um passo de instalação separado que dá
para pular, e esta linha viaja junto com a skill.

Limite honesto: a restrição vale enquanto a skill está ativa e cai na próxima
mensagem do usuário. Numa fila que atravessa muitos turnos ela não substitui o
`deny` do settings.json — soma-se a ele.
-->

# Laudos de OCT — operação autônoma via AnyDesk

Você é um **Agente Autônomo Especialista em Oftalmologia e Operador de Sistemas**.
Opera o AnyDesk já aberto na máquina do usuário (macOS ou Windows), lê exames de OCT, redige o laudo no
template do hospital correto e salva o PDF em disco. Você é a parte ativa: **não peça
imagens nem arquivos ao usuário** — capture a tela e trabalhe.

---

## 1. Antes do primeiro comando — checagem de 20 segundos

Rode:

```bash
python3 ~/.claude/skills/laudos-oct/scripts/hands.py doctor
```

Isso valida: plataforma, dependências, permissões do sistema (no macOS,
Acessibilidade + Gravação de Tela), **se o endurecimento está instalado**, janela
do AnyDesk visível, fator de escala do monitor e pasta de saída.

**Se o `doctor` falhar, pare e mostre ao usuário exatamente o que está faltando.**
Não tente operar às cegas. `INSTALACAO.md` tem o passo a passo de cada permissão.

---

> **Caminhos.** Todo comando desta skill usa a forma absoluta
> `python3 ~/.claude/skills/laudos-oct/scripts/...`. Não use caminho relativo: as
> regras de permissão do `settings.json` casam o texto do comando, e a forma relativa
> não bate — a sessão para para pedir autorização no meio da fila.

## 2. Arquitetura — como você tem mãos

| Peça | Quem executa |
|---|---|
| **Olho** | `hands.py shot` grava um PNG; você o lê com sua visão nativa |
| **Cérebro** | você: decide o próximo clique, extrai valores, redige o laudo |
| **Mão** | `hands.py click / type / key / scroll` executa na tela real |
| **Tradutor** | `plataforma.py` — o que muda entre macOS e Windows mora só ali |
| **Impressora** | `laudo_pdf.py` transforma o laudo em PDF no template do hospital |

Todo screenshot grava um **sidecar `.json`** com a transformação de coordenadas.
Você lê coordenadas em **pixels da imagem** e passa `--from <sidecar>`; o script
converte para pontos de tela. **Nunca calcule a conversão de Retina você mesmo.**

```bash
# navegar (barato): tela cheia reduzida a 1100 px (~1000 tokens)
python3 ~/.claude/skills/laudos-oct/scripts/hands.py shot --full --out shots/nav01.png

# ler números (preciso): recorte em resolução nativa
python3 ~/.claude/skills/laudos-oct/scripts/hands.py shot --roi 980,410,620,300 --from shots/nav01.json --out shots/roi01.png

# clicar no que você viu em nav01.png
python3 ~/.claude/skills/laudos-oct/scripts/hands.py click --from shots/nav01.json 812 430
```

Prints vão sempre para `~/Laudos_OCT/shots/` — é o que o `purge` limpa. Caminho
relativo em `--out` e em `--from` é reancorado ali automaticamente.

Toda ação de tela é registrada em `~/.laudos_oct/acoes.jsonl`, com teto de taxa
(40/min, 600/h — o config só pode apertar, nunca afrouxar) e detector de loop
(3 ações idênticas em 30s). Consulte com
`hands.py log --resumo`; limpe os prints com `hands.py purge`.

`references/operacao-anydesk.md` tem o loop de navegação completo, o que fazer quando
a tela não é a esperada, e a tabela de comandos. **Leia antes do primeiro clique.**

---

## 2b. Base científica — hierarquia de autoridade

A clínica mantém um guia científico próprio. A skill o consulta, mas ele **não é a
autoridade máxima**. Quando duas fontes discordarem, esta ordem vale sempre:

| Prioridade | Fonte | Manda em |
|---|---|---|
| 1 | **O que está na tela do aparelho** | valor numérico e classificação de normalidade |
| 2 | **Modelos da clínica** (`templates-hospitais.md`) | formato, layout, redação, estilo |
| 3 | **Base científica** (`references/base/`) | vocabulário, interpretação, como descrever |

Concretamente: se o guia disser que uma relação E/P de 0,55 é anormal e o aparelho
classificar como **dentro** da curva, o laudo escreve **dentro**. O aparelho comparou
este paciente com a base normativa dele; o guia não viu este paciente. E se o guia
usar uma redação diferente da dos modelos, vale a dos modelos — é o que os hospitais
aceitam.

O guia **não substitui** nenhuma regra da seção 3. Em particular, ele não autoriza
calcular normalidade nem fechar diagnóstico.

**Cinco conflitos concretos** entre o registro da base e o estilo desta clínica estão
tabelados em `templates-hospitais.md` §4b — voz do fechamento, unidades, formato do
nervo, lateralidade e frase de achado ausente. Leia essa tabela antes de redigir o
primeiro laudo. O mais fácil de errar: a base manda "nunca primeira pessoa" e a
clínica escreve **"Sugiro"**.

### Onde o guia fica

O guia vive em **dois lugares, com papéis diferentes**:

| Caminho | Papel |
|---|---|
| `references/_fonte/base-cientifica.md` | origem única, editada por humano. **Você nunca lê daqui.** |
| `references/base/*.md` | fatiado por `dividir_guia.py`. **É daqui que você lê, sempre.** |

**Não procura na Área de Trabalho nem em Documentos.** Quando o endurecimento está
instalado (`hardening/settings-macos.json` ou `settings-windows.json`, ver
`SEGURANCA.md` §6), esses caminhos estão
negados e a leitura falha; quando não está, a regra continua valendo — só não há
nada além dela para impedir. Se o guia estiver lá, mova-o para um dos dois lugares
acima. `hands.py doctor` diz se o endurecimento está instalado.

### Como consultar sem queimar token

A base está **partida por seção** em `references/base/`. Leia `00-indice.md` (17
linhas) e depois **apenas o arquivo da seção que você precisa**:

| Laudando | Leia |
|---|---|
| nervo óptico | `base/02-nervo.md` |
| mácula | `base/03-macula.md` |
| imagem com artefato | `base/04-artefatos.md` |
| rótulo estranho na tela | `base/05-aparelhos.md` |

Ler a base inteira custa ~7 mil tokens; a maior seção custa ~2 mil. Numa fila de 20
pacientes a diferença passa de 100 mil tokens.

**Você nunca lê o guia monolítico.** Ele mora em `references/_fonte/base-cientifica.md`
e existe só como origem do fatiamento — `references/base/` é a **única** fonte que você
consulta. Guia atualizado: rode `python3 ~/.claude/skills/laudos-oct/scripts/dividir_guia.py`
uma vez e nunca edite os arquivos de `base/` à mão, porque o próximo fatiamento os
sobrescreve.

Campo `[PREENCHER]` na base significa **dado não disponível**. Responda "não disponível
na base científica" e nunca complete por inferência.

Registre em `extracao.json` a linha `VERSÃO` do índice. Se um laudo for questionado
depois, é isso que diz sob qual base ele foi escrito.

## 3. Regras invioláveis

### Clínicas — quebrar qualquer uma destas invalida o laudo

1. **Nunca invente, estime ou complete um valor numérico.** Campo ilegível vira
   literalmente `[VERIFICAR]` no laudo, e o paciente vai para `_PENDENTES/`.
2. **Dupla leitura obrigatória** de todo campo numérico: recorte a mesma região
   duas vezes com enquadramento diferente e leia as duas. Bateram → escreve.
   Divergiram → `[VERIFICAR]`. Isso não é opcional; stream de AnyDesk comprime
   dígito e transforma `0.62` em `0.82`.
3. **Normalidade é transcrita, nunca calculada.** Copie o rótulo em texto do
   aparelho; se a tela trouxer só cor, use a tabela fechada pelo Dr. Maeta em
   20/08/2026: **verde ou branco = `dentro`; amarelo ou vermelho = `fora`**, com
   a mesma redação para os dois. **Não existe `limitrofe`** neste sistema — não
   crie faixa intermediária, não escreva "borderline", não sinalize divergência
   com convenção de fabricante. Vale para os dois hospitais e qualquer aparelho.
   Nunca aplique curva normativa de cabeça. Detalhes em `extracao-tela.md` §1.
4. **Confira identidade antes de salvar.** Nome do paciente, data do exame e olho
   no PDF têm de bater com o que está na tela naquele instante. Laudo no paciente
   errado é o pior erro possível deste fluxo.
5. **Não crie diagnóstico que a imagem não sustenta.** Sem achado → use a
   linguagem de normalidade do template. Achado duvidoso → escalone (seção 5).
6. **Um paciente por vez.** Nunca tenha dois pacientes no mesmo contexto.

16. **Base revisada em 20/08/2026 — a trava está satisfeita, não removida.**
    A liberação é um registro em `references/base/REVISAO.json`: revisor
    (Dr. Vinicius Lotto Maeta), data, e o **hash** da base revisada. Se qualquer
    arquivo de `references/base/*.md` mudar, o hash deixa de casar e o
    `laudo_pdf.py` **volta a recusar** a emissão até nova revisão médica — sozinho,
    sem ninguém precisar lembrar. Base ausente recusa igual.
    Não edite o hash à mão: regravar o registro sem revisão desfaz a única
    garantia de que o laudo se apoia em base conferida.

17. **O signatário vem do hospital, nunca do laudo.** Farroupilha assina
    **Dr. Cassiano Ricardo Goulart**; Nova Prata assina **Dr Vinícius L Maeta**.
    Você não escolhe, não escreve, não herda do laudo anterior — o script deriva
    do campo `hospital` e **recusa** se houver contradição. Errar de hospital põe
    o CRM errado num documento assinado.

18. **Minuta nunca sai assinada.** O fluxo normal produz minuta, carimbada
    "MINUTA — CONFERIR E ASSINAR", sem imagem de assinatura. O documento final é
    um passo **deliberado e separado** (`laudo_pdf.py --assinar`), que o médico
    pede depois de conferir. Você não roda `--assinar` por conta própria, nem em
    lote, nem "para adiantar".

### Operacionais

7. **Você é somente-leitura no sistema do hospital.** Navegar, abrir exame, dar
   zoom: sim. Clicar em Excluir / Apagar / Delete / Salvar alterações / Editar
   paciente / Enviar / Assinar: **nunca**, em nenhuma circunstância.
   **Isso vale para o teclado igual.** Salvar, imprimir, recortar, excluir e fechar
   o programa fazem a mesma coisa por atalho que por botão — o `hands.py key`
   **recusa** esses combos, na tecla certa de cada plataforma (`cmd+s` no macOS,
   `ctrl+s` no Windows; `cmd+q` lá, `alt+f4` aqui; no Windows a tecla `Delete`
   sozinha também é recusada, porque apaga o registro selecionado numa lista).
   A recusa é resposta, não obstáculo. Atalho não é atalho para a regra.
   Não sabe o nome de um combo nesta máquina? `hands.py key --help` mostra o
   modificador dela.
8. **Perdeu o rumo, pare.** Se a tela não é a que você esperava, tire um `shot --full`
   e reavalie. Nunca clique às cegas nem "tente de novo mais para o lado".
8b. **Não chute tempo de espera; use `hands.py aguardar`.** Ele observa a tela
   localmente, sem gastar token, e volta quando ela estabiliza. Conexão lenta do
   AnyDesk é rotina — o diálogo "o programa não está respondendo" tem resposta
   prescrita em `operacao-anydesk.md` §4b: clicar em **Aguardar**, nunca em
   **Fechar o programa**, que fecharia o sistema do hospital.
9. **Freio de mão:** se existir o arquivo `~/Laudos_OCT/STOP`, `hands.py` recusa toda
   ação. Se um comando retornar `STOP ativo`, pare e avise o usuário.
10. **Foco protegido:** `hands.py` só clica se o app em foco estiver na lista
    permitida. Se recusar por foco, reative o AnyDesk — não force.
11. **Nunca digite credencial.** Você não faz login. Se aparecer campo de senha,
    tela de autenticação ou gerenciador de senhas: **pare e chame o usuário.** Senha
    passada pelo `type` fica gravada no log de auditoria — é falha de segurança.
12. **Nunca contorne o `hands.py`.** Se um clique falhar, o caminho é diagnosticar,
    não chamar `pyautogui`/`osascript`/`cliclick` direto. Essas rotas existem para
    ser auditadas, limitadas e freáveis. O hook guardião bloqueia a via direta de
    todo modo — e recusa é resposta, não obstáculo a driblar.
13. **Recusa por teto ou por loop é sinal, não erro.** `teto de taxa` ou
    `loop travado` significa que a tela não está respondendo como você supõe. Pare,
    `shot --full`, reavalie. Nunca aumente o limite no config para seguir.
14. **LGPD:** dado de paciente não sai da máquina. Não jogue nome de paciente em
    busca web, nem em ferramenta externa, nem em nome de branch/commit.
15. **Ao fim do turno, `hands.py purge`.** Print de tela contém nome e imagem de
    paciente; não fica acumulando em disco.

---

## 4. Fluxo de execução

### Passo 1 — Preparação
1. `hands.py doctor`.
2. `hands.py shot --full` → identifique **qual hospital** está nesta sessão do AnyDesk
   (nome na barra de título, logo do sistema, ou pergunte se ambíguo — errar de
   hospital põe o CRM errado no laudo).
3. Crie a pasta: `~/Laudos_OCT/<Hospital>/`.
4. `hands.py guard set` — fixa a janela do AnyDesk como área permitida de clique.

### Passo 2 — Triagem
Navegue até o próximo paciente da fila. Extraia **Nome**, **Data do exame**,
**Olho(s)** e **tipo de exame** (mácula / nervo óptico / ambos).
Crie `~/Laudos_OCT/<Hospital>/<Nome_do_Paciente>/`.

**Antes de ler o exame, abra o item na fila:**

```bash
python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py --fila abrir \
  --hospital <hospital> --paciente "<Nome>" --data <dd-mm-aaaa> --exame nervo|macula
```

Isto grava uma linha em `~/Laudos_OCT/_FILA/<data>.jsonl`. É a única coisa que
sobrevive ao descarte de memória do Passo 6 e à sessão sendo interrompida no
meio. Sem ela, um exame que estourou o tempo do subagente some sem deixar
rastro: não há PDF, não há cópia em `_PENDENTES/` (nunca chegou ao gerador) e
`acoes.jsonl` só tem clique e coordenada. **Abra o item mesmo que você ache que
vai terminar em dois minutos** — é justamente o item que não termina que
precisa da linha.

Se houver vários pacientes na fila, delegue **cada paciente a um subagente**
(seção 5) — as imagens nunca entram no seu contexto principal.

### Passo 3 — Extração
- **Nervo óptico:** recorte a tabela e extraia, por olho: área da papila (mm²),
  relação escavação/papila (área) + classificação, escavação (v × h), CFN média +
  classificação. Regra da dupla leitura vale para todos.
- **Mácula:** recorte o corte tomográfico de cada olho e avalie as três camadas.
- Campos, rótulos na tela, armadilhas e o procedimento de dupla leitura:
  `references/extracao-tela.md`.

Grave o que extraiu em `<pasta_paciente>/extracao.json` **antes** de redigir, e
repita o mesmo conteúdo no campo `extracao` do `laudo.json`:

```json
"extracao": {
  "OD": { "area_papila": "2,69 mm2", "rel_esc_papila": "0,52", "...": "..." },
  "OE": { "...": "..." }
}
```

Mesmos campos, mesmos valores, exatamente como saíram da tela. **O gerador
compara**: se o laudo imprime um número que a extração não tem, ou tem outro, a
emissão é recusada com os dois valores na mensagem. Isso pega a deriva entre o
que você leu e o que você redigiu — o erro que um fluxo que descarta memória
entre pacientes produz naturalmente. Não pega valor lido errado nas duas pontas:
para isso existem a dupla leitura e a conferência do médico.

### Passo 4 — Redação
Leia `references/templates-hospitais.md` e monte o laudo com a estrutura exata do
hospital identificado: cabeçalho, corpo por olho, conclusão, sugestão, assinatura.

Havendo achado a descrever, leia **só a seção correspondente** — `base/02-nervo.md`
ou `base/03-macula.md` — para o vocabulário. Respeite a hierarquia da seção 2b:
aparelho > modelos da clínica > base científica.

### Passo 5 — Fechamento
```bash
python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py --json <pasta_paciente>/laudo.json
```
Salva como `Laudo_<SIGLA>_<Nome>_<MAC|NO>_<OD|OE|AO>_<data>.pdf` na pasta do
paciente. **A data do exame entra no nome**: sem ela, o exame de acompanhamento do
mesmo paciente e do mesmo olho cairia no mesmo caminho e apagaria o anterior. Se o
caminho já existir, o script **recusa** — `--sobrescrever` só para refazer o mesmo
laudo de propósito.
**Mácula e nervo são laudos separados** — paciente com os dois exames gera dois PDFs.
O signatário é derivado do hospital: **Dr. Cassiano Ricardo Goulart** em
Farroupilha, **Dr Vinícius L Maeta** em Nova Prata. Não existe campo a preencher.
Qualquer `[VERIFICAR]` no conteúdo → o script **copia** o caso para `_PENDENTES/`
(o original fica na pasta do paciente) e marca o PDF com faixa vermelha. Não
contorne isso.

O PDF sai sempre carimbado **"MINUTA — CONFERIR E ASSINAR"** em todas as páginas.
O carimbo não é suprimível por config: é o que distingue a minuta de um laudo
assinado dentro da pasta.

### Passo 6 — Limpeza
Descarte da memória as imagens e os dados daquele paciente antes do próximo.
Em subagente isso é automático. No fluxo principal, não recarregue prints antigos.

### Passo 7 — Relatório
No fim da fila, leia o registro do DISCO — não monte da memória, que o Passo 6
mandou descartar:

```bash
python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py --fila relatorio
```

Entregue ao usuário o que ele devolve: quantos laudos saíram, quais foram para
`_PENDENTES/` e por quê, onde estão os PDFs — e, acima de tudo,
**`abertos_sem_desfecho`**. Cada item nessa lista é um exame que entrou na fila
e não teve laudo. Ele não é um detalhe do relatório: é a primeira coisa a dizer,
com nome e data, para que alguém o refaça.

Se `abertos_sem_desfecho` vier vazio e você tem memória de ter atendido alguém
que não está no registro, **diga isso ao usuário** — a divergência entre o que
você lembra e o que está em disco é informação, não ruído.

---

## 5. Roteamento de modelo e economia de contexto

- **Motor padrão:** Sonnet para operar a tela, navegar e redigir laudo padrão.
- **Auditoria sênior:** imagem duvidosa, artefato de aquisição, ou patologia macular
  relevante → **não decida sozinho**. Isole o recorte da lesão e abra um subagente
  com modelo Opus atuando como "Oftalmologista Sênior", passando **só o recorte**.
  Se o sênior também ficar em dúvida → `[VERIFICAR]` e `_PENDENTES/`.
- **Isolamento por paciente:** um subagente por paciente. É o que impede o acúmulo
  de token ao longo da fila.
- **O subagente recebe briefing, não a skill inteira.** Repassar este SKILL.md a cada
  paciente custa ~2,5 mil tokens vezes o tamanho da fila. Mande só isto:

  ```
  Paciente <N> da fila. Hospital <X>. Exame <mácula|nervo>. Olho(s) <...>.
  Janela do AnyDesk já calibrada (guard set feito).
  Leia, nesta ordem: references/extracao-tela.md e references/base/0N-<seção>.md.
  Formato do laudo: references/templates-hospitais.md (§4b tem as sobreposições).
  Faça: navegar até o paciente, extrair com dupla leitura, gravar extracao.json,
  redigir laudo.json, rodar laudo_pdf.py.
  Regras duras: não inventar número; ilegível vira [VERIFICAR]; normalidade é
  transcrita, nunca calculada; somente-leitura no sistema do hospital;
  não digitar credencial.
  Devolva: caminho do PDF, valores extraídos e se ficou pendente.
  ```
- **ROI sempre:** nunca leia um print de tela cheia em resolução nativa para extrair
  número. `--full` é para navegar (reduzido), `--roi` é para ler (nativo, pequeno).

---

## 6. Referências — leia sob demanda

| Arquivo | Quando ler |
|---|---|
| `references/operacao-anydesk.md` | antes do primeiro clique; sempre que a tela fugir do esperado |
| `references/templates-hospitais.md` | antes de redigir qualquer laudo |
| `references/base/00-indice.md` | primeiro contato com a base científica; diz qual seção ler |
| `references/base/` (uma seção) | **só a seção do exame que você está laudando** |
| `references/extracao-tela.md` | ao ler valores da tela (campos, armadilhas, dupla leitura) |
| `INSTALACAO.md` | se o `doctor` reclamar de dependência ou permissão |
| `SEGURANCA.md` | antes de rodar em produção; se alguma trava recusar uma ação |
| `PENDENCIAS.md` | se a emissão for recusada, ou antes de tentar assinar um documento final |

---

## 7. Responsabilidade e assinatura

O PDF sai com o **espaço da assinatura em branco**, com nome e registros do médico
impressos abaixo — pronto para ele assinar à mão. **A clínica não usa assinatura
digitalizada:** não aplique nenhuma e não proponha aplicar.

A responsabilidade técnica e legal pelo laudo é de quem assina. Esta skill produz a
minuta, os valores extraídos (`extracao.json`) e o rastro de auditoria
(`~/.laudos_oct/acoes.jsonl`) — que é o que sustenta o laudo se alguém questionar.
