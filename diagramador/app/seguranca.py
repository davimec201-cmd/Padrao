"""Senha simples e cookie assinado. O app não fica aberto na internet.

Sem banco, sem usuário: uma senha só, lida de `SENHA_APP`. O cookie é um HMAC
com validade, assinado por `CHAVE_SESSAO` (ou por uma chave sorteada na subida,
o que faz todo mundo relogar quando o serviço reinicia).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time

COOKIE = "diagramador_sessao"
VALIDADE_EM_SEGUNDOS = 60 * 60 * 24 * 14  # duas semanas: é um tablet pessoal


def _chave() -> bytes:
    return (os.environ.get("CHAVE_SESSAO") or _CHAVE_DA_SUBIDA).encode()


_CHAVE_DA_SUBIDA = secrets.token_hex(32)


def senha_configurada() -> str:
    return os.environ.get("SENHA_APP", "")


def senha_correta(tentativa: str) -> bool:
    esperada = senha_configurada()
    if not esperada:
        # sem SENHA_APP o app não abre: é melhor travar do que ficar exposto
        return False
    return hmac.compare_digest(tentativa.strip(), esperada)


def assinar() -> str:
    validade = str(int(time.time()) + VALIDADE_EM_SEGUNDOS)
    marca = hmac.new(_chave(), validade.encode(), hashlib.sha256).hexdigest()
    return f"{validade}.{marca}"


def valido(cookie: str | None) -> bool:
    if not cookie or "." not in cookie:
        return False
    validade, _, marca = cookie.partition(".")
    esperada = hmac.new(_chave(), validade.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(marca, esperada):
        return False
    try:
        return int(validade) > time.time()
    except ValueError:
        return False
