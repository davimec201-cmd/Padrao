---
description: Limpeza da skill laudos-oct — tira o bloqueio de assinatura vencido, duplicação, seção irrelevante, instrução obsoleta e código morto, com teste de aceite antes e depois
argument-hint: [caminho da skill]
---

# Limpeza da `laudos-oct`

**Alvo:** `$ARGUMENTS`. Vazio → procure nesta ordem e diga qual achou:
`~/.claude/skills/laudos-oct/`, ou a pasta `laudos-oct/` do repositório `Padrao`
(hoje na branch `claude/ophthalmology-skill-review-j6v9un`, não na `main`).

Antes de qualquer coisa, entenda o que esta skill é: ela **opera a máquina de uma
clínica pelo AnyDesk, lê exame de paciente real e produz documento que um médico
assina com o CRM dele**. Não é um gerador de texto. Aqui o custo de uma linha
errada não é token — é laudo no paciente errado, número inventado ou CRM num
documento que ninguém revisou.

Por isso a limpeza tem uma hierarquia que não se inverte:

1. **Segurança clínica primeiro.** Nenhuma trava sai. Nenhuma regra inviolável é
   reescrita "para ficar mais curta".
2. **Verdade depois.** O que está escrito tem que ser o que o código faz hoje.
3. **Economia por último.** Linha repetida é imposto em token, mas some só quando
   as duas de cima já estão satisfeitas.

## Regras do serviço

- **Evidência antes de tesoura.** Nada sai porque "parece velho": sai com o comando
  que prova, e o relatório cita `arquivo:linha`.
- **Na dúvida, não apaga: relata.** É a mesma disciplina que a skill exige do agente
  quando um número está ilegível — `[VERIFICAR]`, não chute.
- **Trava é para ficar.** Se você não consegue explicar por que uma trava existe,
  isso é motivo para ler mais, nunca para removê-la.
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

**O que é.** A clínica decidiu em **20/08/2026** (formulário, Bloco 2, Caminho A) que
**usa** assinatura digitalizada. `SEGURANCA.md` §9 registra a decisão e diz, com todas
as letras, que o texto anterior "deixou de valer naquele dia e ficou aqui por
descuido". O código acompanhou: `--assinatura` virou `--assinar`, com três portões.

Só que a **proibição antiga continua escrita em dois lugares**, e é ela que o agente
lê antes de operar:

- `SKILL.md:399-401` — "A clínica não usa assinatura digitalizada: não aplique
  nenhuma e não proponha aplicar."
- `references/templates-hospitais.md:210-212` — a mesma frase, com "nunca aplique
  nenhuma, nem sugira aplicar".

Isso é o bloqueio. Ele proíbe um fluxo que o médico autorizou, que o código
implementa e que a suíte de aceite testa. Tire as duas frases e escreva no lugar o
que vale hoje, com o mesmo peso das outras regras: sem `--assinar` sai **minuta**;
com `--assinar` sai o **documento final**, e para isso as três condições de
`SEGURANCA.md:300-307` precisam ser verdade ao mesmo tempo.

**O que sai é a frase vencida. O que fica, intacto, é o portão:**

| Fica | Onde |
|---|---|
| a imagem de assinatura vive fora do pacote e fora do git | `PENDENCIAS.md:69-72`, `.gitignore` |
| laudo com `[VERIFICAR]` ou `[RECAPTURAR]` não pode ser assinado | `SEGURANCA.md:304-305` |
| `~/.laudos_oct/PERMITIR_ASSINATURA`, criado pelo médico, apagado no uso | `SEGURANCA.md:306-308`, `laudo_pdf.py:825` |
| o guardião nega qualquer comando que toque o arquivo de autorização | `guardiao-laudos.py:217`, regra 8b em `:240` |
| o agente não roda `--assinar` por conta própria, nem em lote | regra 18, `SKILL.md:196-200` |
| carimbo "MINUTA — CONFERIR E ASSINAR" em toda minuta, não suprimível | `SKILL.md:325-327` |

Se em algum momento a limpeza parecer pedir que um desses saia, **você entendeu o
pedido errado**: o que foi pedido é derrubar a proibição vencida, não os portões que
mantêm a assinatura sendo ato do médico. Divergência aqui é para o relatório, não
para o commit.

## 2. Seção irrelevante — cortar

Teste único: **se eu apagar isto, alguma decisão do agente sai diferente?** Não → fora
do pacote da skill (e não necessariamente fora do repositório: arquivar não é apagar).

O caso grande está pronto: **`REVISAO-2026-08-20.md`, 1317 linhas — 14% do pacote —
que ninguém cita.** Nenhum arquivo da skill aponta para ele, a tabela de referências
de `SKILL.md:382-395` não o lista, e ele mesmo abre dizendo "DOCUMENTO DE ARQUIVO —
não descreve o estado atual do código". É histórico de auditoria: vale no repositório,
não dentro de uma skill que o modelo carrega para laudar paciente.

Cuidado com o oposto: **nota de procedência não é irrelevante.** "verde ou branco =
dentro, amarelo ou vermelho = fora, fechado pelo Dr. Maeta em 20/08/2026" sem a data e
o autor volta a ser discutido no mês seguinte. Procedência de decisão clínica fica.

## 3. Duplicação — uma casa por assunto

O mesmo assunto está escrito em vários lugares, e a cada cópia aumenta a chance de uma
delas envelhecer sozinha — que é exatamente o que produziu a frente 1.

| Assunto | Quantas casas |
|---|---|
| o portão `PERMITIR_ASSINATURA` (com o par `touch`/`ni` copiado) | `PENDENCIAS.md:14-25`, `SEGURANCA.md:298-322`, `INSTALACAO.md:231-236`, `preparar_assinatura.py:135` |
| o carimbo de MINUTA | `SKILL.md:197`, `SKILL.md:325-327`, `INSTALACAO.md:181`, `INSTALACAO.md:231`, `SEGURANCA.md:300-301`, `SEGURANCA.md:337` |
| signatário derivado do hospital | regra 17 (`SKILL.md:190-195`), Passo 5 (`SKILL.md:319-321`), `templates-hospitais.md` |

Regra: **uma casa canônica, as outras remetem por uma linha.** A canônica é a que o
agente lê no momento da decisão — para portão de assinatura é `SEGURANCA.md` §9; para
regra de operação é o `SKILL.md`. Comando de terminal copiado em dois arquivos é o pior
caso: some de um, fica no outro.

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
1-6 e salta para 16, 17, 18; "Operacionais" vai 7-15 com um `8b` no meio — e o
guardião tem uma regra 8b **diferente**, sobre assinatura. Duas coisas com o mesmo
nome numa skill que manda "quebrar qualquer uma destas invalida o laudo" é convite a
citar a regra errada. Renumere em sequência, preservando o texto de cada uma palavra
por palavra, e conserte as referências cruzadas.

E os números soltos: a docstring de `teste_aceite.py:3` promete "os 17 critérios de
aceite" e o arquivo roda 76 asserções.

## 5. Contradição entre o texto e o código

O agente lê o texto e obedece. Contradição não é imprecisão, é bug.

```bash
grep -rniE 'nunca|sempre|não usa|obrigatóri|recusa|não existe|jamais' *.md references/*.md
```

Para cada afirmação forte, ache o que a sustenta no código ou no teste. Exemplo já
levantado: `SKILL.md:325` diz "O PDF sai **sempre** carimbado MINUTA", e
`teste_aceite.py:290` afirma o contrário para o documento assinado — "o carimbo de
MINUTA some do documento assinado". O "sempre" vale para a minuta, não para o final.

Onde texto e código discordarem, **o código ganha o relato e o dono ganha a decisão**:
proponha a correção nos dois sentidos possíveis e diga qual você recomenda. Nunca
deixe os dois discordando em silêncio.

## 6. Código morto e lint

```bash
ruff check --select F,ARG,B,E7 --no-cache scripts/ hardening/     # hoje: 62 achados
grep -rn "TODO\|FIXME\|XXX" scripts/ hardening/
```

Trate por classe, e só o que é seguro: `E702` (dois comandos numa linha por
ponto-e-vírgula), `E741` (variável chamada `l`), `B904` (`raise ... from`) e `F401`
(import sem uso) são cosméticos e passam pelos testes. `ARG002` — argumento recebido e
ignorado, como em `teste_regras.py:45-51` — **não é cosmético**: ou o parâmetro existe
para uma verificação que ninguém faz, ou a assinatura está mentindo. Investigue antes
de tocar, e se for verificação faltando, relate em vez de apagar o parâmetro.

Guarda que nunca dispara é o pior achado possível nesta skill: ela documenta uma
proteção que o programa não tem. Se aparecer, é relatório de cima da pilha.

## 7. Higiene básica

- **Front matter**: `name`, `description` e o `disallowed-tools` com o comentário que
  explica por que não é `allowed-tools`. A `description` é o gatilho — se mexer, mostre
  antes e depois; ela cita os hospitais de propósito.
- **Tamanho**: `SKILL.md` tem 405 linhas. Acima de ~500 é sinal de que algo devia
  descer para `references/`.
- **Caminho absoluto** em todo comando de exemplo (`python3 ~/.claude/skills/laudos-oct/scripts/...`):
  é o que casa com as regras de permissão do `settings.json`. Forma relativa que
  escapou é erro, não estilo.
- **`requirements.txt` e `requirements-windows.txt`** coerentes entre si e com os
  imports.
- **Nada de dado de paciente, nome próprio de paciente, print de tela ou imagem de
  assinatura** entrando no pacote ou no repositório. Confira o `.gitignore` antes de
  qualquer `git add`, e nunca use `git add -A` nesta pasta.

## Verificação — antes de dizer que acabou

```bash
python3 scripts/teste_regras.py; echo "regras: $?"     # 140 passaram, 0 falharam
python3 scripts/teste_aceite.py; echo "aceite: $?"     #  76 passaram, 0 falharam

mkdir -p /tmp/depois
for e in assets/exemplo_*.json; do
  HOME=/tmp/depois python3 scripts/laudo_pdf.py --json "$e" --sobrescrever >/dev/null
done
python3 /tmp/extrai.py /tmp/depois > /tmp/depois.txt
diff /tmp/antes.txt /tmp/depois.txt && echo "os quatro laudos saíram iguais"
```

Diferença no `diff` não é necessariamente regressão — pode ser exatamente a mudança que
você quis. O que não vale é diferença que você não sabe explicar.

Checklist, tudo com resposta escrita:

- [ ] as duas suítes com a mesma contagem de antes, código de saída 0;
- [ ] texto dos quatro laudos de exemplo idêntico, ou a diferença explicada;
- [ ] nenhum portão da tabela da frente 1 tocado — diga isso explicitamente;
- [ ] nenhum `SUMIU` sobrando sem decisão registrada;
- [ ] `grep` por cada trecho removido não acha referência órfã;
- [ ] `git status` sem nenhum arquivo de imagem, print ou dado de paciente;
- [ ] linhas antes → depois, arquivo por arquivo.

## Relatório — é entregável, não bônus

Uma tabela, uma linha por mudança:

| Frente | Arquivo:linha | O que era | O que fiz | Prova |
|---|---|---|---|---|

Depois, quatro listas curtas:

1. **Removido** — com a instrução exata que saiu, citada, para o dono reconhecer.
2. **Juntado** — o que virou remissão e para onde.
3. **Arquivado** — o que saiu do pacote da skill e continua no repositório, e onde.
4. **Não toquei** — cada caso que precisa de decisão do médico ou do dono, com a
   pergunta já formulada e a recomendação. Item aqui não é fracasso; item omitido é.

Feche com os números: linhas antes/depois, as duas contagens de teste, o resultado da
comparação dos PDFs. **Silêncio não é sucesso** — frente que não rendeu nada, diga que
não rendeu.

## Nunca

- afrouxar, condicionar ou apagar qualquer trava: `PERMITIR_ASSINATURA`,
  `PERMITIR_ANYWHERE`, freio de mão `STOP`, guarda de foco, guarda de retângulo, lista
  negra de teclas, teto de taxa, detector de loop, recusa por `[VERIFICAR]`, cópia
  para `_PENDENTES/`, carimbo de MINUTA;
- reescrever, resumir ou reordenar as regras invioláveis clínicas 1-6 — renumerar
  mantendo o texto é permitido, editar o texto não;
- regravar o hash de `references/base/REVISAO.json`, ou editar `references/base/*.md`
  sem revisão médica: o hash é o que faz o `laudo_pdf.py` recusar sozinho;
- fazer o agente capaz de criar autorização, assinar em lote ou rodar `--assinar` por
  conta própria;
- trocar `disallowed-tools` por `allowed-tools`, ou tirar `WebFetch`/`WebSearch` da
  lista;
- amaciar a regra de somente-leitura no sistema do hospital, ou qualquer item da
  lista negra de teclas;
- inventar frase de laudo, mexer na biblioteca de frases, ou promover `[proposta]`
  a `[modelo]`;
- commitar imagem de assinatura, print de tela, nome de paciente ou `~/.laudos_oct/`;
- entregar sem rodar as duas suítes;
- aproveitar a viagem para refatorar o que ninguém pediu.

## Apêndice — pistas desta rodada

Levantadas em 22/08/2026 no pacote da branch `claude/ophthalmology-skill-review-j6v9un`,
todas conferidas no código. **Confirme cada uma antes de agir** e **apague este
apêndice** quando a rodada fechar.

| Frente | Onde | O que tem lá |
|---|---|---|
| 1 | `SKILL.md:399-401` | "A clínica não usa assinatura digitalizada: não aplique nenhuma e não proponha aplicar" — vencida em 20/08/2026 |
| 1 | `templates-hospitais.md:210-212` | a mesma proibição, outra redação |
| 1 | `SEGURANCA.md:291-296` | a própria skill diz que o texto antigo "ficou aqui por descuido" — e ainda está nos outros dois arquivos |
| 1 | `SKILL.md:196-200` vs `SKILL.md:399-401` | a regra 18 descreve o fluxo assinado como existente e deliberado; a §7 proíbe o fluxo inteiro. Mesmo arquivo |
| 2 | `REVISAO-2026-08-20.md` | 1317 linhas, 14% do pacote, **zero arquivos citam** e não está na tabela de referências de `SKILL.md:382-395`; ele mesmo se declara documento de arquivo |
| 2 | `REVISAO-2026-08-20.md:530-561` | o achado A-03 manda "remover `--assinatura`" — decisão superada: o parâmetro foi renomeado e ganhou portão |
| 2 | `PENDENCIAS.md:113-118` | "Entregável combinado" — combinação de projeto, não instrução de operação |
| 3 | `PENDENCIAS.md:14-25`, `SEGURANCA.md:298-322`, `INSTALACAO.md:231-236`, `preparar_assinatura.py:135` | o portão de assinatura explicado quatro vezes, com o par `touch`/`ni` copiado duas |
| 3 | `SKILL.md:197`, `:325-327`, `INSTALACAO.md:181`, `:231`, `SEGURANCA.md:300-301`, `:337` | o carimbo de MINUTA, seis vezes |
| 4 | `SKILL.md:157-201` | regras clínicas numeradas 1-6 e depois 16, 17, 18 |
| 4 | `SKILL.md:202-241` vs `guardiao-laudos.py:240` | dois "8b" diferentes: espera de tela na skill, assinatura no guardião |
| 4 | `teste_aceite.py:3` | docstring promete "os 17 critérios de aceite"; rodam 76 asserções |
| 4 | `REVISAO-2026-08-20.md:38,514,717` | cita `hardening/settings.json`, que hoje é `settings-macos.json` + `settings-windows.json` |
| 5 | `SKILL.md:325` vs `teste_aceite.py:290` | "sai **sempre** carimbado MINUTA" contra o teste que exige o carimbo ausente no documento assinado |
| 6 | `ruff check --select F,ARG,B,E7 scripts/ hardening/` | 62 achados; `E702`/`E741`/`B904` cosméticos, `ARG002` em `teste_regras.py:45-51` é para investigar |
| 7 | `PENDENCIAS.md:74-78` | `svglib` não está em nenhum dos dois `requirements` — o texto está certo, e a emissão do final recusa se só houver `.svg`. Confirme antes de "consertar" |
