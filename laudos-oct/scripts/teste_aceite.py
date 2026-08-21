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


def carrega(caminho, nome):
    """Importa um laudo_pdf.py — o do pacote ou o de uma cópia — sob outro nome."""
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


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
         # A extração é exigida: o que sai impresso tem de ser o que foi lido.
         "extracao": {"OD": dict(olho), "OE": dict(olho)},
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
         "extracao": {"OD": {"interface_vitreo_retiniana": n, "camadas_internas": n,
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
    # A extração acompanha: mudar o laudo sem mudar o que foi lido é justamente
    # a deriva que o gerador passou a recusar.
    for bloco in (d["nervo"], d["extracao"]):
        for o in bloco.values():
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

    print("\n── Documento final assinado ──")
    # O teste 31 só cobria o caso SEM a imagem. Com ela presente, o caminho
    # quebrava com TypeError nos dois templates: --assinar nunca tinha produzido
    # documento nenhum, e a falta das imagens escondia isso atrás da recusa.
    # A imagem abaixo é um PNG sintético em branco — não é assinatura de ninguém.
    assin_dir = casa / ".laudos_oct" / "assinaturas"
    assin_dir.mkdir(parents=True, exist_ok=True)
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAAAOklEQVR4nO3BMQEAAADCoPVP"
        "bQwfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgbYw4AAdX3xh8AAAAA"
        "SUVORK5CYII=")
    for arq in ("assinatura_cassiano.png", "assinatura_maeta.png"):
        (assin_dir / arq).write_bytes(png)

    # Assinar exige, ALÉM da imagem, a autorização do médico — uso único.
    bilhete = casa / ".laudos_oct" / "PERMITIR_ASSINATURA"
    bilhete.unlink(missing_ok=True)
    fx = base_nervo("nova_prata", "28-07-2026")
    fx["paciente"]["nome"] = "Sem Autorizacao Teste"
    rc, _, err = emite(fx, casa, ("--assinar",))
    diz("48b. NEGATIVO: --assinar sem a autorização do médico é RECUSADO",
        rc != 0 and "autoriza" in err.lower(), err.strip()[:80])

    for hosp, quem in (("farroupilha", "Cassiano"), ("nova_prata", "Maeta")):
        bilhete.write_text("autorizado pelo medico")
        fx = base_nervo(hosp, "28-07-2026")
        fx["paciente"]["nome"] = f"Assinado Teste {quem}"
        rc, out, err = emite(fx, casa, ("--assinar",))
        diz(f"49. --assinar COM a imagem emite ({hosp})", rc == 0,
            err.strip()[:90])
        if rc != 0:
            continue
        r = json.loads(out)
        diz(f"50. E sai como documento final, não minuta ({hosp})",
            r["documento"] == "final assinado", r["documento"])
        t = texto_do_pdf(r["pdf"])
        diz(f"51. O carimbo de MINUTA some do documento assinado ({hosp})",
            "MINUTA" not in t)
        diz(f"52. O signatário do hospital continua impresso ({hosp})",
            quem in t or quem.upper() in t.upper())
        diz(f"53. E a autorização foi CONSUMIDA ({hosp})", not bilhete.exists())

    for arq in ("assinatura_cassiano.png", "assinatura_maeta.png"):
        (assin_dir / arq).unlink()

    print("\n── Trava da base: liberada, e volta sozinha ──")
    spec = importlib.util.spec_from_file_location("lp", LAUDO_PDF)
    lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
    revisada, versao, revisor = lp.estado_da_base()
    diz("33. Base liberada com registro (revisor e data)",
        revisada is True and "Maeta" in revisor and "20/08/2026" in revisor,
        f"{versao} | {revisor}")
    diz("34. A checagem continua no código", "estado_da_base" in codigo
        and "hash_da_base" in codigo)

    # A base do PACOTE INSTALADO não é tocada. Antes o teste escrevia em
    # references/base/01-vocabulario.md e restaurava no finally: uma interrupção
    # no meio (Ctrl+C, queda de energia, o processo morto) deixava a base selada
    # alterada e a estação incapaz de emitir, por um motivo que ninguém ligaria
    # ao teste. Aqui a base é COPIADA para um temporário e a cópia é mutilada.
    import shutil
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "pacote"
        shutil.copytree(PACOTE, copia, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".git"))
        lp2 = carrega(copia / "scripts" / "laudo_pdf.py", "lp2")
        diz("35a. A cópia da base começa com a trava satisfeita",
            lp2.estado_da_base()[0] is True)

        alvo = copia / "references" / "base" / "01-vocabulario.md"
        alvo.write_bytes(alvo.read_bytes() + b"\n<!-- alteracao de teste -->\n")
        lp3 = carrega(copia / "scripts" / "laudo_pdf.py", "lp3")
        diz("35. Base ALTERADA depois da revisão: a trava VOLTA sozinha",
            lp3.estado_da_base()[0] is False)

        f = casa / "fx_base.json"
        f.write_text(json.dumps(base_nervo("farroupilha", "22-07-2026"),
                                ensure_ascii=False), encoding="utf-8")
        import os
        pr = subprocess.run([sys.executable, str(copia / "scripts" / "laudo_pdf.py"),
                             "--json", str(f), "--sobrescrever"],
                            capture_output=True, text=True,
                            env=dict(os.environ, HOME=str(casa)))
        diz("36. E a emissão volta a ser recusada",
            pr.returncode != 0 and "base científica não liberada" in pr.stderr,
            pr.stderr.strip()[:70])

    diz("37. A base do pacote instalado NÃO foi tocada pelo teste",
        carrega(LAUDO_PDF, "lp4").estado_da_base()[0] is True)

    print("\n── Lateralidade ponta a ponta ──")
    # Todas as fixtures usavam olhos "AO": mutar OLHOS_OK para normalizar OD como
    # OE deixava as duas suítes verdes. Inversão de lateralidade num laudo que um
    # CRM assina é o erro mais caro possível, e 101 asserções não o pegavam.
    mono = base_nervo("nova_prata", "22-07-2026")
    mono["olhos"] = "OD"
    mono["nervo"].pop("OE", None)
    rc, out, err = emite(mono, casa)
    diz("38. Exame monocular OD emite", rc == 0, err.strip()[:70])
    if rc == 0:
        pdf = json.loads(out)["pdf"]
        diz("39. O nome do arquivo traz _OD_", "_OD_" in Path(pdf).name,
            Path(pdf).name)
        t_od = texto_do_pdf(pdf)
        diz("40. O corpo diz OLHO DIREITO", "OLHO DIREITO" in t_od)
        diz("41. E NÃO diz OLHO ESQUERDO", "OLHO ESQUERDO" not in t_od)

    cruzado = base_nervo("nova_prata", "23-07-2026")
    cruzado["olhos"] = "OD"                       # declara OD, mas há dados de AO
    rc, _, err = emite(cruzado, casa)
    diz("42. NEGATIVO: 'olhos' OD com dados dos dois olhos é RECUSADO",
        rc != 0 and "olhos" in err, err.strip()[:70])

    print("\n── Campo clínico descartado e classificação fora da lista ──")
    obs = base_nervo("farroupilha", "24-07-2026")
    obs["observacoes"] = ("LIMITACAO TECNICA: opacidade de meios impediu avaliar "
                          "o setor inferior.")
    rc, _, err = emite(obs, casa)
    diz("43. NEGATIVO: 'observacoes' na RAIZ é recusado, não descartado calado",
        rc != 0 and "observacoes" in err, err.strip()[:70])

    for valor in ("limítrofe", "borderline (p<5%)"):
        lim = base_nervo("farroupilha", "25-07-2026")
        lim["nervo"]["OD"]["rel_classificacao"] = valor
        rc, _, err = emite(lim, casa)
        diz(f"44. NEGATIVO: classificação {valor!r} é RECUSADA",
            rc != 0 and "classifica" in err.lower(), err.strip()[:70])

    print("\n── Procedência: o impresso é o que foi lido ──")
    sem_ex = base_nervo("nova_prata", "29-07-2026")
    sem_ex.pop("extracao")
    rc, _, err = emite(sem_ex, casa)
    diz("54. NEGATIVO: laudo sem 'extracao' é RECUSADO",
        rc != 0 and "extracao" in err, err.strip()[:70])

    derivado = base_nervo("nova_prata", "30-07-2026")
    derivado["nervo"]["OD"]["cfn_media"] = "89"        # o laudo diz 89...
    # ...e a extração continua dizendo 98: transcrição divergente.
    rc, _, err = emite(derivado, casa)
    diz("55. NEGATIVO: valor impresso diferente do lido é RECUSADO",
        rc != 0 and "extração diz" in err, err.strip()[:90])

    faltando = base_nervo("nova_prata", "31-07-2026")
    faltando["extracao"]["OE"].pop("cfn_media")
    rc, _, err = emite(faltando, casa)
    diz("56. NEGATIVO: campo impresso sem leitura registrada é RECUSADO",
        rc != 0 and "sem leitura registrada" in err, err.strip()[:90])

    print("\n── Caminho de saída no limite do Windows ──")
    # MAX_COMPONENTE limitava CADA pedaço, não o caminho inteiro — e o nome do
    # paciente entra duas vezes, na pasta e no arquivo. Com nome longo e usuário
    # de nome longo dava 298 caracteres, acima do MAX_PATH de 260: a gravação
    # falharia DEPOIS do laudo redigido.
    lp5 = carrega(LAUDO_PDF, "lp5")
    raiz_win = Path("C:/Users/maria.fernanda.rodrigues/Laudos_OCT/Nova_Prata")
    molde = "Laudo_NOVA_PRATA_{n}_NO_AO_9_de_setembro_de_2026.pdf"
    import ntpath
    for nome in ("X" * 96, "Y" * 300, "Fulana de Tal"):
        curto, caminho = lp5.encurta_para_caber(raiz_win, lp5.slug(nome), molde)
        n = len(ntpath.join(*caminho.parts))
        diz(f"57. Caminho cabe no MAX_PATH com nome de {len(nome)} letras",
            n <= lp5.MAX_CAMINHO, f"{n} caracteres")

    a = lp5.slug("Ana Beatriz Rodrigues " + "A" * 90)
    b = lp5.slug("Ana Beatriz Rodrigues " + "B" * 90)
    ca, _ = lp5.encurta_para_caber(raiz_win, a, molde)
    cb, _ = lp5.encurta_para_caber(raiz_win, b, molde)
    diz("58. Nomes longos que começam igual NÃO colidem depois do corte",
        ca != cb, f"{ca[-12:]} vs {cb[-12:]}")

    longo = base_nervo("nova_prata", "01-09-2026")
    longo["paciente"]["nome"] = "Maria Fernanda " * 14
    rc, out, err = emite(longo, casa)
    diz("59. E o laudo com nome longo emite de verdade", rc == 0, err.strip()[:70])
    if rc == 0:
        pdf = Path(json.loads(out)["pdf"])
        diz("60. O PDF existe no caminho encurtado", pdf.exists(), str(pdf)[-50:])

    print("\n── Registro da fila ──")
    # O laço do lote é prosa e a memória do agente é descartada entre pacientes:
    # sem registro em disco, o exame interrompido some sem ninguém saber.
    import os
    env = dict(os.environ, HOME=str(casa))
    subprocess.run([sys.executable, str(LAUDO_PDF), "--fila", "abrir",
                    "--hospital", "nova_prata", "--paciente", "Interrompida Teste",
                    "--data", "26-07-2026", "--exame", "nervo"],
                   capture_output=True, text=True, env=env)
    pr = subprocess.run([sys.executable, str(LAUDO_PDF), "--fila", "relatorio"],
                        capture_output=True, text=True, env=env)
    rel = json.loads(pr.stdout)
    diz("45. Exame aberto e nunca concluído aparece no relatório",
        len(rel["abertos_sem_desfecho"]) == 1, json.dumps(rel["abertos_sem_desfecho"]))
    diz("46. E o relatório vem do DISCO, não da memória do agente",
        "_FILA" in rel["arquivo"], rel["arquivo"])

    emitido = base_nervo("nova_prata", "27-07-2026")
    emitido["paciente"]["nome"] = "Concluida Teste"
    rc, out, _ = emite(emitido, casa)
    pr = subprocess.run([sys.executable, str(LAUDO_PDF), "--fila", "relatorio"],
                        capture_output=True, text=True, env=env)
    rel = json.loads(pr.stdout)
    # Cada emissão desta suíte também entra no registro — é o comportamento
    # certo. O que se afere é a chave DESTE exame, não a contagem total.
    chaves = {i["chave"] for i in rel["emitidos"]}
    diz("47. Exame emitido entra no registro com desfecho",
        any("Concluida_Teste" in k for k in chaves), sorted(chaves)[:3])
    diz("48. E o aberto sem desfecho continua listado como tal",
        any("Interrompida_Teste" in i["chave"] for i in rel["abertos_sem_desfecho"]),
        json.dumps(rel["abertos_sem_desfecho"]))

    print(f"\n{OK} passaram, {FALHA} falharam")
    return 1 if FALHA else 0


if __name__ == "__main__":
    sys.exit(main())
