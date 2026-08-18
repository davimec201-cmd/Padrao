"""App web do diagramador. Uma página, feita para o navegador do tablet.

Fluxo: subir o markdown (ou colar), preencher nome e CRP, gerar, olhar o
resultado, baixar. Sem parada no meio: quem acompanha o progresso é a barra.

Correção de exceção: na miniatura da página, trocar o tipo de bloco e regerar.
Nada de editar JSON.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

from . import seguranca
from .catalogo import Bloco, escolhiveis
from .pipeline import Entrega, gerar
from .renderizador import TOKENS

SUPERVISAO = TOKENS["regras_do_material"]["supervisao_tecnica"]

RAIZ = Path(__file__).resolve().parents[2]
ESTATICO = Path(__file__).resolve().parent / "estatico"
EXEMPLO = RAIZ / "exemplo" / "porto_seguro.md"
FORMATO = RAIZ / "FORMATO.md"

LIMITE_DE_ARQUIVO = 2 * 1024 * 1024  # markdown de e-book não chega perto disso
VALIDADE_DO_TRABALHO = 60 * 60 * 6

app = FastAPI(title="Diagramador de e-books — TEA Formation", docs_url=None, redoc_url=None)


# ---------------------------------------------------------------- trabalhos


@dataclass
class Trabalho:
    identificador: str
    fonte: str
    psicologa: str
    crp: str
    criado_em: float = field(default_factory=time.time)
    etapa: str = "na fila"
    fracao: float = 0.0
    estado: str = "processando"  # processando | pronto | erro
    erro: str = ""
    entrega: Entrega | None = None

    def progresso(self, etapa: str, fracao: float) -> None:
        self.etapa = etapa
        self.fracao = max(self.fracao, min(fracao, 0.99))


TRABALHOS: dict[str, Trabalho] = {}
_TRAVA = threading.Lock()


def _limpar_antigos() -> None:
    agora = time.time()
    with _TRAVA:
        for chave in [
            k for k, t in TRABALHOS.items() if agora - t.criado_em > VALIDADE_DO_TRABALHO
        ]:
            TRABALHOS.pop(chave, None)


def _processar(trabalho: Trabalho, blocos_prontos=None, correcoes=None) -> None:
    try:
        trabalho.entrega = gerar(
            trabalho.fonte,
            trabalho.psicologa,
            trabalho.crp,
            correcoes=correcoes,
            blocos_prontos=blocos_prontos,
            progresso=trabalho.progresso,
        )
        trabalho.etapa = "pronto"
        trabalho.fracao = 1.0
        trabalho.estado = "pronto"
    except Exception as erro:  # o app não pode cair por causa de um markdown torto
        trabalho.estado = "erro"
        trabalho.erro = f"{type(erro).__name__}: {erro}"[:400]
        trabalho.etapa = "erro"


def _iniciar(trabalho: Trabalho, blocos_prontos=None, correcoes=None) -> None:
    TRABALHOS[trabalho.identificador] = trabalho
    threading.Thread(
        target=_processar, args=(trabalho, blocos_prontos, correcoes), daemon=True
    ).start()


# -------------------------------------------------------------------- sessão


def _autenticado(request: Request) -> bool:
    return seguranca.valido(request.cookies.get(seguranca.COOKIE))


def _exige_sessao(request: Request) -> None:
    if not _autenticado(request):
        raise HTTPException(status_code=401, detail="sessão expirada")


def _pagina(nome: str) -> HTMLResponse:
    """Serve a página já com a supervisão técnica registrada preenchida.

    O nome e o CRP da supervisão são dado da marca, não digitação do dia a dia:
    ficam em design/tokens.json e chegam prontos no formulário.
    """
    texto = (ESTATICO / nome).read_text(encoding="utf-8")
    texto = (
        texto.replace("{{PSICOLOGA}}", SUPERVISAO["nome"])
        .replace("{{CRP}}", SUPERVISAO["crp"])
        .replace("{{ESPECIALIDADE}}", SUPERVISAO["especialidade"])
    )
    return HTMLResponse(texto)


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    if not seguranca.senha_configurada():
        return HTMLResponse(
            "<h1>Falta configurar a senha</h1><p>Defina a variável de ambiente "
            "<code>SENHA_APP</code> no Render e reinicie o serviço.</p>",
            status_code=503,
        )
    if not _autenticado(request):
        return _pagina("entrar.html")
    return _pagina("index.html")


@app.post("/entrar")
def entrar(request: Request, senha: str = Form("")):
    if not seguranca.senha_correta(senha):
        time.sleep(1)  # desanima tentativa em série
        return HTMLResponse(
            (ESTATICO / "entrar.html")
            .read_text(encoding="utf-8")
            .replace("<!--ERRO-->", '<p class="erro">Senha incorreta.</p>'),
            status_code=401,
        )
    resposta = RedirectResponse("/", status_code=303)
    resposta.set_cookie(
        seguranca.COOKIE,
        seguranca.assinar(),
        max_age=seguranca.VALIDADE_EM_SEGUNDOS,
        httponly=True,
        samesite="lax",
        # em produção (Render) é sempre https; em teste local, http
        secure=request.url.scheme == "https",
    )
    return resposta


@app.post("/sair")
def sair():
    resposta = RedirectResponse("/", status_code=303)
    resposta.delete_cookie(seguranca.COOKIE)
    return resposta


# ------------------------------------------------------------------ estáticos


@app.get("/app.css")
def css():
    return FileResponse(ESTATICO / "app.css", media_type="text/css")


@app.get("/app.js")
def js():
    return FileResponse(ESTATICO / "app.js", media_type="application/javascript")


@app.get("/exemplo.md")
def exemplo(request: Request):
    _exige_sessao(request)
    return FileResponse(
        EXEMPLO, media_type="text/markdown", filename="exemplo-porto-seguro.md"
    )


@app.get("/formato")
def formato(request: Request):
    _exige_sessao(request)
    return FileResponse(FORMATO, media_type="text/markdown", filename="FORMATO.md")


@app.get("/tipos")
def tipos(request: Request):
    _exige_sessao(request)
    return JSONResponse(
        [
            {"nome": tipo.nome, "rotulo": tipo.rotulo, "descricao": tipo.descricao}
            for tipo in escolhiveis()
        ]
    )


# -------------------------------------------------------------------- geração


@app.post("/gerar")
async def criar(
    request: Request,
    psicologa: str = Form(""),
    crp: str = Form(""),
    texto: str = Form(""),
    arquivo: UploadFile | None = None,
):
    _exige_sessao(request)
    _limpar_antigos()

    fonte = texto or ""
    if arquivo is not None and arquivo.filename:
        bruto = await arquivo.read(LIMITE_DE_ARQUIVO + 1)
        if len(bruto) > LIMITE_DE_ARQUIVO:
            raise HTTPException(status_code=413, detail="arquivo grande demais")
        fonte = bruto.decode("utf-8", errors="replace")

    if not fonte.strip():
        raise HTTPException(status_code=400, detail="mande um arquivo .md ou cole o texto")
    if not psicologa.strip() or not crp.strip():
        raise HTTPException(status_code=400, detail="preencha o nome da psicóloga e o CRP")

    trabalho = Trabalho(
        identificador=uuid.uuid4().hex[:12],
        fonte=fonte,
        psicologa=psicologa[:120],
        crp=crp[:40],
    )
    _iniciar(trabalho)
    return JSONResponse({"trabalho": trabalho.identificador})


def _buscar(identificador: str) -> Trabalho:
    trabalho = TRABALHOS.get(identificador)
    if trabalho is None:
        raise HTTPException(status_code=404, detail="trabalho não encontrado")
    return trabalho


@app.get("/trabalho/{identificador}")
def estado(identificador: str, request: Request):
    _exige_sessao(request)
    trabalho = _buscar(identificador)

    corpo: dict = {
        "estado": trabalho.estado,
        "etapa": trabalho.etapa,
        "fracao": round(trabalho.fracao, 3),
        "erro": trabalho.erro,
    }

    entrega = trabalho.entrega
    if trabalho.estado == "pronto" and entrega is not None:
        por_pagina: dict[int, list[dict]] = {}
        for indice, bloco in enumerate(entrega.blocos):
            pagina = entrega.pagina_por_bloco.get(indice)
            if pagina is None:
                pagina = 1 if bloco.tipo == "capa" else 0
            por_pagina.setdefault(pagina, []).append(
                {
                    "indice": indice,
                    "tipo": bloco.tipo,
                    "rotulo": bloco.rotulo,
                    "procedencia": bloco.procedencia,
                    "observacao": bloco.observacao,
                    "editavel": bloco.procedencia != "automatico",
                    "linha": bloco.origem_linha,
                }
            )
        corpo.update(
            {
                "paginas": entrega.paginas,
                "relatorio": entrega.relatorio.para_json(),
                "blocos_por_pagina": {str(k): v for k, v in sorted(por_pagina.items())},
                "aviso_de_revisao": entrega.aviso_de_revisao,
                "titulo": entrega.meta.titulo if entrega.meta else "",
            }
        )
    return JSONResponse(corpo)


@app.get("/trabalho/{identificador}/miniatura/{numero}")
def miniatura(identificador: str, numero: int, request: Request):
    _exige_sessao(request)
    trabalho = _buscar(identificador)
    if trabalho.entrega is None or not (1 <= numero <= len(trabalho.entrega.miniaturas)):
        raise HTTPException(status_code=404, detail="página não encontrada")
    return Response(
        trabalho.entrega.miniaturas[numero - 1],
        media_type="image/png",
        headers={"Cache-Control": "private, max-age=3600"},
    )


@app.get("/trabalho/{identificador}/pdf")
def pdf(identificador: str, request: Request):
    _exige_sessao(request)
    trabalho = _buscar(identificador)
    if trabalho.entrega is None:
        raise HTTPException(status_code=409, detail="ainda não está pronto")
    titulo = (trabalho.entrega.meta.titulo if trabalho.entrega.meta else "ebook") or "ebook"
    nome = "".join(c if c.isalnum() or c in " -_" else "" for c in titulo).strip() or "ebook"
    return Response(
        trabalho.entrega.pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome}.pdf"'},
    )


@app.post("/trabalho/{identificador}/regerar")
async def regerar(identificador: str, request: Request):
    _exige_sessao(request)
    anterior = _buscar(identificador)
    if anterior.entrega is None:
        raise HTTPException(status_code=409, detail="ainda não está pronto")

    corpo = await request.json()
    correcoes = {
        int(chave): valor
        for chave, valor in (corpo.get("correcoes") or {}).items()
        if valor
    }
    if not correcoes:
        raise HTTPException(status_code=400, detail="nenhuma troca de tipo recebida")

    # reaproveita os blocos já classificados: regerar não reclassifica nada
    prontos = [
        Bloco.de_json(bloco.para_json())
        for bloco in anterior.entrega.blocos
        if bloco.procedencia != "automatico"
    ]
    deslocamento = {}
    posicao = 0
    for indice, bloco in enumerate(anterior.entrega.blocos):
        if bloco.procedencia != "automatico":
            deslocamento[indice] = posicao
            posicao += 1

    trabalho = Trabalho(
        identificador=uuid.uuid4().hex[:12],
        fonte=anterior.fonte,
        psicologa=anterior.psicologa,
        crp=anterior.crp,
    )
    _iniciar(
        trabalho,
        blocos_prontos=prontos,
        correcoes={
            deslocamento[indice]: tipo
            for indice, tipo in correcoes.items()
            if indice in deslocamento
        },
    )
    return JSONResponse({"trabalho": trabalho.identificador})


@app.get("/saude")
def saude():
    return {"ok": True, "trabalhos": len(TRABALHOS)}
