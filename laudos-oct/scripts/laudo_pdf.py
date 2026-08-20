#!/usr/bin/env python3
"""
laudo_pdf.py — gera o PDF do laudo reproduzindo os modelos reais das duas clínicas.

    python3 laudo_pdf.py --json paciente/laudo.json

Layout copiado dos modelos enviados pela clínica:
  hospital="farroupilha" -> BONAVITA: título centralizado, NOME/DATA em Times bold,
                            marca de água central, faixa navy de rodapé.
  hospital="nova_prata"  -> CRO: logo + endereço no topo, título à esquerda,
                            assinatura à direita, rodapé de horários/contatos.

Regra dura: "[VERIFICAR]" em qualquer campo marca o PDF e copia para _PENDENTES/.
"""

import argparse, json, os, re, shutil, sys, time, unicodedata
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame,
                                KeepTogether, PageTemplate, Paragraph, Spacer)

PW, PH = A4
AQUI = Path(__file__).resolve().parent
MARCA = AQUI.parent / "assets" / "marca"
OUT_ROOT = Path.home() / "Laudos_OCT"
PENDENTES = OUT_ROOT / "_PENDENTES"
FLAG = "[VERIFICAR]"        # valor lido, mas não confirmado -> conferir o número
RECAP = "[RECAPTURAR]"      # estrutura não capturada -> voltar e capturar de novo
MARCAS = (FLAG, RECAP)

PRETO = colors.HexColor("#000000")
NAVY = colors.HexColor("#10263D")
PILL_FORA = colors.HexColor("#B10202")
PILL_DENTRO = colors.HexColor("#11734B")
PILL_LIMIAR = colors.HexColor("#8B5E00")
PILL_NEUTRO = colors.HexColor("#5B6670")
ALERTA = colors.HexColor("#B10202")

MEDICOS = {
    "maeta": {
        "nome": "Dr Vinícius L Maeta",
        "registros": ["CRM-SC 23632 RQE 14403", "CRM-RS 40608 RQE 30002"],
    },
}
MEDICO_PADRAO = "maeta"

# Fator de compressão vertical. 1.0 = geometria calibrada pixel a pixel contra os
# laudos modelo. Só cai abaixo de 1.0 quando o conteúdo não cabe em uma página —
# os laudos reais da clínica têm uma página, então achado longo comprime em vez
# de derramar a assinatura sozinha numa página 2.
ESCALA = 1.0


def E(x):
    return x * ESCALA

CLINICAS = {
    "farroupilha": {"template": "bonavita", "nome": "BONAVITA",
                    "pasta": "Farroupilha", "sigla": "FARROUPILHA"},
    "nova_prata": {"template": "cro", "nome": "Centro Regional de Oftalmologia",
                   "pasta": "Nova_Prata", "sigla": "NOVA_PRATA"},
}

TITULOS = {
    "macula": "TOMOGRAFIA DE COERÊNCIA ÓPTICA (OCT) DE MÁCULA",
    "nervo": "TOMOGRAFIA DE COERÊNCIA ÓPTICA (OCT) DE NERVO ÓPTICO",
}
CAMADAS = [
    ("interface_vitreo_retiniana", "interface vítreo-retiniana"),
    ("camadas_internas", "camadas retinianas internas"),
    ("epr_cfr", "epitélio pigmentado da retina (EPR) e camada de fotorreceptores (CFR)"),
]
CLASSIF = {
    "dentro": ("dentro da curva de normalidade", PILL_DENTRO),
    "fora": ("fora da curva de normalidade", PILL_FORA),
    "limitrofe": ("limítrofe", PILL_LIMIAR),
    "limítrofe": ("limítrofe", PILL_LIMIAR),
}


# ------------------------------------------------------------------- estilos

def estilos(tpl):
    def st(n, **kw):
        base = dict(fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=PRETO)
        base.update(kw)
        base["leading"] = base["leading"] * (1 if ESCALA >= 1 else (ESCALA + 1) / 2)
        return ParagraphStyle(n, **base)
    return {
        "titulo_c": st("tc", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                       alignment=TA_CENTER),
        "titulo_e": st("te", fontName="Helvetica-Bold", fontSize=10.5, leading=14),
        "rotulo_tm": st("rt", fontName="Times-Bold", fontSize=11.5, leading=28),
        "ident": st("id", fontSize=10.5, leading=17),
        "olho": st("ol", fontSize=10.5, leading=14),
        "secao": st("se", fontSize=10.5, leading=14),
        "bullet": st("bu", fontSize=10.5, leading=14.5, leftIndent=46,
                     firstLineIndent=-24, bulletIndent=22, alignment=TA_JUSTIFY),
        "corpo": st("co", fontSize=10.5, leading=14.5, alignment=TA_JUSTIFY),
        "assin_c": st("ac", fontName="Times-Bold", fontSize=12, leading=19,
                      alignment=TA_CENTER),
        "assin_e": st("ae", fontSize=10.5, leading=14, alignment=TA_CENTER),
        "alerta": st("al", fontName="Helvetica-Bold", fontSize=9, leading=12,
                     textColor=ALERTA, alignment=TA_CENTER),
    }


# ------------------------------------------- linha com pílula de classificação

class LinhaPill(Flowable):
    """'-  rótulo: valor  (pílula colorida)' — o elemento visual dos modelos."""

    def __init__(self, texto, pill=None, cor=PILL_NEUTRO, largura=None,
                 fonte="Helvetica", tam=10.5, x_dash=19, x_txt=38,
                 espaco_depois=None):
        Flowable.__init__(self)
        self.texto, self.pill, self.cor = texto, pill, cor
        self.fonte, self.tam = fonte, tam
        self.x_dash, self.x_txt = x_dash, x_txt
        self.espaco_depois = E(2.7) if espaco_depois is None else espaco_depois
        self._largura = largura
        self.linhas = []

    def wrap(self, availWidth, availHeight):
        self.disp = self._largura or availWidth
        util = self.disp - self.x_txt
        palavras, atual = self.texto.split(), ""
        self.linhas = []
        for w in palavras:
            teste = (atual + " " + w).strip()
            if stringWidth(teste, self.fonte, self.tam) > util:
                if atual:
                    self.linhas.append(atual)
                atual = w
            else:
                atual = teste
        if atual:
            self.linhas.append(atual)
        # a pílula acompanha a última linha; se não couber, ganha linha própria
        self.pill_nova_linha = False
        if self.pill:
            ult = self.linhas[-1] if self.linhas else ""
            lw = stringWidth(ult, self.fonte, self.tam)
            pw = stringWidth(self.pill, self.fonte, self.tam - 0.5) + 14
            if lw + 6 + pw > util:
                self.pill_nova_linha = True
        n = len(self.linhas) + (1 if self.pill_nova_linha else 0)
        self.passo = self.tam + 3.0 * (1 if ESCALA >= 1 else ESCALA)
        self.altura = n * self.passo + self.espaco_depois
        return (self.disp, self.altura)

    def draw(self):
        c = self.canv
        passo = self.passo
        y = self.altura - self.espaco_depois - self.tam
        c.setFont(self.fonte, self.tam)
        c.setFillColor(PRETO)
        c.drawString(self.x_dash, y, "-")
        for i, ln in enumerate(self.linhas):
            c.setFont(self.fonte, self.tam)
            x = self.x_txt
            yy = y - i * passo
            # segmenta para pintar [VERIFICAR] em vermelho
            resto = ln
            while resto:
                achados = [(resto.find(m), m) for m in MARCAS if resto.find(m) >= 0]
                if not achados:
                    c.setFillColor(PRETO); c.drawString(x, yy, resto); break
                pos, marca = min(achados)
                if pos:
                    c.setFillColor(PRETO); c.drawString(x, yy, resto[:pos])
                    x += stringWidth(resto[:pos], self.fonte, self.tam)
                c.setFillColor(ALERTA); c.drawString(x, yy, marca)
                x += stringWidth(marca, self.fonte, self.tam)
                resto = resto[pos + len(marca):]
        if not self.pill:
            return
        if self.pill_nova_linha:
            px, py = self.x_txt, y - len(self.linhas) * passo
        else:
            ult = self.linhas[-1] if self.linhas else ""
            px = self.x_txt + stringWidth(ult, self.fonte, self.tam) + 6
            py = y - (len(self.linhas) - 1) * passo
        tp = self.tam - 0.5
        pw = stringWidth(self.pill, self.fonte, tp) + 14
        ph = tp + 5
        c.setFillColor(self.cor)
        c.roundRect(px, py - 3.2, pw, ph, ph / 2, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(self.fonte, tp)
        c.drawString(px + 7, py - 0.6, self.pill)


class Linha(Flowable):
    """Traço de assinatura, largura e alinhamento controlados."""

    def __init__(self, larg=230, cx=None):
        Flowable.__init__(self); self.larg, self.cx = larg, cx

    def wrap(self, aw, ah):
        self.aw = aw
        return (aw, 6)

    def draw(self):
        cx = self.cx if self.cx is not None else self.aw / 2
        self.canv.setStrokeColor(PRETO); self.canv.setLineWidth(0.8)
        self.canv.line(cx - self.larg / 2, 2, cx + self.larg / 2, 2)


# ------------------------------------------------------------------ conteúdo

CHAVES = {
    "raiz": {"hospital", "medico", "exame", "paciente", "data_exame", "data_laudo",
             "olhos", "equipamento", "macula", "nervo", "conclusoes", "sugestao",
             "observacoes", "extracao", "_nota"},
    "paciente": {"nome", "nascimento", "prontuario"},
    "nervo": {"area_papila", "rel_esc_papila", "rel_classificacao", "escavacao",
              "escavacao_v", "escavacao_h", "cfn_media", "cfn_classificacao",
              "qualidade", "observacoes"},
    "macula": {"interface_vitreo_retiniana", "camadas_internas", "epr_cfr",
               "qualidade", "observacoes"},
}
# Campos aceitos mas DELIBERADAMENTE não impressos no corpo: o laudo da casa é a
# lista de 4 parâmetros (nervo) ou as 3 camadas (mácula). Ficam no rastro de
# auditoria; se forem parte de uma limitação, entram em 'observacoes' como prosa.
NAO_IMPRESSOS = {"qualidade", "extracao"}

# Fonte única de normalização da lateralidade. A tabela de extracao-tela.md §1
# manda o modelo mapear OS->OE; nada em código conferia, e "olhos" entrava cru no
# NOME DO ARQUIVO enquanto o corpo vinha das chaves preenchidas. Sem allowlist e
# sem reconciliação, saía Laudo_..._OD.pdf com o corpo dizendo OLHO ESQUERDO.
OLHOS_OK = {"OD": "OD", "RE": "OD", "R": "OD", "DIREITO": "OD",
            "OE": "OE", "OS": "OE", "LE": "OE", "L": "OE", "ESQUERDO": "OE",
            "AO": "AO", "OU": "AO", "BOTH": "AO", "AMBOS": "AO"}


def normaliza_olhos(bruto):
    """(valor normalizado, erro). Sem default: ausente é erro, não 'AO'."""
    v = str(bruto or "").upper().replace(" ", "").replace("-", "")
    if not v:
        return None, ("'olhos' ausente. Declare OD, OE ou AO — o laudo não "
                      "assume ambos os olhos por omissão.")
    if v not in OLHOS_OK:
        return None, (f"'olhos' inválido: {bruto!r}. Aceitos: "
                      f"{sorted(set(OLHOS_OK))}.")
    return OLHOS_OK[v], None


def _vazio(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}


def valida(d):
    """(avisos, erros).

    'avisos' são chaves desconhecidas ou não impressas — informação.
    'erros' BLOQUEIAM a emissão. Antes esta função só procurava chave
    desconhecida: um laudo.json sem nome de paciente e sem data do exame passava
    limpo e saía um PDF timbrado, com dois CRMs impressos e os campos em branco.
    A direção que faltava era a inversa — chave obrigatória ausente."""
    avisos, erros = [], []

    def cheque(obj, perm, onde):
        if not isinstance(obj, dict):
            return
        for k in obj:
            if k not in perm:
                avisos.append(f"campo desconhecido '{k}' em {onde} — será ignorado")
            elif k in NAO_IMPRESSOS:
                avisos.append(f"'{k}' em {onde} não é impresso no corpo do laudo "
                              "(por desenho); use 'observacoes' se precisar aparecer")
    cheque(d, CHAVES["raiz"], "raiz")
    cheque(d.get("paciente") or {}, CHAVES["paciente"], "paciente")
    for ex in ("nervo", "macula"):
        for olho in ("OD", "OE"):
            cheque((d.get(ex) or {}).get(olho) or {}, CHAVES[ex], f"{ex}.{olho}")

    # --- presença: o que um laudo assinável não pode deixar em branco ---
    p = d.get("paciente") or {}
    if _vazio(p.get("nome")):
        erros.append("'paciente.nome' vazio — o laudo sairia sem identificação, "
                     "com o CRM do médico impresso abaixo")
    if _vazio(d.get("data_exame")):
        erros.append("'data_exame' vazia — sem data o laudo não é conferível "
                     "contra o exame na estação")
    if _vazio(d.get("hospital")):
        erros.append("'hospital' vazio — define o template, a pasta e o cabeçalho")

    olhos, err = normaliza_olhos(d.get("olhos"))
    if err:
        erros.append(err)

    exame = d.get("exame") or ("nervo" if d.get("nervo") else "macula")
    corpo = d.get(exame) or {}
    preenchidos = sorted(k for k in ("OD", "OE") if corpo.get(k))
    if not preenchidos:
        erros.append(f"nenhum olho preenchido em '{exame}' — o PDF sairia com "
                     "cabeçalho, conclusões e assinatura, sem descrição nenhuma")
    elif olhos:
        esperado = ["OD", "OE"] if olhos == "AO" else [olhos]
        if preenchidos != sorted(esperado):
            erros.append(f"'olhos' declara {olhos} mas há dados de {preenchidos}. "
                         "O nome do arquivo sairia com um olho e o corpo com "
                         "outro. Corrija a extração ou marque [RECAPTURAR]")
    if _vazio(d.get("conclusoes")):
        erros.append("'conclusoes' vazio — a seção CONCLUSÕES sairia só com o título")
    return avisos, erros


def estado_da_base():
    """(revisada?, versao, revisor) lido de references/base/00-indice.md."""
    idx = AQUI.parent / "references" / "base" / "00-indice.md"
    if not idx.exists():
        return None, "ausente", "ausente"
    t = idx.read_text(encoding="utf-8")
    linha = next((l for l in t.splitlines() if "VERSÃO:" in l), "")
    ver = linha if "VERSÃO:" in linha else "VERSÃO: ?"
    rev = next((l for l in t.splitlines() if "REVISADO POR:" in l), "REVISADO POR: ?")
    limpa = lambda x: x.strip().strip("`").replace("`", "").strip()
    if limpa(ver) == limpa(rev):                      # mesma linha traz os dois
        partes = [x.strip() for x in limpa(ver).split("·")]
        ver, rev = (partes + ["REVISADO POR: ?"])[:2]
    pend = ("PENDENTE" in rev.upper() or "RASCUNHO" in ver.upper()
            or "?" in rev)
    return (not pend), limpa(ver), limpa(rev)


def txt(v):
    """Texto para desenho direto no canvas (LinhaPill). SEM escape de markup —
    escapar aqui imprimia '&lt;' literal em '< 63 µm'."""
    return "" if v is None else str(v).strip()


def par(v):
    """Texto para Paragraph, que interpreta markup. COM escape."""
    s = txt(v)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sem_flag_repetida(valor, texto):
    """Se o valor já traz um marcador, o texto explicativo não repete a marca."""
    if any(m in valor for m in MARCAS) and texto:
        t = texto
        for m in MARCAS:
            t = t.replace(m, "", 1)
        return t.lstrip(" —-–:").strip()
    return texto


def pill_de(valor):
    """('texto da pílula', cor) ou (None, None) se não houver classificação."""
    if not valor:
        return None, None
    v = str(valor).strip()
    if FLAG in v:
        return None, None
    chave = unicodedata.normalize("NFKD", v.lower()).encode("ascii", "ignore").decode()
    for k, (txt, cor) in CLASSIF.items():
        kk = unicodedata.normalize("NFKD", k).encode("ascii", "ignore").decode()
        if chave == kk or chave == unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode():
            return txt, cor
    return v, PILL_NEUTRO


def bloco_olho(sigla, dados, exame, S):
    """'OLHO DIREITO' + as linhas com pílula."""
    out = [Paragraph("OLHO DIREITO" if sigla == "OD" else "OLHO ESQUERDO", S["olho"]),
           Spacer(1, E(10.3))]
    if exame == "macula":
        for key, label in CAMADAS:
            val = txt(dados.get(key))
            if not val:
                continue          # campo vazio some do laudo — não vira "—" solto
            out.append(LinhaPill(f"{label} {val}"))
    else:
        area = txt(dados.get("area_papila"))
        if area:
            out.append(LinhaPill(f"área da papila: {area}"))

        rel = txt(dados.get("rel_esc_papila")) or "—"
        cls = txt(dados.get("rel_classificacao"))
        marcado = any(m in rel for m in MARCAS)
        ptxt, pcor = (None, None) if marcado else pill_de(dados.get("rel_classificacao"))
        rotulo = f"relação escavação/papila (área): {rel}"
        cls = sem_flag_repetida(rel, cls)
        if cls and not ptxt:          # sem pílula: o texto entra na linha, com o motivo
            rotulo += f" — {cls}"
        out.append(LinhaPill(rotulo, ptxt, pcor or PILL_NEUTRO))

        v, h = txt(dados.get("escavacao_v")), txt(dados.get("escavacao_h"))
        esc_txt = (f"{v} (v) x {h} (h)" if (v or h) else txt(dados.get("escavacao")) or "—")
        out.append(LinhaPill(f"escavação: {esc_txt}"))

        cfn = txt(dados.get("cfn_media")) or "—"
        ccls = txt(dados.get("cfn_classificacao"))
        cmarcado = any(m in cfn for m in MARCAS)
        ctxt, ccor = (None, None) if cmarcado else pill_de(dados.get("cfn_classificacao"))
        rot = f"camada de fibras nervosas (média): {cfn}"
        ccls = sem_flag_repetida(cfn, ccls)
        if ccls and not ctxt:
            rot += f" — {ccls}"
        out.append(LinhaPill(rot, ctxt, ccor or PILL_NEUTRO))

    if dados.get("observacoes"):
        out.append(LinhaPill(txt(dados["observacoes"])))
    out.append(Spacer(1, E(32.7)))
    return out


def bloco_conclusoes(d, S):
    out = [Paragraph("CONCLUSÕES", S["secao"]), Spacer(1, E(1))]
    concl = d.get("conclusoes")
    if isinstance(concl, str):
        concl = [concl]
    for c in (concl or []):
        out.append(LinhaPill(txt(c)))
    out.append(Spacer(1, E(22)))
    if d.get("sugestao"):
        out.append(Paragraph(par(d["sugestao"]), S["corpo"]))
    return out


def bloco_assinatura(tpl, med, S):
    """Espaço em branco + nome e registros impressos abaixo, para assinatura à mão.

    NÃO existe caminho para embutir imagem de assinatura. A clínica decidiu não
    usar assinatura digitalizada (SEGURANCA.md §9) e a capacidade foi removida do
    código, não apenas desligada: um PDF que já sai assinado é documento
    executado, e quem carrega a consequência é o CRM impresso aqui."""
    if tpl == "bonavita":
        blk = [Spacer(1, E(22)), Spacer(1, E(34)),
               Linha(larg=232), Spacer(1, E(18)),
               Paragraph(med["nome"], S["assin_c"])]
        blk += [Paragraph(r, S["assin_c"]) for r in med["registros"]]
    else:
        blk = [Spacer(1, E(26)), Spacer(1, E(44))]
        est = ParagraphStyle("ad", parent=S["assin_e"], alignment=TA_CENTER,
                             leftIndent=235)
        blk += [Paragraph(med["nome"], est)]
        blk += [Paragraph(r, est) for r in med["registros"]]
    return [KeepTogether(blk)]


# ------------------------------------------------------------ página e monta

def marca_minuta(canv, base_nao_revisada=False):
    """Carimbo em TODAS as páginas: este documento é minuta, não laudo assinado.

    Sem ele o PDF era, no papel, indistinguível de um laudo final — timbre, marca
    d'água da clínica, nome e dois CRMs impressos, linha de assinatura — e a
    revisão do médico era a única coisa entre um número lido errado e um
    documento com CRM."""
    canv.saveState()
    canv.setFont("Helvetica-Bold", 7.2)
    canv.setFillColor(PILL_NEUTRO)
    canv.drawString(34, PH - 26,
                    "MINUTA — CONFERIR E ASSINAR · gerada com apoio automatizado")
    if base_nao_revisada:
        canv.setFillColor(ALERTA)
        canv.drawString(34, PH - 36,
                        "BASE CIENTÍFICA NÃO REVISADA — uso restrito a teste, "
                        "não use com paciente real")
    canv.setFont("Helvetica", 6.6)
    canv.setFillColor(PILL_NEUTRO)
    canv.drawRightString(PW - 34, 16,
                         "Documento sem validade até a assinatura do médico responsável")
    canv.restoreState()


def desenha_bonavita(canv, doc):
    canv.saveState()
    wm = MARCA / "marca_agua_bonavita.png"
    if wm.exists():
        w = 358.5; h = w * 296 / 607
        canv.drawImage(str(wm), (PW - w) / 2, PH / 2 - h / 2 + 14, w, h,
                       mask="auto", preserveAspectRatio=True)
    ft = MARCA / "footer_bonavita.png"
    if ft.exists():
        h = PW * 158 / 840
        canv.drawImage(str(ft), 0, 0, PW, h, mask="auto")
    else:
        canv.setFillColor(NAVY); canv.rect(0, 0, PW, 78, stroke=0, fill=1)
    canv.restoreState()


def desenha_cro(canv, doc):
    canv.saveState()
    lg = MARCA / "logo_cro.png"
    if lg.exists():
        # geometria medida no modelo: conteúdo 311x62 px @100dpi, topo a 78 px
        w = 224.0; h = w * 60.0 / 300.0
        canv.drawImage(str(lg), 83.5, PH - 56.0 - h, w, h, mask="auto")
    canv.setFont("Helvetica", 8.6); canv.setFillColor(PRETO)
    canv.drawRightString(PW - 72, PH - 62, "Av. Cônego Peres 765 - 2º Andar")
    canv.drawRightString(PW - 72, PH - 74, "junto ao hospital São João Batista")

    y = 74
    canv.setFont("Helvetica-Bold", 9.6)
    t1 = "Horários de Atendimento"
    canv.drawString(76, y, t1)
    canv.setFont("Helvetica", 9)
    canv.drawString(76 + stringWidth(t1, "Helvetica-Bold", 9.6) + 5, y,
                    "Segunda à Sexta das 8:00hrs às 12:00 hrs e 13:30 hrs às 18:00hrs")
    y -= 26
    canv.setFont("Helvetica-Bold", 9.6)
    t2 = "Contatos"
    canv.drawString(76, y, t2)
    canv.setFont("Helvetica", 9)
    canv.drawString(76 + stringWidth(t2, "Helvetica-Bold", 9.6) + 5, y,
                    "Recepção (54) 3242-7641 ou 9 9943-5980")
    canv.drawString(PW - 72 - stringWidth("atendimento@croftalmologia.com.br",
                                          "Helvetica", 9), y,
                    "atendimento@croftalmologia.com.br")
    canv.restoreState()


def build(d, out_pdf, base_nao_revisada=False):
    clin = CLINICAS[d["hospital"]]
    tpl = clin["template"]
    med = MEDICOS[d.get("medico", MEDICO_PADRAO)]
    exame = d.get("exame") or ("nervo" if d.get("nervo") else "macula")
    S = estilos(tpl)
    bruto = json.dumps(d, ensure_ascii=False)
    tem_verificar, tem_recap = FLAG in bruto, RECAP in bruto
    pend = tem_verificar or tem_recap

    if tpl == "bonavita":
        ml, mr, mt, mb = 72, 72, 82.8, 116
        onpage = desenha_bonavita
    else:
        ml, mr, mt, mb = 72, 72, 148, 118
        onpage = desenha_cro

    # Metadados SEM nome de paciente: o título vazava para índice do Finder,
    # pré-visualização e backup. E o autor não é o médico — ele ainda não assinou;
    # dizer que é dele nos metadados é afirmar uma revisão que não aconteceu.
    doc = BaseDocTemplate(str(out_pdf), pagesize=A4,
                          leftMargin=ml, rightMargin=mr, topMargin=mt, bottomMargin=mb,
                          title=f"Minuta de laudo — {TITULOS[exame]}",
                          author="Minuta gerada com apoio automatizado — não assinada",
                          subject=TITULOS[exame])

    def com_marca(canv, doc_):
        onpage(canv, doc_)
        marca_minuta(canv, base_nao_revisada)

    doc.addPageTemplates([PageTemplate(id="p", onPage=com_marca, frames=[
        Frame(ml, mb, PW - ml - mr, PH - mt - mb, id="c",
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])

    story = []
    p = d.get("paciente", {})

    if tpl == "bonavita":
        story += [Paragraph(TITULOS[exame], S["titulo_c"]), Spacer(1, E(41.2))]
        story += [Paragraph(f"NOME: {par(p.get('nome'))}", S["rotulo_tm"]),
                  Paragraph(f"DATA DE NASCIMENTO: {par(p.get('nascimento'))}", S["rotulo_tm"]),
                  Paragraph(f"DATA DO EXAME: {par(d.get('data_exame'))}", S["rotulo_tm"]),
                  Spacer(1, E(13.9))]
    else:
        ident = f"Paciente: {par(p.get('nome'))}"
        if p.get("nascimento"):
            # Acréscimo ao modelo original do CRO: sem nascimento, dois homônimos
            # ficam indistinguíveis no documento assinado (regra 4 da skill).
            ident += f"  —  Nascimento: {par(p.get('nascimento'))}"
        story += [Paragraph(ident, S["ident"]),
                  Paragraph(f"Data: {par(d.get('data_exame'))}", S["ident"]),
                  Spacer(1, E(26)),
                  Paragraph(TITULOS[exame], S["titulo_e"]), Spacer(1, E(14))]

    if pend:
        avisos = []
        if tem_verificar:
            avisos.append(f"{FLAG} — valor lido sem confirmação: conferir o número na "
                          "estação antes de liberar")
        if tem_recap:
            avisos.append(f"{RECAP} — estrutura não capturada: voltar ao exame e capturar "
                          "o corte completo. Não significa exame alterado")
        story += [Paragraph("ATENÇÃO — " + ".  ".join(avisos) + ".", S["alerta"]),
                  Spacer(1, E(12))]

    corpo = d.get(exame) or {}
    # A reconciliação olhos-declarados x olhos-preenchidos é feita em valida(),
    # que BLOQUEIA. Aqui já se sabe que as duas fontes concordam.
    for sig in ("OD", "OE"):
        if corpo.get(sig):
            story += bloco_olho(sig, corpo[sig], exame, S)

    story += bloco_conclusoes(d, S)
    story += bloco_assinatura(tpl, med, S)
    doc.build(story)
    return pend, doc.page


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "Paciente"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out")
    ap.add_argument("--sobrescrever", action="store_true",
                    help="refaz um laudo já emitido, apagando o anterior")
    ap.add_argument("--base-nao-revisada", action="store_true",
                    help="SÓ PARA TESTE: emite mesmo com a base marcada como rascunho")
    a = ap.parse_args()

    src = Path(a.json)
    if not src.exists():
        sys.exit(f"ERRO: não achei {src}")
    d = json.loads(src.read_text(encoding="utf-8"))
    bruto_final = json.dumps(d, ensure_ascii=False)

    # A base científica orienta a redação clínica deste laudo. Enquanto ela estiver
    # marcada como rascunho ou sem revisão médica, emitir é produzir documento
    # clínico apoiado em guia que se declara impróprio. Trava de código, não de prosa.
    avisos, erros = valida(d)
    for av in avisos:
        print(f"AVISO: {av}", file=sys.stderr)
    if erros:
        sys.exit("ERRO: laudo não emitido — campo obrigatório ausente ou "
                 "inconsistente:\n  - " + "\n  - ".join(erros) +
                 "\n  Corrija o laudo.json. Se o dado não existe no exame, use "
                 "[VERIFICAR] ou [RECAPTURAR] no valor — não deixe em branco.")

    revisada, versao, revisor = estado_da_base()
    if revisada is False and not a.base_nao_revisada:
        sys.exit(
            "ERRO: base científica não liberada para produção.\n"
            f"  {versao}\n  {revisor}\n"
            "  A base orienta a redação clínica deste laudo. Emitir agora produz\n"
            "  documento médico apoiado em guia que se declara não revisado.\n"
            "  Peça a revisão e troque as duas linhas em references/_fonte/base-cientifica.md,\n"
            "  depois rode scripts/dividir_guia.py.\n"
            "  Só para TESTE, e nunca com paciente real: --base-nao-revisada")
    if revisada is None and not a.base_nao_revisada:
        # Base ausente não é estado mais seguro que base não revisada: é o estado
        # que dividir_guia.py deixa se falhar no meio. Antes só avisava e emitia.
        sys.exit(
            "ERRO: base científica ausente (references/base/ vazio ou inexistente).\n"
            "  A base orienta o vocabulário clínico deste laudo. Sem ela o laudo\n"
            "  sairia sem o apoio que sustenta a redação.\n"
            "  Rode: python3 ~/.claude/skills/laudos-oct/scripts/dividir_guia.py")
    if d.get("hospital") not in CLINICAS:
        sys.exit(f"ERRO: 'hospital' deve ser um de {list(CLINICAS)}")
    if d.get("medico", MEDICO_PADRAO) not in MEDICOS:
        sys.exit(f"ERRO: 'medico' deve ser um de {list(MEDICOS)}")

    exame = d.get("exame") or ("nervo" if d.get("nervo") else "macula")
    clin = CLINICAS[d["hospital"]]
    nome = slug(d.get("paciente", {}).get("nome", "Paciente"))
    olhos, _ = normaliza_olhos(d.get("olhos"))     # já validado acima
    suf = "NO" if exame == "nervo" else "MAC"
    # A DATA entra no nome. Sem ela, o exame de acompanhamento do mesmo paciente,
    # mesmo olho e mesma modalidade caía no mesmo caminho e o segundo laudo
    # apagava o primeiro sem avisar ninguém.
    data = slug(d.get("data_exame"))[:24]
    arquivo = f"Laudo_{clin['sigla']}_{nome}_{suf}_{olhos}_{data}.pdf"
    if a.out:
        out = Path(a.out).expanduser()
    else:
        # Sempre ancorado, nunca herdando o diretório do JSON: hospital no nome do
        # arquivo e na pasta evita sobrescrever laudo de homônimo de outra unidade.
        out = OUT_ROOT / clin["pasta"] / nome / arquivo
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not a.sobrescrever:
        sys.exit(f"ERRO: já existe {out}\n"
                 "  Emitir apagaria o laudo anterior em silêncio. Se a intenção é\n"
                 "  refazer este mesmo laudo, use --sobrescrever; se é outro exame,\n"
                 "  confira 'data_exame' — é ela que distingue os dois no nome.")

    global ESCALA
    # Piso 0,82: abaixo disso a entrelinha aperta demais para um documento que um
    # médico assina. Se nem a 0,82 couber, o laudo vai para duas páginas e avisa —
    # duas páginas legíveis é melhor que uma ilegível.
    # Escrita atômica: build() escrevia direto no destino final, e uma
    # interrupção (Ctrl+C está no procedimento de emergência de SEGURANCA.md §8)
    # deixava PDF truncado no lugar do laudo.
    parcial = out.with_name(out.name + ".part")
    try:
        for esc in (1.0, 0.90, 0.82):
            ESCALA = esc
            pend, paginas = build(d, parcial, a.base_nao_revisada)
            if paginas == 1:
                break
        os.replace(parcial, out)
    finally:
        Path(parcial).unlink(missing_ok=True)
    if ESCALA < 1.0:
        print(f"AVISO: conteúdo longo — entrelinha comprimida a {ESCALA:.2f}; "
              f"{paginas} página(s).", file=sys.stderr)
    if paginas > 1:
        print("AVISO: o laudo passou de uma página mesmo no piso de compressão. "
              "Os laudos da clínica têm uma página — confira se a redação pode ser "
              "enxugada antes de liberar.", file=sys.stderr)
    res = {"pdf": str(out), "template": clin["template"], "base": versao,
           "medico": MEDICOS[d.get("medico", MEDICO_PADRAO)]["nome"],
           "pendente": pend,
           "paginas": paginas, "escala": ESCALA}
    if pend:
        # A cópia leva a hora no nome: reprocessar um laudo acumula versões aqui de
        # propósito (nada se perde na fila de conferência), e a mais recente é
        # identificável pela ordem alfabética do nome.
        PENDENTES.mkdir(parents=True, exist_ok=True)
        selo = time.strftime("%Y-%m-%d_%H%M%S")
        alvo = PENDENTES / f"{out.stem}__{selo}{out.suffix}"
        shutil.copy2(out, alvo)
        res["copia_pendentes"] = str(alvo)
        res["motivos"] = ([f"{FLAG}: valor não confirmado"] if FLAG in bruto_final else []) + \
                         ([f"{RECAP}: estrutura não capturada"] if RECAP in bruto_final else [])
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
