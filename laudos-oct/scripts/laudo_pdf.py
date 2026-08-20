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
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image,
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
PILL_NEUTRO = colors.HexColor("#5B6670")
ALERTA = colors.HexColor("#B10202")

# Signatário por HOSPITAL, extraído dos laudos reais. Nunca vem do laudo.json:
# um laudo de Farroupilha com os dados do Dr. Maeta (ou o contrário) é documento
# assinado por quem não atendeu, e por isso é recusa, não aviso.
#
# A grafia abaixo é a dos laudos reais e NÃO deve ser uniformizada:
#   - Farroupilha escreve "Dr." com ponto; Nova Prata escreve "Dr" sem ponto.
#   - Farroupilha usa ponto de milhar ("30.544", "25.730"); Nova Prata não.
#   - Nova Prata imprime as DUAS inscrições, SC antes de RS, uma por linha.
ASSINANTES = {
    "farroupilha": {
        "chave": "cassiano",
        "nome": "Dr. Cassiano Ricardo Goulart",
        "registros": ["CRM-RS 30.544 RQE 25.730"],
        "arquivo_assinatura": "assinatura_cassiano",
    },
    "nova_prata": {
        "chave": "maeta",
        "nome": "Dr Vinícius L Maeta",
        "registros": ["CRM-SC 23632 RQE 14403", "CRM-RS 40608 RQE 30002"],
        "arquivo_assinatura": "assinatura_maeta",
    },
}

# Onde as imagens de assinatura vivem: FORA do pacote e fora do versionamento.
DIR_ASSINATURAS = Path.home() / ".laudos_oct" / "assinaturas"


def pend_marcadores(d):
    """True se houver [VERIFICAR]/[RECAPTURAR] em qualquer profundidade."""
    bruto = json.dumps(d, ensure_ascii=False)
    return any(m in bruto for m in MARCAS)


def assinante_de(hospital):
    """O signatário daquele hospital, ou uma parada. Sem default, sem herança."""
    a = ASSINANTES.get(hospital)
    if not a:
        sys.exit(f"ERRO: hospital indefinido ou desconhecido: {hospital!r}. "
                 f"Sem hospital não há signatário, e sem signatário não há laudo. "
                 f"Aceitos: {sorted(ASSINANTES)}")
    faltando = [c for c in ("nome", "registros") if not a.get(c)]
    if faltando:
        sys.exit(f"ERRO: signatário de {hospital} incompleto — falta: "
                 f"{', '.join(faltando)}.")
    return a

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
# Decisão do Dr. Maeta (formulário 20/08/2026, item 3.4): verde e branco são
# DENTRO; amarelo e vermelho são FORA, com a MESMA redação. Não existe categoria
# "limítrofe" neste sistema — quem lê a tela classifica em dois estados, não três.
CLASSIF = {
    "dentro": ("dentro da curva de normalidade", PILL_DENTRO),
    "fora": ("fora da curva de normalidade", PILL_FORA),
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
              "observacoes"},
    "macula": {"interface_vitreo_retiniana", "camadas_internas", "epr_cfr",
               "observacoes"},
}
# Campos aceitos mas DELIBERADAMENTE não impressos no corpo: o laudo da casa é a
# lista de 4 parâmetros (nervo) ou as 3 camadas (mácula). Ficam no rastro de
# auditoria; se forem parte de uma limitação, entram em 'observacoes' como prosa.
NAO_IMPRESSOS = {"extracao"}

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
    if _vazio(d.get("conclusoes")) and not nervo_todo_dentro(d, exame):
        erros.append("'conclusoes' vazio — a seção CONCLUSÕES sairia só com o título")
    # A exceção é UMA só: nervo com os dois parâmetros dentro da curva nos dois
    # olhos. O Dr. Maeta reprovou a conclusão proposta para esse caso e não
    # escreveu substituta (Bloco 2, 20/08/2026), então não existe frase aprovada
    # — o campo sai em branco e a conclusão é dele. Mácula sem conclusão continua
    # sendo erro.
    return avisos, erros


BASE_DIR = AQUI.parent / "references" / "base"
REGISTRO_REVISAO = BASE_DIR / "REVISAO.json"


def hash_da_base():
    """Impressão digital do conteúdo clínico da base, em ordem estável.

    É o que faz a liberação valer PARA A VERSÃO REVISADA: se a base mudar depois,
    o hash muda, o registro deixa de casar e a trava volta sozinha — sem ninguém
    precisar lembrar de reativá-la."""
    import hashlib
    h = hashlib.sha256()
    for f in sorted(BASE_DIR.glob("*.md")):
        if f.name == "00-indice.md":
            continue                      # gerado; carrega o carimbo, não o conteúdo
        h.update(f.name.encode("utf-8"))
        h.update(f.read_bytes())
    return h.hexdigest()


def estado_da_base():
    """(revisada?, versao, revisor).

    A liberação é um REGISTRO, não uma linha apagada: quem revisou, quando, e
    sobre qual conteúdo. A checagem continua aqui — apenas satisfeita."""
    if not BASE_DIR.exists() or not any(BASE_DIR.glob("*.md")):
        return None, "ausente", "ausente"
    if not REGISTRO_REVISAO.exists():
        return False, "sem registro de revisão", "REVISADO POR: PENDENTE"
    try:
        reg = json.loads(REGISTRO_REVISAO.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"registro de revisão ilegível ({e})", "REVISADO POR: ?"

    revisor, data = reg.get("revisor") or "", reg.get("data") or ""
    versao = reg.get("versao_revisada") or "?"
    if not revisor or not data:
        return False, f"VERSÃO: {versao}", "REVISADO POR: registro incompleto"
    if reg.get("hash_base") != hash_da_base():
        return (False,
                f"VERSÃO: {versao} — a base MUDOU depois da revisão",
                f"REVISADO POR: {revisor} em {data} (o registro não vale para o "
                "conteúdo atual)")
    return True, f"VERSÃO: {versao}", f"REVISADO POR: {revisor} em {data}"


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


# Decisão 1.1 (formulário 20/08/2026): entra em TODO laudo de nervo óptico, dos
# dois hospitais, e em NENHUM de mácula.
RESERVA_DIAGNOSTICA = ("Os achados estruturais isoladamente não estabelecem "
                       "diagnóstico; sugere-se correlação com quadro clínico, "
                       "pressão intraocular e campo visual.")


def nervo_todo_dentro(d, exame):
    """Nervo com os dois parâmetros classificados dentro da curva, nos dois olhos.

    Bloco 2 do formulário: a conclusão proposta para esse caso foi REPROVADA e o
    Dr. Maeta não escreveu substituta. Não existe frase aprovada — então o campo
    sai em branco e a conclusão é dele. Não é erro nem bloqueio."""
    if exame != "nervo":
        return False
    corpo = d.get("nervo") or {}
    olhos = [corpo[k] for k in ("OD", "OE") if corpo.get(k)]
    if not olhos:
        return False
    for olho in olhos:
        for campo in ("rel_classificacao", "cfn_classificacao"):
            v = str(olho.get(campo) or "").strip().lower()
            if not v.startswith("dentro"):
                return False
    return True


def bloco_conclusoes(d, S, exame):
    out = [Paragraph("CONCLUSÕES", S["secao"]), Spacer(1, E(1))]
    concl = d.get("conclusoes")
    if isinstance(concl, str):
        concl = [concl]
    concl = [c for c in (concl or []) if txt(c)]

    if concl:
        for c in concl:
            out.append(LinhaPill(txt(c)))
    elif nervo_todo_dentro(d, exame):
        # Em branco de propósito, e dito em voz alta para quem revisa.
        out.append(Paragraph(
            "<i>— a conclusão deste caso é do médico responsável: não há frase "
            "aprovada para nervo inteiramente dentro da curva.</i>", S["corpo"]))
    out.append(Spacer(1, E(22)))

    if d.get("sugestao"):
        out.append(Paragraph(par(d["sugestao"]), S["corpo"]))
    if exame == "nervo":
        out.append(Spacer(1, E(10)))
        out.append(Paragraph(RESERVA_DIAGNOSTICA, S["corpo"]))
    return out


# Farroupilha imprime a linha de assinatura no laudo de nervo e não imprime no de
# mácula. Padronizado COM a linha nos dois; vire False para voltar ao original.
LINHA_ASSINATURA_FARROUPILHA = True


def caminho_assinatura(assinante):
    """PNG/SVG do signatário, de ~/.laudos_oct/assinaturas. None se não houver.

    Fora do pacote e fora do versionamento de propósito: imagem de assinatura é
    o ativo mais sensível do projeto."""
    base = assinante.get("arquivo_assinatura")
    if not base:
        return None
    for ext in (".svg", ".png"):          # SVG é o padrão; PNG é a reserva
        p = DIR_ASSINATURAS / (base + ext)
        if p.exists():
            return p
    return None


def bloco_assinatura(tpl, assinante, S, assinar=False):
    """Nome e registros do signatário do hospital.

    A imagem de assinatura só entra quando `assinar` é verdadeiro — o que exige
    a ação deliberada `--assinar`. Minuta sai sempre SEM assinatura: documento
    que já sai assinado é documento executado, e quem carrega a consequência é o
    CRM impresso aqui."""
    img = []
    if assinar:
        cam = caminho_assinatura(assinante)
        if cam and cam.suffix.lower() == ".png":
            img = [Image(str(cam), height=E(51), width=None, kind="proportional")]
        # SVG exige svglib; enquanto não houver, o final recusa antes de chegar
        # aqui (ver exige_assinatura()).

    if tpl == "bonavita":
        blk = [Spacer(1, E(22))]
        blk += (img + [Spacer(1, E(2))]) if img else [Spacer(1, E(34))]
        if LINHA_ASSINATURA_FARROUPILHA:
            blk += [Linha(larg=232), Spacer(1, E(18))]
        blk += [Paragraph(assinante["nome"], S["assin_c"])]
        blk += [Paragraph(r, S["assin_c"]) for r in assinante["registros"]]
    else:
        # Nova Prata: sem linha, alinhado à direita.
        blk = [Spacer(1, E(26))]
        if img:
            im = img[0]; im.hAlign = "RIGHT"
            blk += [im, Spacer(1, E(1))]
        else:
            blk += [Spacer(1, E(44))]
        est = ParagraphStyle("ad", parent=S["assin_e"], alignment=TA_CENTER,
                             leftIndent=235)
        blk += [Paragraph(assinante["nome"], est)]
        blk += [Paragraph(r, est) for r in assinante["registros"]]
    return [KeepTogether(blk)]


def exige_assinatura(assinante, hospital):
    """Recusa o documento final dizendo exatamente qual elemento falta."""
    cam = caminho_assinatura(assinante)
    if cam is None:
        sys.exit(
            f"ERRO: falta a IMAGEM DE ASSINATURA de {assinante['nome']} "
            f"({hospital}).\n"
            f"  Esperada em: {DIR_ASSINATURAS / (assinante['arquivo_assinatura'] + '.png')}\n"
            "  (ou .svg). Sem ela o documento final não é emitido — a minuta,\n"
            "  sem --assinar, continua saindo normalmente.")
    if cam.suffix.lower() == ".svg":
        sys.exit(
            f"ERRO: assinatura em SVG ({cam.name}) ainda não é renderizável — "
            "falta a dependência svglib.\n"
            "  Instale svglib ou forneça a versão .png ao lado do .svg.")
    return cam


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


def build(d, out_pdf, base_nao_revisada=False, assinar=False):
    clin = CLINICAS[d["hospital"]]
    tpl = clin["template"]
    assinante = assinante_de(d.get("hospital"))
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
                          title=(TITULOS[exame] if assinar
                                 else f"Minuta de laudo — {TITULOS[exame]}"),
                          author=(assinante["nome"] if assinar else
                                  "Minuta gerada com apoio automatizado — não assinada"),
                          subject=TITULOS[exame])

    def com_marca(canv, doc_):
        onpage(canv, doc_)
        if not assinar:
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
        # Decisão 1.3: nascimento em linha própria, impressa SÓ quando existe —
        # sem rótulo vazio e sem placeholder.
        story += [Paragraph(f"Paciente: {par(p.get('nome'))}", S["ident"])]
        if txt(p.get("nascimento")):
            story += [Paragraph(
                f"Data de nascimento: {par(p.get('nascimento'))}", S["ident"])]
        story += [Paragraph(f"Data: {par(d.get('data_exame'))}", S["ident"]),
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

    story += bloco_conclusoes(d, S, exame)
    story += bloco_assinatura(tpl, assinante, S, assinar)
    doc.build(story)
    return pend, doc.page


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "Paciente"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out")
    ap.add_argument("--assinar", action="store_true",
                    help="emite o DOCUMENTO FINAL assinado (exige a imagem de "
                         "assinatura do signatário do hospital). Sem esta flag "
                         "sai a minuta, sempre sem assinatura.")
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
            "  A liberação é um registro: references/base/REVISAO.json com revisor,\n"
            "  data e o hash da base revisada. Se a base mudou depois da revisão, o\n"
            "  registro deixa de valer e a trava volta — por desenho.\n"
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
    # 'medico' é redundante: o signatário vem do hospital. Se vier no JSON e
    # contradisser, é exatamente o caso da troca cruzada — recusa.
    assinante = assinante_de(d.get("hospital"))
    if d.get("medico") and d["medico"] != assinante["chave"]:
        sys.exit(
            f"ERRO: 'medico' diz {d['medico']!r} mas o signatário de "
            f"{d['hospital']} é {assinante['chave']!r} ({assinante['nome']}).\n"
            "  Emitir assim poria a assinatura de um médico num laudo do outro.\n"
            "  Remova o campo 'medico': ele é derivado do hospital.")

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
    if a.assinar:
        if pend_marcadores(d):
            sys.exit("ERRO: este laudo tem [VERIFICAR] ou [RECAPTURAR] — não pode "
                     "ser assinado.\n  Resolva a pendência e gere de novo.")
        exige_assinatura(assinante, d["hospital"])

    parcial = out.with_name(out.name + ".part")
    try:
        for esc in (1.0, 0.90, 0.82):
            ESCALA = esc
            pend, paginas = build(d, parcial, a.base_nao_revisada, a.assinar)
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
           "signatario": assinante["nome"],
           "documento": "final assinado" if a.assinar else "minuta",
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
