#!/usr/bin/env python3
"""
plataforma.py — o que muda entre macOS e Windows, e só isso.

O `hands.py` guarda as REGRAS: freio de mão, teto de taxa, detector de loop,
guarda de foco, tabela fechada de teclas com lista negra, rastro de auditoria e
contenção do purge. Nada disso depende de sistema operacional, e por isso nada
disso vive aqui — regra de segurança duplicada em dois arquivos é regra que um
dia é corrigida só num deles.

Aqui vive só o que o sistema faz de fato diferente: capturar a tela, medir a
janela, saber quem está em foco, mover o mouse, mandar tecla e restringir a
permissão de um arquivo.

    from plataforma import PLAT
    PLAT.capturar(destino, regiao=(x, y, w, h))

Para teste, o `hands.py` aceita a plataforma injetada — é assim que a suíte de
regras roda num Linux sem tela, cobrindo as duas plataformas.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

WINDOWS = sys.platform.startswith("win")
MAC = sys.platform == "darwin"


class ErroDePlataforma(RuntimeError):
    """Falha que o operador precisa ler, não um traceback."""


# Motivos de recusa, iguais nos dois sistemas — muda a tecla, não a razão.
GRAVA = ("grava, imprime ou apaga no sistema do hospital. Você é somente-leitura "
         "lá dentro (SKILL.md §3.7). Se o caminho que você quer só existe passando "
         "por aqui, pare e pergunte ao usuário.")
ENCERRA = ("encerra o aplicativo ou a sessão. Fechar o AnyDesk derrubaria a "
           "conexão remota e poderia perder o exame aberto. Conexão lenta se "
           "resolve com 'hands.py aguardar', não fechando.")


def _sh(args, check=True):
    try:
        p = subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError:
        raise ErroDePlataforma(f"comando '{args[0]}' não existe nesta máquina.")
    if check and p.returncode != 0:
        raise ErroDePlataforma(
            f"comando falhou: {' '.join(map(str, args))}\n{p.stderr.strip()}")
    return p.stdout.strip()


# --------------------------------------------------------------------- base

class Plataforma:
    nome = "?"
    TECLAS = {}          # tecla aceita -> como a implementação a chama
    MODS = {}            # modificador aceito -> nome interno
    COMBOS_NEGADOS = {}  # (frozenset(mods), tecla) -> motivo
    MOD_MENU = "cmd"     # como o operador escreve o modificador de menu aqui

    def preparar(self):
        """Roda uma vez antes de qualquer uso. Silencioso quando não há o que fazer."""

    def motivo_negado(self, mods, key):
        """Motivo da recusa, ou None. Consulta por VALOR canônico, não por grafia.

        TECLAS e MODS aceitam apelidos de propósito — 'ctrl' e 'control',
        'esc' e 'escape' — e a tabela COMBOS_NEGADOS é escrita com UMA delas.
        Consultar com o texto cru fazia 'control+s' não casar 'ctrl+s': o
        Salvar atravessava a lista negra e chegava ao sistema do hospital.
        Canonizando os dois lados, toda grafia aceita cai na mesma chave."""
        def canon(ms, k):
            return frozenset(self.MODS[m] for m in ms), self.TECLAS[k]
        alvo = canon(mods, key)
        for (mm, kk), motivo in self.COMBOS_NEGADOS.items():
            if canon(mm, kk) == alvo:
                return motivo
        return None

    # olhos
    def capturar(self, destino, regiao=None): raise NotImplementedError
    def redimensionar(self, caminho, lado_maior): raise NotImplementedError
    def tamanho_png(self, caminho): raise NotImplementedError

    # geometria
    def tela_pontos(self): raise NotImplementedError

    def escala(self):
        """Pixels por ponto. None significa 'meça capturando'."""
        raise NotImplementedError

    def janela_do_app(self, app): raise NotImplementedError

    def app_em_foco(self):
        """Nome do app em primeiro plano, ou "" quando não dá para saber.

        O "" é significativo: o hands.py trata foco ilegível como recusa."""
        raise NotImplementedError

    # mãos
    def mouse(self, tipo, x, y): raise NotImplementedError
    def arrastar(self, p1, p2): raise NotImplementedError
    def rolar(self, quantidade): raise NotImplementedError
    def tecla(self, chave, mods): raise NotImplementedError
    def digitar(self, texto): raise NotImplementedError

    # disco
    def restringir(self, caminho): raise NotImplementedError

    def diagnostico(self):
        """{campo: valor} do que o `doctor` mostra e que é específico daqui."""
        return {}


# -------------------------------------------------------------------- macOS

class MacOS(Plataforma):
    nome = "macOS"
    MOD_MENU = "cmd"

    TECLAS = {"enter": 36, "return": 36, "tab": 48, "space": 49, "esc": 53,
              "escape": 53, "delete": 51, "backspace": 51, "left": 123,
              "right": 124, "down": 125, "up": 126, "pageup": 116,
              "pagedown": 121, "home": 115, "end": 119, "f11": 103,
              "a": 0, "c": 8, "f": 3, "z": 6, "v": 9, "x": 7, "w": 13, "q": 12,
              "s": 1, "p": 35, "d": 2, "=": 24, "-": 27, "0": 29,
              "1": 18, "2": 19, "3": 20, "4": 21, "5": 23}
    MODS = {"cmd": "command down", "command": "command down",
            "shift": "shift down", "alt": "option down",
            "option": "option down", "ctrl": "control down",
            "control": "control down"}
    COMBOS_NEGADOS = {
        (frozenset({"cmd"}), "s"): GRAVA,
        (frozenset({"cmd", "shift"}), "s"): GRAVA,
        (frozenset({"cmd"}), "p"): GRAVA,
        (frozenset({"cmd"}), "d"): GRAVA,
        (frozenset({"cmd"}), "x"): GRAVA,
        (frozenset({"cmd"}), "delete"): GRAVA,
        (frozenset({"cmd"}), "backspace"): GRAVA,
        (frozenset({"cmd"}), "q"): ENCERRA,
        (frozenset({"cmd"}), "w"): ENCERRA,
        (frozenset({"cmd", "alt"}), "esc"): ENCERRA,
    }

    def _osa(self, script):
        try:
            r = subprocess.run(["osascript", "-e", script],
                               capture_output=True, text=True)
        except FileNotFoundError:
            return ""
        return r.stdout.strip()

    def capturar(self, destino, regiao=None):
        cmd = ["screencapture", "-x", "-o"]
        if regiao:
            x, y, w, h = regiao
            cmd += ["-R", f"{int(x)},{int(y)},{max(1, int(w))},{max(1, int(h))}"]
        _sh(cmd + [str(destino)])

    def redimensionar(self, caminho, lado_maior):
        _sh(["sips", "-Z", str(lado_maior), str(caminho)], check=False)

    def tamanho_png(self, caminho):
        out = _sh(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(caminho)])
        w = h = None
        for linha in out.splitlines():
            linha = linha.strip()
            if linha.startswith("pixelWidth:"):
                w = int(linha.split(":")[1])
            elif linha.startswith("pixelHeight:"):
                h = int(linha.split(":")[1])
        if not w or not h:
            raise ErroDePlataforma(f"não consegui medir {caminho}")
        return w, h

    def tela_pontos(self):
        out = self._osa('tell application "Finder" to get bounds of window of desktop')
        try:
            _, _, w, h = [int(x.strip()) for x in out.split(",")]
            return w, h
        except Exception:
            raise ErroDePlataforma(
                "não consegui ler o tamanho da tela via AppleScript. "
                "Conceda Automação/Acessibilidade ao app que roda este script.")

    def escala(self):
        return None      # o hands.py mede: pixels da captura / pontos da tela

    def janela_do_app(self, app):
        out = self._osa(f'tell application "System Events" to tell process "{app}" '
                        'to get {position, size} of window 1')
        try:
            nums = [int(float(n.strip())) for n in out.split(",")]
            if len(nums) != 4:
                return None
            return {"x": nums[0], "y": nums[1], "w": nums[2], "h": nums[3]}
        except Exception:
            return None

    def app_em_foco(self):
        return self._osa('tell application "System Events" to get name of first '
                         'application process whose frontmost is true')

    def _motor(self):
        if shutil.which("cliclick"):
            return "cliclick"
        try:
            import pyautogui  # noqa: F401
            return "pyautogui"
        except Exception:
            return None

    def mouse(self, tipo, x, y):
        eng = self._motor()
        if eng == "cliclick":
            verbo = {"click": "c", "dblclick": "dc", "rclick": "rc", "move": "m"}[tipo]
            _sh(["cliclick", f"{verbo}:{int(x)},{int(y)}"])
        elif eng == "pyautogui":
            import pyautogui
            pyautogui.FAILSAFE = True
            {"move": lambda: pyautogui.moveTo(int(x), int(y), duration=0.12),
             "click": lambda: pyautogui.click(int(x), int(y)),
             "dblclick": lambda: pyautogui.doubleClick(int(x), int(y)),
             "rclick": lambda: pyautogui.rightClick(int(x), int(y))}[tipo]()
        else:
            raise ErroDePlataforma(
                "nenhum motor de clique. Rode scripts/setup.sh ou 'brew install cliclick'.")

    def arrastar(self, p1, p2):
        eng = self._motor()
        if eng == "cliclick":
            _sh(["cliclick", f"dd:{int(p1[0])},{int(p1[1])}",
                 f"du:{int(p2[0])},{int(p2[1])}"])
        elif eng == "pyautogui":
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.moveTo(int(p1[0]), int(p1[1]))
            pyautogui.dragTo(int(p2[0]), int(p2[1]), duration=0.35, button="left")
        else:
            raise ErroDePlataforma("nenhum motor de clique disponível.")

    def rolar(self, quantidade):
        eng = self._motor()
        if eng == "cliclick":
            direcao = "d" if quantidade < 0 else "u"
            _sh(["cliclick", f"w:{direcao},{abs(int(quantidade))}"], check=False)
        elif eng == "pyautogui":
            import pyautogui
            pyautogui.scroll(int(quantidade))
        else:
            raise ErroDePlataforma("nenhum motor de clique disponível.")

    def tecla(self, chave, mods):
        usando = (" using {%s}" % ", ".join(self.MODS[m] for m in mods)) if mods else ""
        self._osa('tell application "System Events" to key code '
                  f'{self.TECLAS[chave]}{usando}')

    def digitar(self, texto):
        esc = texto.replace("\\", "\\\\").replace('"', '\\"')
        self._osa(f'tell application "System Events" to keystroke "{esc}"')

    def restringir(self, caminho):
        try:
            os.chmod(caminho, 0o700 if Path(caminho).is_dir() else 0o600)
        except Exception:
            pass

    def diagnostico(self):
        return {"screencapture": bool(shutil.which("screencapture")),
                "sips": bool(shutil.which("sips")),
                "motor_de_clique": self._motor() or "AUSENTE"}


# ------------------------------------------------------------------ Windows

class Windows(Plataforma):
    nome = "Windows"
    MOD_MENU = "ctrl"

    # pyautogui entende estes nomes direto — não há tabela de virtual key code
    # para manter em sincronia.
    # Apelido -> nome canônico do pyautogui. Os apelidos ('return', 'escape')
    # colapsam no mesmo valor DE PROPÓSITO: é esse valor que motivo_negado()
    # compara, e sem o colapso 'ctrl+shift+escape' escapava da recusa escrita
    # como 'ctrl+shift+esc'.
    TECLAS = dict({k: k for k in (
        "enter", "tab", "space", "esc", "delete",
        "backspace", "left", "right", "down", "up", "pageup", "pagedown",
        "home", "end", "f4", "f5", "f11",
        "a", "c", "f", "z", "v", "x", "w", "s", "p", "d",
        "0", "1", "2", "3", "4", "5", "=", "-")},
        **{"return": "enter", "escape": "esc"})
    MODS = {"ctrl": "ctrl", "control": "ctrl", "shift": "shift",
            "alt": "alt", "win": "win"}
    COMBOS_NEGADOS = {
        (frozenset({"ctrl"}), "s"): GRAVA,              # salvar
        (frozenset({"ctrl", "shift"}), "s"): GRAVA,     # salvar como
        (frozenset({"ctrl"}), "p"): GRAVA,              # imprimir
        (frozenset({"ctrl"}), "x"): GRAVA,              # recortar
        (frozenset({"ctrl"}), "d"): GRAVA,              # excluir/duplicar
        # No Windows, Delete sozinho apaga o item selecionado de uma lista. Para
        # corrigir texto digitado existe backspace, que continua permitida.
        (frozenset(), "delete"): GRAVA,
        (frozenset({"shift"}), "delete"): GRAVA,        # apaga sem passar pela lixeira
        (frozenset({"ctrl"}), "w"): ENCERRA,
        (frozenset({"alt"}), "f4"): ENCERRA,
        (frozenset({"ctrl", "shift"}), "esc"): ENCERRA,  # gerenciador de tarefas
        (frozenset({"ctrl", "alt"}), "delete"): ENCERRA,
    }

    def preparar(self):
        """Declara consciência de DPI por monitor.

        Sem isto o Windows MENTE sobre coordenadas em tela com escala != 100%:
        o processo enxerga uma resolução virtual e o clique cai deslocado. É a
        causa número um de clique no lugar errado nesta plataforma, e o modo de
        falha é justamente o que a guarda de retângulo não pega — o clique
        continua dentro da janela do AnyDesk, só que no elemento vizinho.

        Declarada a consciência, o processo trabalha em pixels físicos e a
        conversão de escala deixa de existir: escala() devolve 1.0."""
        import ctypes
        for tentativa in (
                lambda: ctypes.windll.user32.SetProcessDpiAwarenessContext(-4),
                lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
                lambda: ctypes.windll.user32.SetProcessDPIAware()):
            try:
                tentativa()
                return
            except Exception:
                continue

    def capturar(self, destino, regiao=None):
        try:
            from PIL import ImageGrab
        except ImportError:
            raise ErroDePlataforma("pillow não está instalado. Rode scripts/setup.ps1.")
        if regiao:
            x, y, w, h = [int(v) for v in regiao]
            im = ImageGrab.grab(bbox=(x, y, x + max(1, w), y + max(1, h)),
                                all_screens=True)
        else:
            im = ImageGrab.grab(all_screens=True)
        im.save(str(destino))

    def redimensionar(self, caminho, lado_maior):
        from PIL import Image
        with Image.open(str(caminho)) as im:
            if max(im.size) <= lado_maior:
                return
            f = lado_maior / max(im.size)
            novo = (max(1, int(im.width * f)), max(1, int(im.height * f)))
            im.resize(novo, Image.LANCZOS).save(str(caminho))

    def tamanho_png(self, caminho):
        from PIL import Image
        with Image.open(str(caminho)) as im:
            return im.size

    def tela_pontos(self):
        import ctypes
        u = ctypes.windll.user32
        w, h = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
        if not w or not h:
            raise ErroDePlataforma("não consegui ler o tamanho da tela.")
        return w, h

    def escala(self):
        return 1.0       # consciência de DPI declarada em preparar()

    @staticmethod
    def _nome_do_processo(pid):
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)   # QUERY_LIMITED_INFORMATION
        if not h:
            return ""
        try:
            tam = wintypes.DWORD(260)
            buf = ctypes.create_unicode_buffer(tam.value)
            if k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(tam)):
                return os.path.basename(buf.value)
            return ""
        finally:
            k.CloseHandle(h)

    def janela_do_app(self, app):
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        alvo = app.lower().removesuffix(".exe")
        achadas = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def visita(hwnd, _):
            if not u.IsWindowVisible(hwnd):
                return True
            pid = wintypes.DWORD()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            nome = self._nome_do_processo(pid.value)
            if nome and nome.lower().removesuffix(".exe") == alvo:
                n = u.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(n + 1)
                u.GetWindowTextW(hwnd, buf, n + 1)
                if buf.value.strip():
                    achadas.append(hwnd)
            return True

        u.EnumWindows(visita, 0)
        if not achadas:
            return None
        r = wintypes.RECT()
        if not u.GetWindowRect(achadas[0], ctypes.byref(r)):
            return None
        return {"x": r.left, "y": r.top,
                "w": r.right - r.left, "h": r.bottom - r.top}

    def app_em_foco(self):
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return ""
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return self._nome_do_processo(pid.value).removesuffix(".exe")

    def _pyautogui(self):
        try:
            import pyautogui
        except Exception:
            raise ErroDePlataforma(
                "pyautogui não está instalado. Rode scripts/setup.ps1.")
        pyautogui.FAILSAFE = True
        return pyautogui

    def mouse(self, tipo, x, y):
        p = self._pyautogui()
        {"move": lambda: p.moveTo(int(x), int(y), duration=0.12),
         "click": lambda: p.click(int(x), int(y)),
         "dblclick": lambda: p.doubleClick(int(x), int(y)),
         "rclick": lambda: p.rightClick(int(x), int(y))}[tipo]()

    def arrastar(self, p1, p2):
        p = self._pyautogui()
        p.moveTo(int(p1[0]), int(p1[1]))
        p.dragTo(int(p2[0]), int(p2[1]), duration=0.35, button="left")

    def rolar(self, quantidade):
        self._pyautogui().scroll(int(quantidade))

    def tecla(self, chave, mods):
        p = self._pyautogui()
        nome = self.TECLAS[chave]
        if mods:
            p.hotkey(*[self.MODS[m] for m in mods], nome)
        else:
            p.press(nome)

    def digitar(self, texto):
        # write() não dá conta de acento fora do layout, e a área de transferência
        # seria mais um lugar com nome de paciente. typewrite com intervalo é o
        # que sobra, e o teto de 200 caracteres do hands.py mantém isso curto.
        self._pyautogui().typewrite(texto, interval=0.02)

    def restringir(self, caminho):
        """ACL, não chmod.

        os.chmod no Windows só mexe no bit de somente-leitura: NÃO restringe
        outro usuário nenhum. O rastro tem nome de paciente e precisa de ACL."""
        usuario = os.environ.get("USERNAME") or ""
        if not usuario:
            return
        try:
            _sh(["icacls", str(caminho), "/inheritance:r",
                 "/grant:r", f"{usuario}:(OI)(CI)F"], check=False)
        except Exception:
            pass

    def diagnostico(self):
        d = {}
        try:
            from PIL import Image  # noqa: F401
            d["pillow"] = True
        except Exception:
            d["pillow"] = False
        try:
            import pyautogui  # noqa: F401
            d["motor_de_clique"] = "pyautogui"
        except Exception:
            d["motor_de_clique"] = "AUSENTE"
        return d


def detecta():
    if WINDOWS:
        return Windows()
    if MAC:
        return MacOS()
    raise ErroDePlataforma(
        f"sistema não suportado: {sys.platform}. "
        "Esta skill roda em macOS ou Windows.")


try:
    PLAT = detecta()
except ErroDePlataforma:
    PLAT = None      # o hands.py reclama com mensagem própria no doctor
