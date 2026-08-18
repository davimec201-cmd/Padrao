"""Prepara as ilustrações dos personagens para uso nas capas e blocos.

Entrada: JPG com fundo branco (como vêm do Drive).
Saída:   PNG com fundo transparente, recortado no conteúdo, em assets/ilustracoes/.

O que faz, na ordem:
  1. marca como fundo tudo que é quase-branco e está conectado à borda da imagem
     (fundo interno — barriga do pinguim, peito da coruja — nunca é atingido);
  2. joga fora componentes soltos pequenos, que é o que remove as legendas
     "Pipo" e "Cora" gravadas em algumas imagens;
  3. suaviza a franja branca do JPEG na borda do desenho, dando alfa parcial
     conforme a distância do pixel até o branco puro;
  4. recorta na caixa do conteúdo e grava PNG.

Uso: python3 diagramador/ferramentas/preparar_ilustracoes.py [pasta_de_entrada]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "assets" / "ilustracoes"

# arquivo de origem -> nome canônico do personagem
PERSONAGENS = {
    "f83dfb53-mam_e_urso.jfif.jpg": "mamae_urso",
    "4f18a5c2-Leo_o_le_o.jpg": "leo",
    "775581f3-jojo_raposinha.jfif.jpg": "jojo",
    "8a6f34d9-Cora_a_coruja.jpg": "cora",
    "d1d2246e-Pipo_o_Pinguim.jpg": "pipo",
    "da3d2794-Marcos_o_macaco.jpg": "marcos",
    "dc0b3d8c-prof._canguro.jfif.jpg": "professora_canguru",
    "40d9a555-sr_miau.jfif.jpg": "sr_miau",
}

TOLERANCIA_FUNDO = 30  # distância máxima do branco para contar como fundo
RAMPA_FRANJA = 45  # largura da rampa de alfa na borda do desenho
FRACAO_COMPONENTE = 0.06  # componente menor que isso do maior é legenda/sujeira


def recortar_fundo(caminho: Path) -> Image.Image:
    rgb = np.asarray(Image.open(caminho).convert("RGB")).astype(np.int16)
    altura, largura, _ = rgb.shape

    quase_branco = (255 - rgb.min(axis=2)) <= TOLERANCIA_FUNDO

    # fundo = quase-branco conectado à borda
    rotulos, _ = ndimage.label(quase_branco)
    da_borda = set(rotulos[0, :]) | set(rotulos[-1, :]) | set(rotulos[:, 0]) | set(rotulos[:, -1])
    da_borda.discard(0)
    fundo = np.isin(rotulos, list(da_borda))

    desenho = ~fundo

    # componentes soltos: mantém o maior e os que tiverem tamanho comparável
    rotulos_desenho, quantos = ndimage.label(desenho)
    if quantos > 1:
        areas = ndimage.sum(desenho, rotulos_desenho, range(1, quantos + 1))
        maior = areas.max()
        manter = [i + 1 for i, area in enumerate(areas) if area >= maior * FRACAO_COMPONENTE]
        desenho = np.isin(rotulos_desenho, manter)

    alfa = np.where(desenho, 255, 0).astype(np.int16)

    # franja: pixels de desenho quase-brancos vizinhos do fundo ganham alfa parcial
    vizinho_do_fundo = ndimage.binary_dilation(~desenho, iterations=2) & desenho
    distancia_do_branco = 255 - rgb.min(axis=2)
    parcial = np.clip(distancia_do_branco * 255 // RAMPA_FRANJA, 0, 255)
    alfa = np.where(vizinho_do_fundo, np.minimum(alfa, parcial), alfa)

    rgba = np.dstack([rgb.astype(np.uint8), alfa.astype(np.uint8)])
    imagem = Image.fromarray(rgba, "RGBA")

    caixa = imagem.getbbox()
    return imagem.crop(caixa) if caixa else imagem


def main() -> None:
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if origem is None:
        print("informe a pasta com os JPG de origem", file=sys.stderr)
        raise SystemExit(1)

    DESTINO.mkdir(parents=True, exist_ok=True)
    for arquivo, personagem in PERSONAGENS.items():
        entrada = origem / arquivo
        if not entrada.exists():
            print(f"faltando: {arquivo}")
            continue
        imagem = recortar_fundo(entrada)
        saida = DESTINO / f"{personagem}.png"
        imagem.save(saida, optimize=True)
        print(f"{personagem}: {imagem.size[0]}×{imagem.size[1]}  {saida.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
