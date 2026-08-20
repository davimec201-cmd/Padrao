#!/usr/bin/env python3
"""
guardiao-laudos.py — backstop determinístico da estação de laudos de OCT.

Hook PreToolUse (matcher: Bash). Lê o JSON do Claude Code no stdin e decide.
Ao contrário das travas de dentro do hands.py, este hook é aplicado pelo harness:
o modelo não argumenta com ele nem o contorna escrevendo outro script.

Instalação:
  cp guardiao-laudos.py ~/.claude/hooks/ && chmod +x ~/.claude/hooks/guardiao-laudos.py

Não depende de jq. Falha FECHADO: se não conseguir entender o comando, nega.
"""

import json
import re
import sys
import time
from pathlib import Path

HOME = Path.home()
LOG = HOME / ".laudos_oct" / "guardiao.log"
STOP = HOME / "Laudos_OCT" / "STOP"
SKILL = ".claude/skills/laudos-oct"


def redige(cmd):
    """Tira o dado de paciente do que vai para o log.

    'hands.py type "Maria da Silva"' era gravado inteiro: o log de segurança
    virava um índice de quem foi atendido, sem prazo de expurgo."""
    return re.sub(r'((?:hands\.py|\btype\b)\s+)(["\']).*?\2',
                  r'\1"<texto omitido>"', cmd)


def registra(veredito, motivo, cmd):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        novo = not LOG.exists()
        with LOG.open("a") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} | {veredito} | "
                    f"{motivo} | {redige(cmd)[:400]}\n")
        if novo:
            LOG.chmod(0o600)
    except Exception:
        pass


def decide(acao, motivo, cmd):
    registra(acao.upper(), motivo, cmd)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": acao,
        "permissionDecisionReason": motivo,
    }}, ensure_ascii=False))
    sys.exit(0)


nega = lambda m, c: decide("deny", m, c)
escala = lambda m, c: decide("escalate", m, c)

# ------------------------------------------------------------------ entrada

try:
    dados = json.load(sys.stdin)
except Exception as e:
    # falha FECHADO: sem entender a entrada, não libera nada
    decide("deny", f"guardião não conseguiu interpretar a chamada ({e}). "
                   "Nada é liberado sem análise.", "<entrada ilegível>")

cmd = (dados.get("tool_input") or {}).get("command") or ""
if not cmd.strip():
    sys.exit(0)                      # nada a analisar (não é Bash com comando)

# ------------------------------------------------------------------- regras
# Cada regra: (regex, motivo). Fronteira de palavra evita falso positivo
# do tipo "platform " casando com "rm ".

TELA = r"pyautogui|pynput|cliclick|xdotool|osascript|screencapture|CGEvent|Quartz"
# Ancorado no INÍCIO do comando: antes bastava a string "hands.py" aparecer em
# qualquer ponto — num comentário, num nome de arquivo — para a porta de
# controle de tela (regra 6) abrir para o resto da linha.
E_HANDS = re.match(r"\s*python3?\s+\S*hands\.py\b", cmd) is not None
# E um comando encadeado nunca é "só o hands.py".
TEM_ENCADEAMENTO = re.search(r"[;&|]|\$\(|`|\n", cmd) is not None

REGRAS = [
    # 1. destrutivo / irreversível
    (r"(^|[;&|]\s*|\s)(rm|rmdir|shred|unlink|mv|dd|mkfs\w*|diskutil)\s",
     "Comando destrutivo bloqueado. Nesta estação nada é apagado ou movido — "
     "arquivo de paciente é registro clínico. Para descartar prints use "
     "'hands.py purge', que registra em log."),
    (r">\s*/dev/|:\s*>\s*\S|truncate\s",
     "Truncar ou sobrescrever arquivo por redirecionamento é bloqueado."),

    # 1b. encerrar processo: mata a sessão do AnyDesk e o exame aberto com ela
    (r"(^|[;&|]\s*|\s)(killall|pkill|kill)\s|osascript.*\b(quit|terminate)\b",
     "Encerrar processo é bloqueado. Matar o AnyDesk derruba a sessão remota e pode "
     "perder o exame aberto no sistema do hospital. Conexão lenta se resolve "
     "esperando (hands.py aguardar), não fechando."),

    # 2. privilégio / sistema
    (r"(^|[;&|]\s*|\s)(sudo|su|chmod|chown|launchctl|csrutil|spctl|systemsetup)\s",
     "Alteração de privilégio ou de sistema bloqueada nesta estação."),
    (r"defaults\s+write",
     "Alteração de preferências do sistema bloqueada."),

    # 3. exfiltração de dado clínico (LGPD)
    (r"(^|[;&|]\s*|\s)(curl|wget|nc|ncat|telnet|ssh|scp|sftp|rsync|ftp)\s",
     "Saída de rede bloqueada. Nome e imagem de paciente não saem desta máquina "
     "por comando de shell."),
    (r"git\s+push|pbcopy|sendmail|(^|\s)mail\s|osascript.*Mail",
     "Envio de dado para fora bloqueado (LGPD)."),

    # 4. leitura de área pessoal / credencial
    (r"Keychains|\.ssh/|\.aws/|security\s+(find|dump)|/Mail/|/Messages/|chat\.db|"
     r"Photos\.sqlite|Safari/History|Cookies\.binarycookies",
     "Leitura de área pessoal ou de credencial do usuário bloqueada. "
     "Esta sessão só enxerga ~/Laudos_OCT e a pasta da skill."),
]

for rx, motivo in REGRAS:
    if re.search(rx, cmd):
        nega(motivo, cmd)

# 5. freio de mão: com STOP ativo, nenhuma ação de tela
if STOP.exists():
    if re.search(TELA, cmd) or (E_HANDS and not re.search(
            r"hands\.py\s+(doctor|window|log|guard\s+show)", cmd)):
        nega(f"STOP acionado pelo operador ({STOP}). Nenhuma ação na tela até "
             "'rm ~/Laudos_OCT/STOP'.", cmd)

# 6. controle de tela só pela via auditada
if re.search(TELA, cmd) and not (E_HANDS and not TEM_ENCADEAMENTO):
    nega("Controle de tela só é permitido via scripts/hands.py, que registra em "
         "log, limita a taxa e respeita as guardas de foco e de janela. "
         "Use: python3 ~/.claude/skills/laudos-oct/scripts/hands.py <comando>", cmd)

# 7. autoescalada: reescrever as próprias regras ou os próprios limites
ALVO_PROTEGIDO = (r"\.claude/settings|\.claude/hooks|guardiao-laudos|"
                  r"\.zshrc|\.bashrc|\.zprofile|\.profile|"
                  + SKILL.replace(".", r"\.") + r"|"
                  r"\.laudos_oct/config\.json|"
                  # O freio de mão estava menos protegido que o teto de taxa:
                  # ~/Laudos_OCT é gravável pelo sandbox, e os.remove(STOP) não
                  # casava com a regra de 'rm' (que exige a palavra seguida de espaço).
                  r"Laudos_OCT/STOP")
# leitura é permitida; escrita não. 'sed -n' e 'awk' leem; 'sed -i' escreve.
EDITOR_IN_PLACE = re.search(r"sed\s+(-\w*\s+)*-i|perl\s+-\w*i|(^|\s)tee\s|>>?\s", cmd)
E_LEITURA = (re.match(r"\s*(cat|less|more|head|tail|ls|grep|egrep|rg|wc|file|stat|nl|"
                      r"diff|md5|shasum|awk|sed\s+-n|python3\s+\S*(hands|laudo_pdf)\.py)\b",
                      cmd) and not EDITOR_IN_PLACE)
if re.search(ALVO_PROTEGIDO, cmd) and not E_LEITURA:
    nega("Modificar as próprias regras de segurança ou os próprios limites "
         "(settings, hooks, shell rc, arquivos da skill, config.json com os tetos "
         "de taxa) é bloqueado. Quem muda isso é o operador humano, fora da sessão.",
         cmd)

# 8. burlar a guarda de foco/janela exige aval humano
if re.search(r"--anywhere", cmd):
    escala("O comando usa --anywhere, que desliga a guarda de foco e de janela. "
           "Isso permite clicar fora do AnyDesk. Confirme que é intencional.", cmd)

registra("OK", "-", cmd)
sys.exit(0)
