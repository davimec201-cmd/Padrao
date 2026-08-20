# Segurança da estação de laudos — análise e endurecimento

## 1. O problema real

Para operar o AnyDesk, o Claude Code precisa de duas coisas perigosas ao mesmo tempo:
**controle de mouse e teclado da tela inteira** e **shell livre no macOS**. Com isso,
por acidente e sem nenhuma má intenção, ele pode:

| Onde | O que pode acontecer sem querer |
|---|---|
| Sua máquina | apagar, mover ou sobrescrever arquivo seu; alterar configuração; instalar coisa |
| Sua tela | clicar/digitar na janela errada quando o foco muda ou o AnyDesk atrasa |
| Sistema do hospital | clicar num botão destrutivo que leu errado; alterar prontuário |
| Dado de paciente | print com nome de paciente parado numa pasta sincronizada; nome em log |
| Custo/ruído | loop de milhares de cliques queimando token e martelando o sistema remoto |

## 2. Por que as travas do `hands.py` não bastam

O `hands.py` tem freio de mão (`STOP`), guarda de foco (que **falha fechado** quando
não consegue ler o foco), guarda de retângulo, tabela fechada de teclas com recusa de
`cmd+s`/`cmd+p`/`cmd+q`, teto de taxa e detector de loop — e `scroll` e `drag` também
entram no rastro e no teto. Tudo isso é **conselho, não jaula**: vale enquanto o agente
usar o `hands.py`. Um modelo tentando resolver um clique que falhou tende a tentar
outro caminho — `python3 -c "import pyautogui; pyautogui.click(...)"` — e contorna as
cinco travas de uma vez.

**Conclusão de arquitetura:** o controle que importa tem de morar onde o modelo não
alcança. Três lugares: o permissionamento do Claude Code, o macOS, e a conta que
vocês usam no sistema do hospital.

## 3. As quatro camadas, em ordem de valor

### Camada 1 — Login somente-leitura no sistema do hospital ★ maior valor, custo zero

Peça à TI do hospital um usuário **sem permissão de escrita** no sistema de exames:
vê, abre, dá zoom, exporta; não edita, não apaga, não assina, não libera.

Isto é qualitativamente superior a qualquer coisa que eu escreva. Se a credencial não
consegue apagar, **nenhuma** falha de leitura, de clique ou de raciocínio consegue
apagar. As outras três camadas reduzem probabilidade; esta elimina a consequência.

Se a TI perguntar por quê: "vamos usar uma ferramenta de leitura automatizada de
exames e queremos garantia técnica de que ela não altera registro."

### Camada 2 — Usuário do macOS dedicado ★ segunda maior alavanca

Crie uma conta **padrão (não-administrador)** no Mac, ex. `laudos`, e rode tudo lá.

Ajustes do Sistema → Usuários e Grupos → Adicionar Usuário → tipo **Padrão**.

O raio de dano encolhe para dentro daquela conta: seus documentos, e-mail, Fotos,
Chaves e iCloud pessoais ficam inacessíveis por construção do sistema operacional,
não por regra que alguém pode contornar. Conceda as permissões de Gravação de Tela e
Acessibilidade **só nessa conta**. E como é conta padrão, `sudo` não existe.

### Camada 3 — `settings.json` com sandbox do macOS

Está pronto em `hardening/settings.json`. Duas partes:

**Permissões** — `allow` só os dois scripts da skill; `deny` em 39 padrões:
`rm`, `mv`, `sudo`, `chmod`, `curl`, `wget`, `ssh`, `git push`, `osascript`,
`screencapture`, `security`, `pbcopy`, `launchctl`, `open`, mais leitura de
`~/Library`, `~/.ssh`, `~/Documents`, `~/Desktop`, `~/Downloads`, `~/Pictures`, e
escrita nas próprias configurações. `WebFetch` e `WebSearch` negados — dado de
paciente não vai para busca.

**Sandbox** — no macOS usa o **Seatbelt**, que já vem no sistema: nada a instalar.
É imposto pelo kernel, não pelo modelo. A configuração restringe escrita a
`~/Laudos_OCT` e `~/.laudos_oct`, nega leitura de todo o resto do home, e zera a rede
(`allowedDomains: []`). `allowUnsandboxedCommands: false` fecha a saída de emergência.

> **Teste isto no primeiro dia.** O Seatbelt pode barrar o evento de mouse — clicar
> exige falar com o WindowServer. Por isso o `excludedCommands` já tira **só** o
> `hands.py` do sandbox. Se o clique não funcionar com sandbox ligado, o problema é
> esse e a saída já está configurada. Se funcionar dentro do sandbox, melhor ainda:
> remova o `excludedCommands`.

Duas armadilhas de instalação:

- **Rode o Claude Code de uma pasta dedicada**, ex. `~/laudos-trabalho` — não de
  dentro de `~/Documents`, que está na lista de leitura negada.
- O Claude Code em modo Manual **já** limita escrita à pasta onde foi iniciado e suas
  subpastas. Isso é de fábrica e ajuda: use a favor.

### Camada 4 — Hook guardião (backstop determinístico)

`hardening/hooks/guardiao-laudos.py` roda como `PreToolUse` em todo comando Bash e
decide com resposta estruturada. É código, não instrução: o modelo não argumenta com
ele. **Não depende de nada além do python3** — a primeira versão usava `jq` e, quando
`jq` faltava, o comando saía vazio e o hook **liberava tudo em silêncio**. Agora falha
fechado: entrada que ele não entende é negada.

| # | Decisão |
|---|---|
| 1 | **nega** `rm`, `rmdir`, `mv`, `shred`, `dd`, `diskutil`, redirecionamento destrutivo |
| 1b | **nega** `killall`, `pkill`, `kill`, `osascript ... quit` — matar o AnyDesk derruba a sessão e o exame aberto |
| 2 | **nega** `sudo`, `su`, `chmod`, `chown`, `launchctl`, `csrutil`, `defaults write` |
| 3 | **nega** `curl`, `wget`, `ssh`, `scp`, `rsync`, `git push`, `pbcopy`, `sendmail` |
| 4 | **nega** Chaves, `.ssh`, `.aws`, Mail, Messages, Fotos, histórico do Safari |
| 5 | **nega** ação de tela enquanto `~/Laudos_OCT/STOP` existir |
| 6 | **nega** `pyautogui`, `cliclick`, `osascript`, `screencapture`, `xdotool` fora do `hands.py` — e "fora do hands.py" quer dizer que o comando **começa** com `python3 .../hands.py` e não encadeia (`;`, `&&`, `\|`, `$(...)`). Antes bastava a string `hands.py` aparecer em qualquer ponto da linha, inclusive num comentário |
| 7 | **nega** autoescalada: `settings.json`, hooks, `.zshrc`, arquivos da skill, o `config.json` com os tetos de taxa **e o `~/Laudos_OCT/STOP`** — o freio de mão estava menos protegido que o teto de taxa |
| 8 | **escala para você** qualquer comando com `--anywhere`, que desliga a guarda de foco |
| — | grava em `~/.laudos_oct/guardiao.log`, com `chmod 600` e **omitindo o texto digitado** — o log guardava o nome do paciente em claro, sem prazo de expurgo |

Leitura é permitida (`cat`, `grep`, `sed -n`, `awk`); escrita in-place não
(`sed -i`, `perl -i`, `tee`, `>>`).

O item 7 é o que fecha o círculo: sem ele, um agente poderia reescrever as próprias
regras — ou só o próprio teto de taxa — e as outras famílias cairiam junto. O item 8
existe porque `--anywhere` é a única porta legítima para clicar fora do AnyDesk, e
porta legítima sem aval humano é porta aberta.

## 4. Reduzir a chance do acidente

- **Space dedicado.** Deixe o AnyDesk sozinho num Desktop/Space em tela cheia. Se não
  há mais nada clicável, não há clique perdido.
- **Não Perturbe ligado.** Notificação roubando foco no meio de um clique é a causa
  mais provável de digitar no lugar errado.
- **O agente nunca faz login.** Você conecta o AnyDesk e autentica no sistema do
  hospital; só depois entrega. A skill tem regra explícita de parar ao ver campo de
  senha. Senha nunca deve passar pelo `hands.py type` — ficaria no log de auditoria.
- **Pasta de saída fora de sincronização.** `~/Laudos_OCT` está na raiz do home,
  fora do iCloud Drive. Confira que "Pastas Documentos e Mesa" no iCloud está
  **desligado**, ou que ao menos `~/Laudos_OCT` não caia dentro. Laudo em pasta
  sincronizada = dado de paciente na nuvem de terceiro sem você decidir isso.
- **Prints são dado clínico.** `hands.py purge` apaga todos, `purge --dias 7` os
  antigos. Rode ao fim de cada turno. O `--dir` só aceita caminho dentro de
  `~/Laudos_OCT`: antes apagava `*.png/*.json/*.jpg` recursivamente em qualquer
  pasta que recebesse.
- **Temporários de captura ficam em `~/.laudos_oct/tmp`**, com `chmod 600` e
  removidos no `finally`. Antes iam para `/tmp` com nome fixo e sobreviviam ao
  caminho de erro — captura de tela cheia do sistema do hospital, legível por
  qualquer processo da máquina.
- **Nunca** `--dangerously-skip-permissions`. Nesta estação, jamais.
- **Prefira regra explícita ao modo automático.** O auto mode usa um classificador
  para decidir sozinho. Para este fluxo, `defaultMode: "default"` com a lista de
  `allow` curta é mais previsível.

## 5. O ponto que não é sobre clique

Vale mais que todas as camadas acima, e não se resolve com configuração.

**Os prints dos exames saem da máquina.** O "olho" da skill é o modelo, que roda na
nuvem: cada recorte com nome de paciente e imagem de retina é enviado à API da
Anthropic para ser lido. Isso não é falha — é o desenho. Mas significa que existe
tratamento de dado pessoal sensível por operador externo, e isso tem consequência
sob a LGPD: base legal, registro da operação, e provavelmente contrato de tratamento
de dados. Os termos aplicáveis mudam conforme o plano (consumidor vs comercial),
inclusive quanto a retenção e a uso para treino.

Não sou advogado e isto não é orientação jurídica. Mas é a pergunta que eu levaria a
quem cuida de LGPD na clínica **antes** do primeiro paciente real, porque é a única
da lista que não tem correção técnica depois do fato. Verifique também os termos do
plano de vocês diretamente com a Anthropic.

Mitigação parcial que está no seu alcance: se o sistema do hospital exportar o
relatório em PDF, a skill prefere o arquivo à tela — menos imagem trafegada, e
recorte de ROI em vez de tela cheia reduz o que é enviado.

## 6. Checklist de implantação

```
[ ] Login somente-leitura no sistema do hospital (pedido à TI)
[ ] Conta macOS "laudos", tipo Padrão, sem admin
[ ] cp hardening/settings.json            ~/.claude/settings.json
[ ] cp hardening/hooks/guardiao-laudos.py ~/.claude/hooks/  && chmod +x
[ ] Pasta de trabalho dedicada (~/laudos-trabalho), fora de Documents
[ ] Gravação de Tela + Acessibilidade + Automação, só na conta laudos
[ ] iCloud "Documentos e Mesa" desligado, ou ~/Laudos_OCT fora dele
[ ] Não Perturbe ligado; AnyDesk sozinho num Space em tela cheia
[ ] hands.py doctor  ->  VEREDITO: PRONTO
[ ] hands.py guard set
[ ] Teste do sandbox: o clique funciona com sandbox ligado?
[ ] Pergunta de LGPD levada a quem responde por isso na clínica
```

## 7. Primeira semana: modo sombra

Antes de confiar, gaste uma semana assim:

1. **Dia 1 — só olhos.** Peça para navegar e extrair valores, **sem** gerar PDF.
   Todo clique com `--dry-run`. Você lê o que ele diria clicar. Custo zero de risco.
2. **Dia 2 — um paciente de teste.** Um registro de demonstração, ou um exame antigo
   já laudado por vocês. Compare o laudo dele com o de vocês, campo por campo.
3. **Dias 3 a 5 — três pacientes reais por dia**, com você olhando a tela. É aqui que
   você vê a dupla leitura funcionando e descobre onde ela erra.
4. **Só então a fila inteira** — e sempre com o médico revisando antes de liberar.

Todo dia: `hands.py log --resumo`. Se aparecer `recusa/loop_travado` ou
`recusa/teto_por_minuto`, alguma tela está enganando o agente. Investigue antes de
aumentar o teto.

## 8. Quando algo der errado

1. `touch ~/Laudos_OCT/STOP` — congela toda ação de tela na hora.
2. Mouse rápido para o canto superior esquerdo aborta a ação em curso (failsafe).
3. `Ctrl+C` na sessão do Claude Code.
4. `hands.py log -n 100` e `~/.laudos_oct/guardiao.log` — o rastro completo do que
   foi feito e do que foi negado, com hora.
5. Se algo mudou no sistema do hospital: avise a TI **na hora**, com o horário e o
   trecho do log. Registro clínico alterado é assunto de prontuário, não de TI.

## 9. Assinatura digitalizada

**A clínica decidiu não usar assinatura digitalizada.** O PDF sai sempre com o espaço
em branco e nome/registros impressos abaixo, para assinatura à mão. Nenhuma imagem de
assinatura acompanha o pacote — **e não existe caminho no código para embutir uma**.
O parâmetro `--assinatura` do `laudo_pdf.py` foi removido: decisão em prosa com o
mecanismo intacto no código é decisão que uma linha de comando desfaz.

Vale entender o que a opção muda. Um PDF sem assinatura é uma minuta: quem assina
declara ter revisado. Um PDF que já sai assinado é um documento executado — e se ele
foi gerado, assinado e salvo sem ninguém olhar, a declaração de revisão não
corresponde ao que aconteceu. Quem carrega a consequência disso é o CRM impresso ali.

Se a clínica quiser automatizar, que seja decisão explícita do médico que assina, e de
preferência amarrada ao momento em que ele realmente conferiu — não ao momento em que
o arquivo foi criado.

## 10. Limites honestos

- Nada disto protege contra o erro que mais importa: **número lido errado indo para
  um laudo assinado**. Contra isso existem a dupla leitura, o `[VERIFICAR]`, a pasta
  `_PENDENTES/`, o carimbo **"MINUTA — CONFERIR E ASSINAR"** em todas as páginas —
  e a revisão do médico, que é insubstituível. O carimbo impede que a minuta seja
  confundida com laudo pronto dentro da pasta; ele não confere número nenhum.
- O sandbox e os hooks reduzem muito, não zeram. A recomendação da própria Anthropic
  para trabalho com conteúdo não confiável inclui rodar em VM.
- A configuração mais forte que existe aqui é a mais chata de conseguir: o login
  somente-leitura. Se você só for atrás de uma coisa desta lista, vá atrás dessa.
