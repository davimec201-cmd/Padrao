#!/usr/bin/env bash
# setup.sh — instala as dependências da skill laudos-oct no macOS.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "==> Skill em: $SKILL_DIR"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "!! Este setup é para macOS. Detectado: $(uname)"; exit 1
fi

command -v python3 >/dev/null || { echo "!! python3 não encontrado. Instale com: xcode-select --install"; exit 1; }
echo "==> Python: $(python3 -V)"

echo "==> Instalando dependências Python..."
if ! python3 -m pip install --user -r "$SKILL_DIR/scripts/requirements.txt" 2>/dev/null; then
  echo "   (retentando com --break-system-packages)"
  python3 -m pip install --user --break-system-packages -r "$SKILL_DIR/scripts/requirements.txt" || {
    echo "!! Falha ao instalar. Tente:  python3 -m pip install --user --break-system-packages pyautogui pillow reportlab pyobjc-core pyobjc-framework-Quartz"
    exit 1; }
fi

if command -v brew >/dev/null && ! command -v cliclick >/dev/null; then
  echo "==> Homebrew presente. Instalando cliclick (motor de clique mais leve)..."
  brew install cliclick || echo "   (cliclick opcional — pyautogui já serve)"
fi

mkdir -p "$HOME/Laudos_OCT"
echo "==> Pasta de saída: $HOME/Laudos_OCT"

cat <<'PERM'

=====================================================================
 PERMISSÕES DO macOS — faça isto agora, senão nada funciona
=====================================================================
 Abra: Ajustes do Sistema  ->  Privacidade e Segurança

 1) Gravação de Tela        -> ligue para o app que roda o Claude Code
                               (Terminal, iTerm ou Claude)
 2) Acessibilidade          -> ligue para o mesmo app
 3) Automação               -> permita "System Events" e "Finder"
                               para o mesmo app

 Feche e reabra o app depois de conceder. O macOS só aplica na
 reabertura.
=====================================================================

PERM

echo "==> Rodando diagnóstico..."
python3 "$SKILL_DIR/scripts/hands.py" doctor || {
  echo ""
  echo "!! O diagnóstico apontou pendências acima. Resolva-as e rode de novo:"
  echo "   python3 $SKILL_DIR/scripts/hands.py doctor"
  exit 1
}
echo ""
echo "==> Tudo pronto. Abra o AnyDesk, deixe a janela visível e peça ao Claude:"
echo "    \"lauda os OCTs da fila do AnyDesk\""
