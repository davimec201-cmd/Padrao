# Revisão de código — skill `laudos-oct` (SkillLaudoWindowsV1)

ZIP `7183dea1-SkillLaudoWindowsV1.zip` · sha256 `4432182c70d85fc43c630a5ff5598b1d8f7894891542d112bc60bd89f82e420f`
47 entradas, 38 arquivos, 368.557 bytes · revisão em 21/08/2026

Nada foi aplicado nesta rodada. O pacote entregue permanece intacto.

---

## Seção 0 — Cobertura, pipeline e superfícies

### 0.1 Tabela de cobertura

| arquivo | bytes/linhas | status |
|---|---|---|
| `laudos-oct/SKILL.md` | 18922 / 349 | integral |
| `laudos-oct/INSTALACAO.md` | 8590 / 217 | integral |
| `laudos-oct/SEGURANCA.md` | 16896 / 283 | integral |
| `laudos-oct/PENDENCIAS.md` | 4258 / 81 | integral |
| `laudos-oct/.gitignore` | 323 / 13 | integral |
| `laudos-oct/scripts/hands.py` | 31187 / 806 | integral |
| `laudos-oct/scripts/plataforma.py` | 18802 / 493 | integral |
| `laudos-oct/scripts/laudo_pdf.py` | 41616 / 933 | integral |
| `laudos-oct/scripts/dividir_guia.py` | 6653 / 158 | integral |
| `laudos-oct/scripts/teste_regras.py` | 7474 / 190 | integral |
| `laudos-oct/scripts/teste_aceite.py` | 12128 / 272 | parcial — lido integralmente por `rg` de asserções + leitura de 1–80 e 160–272; o miolo 80–120 (construtores de fixture) foi lido por amostragem |
| `laudos-oct/scripts/setup.sh` | 2360 / 59 | integral |
| `laudos-oct/scripts/setup.ps1` | 2776 / 61 | integral |
| `laudos-oct/scripts/requirements.txt` | 275 / 7 | integral |
| `laudos-oct/scripts/requirements-windows.txt` | 344 / 7 | integral |
| `laudos-oct/hardening/hooks/guardiao-laudos.py` | 9993 / 218 | integral |
| `laudos-oct/hardening/settings-windows.json` | 5177 / 131 | integral |
| `laudos-oct/hardening/settings-macos.json` | 4186 / 111 | integral |
| `laudos-oct/references/extracao-tela.md` | 6950 / 133 | integral |
| `laudos-oct/references/operacao-anydesk.md` | 9815 / 176 | integral |
| `laudos-oct/references/templates-hospitais.md` | 16968 / 335 | integral |
| `laudos-oct/references/base/00-indice.md` | 1432 / 23 | integral |
| `laudos-oct/references/base/07-lacunas.md` | 953 / 17 | integral |
| `laudos-oct/references/base/01-vocabulario.md` | 3272 | parcial — cabeçalho e carimbo de versão; conteúdo clínico não auditado (não é objeto desta revisão) |
| `laudos-oct/references/base/02-nervo.md` | 5168 | parcial — idem |
| `laudos-oct/references/base/03-macula.md` | 12617 | parcial — idem |
| `laudos-oct/references/base/04-artefatos.md` | 4147 | parcial — idem |
| `laudos-oct/references/base/05-aparelhos.md` | 3426 | parcial — idem |
| `laudos-oct/references/base/06-referencias.md` | 3479 | parcial — idem |
| `laudos-oct/references/base/REVISAO.json` | 638 | integral |
| `laudos-oct/references/_fonte/base-cientifica.md` | 32652 | parcial — cabeçalho (1–14) integral; corpo clínico não auditado |
| `laudos-oct/assets/exemplo_macula_farroupilha.json` | 818 | integral |
| `laudos-oct/assets/exemplo_macula_nova_prata.json` | 1088 | integral |
| `laudos-oct/assets/exemplo_nervo_farroupilha.json` | 1094 | integral |
| `laudos-oct/assets/exemplo_nervo_nova_prata.json` | 1093 | integral |
| `laudos-oct/assets/marca/footer_bonavita.png` | 25441 | binário — extraído com `file` + PIL (`info`/`getexif`) + `strings` |
| `laudos-oct/assets/marca/logo_cro.png` | 19809 | binário — idem |
| `laudos-oct/assets/marca/marca_agua_bonavita.png` | 25737 | binário — idem |

Não há `.git/` no pacote, nem dotfile além do `.gitignore` (`unzip -l` + `find ref -type f` conferidos).

### 0.2 Pipeline e runtime

Linguagens: Python 3 (6 arquivos), Markdown (12), JSON (7), PowerShell (1), Bash (1), PNG (3).

**Como o pacote fala com a origem:** não fala por rede. Não há `requests`, `httpx`, `urlopen`, socket, DICOM, banco nem share (§C1, todas as buscas vazias com `exit=1`). A origem é **a tela de uma sessão de AnyDesk já aberta**: o pacote lê por captura de tela e escreve por evento sintético de mouse e teclado (`cliclick`/`pyautogui` no macOS, `pyautogui` no Windows). **Tradução de padrões:** onde o catálogo diz `requests.post`/`page.click`, aqui o equivalente é `plataforma.mouse()`, `plataforma.tecla()` e `plataforma.digitar()`; onde diz "seletor DOM", aqui é par de coordenadas + sidecar de transformação; onde diz "login", aqui é o operador humano (a skill tem regra de parar diante de campo de senha).

**Como o agente invoca:** por linha de comando, sempre `python3 ~/.claude/skills/laudos-oct/scripts/<script>.py`, casada textualmente pelas regras de `permissions` do `settings.json` e filtrada pelo hook `PreToolUse` `guardiao-laudos.py`.

**Fluxo:** `hands.py doctor` → operador conecta o AnyDesk e autentica (o agente não faz login) → `hands.py guard set` → **[laço]** `shot --full` → o modelo lê a imagem → `click`/`key`/`type`/`scroll`/`aguardar` → `shot --roi` para ler números (dupla leitura) → o modelo grava `extracao.json` e `laudo.json` → `laudo_pdf.py --json` valida, sela contra a base e grava o PDF → `[VERIFICAR]`/`[RECAPTURAR]` copiam para `_PENDENTES/` → **[fim do laço]** relatório final ao usuário.

**Onde o laço do lote executa (A1): em prosa.** `SKILL.md:241,245` manda "delegue **cada paciente a um subagente**". Não existe iteração em código: a busca por invocação por item (`subprocess|Task\(|subagent|for paciente|for exame|nova sessão`) em `scripts/` e `hardening/` devolve apenas os `subprocess.run` da camada de plataforma e do arquivo de teste. Toda a fila, a ordem, a contagem e o relatório final vivem na janela de contexto do agente hospedeiro.

### 0.3 Tabela de superfícies

| entrada não confiável | destino de saída | variável que carrega identidade |
|---|---|---|
| pixels da tela do hospital, lidos pela visão do modelo (`hands.py:299` `cmd_shot`) | `~/Laudos_OCT/shots/*.png` + sidecar `.json` (`hands.py:303`) | `sc["origin_pt"]`, `sc["px_per_pt"]` (`hands.py:292`) — identidade **de coordenada**, não de paciente |
| texto do nome do paciente digitado na busca (`hands.py:414` `cmd_type`) | evento de teclado na sessão remota (`plataforma.py:246`/`445`) | `a.text` (só o hash entra no rastro, `hands.py:432`) |
| conteúdo de `laudo.json`, redigido pelo modelo a partir da tela | `~/Laudos_OCT/<Hospital>/<Nome>/Laudo_*.pdf` (`laudo_pdf.py:868`) **ou qualquer caminho via `--out`** (`laudo_pdf.py:863-864`) | `d["paciente"]["nome"]`, `d["data_exame"]`, `d["olhos"]` (`laudo_pdf.py:855-862`) |
| idem | `~/Laudos_OCT/_PENDENTES/` (`laudo_pdf.py:922-925`) | `out.stem` (`laudo_pdf.py:924`) |
| linha de comando montada pelo modelo | `~/.laudos_oct/guardiao.log` (`guardiao-laudos.py:38-48`) | caminho do `--json`, que contém o nome do paciente |
| ações de tela | `~/.laudos_oct/acoes.jsonl` (`hands.py:119`) | `assinatura`, `pt`, `texto_hash` |
| **o transcript do agente** — cada recorte com nome e imagem de retina vai à API do modelo | fora da máquina | tudo |

### 0.4 Execuções e ambiente

- `SCRATCH=/tmp/claude-0/-home-user-Padrao/9e95a060-.../scratchpad/rev-laudos` — apagado ao fim (contém dado extraído do pacote, §2.3).
- `sha256sum -c "$SCRATCH/ref.sha256" --quiet` → **REF_INTACTA**. `diff -rq ref/ bancada/` → só `fixtures-rev/` e `__pycache__/` a mais na bancada; nenhum arquivo-fonte divergiu. Todas as linhas citadas foram reancoradas em `ref/` com `sed -n`.
- **AVISO de bancada disparou:** rodo como root, `chmod -R a-w ref/` não trava; a imutabilidade da referência depende da testemunha `ref.sha256`, que fechou.
- `python3 scripts/teste_regras.py` → **58 passaram, 0 falharam**.
- `python3 scripts/teste_aceite.py` → **43 passaram, 0 falharam** (com `reportlab 5.0.1` instalado na bancada; o pacote não fixa versão).
- `python3 -m vulture bancada/ --min-confidence 60` → 11 achados, **todos falsos positivos** de override de framework (`wrap`/`draw` de `Flowable`, `pyautogui.FAILSAFE`) exceto o de `teste_aceite.py:251`.
- `python3 -m ruff check --select F401,F811,F841` → `All checks passed!`.
- `python3 -m ruff check --select C901 --config 'lint.mccabe.max-complexity=10'` → `main` de `dividir_guia.py` (15) e `valida` de `laudo_pdf.py` (16).
- **Ferramentas ausentes e substitutos:** `pdftotext`/`mutool`/`qpdf` não existem no ambiente; `pypdf` e `pdfminer.six` instalam mas quebram (`cryptography` com `_cffi_backend` ausente). Escrevi um extrator próprio (ASCII85 → Flate → operadores `Tj`/`TJ`, filtrando streams de página por `BT`/`Tf`) e é a saída dele que aparece nos blocos abaixo.
- **Correção de comando deste prompt:** nenhuma. Todos os padrões rodaram na forma canônica `rg -n -uu --hidden -g '!.git' -e '<padrão>' ref/`.
- Fonte externa consultada: `https://code.claude.com/docs/en/hooks`, para os valores aceitos de `permissionDecision` (A-01 / B-02).

### 0.5 Respostas a P1, P2 e P3

```
P1 — o laudo pode sair no paciente ou no olho errado?
P1: ABERTO
verificado em: laudo_pdf.py:275-289, laudo_pdf.py:332-347, laudo_pdf.py:855-881, hands.py:274-289, SKILL.md:241-246
como: rodei FX-OD / FX-CONFLITO / FX-SEMOLHO contra laudo_pdf.py e mutei OLHOS_OK na bancada; e exercitei load_sidecar com o sidecar do paciente errado
sustenta: A-07 (sidecar de outro paciente por basename), B-03 (sem estado de execução em disco)
residual: a reconciliação olhos-declarados × olhos-preenchidos e a colisão de nome FUNCIONAM (Seção 6). O que fica aberto é o
  que não tem código nenhum: não existe chave de exame que viaje com o texto, o casamento paciente↔exame é a memória do agente,
  e o laço do lote é prosa. Fecha exibindo, num teste com dois pacientes na fila e o agente hospedeiro real, que o item N não
  herda nada do N-1 — o que exige a estação e o modelo.

P2 — PHI sai do controle da clínica por caminho não declarado?
P2: SIM
verificado em: laudo_pdf.py:863-864, guardiao-laudos.py:34-35, SEGURANCA.md:133, SEGURANCA.md:195-206
como: emiti com --out para ~/OneDrive/Documentos e saiu; rodei redige() contra 'type Bernardete' e contra o comando de --json que a própria doc manda usar
sustenta: A-05, M-04
residual: o canal maior — cada recorte de tela indo à API do modelo — é DECLARADO com honestidade em SEGURANCA.md §5 e não é
  achado. O que não está declarado é (a) --out, que não aparece em nenhum arquivo do pacote, e (b) o nome do paciente em claro
  no guardiao.log a cada laudo, num log que o purge não alcança e que a doc afirma redigido.

P3 — o pacote pode assinar, publicar ou gravar na origem?
P3: SIM
verificado em: laudo_pdf.py:794-797, laudo_pdf.py:543-610, plataforma.py:116-131, plataforma.py:276-292, settings-windows.json:10-12, guardiao-laudos.py:202-206
como: liguei a flag na bancada (PNG sintético em ~/.laudos_oct/assinaturas/) e rodei --assinar nos dois templates; e exercitei cmd_key com o alias longo do modificador
sustenta: B-01 (escrita/impressão na origem por alias de tecla), A-01 (capacidade de assinar alcançável e pré-aprovada), M-01
residual: --assinar QUEBRA hoje (TypeError, M-01), então não consegui produzir o desfecho (iii) por essa via — por 1.7 vale alta
  pela presença, não bloqueante. Por B-01 o desfecho (iii) é executado e bloqueante. Fecha quando o alias de modificador for
  normalizado antes da tabela de recusa e quando --assinar deixar de estar na lista allow sem confirmação humana.
```

---

## Seção 1 — Veredito

`NÃO — plataforma.py:116-131 e 276-292 deixam 'command+s' / 'control+s' / 'control+p' / 'control+x' atravessarem COMBOS_NEGADOS e chegarem como Salvar e Imprimir ao sistema do hospital, que a skill declara operar em somente-leitura.`

Sustentam: **B-01**, **B-02**, **B-03**.

**Condição verificável para virar apto:** (a) `hands.py:445-456` normaliza cada modificador pelo valor de `PLAT.MODS` **antes** de consultar `COMBOS_NEGADOS`, e `teste_regras.py` passa a exercitar as duas grafias de cada combo negado, com a suíte vermelha se qualquer alias passar; (b) a guarda de foco/retângulo deixa de depender de casar o texto `--anywhere` — `hands.py` recusa a flag por padrão e exige uma variável de ambiente que só o operador humano põe, e a suíte prova que `--any` e `--anywh` são recusados; (c) existe, no disco, um registro append-only por item da fila (chave do exame, hora, desfecho) que `laudo_pdf.py` grava e o relatório final do Passo 7 lê, com um teste que mostra um item interrompido aparecendo como pendente na segunda execução.

---

## Seção 2 — Índice de achados

| ID | sev | marcador | tipo | arquivo:linha | eixo | defeito |
|---|---|---|---|---|---|---|
| B-01 | bloqueante | `[executado]` | comportamento | `scripts/plataforma.py:116-119` (e `276-277`) | A/B/D | Alias de modificador (`command+s`, `control+s`, `control+p`, `control+x`) não casa a chave de `COMBOS_NEGADOS` e a tecla chega ao sistema do hospital |
| B-02 | bloqueante | `[executado]` | comportamento | `scripts/hands.py:729` + `hardening/hooks/guardiao-laudos.py:213-215` | A/B/E | `--any`/`--anywh` (abreviação do argparse) desliga guarda de foco e de retângulo e não casa a regex do guardião; e o veredito `escalate` não é valor aceito de `permissionDecision` |
| B-03 | bloqueante | `[ausência]` | ausência | `scripts/laudo_pdf.py:929` (âncora) + `SKILL.md:291-293` (promessa) | A/D | Nenhum estado de execução em disco: a fila, o que foi feito e o que faltou vivem só na memória do agente, que o próprio fluxo manda descartar entre pacientes |
| A-01 | alta | `[estático]` | comportamento | `scripts/laudo_pdf.py:794-797` (+ `SEGURANCA.md:260-262`, `INSTALACAO.md:211-212`) | D | A capacidade de embutir assinatura existe, está na lista `allow` sem confirmação e é tratada como leitura pelo guardião — enquanto dois documentos afirmam ao operador que ela foi removida do código |
| A-02 | alta | `[executado]` | comportamento | `scripts/laudo_pdf.py:255-269` | D | `observacoes`, `equipamento` e `data_laudo` na raiz do JSON são aceitos **sem aviso** e nunca impressos: a frase de limitação técnica some do laudo em silêncio |
| A-03 | alta | `[executado]` | comportamento | `scripts/laudo_pdf.py:426-438` (+ `references/extracao-tela.md:39`, `scripts/teste_aceite.py:174`) | D/G | Classificação de normalidade sem allowlist: `limítrofe` e `borderline (p<5%)` saem impressos, sem pendência, contra cinco regras fechadas — e o teste que afirma o contrário é um grep no código-fonte |
| A-04 | alta | `[executado]` | comportamento | `scripts/hands.py:691` | E | `doctor` exige a string `"sandbox"` no `settings.json`; o perfil oficial do Windows não a tem e não pode ter → `VEREDITO: NAO_PRONTO` permanente na plataforma-alvo, e `setup.ps1:54-58` nunca conclui |
| A-05 | alta | `[executado]` | comportamento | `scripts/laudo_pdf.py:863-864` | C/D | `--out`, não documentado em lugar nenhum do pacote, grava o PDF com PHI em qualquer caminho — inclusive `~/OneDrive/`, contornando o `Write(~/OneDrive/**)` do deny |
| A-06 | alta | `[executado]` | comportamento | `references/base/00-indice.md:3` (+ os 7 `base/0N-*.md:2`) | D/E | Todos os arquivos da base que o agente lê carregam `VERSÃO: 1.0-rascunho · REVISADO POR: PENDENTE — não colocar em produção`, enquanto `REVISAO.json` os declara revisados e o gerador emite |
| A-07 | alta | `[executado]` | comportamento | `scripts/hands.py:283-286` | A | `load_sidecar` casa por **basename** em toda a árvore de shots: pedir o sidecar do paciente B, inexistente, devolve o do paciente A e o clique é convertido pela geometria errada |
| A-08 | alta | `[executado]` | comportamento | `scripts/hands.py:126-133` | A/C | `audit()` falha **aberto**: com o rastro ingravável, o teto de taxa, o detector de loop e a trilha somem juntos e as ações seguem — 60 cliques idênticos onde o limite é 3 |
| M-01 | média | `[executado]` | comportamento | `scripts/laudo_pdf.py:569` — `Image(..., width=None, kind="proportional")` levanta `TypeError`: o caminho `--assinar` nunca produziu documento final, nos dois templates. `PENDENCIAS.md:12` atribui o bloqueio às imagens que faltam; com a imagem presente ele quebra igual. |
| M-02 | média | `[executado]` | comportamento | `scripts/hands.py:478-488` — `cmd_scroll` sem `--x/--y` não chama `guard_ok`: rola o app em primeiro plano seja ele qual for, inclusive com o foco ilegível. É a única ação de tela fora da guarda. |
| M-03 | média | `[executado]` | comportamento | `scripts/laudo_pdf.py:371-372` — o selo da base exclui `00-indice.md`, que é o arquivo que o `SKILL.md:119-120` manda ler primeiro e que carrega a regra de precedência e o "nunca complete por inferência". Editei-o inserindo o oposto e a emissão seguiu normal, reportando `VERSÃO: 1.0`. |
| M-04 | média | `[executado]` | comportamento | `hardening/hooks/guardiao-laudos.py:34-35` — a redação do log só cobre texto entre aspas. `hands.py type Bernardete` e **todo** `laudo_pdf.py --json ~/Laudos_OCT/<Hospital>/<Nome>/laudo.json` gravam o nome do paciente em claro em `guardiao.log`, que nenhum `purge` alcança. `SEGURANCA.md:133` afirma o problema resolvido. |
| M-05 | média | `[ausência]` | ausência | `scripts/laudo_pdf.py:807` (âncora: onde o laudo entra) — `AUSÊNCIA:` `extracao.json` é prometido como rastro de auditoria em `SKILL.md:256-257`, `SKILL.md:141-142` e `SKILL.md:348`, e nenhum código o escreve, exige ou lê. Sem ele conferir é ler plausibilidade, não comparar. |
| M-06 | média | `[interpretação]` | instrução | `references/templates-hospitais.md:100-106` — o schema canônico traz `"hospital": "farroupilha"` com `"medico": "maeta"`, a contradição exata que `laudo_pdf.py:846` recusa; e `templates-hospitais.md:18` diz que o campo não existe. Copiar o schema produz um laudo que o script rejeita. |
| M-07 | média | `[ausência]` | ausência | `scripts/laudo_pdf.py:869` (âncora: o `mkdir` do destino) — `AUSÊNCIA:` o PDF sai `0644` e as pastas `0755`, enquanto `hands.py:107-116` restringe o rastro a `0600`/`0700` de propósito. O documento com nome, nascimento e conteúdo clínico é o artefato menos protegido do fluxo. |
| M-08 | média | `[estático]` | comportamento | `scripts/teste_aceite.py:247-260` — a suíte **escreve** em `references/base/01-vocabulario.md` do pacote instalado e restaura no `finally`. Interrupção no meio deixa a base selada alterada e a estação incapaz de emitir, por um motivo que não se liga ao teste. |
| M-09 | média | `[executado]` | comportamento | `scripts/teste_aceite.py:82,97` — todas as fixtures usam `olhos: "AO"`. Mutei `OLHOS_OK` para normalizar `OD` como `OE` e as **duas** suítes seguiram verdes (43/43 e 58/58): 101 asserções não pegam a inversão de lateralidade. |
| M-10 | média | `[estático]` | instrução | `SKILL.md:1-4` — o frontmatter tem só `name` e `description`. Sem `allowed-tools` a skill herda toda a superfície de ferramentas da sessão; a contenção fica inteira nos perfis de `hardening/`, que `INSTALACAO.md:65` admite ser um passo separado e pulável. |
| R-01 | baixa | `[ruído]` | ruído | `scripts/teste_aceite.py:251` — `importlib.reload(lp) if False else None`: condição constante, sobra de depuração. |
| R-02 | baixa | `[estático]` | comportamento | `scripts/requirements.txt:1-6` e `requirements-windows.txt` — dependências com `>=` e sem lock nem hash, numa máquina que tem sessão autenticada de prontuário aberta. |

`achados = 22 causas-raiz distintas`
Contagem contra os tetos de 1.8: **3 bloqueantes** (teto 8) · **8 altas** (teto 10) · **12 médias+baixas** (teto 12) · **2 ruídos** (teto 10, Seção 5).
Sem transbordo.

---

## Seção 3 — Blocos de detalhe

### B-01 · bloqueante · `[executado]` · comportamento · eixo A/B/D

**`scripts/plataforma.py:116-119` e `scripts/plataforma.py:276-277`, consumidos por `scripts/hands.py:457`.**

`MODS` aceita duas grafias do mesmo modificador — `cmd` e `command` no macOS, `ctrl` e `control` no Windows — e ambas mapeiam para o modificador real:

```
116	    MODS = {"cmd": "command down", "command": "command down",
119	            "control": "control down"}
276	    MODS = {"ctrl": "ctrl", "control": "ctrl", "shift": "shift",
```

`COMBOS_NEGADOS` é indexado por `(frozenset(mods), key)` com **uma só** dessas grafias (`plataforma.py:121` `frozenset({"cmd"})`, `plataforma.py:279` `frozenset({"ctrl"})`), e `hands.py:457` consulta a tabela com o texto cru que o agente escreveu:

```
457	    motivo = P.COMBOS_NEGADOS.get((frozenset(mods), key))
```

**Entrada concreta:** o agente escreve `hands.py key control+s` em vez de `hands.py key ctrl+s` — grafia que `MODS` aceita, que `operacao-anydesk.md:130-134` não desautoriza (a tabela de recusas lista só `ctrl+s`) e que o `--help` do `key` sugere ao imprimir `MOD_MENU`.

**Comportamento errado observável** (bancada, plataforma falsa que só anota o que teria feito):

```
$ python3 probe_alias.py
== macOS (MOD_MENU=cmd) ==
  cmd+s          (salvar            ) -> recusado
  command+s      (salvar via ALIAS  ) -> PASSOU  [('TECLA ENVIADA AO SISTEMA', 's', ('command',))]
  cmd+p          (imprimir          ) -> recusado
  command+p      (imprimir via ALIAS) -> PASSOU  [('TECLA ENVIADA AO SISTEMA', 'p', ('command',))]
== Windows (MOD_MENU=ctrl) ==
  ctrl+s         (salvar            ) -> recusado
  control+s      (salvar via ALIAS  ) -> PASSOU  [('TECLA ENVIADA AO SISTEMA', 's', ('control',))]
  control+x      (recortar via ALIAS) -> PASSOU  [('TECLA ENVIADA AO SISTEMA', 'x', ('control',))]
[… 4 linhas omitidas]
```

A tecla chega a `plataforma.tecla()` (`plataforma.py:437-443` no Windows: `p.hotkey('ctrl', 's')`; `plataforma.py:241-244` no macOS: `key code 1 using {command down}`), ou seja, **Salvar de verdade** na janela do sistema do hospital.

**Impacto no fluxo real:** desfecho (iii). `SKILL.md:191-199` e `operacao-anydesk.md:118-138` fundam a garantia de somente-leitura nessa lista negra — "o `hands.py key` **recusa** esses combos". `alt+f4` e `delete` continuam corretamente recusados porque não têm alias; salvar, imprimir e recortar têm. `teste_regras.py:126-128` testa só a grafia canônica, por isso a suíte fica verde.

**Correção em uma frase:** normalizar cada modificador por `PLAT.MODS[m]` antes de montar o `frozenset` da consulta, e chavear `COMBOS_NEGADOS` pelo valor normalizado.

---

### B-02 · bloqueante · `[executado]` · comportamento · eixo A/B/E

**`scripts/hands.py:729` + `hardening/hooks/guardiao-laudos.py:213-215`.**

```
729	        p.add_argument("--anywhere", action="store_true", help="ignora a guarda (use com cuidado)")
```
```
213	if re.search(r"--anywhere", cmd):
214	    escala("O comando usa --anywhere, que desliga a guarda de foco e de janela. "
```

`argparse` aceita prefixo não ambíguo por padrão (`allow_abbrev=True`), e a regex do guardião casa a palavra inteira.

**Entrada concreta:** `python3 ~/.claude/skills/laudos-oct/scripts/hands.py click --any 5000 5000`, com o Finder em primeiro plano e o retângulo calibrado em 1600×1000.

**Comportamento errado observável** — o guardião não emite decisão nenhuma:

```
$ printf '%s' "...hands.py click --anywhere 100 200" | python3 guardiao-laudos.py
{"hookSpecificOutput": {..., "permissionDecision": "escalate", ...}}
$ printf '%s' "...hands.py click --anywh 100 200"    | python3 guardiao-laudos.py
$ printf '%s' "...hands.py click --any 100 200"      | python3 guardiao-laudos.py
                       (saída vazia — nenhuma decisão, o comando segue para a lista allow)
```

E o `hands.py` executa o clique:

```
$ python3 probe_anywhere.py         # foco='Finder', ponto fora do retângulo
  click 5000 5000              -> recusado (exit 4)
  click --any 5000 5000        -> PASSOU  [('CLIQUE REAL', 'click', 5000, 5000)]
  click --anywh 5000 5000      -> PASSOU  [('CLIQUE REAL', 'click', 5000, 5000)]
```

**Segundo defeito na mesma causa-raiz:** mesmo escrito por extenso, o veredito é `escalate`, que **não é valor aceito** de `permissionDecision` — a documentação do Claude Code lista `allow`, `deny`, `ask` e `defer` para `PreToolUse` (`https://code.claude.com/docs/en/hooks`). Um hook que sai com código 0 e JSON fora do schema não reporta decisão, e o comando cai na regra `Bash(python3 ~/.claude/skills/laudos-oct/scripts/hands.py *)` da lista `allow` (`settings-windows.json:8`, `settings-macos.json:6`), que é aprovação sem prompt. Se essa leitura do harness estiver certa, a regra 8 do guardião nunca funcionou em nenhuma grafia. Registrei a confirmação em runtime na Seção 12.

**Impacto no fluxo real:** desfecho (iii). `SEGURANCA.md:152-154` diz que "`--anywhere` é a única porta legítima para clicar fora do AnyDesk, e porta legítima sem aval humano é porta aberta"; `operacao-anydesk.md:73-75` diz "não use `--anywhere` para contornar guard". Com `--any`, o agente clica em coordenada arbitrária de qualquer aplicativo em foco, sem retângulo, sem foco protegido e sem escalonamento — inclusive em "Assinar" ou "Excluir" fora da área calibrada, e inclusive em janelas pessoais do operador.

**Correção em uma frase:** `argparse.ArgumentParser(allow_abbrev=False)` nos subparsers de ação, e trocar `escalate` por `ask`.

---

### B-03 · bloqueante · `[ausência]` · eixo A/D

**`AUSÊNCIA:` não existe estado de execução em disco — nem ledger de itens já processados, nem manifesto do que a rodada fez.**

**Âncora:** `scripts/laudo_pdf.py:929` (`print(json.dumps(res, ...))` — o único ponto do pacote onde um item termina) e `SKILL.md:291-293`, que promete o manifesto:

```
291	### Passo 7 — Relatório
292	No fim da fila, entregue ao usuário: quantos laudos saíram, quais foram para
293	`_PENDENTES/` e por quê, e onde estão os PDFs.
```

**Prova de busca, três partes:**

*(a) controle positivo* — o ponto do item (a) existe e foi lido:
```
$ rg -n -uu --hidden -g '!.git' -e 'jsonl' ref/ ; echo "exit=$?"
ref/laudos-oct/scripts/hands.py:104:    return CONFIG_DIR / "acoes.jsonl"
ref/laudos-oct/SKILL.md:349:(`~/.laudos_oct/acoes.jsonl`) — que é o que sustenta o laudo se alguém questionar.
[… 3 linhas omitidas]
exit=0
```

*(b) busca negativa sobre o pacote inteiro:*
```
$ rg -ni -uu --hidden -g '!.git' -e 'ledger|manifesto|manifest|retomada|ja_processado|processados|pendentes\.json' ref/ ; echo "exit=$?"
ref/laudos-oct/SKILL.md:349:(`~/.laudos_oct/acoes.jsonl`) — que é o que sustenta o laudo se alguém questionar.
exit=0
```
(o único acerto é a palavra "pendentes" dentro de outra frase; não há ledger, manifesto nem retomada)

*(c) leitura do trecho* — `sed -n '913,929p' ref/laudos-oct/scripts/laudo_pdf.py` mostra que o fim da emissão monta `res` e imprime, e o único efeito colateral persistente é a cópia para `_PENDENTES/` quando há marcador; nada é acrescentado a um registro por execução, e `hands.py:119` grava só evento de tela (tipo, coordenada, hash do texto), nunca a chave do exame nem o PDF emitido.

**Entrada que passa hoje:** fila de 6 pacientes no AnyDesk. O agente delega cada um a um subagente (`SKILL.md:245`), e `SKILL.md:287-289` manda descartar da memória os dados de cada paciente antes do próximo. O subagente do paciente 4 estoura o timeout, ou a sessão é interrompida no meio (`SEGURANCA.md:250` põe `Ctrl+C` no procedimento de emergência). Não existe, em disco, nada que diga que o paciente 4 estava na fila: não há PDF, não há cópia em `_PENDENTES/` (ele nunca chegou ao `laudo_pdf.py`), e `acoes.jsonl` tem só cliques e coordenadas. O relatório do Passo 7 é montado da memória do orquestrador, que já descartou aquele item. **O exame fica sem laudo e ninguém fica sabendo** — desfecho (v).

**Impacto no fluxo real:** é o modo de falha que combina com A-04 (no Windows a fila nunca começa por caminho declarado, então começa por caminho improvisado) e com o laço em prosa (0.2). A segunda execução também não sabe o que já saiu: reprocessar a fila inteira é o único caminho, e aí a guarda de colisão (`laudo_pdf.py:875`) recusa os já emitidos — o que é correto, mas transforma a retomada em leitura manual de mensagens de erro.

**Correção:** ver Seção 4 (não escrevo módulo novo para ausência estrutural).

---

### A-01 · alta · `[estático]` · comportamento · eixo D

**`scripts/laudo_pdf.py:794-797`, `543-555`, `558-571`, `595-610`; `hardening/settings-windows.json:10-12`; `hardening/hooks/guardiao-laudos.py:202-206`.**

A capacidade de embutir imagem de assinatura existe inteira:

```
794	    ap.add_argument("--assinar", action="store_true",
795	                    help="emite o DOCUMENTO FINAL assinado (exige a imagem de "
```
```
566	    if assinar:
567	        cam = caminho_assinatura(assinante)
568	        if cam and cam.suffix.lower() == ".png":
569	            img = [Image(str(cam), height=E(51), width=None, kind="proportional")]
```

E **dois documentos que o operador lê afirmam o contrário:**

- `SEGURANCA.md:259-262` — "Nenhuma imagem de assinatura acompanha o pacote — **e não existe caminho no código para embutir uma**. O parâmetro `--assinatura` do `laudo_pdf.py` foi removido: decisão em prosa com o mecanismo intacto no código é decisão que uma linha de comando desfaz."
- `INSTALACAO.md:210-212` — "não há caminho no código para embutir uma: a capacidade foi removida, não apenas desligada."

O parâmetro não foi removido: foi renomeado de `--assinatura` para `--assinar`, com o mecanismo intacto — exatamente o que o próprio texto diz que não se deve fazer. `SKILL.md:183-187` e `PENDENCIAS.md:10-41` descrevem `--assinar` como o passo final previsto, e `PENDENCIAS.md:22-30` dá o passo a passo de produzir as imagens.

**Por que a barreira não é humana:** a lista `allow` pré-aprova a linha inteira, com qualquer flag —
```
settings-windows.json:11	"Bash(python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py *)",
```
— e o guardião classifica `laudo_pdf.py` como comando de **leitura**, o que o isenta da regra 7 mesmo tocando o diretório protegido da skill:
```
202	E_LEITURA = (re.match(r"\s*(cat|less|more|head|tail|ls|dir|grep|egrep|rg|wc|file|stat|nl|"
204	                      r"(py|python3?)\s+\S*(hands|laudo_pdf|dividir_guia)\.py)\b",
```
Confirmado na bancada: `laudo_pdf.py --json p/laudo.json --assinar` no guardião devolve **saída vazia** — nenhuma decisão, nenhum prompt.

**Estado de hoje:** liguei a flag na bancada com um PNG sintético (imagem em branco, não é assinatura de ninguém) e o caminho **quebrou** com `TypeError` nos dois templates (M-01). Por isso, e pela regra de 1.7 ("se não conseguir ligar, vale alta pela presença"), este achado é **alta** e não bloqueante. Consertado o M-01 sem mexer no permissionamento, ele vira desfecho (iii).

**Correção em uma frase:** tirar `laudo_pdf.py` da regra `allow` genérica (deixando `allow` só para a forma sem `--assinar` e `ask` para a forma com), ou fazer `--assinar` exigir uma variável de ambiente que a sessão do agente não tem.

---

### A-02 · alta · `[executado]` · comportamento · eixo D

**`scripts/laudo_pdf.py:255-269` e `754-762`.**

```
256	    "raiz": {"hospital", "medico", "exame", "paciente", "data_exame", "data_laudo",
257	             "olhos", "equipamento", "macula", "nervo", "conclusoes", "sugestao",
258	             "observacoes", "extracao", "_nota"},
269	NAO_IMPRESSOS = {"extracao"}
```

`observacoes`, `equipamento` e `data_laudo` estão na allowlist de chaves da raiz — logo `valida()` não os reporta como "campo desconhecido" (`laudo_pdf.py:310-311`) — e não estão em `NAO_IMPRESSOS` — logo também não recebem o aviso de "não é impresso no corpo" (`laudo_pdf.py:312-314`). `build()` (`laudo_pdf.py:723-762`) nunca os lê. O laudo só imprime `observacoes` **de dentro do bloco de cada olho** (`laudo_pdf.py:480-481`).

**Entrada concreta** (`fixtures-rev/FX-OBS.json`, sintética): o exemplo de nervo, com o nome trocado e três chaves acrescentadas na raiz —
`"observacoes": "LIMITACAO TECNICA: opacidade de meios impediu avaliar o setor inferior."`, `"equipamento": "Cirrus 5000"`, `"data_laudo": "21/08/2026"`.

**Comportamento errado observável:**

```
$ HOME=$CASA python3 scripts/laudo_pdf.py --json fixtures-rev/FX-OBS.json
AVISO: conteúdo longo — entrelinha comprimida a 0.90; 1 página(s).
{ "pdf": ".../Laudo_FARROUPILHA_Zulmira_Teste_Obs_NO_AO_22_07_2026.pdf", "pendente": false, ... }
                       (nenhum outro AVISO no stderr)
$ python3 lerpdf.py .../Laudo_..._NO_AO_22_07_2026.pdf
   PDF contem 'LIMITACAO': False
   PDF contem 'opacidade': False
   PDF contem 'Cirrus':    False
   PDF contem 'MINUTA':    True
```

**Impacto no fluxo real:** a frase perdida é justamente a que `extracao-tela.md:97-103` e `templates-hospitais.md:250-255` mandam usar quando a avaliação é impossível — a única frase aprovada pelo Dr. Maeta para exame limitado. Posta um nível acima de onde o código a lê (erro plausível: `observacoes` existe nos dois níveis), ela desaparece sem sinal nenhum, e o laudo sai **completo e limpo**, com `pendente: false`, descrevendo um exame como se tivesse sido avaliado por inteiro. `templates-hospitais.md:179-180` promete o oposto: "O gerador avisa no stderr sobre campo desconhecido e sobre campo que ele não imprime. Nada documentado é ignorado em silêncio."

**Correção em uma frase:** mover `observacoes`, `equipamento` e `data_laudo` da allowlist da raiz para `NAO_IMPRESSOS`, que já emite o aviso — e, para `observacoes`, elevar a erro, porque conteúdo clínico descartado não é aviso.

---

### A-03 · alta · `[executado]` · comportamento · eixo D/G

**`scripts/laudo_pdf.py:426-438`, com `references/extracao-tela.md:39` e `scripts/teste_aceite.py:174`.**

```
434	    for k, (txt, cor) in CLASSIF.items():
437	            return txt, cor
438	    return v, PILL_NEUTRO
```

`CLASSIF` (`laudo_pdf.py:118-121`) tem só `dentro` e `fora`. A linha 438 é a saída de escape: **qualquer outra string vira pílula cinza com o texto escrito**. `olhos` tem allowlist (`OLHOS_OK`, `laudo_pdf.py:275-289`) e recusa o que não está nela; classificação de normalidade não tem.

Do lado do texto, o pacote afirma a regra fechada em cinco lugares (`SKILL.md:154-159`, `extracao-tela.md:29-31`, `extracao-tela.md:51`, `templates-hospitais.md:143-144`, `templates-hospitais.md:330-332`, `PENDENCIAS.md:53`) e a contradiz em um:

> `extracao-tela.md:39` — "**Nunca escreva percentil no laudo.** O laudo diz "dentro" / "fora" / **"limítrofe"** — nunca "p < 1%"."

Dez linhas depois de `extracao-tela.md:29` ter dito "Não existe `limitrofe` neste sistema". As duas leituras: (i) a categoria não existe, amarelo é `fora`; (ii) o laudo tem três categorias e uma delas é "limítrofe". A regra que deveria excluir (ii) é a tabela de `templates-hospitais.md:136-144` — mas essa mesma tabela documenta `| texto livre | pílula cinza com o texto que você escreveu |` na linha 140, isto é, descreve a linha 438 como recurso.

**Entrada concreta** (`fixtures-rev/FX-LIMITROFE.json`, sintética): exemplo de nervo com `nervo.OD.rel_classificacao = "limítrofe"` e `nervo.OE.cfn_classificacao = "borderline (p<5%)"`.

**Comportamento errado observável:**

```
$ HOME=$CASA python3 scripts/laudo_pdf.py --json fixtures-rev/FX-LIMITROFE.json
  "pdf": ".../Laudo_FARROUPILHA_Zulmira_Teste_Limitrofe_NO_AO_22_07_2026.pdf",
  "pendente": false,
$ python3 lerpdf.py .../Laudo_..._Limitrofe_...pdf
OLHO DIREITO
rela\347\343o escava\347\343o/papila \(\341rea\): 0,52
lim\355trofe
[… 6 linhas omitidas …]
camada de fibras nervosas \(m\351dia\): 99
borderline \(p<5%\)
```

Saiu impresso "limítrofe" e "borderline (p<5%)" — a categoria que não existe **e** o percentil que a linha 39 proíbe na mesma frase em que autoriza a categoria — num documento carimbado MINUTA, com `pendente: false`, sem cópia em `_PENDENTES/` e sem nenhum sinal para quem confere.

**E o teste afirma o contrário.** `teste_aceite.py:174-176`:
```
174	    diz("14. Nenhuma categoria 'limitrofe' aceita pelo código",
175	        "limitrofe" not in codigo.replace("`\"limitrofe\"`", ""))
```
É um grep no texto-fonte de `laudo_pdf.py`, não um teste de comportamento. Ele passa (`ok 14.` na saída de 43/43) enquanto o comportamento acima é o que se vê.

**Impacto no fluxo real:** desfecho (ii) na leitura mais direta — com a tela mostrando só cor (amarelo), a única redação que a entrada sustenta é "fora da curva de normalidade"; "limítrofe" é classificação sem fonte. E o efeito prático é suavizar: um parâmetro que a decisão 3.4 classifica como **fora** sai rotulado como intermediário, num documento que um CRM vai assinar.

**Correção em uma frase:** a regra é do médico responsável, e ela já está escrita — `rel_classificacao` e `cfn_classificacao` aceitam exatamente `dentro`, `fora` ou um marcador `[VERIFICAR]`/`[RECAPTURAR]`; qualquer outro valor é erro de `valida()`, não pílula cinza. O ponto do código é `laudo_pdf.py:296` (`valida`), com `pill_de` deixando de ter saída de escape.

---

### A-04 · alta · `[executado]` · comportamento · eixo E

**`scripts/hands.py:689-701`.**

```
689	    cfg_txt = settings.read_text(encoding="utf-8", errors="replace") if settings.exists() else ""
690	    tem_hook = "guardiao-laudos" in cfg_txt
691	    tem_sandbox = '"sandbox"' in cfg_txt
695	    if not (hook.exists() and tem_hook and tem_sandbox):
```

O `doctor` exige a string literal `"sandbox"` (com aspas) no `settings.json`. O perfil oficial do Windows **não a tem, por decisão declarada e correta**: `settings-windows.json:3` explica que não incluir um bloco `sandbox` inerte é deliberado, e `SEGURANCA.md:84-85` repete ("Foi decisão consciente **não** incluir um bloco `sandbox` no perfil do Windows: um bloco inerte pareceria proteção e não seria"). A chave que existe lá é `"$aviso_sandbox"`, que não casa a busca.

**Entrada concreta:** o operador segue `INSTALACAO.md:79-84` à risca — copia o hook e `settings-windows.json` para `~/.claude/` — e roda o Passo 5.

**Comportamento errado observável** (reprodução exata da checagem contra os dois perfis do pacote):

```
$ python3 - settings-windows.json
  tem_hook   ("guardiao-laudos" in texto): True
  tem_sandbox ('"sandbox"' in texto)     : False
$ python3 - settings-macos.json
  tem_hook   ("guardiao-laudos" in texto): True
  tem_sandbox ('"sandbox"' in texto)     : True
```

Logo, no Windows: `settings_endurecido: INCOMPLETO — hook=True sandbox=False`, `ok = False`, `VEREDITO: NAO_PRONTO`, `sys.exit(1)` (`hands.py:715-717`) — **sempre**, com o endurecimento corretamente instalado. E `COMO_RESOLVER` (`hands.py:697-700`) manda copiar exatamente o que já foi copiado.

**Impacto no fluxo real:** `SKILL.md:27` é categórico — "**Se o `doctor` falhar, pare e mostre ao usuário exatamente o que está faltando.** Não tente operar às cegas." Seguido à risca, o fluxo nunca começa no Windows, que é a plataforma que dá nome ao pacote. Não seguido, o operador e o agente aprendem a passar por cima do único sinal que detecta endurecimento ausente — e aí um `hook_guardiao: AUSENTE` de verdade some no mesmo ruído. `setup.ps1:54-58` amplifica: o instalador termina em `!! O diagnostico apontou pendencias acima. Resolva e rode de novo.` e nunca chega à linha de sucesso. `INSTALACAO.md:201` mapeia `settings_endurecido: INCOMPLETO` para "Falta o Passo 3b, ou o `settings.json` foi sobrescrito" — nenhum dos dois é o caso.

**Correção em uma frase:** condicionar a exigência do sandbox à plataforma — no Windows, `settings_endurecido` é `ok` com `tem_hook` e uma lista `deny` presente, e o relatório traz uma linha dizendo que ali a camada de kernel não existe.

---

### A-05 · alta · `[executado]` · comportamento · eixo C/D

**`scripts/laudo_pdf.py:863-864`.**

```
863	    if a.out:
864	        out = Path(a.out).expanduser()
```

Sem contenção, sem checagem de base e sem sanitização — em contraste com o caminho ancorado da linha 868, que o comentário das linhas 866-867 defende explicitamente ("Sempre ancorado, nunca herdando o diretório do JSON"). E `--out` **não aparece em nenhum documento do pacote**:

```
$ rg -n -uu --hidden -g '!.git' -e 'laudo_pdf.*--out|--out .*pdf|--sobrescrever|--base-nao-revisada' ref/ ; echo "exit=$?"
ref/laudos-oct/scripts/laudo_pdf.py:798:    ap.add_argument("--sobrescrever", ...
ref/laudos-oct/SKILL.md:274:caminho já existir, o script **recusa** — `--sobrescrever` só para refazer o mesmo
[… 4 linhas omitidas]
exit=0
```
As outras duas flags aparecem; `--out` não aparece em lugar nenhum — nem no `SKILL.md`, nem em `templates-hospitais.md:202-206`, nem em `INSTALACAO.md`.

**Entrada concreta:** `laudo_pdf.py --json <laudo>.json --out ~/OneDrive/Documentos/laudo.pdf`.

**Comportamento errado observável:**

```
$ HOME=$CASA python3 scripts/laudo_pdf.py --json assets/exemplo_macula_nova_prata.json \
    --out $CASA/OneDrive/Documentos/laudo.pdf
  "pdf": ".../casa/OneDrive/Documentos/laudo.pdf",
$ ls -la $CASA/OneDrive/Documentos/
-rw-r--r-- 1 root root 25853 Aug 21 13:10 laudo.pdf
```

**Impacto no fluxo real:** desfecho (iv). `~/OneDrive` é exatamente a pasta que `SEGURANCA.md:176-179` e `INSTALACAO.md:128-130` mandam manter fora do fluxo ("Laudo em pasta sincronizada é dado de paciente na nuvem de terceiro sem você decidir isso"), e a lista `deny` do Windows a protege — `settings-windows.json:113` `"Write(~/OneDrive/**)"`. Essa regra vale para a ferramenta `Write`; um PDF gravado por `laudo_pdf.py`, que está na lista `allow` com glob aberto, não passa por ela. No Windows não há sandbox de kernel para pegar a diferença. O guardião não inspeciona `--out`.

Não é bloqueante porque não exibi, no fluxo hoje implementado, a entrada que faz o agente escolher `--out`: a flag é invisível na documentação, então nada no fluxo normal a sugere. O caminho plausível — um texto na tela do sistema remoto pedindo que o laudo seja salvo em outra pasta, que o modelo lê por visão junto com os dados clínicos — é injeção de conteúdo (E10) e não tem barreira nenhuma no pacote; mas não o demonstrei com o agente real.

**Correção em uma frase:** conter `--out` na mesma raiz do caminho ancorado (`(OUT_ROOT.resolve() / relativo).resolve()` com checagem de contenção), ou remover a flag, que nenhuma documentação usa.

---

### A-06 · alta · `[executado]` · comportamento · eixo D/E

**`references/base/00-indice.md:3` e a linha 2 de cada um dos sete `references/base/0N-*.md`.**

```
$ rg -n -e 'rascunho|PENDENTE' ref/laudos-oct/references/base/ ; echo "exit=$?"
ref/laudos-oct/references/base/00-indice.md:3:`VERSÃO: 1.0-rascunho`  ·  `REVISADO POR: PENDENTE — não colocar em produção antes da revisão`
ref/laudos-oct/references/base/01-vocabulario.md:2:<!-- VERSÃO: 1.0-rascunho | REVISADO POR: PENDENTE — não colocar em produção antes da revisão -->
ref/laudos-oct/references/base/02-nervo.md:2:<!-- VERSÃO: 1.0-rascunho | REVISADO POR: PENDENTE — não colocar em produção antes da revisão -->
[… 5 linhas omitidas — 04, 05, 06, 07 e 03 trazem o mesmo carimbo …]
exit=0
```

A origem é `references/_fonte/base-cientifica.md:4-6`, que nunca teve o cabeçalho atualizado depois da revisão de 20/08 — e cuja linha 13 diz "Trocar o campo `REVISADO POR` só depois da revisão assinada". As linhas 9-11 do mesmo arquivo acrescentam: "As frases de laudo são composição minha, em registro neutro, e **não** foram calibradas contra laudos reais da clínica."

**Comportamento errado observável:** `REVISAO.json` declara `"versao_revisada": "1.0"` e o hash casa, então o selo está satisfeito e o gerador emite normalmente, reportando `"base": "VERSÃO: 1.0"` (saída de todas as emissões acima). A versão relatada vem de `laudo_pdf.py:393` (`reg.get("versao_revisada")`), nunca do carimbo dos arquivos.

**Impacto no fluxo real:** duas leituras irreconciliáveis para o agente, sem nada no pacote que exclua a errada. (i) A base está revisada — `SKILL.md:168-175`, `PENDENCIAS.md:52`, `REVISAO.json`. (ii) A base diz de si mesma, no topo de cada arquivo que o agente abre, "não colocar em produção antes da revisão". E `SKILL.md:141-142` fecha o círculo pelo lado errado: "Registre em `extracao.json` a linha `VERSÃO` do índice. Se um laudo for questionado depois, é isso que diz sob qual base ele foi escrito." — a proveniência que o pacote manda arquivar para o caso de contestação é literalmente `VERSÃO: 1.0-rascunho`, para um laudo emitido como produção.

**Correção em uma frase:** atualizar o cabeçalho de `references/_fonte/base-cientifica.md` para a versão e o revisor de 20/08, rodar `dividir_guia.py` e regravar `REVISAO.json` com o hash novo — nessa ordem, e uma vez só, com a revisão médica já feita.

---

### A-07 · alta · `[executado]` · comportamento · eixo A

**`scripts/hands.py:274-289`, especificamente 283-286.**

```
283	                p = alt; break
284	            alt2 = base / Path(path).name
285	            if alt2.exists():
286	                p = alt2; break
```

Quando o caminho relativo pedido não existe, `load_sidecar` tenta o mesmo caminho sob `~/Laudos_OCT/shots`, e, falhando, **casa só pelo nome do arquivo** em cima dessa raiz. O sidecar carrega `origin_pt` e `px_per_pt`, isto é, a transformação de pixel de imagem para ponto de tela: usar o sidecar errado converte a coordenada com a geometria de outra captura.

**Entrada concreta:** `operacao-anydesk.md:174` manda gravar os shots em `shots/<paciente>/`. O agente está no paciente B, pede `hands.py click --from shots/pacienteB/nav01.json 10 10`, e `shots/pacienteB/nav01.json` ainda não existe (o `shot` daquele paciente falhou, ou o subagente escreveu com outro nome). Existe `shots/nav01.json`, do paciente A, com `origin_pt = (2000,1500)`.

**Comportamento errado observável:**

```
$ python3 probe_extra.py
== (b) --from com sidecar inexistente cai no de OUTRO paciente, por basename ==
   existe shots/nav01.json (paciente A, origem 2000,1500); shots/pacienteB/nav01.json NÃO existe
   -> clicou: [('CLIQUE', 'click', 2010, 1510)]  (esperado: PARAR, sidecar do paciente B não existe)
```

Em vez de parar, o clique saiu em (2010,1510) — geometria do paciente A, dentro do retângulo da janela do AnyDesk, portanto invisível para a guarda de retângulo.

**Impacto no fluxo real:** é a variante de carryover que `SKILL.md:287-289` e `operacao-anydesk.md:172-176` não cobrem, porque não é contaminação de texto: nenhum dado clínico atravessa, só a **transformação de coordenada**. O clique cai num ponto que o modelo não escolheu, dentro do sistema do hospital, e o único sinal é a tela não mudar como esperado — que `operacao-anydesk.md:64-67` manda tratar reavaliando, não parando. `hands.py:288` já tem a mensagem de fail-fast pronta; ela só não é alcançada porque a linha 284 sempre encontra alguma coisa.

**Correção em uma frase:** remover a busca por basename (linhas 284-286) e deixar só a reancoragem do caminho relativo completo, caindo no `die` da linha 288 quando não houver.

---

### A-08 · alta · `[executado]` · comportamento · eixo A/C

**`scripts/hands.py:119-133`.**

```
120	    """Rastro append-only de tudo que tocou a tela. Nunca falha silenciosamente."""
126	    try:
128	        with audit_path().open("a") as f:
132	    except Exception as e:
133	        print(f"AVISO: não consegui gravar auditoria: {e}", file=sys.stderr)
```

A exceção é avisada e engolida; a função retorna e o chamador segue para a ação. E `limites()` (`hands.py:155-180`) decide **lendo esse mesmo arquivo** por `audit_recentes()`, que também engole falha e devolve `[]` (`hands.py:150-152`). Com o rastro ingravável, o teto de taxa, o detector de loop e a trilha de auditoria desaparecem **juntos**, e nenhum deles recusa nada.

**Entrada concreta:** `~/.laudos_oct/acoes.jsonl` deixa de ser gravável — disco cheio no meio de uma fila, permissão alterada, ou o caminho ocupado por um diretório (foi o que usei para reproduzir de forma determinística).

**Comportamento errado observável:**

```
$ python3 probe_extra.py
== (f) rastro de auditoria não gravável: o teto de taxa e o detector de loop ainda valem? ==
   3 cliques idênticos com rastro OK -> o 3º deveria ser 'loop travado':
ERRO: loop travado: 'click:100,100' repetida 3x em 30s. [...]
      4º clique recusado (detector de loop OK)
   com o rastro inutilizável: 60 cliques idênticos seguidos executados (teto=40/min, loop=3)
   ações que chegaram à plataforma: 60
```

Sessenta cliques idênticos na mesma coordenada, onde o limite declarado é três em trinta segundos e quarenta por minuto. O único sinal é uma linha de `AVISO` no stderr por ação — no meio de saída JSON que o agente lê como sucesso (`{"ok": "click", ...}` continua sendo impresso).

**Impacto no fluxo real:** `SKILL.md:65-68` promete "Toda ação de tela é registrada em `~/.laudos_oct/acoes.jsonl`, com teto de taxa (40/min, 600/h ...) e detector de loop"; `SEGURANCA.md:21` lista "loop de milhares de cliques queimando token e martelando o sistema remoto" como um dos cinco riscos que o desenho existe para conter; `SKILL.md:347-349` diz que o rastro "é o que sustenta o laudo se alguém questionar". Os três se perdem ao mesmo tempo, sem parar, exatamente no cenário em que mais importam. O docstring da linha 120 afirma "Nunca falha silenciosamente" — ele avisa, mas não impede, que é o que o resto do desenho pressupõe.

**Correção em uma frase:** falhar **fechado** — se `audit()` não conseguir gravar, `die()` com o motivo, do mesmo jeito que a guarda de foco recusa quando não consegue ler quem está em primeiro plano (`hands.py:355-357`, que é o precedente do próprio pacote).

---

## Seção 4 — Patch mínimo

Seis, todos mecânicos, todos dentro de arquivo existente:

**P1 · B-01 · `scripts/hands.py:445-457`** — normalizar o modificador antes de consultar a tabela.
```python
    parts = [p.strip().lower() for p in a.combo.split("+")]
    key, mods = parts[-1], parts[:-1]
    ...
    if any(m not in P.MODS for m in mods):
        die(...)
-   motivo = P.COMBOS_NEGADOS.get((frozenset(mods), key))
+   # A tabela é chaveada por UMA grafia; MODS aceita duas ('cmd'/'command',
+   # 'ctrl'/'control'). Sem normalizar, 'control+s' não casa 'ctrl+s' e salva.
+   canon = frozenset(P.MODS[m] for m in mods)
+   motivo = next((v for (mm, kk), v in P.COMBOS_NEGADOS.items()
+                  if kk == key and frozenset(P.MODS[m] for m in mm) == canon), None)
    if motivo:
```

**P2 · B-02 · `scripts/hands.py:723`** — desligar a abreviação de flag.
```python
-   ap = argparse.ArgumentParser(description="Mãos e olhos do agente de laudos OCT (macOS)")
+   # allow_abbrev=False: '--any' resolvia para '--anywhere' e desligava as guardas
+   # sem casar a regra 8 do guardião, que procura o texto '--anywhere'.
+   ap = argparse.ArgumentParser(description="Mãos e olhos do agente de laudos OCT",
+                                allow_abbrev=False)
```

**P3 · B-02 · `hardening/hooks/guardiao-laudos.py:62` e `213`** — usar um veredito que o harness aceita, e casar o prefixo.
```python
-escala = lambda m, c: decide("escalate", m, c)
+escala = lambda m, c: decide("ask", m, c)   # PreToolUse aceita allow/deny/ask/defer
...
-if re.search(r"--anywhere", cmd):
+if re.search(r"--any\w*", cmd):
```

**P4 · A-08 · `scripts/hands.py:132-133`** — falhar fechado, como a guarda de foco já faz.
```python
    except Exception as e:
-       print(f"AVISO: não consegui gravar auditoria: {e}", file=sys.stderr)
+       # Falha FECHADO: limites() decide lendo este arquivo. Sem ele, teto de taxa e
+       # detector de loop somem juntos e nada mais recusa nada.
+       die(f"não consegui gravar o rastro de auditoria ({e}). Nenhuma ação de tela "
+           f"acontece sem rastro. Verifique {audit_path()} e o espaço em disco.", 7)
```

**P5 · A-07 · `scripts/hands.py:284-286`** — tirar a busca por basename.
```python
            alt = base / path
            if alt.exists():
                p = alt; break
-           alt2 = base / Path(path).name
-           if alt2.exists():
-               p = alt2; break
+           # Sem casar por basename: 'shots/pacienteB/nav01.json' inexistente caía
+           # em 'shots/nav01.json' do paciente ANTERIOR e o clique era convertido
+           # com a geometria dele.
```

**P6 · A-02 · `scripts/laudo_pdf.py:269`** — devolver o aviso que a documentação promete.
```python
-NAO_IMPRESSOS = {"extracao"}
+NAO_IMPRESSOS = {"extracao", "equipamento", "data_laudo"}
+# 'observacoes' na raiz é conteúdo clínico, não metadado: some do PDF sem sinal.
+# Vira erro em valida(), junto dos outros campos obrigatórios (ver linha 321).
```
(a elevação de `observacoes` a erro é uma linha em `valida()`, dentro do bloco de presença já existente.)

**Ausências estruturais — uma linha cada, sem módulo novo:**

- `AUSÊNCIA B-03 → entra em laudo_pdf.py:929 (fim da emissão) e num ponto de abertura de fila que o SKILL.md hoje não tem → bloqueia quando a chave <hospital, paciente, data, exame, olho> já consta do registro da rodada → deixa passar quando a chave é nova, e nesse caso grava a linha antes de o item ser dado por concluído.`
- `AUSÊNCIA M-05 → entra em laudo_pdf.py:807 (leitura do laudo.json) → bloqueia quando não existe <pasta_paciente>/extracao.json com id do exame, data, olho e cada valor usado no texto com o campo de origem → deixa passar quando existe e os valores citados no laudo constam dele.`
- `AUSÊNCIA M-07 → entra em laudo_pdf.py:869 (mkdir do destino) → bloqueia nada; restringe pasta e arquivo pelo mesmo PLAT.restringir() que hands.py:107 já usa para o rastro.`

**Regra clínica (não escrevo código):** a classificação de normalidade aceita **`dentro`, `fora`, ou um marcador de pendência — e nada mais**; quem decide é o médico responsável, e a decisão já está registrada (formulário 20/08/2026, item 3.4). O ponto do código onde ela entra é `laudo_pdf.py:296` (`valida`), não `pill_de`.

---

## Seção 5 — Ruído a remover

Orçamento próprio de 10; o eixo G rendeu 2.

**R-01 · `scripts/teste_aceite.py:251`** — `importlib.reload(lp) if False else None`.
Alcançabilidade, as quatro rotas:
- (a) `rg -n -uu --hidden -e 'importlib.reload' ref/` → só esta linha. `exit=0`, 1 acerto, nenhuma citação em `SKILL.md` nem em `references/`.
- (b) não há flag nem subcomando que a alcance: a linha está no corpo de `main()`, com condição literal `False`.
- (c) `rg -n -uu --hidden -e 'getattr\(|importlib|__import__|entry_points|handlers\[' ref/` → os acertos são os `spec_from_file_location` legítimos das linhas 238, 252, 262 e de `teste_regras.py:62`; nenhum despacho dinâmico chega aqui.
- (d) nenhum teste ou hook a invoca — ela **é** o teste.
Remoção não muda comportamento: o ramo nunca executa (confirmado por `vulture`: `unsatisfiable 'ternary' condition (100% confidence)`).

**R-02 · `scripts/requirements.txt:1-6` e `scripts/requirements-windows.txt:1-6`** — não é ruído no sentido de código morto, e por isso está no índice como baixa e não aqui; registro só que o `pip install` de `setup.sh:16-21` e `setup.ps1:23` resolve `>=` na hora, sem lock nem hash, numa máquina com sessão de prontuário aberta.

**Nenhum outro achado de ruído sobreviveu às quatro rotas.** Os 10 restantes do `vulture` são override de framework (`Flowable.wrap`/`draw` chamados pelo `reportlab`, `pyautogui.FAILSAFE` lido pela biblioteca) e o `ruff` não encontrou import, redefinição nem variável sem uso. `LINHA_ASSINATURA_FARROUPILHA` (`laudo_pdf.py:540`) é flag booleana que nenhum chamador altera, mas está documentada na própria linha como interruptor deliberado de layout e sua remoção mudaria o desenho do laudo — não é ruído.

---

## Seção 5.5 — Cobertura por eixo

`A (identidade, isolamento e estado) | B-03, A-07, A-08, M-02 | verifiquei: onde o laço executa, carryover de estado e de destino, colisão de nome, idempotência, escrita atômica, teto/loop | como: SKILL.md:241-246 e busca negativa por invocação por item; hands.py:274-289 e 119-180 exercitados em bancada; laudo_pdf.py:870-881 com FX-DUP | não coberto: contaminação de contexto entre pacientes no agente real (exige o modelo — Seção 12)`

`B (segurança técnica do acesso) | B-01, B-02 | verifiquei: credencial, artefato de sessão, TLS, injeção de shell/AppleScript, path traversal, desserialização, execução dinâmica, permissões, superfície de ferramentas, dependências | como: grep de credencial e de URL com senha (exit=1); rg de verify=False/ignore_https_errors (exit=1); slug() exercitado com FX-NOME; teste_regras.py:131-134 confirma que a tabela fechada de teclas barra injeção de AppleScript | não coberto: nada — não há rede, banco, XML nem desserialização no pacote`

`C (privacidade: egress em três camadas) | A-05, M-04, M-07 | verifiquei: destinos literais (URL, host:porta, UNC, socket, telemetria), o que chega ao modelo, o rastro do agente, minimização, PHI em log/nome de arquivo/metadado, fixtures | como: as cinco buscas de C1 (URLs: 4 acertos, todos de documentação de instalação; host:porta e sockets: exit=1); redige() exercitado; PIL/getexif nos três PNG; rg de CPF (exit=1) | não coberto: o que o provedor do modelo retém — é decisão jurídica, e SEGURANCA.md:195-206 já a registra como fato técnico e a encaminha`

`D (segurança clínica do laudo) | A-01, A-02, A-03, A-06, M-01, M-03, M-05, M-06 | verifiquei: conteúdo além da entrada, defaults do template, validador final, coerência achado↔modalidade, procedência do dígito, polaridade, descrição↔conclusão, marca de rascunho, destino, falha fechada | como: valida() exercitado com FX-VAZIO/FX-CONFLITO/FX-SEMOLHO/FX-OBS/FX-LIMITROFE; carimbo MINUTA extraído do PDF em todas as emissões; selo da base quebrado e restaurado | não coberto: D1 (laudo mais rico que a entrada) e D4/D9 só existem no texto — não há chamada ao modelo em código, então a redação não é exercitável aqui (Seção 12)`

`E (engenharia de skill) | A-04, B-02, M-10 | verifiquei: frontmatter (YAML válido, name em kebab-case, description com 561 caracteres e sem < >), progressive disclosure, prosa vs. código, instrução ambígua, testabilidade, evals, proveniência | como: yaml.safe_load do frontmatter; varredura de órfãos e de ponteiro quebrado (zero de cada, considerando 00-indice.md); as duas suítes rodadas; mutação de OLHOS_OK | não coberto: disparo real da description — exige sessão com a skill instalada (Seção 12)`

`F (interior do template) | nenhum | verifiquei: se existe template binário e o que os assets carregam de metadado | como: find por .docx/.dotx/.docm/.dotm/.pdf/.dcm → exit=0 sem acertos; file + PIL info/getexif + strings nos três PNG de marca → info e exif vazios, nenhum nome próprio, nenhum caminho local | não coberto: nada. **§F é não aplicável — nenhum .docx/.dotx no pacote.** O template é código (laudo_pdf.py:639-683 desenha o timbre), e foi auditado como código; a pergunta que sobra está na Seção 11`

`G (ruído de implementação) | R-01, R-02, M-08, M-09, A-03 (o teste 14) | verifiquei: símbolo sem chamador pelas quatro rotas, caminho inalcançável, config órfã, literal repetido, sobras, comentário divergente do código, teste decorativo | como: vulture --min-confidence 60, ruff F401/F811/F841 (limpo) e C901, mutação de lateralidade nas duas suítes | não coberto: coverage não rodou (corte declarado na Seção 12)`

---

## Seção 6 — Controle negativo

Cinco itens verificados e **corretos**, um por desfecho bloqueante de 1.7.

**(i) laudo no paciente ou olho errado — `scripts/laudo_pdf.py:275-289` e `332-347`.**
`OLHOS_OK` é allowlist fechada, sem default, e `valida()` reconcilia o olho declarado com os olhos preenchidos antes de emitir. Exercitado:
```
--- FX-OD        -> "pdf": ".../Laudo_FARROUPILHA_Teste_Mono_OD_NO_OD_22_07_2026.pdf"
--- FX-CONFLITO  -> ERRO: 'olhos' declara OD mas há dados de ['OE']. O nome do arquivo sairia
                    com um olho e o corpo com outro.
--- FX-SEMOLHO   -> ERRO: 'olhos' ausente. Declare OD, OE ou AO — o laudo não assume ambos
                    os olhos por omissão.
```
E `laudo_pdf.py:778-787` (`slug`) é allowlist `[^A-Za-z0-9]`, com nome reservado do Windows e truncamento: `"../../etc/passwd" → 'etc_passwd'`, `"CON" → 'N_CON'`, `"José D'Ávila/Souza" → 'Jose_D_Avila_Souza'`, `"   " → 'Paciente'`.

**(ii) conteúdo clínico que não está na entrada — `scripts/laudo_pdf.py:321-349` (bloco de presença de `valida`).**
Campo obrigatório ausente **bloqueia**, não vira placeholder: `paciente.nome`, `data_exame`, `hospital`, `olhos`, `conclusoes` e "nenhum olho preenchido" são erros com mensagem que explica o que sairia errado. E `bloco_olho:447-450` faz o inverso do default: campo vazio **some** do laudo em vez de virar "—" ou "sem alterações". Verificado lendo `sed -n '296,355p'` e exercitado por FX-CONFLITO/FX-SEMOLHO acima. (A exceção é A-03, que é sobre o *valor* da classificação, não sobre presença.)

**(iii) assinatura, publicação ou escrita na origem sem ação humana — `scripts/laudo_pdf.py:615-636` e `686-721`.**
O carimbo de minuta é desenhado no `onPage` de **todas** as páginas, não é suprimível por config, e os metadados do PDF não trazem o nome do médico enquanto não houver `--assinar`. Extraído do PDF real:
```
$ python3 lerpdf.py .../Laudo_FARROUPILHA_Zulmira_Teste_Obs_NO_AO_22_07_2026.pdf
MINUTA \227 CONFERIR E ASSINAR \267 gerada com apoio automatizado
Documento sem validade at\351 a assinatura do m\351dico respons\341vel
$ ... /Author = 'Minuta gerada com apoio automatizado \204 n\343o assinada'
        /Title  = 'Minuta de laudo \204 TOMOGRAFIA DE COER\312NCIA \323PTICA...'
```
E `Title`/`Author` não carregam nome de paciente (`laudo_pdf.py:703-712`), o que também fecha o vazamento por índice do sistema de arquivos.

**(iv) PHI ou credencial para destino não declarado — o pacote não fala com a rede.**
```
$ rg -ni -uu --hidden -g '!.git' -e 'socket\.socket|paramiko|ftplib|smtplib|pynetdicom|storescu|requests|httpx|urlopen|urllib' ref/ ; echo "exit=$?"
[4 acertos, todos textos de documentação e de lista deny sobre robocopy/net use]
exit=0
$ grep -rInoE '\b[A-Za-z0-9.-]+:(21|22|25|104|389|445|465|587|2575|4242|8080|8443|11112)\b' ref/ ; echo "exit=$?"
exit=1
$ grep -rInE '(senha|password|token|api[_-]?key|bearer|authorization|jwt|cookie)["'"'"' ]*[:=]' ref/ ; echo "exit=$?"
exit=0    (nenhuma linha)
```
Nenhum host, porta, share, socket, telemetria ou credencial no pacote; nenhum CPF; os quatro `assets/*.json` são sintéticos e se declaram assim. `WebFetch` e `WebSearch` estão negados nos dois perfis.

**(v) exame pendente perdido em silêncio — `scripts/laudo_pdf.py:870-881`.**
A guarda de colisão de nome funciona, e funciona também no caso insensível à caixa que o NTFS impõe: varre a pasta comparando em minúsculas e **recusa** em vez de sobrescrever. Exercitada sem querer, o que é a melhor prova:
```
$ python3 scripts/laudo_pdf.py --json assets/exemplo_nervo_farroupilha.json --assinar
ERRO: já existe .../Laudo_FARROUPILHA_Fulana_de_Tal_Exemplo_NO_AO_22_07_2026.pdf
  Emitir apagaria o laudo anterior em silêncio.
```
E a data do exame está no nome (`laudo_pdf.py:861-862`), então o acompanhamento do mesmo paciente e olho não colide com o exame anterior. Isso cobre a perda por **sobrescrita**; a perda por **item que nunca chegou ao script** é B-03.

---

## Seção 7 — Defeitos fora do catálogo

Passagem deliberada sem o catálogo aberto, guiada por "o que acontece na terça-feira em que o AnyDesk atualiza, a tela trava ou o disco enche?".

1. **A-08 saiu daqui** — "e se o disco encher no meio da fila?". O rastro para de gravar, e com ele param os dois freios que dependem dele, sem que nada pare.
2. **A-07 saiu daqui** — "e se o `shot` do paciente B falhar e o agente pedir o sidecar mesmo assim?". Cai no do paciente anterior por nome.
3. **A-04 saiu daqui** — "o operador segue o INSTALACAO.md à risca no Windows; o que ele vê?". `NAO_PRONTO` para sempre.
4. **`cmd_aguardar` não passa pelo teto de taxa.** `hands.py:553-612` captura a tela a cada `--intervalo` (padrão 1,0 s) por até `--timeout` (padrão 45 s), e só audita **uma** linha no fim (`hands.py:602`). São até 45 capturas de tela cheia do sistema do hospital que não contam para o teto de 40/min nem aparecem no rastro individualmente. Não é achado pelo 1.7 — os temporários são apagados no `finally` (`hands.py:549-550`) e a captura não altera nada —, mas é a única ação de tela cujo custo real o rastro não reflete, e `SEGURANCA.md:242-244` manda o operador diagnosticar a fila justamente pelo `log --resumo`.
5. **`estado_da_base()` recusa por base ausente, mas `dividir_guia.py` pode deixar `references/base/` num estado que passa.** `dividir_guia.py:100-102` aborta preservando a base antiga se nenhuma seção mapear — correto. Mas `destino_de()` (`dividir_guia.py:42-50`) manda qualquer seção não prevista para `99-<slug>.md`, que entra no glob de `hash_da_base()`. Renomear um título no guia-fonte cria um `99-*.md`, muda o hash e derruba o selo — o que é o comportamento certo, e registro aqui só porque o operador vai ler "a base mudou depois da revisão" sem ter mudado conteúdo clínico nenhum.

Procurei também, e **não achei**, defeito em: conversão de coordenada Retina (`hands.py:292-294` é uma linha e o sidecar carrega tudo), contenção do `purge` (`hands.py:494-500`, testada), escape de AppleScript (`plataforma.py:246-248` mais a tabela fechada de teclas), e escrita atômica do PDF (`laudo_pdf.py:896-905`, `os.replace` com `.part` e `finally`).

---

## Seção 8 — Testes que faltam

1. **Alias de modificador.** Para cada par de `COMBOS_NEGADOS`, chamar `cmd_key` com **as duas** grafias aceitas por `MODS` (`ctrl+s` e `control+s`; `cmd+q` e `command+q`; `alt+f4` e `option+f4` onde existir) e asseverar `SystemExit` nas duas. Hoje `teste_regras.py:126` testa só `MOD_MENU`.
2. **Abreviação de flag.** `hands.py click --any 5000 5000` com foco em `"Finder"` deve recusar com exit 4, e `plataforma.mouse` não deve ter sido chamado.
3. **`--assinar` com a imagem presente.** Gerar um PNG sintético em `~/.laudos_oct/assinaturas/assinatura_cassiano.png`, emitir com `--assinar`, e asseverar: exit 0, o PDF **não** contém "MINUTA — CONFERIR E ASSINAR", `/Author` é o nome do signatário, e há uma imagem a mais que na minuta. É o teste que teria pegado M-01. `teste_aceite.py:230` só cobre o caso sem a imagem.
4. **Lateralidade monocular ponta a ponta.** Fixture com `olhos: "OD"` e dados só em `OD`: o nome do arquivo termina em `_OD_` e o corpo diz `OLHO DIREITO`. Com `OLHOS_OK` mutado para `{"OD": "OE", ...}`, este teste tem de **falhar** — hoje 101 asserções ficam verdes com a inversão.
5. **Campo de raiz descartado.** `laudo.json` com `observacoes` na raiz: o processo deve terminar diferente de 0, ou no mínimo imprimir no stderr o aviso que `templates-hospitais.md:180` promete. Hoje sai limpo.
6. **Classificação fora da lista fechada.** `rel_classificacao: "limítrofe"` e `cfn_classificacao: "borderline (p<5%)"` devem abortar a emissão; o PDF não deve existir. É um teste de comportamento no lugar do grep de `teste_aceite.py:174`.
7. **Rastro ingravável.** Tornar `acoes.jsonl` não gravável e asseverar que o **primeiro** clique seguinte é recusado, e que `plataforma.mouse` não foi chamado.
8. **Sidecar de outro paciente.** Com `shots/nav01.json` existindo e `shots/pacienteB/nav01.json` não, `click --from shots/pacienteB/nav01.json 10 10` deve recusar com "sidecar não encontrado".
9. **`doctor` no perfil oficial do Windows.** Apontar `HOME` para uma casa com `hardening/settings-windows.json` copiado como `~/.claude/settings.json` e o hook em `~/.claude/hooks/`, e asseverar `settings_endurecido == "ok"`.
10. **`--out` contido.** `--out /caminho/fora/laudo.pdf` deve recusar; `--out laudo.pdf` (relativo à raiz de saída) deve gravar dentro de `~/Laudos_OCT`.
11. **Selo cobrindo o índice.** Acrescentar uma linha a `references/base/00-indice.md` e asseverar que `estado_da_base()[0] is False`.

---

## Seção 9 — Lacunas de projeto (não defeito)

1. Não existe chave imutável de exame (equivalente a Accession Number) atravessando extração → redação → gravação; a identidade é o nome do paciente mais a data, ambos transcritos por visão.
2. A folha de evidência de D15a poderia ser o próprio `extracao.json` gravado ao lado do PDF, com cada valor impresso ligado ao campo de origem — conferir viraria comparar, não ler plausibilidade.
3. O laço do lote em prosa poderia ser um script de fila que invoca um subprocesso por exame, deixando o modelo como leitor de tela dentro de cada item em vez de orquestrador de todos.
4. O canário de lote de A13 (taxa de campos vazios e similaridade entre os laudos da rodada, com abortar acima do limiar) não existe e não foi prometido; num fluxo de 20 pacientes é o que detecta a tela do aparelho ter mudado de layout.
5. `--dry-run` existe para clique e scroll (`hands.py:730`, `769`) mas não para `key` nem `type`, e `SEGURANCA.md:234-236` monta o Dia 1 do modo sombra em cima dele.
6. O guardião filtra por lista negra de nomes de comando; `python3 -c` com o nome do módulo montado por concatenação não casa nenhum padrão de `TELA`. No macOS o sandbox de kernel fecha; no Windows não há equivalente, como o próprio pacote declara.
7. `LINHA_ASSINATURA_FARROUPILHA` (`laudo_pdf.py:540`) é decisão de layout num literal de módulo; junto de `ESCALA`, `MAX_COMPONENTE` e `RESERVA_DIAGNOSTICA`, formaria um bloco de configuração de documento.
8. `references/_fonte/base-cientifica.md` não é selado por nada; o selo protege o derivado, não a origem.

---

## Seção 10 — Consequências de decisões fechadas

Não há campo de decisões fechadas preenchido em §3 (ver Seção 11). As decisões que o **próprio pacote** declara fechadas e cujas consequências cabem aqui:

- `consequência de decisão fechada: não incluir bloco sandbox no perfil Windows (settings-windows.json:3, SEGURANCA.md:84) → a contenção de escrita e o bloqueio de rede viram filtro de texto do comando, e um caminho não previsto passa (A-05 é um exemplo concreto: --out atravessa o deny de Write) → mitigação possível DENTRO da decisão: a conta padrão sem privilégio de administrador (Camada 2) e o login somente-leitura no hospital (Camada 1), que o próprio SEGURANCA.md:39-60 já eleva a sustentação do resto no Windows.`
- `consequência de decisão fechada: sem campo de equipamento, "a imagem que ele lauda é sempre a mesma" (PENDENCIAS.md:54) → nenhuma classificação depende do aparelho, o que é coerente porque a normalidade é transcrita e nunca calculada; em compensação, a comparação evolutiva entre exames de plataformas diferentes fica sem barreira em código (só a prosa de extracao-tela.md:118-119 avisa) → mitigação possível DENTRO da decisão: registrar em extracao.json o rótulo do aparelho como texto livre, sem criar campo no laudo nem regra de classificação.`
- `consequência de decisão fechada: sem índice de qualidade e sem limiar (PENDENCIAS.md:55) → exame ruim é laudado, e o único sinal de limitação é uma frase em observacoes — que hoje some quando escrita na raiz (A-02) → mitigação possível DENTRO da decisão: fazer valida() recusar observacoes na raiz, para que a única frase aprovada de limitação nunca se perca.`
- `consequência de decisão fechada: sem assinatura digitalizada (SEGURANCA.md:258) → a decisão está escrita em prosa em dois documentos, e o mecanismo continua no código com a flag pré-aprovada (A-01), que é exatamente o que SEGURANCA.md:261 diz que não se deve fazer → mitigação possível DENTRO da decisão: manter --assinar, tirá-lo da lista allow e exigir uma variável de ambiente que só o operador põe.`

---

## Seção 11 — Perguntas ao autor

**DESCONHECIDOS de §3 (fora da cota).** O prompt veio com o bloco de contexto em branco; nada foi preenchido por dedução.

- `Stack, linguagem e forma de acesso: DESCONHECIDO → o pacote é inequívoco (Python 3 + captura de tela + evento sintético de mouse/teclado sobre AnyDesk), então este campo não muda nada no relatório.`
- `Sistema de terceiros: DESCONHECIDO → se for um sistema com API ou export DICOM, P1 muda de figura: haveria chave de exame para ancorar identidade, e B-03 e a lacuna 1 deixariam de ser sobre memória do agente.`
- `Destino dos laudos: DESCONHECIDO → se ~/Laudos_OCT estiver dentro de OneDrive/iCloud na estação real, A-05 deixa de precisar de --out para produzir o desfecho (iv) e vira bloqueante.`
- `Já roda com paciente real: DESCONHECIDO → se sim, e desde quando, B-01 e A-08 passam a ter escopo retroativo: é preciso olhar acoes.jsonl e guardiao.log das rodadas já feitas.`
- `Equipamentos e protocolos no fluxo: DESCONHECIDO → a decisão 3.1/3.2 declara o aparelho irrelevante, então este campo não altera severidade nenhuma aqui.`
- `Sistema operacional da máquina da clínica: DESCONHECIDO → o pacote se chama SkillLaudoWindowsV1, mas se a estação for macOS, A-04 cai para lacuna e B-02 fica contido pelo Seatbelt; se for Windows, ambos valem inteiros.`
- `Decisões fechadas, fora de discussão: DESCONHECIDO → li como fechadas apenas as que o próprio pacote declara (Seção 10); se houver outras, alguns itens da Seção 9 podem já estar decididos.`

**Perguntas de decisão (12 no máximo; são 9):**

1. `--out` é usado por alguém, ou é sobra? Se for sobra, remover fecha A-05 sem discussão.
2. As imagens de assinatura de P1 já foram produzidas e postas em `~/.laudos_oct/assinaturas/` em alguma estação? Se sim, A-01 tem escopo hoje, não amanhã.
3. Qual das duas afirmações vale — `SEGURANCA.md:260` ("não existe caminho no código") ou `PENDENCIAS.md:12` (`--assinar` como fluxo previsto)? Uma das duas precisa ser reescrita, e a escolha muda o patch.
4. Alguém rodou `laudo_pdf.py --assinar` com a imagem presente? A quebra de M-01 é imediata e determinística; se ninguém viu, é sinal de que o caminho nunca foi exercitado fora do teste 31.
5. `extracao-tela.md:39` autoriza "limítrofe"; as outras cinco menções proíbem. Confirma que a linha 39 é erro de redação e que a regra fechada é a de duas categorias?
6. A base foi mesmo revisada em 20/08 e o carimbo `1.0-rascunho / PENDENTE` é só o cabeçalho não atualizado (A-06)? Ou o `REVISAO.json` foi gravado antes de a revisão terminar? A resposta muda A-06 de "erro de carimbo" para "selo sem lastro".
7. O `settings-windows.json` da estação real é o do pacote, ou foi mesclado com um `settings.json` que já existia (`INSTALACAO.md:91-93`)? Se foi mesclado, o `doctor` pode estar dizendo `INCOMPLETO` por um segundo motivo além de A-04.
8. Os valores clínicos dos quatro `assets/exemplo_*.json` (áreas de papila, relações E/P, datas de nascimento) foram inventados, ou derivados de laudos reais com o nome trocado? Se derivados, é PHI parcialmente anonimizada dentro do pacote, e a correção não é apagar o arquivo — é avisar quem responde pelo tratamento de dados na clínica e mapear por onde o ZIP já circulou.
9. **Pergunta agregada, jurídica — registro como fato técnico, não avalio:**
   a. cada recorte de tela com nome e imagem de retina vai à API do provedor do modelo (`SEGURANCA.md:195-206` já registra isso e encaminha a pergunta);
   b. `~/.laudos_oct/guardiao.log` acumula o nome do paciente em claro, um por laudo, sem prazo de expurgo e fora do alcance do `purge` (M-04);
   c. `~/Laudos_OCT` e os PDFs ficam legíveis por qualquer conta local da máquina (M-07);
   d. o rastro `acoes.jsonl` não tem política de retenção declarada;
   e. o acesso ao prontuário é feito com a conta que o operador autenticou, e nada no pacote distingue no rastro quem operou.

---

## Seção 12 — O que eu não consegui verificar

1. **Contaminação de contexto entre pacientes (A1/P1).** Exige o agente hospedeiro real processando dois pacientes em sequência. É proibido narrar geração que não houve; a rota que usei foi a estrutural (`[ausência]` de invocação por item, B-03) e a de instrução.
2. **Disparo da `description` (E2).** Não é testável sem sessão com a skill instalada, e simular a decisão é proibido. O que fiz foi lexical: `mácula`, `retina` (via "camada de fibras nervosas" e "OCT de nervo óptico"), `OCT`, `laudo`, `escavação/papila`, `CFN` e os quatro nomes de unidade aparecem literalmente na `description`; `córnea`, `glaucoma`, `campo visual`, `biometria`, `topografia` e `agendamento` não aparecem — nem como qualificador de exclusão. **Disparo real não testado — exige sessão com a skill instalada.**
3. **Se o harness ignora `permissionDecision: "escalate"` (B-02).** A documentação lista `allow`/`deny`/`ask`/`defer`; não consegui observar o comportamento do Claude Code diante do valor inválido a partir do pacote. O achado B-02 se sustenta sozinho pela abreviação `--any`, que é `[executado]`; esta parte fecha rodando o hook numa sessão real com `--anywhere` por extenso e vendo se aparece prompt.
4. **Se o clique cai no pixel certo, se a captura enxerga a janela do AnyDesk e se a consciência de DPI é aceita pelo Windows.** Exige a estação; o próprio `teste_regras.py:10-12` diz isso e está certo.
5. **`plataforma.py` no sistema real.** Rodei tudo com a plataforma falsa injetada, que é o mecanismo do próprio pacote. `osascript`, `screencapture`, `sips`, `cliclick`, `pyautogui`, `ctypes.windll` e `icacls` não foram exercitados — não há macOS nem Windows aqui.
6. **Se `_restringe` funciona no Windows.** `plataforma.py:451-463` chama `icacls` com `check=False` e engole exceção; sem Windows não sei se a ACL é aplicada, e a falha é silenciosa por construção.
7. **Se os valores clínicos dos assets são sintéticos.** Ver pergunta 8. Não uso dado real de paciente em teste e não tenho como decidir isso lendo o pacote — todas as fixtures que gerei (`FX-OBS`, `FX-LIMITROFE`, `FX-OD`, `FX-CONFLITO`, `FX-SEMOLHO`) são inventadas, com nomes que não são de ninguém.
8. **Corte de orçamento declarado (§4.5a):** `coverage run -m pytest` não rodou — o pacote não usa `pytest` e as duas suítes são scripts próprios com `sys.exit`. O eixo G ficou por `vulture` + `ruff` + leitura + mutação, que é o que 4.5 prevê.
9. **Conteúdo clínico da base científica.** Os seis arquivos de `references/base/` estão como `parcial` na tabela 0.1: li cabeçalho, carimbo e estrutura, não auditei a medicina. Não é objeto desta revisão e não seria eu a auditá-la.
