#!/usr/bin/env python3
"""
preparar_assinatura.py — transforma o escaneado da assinatura no PNG que o laudo usa.

    python3 preparar_assinatura.py maeta ~/Desktop/assinatura_maeta.jpg
    python3 preparar_assinatura.py cassiano ~/Desktop/scan.png --ver

Faz o que PENDENCIAS.md descreve à mão: recorta rente ao traço, tira o fundo
branco (que sairia como um retângulo por cima da linha do documento), converte
para PNG-24 com canal alfa e grava em ~/.laudos_oct/assinaturas/.

**Rode isto NA MÁQUINA DO MÉDICO, com o arquivo original ali.** A imagem de
assinatura não passa por repositório, por pasta sincronizada nem por mensagem:
quem a tem, assina. Este script existe para que ela vá do escâner ao destino
final sem escala em lugar nenhum.
"""

import argparse
import sys
from pathlib import Path

DESTINO = Path.home() / ".laudos_oct" / "assinaturas"
# As chaves são as de ASSINANTES em laudo_pdf.py. Nome de arquivo errado = o
# gerador não acha a imagem e recusa o documento final, dizendo o que falta.
CHAVES = {"maeta": "assinatura_maeta", "cassiano": "assinatura_cassiano"}
LARGURA_MINIMA = 1200        # abaixo disto o traço serrilha no tamanho impresso
LIMIAR_FUNDO = 235           # acima deste cinza é papel, não tinta


def prepara(origem, saida, limiar=LIMIAR_FUNDO, margem=8):
    try:
        from PIL import Image
    except ImportError:
        sys.exit("ERRO: falta a biblioteca pillow.\n"
                 "  python3 -m pip install --user pillow")

    im = Image.open(origem).convert("RGBA")
    px = im.load()
    larg, alt = im.size

    # Papel -> transparente, com transição suave: um corte seco deixa o traço
    # serrilhado, porque a borda da caneta é um degradê de cinza.
    for y in range(alt):
        for x in range(larg):
            r, g, b, _ = px[x, y]
            claro = max(r, g, b)
            if claro >= limiar:
                px[x, y] = (r, g, b, 0)
            elif claro > limiar - 60:
                # quanto mais claro, mais transparente
                px[x, y] = (r, g, b, int(255 * (limiar - claro) / 60))

    # Recorte rente ao traço, com uma margem de folga.
    caixa = im.getbbox()
    if caixa is None:
        sys.exit(f"ERRO: {Path(origem).name} ficou inteiramente transparente.\n"
                 f"  Nenhum pixel mais escuro que {limiar} — a imagem está clara "
                 "demais, ou é papel em branco.\n"
                 "  Tente --limiar mais alto (ex.: --limiar 250).")
    x0, y0, x1, y1 = caixa
    caixa = (max(0, x0 - margem), max(0, y0 - margem),
             min(larg, x1 + margem), min(alt, y1 + margem))
    im = im.crop(caixa)

    avisos = []
    if im.width < LARGURA_MINIMA:
        avisos.append(
            f"largura de {im.width} px, abaixo dos {LARGURA_MINIMA} px "
            "recomendados — o traço vai serrilhar no tamanho impresso (~50 mm). "
            "Digitalize a 600 dpi se puder.")
    proporcao = im.width / im.height if im.height else 0
    if not (1.5 <= proporcao <= 8):
        avisos.append(
            f"proporção {proporcao:.1f}:1 fora do usual para assinatura "
            "(entre 1,5:1 e 8:1). Confira se o recorte pegou só o traço.")

    saida.parent.mkdir(parents=True, exist_ok=True)
    im.save(saida, "PNG")
    try:                                   # mesma restrição do resto do fluxo
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import plataforma as _plat
        if _plat.PLAT is not None:
            _plat.PLAT.restringir(saida.parent)
            _plat.PLAT.restringir(saida)
    except Exception:
        pass
    return im, avisos


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quem", choices=sorted(CHAVES),
                    help="de quem é a assinatura")
    ap.add_argument("imagem", help="o escaneado (JPG, PNG, o que o escâner deu)")
    ap.add_argument("--limiar", type=int, default=LIMIAR_FUNDO,
                    help=f"acima deste cinza é fundo (padrão {LIMIAR_FUNDO}). "
                         "Suba se sobrar fundo; desça se o traço sumir.")
    ap.add_argument("--ver", action="store_true",
                    help="grava também um _conferir.png com xadrez atrás, para "
                         "você ver o que ficou transparente")
    a = ap.parse_args()

    origem = Path(a.imagem).expanduser()
    if not origem.exists():
        sys.exit(f"ERRO: não achei {origem}")
    saida = DESTINO / (CHAVES[a.quem] + ".png")
    if saida.exists():
        print(f"AVISO: {saida} já existe e vai ser substituída.", file=sys.stderr)

    im, avisos = prepara(origem, saida, a.limiar)
    print(f"gravado: {saida}")
    print(f"  {im.width} x {im.height} px, PNG-24 com canal alfa")
    for av in avisos:
        print(f"AVISO: {av}", file=sys.stderr)

    if a.ver:
        from PIL import Image
        xadrez = Image.new("RGBA", im.size, (255, 255, 255, 255))
        lado = 16
        for y in range(0, im.height, lado):
            for x in range(0, im.width, lado):
                if (x // lado + y // lado) % 2:
                    for yy in range(y, min(y + lado, im.height)):
                        for xx in range(x, min(x + lado, im.width)):
                            xadrez.putpixel((xx, yy), (205, 205, 205, 255))
        xadrez.alpha_composite(im)
        conf = saida.with_name(saida.stem + "_conferir.png")
        xadrez.save(conf, "PNG")
        print(f"  conferência: {conf}")
        print("  Abra: onde houver xadrez cinza é transparente. Se o xadrez "
              "sumiu atrás de um bloco branco, suba o --limiar.")

    print("\nConfira o resultado emitindo um laudo final de teste:")
    print("  touch ~/.laudos_oct/PERMITIR_ASSINATURA")
    print("  python3 ~/.claude/skills/laudos-oct/scripts/laudo_pdf.py \\")
    print(f"    --json <um laudo de {a.quem}>.json --assinar --sobrescrever")


if __name__ == "__main__":
    main()
