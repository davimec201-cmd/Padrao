# Instalação — skill `laudos-oct`

Uma vez só. Dá uns 15 minutos, a maior parte esperando download.

**A skill roda em macOS e em Windows.** Os passos são os mesmos; onde muda, a seção
diz qual é qual. Se você vai rodar em Windows, leia também `SEGURANCA.md` §3 — lá
existe **uma camada de proteção a menos**, e isso muda o que sustenta a segurança
da estação.

---

## Passo 1 — Instalar o Claude Code

Esta skill precisa do **Claude Code**, não do Cowork: só ele consegue executar o
script que move o mouse e digita na sua máquina.

**macOS** — abra o Terminal (Spotlight → "Terminal") e cole:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows** — instale antes o [Git para Windows](https://git-scm.com/download/win)
(o Claude Code usa o Git Bash como terminal) e o
[Python](https://www.python.org/downloads/), marcando **"Add python.exe to PATH"**.
Depois, no Git Bash, o mesmo comando acima.

Depois:

```bash
claude
```

Ele pede login na primeira vez. Requer assinatura paga do Claude.

> Preferindo interface gráfica, existe o app desktop do Claude Code em
> code.claude.com — a skill funciona igual nos dois. O Terminal é o caminho
> mais curto para a primeira configuração.

## Passo 2 — Instalar a skill

Descompacte o `laudos-oct.skill` (é um zip) dentro da pasta de skills:

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
unzip ~/Downloads/laudos-oct.skill -d .
ls ~/.claude/skills/laudos-oct/SKILL.md   # deve existir
```

## Passo 3 — Instalar dependências

**macOS:**
```bash
bash ~/.claude/skills/laudos-oct/scripts/setup.sh
```

**Windows** (no PowerShell, uma vez, como operador — o agente não roda isto):
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\laudos-oct\scripts\setup.ps1"
```

Ele instala o que falta, cria a pasta `Laudos_OCT` e roda o diagnóstico no fim.

## Passo 3b — Instalar o endurecimento (não pule)

Sem isto a estação roda com shell livre e controle de tela: nenhuma das travas
descritas em `SEGURANCA.md` existe. **O `doctor` do Passo 5 reprova enquanto
faltar.**

**macOS:**
```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/laudos-oct/hardening/hooks/guardiao-laudos.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/guardiao-laudos.py
cp ~/.claude/skills/laudos-oct/hardening/settings-macos.json ~/.claude/settings.json
```

**Windows** (Git Bash):
```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/laudos-oct/hardening/hooks/guardiao-laudos.py ~/.claude/hooks/
cp ~/.claude/skills/laudos-oct/hardening/settings-windows.json ~/.claude/settings.json
```

> **Os dois perfis não são o mesmo arquivo com caminhos trocados.** O do Windows
> **não tem** o bloco `sandbox` — aquilo é o Seatbelt, do kernel do macOS. Em troca,
> a lista `deny` do Windows é o dobro do tamanho, porque está compensando a ausência
> dele. Leia o aviso no topo do `settings-windows.json`.

> **Já tem um `~/.claude/settings.json`?** Não sobrescreva às cegas: abra os dois
> e junte à mão os blocos `permissions`, `sandbox` e `hooks`. `SEGURANCA.md` §3
> explica o que cada um faz.

O que isso liga: lista de comandos permitidos, sandbox do macOS (Seatbelt), o
hook guardião que barra comando destrutivo e saída de rede, e a confirmação
humana antes de qualquer digitação. Leia `SEGURANCA.md` antes de rodar com
paciente real — as duas camadas mais fortes (login somente-leitura no hospital e
conta macOS dedicada) não são arquivo, são pedido à TI e cinco minutos de ajuste.

## Passo 4 — Conceder as permissões do macOS

Sem isto a skill não vê a tela nem clica. **Ajustes do Sistema → Privacidade e
Segurança:**

| Permissão | Para quê | Ligar para |
|---|---|---|
| **Gravação de Tela** | capturar a janela do AnyDesk | Terminal (ou iTerm / Claude) |
| **Acessibilidade** | mover mouse e digitar | o mesmo app |
| **Automação** | ler posição da janela (System Events, Finder) | o mesmo app |

**Feche e reabra o Terminal depois de conceder** — o macOS só aplica na reabertura.
Em macOS recente, a Gravação de Tela pode pedir reconfirmação periódica; é normal.

### No Windows não há esse passo

O Windows não pede permissão para capturar a tela nem para mover o mouse. Isso
facilita a instalação e **piora a sua posição**: no macOS, negar Acessibilidade era
um freio de emergência do próprio sistema operacional; aqui esse freio não existe, e
o sandbox de kernel também não. O que sobra é o `STOP`, a lista `deny` e o guardião.

Duas coisas que valem no Windows e não valiam no macOS:

- **Escala do monitor.** O `hands.py` declara consciência de DPI e trabalha em pixels
  físicos. **Não mude a escala nem troque de monitor com a fila rodando** — a
  conversão de coordenada muda no meio e o clique passa a cair no elemento vizinho,
  dentro da janela, onde a guarda de retângulo não pega.
- **OneDrive.** Confira em Configurações do OneDrive → Backup que a pasta
  `Laudos_OCT` não está incluída. Laudo em pasta sincronizada é dado de paciente na
  nuvem de terceiro sem você decidir isso.

## Passo 5 — Conferir

Abra o AnyDesk, conecte na sessão do hospital, deixe a janela visível (não
minimizada, no mesmo Space) e rode:

```bash
python3 ~/.claude/skills/laudos-oct/scripts/hands.py doctor
```

Você quer ver `"VEREDITO": "PRONTO"`. Se vier `NAO_PRONTO`, o campo que falhou está
descrito ali mesmo.

Calibre a área de clique permitida:

```bash
python3 ~/.claude/skills/laudos-oct/scripts/hands.py guard set
```

(Refaça isso sempre que mover ou redimensionar a janela do AnyDesk.)

## Passo 6 — Usar

Na pasta que você quiser, rode `claude` e peça em português:

> lauda os OCTs da fila do AnyDesk

A skill dispara sozinha. Os PDFs saem em
`~/Laudos_OCT/<Hospital>/<Paciente>/Laudo_<SIGLA>_<Paciente>_<MAC|NO>_<OD|OE|AO>_<data>.pdf`,
carimbados **"MINUTA — CONFERIR E ASSINAR"** até o médico assinar.

> **Antes do primeiro laudo real:** a base científica ainda não passou pela
> revisão do médico, e o gerador **recusa emitir** enquanto não passar. Isso é
> trava de programa. Ver `PENDENCIAS.md`.

---

## Freio de mão

Para travar tudo na hora, de qualquer terminal:

```bash
touch ~/Laudos_OCT/STOP
```

Enquanto esse arquivo existir, nenhum clique ou tecla é executado. Para liberar:

```bash
rm ~/Laudos_OCT/STOP
```

Além disso: mover o mouse rapidamente para o **canto superior esquerdo** da tela
aborta a ação em andamento (failsafe do pyautogui).

## Problemas comuns

| Erro | Causa e solução |
|---|---|
| `captura_de_tela: FALHOU` | Falta Gravação de Tela. Conceda e **reabra o Terminal**. |
| Clique não acontece | Falta Acessibilidade. Conceda e reabra o Terminal. |
| `tela_pt: FALHOU` | Falta Automação para System Events/Finder. |
| `janela_anydesk_pt: NÃO ENCONTRADA` | AnyDesk fechado, minimizado ou em outro Space. |
| `motor_de_clique: AUSENTE` | Rode o `setup.sh` de novo, ou `brew install cliclick`. |
| `foco protegido` | Clique na janela do AnyDesk para trazê-la à frente. |
| `clique fora da área permitida` | A janela mudou de lugar → `hands.py guard set`. |
| `STOP ativo` | Rode `rm ~/Laudos_OCT/STOP` **de outro terminal** — o agente não consegue remover o freio. |
| `plataforma: NÃO SUPORTADA` | A skill roda em macOS e Windows. |
| `pillow: False` (Windows) | Rode o `setup.ps1` de novo. Sem pillow não há captura de tela. |
| Clique cai deslocado (Windows) | A escala do monitor mudou depois do `guard set`. Refaça `guard set` e rode `doctor`. |
| `hook_guardiao: AUSENTE` | Falta o Passo 3b. |
| `settings_endurecido: INCOMPLETO` | Falta o Passo 3b, ou o `settings.json` foi sobrescrito. |
| `ERRO: base científica não liberada` | A base ainda não foi revisada pelo médico. Ver `PENDENCIAS.md`. |

## Ajustes que você provavelmente vai querer

- **Marca das clínicas:** já vem pronta em `assets/marca/` (faixa navy do Bonavita,
  marca de água e logo do CRO), extraída dos laudos modelo — layout calibrado
  contra eles.
- **Assinatura:** por decisão da clínica, o laudo sai sempre **sem assinatura
  digitalizada** — espaço em branco para assinar à mão. Não há imagem de
  assinatura no pacote **e não há caminho no código para embutir uma**: a
  capacidade foi removida, não apenas desligada.
- **Outra pasta de saída:** edite `OUT_ROOT` em `scripts/hands.py` e
  `scripts/laudo_pdf.py`.
- **Outro app remoto (não AnyDesk):** troque `TARGET_APP` em `scripts/hands.py`
  pelo nome exato do app. No Windows é o nome do executável sem o `.exe`.
