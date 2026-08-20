# Pendências — o que espera o formulário do médico

A revisão de código de 20/08/2026 fechou 27 achados. **Quatro ficaram em haver**,
porque a resposta não é minha nem do código: está no formulário
`Maeta_decisoes_e_equipamentos.docx`, que o Dr. Vinícius L. Maeta vai preencher.

Este arquivo existe para que ninguém confunda "não corrigido" com "esquecido".

---

## 1. Convenção de cor por aparelho — **trava o laudo hoje**

**Onde:** `references/base/05-aparelhos.md` §"Campos a preencher", tabela com
`[PREENCHER]` para Zeiss, Heidelberg, Topcon e Nidek.
**Formulário:** Bloco 3.4 (e 3.1, que diz qual aparelho cada hospital usa).

O que **já foi corrigido**: `SKILL.md` afirmava, na regra inviolável 3, que
"branco/verde = dentro, amarelo = limítrofe, vermelho = fora". Essa frase saiu.
A regra agora manda copiar o **rótulo em texto** do aparelho e, havendo só cor,
traduzir apenas pela tabela do fabricante — enquanto a linha estiver
`[PREENCHER]`, o campo vira `[VERIFICAR]` e o item para.

O que **falta**: o conteúdo da tabela, do manual de cada equipamento. Enquanto
não vier, exame cuja tela só traga cor não é laudado — é a conduta correta, e é
o comportamento que o pacote tem hoje.

> `branco` era o caso mais frágil: aparecia uma única vez em todo o pacote,
> colado a `verde` como "dentro", e nenhum arquivo definia o que a faixa branca
> significa em qualquer aparelho. Não preenchi por dedução, de propósito.

## 2. Limiar de intensidade de sinal

**Onde:** `references/base/04-artefatos.md` §"Sinal fraco", `[PREENCHER]`; e
`references/base/07-lacunas.md`.
**Formulário:** Bloco 3.3.

Comportamento atual, mantido: **não existe limiar numérico**. O exame só é
reprovado quando o próprio aparelho sinaliza qualidade insuficiente ou quando há
artefato na área de interesse. Índice baixo, sozinho, não reprova.

Se o médico marcar "prefiro não definir limiar numérico", esta pendência fecha
sem mudança de código — vira decisão registrada.

## 3. Nomes de parâmetro e de relatório por aparelho

**Onde:** `references/base/05-aparelhos.md`, colunas "Nome do relatório" e
"Parâmetros e unidades".
**Formulário:** Bloco 3.2 — anexar um relatório impresso de cada tipo de exame,
de cada aparelho, com os dados do paciente cobertos.

`references/extracao-tela.md` §2 já traz os rótulos **comuns** (`Disc Area`,
`C/D Area Ratio`, `RNFL Thickness Average`…). Isso cobre o caso geral e não
substitui os nomes exatos da tela de cada equipamento.

## 4. Quatro decisões de redação

**Onde:** `references/templates-hospitais.md` §8 (as três primeiras) e §7 (a quarta).
**Formulário:** Bloco 1, itens 1.1 a 1.4. E o Bloco 2 aprova as frases marcadas
`[proposta]` na biblioteca de §7.

| Questão | Padrão atual mantido |
|---|---|
| Reserva diagnóstica quando há parâmetro sinalizado | não incluir |
| "aparentemente dentro" vs "dentro" da normalidade | por hospital, como nos modelos |
| Nascimento no laudo do CRO | imprimir quando houver |
| "área da escavação" na conclusão vs "relação escavação/papila (área)" no corpo | manter como está, copiado do laudo real |

Nenhuma dessas quatro é defeito de código. Todas estão registradas em prosa, com
o "padrão atual" implementado, e o agente avisa no relatório final quando uma
delas afeta um laudo.

---

## A trava que continua de pé

`references/base/00-indice.md` diz `VERSÃO: 1.0-rascunho` e
`REVISADO POR: PENDENTE`. Enquanto disser, `laudo_pdf.py` **recusa emitir
qualquer laudo** — e agora recusa também quando a base está *ausente*, que antes
passava com um aviso.

Isso não é bug: é o desenho. A trava sai quando o médico revisar a base e as duas
linhas forem trocadas em `references/_fonte/base-cientifica.md`, seguidas de
`python3 scripts/dividir_guia.py`.

Para testar o pipeline antes disso existe `--base-nao-revisada`, que **carimba o
PDF** com "BASE CIENTÍFICA NÃO REVISADA" em todas as páginas. Nunca com paciente
real.

---

## Uma observação sobre o próprio formulário

O texto de abertura diz *"O Bloco 4 é a revisão da base em si"*, mas o documento
termina no Bloco 3 e no "Próximo passo" — **não existe Bloco 4**. Ou a frase de
abertura sai, ou o bloco entra. Como está, o médico pode preencher tudo e ficar
esperando uma quarta parte que nunca aparece.
