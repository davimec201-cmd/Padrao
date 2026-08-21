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

    print("  · lista negra: TODAS as grafias aceitas, não só a canônica")
    # MODS e TECLAS aceitam apelido ('ctrl'/'control', 'esc'/'escape'), e a
    # tabela é escrita com um só. Sem canonizar, 'control+s' não casava 'ctrl+s'
    # e o Salvar chegava ao sistema do hospital — com a suíte verde, porque ela
    # só testava a grafia canônica. Aqui cada combo negado é exercitado em TODAS
    # as escritas que a plataforma aceita.
    apelidos_mod = {}
    for escrito, valor in base.MODS.items():
        apelidos_mod.setdefault(valor, []).append(escrito)
    apelidos_key = {}
    for escrito, valor in base.TECLAS.items():
        apelidos_key.setdefault(valor, []).append(escrito)

    import itertools
    variantes = 0
    for (mods, key) in base.COMBOS_NEGADOS:
        listas = [apelidos_mod[base.MODS[m]] for m in sorted(mods)]
        for combo_mods in itertools.product(*listas) if listas else [()]:
            for k in apelidos_key[base.TECLAS[key]]:
                escrita = "+".join(list(combo_mods) + [k])
                variantes += 1
                checa(f"{escrita} é recusado", "recusa", tecla(escrita))
    afirma(f"{variantes} grafias cobertas ({len(base.COMBOS_NEGADOS)} combos)",
           variantes >= len(base.COMBOS_NEGADOS))

    print("  · abreviação de flag não desliga a guarda")
    # argparse aceita prefixo não ambíguo por padrão: '--any' virava '--anywhere'
    # e desligava foco e retângulo sem casar a regra do guardião.
    import contextlib, io

    def pela_cli(*argv):
        """Roda o CLI de verdade e diz se algo chegou à plataforma.

        `preparar` não conta: main() sempre chama, e é declaração de DPI, não
        ação de tela."""
        fake.foco = "Finder"
        antes = [f for f in fake.feitos if f[0] != "preparar"]
        antes = len(antes)
        try:
            with contextlib.redirect_stderr(io.StringIO()), \
                 contextlib.redirect_stdout(io.StringIO()):
                h.main(list(argv))
            saiu = "passou"
        except SystemExit as e:
            saiu = "recusa" if e.code else "passou"
        agora = len([f for f in fake.feitos if f[0] != "preparar"])
        return saiu, agora - antes

    for escrita in ("--any", "--anywh"):
        saiu, novas = pela_cli("click", escrita, "5000", "5000")
        afirma(f"click {escrita} 5000 5000 é recusado pelo parser",
               saiu == "recusa" and novas == 0, f"saiu={saiu}, ações={novas}")

    print("  · --anywhere exige autorização do operador")
    # A flag desliga foco e retângulo. O hook 'ask' era o único portão, e o hook
    # é passo de instalação separado — INSTALACAO.md admite que dá para pular.
    bilhete = h.CONFIG_DIR / h.PERMISSAO_ANYWHERE
    bilhete.unlink(missing_ok=True)
    h._anywhere_consumido = False
    saiu, novas = pela_cli("click", "--anywhere", "5000", "5000")
    afirma("sem autorização, --anywhere não clica",
           saiu == "recusa" and novas == 0, f"saiu={saiu}, ações={novas}")

    bilhete.write_text("liberado pelo operador")
    h._anywhere_consumido = False
    saiu, novas = pela_cli("click", "--anywhere", "5000", "5000")
    afirma("com autorização, --anywhere clica", saiu == "passou" and novas == 1,
           f"saiu={saiu}, ações={novas}")
    afirma("e a autorização é CONSUMIDA (vale um comando só)", not bilhete.exists())

    h._anywhere_consumido = False
    saiu, novas = pela_cli("click", "--anywhere", "5000", "5000")
    afirma("o segundo --anywhere já é recusado",
           saiu == "recusa" and novas == 0, f"saiu={saiu}, ações={novas}")

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

    print("  · sidecar de outro paciente")
    shots = h.OUT_ROOT / "shots"
    (shots / "pacienteA").mkdir(parents=True, exist_ok=True)
    lado = {"origin_pt": {"x": 2000, "y": 1500}, "px_per_pt": 1.0}
    (shots / "nav01.json").write_text(json.dumps(lado))
    fake.foco = "AnyDesk"
    antes = len(fake.feitos)
    checa("--from de paciente inexistente NÃO cai no sidecar de outro", "recusa",
          lambda: h.cmd_mouse(Args(x=10, y=10, frm="shots/pacienteB/nav01.json",
                                   anywhere=False, dry_run=False), "click"))
    afirma("e nenhum clique saiu", len(fake.feitos) == antes)

    print("  · rastro de auditoria ingravável")
    # Com o rastro inutilizável, limites() perdia o teto de taxa e o detector de
    # loop junto — e nada recusava nada. A PRIMEIRA ação já tem de parar.
    rastro = h.CONFIG_DIR / "acoes.jsonl"
    rastro.unlink(missing_ok=True)
    rastro.mkdir()                    # diretório no lugar do arquivo: ingravável
    fake.foco = "AnyDesk"
    antes = len(fake.feitos)
    checa("rastro ingravável recusa a PRIMEIRA ação", "recusa", clique(800, 500))
    afirma("e nada chegou à plataforma", len(fake.feitos) == antes)
    rastro.rmdir()

    print("  · contenção do purge")
    fora = casa / "Documentos"; fora.mkdir(); (fora / "particular.png").write_bytes(b"x")
    checa("purge fora de Laudos_OCT é recusado", "recusa",
          lambda: h.cmd_purge(Args(dir=str(fora), dias=0)))
    afirma("o arquivo de fora continua lá", (fora / "particular.png").exists())
    checa("purge dentro de Laudos_OCT passa", "passa",
          lambda: h.cmd_purge(Args(dir=None, dias=0)))


def doctor_com_perfil(base):
    """O perfil OFICIAL da plataforma tem de dar PRONTO, e NAO_PRONTO tem de dizer
    o que falta.

    Duas coisas travavam o Windows para sempre com o endurecimento correto: a
    exigência da string `"sandbox"`, que o perfil do Windows não tem por decisão
    declarada, e a checagem de `motor_de_clique`, que é diagnóstico só do macOS e
    devolvia None aqui — esta última sem NENHUMA linha do relatório dizendo por
    quê. SKILL.md manda parar e mostrar o que falta; não havia o que mostrar."""
    import contextlib, io, shutil
    perfil = "settings-macos.json" if base.nome == "macOS" else "settings-windows.json"
    casa = Path(tempfile.mkdtemp())
    (casa / ".claude" / "hooks").mkdir(parents=True)
    raiz = AQUI.parent / "hardening"
    shutil.copy(raiz / "hooks" / "guardiao-laudos.py",
                casa / ".claude" / "hooks" / "guardiao-laudos.py")
    shutil.copy(raiz / perfil, casa / ".claude" / "settings.json")
    fake = PlataformaFalsa(base)
    h = carrega_hands(fake, casa)
    h.save_config({"allowed_apps": ["AnyDesk"],
                   "guard_rect_pt": {"x": 0, "y": 0, "w": 1600, "h": 1000}})

    def diagnostico():
        saida = io.StringIO()
        try:
            with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
                h.main(["doctor"])
        except SystemExit:
            pass
        return json.loads(saida.getvalue())

    print(f"\n── doctor com {perfil} ──")
    rep = diagnostico()
    afirma(f"{perfil} instalado dá PRONTO", rep["VEREDITO"] == "PRONTO",
           f"{rep['VEREDITO']} · falta={rep.get('FALTA')}")
    afirma("settings_endurecido diz ok", rep["settings_endurecido"] == "ok",
           str(rep["settings_endurecido"]))
    if base.nome != "macOS":
        afirma("e o relatório explica que não há sandbox de kernel aqui",
               "sandbox_de_kernel" in rep)

    h.STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    h.STOP_FILE.write_text("parar")
    rep = diagnostico()
    afirma("com STOP, o veredito cai", rep["VEREDITO"] == "NAO_PRONTO")
    afirma("e NAO_PRONTO SEMPRE diz o que falta", bool(rep.get("FALTA")),
           "veredito negativo sem lista de faltas é o que SKILL.md proíbe")
    h.STOP_FILE.unlink()


def main():
    for base in (_plat.MacOS(), _plat.Windows()):
        roda_para(base)
        doctor_com_perfil(base)
    print(f"\n{OK} passaram, {FALHA} falharam")
    return 1 if FALHA else 0


if __name__ == "__main__":
    sys.exit(main())
