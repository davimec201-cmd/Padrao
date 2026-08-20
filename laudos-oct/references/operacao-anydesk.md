# Operação do AnyDesk — loop de navegação

Leia isto **antes do primeiro clique**.

## 1. Prefira o arquivo à tela — mas a dupla leitura continua

Se o sistema remoto **exportar o relatório do OCT em PDF** e o AnyDesk tiver
transferência de arquivo, traga o PDF: a imagem chega em resolução plena em vez de
comprimida, e o risco de ler `0,62` como `0,82` cai muito.

**A dupla leitura continua obrigatória mesmo assim.** Ela é regra inviolável (SKILL.md
§3.2) e nenhuma economia a dispensa. Você lê o número por visão nos dois casos; a
diferença é só a qualidade da imagem, não a natureza da leitura. Recorte de ROI custa
cerca de 250 tokens — é o item mais barato de toda a operação e o que protege o dado
que vai para um documento assinado.

## 2. Tabela de comandos

Todos relativos à pasta da skill. `S=` é o sidecar `.json` do último shot.

| Objetivo | Comando |
|---|---|
| Validar ambiente | `~/.claude/skills/laudos-oct/scripts/hands.py doctor` |
| Fixar área permitida | `~/.claude/skills/laudos-oct/scripts/hands.py guard set` |
| Ver janela / foco atual | `~/.claude/skills/laudos-oct/scripts/hands.py window` |
| Navegar (tela cheia, reduzida) | `~/.claude/skills/laudos-oct/scripts/hands.py shot --full --out shots/nav01.png` |
| Ler número (recorte nativo) | `~/.claude/skills/laudos-oct/scripts/hands.py shot --roi X,Y,W,H --from $S --out shots/roi01.png` |
| Clicar | `~/.claude/skills/laudos-oct/scripts/hands.py click --from $S 812 430` |
| Duplo clique / direito | `~/.claude/skills/laudos-oct/scripts/hands.py dblclick ... ` / `~/.claude/skills/laudos-oct/scripts/hands.py rclick ...` |
| Mover sem clicar | `~/.claude/skills/laudos-oct/scripts/hands.py move --from $S 812 430` |
| Arrastar | `~/.claude/skills/laudos-oct/scripts/hands.py drag 100 200 400 200 --from $S` |
| Digitar (acento OK) | `~/.claude/skills/laudos-oct/scripts/hands.py type "Maria da Silva"` |
| Tecla / combo | `~/.claude/skills/laudos-oct/scripts/hands.py key enter` · `~/.claude/skills/laudos-oct/scripts/hands.py key tab` · `~/.claude/skills/laudos-oct/scripts/hands.py key cmd+c` |
| Rolar | `~/.claude/skills/laudos-oct/scripts/hands.py scroll -6 --x 900 --y 500 --from $S` |
| **Esperar a tela responder** | `~/.claude/skills/laudos-oct/scripts/hands.py aguardar` |
| Só converter coordenada | `~/.claude/skills/laudos-oct/scripts/hands.py map --from $S 812 430` |
| Ensaiar sem agir | acrescente `--dry-run` |

Coordenadas vêm sempre em **pixels da imagem** que você acabou de ler, com `--from`
apontando para o sidecar daquela imagem. Nunca converta Retina na mão.

## 3. O loop

Para cada ação, quatro passos. Não pule o quarto.

1. **Observar** — `shot --full`. Leia a imagem. Diga a si mesmo, em uma linha, em que
   tela você está.
2. **Decidir** — escolha **um** alvo e leia a coordenada do centro dele na imagem.
3. **Agir** — `click --from ...`. Depois, **não chute o tempo de espera**: rode
   `hands.py aguardar`. Ele observa a janela localmente e volta quando a tela
   estabiliza — **sem gastar token nenhum**, porque o modelo não fica olhando print
   atrás de print. `sleep` fixo erra nos dois sentidos: curto demais numa conexão
   lenta, longo demais numa rápida.

   ```bash
   hands.py click --from shots/nav01.json 812 430
   hands.py aguardar --modo estabilizar --exigir-mudanca --timeout 60
   hands.py shot --full --out shots/nav02.png
   ```

   Saiu com `"timeout": true` significa que a tela não se moveu no tempo dado. Isso
   é conexão lenta ou clique sem efeito — **aumente o `--timeout`, não clique de
   novo.**
4. **Verificar** — novo `shot --full`. A tela mudou para o que você esperava?
   - Sim → siga.
   - Não → **não clique de novo**. Volte ao passo 1 e reavalie. Duas verificações
     falhadas seguidas: pare e chame o usuário.

## 4. Regras de clique

- Clique no **centro** do elemento, não na borda.
- Um clique por vez. Nunca encadeie três cliques "no escuro".
- Se o guard recusar por foco: o AnyDesk perdeu o primeiro plano. Reative a janela
  e refaça o `shot`. Não use `--anywhere` para contornar guard — ele existe para
  impedir que você clique no Mail, no Slack ou no Finder do usuário.
- **Teclado e mouse têm a mesma regra.** O atalho não é rota alternativa para o
  que o botão não pode fazer: `key` passa pela mesma guarda de foco do clique e
  **recusa** `cmd+s`, `cmd+p`, `cmd+x`, `cmd+delete`, `cmd+q` e `cmd+w`. Se um
  atalho for recusado, é porque ele gravaria, imprimiria ou fecharia o sistema —
  pare e pergunte, não procure outro caminho.
- `key` também recusa tecla fora da tabela conhecida. Para digitar texto existe
  `type`, que escapa o conteúdo e pede confirmação ao usuário.

## 4b. Diálogos conhecidos — os únicos que você pode responder

A regra geral é não clicar em pop-up desconhecido. Estes são a exceção: são
identificados **pelo texto dos botões**, não pela posição, e cada um tem **uma única**
resposta permitida.

### "O programa não está respondendo"

Aparece quando a internet do lado remoto está lenta e o sistema do hospital demora.
Texto típico: *"O programa não está respondendo"* / *"não está respondendo"* /
*"is not responding"*, com dois botões.

| Botão | O que fazer |
|---|---|
| `Aguardar que o programa responda` · `Aguardar` · `Wait` | **É este.** Clique nele. |
| `Fechar o programa` · `Fechar` · `Forçar encerramento` · `End task` · `Force Quit` | **Nunca.** Fecharia o sistema do hospital e poderia perder o exame aberto. |

Procedimento:

1. `shot --full` e **leia o texto dos botões**. A ordem varia entre versões e
   idiomas — nunca clique "o da esquerda" de memória.
2. Clique no botão de aguardar.
3. `hands.py aguardar --modo estabilizar --exigir-mudanca --timeout 120` — conexão
   lenta merece tempo generoso, e esperar não custa token.
4. `shot --full` e confira que o diálogo saiu antes de retomar.
5. Se o mesmo diálogo voltar **três vezes no mesmo paciente**, pare e avise o
   usuário: a conexão não está em condição de laudar, e insistir só produz leitura
   ruim de número.

**Nenhum outro diálogo tem resposta autorizada.** Qualquer outro: `shot --full`,
descreva ao usuário, não clique.

## 5. Nunca clicar

Lista negra absoluta no sistema do hospital. Você é **somente-leitura** lá dentro:

`Excluir` · `Apagar` · `Delete` · `Remover` · `Editar paciente` · `Salvar alterações` ·
`Enviar` · `Assinar` · `Liberar` · `Finalizar atendimento` · `Cancelar exame` ·
`Fechar o programa` · `Forçar encerramento` · `Force Quit` · `End task` ·
qualquer coisa que altere prontuário, agenda ou o próprio exame.

**E os atalhos equivalentes**, que fazem a mesma coisa sem passar por botão:
`cmd+s` (salvar) · `cmd+shift+s` (salvar como) · `cmd+p` (imprimir) ·
`cmd+x` (recortar) · `cmd+delete` (lixeira) · `cmd+q` e `cmd+w` (fechar o
sistema do hospital). O `hands.py key` recusa todos.

Se o caminho que você quer só existe passando por um desses botões, **pare e pergunte**.

## 6. Ler números com precisão

1. `shot --full` para localizar a tabela.
2. `shot --roi` cercando **só** a tabela, com uma folga de ~10 px.
3. Leia e anote os valores.
4. **Segunda leitura:** repita o `--roi` com enquadramento diferente (mais largo, ou
   dividido em duas metades). Leia de novo, sem olhar a primeira anotação.
5. Bateram → valor confirmado. Divergiram ou algum ficou ilegível → `[VERIFICAR]`.

Se a fonte na tela estiver pequena demais, aumente o zoom **dentro do sistema remoto**
(ou o zoom da própria janela do AnyDesk) e recapture. Nunca "amplie por interpolação"
mentalmente um dígito borrado.

## 7. Quando algo dá errado

| Sintoma | O que fazer |
|---|---|
| Diálogo "não está respondendo" | Conexão lenta. Clique em **Aguardar** (§4b), nunca em Fechar. |
| `aguardar` retorna `timeout: true` | A tela não se moveu. Aumente o `--timeout`. **Não clique de novo.** |
| `loop travado` numa conexão lenta | O detector está certo: você clicou 3× no mesmo ponto porque a tela não respondeu. A saída é **esperar mais**, com `aguardar --timeout 120`, não clicar mais rápido. |
| `STOP ativo` | O usuário acionou o freio. Pare tudo e avise. |
| `foco protegido` | Reative o AnyDesk. Não force. |
| `clique fora da área permitida` | A janela do AnyDesk mudou de posição/tamanho → `guard set` de novo. |
| `janela_anydesk_pt: NÃO ENCONTRADA` | AnyDesk fechado, minimizado ou em outro Space. Peça ao usuário. |
| Captura falha / imagem preta | Falta permissão de Gravação de Tela → `INSTALACAO.md`. |
| Clique não faz nada | Falta permissão de Acessibilidade → `INSTALACAO.md`. |
| Tela congelada / sessão caiu | Não tente reconectar sozinho. Avise o usuário. |
| Aparece pop-up desconhecido | `shot --full`, descreva ao usuário, **não clique**. |

## 8. Higiene de contexto

- Grave os shots em `shots/<paciente>/` e não recarregue print de paciente anterior.
- Ao terminar um paciente, o subagente dele morre e leva as imagens embora. É de
  propósito. No fluxo principal, apenas não releia imagens antigas.
