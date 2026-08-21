#!/usr/bin/env python3
"""
teste_regras.py — exercita as regras de segurança do hands.py sem tela.

A camada de plataforma é injetada por uma falsa, que só anota o que teria feito.
Assim as regras — lista negra de teclas, guarda de foco, guarda de retângulo,
freio de mão, contenção do purge, rastro de auditoria — rodam em qualquer
máquina, e rodam para AS DUAS plataformas reais.

O que este arquivo NÃO cobre, e nenhum teste sem a máquina da clínica cobre:
se o clique cai no pixel certo, se a captura enxerga a janela do AnyDesk, e se
a consciência de DPI foi aceita pelo Windows. Isso é o dia 1 na estação.

    python3 scripts/teste_regras.py
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import plataforma as _plat            # noqa: E402

OK = FALHA = 0


class PlataformaFalsa(_plat.Plataforma):
    """Anota em vez de agir. `foco` é o que o teste quer em primeiro plano."""

    def __init__(self, base, foco="AnyDesk"):
        self.nome = "Falsa/" + base.nome
        self.TECLAS, self.MODS = base.TECLAS, base.MODS
        self.COMBOS_NEGADOS, self.MOD_MENU = base.COMBOS_NEGADOS, base.MOD_MENU
        self.foco, self.feitos = foco, []

    def preparar(self): self.feitos.append(("preparar",))

    def capturar(self, destino, regiao=None):
        Path(destino).write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
        self.feitos.append(("capturar", regiao))

    def redimensionar(self, caminho, lado_maior):
        self.feitos.append(("redimensionar", lado_maior))

    def tamanho_png(self, caminho): return (1600, 1000)
    def tela_pontos(self): return (1600, 1000)
    def escala(self): return 1.0
    def janela_do_app(self, app): return {"x": 0, "y": 0, "w": 1600, "h": 1000}
    def app_em_foco(self): return self.foco
    def mouse(self, tipo, x, y): self.feitos.append((tipo, int(x), int(y)))
    def arrastar(self, p1, p2): self.feitos.append(("arrastar", p1, p2))
    def rolar(self, q): self.feitos.append(("rolar", q))
    def tecla(self, chave, mods): self.feitos.append(("tecla", chave, tuple(sorted(mods))))
    def digitar(self, texto): self.feitos.append(("digitar", len(texto)))
    def restringir(self, caminho): pass


def carrega_hands(plataforma, casa):
    spec = importlib.util.spec_from_file_location("hands", AQUI / "hands.py")
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    h.PLAT = plataforma
    h.HOME = casa
    h.CONFIG_DIR = casa / ".laudos_oct"
    h.CONFIG_FILE = h.CONFIG_DIR / "config.json"
    h.OUT_ROOT = casa / "Laudos_OCT"
    h.STOP_FILE = h.OUT_ROOT / "STOP"
    (h.OUT_ROOT / "shots").mkdir(parents=True, exist_ok=True)
    return h


class Args:
    def __init__(self, **kw): self.__dict__.update(kw)


def checa(nome, esperado, fn):
    """esperado: 'passa' | 'recusa'."""
    global OK, FALHA
    try:
        fn()
        obtido = "passa"
    except SystemExit:
        obtido = "recusa"
    if obtido == esperado:
        OK += 1
        print(f"  \033[32mok\033[0m   {nome}")
    else:
        FALHA += 1
        print(f"  \033[31mFALHA\033[0m {nome}: esperado {esperado}, obtido {obtido}")


def afirma(nome, cond, detalhe=""):
    global OK, FALHA
    if cond:
        OK += 1
        print(f"  \033[32mok\033[0m   {nome}")
    else:
        FALHA += 1
        print(f"  \033[31mFALHA\033[0m {nome}" + (f" — {detalhe}" if detalhe else ""))


def roda_para(base):
    print(f"\n── {base.nome} ──")
    casa = Path(tempfile.mkdtemp())
    fake = PlataformaFalsa(base)
    h = carrega_hands(fake, casa)
    h.save_config({"allowed_apps": ["AnyDesk"],
                   "guard_rect_pt": {"x": 0, "y": 0, "w": 1600, "h": 1000}})
    mm = base.MOD_MENU

    def tecla(combo, foco="AnyDesk"):
        fake.foco = foco
        return lambda: h.cmd_key(Args(combo=combo))

    def clique(x, y, foco="AnyDesk", anywhere=False):
        fake.foco = foco
        return lambda: h.cmd_mouse(
            Args(x=x, y=y, frm=None, anywhere=anywhere, dry_run=False), "click")

    print("  · teclado: tabela fechada e lista negra")
    checa("tecla legítima (enter) passa", "passa", tecla("enter"))
    checa(f"atalho de leitura ({mm}+c) passa", "passa", tecla(f"{mm}+c"))
    checa(f"gravar ({mm}+s) é recusado", "recusa", tecla(f"{mm}+s"))
    checa(f"imprimir ({mm}+p) é recusado", "recusa", tecla(f"{mm}+p"))
    checa(f"recortar ({mm}+x) é recusado", "recusa", tecla(f"{mm}+x"))
    encerra = "cmd+q" if mm == "cmd" else "alt+f4"
    checa(f"encerrar o app ({encerra}) é recusado", "recusa", tecla(encerra))
    checa("injeção de AppleScript é recusada", "recusa",
          tecla('a" & (do shell script "id") & "'))
    checa("tecla fora da tabela é recusada", "recusa", tecla("f13"))
    checa("modificador desconhecido é recusado", "recusa", tecla("hyper+s"))
    if mm == "ctrl":
        checa("Delete sozinho é recusado (apaga item da lista)", "recusa", tecla("delete"))
        checa("backspace continua permitida (corrigir texto)", "passa", tecla("backspace"))

    print("  · guarda de foco")
    checa("foco em outro app recusa a tecla", "recusa", tecla("enter", "Mail"))
    checa("foco ILEGÍVEL recusa a tecla", "recusa", tecla("enter", ""))
    checa("foco em outro app recusa o clique", "recusa", clique(800, 500, "Finder"))
    checa("foco ILEGÍVEL recusa o clique", "recusa", clique(800, 500, ""))

    print("  · guarda de retângulo")
    checa("clique dentro da área passa", "passa", clique(800, 500))
    checa("clique fora do retângulo é recusado", "recusa", clique(5000, 5000))

    print("  · digitação")
    fake.foco = "AnyDesk"
    checa("digitação normal passa", "passa",
          lambda: h.cmd_type(Args(text="Fulana de Tal", anywhere=False)))
    checa("acima de 200 caracteres é recusada", "recusa",
          lambda: h.cmd_type(Args(text="x" * 201, anywhere=False)))
    rastro = (casa / ".laudos_oct" / "acoes.jsonl").read_text(encoding="utf-8")
    afirma("nome digitado NÃO aparece em acoes.jsonl", "Fulana de Tal" not in rastro)

    print("  · rastro de auditoria")
    fake.foco = "AnyDesk"
    h.cmd_scroll(Args(amount=-6, x=None, y=None, frm=None, anywhere=False, dry_run=False))
    h.cmd_drag(Args(x1=10, y1=10, x2=90, y2=90, frm=None, anywhere=False))
    tipos = [json.loads(l).get("tipo")
             for l in (casa / ".laudos_oct" / "acoes.jsonl").read_text().splitlines()]
    for t in ("click", "key", "type", "scroll", "drag"):
        afirma(f"'{t}' entra no rastro", t in tipos)

    print("  · freio de mão")
    h.STOP_FILE.write_text("parar")
    checa("STOP bloqueia a tecla", "recusa", tecla("enter"))
    checa("STOP bloqueia o clique", "recusa", clique(800, 500))
    h.STOP_FILE.unlink()

    print("  · contenção do purge")
    fora = casa / "Documentos"; fora.mkdir(); (fora / "particular.png").write_bytes(b"x")
    checa("purge fora de Laudos_OCT é recusado", "recusa",
          lambda: h.cmd_purge(Args(dir=str(fora), dias=0)))
    afirma("o arquivo de fora continua lá", (fora / "particular.png").exists())
    checa("purge dentro de Laudos_OCT passa", "passa",
          lambda: h.cmd_purge(Args(dir=None, dias=0)))


def main():
    for base in (_plat.MacOS(), _plat.Windows()):
        roda_para(base)
    print(f"\n{OK} passaram, {FALHA} falharam")
    return 1 if FALHA else 0


if __name__ == "__main__":
    sys.exit(main())
