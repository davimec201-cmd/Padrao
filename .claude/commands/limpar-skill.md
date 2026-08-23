---
description: Limpeza da skill laudos-oct — libera a assinatura no fluxo normal, mantém só a recusa por assinatura errada com correção automática, e limpa duplicação, seção irrelevante, instrução obsoleta e código morto
argument-hint: [caminho da skill]
---

# Limpeza da `laudos-oct`

**Alvo:** `$ARGUMENTS`. Vazio → procure nesta ordem e diga qual achou:
`~/.claude/skills/laudos-oct/`, ou a pasta `laudos-oct/` do repositório `Padrao`
(hoje na branch `claude/ophthalmology-skill-review-j6v9un`, não na `main`).

Antes de qualquer coisa, entenda o que esta skill é: ela **opera a máquina de uma
clínica pelo AnyDesk, lê exame de paciente real e produz o laudo que sai com o nome e
o CRM de um médico**. Não é um gerador de texto. Aqui o custo de uma linha errada não
é token — é laudo no paciente errado, número inventado, ou **o CRM do médico errado
num documento assinado**.

A ordem de prioridade da limpeza:

1. **Assinar tem que funcionar.** O fluxo normal produz o laudo assinado. Tudo o que
   impede isso sai.
2. **Assinar errado tem que falhar.** A única recusa que fica é a de assinatura
   errada — e ela não termina em "avise o humano": termina em **corrigir e refazer**.
3. **Verdade.** O que está escrito tem que ser o que o código faz hoje.
4. **Economia.** Linha repetida é imposto em token, e some depois das três de cima.

## Regras do serviço

- **Evidência antes de tesoura.** Nada sai porque "parece velho": sai com o comando
  que prova, e o relatório cita `arquivo:linha`.
- **Na dúvida, não apaga: relata.** É a mesma disciplina que a skill exige do agente
  quando um número está ilegível — `[VERIFICAR]`, não chute.
- **Trava de conteúdo não se mexe.** Este pedido é sobre o portão da assinatura. As
  regras clínicas, o freio de mão, a guarda de foco, a lista negra de teclas e a trava
  da base científica não estão em jogo.
- **Escopo é o que está escrito aqui.** Não renomeie script, não troque biblioteca,
  não reformate arquivo que você não tocou, não refatore de passagem.
- **Um commit por frente**, com o nome da frente na mensagem.

## 0. Fotografe antes de mexer

Esta skill tem duas suítes offline. Elas são o baseline, e rodam em qualquer máquina
— sem tela, sem AnyDesk, sem clínica.

```bash
SKILL=/caminho/da/skill        # o que você resolveu no cabeçalho
cd "$SKILL"
wc -l SKILL.md *.md references/*.md references/base/*.md scripts/*.py hardening/hooks/*.py

pip install reportlab                       # única dependência dos testes offline
python3 scripts/teste_regras.py; echo "regras: $?"     # espere 140 passaram, 0 falharam
python3 scripts/teste_aceite.py; echo "aceite: $?"     # espere  76 passaram, 0 falharam
```

Guarde os dois números e os dois códigos de saída. **Se algum já falhar antes de você
mexer, pare e relate** — limpeza em cima de teste vermelho não tem como ser provada.

O `140` não muda nesta limpeza. O `76` **vai mudar**, porque duas asserções da suíte de
aceite existem só para provar o portão que está sendo removido (§1d). Registre o número
novo e justifique cada asserção que trocou de nome ou de sentido.

Guarde também o laudo dos quatro exemplos — é o que prova que o documento não mudou.
`laudo_pdf.py` **não tem flag de saída**: o caminho é derivado do laudo, então o `HOME`
redirecionado é o que mantém os exemplos longe do `~/Laudos_OCT` de verdade. É como a
própria suíte de aceite faz.

```bash
mkdir -p /tmp/antes
for e in assets/exemplo_*.json; do
  HOME=/tmp/antes python3 scripts/laudo_pdf.py --json "$e" --sobrescrever >/dev/null
done
```

O PDF carrega data de geração, então **hash não serve** — dois PDFs iguais em conteúdo
dão hashes diferentes. O que é estável é o texto extraído, e o extrator já existe
dentro da suíte:

```bash
cat > /tmp/extrai.py <<'FIM'
# Texto legível dos PDFs de uma pasta, para diff. Uso: extrai.py <pasta>
import importlib.util, re, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("ta", "scripts/teste_aceite.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for pdf in sorted(Path(sys.argv[1]).rglob("*.pdf")):
    print("=====", pdf.name)
    for linha in re.sub(r"[^\x20-\x7eÀ-ſ]+", "\n", m.texto_do_pdf(pdf)).splitlines():
        if len(linha.strip()) >= 4:
            print(linha.strip()[:300])
FIM
python3 /tmp/extrai.py /tmp/antes > /tmp/antes.txt; wc -l /tmp/antes.txt
```

São ~800 linhas de texto por rodada, estáveis entre execuções — foi conferido.

## 1. Bloqueio de assinatura — tirar

**Decisão do dono:** a skill passa a **assinar no fluxo normal**. Sai tudo o que impede
a assinatura de ser aplicada. Fica só o que impede a assinatura **errada** — e, quando
ela estiver errada, o agente **corrige e refaz**, em vez de parar.

Contexto que você vai encontrar no caminho: em 20/08/2026 a clínica decidiu usar
assinatura digitalizada (formulário, Bloco 2, Caminho A). O `SEGURANCA.md:291-296`
registra a decisão e diz que o texto anterior "ficou aqui por descuido". A proibição
antiga, porém, continua escrita — e o portão de uso único foi acrescentado depois.
Os dois saem agora.

### 1a. O que sai

| Onde | O que é |
|---|---|
| `SKILL.md:399-401` | "A clínica não usa assinatura digitalizada: não aplique nenhuma e não proponha aplicar" |
| `references/templates-hospitais.md:210-212` | a mesma proibição, outra redação |
| `SKILL.md:196-200` — regra 18 | "Você não roda `--assinar` por conta própria, nem em lote, nem 'para adiantar'" — a proibição no nível da instrução |
| `scripts/laudo_pdf.py:825` e `:828-854` | a constante `PERMISSAO_ASSINATURA` e `consome_permissao_assinatura()` — o portão de uso único |
| `scripts/laudo_pdf.py:1227` | a chamada do portão (a linha **1226**, `exige_assinatura()`, é a que fica) |
| `hardening/hooks/guardiao-laudos.py:215-217` | o ramo `PERMITIR_ASSINATURA` de `ALVO_PROTEGIDO` — **só esse ramo**: `PERMITIR_ANYWHERE`, `STOP`, settings, hooks, arquivos da skill e `config.json` continuam protegidos |
| `hardening/hooks/guardiao-laudos.py:240-245` | a regra 8b, que escala `--assinar` para confirmação humana |
| `SEGURANCA.md:298-322` | o item 3 dos três portões e o bloco `touch`/`ni` |
| `PENDENCIAS.md:9-25` e `:31-34` | a tabela das "duas autorizações" (a linha do `PERMITIR_ANYWHERE` fica) e a frase que trata o assinado como exceção |
| `INSTALACAO.md:231-236` | a mesma explicação do portão |
| `scripts/preparar_assinatura.py:135` | a linha que manda criar a autorização |

Feito isso, `--assinar` deixa de ser exceção: o Passo 5 do `SKILL.md` passa a emitir o
documento assinado como caminho normal, e a minuta passa a ser o que sai quando **não
dá** para assinar. Se você achar melhor inverter a flag (assinar por padrão, `--minuta`
para o rascunho), **proponha no relatório e não faça sozinho** — trocar o padrão da CLI
muda todo comando escrito nos docs, nos testes e nas regras de permissão do
`settings.json`.

Escreva no `SEGURANCA.md`, no lugar do item removido, o que passou a sustentar a
declaração de revisão: o relatório de fila (`--fila relatorio`), o `extracao.json` e o
`~/.laudos_oct/acoes.jsonl`. O médico precisa saber que o fluxo mudou — isso vai no
relatório final, em uma linha, com essas palavras.

### 1b. O que fica — a única recusa que sobra

| Onde | Recusa quando |
|---|---|
| `SKILL.md:190-195` — regra 17 | o signatário não é o do hospital: Farroupilha assina **Dr. Cassiano Ricardo Goulart**, Nova Prata assina **Dr Vinícius L Maeta**; contradição no laudo é recusada |
| `scripts/laudo_pdf.py:56,62` + `:766-775` (`caminho_assinatura`) | o mapa hospital → signatário → arquivo de imagem (`assinatura_cassiano`, `assinatura_maeta`). É o que impede assinar com a imagem do outro |
| `scripts/laudo_pdf.py:857-873` (`exige_assinatura`) | falta a imagem daquele signatário, ou só existe `.svg` (que ainda não renderiza, falta `svglib`) |

Essas três não são portão de assinatura: são a garantia de que a assinatura aplicada é
**a certa**. Elas ficam, e ficam mais fortes — a mensagem de recusa tem que dizer qual
dos três casos ocorreu, porque é o que o laço da §1c lê para decidir o que corrigir.

Também ficam, e **não** são portão de assinatura — não confunda, não toque:

- regra 1 e `[VERIFICAR]` / `[RECAPTURAR]` → `_PENDENTES/`: é a trava de **conteúdo**.
  Tirar isso não libera assinatura, põe CRM em laudo com buraco;
- regra 4, conferência de identidade (nome, data, olho) antes de salvar;
- regra 16, o hash de `references/base/REVISAO.json`;
- o carimbo "MINUTA — CONFERIR E ASSINAR" no PDF **não** assinado: é rótulo, não
  portão, e é o que impede confundir minuta com laudo pronto dentro da pasta;
- o freio de mão `STOP`, o `PERMITIR_ANYWHERE`, a guarda de foco e de retângulo, a
  lista negra de teclas, o teto de taxa e o detector de loop.

### 1c. Refazer certo — o laço que substitui o portão

Quando a emissão for recusada por assinatura, o agente **não para**: diagnostica,
corrige e refaz. Escreva isto no `SKILL.md`, no Passo 5, com esta estrutura:

1. **Leia a mensagem de recusa** — ela nomeia o caso. Três casos, três correções:
   - *signatário contradiz o hospital* → o signatário se deriva do campo `hospital`,
     nunca do laudo anterior nem do que estava no JSON. Corrija o laudo e refaça.
   - *falta a imagem daquele signatário* → procure o digitalizado na máquina e rode
     `preparar_assinatura.py <chave> <arquivo>` com a chave certa (`cassiano` ou
     `maeta`) — nome de arquivo errado faz o gerador não achar a imagem.
   - *só existe `.svg`* → produza o `.png` ao lado com o mesmo script, ou instale
     `svglib`. Não converta à mão.
2. **Refaça** com `--assinar --sobrescrever`.
3. **Confira o que saiu**, e não o que você esperava que saísse: `documento` igual a
   `final assinado`, o nome **e** o CRM do signatário daquele hospital presentes no
   texto do PDF, nenhum "MINUTA" no texto, e nome do paciente, data e olho iguais aos
   da tela.
4. **Duas tentativas, no máximo.** Na terceira, pare e relate o que falta, com o
   caminho exato do arquivo esperado.

Três coisas que o laço nunca faz, e que precisam estar escritas com essa força:

- **nunca assina com a imagem do outro signatário** para "passar" — é exatamente o erro
  que a regra 17 existe para impedir, e o custo é CRM errado num documento assinado;
- **nunca entrega a minuta calada** como se fosse o laudo pronto. Se terminou em
  minuta, o relatório diz isso, com o motivo;
- **nunca reaproveita** o PDF de um paciente para outro, nem refaz sem `--sobrescrever`
  achando que sobrescreveu.

### 1d. Os testes que codificavam o portão

Duas asserções da suíte de aceite existem só para provar o portão removido:

- `scripts/teste_aceite.py:268-275` — *"48b. NEGATIVO: `--assinar` sem a autorização do
  médico é RECUSADO"*, com o `bilhete.unlink()` que a prepara;
- `scripts/teste_aceite.py:294` — *"53. E a autorização foi CONSUMIDA"*, mais o
  `bilhete.write_text(...)` da linha 278 que alimenta o laço.

**Reescreva, nunca apague.** Teste que sai sem substituto é cobertura perdida sem
ninguém notar. No lugar delas, quatro asserções que provam o comportamento novo:

1. `--assinar` com a imagem presente **emite, sem arquivo de autorização nenhum**;
2. NEGATIVO: signatário que contradiz o hospital é **recusado**, e a mensagem nomeia o
   hospital e o signatário esperado;
3. NEGATIVO: imagem ausente daquele signatário é **recusada**, e a mensagem nomeia o
   caminho esperado;
4. depois de corrigir a causa e refazer, sai `final assinado`, com o nome e o CRM certos
   e sem carimbo de MINUTA.

Os testes 49 a 52 continuam valendo como estão — o que muda neles é só o preparo, que
não cria mais o bilhete.

## 2. Seção irrelevante — cortar

Teste único: **se eu apagar isto, alguma decisão do agente sai diferente?** Não → fora
do pacote da skill (e não necessariamente fora do repositório: arquivar não é apagar).

O caso grande está pronto: **`REVISAO-2026-08-20.md`, 1317 linhas — 14% do pacote —
que ninguém cita.** Nenhum arquivo da skill aponta para ele, a tabela de referências
de `SKILL.md:382-395` não o lista, e ele mesmo abre dizendo "DOCUMENTO DE ARQUIVO —
não descreve o estado atual do código". É histórico de auditoria: vale no repositório,
não dentro de uma skill que o modelo carrega para laudar paciente. O achado A-03 dele,
que manda remover `--assinatura`, é a decisão contrária à desta rodada — mais uma razão
para ele não morar aqui.

Cuidado com o oposto: **nota de procedência não é irrelevante.** "verde ou branco =
dentro, amarelo ou vermelho = fora, fechado pelo Dr. Maeta em 20/08/2026" sem a data e
o autor volta a ser discutido no mês seguinte. Procedência de decisão clínica fica.

## 3. Duplicação — uma casa por assunto

O mesmo assunto escrito em vários lugares, e a cada cópia aumenta a chance de uma delas
envelhecer sozinha — foi exatamente isso que deixou uma proibição vencida de pé por
dois dias em dois arquivos.

| Assunto | Quantas casas |
|---|---|
| o carimbo de MINUTA | `SKILL.md:197`, `SKILL.md:325-327`, `INSTALACAO.md:181`, `INSTALACAO.md:231`, `SEGURANCA.md:300-301`, `SEGURANCA.md:337` |
| signatário derivado do hospital | regra 17 (`SKILL.md:190-195`), Passo 5 (`SKILL.md:319-321`), `templates-hospitais.md` |
| onde a imagem de assinatura mora e por quê | `PENDENCIAS.md:69-72`, `.gitignore`, `SEGURANCA.md` §9 |

A quarta duplicação — o portão `PERMITIR_ASSINATURA` explicado em quatro arquivos — a
frente 1 resolve apagando, não juntando. Confira no fim que não sobrou menção órfã.

Regra: **uma casa canônica, as outras remetem por uma linha.** A canônica é a que o
agente lê no momento da decisão: regra de operação no `SKILL.md`, política no
`SEGURANCA.md`, formato do documento em `templates-hospitais.md`. Comando de terminal
copiado em dois arquivos é o pior caso: some de um, fica no outro.

## 4. Instrução obsoleta

Caminho, arquivo, comando e **número** que não correspondem mais:

```bash
grep -rnoE '`[a-zA-Z0-9_./-]+\.(md|py|json|txt|ps1|sh)`' *.md references/*.md \
  | tr -d '`' | while IFS=: read -r origem linha alvo; do
      find . -name "${alvo##*/}" -print -quit | grep -q . || echo "SUMIU  $origem:$linha  ->  $alvo"
    done
```

Cada `SUMIU` é uma decisão, nunca um `rm` automático — pode ser link a corrigir,
arquivo que só existe na máquina da clínica (`~/.laudos_oct/...`, e aí a frase tem que
dizer isso), ou citação de arquivo que a auditoria viu e que hoje tem outro nome
(`hardening/settings.json` virou `settings-macos.json` + `settings-windows.json`).
O grep não entra em bloco de código: os comandos dentro das cercas você confere à mão.

Confira também a **numeração das regras invioláveis**: em `SKILL.md`, "Clínicas" vai
1-6 e salta para 16, 17, 18; "Operacionais" vai 7-15 com um `8b` no meio — e o guardião
tem uma regra 8b **diferente**, sobre assinatura (que a frente 1 remove, o que já
desfaz metade da confusão). Renumere em sequência, preservando o texto de cada regra
palavra por palavra, e conserte as referências cruzadas. A regra 18 sai nesta rodada:
renumere depois de removê-la, não antes.

E os números soltos: a docstring de `teste_aceite.py:3` promete "os 17 critérios de
aceite" e o arquivo roda 76 asserções.

## 5. Contradição entre o texto e o código

O agente lê o texto e obedece. Contradição não é imprecisão, é bug.

```bash
grep -rniE 'nunca|sempre|não usa|obrigatóri|recusa|não existe|jamais' *.md references/*.md
```

Para cada afirmação forte, ache o que a sustenta no código ou no teste. Exemplo já
levantado: `SKILL.md:325` diz "O PDF sai **sempre** carimbado MINUTA", e
`teste_aceite.py:290` afirma o contrário para o documento assinado. Depois da frente 1
esse "sempre" fica ainda mais errado, porque o assinado passa a ser o caminho normal —
conserte a frase, não o teste.

Onde texto e código discordarem, **o código ganha o relato e o dono ganha a decisão**:
proponha a correção nos dois sentidos possíveis e diga qual você recomenda. Nunca deixe
os dois discordando em silêncio.

## 6. Código morto e lint

```bash
ruff check --select F,ARG,B,E7 --no-cache scripts/ hardening/     # hoje: 62 achados
grep -rn "TODO\|FIXME\|XXX" scripts/ hardening/
```

Trate por classe, e só o que é seguro: `E702` (dois comandos numa linha por
ponto-e-vírgula), `E741` (variável chamada `l`), `B904` (`raise ... from`) e `F401`
(import sem uso) são cosméticos e passam pelos testes. `ARG002` — argumento recebido e
ignorado, como em `teste_regras.py:45-51` — **não é cosmético**: ou o parâmetro existe
para uma verificação que ninguém faz, ou a assinatura da função está mentindo.
Investigue antes de tocar, e se for verificação faltando, relate em vez de apagar o
parâmetro.

Depois da frente 1, passe o lint de novo: remoção deixa import órfão e parâmetro sem
uso. `exige_assinatura(assinante, hospital)` continua recebendo `hospital` — confira se
ainda usa, agora que a função vizinha saiu.

## 7. Higiene básica

- **Front matter**: `name`, `description` e o `disallowed-tools` com o comentário que
  explica por que não é `allowed-tools`. A `description` é o gatilho — se mexer, mostre
  antes e depois; ela cita os hospitais de propósito.
- **Tamanho**: `SKILL.md` tem 405 linhas. Acima de ~500 é sinal de que algo devia
  descer para `references/`.
- **Caminho absoluto** em todo comando de exemplo
  (`python3 ~/.claude/skills/laudos-oct/scripts/...`): é o que casa com as regras de
  permissão do `settings.json`. Forma relativa que escapou é erro, não estilo.
- **`requirements.txt` e `requirements-windows.txt`** coerentes entre si e com os
  imports. Se a frente 1 tornar `svglib` caminho normal, ela entra aqui com teto de
  versão, como as outras.
- **Nada de dado de paciente, nome próprio de paciente, print de tela ou imagem de
  assinatura** entrando no pacote ou no repositório. Confira o `.gitignore` antes de
  qualquer `git add`, e nunca use `git add -A` nesta pasta.

## Verificação — antes de dizer que acabou

```bash
python3 scripts/teste_regras.py; echo "regras: $?"     # 140 passaram, 0 falharam
python3 scripts/teste_aceite.py; echo "aceite: $?"     # o número novo, 0 falharam

mkdir -p /tmp/depois
for e in assets/exemplo_*.json; do
  HOME=/tmp/depois python3 scripts/laudo_pdf.py --json "$e" --sobrescrever >/dev/null
done
python3 /tmp/extrai.py /tmp/depois > /tmp/depois.txt
diff /tmp/antes.txt /tmp/depois.txt && echo "os quatro laudos saíram iguais"
```

Os exemplos rodam **sem** `--assinar`, então o texto deles tem que sair idêntico: a
frente 1 não muda a minuta. Se mudou, você mexeu em mais do que devia.

Prove também o caminho novo, à mão, com a imagem sintética que a suíte de aceite já
sabe criar (`teste_aceite.py:259-266` — um PNG branco, não é assinatura de ninguém):

- `--assinar` emite sem nenhum arquivo de autorização;
- signatário trocado é recusado com mensagem que nomeia o esperado;
- imagem ausente é recusada com o caminho no texto;
- depois de corrigir, sai `final assinado`, com nome e CRM certos e sem MINUTA.

Checklist, tudo com resposta escrita:

- [ ] `teste_regras.py` com 140, código de saída 0;
- [ ] `teste_aceite.py` com o número novo declarado e justificado, código de saída 0;
- [ ] texto dos quatro laudos de exemplo idêntico, ou a diferença explicada;
- [ ] os quatro cenários de assinatura acima, cada um com a saída real colada;
- [ ] nenhuma trava da lista da §1b tocada — diga isso explicitamente, item por item;
- [ ] nenhuma menção órfã a `PERMITIR_ASSINATURA` em md, py, json ou ps1;
- [ ] nenhum `SUMIU` sobrando sem decisão registrada;
- [ ] `git status` sem nenhum arquivo de imagem, print ou dado de paciente;
- [ ] linhas antes → depois, arquivo por arquivo.

## Relatório — é entregável, não bônus

Uma tabela, uma linha por mudança:

| Frente | Arquivo:linha | O que era | O que fiz | Prova |
|---|---|---|---|---|

Depois, cinco listas curtas:

1. **Removido** — com a instrução exata que saiu, citada, para o dono reconhecer.
2. **Reescrito** — cada teste e cada regra que trocou de sentido, com o antes e o
   depois lado a lado.
3. **Juntado / arquivado** — o que virou remissão, e o que saiu do pacote e continua no
   repositório, com o caminho.
4. **O que mudou para o médico** — em uma linha, sem rodeio: o laudo passa a sair
   assinado no fluxo normal, sem autorização por documento, e o que sustenta a
   declaração de revisão agora é o relatório de fila mais o rastro de auditoria.
5. **Não toquei** — cada caso que precisa de decisão do médico ou do dono, com a
   pergunta já formulada e a recomendação. Item aqui não é fracasso; item omitido é.

Feche com os números: linhas antes/depois, as duas contagens de teste, o resultado da
comparação dos laudos. **Silêncio não é sucesso** — frente que não rendeu nada, diga
que não rendeu.

## Nunca

- assinar com a imagem de um signatário que não é o do hospital do laudo, por nenhum
  motivo, nem "para testar";
- apagar teste: o que codificava o portão é **reescrito** para o comportamento novo;
- afrouxar o que não é portão de assinatura — `[VERIFICAR]` → `_PENDENTES/`, freio de
  mão `STOP`, `PERMITIR_ANYWHERE`, guarda de foco, guarda de retângulo, lista negra de
  teclas, teto de taxa, detector de loop, carimbo de MINUTA na minuta;
- reescrever, resumir ou reordenar as regras invioláveis clínicas 1-6 — renumerar
  mantendo o texto é permitido, editar o texto não;
- regravar o hash de `references/base/REVISAO.json`, ou editar `references/base/*.md`
  sem revisão médica: o hash é o que faz o `laudo_pdf.py` recusar sozinho;
- tirar do `ALVO_PROTEGIDO` do guardião qualquer coisa além do ramo
  `PERMITIR_ASSINATURA` — settings, hooks, shell rc, arquivos da skill, `config.json`,
  `PERMITIR_ANYWHERE` e `STOP` ficam;
- trocar `disallowed-tools` por `allowed-tools`, ou tirar `WebFetch`/`WebSearch` da
  lista;
- amaciar a regra de somente-leitura no sistema do hospital;
- inventar frase de laudo, mexer na biblioteca de frases, ou promover `[proposta]` a
  `[modelo]`;
- commitar imagem de assinatura, print de tela, nome de paciente ou `~/.laudos_oct/`;
- entregar sem rodar as duas suítes e os quatro cenários de assinatura;
- aproveitar a viagem para refatorar o que ninguém pediu.

## Apêndice — pistas desta rodada

Conferidas no pacote da branch `claude/ophthalmology-skill-review-j6v9un`. **Confirme
cada uma antes de agir** e **apague este apêndice** quando a rodada fechar.

| Frente | Onde | O que tem lá |
|---|---|---|
| 1a | `SKILL.md:399-401` | "A clínica não usa assinatura digitalizada: não aplique nenhuma e não proponha aplicar" — vencida em 20/08/2026 |
| 1a | `templates-hospitais.md:210-212` | a mesma proibição, outra redação |
| 1a | `SKILL.md:196-200` | regra 18: o agente não roda `--assinar` por conta própria |
| 1a | `laudo_pdf.py:825`, `:828-854`, `:1227` | o portão de uso único: constante, função e chamada |
| 1a | `guardiao-laudos.py:215-217` e `:240-245` | o ramo protegido do arquivo de autorização e a regra 8b, que escala `--assinar` |
| 1a | `SEGURANCA.md:298-322`, `PENDENCIAS.md:9-25`, `INSTALACAO.md:231-236`, `preparar_assinatura.py:135` | o portão documentado quatro vezes |
| 1b | `laudo_pdf.py:1226` (`exige_assinatura`) e `:857-873` | a recusa por imagem ausente ou `.svg` — **fica**, é o gatilho do laço de correção |
| 1b | `laudo_pdf.py:56,62` e `:766-775` | `arquivo_assinatura` por signatário e `caminho_assinatura()` — o mapa que impede assinar com a imagem do outro |
| 1d | `teste_aceite.py:268-275` e `:294` | as asserções 48b e 53, que provam o portão; `:259-266` cria o PNG sintético que serve aos testes novos |
| 2 | `REVISAO-2026-08-20.md` | 1317 linhas, 14% do pacote, **zero arquivos citam**, e ele mesmo se declara documento de arquivo |
| 2 | `REVISAO-2026-08-20.md:530-561` | o achado A-03 manda remover `--assinatura` — decisão contrária à desta rodada |
| 2 | `PENDENCIAS.md:113-118` | "Entregável combinado" — combinação de projeto, não instrução de operação |
| 3 | `SKILL.md:197`, `:325-327`, `INSTALACAO.md:181`, `:231`, `SEGURANCA.md:300-301`, `:337` | o carimbo de MINUTA, seis vezes |
| 4 | `SKILL.md:157-201` | regras clínicas numeradas 1-6 e depois 16, 17, 18 |
| 4 | `SKILL.md:202-241` | um `8b` no meio das operacionais, homônimo do 8b do guardião |
| 4 | `teste_aceite.py:3` | docstring promete "os 17 critérios de aceite"; rodam 76 asserções |
| 4 | `REVISAO-2026-08-20.md:38,514,717` | cita `hardening/settings.json`, hoje `settings-macos.json` + `settings-windows.json` |
| 5 | `SKILL.md:325` vs `teste_aceite.py:290` | "sai **sempre** carimbado MINUTA" contra o teste que exige o carimbo ausente no assinado |
| 6 | `ruff check --select F,ARG,B,E7 scripts/ hardening/` | 62 achados; `E702`/`E741`/`B904` cosméticos, `ARG002` em `teste_regras.py:45-51` é para investigar |
| 7 | `PENDENCIAS.md:74-78` | `svglib` não está em nenhum dos dois `requirements` — por isso a recusa quando só existe `.svg` |
