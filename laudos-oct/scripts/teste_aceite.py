#!/usr/bin/env python3
"""
teste_aceite.py — os 17 critérios de aceite da rodada de 20/08/2026.

Um teste por critério da devolutiva do formulário, incluindo os negativos: a
troca cruzada de signatário tem de FALHAR, "área da escavação" não pode existir
em lugar nenhum, minuta não pode sair assinada.

    python3 scripts/teste_aceite.py

Roda offline, sem tela e sem AnyDesk. Não cobre o que só a estação confirma
(clique, captura); cobre o que sai no documento e o que o código recusa.
"""

import base64
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PACOTE = AQUI.parent
LAUDO_PDF = AQUI / "laudo_pdf.py"

OK = FALHA = 0
_casa = None


def diz(nome, passou, detalhe=""):
    global OK, FALHA
    if passou:
        OK += 1
        print(f"  \033[32mok\033[0m   {nome}")
    else:
        FALHA += 1
        print(f"  \033[31mFALHA\033[0m {nome}" + (f" — {detalhe}" if detalhe else ""))


def roda(args, casa):
    """Executa o laudo_pdf.py. Devolve (returncode, stdout, stderr)."""
    import os
    env = dict(os.environ, HOME=str(casa))
    p = subprocess.run([sys.executable, str(LAUDO_PDF)] + args,
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


def emite(fixture, casa, extra=()):
    f = casa / "fx.json"
    f.write_text(json.dumps(fixture, ensure_ascii=False), encoding="utf-8")
    return roda(["--json", str(f), "--sobrescrever", *extra], casa)


def texto_do_pdf(caminho):
    d = Path(caminho).read_bytes()
    partes = []
    for b in re.findall(rb"stream\r?\n(.*?)endstream", d, re.S):
        c = b.strip()
        try:
            c = base64.a85decode(c, adobe=True)
        except Exception:
            pass
        try:
            partes.append(zlib.decompress(c).decode("latin-1"))
        except Exception:
            pass
    junto = "\n".join(partes)
    return re.sub(r"[()]", "", " ".join(re.findall(r"\((?:[^()\\]|\\.)*\)", junto)))


def base_nervo(hospital, data, **kw):
    olho = {"area_papila": "2,69 mm2", "rel_esc_papila": "0,52",
            "rel_classificacao": "fora", "escavacao_v": "0,73",
            "escavacao_h": "0,80", "cfn_media": "98",
            "cfn_classificacao": "dentro"}
    d = {"hospital": hospital, "exame": "nervo",
         "paciente": {"nome": "Fulana de Tal", "nascimento": "14/02/1958"},
         "data_exame": data, "olhos": "AO",
         "nervo": {"OD": dict(olho), "OE": dict(olho)},
         "conclusoes": ["AMBOS OS OLHOS com relação escavação/papila (área) fora "
                        "da curva de normalidade e espessura média da camada de "
                        "fibras nervosas dentro da curva de normalidade."],
         "sugestao": "Sugiro correlação clínica e acompanhamento com exames "
                     "periódicos para comparação dos parâmetros."}
    d.update(kw)
    return d


def base_macula(hospital, data, **kw):
    n = "aparentemente dentro da normalidade."
    d = {"hospital": hospital, "exame": "macula",
         "paciente": {"nome": "Beltrana de Tal", "nascimento": "07/05/1966"},
         "data_exame": data, "olhos": "AO",
         "macula": {"OD": {"interface_vitreo_retiniana": n, "camadas_internas": n,
                           "epr_cfr": n},
                    "OE": {"interface_vitreo_retiniana": n, "camadas_internas": n,
                           "epr_cfr": n}},
         "conclusoes": ["AMBOS OS OLHOS com máculas aparentemente dentro da "
                        "normalidade."],
         "sugestao": "Sugiro correlação clínica."}
    d.update(kw)
    return d


def pdf_de(saida):
    return json.loads(saida)["pdf"]


# ---------------------------------------------------------------- os critérios

def main():
    global _casa
    _casa = Path(tempfile.mkdtemp())
    casa = _casa
    print("\n── Signatário derivado do hospital ──")

    rc, out, _ = emite(base_nervo("farroupilha", "22-07-2026"), casa)
    t_far = texto_do_pdf(pdf_de(out)) if rc == 0 else ""
    diz("1. Farroupilha assina Dr. Cassiano Ricardo Goulart",
        "Cassiano Ricardo Goulart" in t_far)
    diz("2. Farroupilha imprime UMA inscrição (CRM-RS 30.544 RQE 25.730)",
        "CRM-RS 30.544 RQE 25.730" in t_far and "CRM-SC" not in t_far)

    rc, out, _ = emite(base_nervo("nova_prata", "9 de julho de 2026"), casa)
    t_np = texto_do_pdf(pdf_de(out)) if rc == 0 else ""
    diz("3. Nova Prata assina Dr Vinícius L Maeta",
        "Vin" in t_np and "cius L Maeta" in t_np)
    diz("4. Nova Prata imprime AS DUAS inscrições, SC antes de RS",
        "CRM-SC 23632 RQE 14403" in t_np and "CRM-RS 40608 RQE 30002" in t_np
        and t_np.index("CRM-SC") < t_np.index("CRM-RS 40608"))
    diz("5. Grafia preservada: 'Dr.' em Farroupilha, 'Dr' em Nova Prata",
        "Dr. Cassiano" in t_far and "Dr Vin" in t_np)

    # NEGATIVO: troca cruzada
    rc, _, err = emite(base_nervo("farroupilha", "22-07-2026", medico="maeta"), casa)
    diz("6. NEGATIVO: Farroupilha com 'medico: maeta' é RECUSADO",
        rc != 0 and "signat" in err.lower(), err.strip()[:60])
    rc, _, err = emite(base_nervo("nova_prata", "9 de julho de 2026",
                                  medico="cassiano"), casa)
    diz("7. NEGATIVO: Nova Prata com 'medico: cassiano' é RECUSADO", rc != 0)
    d = base_nervo("farroupilha", "22-07-2026"); d.pop("hospital")
    rc, _, err = emite(d, casa)
    diz("8. NEGATIVO: hospital indefinido é RECUSADO", rc != 0)

    print("\n── Decisões clínicas ──")
    diz("9. Reserva diagnóstica presente no laudo de NERVO (Farroupilha)",
        "achados estruturais isoladamente" in t_far)
    diz("10. Reserva diagnóstica presente no laudo de NERVO (Nova Prata)",
        "achados estruturais isoladamente" in t_np)
    rc, out, _ = emite(base_macula("farroupilha", "22-07-2026"), casa)
    t_mac = texto_do_pdf(pdf_de(out)) if rc == 0 else ""
    diz("11. Reserva diagnóstica AUSENTE no laudo de MÁCULA",
        "achados estruturais isoladamente" not in t_mac)

    ref = (PACOTE / "references").rglob("*.md")
    corpo = "\n".join(f.read_text(encoding="utf-8") for f in ref
                      if "_fonte" not in str(f) and "/base/" not in str(f))
    assets = "\n".join(f.read_text(encoding="utf-8")
                       for f in (PACOTE / "assets").glob("*.json"))
    codigo = LAUDO_PDF.read_text(encoding="utf-8")

    diz("12. Nenhuma ocorrência de 'área da escavação' na biblioteca",
        "área da escavação" not in assets
        and corpo.count("área da escavação") == corpo.count(
            '"área da escavação"'))   # só as menções entre aspas, que a explicam
    diz("13. Mácula unificada em 'aparentemente dentro da normalidade'",
        not re.search(r"(?<!aparentemente )dentro da normalidade\.", assets))

    print("\n── Cores e qualidade ──")
    diz("14. Nenhuma categoria 'limitrofe' aceita pelo código",
        "limitrofe" not in codigo.replace("`\"limitrofe\"`", ""))
    diz("15. Nenhum campo de índice de qualidade no schema",
        '"qualidade"' not in codigo)
    diz("16. Nenhum limiar numérico de qualidade",
        not re.search(r"qualidade\s*[<>]=?\s*\d", codigo))
    frase = "impossível avaliar detalhes por possível artefato ou opacidade de meios"
    diz("17. Frase de qualidade aprovada está na biblioteca", frase in corpo)

    print("\n── Sugestões: as três ficam, as duas saem ──")
    for s in ("Sugiro correlação clínica.",
              "Sugiro correlação clínica e acompanhamento com exames periódicos",
              "Sugiro correlação clínica para indicação de tratamento."):
        diz(f"18. Preservada: {s[:46]}…", s in corpo)
    for s in ("aferição da pressão intraocular e campimetria",
              "Sugiro repetição do exame para adequada"):
        # podem aparecer só na lista do que foi REMOVIDO (riscada com ~~)
        vivas = [l for l in corpo.splitlines() if s in l and "~~" not in l]
        diz(f"19. NEGATIVO: removida: {s[:40]}…", not vivas, str(vivas[:1])[:70])

    print("\n── Nervo inteiramente dentro da curva ──")
    d = base_nervo("farroupilha", "01-08-2026")
    for o in d["nervo"].values():
        o["rel_classificacao"] = "dentro"
    d["conclusoes"] = []
    rc, out, _ = emite(d, casa)
    t_norm = texto_do_pdf(pdf_de(out)) if rc == 0 else ""
    diz("20. Nervo todo dentro EMITE mesmo com conclusões vazias", rc == 0)
    diz("21. E sinaliza que a conclusão é do médico",
        "conclus" in t_norm and "do m" in t_norm and "dico respons" in t_norm)
    d2 = base_macula("farroupilha", "02-08-2026"); d2["conclusoes"] = []
    rc, _, err = emite(d2, casa)
    diz("22. NEGATIVO: mácula sem conclusão continua sendo RECUSADA", rc != 0)

    print("\n── Nascimento e datas ──")
    diz("23. Nova Prata imprime 'Data de nascimento' quando existe",
        "Data de nascimento" in t_np)
    d = base_nervo("nova_prata", "9 de julho de 2026")
    d["paciente"].pop("nascimento")
    rc, out, _ = emite(d, casa)
    t_sem = texto_do_pdf(pdf_de(out)) if rc == 0 else ""
    diz("24. Nova Prata NÃO imprime rótulo vazio quando não existe",
        "Data de nascimento" not in t_sem)
    diz("25. Farroupilha usa rótulos em caixa alta", "DATA DO EXAME" in t_far)

    print("\n── Os quatro parâmetros do nervo ──")
    for i, p in enumerate(["rea da papila", "rela", "escava", "camada de fibras nervosas"], 1):
        diz(f"26.{i} parâmetro presente: {p}", p in t_far)
    diz("27. 'mm2' sem expoente e vírgula decimal", "mm2" in t_far and "2,69" in t_far)
    diz("28. CFN sem unidade (nenhum µm no documento)", "µm" not in t_far)

    print("\n── Minuta, assinatura e travas ──")
    diz("29. Minuta sai carimbada MINUTA", "MINUTA" in t_far)
    rc, out, _ = emite(base_nervo("farroupilha", "22-07-2026"), casa)
    diz("30. Minuta NUNCA vem assinada",
        json.loads(out)["documento"] == "minuta")
    rc, _, err = emite(base_nervo("farroupilha", "22-07-2026"), casa, ("--assinar",))
    diz("31. NEGATIVO: --assinar sem a imagem RECUSA e diz o que falta",
        rc != 0 and "IMAGEM DE ASSINATURA" in err, err.strip()[:60])
    diz("32. Assinatura é lida de fora do pacote (~/.laudos_oct/assinaturas)",
        "DIR_ASSINATURAS" in codigo and ".laudos_oct" in codigo
        and "assinaturas" in codigo)

    print("\n── Trava da base: liberada, e volta sozinha ──")
    spec = importlib.util.spec_from_file_location("lp", LAUDO_PDF)
    lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
    revisada, versao, revisor = lp.estado_da_base()
    diz("33. Base liberada com registro (revisor e data)",
        revisada is True and "Maeta" in revisor and "20/08/2026" in revisor,
        f"{versao} | {revisor}")
    diz("34. A checagem continua no código", "estado_da_base" in codigo
        and "hash_da_base" in codigo)

    alvo = PACOTE / "references" / "base" / "01-vocabulario.md"
    original = alvo.read_bytes()
    try:
        alvo.write_bytes(original + b"\n<!-- alteracao de teste -->\n")
        importlib.reload(lp) if False else None
        spec2 = importlib.util.spec_from_file_location("lp2", LAUDO_PDF)
        lp2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(lp2)
        revisada2, _, _ = lp2.estado_da_base()
        diz("35. Base ALTERADA depois da revisão: a trava VOLTA sozinha",
            revisada2 is False)
        rc, _, err = emite(base_nervo("farroupilha", "22-07-2026"), casa)
        diz("36. E a emissão volta a ser recusada", rc != 0)
    finally:
        alvo.write_bytes(original)

    spec3 = importlib.util.spec_from_file_location("lp3", LAUDO_PDF)
    lp3 = importlib.util.module_from_spec(spec3); spec3.loader.exec_module(lp3)
    diz("37. Restaurada a base, a trava volta a ficar satisfeita",
        lp3.estado_da_base()[0] is True)

    print(f"\n{OK} passaram, {FALHA} falharam")
    return 1 if FALHA else 0


if __name__ == "__main__":
    sys.exit(main())
