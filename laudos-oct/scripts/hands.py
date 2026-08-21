#!/usr/bin/env python3
"""
hands.py — mãos e olhos do agente de laudos de OCT.

Roda em macOS e em Windows. O que muda entre os dois vive em `plataforma.py`;
aqui ficam as regras, que são as mesmas nos dois: freio de mão, teto de taxa,
detector de loop, guarda de foco e de retângulo, tabela fechada de teclas com
lista negra de gravação, rastro de auditoria e contenção do purge.

Olho:  captura nativa da plataforma  ->  PNG + sidecar .json com a transformação
Mão:   plataforma.py                 ->  clique / digitação / scroll
Freio: arquivo STOP + guarda de app em foco + guarda de retângulo

Coordenadas: você lê pixels da IMAGEM e passa --from <sidecar.json>.
O script converte para pontos de tela. Nunca faça essa conta na mão.

    python3 hands.py doctor
    python3 hands.py shot --full --out shots/nav01.png
    python3 hands.py shot --roi 980,410,620,300 --from shots/nav01.json --out shots/roi01.png
    python3 hands.py click --from shots/nav01.json 812 430
    python3 hands.py type "Maria da Silva"
    python3 hands.py key cmd+s
"""

import argparse, hashlib, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plataforma as _plat

# Trocável em teste: a suíte injeta uma plataforma falsa para exercitar as
# regras de segurança num Linux sem tela.
PLAT = _plat.PLAT

HOME = Path.home()
CONFIG_DIR = HOME / ".laudos_oct"
CONFIG_FILE = CONFIG_DIR / "config.json"
OUT_ROOT = HOME / "Laudos_OCT"
STOP_FILE = OUT_ROOT / "STOP"
TARGET_APP = "AnyDesk"
NAV_MAX_EDGE = 1100   # navegação: ~1010 tokens/print (1400px custava ~1630)
ROI_MAX_EDGE = 1500   # recorte: resolução alta o suficiente para ler dígito
MAX_POR_MIN = 40      # teto de ações por minuto
MAX_POR_HORA = 600    # teto de ações por hora
LOOP_N = 3            # N ações idênticas seguidas...
LOOP_JANELA = 30      # ...dentro de N segundos = loop travado


# ----------------------------------------------------------------- utilidades

def die(msg, code=2):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(code)


def _foco_ilegivel():
    if PLAT is not None and PLAT.nome == "macOS":
        return "ILEGÍVEL — falta permissão de Automação"
    return "ILEGÍVEL — não consegui ler o app em primeiro plano"


def plat():
    """A plataforma, ou uma parada com mensagem que o operador entende."""
    if PLAT is None:
        die(f"sistema não suportado: {sys.platform}. "
            "Esta skill roda em macOS ou Windows.")
    return PLAT


def _p(fn, *a, **kw):
    """Chama a plataforma convertendo a falha dela em parada limpa."""
    try:
        return fn(*a, **kw)
    except _plat.ErroDePlataforma as e:
        die(str(e))


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _restringe(CONFIG_DIR)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    _restringe(CONFIG_FILE)


def check_stop():
    if STOP_FILE.exists():
        die("STOP ativo — freio de mão acionado. "
            f"Remova {STOP_FILE} para liberar.", 3)



# --------------------------------------------------- auditoria e limite de taxa

def audit_path():
    return CONFIG_DIR / "acoes.jsonl"


def _restringe(caminho):
    """Legível só pelo usuário corrente. O rastro contém nome de paciente.

    No macOS é chmod; no Windows é ACL — lá o chmod só mexe no bit de
    somente-leitura e não restringe outro usuário nenhum."""
    try:
        if PLAT is not None:
            PLAT.restringir(caminho)
    except Exception:
        pass


def audit(evento, **campos):
    """Rastro append-only de tudo que tocou a tela. Nunca falha silenciosamente."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _restringe(CONFIG_DIR)
    linha = {"ts": time.time(), "iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "evento": evento}
    linha.update(campos)
    try:
        novo = not audit_path().exists()
        with audit_path().open("a") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
        if novo:
            _restringe(audit_path())
    except Exception as e:
        print(f"AVISO: não consegui gravar auditoria: {e}", file=sys.stderr)


def audit_recentes(segundos):
    p = audit_path()
    if not p.exists():
        return []
    corte = time.time() - segundos
    out = []
    try:
        for ln in p.read_text().splitlines()[-4000:]:
            try:
                d = json.loads(ln)
            except Exception:
                continue
            if d.get("evento") == "acao" and d.get("ts", 0) >= corte:
                out.append(d)
    except Exception:
        pass
    return out


def limites(assinatura):
    """Teto de taxa + detector de loop travado. Recusa antes de agir."""
    cfg = load_config()
    # min(): o config pode APERTAR o teto, nunca afrouxar. Sem isso, o próprio
    # agente poderia reescrever config.json e desligar o limitador.
    por_min = min(int(cfg.get("max_por_min", MAX_POR_MIN)), MAX_POR_MIN)
    por_hora = min(int(cfg.get("max_por_hora", MAX_POR_HORA)), MAX_POR_HORA)

    ult_min = audit_recentes(60)
    if len(ult_min) >= por_min:
        audit("recusa", motivo="teto_por_minuto", n=len(ult_min))
        die(f"teto de taxa: {len(ult_min)} ações no último minuto (limite {por_min}). "
            "Isso normalmente indica loop. Pare, tire um shot --full e reavalie.", 5)

    ult_hora = audit_recentes(3600)
    if len(ult_hora) >= por_hora:
        audit("recusa", motivo="teto_por_hora", n=len(ult_hora))
        die(f"teto de taxa: {len(ult_hora)} ações na última hora (limite {por_hora}). "
            "Chame o operador humano.", 5)

    janela = [d for d in audit_recentes(LOOP_JANELA) if d.get("assinatura") == assinatura]
    if len(janela) >= LOOP_N:
        audit("recusa", motivo="loop_travado", assinatura=assinatura, n=len(janela))
        die(f"loop travado: '{assinatura}' repetida {len(janela)}x em {LOOP_JANELA}s. "
            "A tela não está respondendo como você espera. Pare e reavalie — "
            "não insista na mesma coordenada.", 5)


# ------------------------------------------------------------------ geometria

def screen_points():
    """Tamanho da tela principal em PONTOS lógicos."""
    return _p(plat().tela_pontos)


def png_size(path):
    """Dimensões em PIXELS."""
    return _p(plat().tamanho_png, path)


def _tmp_png(nome):
    """Temporário DENTRO de ~/.laudos_oct, nunca em /tmp.

    Captura de tela é prontuário: /tmp é 1777 e o nome fixo era previsível. E
    ~/.laudos_oct é um dos dois caminhos que o sandbox declara graváveis — /tmp
    não era declarado a lugar nenhum."""
    d = CONFIG_DIR / "tmp"
    d.mkdir(parents=True, exist_ok=True)
    _restringe(CONFIG_DIR); _restringe(d)
    return d / f"{nome}_{os.getpid()}.png"


def detect_scale():
    """Fator Retina: pixels por ponto.

    O valor é cacheado por GEOMETRIA de tela, não globalmente: trocar de monitor
    ou mudar a escala do display invalidava silenciosamente toda conversão de
    coordenada, e o clique ia para o elemento vizinho dentro da janela — que a
    guarda de retângulo não pega."""
    fixa = plat().escala()
    if fixa is not None:
        return float(fixa)               # Windows: consciência de DPI declarada

    cfg = load_config()
    pt_w, pt_h = screen_points()
    marca = f"{pt_w}x{pt_h}"
    if cfg.get("scale") and cfg.get("scale_tela") == marca:
        return float(cfg["scale"])

    tmp = _tmp_png("scale")
    try:
        _p(plat().capturar, tmp)
        px_w, _ = png_size(tmp)
    finally:
        tmp.unlink(missing_ok=True)      # some no caminho de erro também
    scale = round(px_w / pt_w, 4) if pt_w else 1.0
    cfg["scale"], cfg["scale_tela"] = scale, marca
    save_config(cfg)
    return scale


def app_window(app=TARGET_APP):
    """{x,y,w,h} da janela do app, em pontos. None se não achar."""
    try:
        return plat().janela_do_app(app)
    except Exception:
        return None


def frontmost_app():
    """Nome do app em foco, ou "" quando não dá para saber.

    O "" é tratado como recusa em toda guarda: sem saber quem está na frente,
    não há o que proteger."""
    try:
        return plat().app_em_foco() or ""
    except Exception:
        return ""


# ------------------------------------------------------------------- sidecars

def write_sidecar(png, kind, origin_pt, region_pt, scale):
    px_w, px_h = png_size(png)
    data = {
        "shot": str(png),
        "kind": kind,
        "scale_retina": scale,
        "origin_pt": {"x": origin_pt[0], "y": origin_pt[1]},
        "region_pt": {"w": region_pt[0], "h": region_pt[1]},
        "image_px": {"w": px_w, "h": px_h},
        "px_per_pt": round(px_w / region_pt[0], 6) if region_pt[0] else 1.0,
        "hint": "pt = origin_pt + (px / px_per_pt). Use --from neste .json.",
    }
    side = Path(str(png).rsplit(".", 1)[0] + ".json")
    side.write_text(json.dumps(data, indent=2))
    return side, data


def load_sidecar(path):
    """Aceita caminho absoluto ou relativo. Relativo é procurado no cwd e depois
    em ~/Laudos_OCT/shots, que é onde 'shot' grava — assim '--from shots/nav.json'
    funciona exatamente como escrito na documentação."""
    p = Path(path).expanduser()
    if not p.exists() and not p.is_absolute():
        for base in (OUT_ROOT / "shots", OUT_ROOT):
            alt = base / path
            if alt.exists():
                p = alt; break
            alt2 = base / Path(path).name
            if alt2.exists():
                p = alt2; break
    if not p.exists():
        die(f"sidecar não encontrado: {path} (procurei no cwd e em {OUT_ROOT/'shots'})")
    return json.loads(p.read_text())


def px_to_pt(sc, x, y):
    ppp = sc["px_per_pt"] or 1.0
    return (sc["origin_pt"]["x"] + x / ppp, sc["origin_pt"]["y"] + y / ppp)


# ---------------------------------------------------------------------- olhos

def cmd_shot(a):
    scale = detect_scale()
    # Prints contêm nome e imagem de paciente: vão SEMPRE para ~/Laudos_OCT/shots,
    # que é exatamente o que 'purge' limpa. Caminho relativo é reancorado ali.
    SHOTS = OUT_ROOT / "shots"
    if a.out:
        out = Path(a.out).expanduser()
        if not out.is_absolute():
            out = SHOTS / out
    else:
        out = SHOTS / f"shot_{int(time.time())}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    if a.roi:
        try:
            rx, ry, rw, rh = [float(v) for v in a.roi.split(",")]
        except Exception:
            die("--roi espera x,y,w,h")
        if a.frm:                       # ROI vem em pixels de outro shot
            sc = load_sidecar(a.frm)
            x0, y0 = px_to_pt(sc, rx, ry)
            ppp = sc["px_per_pt"] or 1.0
            w_pt, h_pt = rw / ppp, rh / ppp
        else:                           # ROI já vem em pontos de tela
            x0, y0, w_pt, h_pt = rx, ry, rw, rh
        _p(plat().capturar, out, regiao=(x0, y0, w_pt, h_pt))
        origin, reg, kind, cap = (int(x0), int(y0)), (int(w_pt), int(h_pt)), "roi", ROI_MAX_EDGE
    else:
        _p(plat().capturar, out)
        pt_w, pt_h = screen_points()
        origin, reg, kind, cap = (0, 0), (pt_w, pt_h), "full", NAV_MAX_EDGE

    if not a.raw:
        px_w, px_h = png_size(out)
        if max(px_w, px_h) > cap:
            _p(plat().redimensionar, out, cap)

    side, data = write_sidecar(out, kind, origin, reg, scale)
    data["sidecar"] = str(side)
    print(json.dumps(data, indent=2))


def cmd_map(a):
    sc = load_sidecar(a.frm)
    x, y = px_to_pt(sc, a.x, a.y)
    print(json.dumps({"pt_x": round(x, 1), "pt_y": round(y, 1)}))


# ----------------------------------------------------------------------- mãos

def guard_ok(x, y, anywhere=False):
    if anywhere:
        return True
    cfg = load_config()
    allowed = cfg.get("allowed_apps") or [TARGET_APP]
    front = frontmost_app()
    # Falha FECHADO: frontmost_app() devolve "" quando falta permissão de
    # Automação (macOS), e o motor de clique continua clicando. Vazio recusa.
    if front not in allowed:
        quem = front or _foco_ilegivel()
        die(f"foco protegido: app em foco é '{quem}', permitido {allowed}. "
            "Reative o AnyDesk e refaça o shot. Não force.", 4)
    r = cfg.get("guard_rect_pt")
    if r:
        if not (r["x"] <= x <= r["x"] + r["w"] and r["y"] <= y <= r["y"] + r["h"]):
            die(f"clique ({int(x)},{int(y)}) fora da área permitida {r}. "
                "Recalibre com 'guard set' ou revise a coordenada.", 4)
    return True


def do_mouse(kind, x, y):
    _p(plat().mouse, kind, x, y)


def resolve_xy(a):
    if a.frm:
        return px_to_pt(load_sidecar(a.frm), a.x, a.y)
    return float(a.x), float(a.y)


def cmd_mouse(a, kind):
    check_stop()
    x, y = resolve_xy(a)
    guard_ok(x, y, a.anywhere)
    if a.dry_run:
        print(json.dumps({"dry_run": kind, "pt_x": round(x, 1), "pt_y": round(y, 1)}))
        return
    assin = f"{kind}:{int(x)},{int(y)}"
    limites(assin)
    # registra a TENTATIVA antes de agir: assim o detector de loop também vê
    # as ações que falham, que é justamente quando o agente tende a insistir.
    audit("acao", tipo=kind, assinatura=assin, pt=[int(x), int(y)],
          janela=frontmost_app())
    try:
        do_mouse(kind, x, y)
    except SystemExit:
        audit("falha", tipo=kind, assinatura=assin)
        raise
    print(json.dumps({"ok": kind, "pt_x": round(x, 1), "pt_y": round(y, 1)}))


def cmd_drag(a):
    check_stop()
    sc = load_sidecar(a.frm) if a.frm else None
    p1 = px_to_pt(sc, a.x1, a.y1) if sc else (a.x1, a.y1)
    p2 = px_to_pt(sc, a.x2, a.y2) if sc else (a.x2, a.y2)
    guard_ok(*p1, a.anywhere); guard_ok(*p2, a.anywhere)
    assin = f"drag:{int(p1[0])},{int(p1[1])}->{int(p2[0])},{int(p2[1])}"
    limites(assin)
    audit("acao", tipo="drag", assinatura=assin, de=[int(p1[0]), int(p1[1])],
          para=[int(p2[0]), int(p2[1])], janela=frontmost_app())
    _p(plat().arrastar, p1, p2)
    print(json.dumps({"ok": "drag", "de": p1, "para": p2}))


def cmd_type(a):
    """Digitação. Quem escolhe o motor é a plataforma."""
    check_stop()
    guard_ok(0, 0, anywhere=True)  # digitação não tem coordenada; valida só o foco
    cfg = load_config()
    allowed = cfg.get("allowed_apps") or [TARGET_APP]
    front = frontmost_app()
    if not a.anywhere and front not in allowed:      # vazio também recusa
        quem = front or _foco_ilegivel()
        die(f"foco protegido: app em foco é '{quem}', permitido {allowed}.", 4)
    if not cfg.get("permitir_digitacao", True):
        die("digitação desabilitada nesta estação (permitir_digitacao=false no config).", 4)
    text = a.text
    if len(text) > 200:
        die("texto acima de 200 caracteres — recusado. Digitação nesta estação serve "
            "para busca de paciente, não para preencher formulário.", 4)
    # O rastro precisa distinguir duas digitações para o detector de loop, e não
    # precisa do nome do paciente em claro num arquivo que ninguém expurga.
    marca = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    limites(f"type:{marca}")
    audit("acao", tipo="type", assinatura=f"type:{marca}", chars=len(text),
          texto_hash=marca, janela=frontmost_app())
    _p(plat().digitar, text)
    print(json.dumps({"ok": "type", "chars": len(text)}))




def cmd_key(a):
    check_stop()
    P = plat()
    parts = [p.strip().lower() for p in a.combo.split("+")]
    key, mods = parts[-1], parts[:-1]

    # Tabela FECHADA: nada que não esteja em TECLAS/MODS chega ao sistema.
    # Sem isto, `key 'a" & (do shell script "...") & "'` virava shell arbitrário —
    # cmd_type escapa, cmd_key não escapava.
    if key not in P.TECLAS:
        die(f"tecla não reconhecida: {key!r}. Aceitas: {sorted(P.TECLAS)}. "
            "Para digitar texto use 'type', que escapa e passa por confirmação.", 4)
    if any(m not in P.MODS for m in mods):
        die(f"modificador não reconhecido em {a.combo!r}. "
            f"Aceitos: {sorted(set(P.MODS))}.", 4)
    motivo = P.COMBOS_NEGADOS.get((frozenset(mods), key))
    if motivo:
        die(f"combo recusado: '{a.combo}' {motivo}", 4)

    # Mesma guarda de foco do clique e da digitação: a tecla vai para o app em
    # primeiro plano, e sem isto ia para qualquer um. Falha fechado.
    cfg = load_config()
    allowed = cfg.get("allowed_apps") or [TARGET_APP]
    front = frontmost_app()
    if front not in allowed:
        quem = front or _foco_ilegivel()
        die(f"foco protegido: app em foco é '{quem}', permitido {allowed}. "
            "Reative o AnyDesk antes de mandar tecla.", 4)

    limites(f"key:{a.combo}")
    audit("acao", tipo="key", assinatura=f"key:{a.combo}", combo=a.combo,
          janela=front)
    _p(P.tecla, key, mods)
    print(json.dumps({"ok": "key", "combo": a.combo}))


def cmd_scroll(a):
    check_stop()
    limites(f"scroll:{a.amount}:{a.x},{a.y}")
    audit("acao", tipo="scroll", assinatura=f"scroll:{a.amount}:{a.x},{a.y}",
          amount=a.amount, janela=frontmost_app())
    if a.x is not None and a.y is not None:
        x, y = resolve_xy(a)
        guard_ok(x, y, a.anywhere)
        do_mouse("move", x, y)
    _p(plat().rolar, a.amount)
    print(json.dumps({"ok": "scroll", "amount": a.amount}))



def cmd_purge(a):
    """Apaga prints — eles contêm nome e imagem de paciente."""
    alvo = Path(a.dir).expanduser().resolve() if a.dir else (OUT_ROOT / "shots")
    # Contenção: --dir apagava *.png/*.json/*.jpg recursivamente em QUALQUER
    # caminho, e --dias 0 é o padrão. Fora de ~/Laudos_OCT, recusa.
    raiz = OUT_ROOT.resolve()
    if not (alvo == raiz or raiz in alvo.parents):
        die(f"purge recusado: {alvo} está fora de {raiz}. "
            "Esta estação só apaga os próprios prints.", 4)
    if not alvo.exists():
        print(json.dumps({"ok": "purge", "dir": str(alvo), "nada": True})); return
    corte = time.time() - a.dias * 86400
    apagados, bytes_ = 0, 0
    for ext in ("*.png", "*.json", "*.jpg"):
        for f in alvo.rglob(ext):
            try:
                if a.dias == 0 or f.stat().st_mtime < corte:
                    bytes_ += f.stat().st_size
                    f.unlink()
                    apagados += 1
            except Exception:
                pass
    audit("purge", dir=str(alvo), apagados=apagados, dias=a.dias)
    print(json.dumps({"ok": "purge", "dir": str(alvo), "apagados": apagados,
                      "kb_liberados": round(bytes_ / 1024, 1)}, ensure_ascii=False))


def cmd_log(a):
    p = audit_path()
    if not p.exists():
        print(json.dumps({"log": str(p), "linhas": 0})); return
    linhas = p.read_text().splitlines()
    if a.resumo:
        from collections import Counter
        c = Counter()
        for ln in linhas:
            try:
                d = json.loads(ln)
                c[f"{d.get('evento')}/{d.get('tipo') or d.get('motivo') or '-'}"] += 1
            except Exception:
                pass
        print(json.dumps({"log": str(p), "total": len(linhas),
                          "resumo": dict(c.most_common())}, indent=2, ensure_ascii=False))
        return
    for ln in linhas[-a.n:]:
        print(ln)



def _hash_regiao(x, y, w, h, grossura=160):
    """Assinatura grosseira de uma região da tela. Grossa de propósito: ignora
    cursor e relógio, mas pega diálogo aparecendo ou tela mudando."""
    tmp = _tmp_png("wait")
    try:
        _p(plat().capturar, tmp, regiao=(x, y, w, h))
        _p(plat().redimensionar, tmp, grossura)
        return hashlib.md5(tmp.read_bytes()).hexdigest()
    finally:
        tmp.unlink(missing_ok=True)


def cmd_aguardar(a):
    """Espera a tela mudar ou estabilizar, SEM gastar token do modelo.

    O modelo não fica olhando print atrás de print: o polling é local. É a
    resposta certa para conexão lenta do AnyDesk — em vez de adivinhar quanto
    tempo dormir, espera até a tela realmente se mover (ou parar de se mover).
    """
    check_stop()
    cfg = load_config()
    if a.roi:
        try:
            x, y, w, h = [float(v) for v in a.roi.split(",")]
        except Exception:
            die("--roi espera x,y,w,h")
        if a.frm:
            sc = load_sidecar(a.frm)
            x, y = px_to_pt(sc, x, y)
            ppp = sc["px_per_pt"] or 1.0
            w, h = w / ppp, h / ppp
    else:
        r = cfg.get("guard_rect_pt") or app_window(TARGET_APP)
        if not r:
            die("sem --roi e sem janela do AnyDesk para observar. Rode 'guard set'.")
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]

    intervalo = max(0.4, a.intervalo)
    limite = time.time() + a.timeout
    base = _hash_regiao(x, y, w, h)
    amostras, iguais_seguidas, mudou = 1, 1, False

    while time.time() < limite:
        time.sleep(intervalo)
        check_stop()          # freio de mão interrompe espera longa em andamento
        atual = _hash_regiao(x, y, w, h)
        amostras += 1
        if atual == base:
            iguais_seguidas += 1
        else:
            mudou, base, iguais_seguidas = True, atual, 1
        if a.modo == "mudar" and mudou:
            break
        if a.modo == "estabilizar" and iguais_seguidas >= a.estaveis:
            if not a.exigir_mudanca or mudou:
                break

    decorrido = round(a.timeout - max(0.0, limite - time.time()), 1)
    estourou = time.time() >= limite and not (
        (a.modo == "mudar" and mudou) or
        (a.modo == "estabilizar" and iguais_seguidas >= a.estaveis))
    audit("aguardar", modo=a.modo, segundos=decorrido, mudou=mudou,
          amostras=amostras, timeout=estourou)
    print(json.dumps({"ok": "aguardar", "modo": a.modo, "segundos": decorrido,
                      "mudou": mudou, "amostras": amostras,
                      "estabilizou": iguais_seguidas >= a.estaveis,
                      "timeout": estourou,
                      "dica": ("tela não se moveu no tempo dado — conexão lenta ou "
                               "ação não surtiu efeito; aumente --timeout antes de "
                               "clicar de novo") if estourou else ""},
                     ensure_ascii=False))
    sys.exit(6 if estourou else 0)


# ------------------------------------------------------------------ controles

def cmd_window(a):
    w = app_window(a.app)
    print(json.dumps({"app": a.app, "window_pt": w,
                      "frontmost": frontmost_app()}, indent=2))


def cmd_guard(a):
    cfg = load_config()
    if a.action == "set":
        w = app_window(a.app)
        if not w:
            die(f"não achei a janela do '{a.app}'. Ele está aberto e visível?")
        pad = a.pad
        cfg["guard_rect_pt"] = {"x": w["x"] - pad, "y": w["y"] - pad,
                                "w": w["w"] + 2 * pad, "h": w["h"] + 2 * pad}
        cfg.setdefault("allowed_apps", [a.app])
        save_config(cfg)
    elif a.action == "clear":
        cfg.pop("guard_rect_pt", None)
        save_config(cfg)
    print(json.dumps({"guard_rect_pt": cfg.get("guard_rect_pt"),
                      "allowed_apps": cfg.get("allowed_apps")}, indent=2))


def cmd_doctor(a):
    rep, ok = {}, True
    rep["python"] = sys.version.split()[0]
    rep["plataforma"] = PLAT.nome if PLAT else f"NÃO SUPORTADA ({sys.platform})"
    if PLAT is None:
        rep["VEREDITO"] = "NAO_PRONTO"
        print(json.dumps(rep, indent=2, ensure_ascii=False)); sys.exit(1)
    rep.update(plat().diagnostico())
    if rep.get("motor_de_clique") in (None, "AUSENTE"):
        ok = False

    plat().preparar()
    tmp = _tmp_png("doctor")
    try:
        _p(plat().capturar, tmp)
        rep["captura_de_tela"] = "ok"
        rep["screenshot_px"] = png_size(tmp)
    except SystemExit:
        rep["captura_de_tela"] = ("FALHOU — conceda Gravação de Tela"
                                  if PLAT.nome == "macOS" else
                                  "FALHOU — verifique pillow e a sessão gráfica")
        ok = False
    finally:
        tmp.unlink(missing_ok=True)

    try:
        rep["tela_pt"] = screen_points()
        rep["escala_retina"] = detect_scale()
    except SystemExit:
        rep["tela_pt"] = ("FALHOU — conceda Automação/Acessibilidade"
                          if PLAT.nome == "macOS" else "FALHOU — não li a tela")
        ok = False

    front = frontmost_app()
    rep["app_em_foco"] = front or "ILEGÍVEL — falta permissão de Automação"
    if not front:
        ok = False           # sem leitura de foco a guarda não protege nada
    win = app_window(TARGET_APP)
    rep["janela_anydesk_pt"] = win or f"NÃO ENCONTRADA (abra o {TARGET_APP})"
    if not win:
        ok = False

    # O endurecimento é o que separa "somente-leitura na estação" de "shell livre
    # com controle de tela". INSTALACAO.md não o instalava e o doctor não o via:
    # a estação saía PRONTO sem hook, sem sandbox e sem deny.
    hook = HOME / ".claude" / "hooks" / "guardiao-laudos.py"
    settings = HOME / ".claude" / "settings.json"
    rep["hook_guardiao"] = "ok" if hook.exists() else f"AUSENTE — {hook}"
    cfg_txt = settings.read_text(encoding="utf-8", errors="replace") if settings.exists() else ""
    tem_hook = "guardiao-laudos" in cfg_txt
    tem_sandbox = '"sandbox"' in cfg_txt
    rep["settings_endurecido"] = ("ok" if (tem_hook and tem_sandbox) else
                                  f"INCOMPLETO — hook={tem_hook} sandbox={tem_sandbox} "
                                  f"em {settings}")
    if not (hook.exists() and tem_hook and tem_sandbox):
        perfil = "settings-macos.json" if PLAT.nome == "macOS" else "settings-windows.json"
        rep["COMO_RESOLVER"] = (
            "cp hardening/hooks/guardiao-laudos.py ~/.claude/hooks/ ; "
            f"cp hardening/{perfil} ~/.claude/settings.json  "
            "— ver INSTALACAO.md Passo 3b e SEGURANCA.md §6")
        ok = False

    cfg = load_config()
    rep["guard_rect_pt"] = cfg.get("guard_rect_pt") or "não calibrado (rode: guard set)"
    rep["allowed_apps"] = cfg.get("allowed_apps") or [TARGET_APP]
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rep["pasta_saida"] = str(OUT_ROOT)
    rep["STOP_ativo"] = STOP_FILE.exists()
    rep["auditoria"] = str(audit_path())
    rep["acoes_ultimo_min"] = len(audit_recentes(60))
    rep["acoes_ultima_hora"] = len(audit_recentes(3600))
    rep["teto_min_hora"] = [cfg.get("max_por_min", MAX_POR_MIN),
                            cfg.get("max_por_hora", MAX_POR_HORA)]
    rep["digitacao_permitida"] = cfg.get("permitir_digitacao", True)
    rep["VEREDITO"] = "PRONTO" if ok and not STOP_FILE.exists() else "NAO_PRONTO"
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["VEREDITO"] == "PRONTO" else 1)


# ------------------------------------------------------------------------ CLI

def main():
    ap = argparse.ArgumentParser(description="Mãos e olhos do agente de laudos OCT (macOS)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_xy(p):
        p.add_argument("x", type=float); p.add_argument("y", type=float)
        p.add_argument("--from", dest="frm", help="sidecar .json do shot de origem")
        p.add_argument("--anywhere", action="store_true", help="ignora a guarda (use com cuidado)")
        p.add_argument("--dry-run", action="store_true")

    s = sub.add_parser("doctor", help="valida ambiente, permissões e janela"); s.set_defaults(f=cmd_doctor)

    s = sub.add_parser("shot", help="captura tela cheia (--full) ou recorte (--roi)")
    s.add_argument("--full", action="store_true")
    s.add_argument("--roi", help="x,y,w,h")
    s.add_argument("--from", dest="frm", help="sidecar cujo espaço de pixels define o --roi")
    s.add_argument("--out"); s.add_argument("--raw", action="store_true", help="não reduzir")
    s.set_defaults(f=cmd_shot)

    s = sub.add_parser("map", help="converte pixel de imagem -> ponto de tela")
    s.add_argument("--from", dest="frm", required=True)
    s.add_argument("x", type=float); s.add_argument("y", type=float)
    s.set_defaults(f=cmd_map)

    for name in ("click", "dblclick", "rclick", "move"):
        s = sub.add_parser(name); add_xy(s)
        s.set_defaults(f=lambda a, k=name: cmd_mouse(a, k))

    s = sub.add_parser("drag")
    for n in ("x1", "y1", "x2", "y2"):
        s.add_argument(n, type=float)
    s.add_argument("--from", dest="frm"); s.add_argument("--anywhere", action="store_true")
    s.set_defaults(f=cmd_drag)

    s = sub.add_parser("type"); s.add_argument("text")
    s.add_argument("--anywhere", action="store_true"); s.set_defaults(f=cmd_type)

    _mm = PLAT.MOD_MENU if PLAT else "cmd"
    s = sub.add_parser("key")
    s.add_argument("combo",
                   help=f"ex: enter, tab, esc, {_mm}+c "
                        "(gravar/imprimir/fechar é recusado)")
    s.set_defaults(f=cmd_key)

    s = sub.add_parser("scroll"); s.add_argument("amount", type=int, help="+ sobe, - desce")
    s.add_argument("--x", type=float); s.add_argument("--y", type=float)
    s.add_argument("--from", dest="frm"); s.add_argument("--anywhere", action="store_true")
    s.add_argument("--dry-run", action="store_true"); s.set_defaults(f=cmd_scroll)

    s = sub.add_parser("window"); s.add_argument("--app", default=TARGET_APP)
    s.set_defaults(f=cmd_window)

    s = sub.add_parser("aguardar", help="espera a tela mudar/estabilizar sem gastar token")
    s.add_argument("--modo", choices=["mudar", "estabilizar"], default="estabilizar")
    s.add_argument("--timeout", type=float, default=45.0)
    s.add_argument("--intervalo", type=float, default=1.0)
    s.add_argument("--estaveis", type=int, default=3,
                   help="amostras iguais seguidas para considerar estável")
    s.add_argument("--exigir-mudanca", dest="exigir_mudanca", action="store_true",
                   help="no modo estabilizar, só aceita depois de ter mudado ao menos uma vez")
    s.add_argument("--roi", help="x,y,w,h (padrão: a janela do AnyDesk)")
    s.add_argument("--from", dest="frm")
    s.set_defaults(f=cmd_aguardar)

    s = sub.add_parser("purge", help="apaga prints (contêm dado de paciente)")
    s.add_argument("--dir", help="padrão: ~/Laudos_OCT/shots")
    s.add_argument("--dias", type=int, default=0, help="0 = apaga tudo (padrão)")
    s.set_defaults(f=cmd_purge)

    s = sub.add_parser("log", help="rastro de auditoria das ações na tela")
    s.add_argument("-n", type=int, default=30); s.add_argument("--resumo", action="store_true")
    s.set_defaults(f=cmd_log)

    s = sub.add_parser("guard"); s.add_argument("action", choices=["set", "clear", "show"])
    s.add_argument("--app", default=TARGET_APP); s.add_argument("--pad", type=int, default=0)
    s.set_defaults(f=cmd_guard)

    a = ap.parse_args()
    if PLAT is not None:
        PLAT.preparar()
    a.f(a)


if __name__ == "__main__":
    main()
