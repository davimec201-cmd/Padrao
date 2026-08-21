#!/usr/bin/env python3
"""
dividir_guia.py — parte a base científica em arquivos por seção.

Motivo: o guia inteiro custa ~7 mil tokens. Numa fila de 20 pacientes, lido
uma vez por paciente, são 140 mil tokens só de guia. Partido por seção, o
agente lê apenas o trecho do exame que está laudando (~1 mil tokens).

    python3 scripts/dividir_guia.py                    # usa references/_fonte/base-cientifica.md
    python3 scripts/dividir_guia.py --guia caminho.md

Gera references/base/NN-nome.md + 00-indice.md, e reporta o ganho.
"""

import argparse, os, re, shutil, sys, tempfile, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
DESTINO = AQUI / "references" / "base"

# título da seção -> nome do arquivo e quando ler
MAPA = [
    ("vocabul",   "01-vocabulario.md", "sempre, ao redigir qualquer laudo"),
    ("nervo",     "02-nervo.md",       "laudo de nervo óptico"),
    ("mácula",    "03-macula.md",      "laudo de mácula"),
    ("macula",    "03-macula.md",      "laudo de mácula"),
    ("artefat",   "04-artefatos.md",   "imagem duvidosa, antes de escalar"),
    ("aparelh",   "05-aparelhos.md",   "rótulo na tela não bate com o esperado"),
    ("referên",   "06-referencias.md", "só quando o médico for conferir a fonte"),
    ("lacuna",    "07-lacunas.md",     "para responder 'não disponível na base'"),
]


def chave(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


# seções do guia que o split descarta: o índice gerado substitui o original
DESCARTAR = ("indice", "index", "sumario")


def destino_de(titulo):
    k = chave(titulo)
    if any(d in k for d in DESCARTAR):
        return None, None
    for gatilho, arquivo, quando in MAPA:
        if chave(gatilho) in k:
            return arquivo, quando
    slug = re.sub(r"[^a-z0-9]+", "-", chave(titulo)).strip("-")[:32] or "extra"
    return f"99-{slug}.md", "seção não prevista no mapa"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guia", default=str(AQUI / "references" / "_fonte" / "base-cientifica.md"))
    a = ap.parse_args()
    src = Path(a.guia)
    if not src.exists():
        sys.exit(f"ERRO: não achei {src}")

    linhas = src.read_text(encoding="utf-8").splitlines(True)

    # cabeçalho: tudo antes do primeiro "## " (versão, advertências, índice)
    ini = next((i for i, l in enumerate(linhas) if l.startswith("## ")), len(linhas))
    versao = next((l.strip() for l in linhas[:ini] if l.strip().startswith("VERSÃO:")), "VERSÃO: ?")
    revisor = next((l.strip() for l in linhas[:ini] if l.strip().startswith("REVISADO POR:")),
                   "REVISADO POR: ?")

    # corta por "## "
    secoes, atual, titulo = [], [], None
    for l in linhas[ini:]:
        if l.startswith("## "):
            if titulo is not None:
                secoes.append((titulo, "".join(atual)))
            titulo, atual = l[3:].strip(), [l]
        else:
            atual.append(l)
    if titulo is not None:
        secoes.append((titulo, "".join(atual)))

    if not secoes:
        sys.exit("ERRO: nenhuma seção '## ' encontrada. O guia precisa de títulos de nível 2.")

    # Monta TUDO num diretório temporário antes de tocar em references/base/.
    # Antes o script apagava base/*.md e só depois escrevia: uma falha no meio
    # deixava a base vazia — e base vazia é justamente o estado que o laudo_pdf.py
    # não distinguia de "base ausente, siga em frente".
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(dir=str(DESTINO.parent), prefix=".base-novo-"))

    escritos, indice = {}, []
    for titulo, corpo in secoes:
        arq, quando = destino_de(titulo)
        if arq is None:
            continue                      # índice original descartado
        escritos.setdefault(arq, [])
        escritos[arq].append(corpo)
        indice.append((arq, titulo, quando))

    if not escritos:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit("ERRO: nenhuma seção mapeada. A base atual foi preservada.")

    for arq, partes in escritos.items():
        texto = (f"<!-- Gerado por dividir_guia.py a partir de {src.name}. "
                 f"Não edite aqui: edite o guia e rode o script de novo. -->\n"
                 f"<!-- {versao} | {revisor} -->\n\n" + "\n".join(partes))
        (tmp / arq).write_text(texto, encoding="utf-8")

    vistos, linhas_idx = set(), []
    for arq, titulo, quando in indice:
        if arq in vistos:
            continue
        vistos.add(arq)
        n = len((tmp / arq).read_text().splitlines())
        linhas_idx.append(f"| `base/{arq}` | {titulo} | {quando} | {n} |")

    (tmp / "00-indice.md").write_text(
        "# Base científica — índice\n\n"
        f"`{versao}`  ·  `{revisor}`\n\n"
        "**Leia apenas o arquivo da seção que você precisa.** Carregar a base inteira "
        "no meio de uma fila de pacientes desperdiça token sem ganho nenhum.\n\n"
        "| Arquivo | Seção | Quando ler | Linhas |\n|---|---|---|---|\n"
        + "\n".join(linhas_idx) + "\n\n"
        "## Precedência (repetida aqui de propósito)\n\n"
        "1. **Tela do aparelho** manda em valor e classificação de normalidade.\n"
        "2. **`templates-hospitais.md`** manda em formato, unidade e redação.\n"
        "3. **Esta base** manda em vocabulário e em como descrever.\n\n"
        "Campo `[PREENCHER]` ou `[MEDIR]` na base = **dado não disponível**. Responda "
        "\"não disponível na base científica\" e nunca complete por inferência.\n",
        encoding="utf-8")

    # O que NÃO é gerado por este script viaja junto para a base nova. A troca é
    # de diretório inteiro: sem isto, o REVISAO.json — o registro de quem revisou
    # a base, quando, e sobre qual hash — era APAGADO justamente pelo comando que
    # a documentação manda rodar depois de editar o guia. Perder o registro não é
    # só perder história: é perder a única prova de que houve revisão médica.
    preservados = []
    if DESTINO.exists():
        for f in DESTINO.iterdir():
            if f.is_file() and f.suffix != ".md":
                shutil.copy2(f, tmp / f.name)
                preservados.append(f.name)

    # Só agora a base antiga sai de cena, e a troca é atômica por arquivo.
    antiga = DESTINO.with_name(DESTINO.name + ".anterior")
    shutil.rmtree(antiga, ignore_errors=True)
    if DESTINO.exists():
        os.replace(DESTINO, antiga)
    os.replace(tmp, DESTINO)
    shutil.rmtree(antiga, ignore_errors=True)

    total = len(src.read_text().splitlines())
    maior = max(len((DESTINO / a).read_text().splitlines()) for a in escritos)
    print(f"guia: {total} linhas -> {len(escritos)} seções + índice")
    print(f"maior seção: {maior} linhas  ({100 - round(maior / total * 100)}% menos "
          f"que ler o guia inteiro)")
    for arq in sorted(escritos):
        print(f"  base/{arq:22s} {len((DESTINO/arq).read_text().splitlines()):>4} linhas")
    if preservados:
        print(f"preservados (não gerados aqui): {', '.join(sorted(preservados))}")
    print("\nATENÇÃO: a base mudou, então o hash mudou e o registro de revisão\n"
          "deixou de casar — a emissão está TRAVADA, por desenho. Quem destrava é\n"
          "a revisão médica do conteúdo novo, regravando references/base/REVISAO.json\n"
          "com o revisor, a data e o hash atual. Não edite o hash à mão.")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # saída cortada por '| head' — não é erro, não polui com traceback
        try:
            sys.stdout.close()
        except Exception:
            pass
