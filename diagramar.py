#!/usr/bin/env python3
"""Ponto de entrada do diagramador.

Este arquivo é idêntico no repositório e dentro da skill: nos dois lugares ele
tem uma pasta `diagramador/` ao lado, e é de lá que o código vem. Por isso o
mesmo comando funciona nos dois:

    python3 diagramar.py material.md --trechos
    python3 diagramar.py material.md --classificacao classificacao.json
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "diagramador"))

from app.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
