"""Catálogo de blocos.

Cada bloco é um tipo fechado, com campos declarados e um template próprio. Este
arquivo é a lista completa do que o sistema sabe diagramar: se um trecho não
encaixa em nenhum tipo daqui, ele vira `secao_conceitual` e o caso entra no
relatório de QA — o sistema nunca inventa layout.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TipoDeBloco:
    nome: str
    rotulo: str  # como aparece na interface
    descricao: str  # usado também no prompt do classificador
    diretiva: str | None  # ::: que produz este bloco, quando existe
    campos: tuple[str, ...] = ()
    automatico: bool = False  # gerado pelo sistema, não escrito no markdown
    pagina_propria: bool = False
    escolhivel: bool = True  # aparece no seletor de correção da interface


CATALOGO: dict[str, TipoDeBloco] = {
    "capa": TipoDeBloco(
        nome="capa",
        rotulo="Capa",
        descricao="Capa do material: título, subtítulo curto, marca e supervisão técnica. Ilustração de personagem só quando o material pede.",
        diretiva=None,
        campos=("titulo", "subtitulo", "personagem", "psicologa", "crp"),
        automatico=True,
        pagina_propria=True,
        escolhivel=False,
    ),
    "carta_abertura": TipoDeBloco(
        nome="carta_abertura",
        rotulo="Carta de abertura",
        descricao="Carta em primeira pessoa para quem vai ler, em texto corrido, terminando com assinatura.",
        diretiva="carta",
        campos=("corpo", "assinatura"),
    ),
    "sumario": TipoDeBloco(
        nome="sumario",
        rotulo="Sumário",
        descricao="Lista do que o material contém, com número de página real.",
        diretiva=None,
        campos=("itens",),
        automatico=True,
        pagina_propria=True,
        escolhivel=False,
    ),
    "secao_conceitual": TipoDeBloco(
        nome="secao_conceitual",
        rotulo="Seção conceitual",
        descricao="Texto explicativo com título e subtítulos: conceito, mecanismo, contexto técnico. É o bloco genérico de fallback.",
        diretiva=None,
        campos=("titulo", "corpo"),
    ),
    "tabela_comparativa": TipoDeBloco(
        nome="tabela_comparativa",
        rotulo="Tabela comparativa",
        descricao="Duas colunas que contrastam dois conceitos, no padrão 'Birra × Crise'.",
        diretiva=None,
        campos=("cabecalhos", "linhas"),
    ),
    "caixa_atencao": TipoDeBloco(
        nome="caixa_atencao",
        rotulo="Caixa de atenção",
        descricao="Destaque curto de um ponto crítico, ressalva clínica ou aviso que o leitor não pode perder.",
        diretiva="atencao",
        campos=("rotulo", "corpo"),
    ),
    "abertura_bloco": TipoDeBloco(
        nome="abertura_bloco",
        rotulo="Abertura de bloco",
        descricao="Página divisória que abre um bloco de atividades: número, nome e uma frase.",
        diretiva="bloco",
        campos=("numero", "nome", "frase"),
        pagina_propria=True,
    ),
    "ficha_atividade": TipoDeBloco(
        nome="ficha_atividade",
        rotulo="Ficha de atividade",
        descricao="Atividade completa: número e nome, objetivo terapêutico, princípio ABA-TCC, materiais, passo a passo, versão mais fácil e mais desafiadora, e o que observar.",
        diretiva="ficha",
        campos=("numero", "nome", "objetivo", "principio", "materiais", "passos", "facil", "desafiador", "observar"),
        pagina_propria=True,
    ),
    "formulario_imprimivel": TipoDeBloco(
        nome="formulario_imprimivel",
        rotulo="Formulário imprimível",
        descricao="Página para preencher à mão: campos com linhas e opções para marcar.",
        diretiva="formulario",
        campos=("titulo", "instrucao", "campos", "repeticoes"),
        pagina_propria=True,
    ),
    "dicas_praticas": TipoDeBloco(
        nome="dicas_praticas",
        rotulo="Dicas práticas",
        descricao="Série de dicas curtas para o adulto, cada uma com título imperativo e um parágrafo.",
        diretiva="dicas",
        campos=("titulo", "dicas"),
    ),
    "roda_conversa": TipoDeBloco(
        nome="roda_conversa",
        rotulo="Roda de conversa",
        descricao="Perguntas numeradas para ler junto com a criança depois da história.",
        diretiva="conversa",
        campos=("titulo", "perguntas"),
    ),
    "voz_personagem": TipoDeBloco(
        nome="voz_personagem",
        rotulo="Voz do personagem",
        descricao="Fala do personagem do Vale da Harmonia, em tom afetivo, fechando uma ideia.",
        diretiva="voz",
        campos=("personagem", "titulo", "corpo"),
    ),
    "secao_encerramento": TipoDeBloco(
        nome="secao_encerramento",
        rotulo="Encerramento",
        descricao="Fecho do material: o que observar daqui para frente, quando buscar ajuda, última palavra.",
        diretiva="encerramento",
        campos=("titulo", "corpo"),
    ),
    "pagina_final": TipoDeBloco(
        nome="pagina_final",
        rotulo="Página final",
        descricao="Fundamentação científica literal, disclaimer legal com nome e CRP, e marca.",
        diretiva=None,
        campos=("psicologa", "crp"),
        automatico=True,
        pagina_propria=True,
        escolhivel=False,
    ),
}

# diretiva -> tipo de bloco
POR_DIRETIVA: dict[str, str] = {
    tipo.diretiva: nome for nome, tipo in CATALOGO.items() if tipo.diretiva
}

# tipos que o classificador pode escolher para um trecho ambíguo
CLASSIFICAVEIS: tuple[str, ...] = (
    "secao_conceitual",
    "carta_abertura",
    "caixa_atencao",
    "dicas_praticas",
    "roda_conversa",
    "voz_personagem",
    "secao_encerramento",
)

FALLBACK = "secao_conceitual"


def escolhiveis() -> list[TipoDeBloco]:
    """Tipos que a interface oferece no seletor de correção."""
    return [tipo for tipo in CATALOGO.values() if tipo.escolhivel]


@dataclass
class Bloco:
    """Uma unidade de conteúdo já classificada, pronta para o template."""

    tipo: str
    dados: dict = field(default_factory=dict)
    origem_linha: int = 0
    # como o tipo foi decidido: 'diretiva', 'estrutura', 'classificador',
    # 'fallback' ou 'correcao_manual'
    procedencia: str = "estrutura"
    observacao: str = ""

    @property
    def rotulo(self) -> str:
        return CATALOGO[self.tipo].rotulo

    def para_json(self) -> dict:
        return {
            "tipo": self.tipo,
            "dados": self.dados,
            "origem_linha": self.origem_linha,
            "procedencia": self.procedencia,
            "observacao": self.observacao,
        }

    @classmethod
    def de_json(cls, bruto: dict) -> "Bloco":
        return cls(
            tipo=bruto["tipo"],
            dados=bruto.get("dados", {}),
            origem_linha=bruto.get("origem_linha", 0),
            procedencia=bruto.get("procedencia", "estrutura"),
            observacao=bruto.get("observacao", ""),
        )
