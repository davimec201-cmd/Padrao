/* Interface do diagramador. JS simples, sem framework.
   Um caminho só: entrada → progresso → resultado. E, se você discordar de uma
   classificação, troca de tipo na miniatura + regerar. */

"use strict";

const $ = (id) => document.getElementById(id);

const estado = {
  trabalho: null,
  tipos: [],
  correcoes: {},
  aba: "arquivo",
};

/* ----------------------------------------------------------------- abas */

function trocarAba(qual) {
  estado.aba = qual;
  $("aba-arquivo").setAttribute("aria-selected", String(qual === "arquivo"));
  $("aba-texto").setAttribute("aria-selected", String(qual === "texto"));
  $("painel-arquivo").classList.toggle("escondido", qual !== "arquivo");
  $("painel-texto").classList.toggle("escondido", qual !== "texto");
}

$("aba-arquivo").addEventListener("click", () => trocarAba("arquivo"));
$("aba-texto").addEventListener("click", () => trocarAba("texto"));

$("arquivo").addEventListener("change", (evento) => {
  const arquivo = evento.target.files[0];
  $("nome-arquivo").textContent = arquivo ? arquivo.name : "nenhum arquivo escolhido";
});

/* --------------------------------------------------------------- gerar */

function mostrarErro(mensagem) {
  const caixa = $("erro-entrada");
  caixa.textContent = mensagem;
  caixa.classList.remove("escondido");
}

function esconderErro() {
  $("erro-entrada").classList.add("escondido");
}

async function gerar() {
  esconderErro();
  const psicologa = $("psicologa").value.trim();
  const crp = $("crp").value.trim();
  const arquivo = $("arquivo").files[0];
  const texto = $("texto").value.trim();

  if (!psicologa || !crp) {
    mostrarErro("Preencha o nome da psicóloga e o CRP.");
    return;
  }
  if (estado.aba === "arquivo" && !arquivo) {
    mostrarErro("Escolha o arquivo .md ou use a aba de colar texto.");
    return;
  }
  if (estado.aba === "texto" && !texto) {
    mostrarErro("Cole o markdown do e-book.");
    return;
  }

  const dados = new FormData();
  dados.append("psicologa", psicologa);
  dados.append("crp", crp);
  if (estado.aba === "arquivo") dados.append("arquivo", arquivo);
  else dados.append("texto", texto);

  $("gerar").disabled = true;
  try {
    const resposta = await fetch("/gerar", { method: "POST", body: dados });
    if (!resposta.ok) {
      const corpo = await resposta.json().catch(() => ({}));
      throw new Error(corpo.detail || "não foi possível começar");
    }
    const { trabalho } = await resposta.json();
    estado.trabalho = trabalho;
    estado.correcoes = {};
    $("entrada").classList.add("escondido");
    $("resultado").classList.add("escondido");
    $("progresso").classList.remove("escondido");
    acompanhar();
  } catch (erro) {
    mostrarErro(erro.message);
    $("gerar").disabled = false;
  }
}

$("gerar").addEventListener("click", gerar);

/* ----------------------------------------------------------- progresso */

async function acompanhar() {
  try {
    const resposta = await fetch(`/trabalho/${estado.trabalho}`);
    if (resposta.status === 401) {
      location.reload();
      return;
    }
    const dados = await resposta.json();

    $("barra").style.width = `${Math.round(dados.fracao * 100)}%`;
    $("etapa").innerHTML = `<strong>${dados.etapa}</strong>`;

    if (dados.estado === "processando") {
      setTimeout(acompanhar, 700);
      return;
    }
    if (dados.estado === "erro") {
      $("progresso").classList.add("escondido");
      $("entrada").classList.remove("escondido");
      $("gerar").disabled = false;
      mostrarErro(`Não deu para gerar: ${dados.erro}`);
      return;
    }
    mostrarResultado(dados);
  } catch (erro) {
    setTimeout(acompanhar, 1500);
  }
}

/* ----------------------------------------------------------- resultado */

const MARCA = { ok: "✓", aviso: "!", falha: "✕" };

function cartaoDeAchado(achado) {
  const item = document.createElement("div");
  item.className = `achado ${achado.estado}`;
  const detalhes =
    achado.detalhes.length && achado.estado !== "ok"
      ? `<ul>${achado.detalhes.map((d) => `<li>${escapar(d)}</li>`).join("")}</ul>`
      : "";
  item.innerHTML = `
    <div class="cabeca">
      <span class="ponto"></span>
      <span class="nome">${escapar(achado.verificacao)}</span>
      <span class="resumo">${escapar(achado.resumo)}</span>
    </div>${detalhes}`;
  return item;
}

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function mostrarResultado(dados) {
  const relatorio = dados.relatorio;
  $("progresso").classList.add("escondido");
  $("resultado").classList.remove("escondido");

  $("titulo-resultado").textContent = dados.titulo || "Resultado";
  $("resumo-paginas").textContent = `${dados.paginas} páginas`;
  $("lembrete-texto").textContent = dados.aviso_de_revisao;
  $("baixar").href = `/trabalho/${estado.trabalho}/pdf`;

  const selo = $("selo");
  selo.innerHTML = "";
  const caixa = document.createElement("div");
  if (relatorio.falhas === 0 && relatorio.avisos === 0) {
    caixa.className = "selo verde";
    caixa.innerHTML = `<span class="marca">✓</span><span>QA todo verde — ${relatorio.total} verificações</span>`;
  } else if (relatorio.tem_critico) {
    caixa.className = "selo falha";
    caixa.innerHTML = `<span class="marca">✕</span><span>${relatorio.falhas} falha(s) crítica(s) — confira antes de baixar</span>`;
  } else {
    caixa.className = "selo aviso";
    caixa.innerHTML = `<span class="marca">!</span><span>${relatorio.avisos} aviso(s) para conferir</span>`;
  }
  selo.appendChild(caixa);

  const importantes = $("achados-importantes");
  const ok = $("achados-ok");
  importantes.innerHTML = "";
  ok.innerHTML = "";
  relatorio.achados.forEach((achado) => {
    (achado.estado === "ok" ? ok : importantes).appendChild(cartaoDeAchado(achado));
  });
  if (!importantes.children.length) {
    importantes.innerHTML =
      '<p class="ajuda" style="margin:0">Nada a corrigir: todas as verificações passaram.</p>';
  }

  montarPaginas(dados);
}

/* -------------------------------------------------- páginas e correção */

async function carregarTipos() {
  if (estado.tipos.length) return;
  const resposta = await fetch("/tipos");
  estado.tipos = await resposta.json();
}

async function montarPaginas(dados) {
  await carregarTipos();
  const area = $("paginas");
  area.innerHTML = "";
  estado.correcoes = {};
  $("regerar").classList.add("escondido");

  for (let numero = 1; numero <= dados.paginas; numero += 1) {
    const blocos = dados.blocos_por_pagina[String(numero)] || [];
    const cartao = document.createElement("div");
    cartao.className = "pagina-cartao";
    cartao.dataset.pagina = String(numero);

    const imagem = document.createElement("img");
    imagem.loading = "lazy";
    imagem.alt = `Página ${numero}`;
    imagem.src = `/trabalho/${estado.trabalho}/miniatura/${numero}`;
    cartao.appendChild(imagem);

    const rotulo = document.createElement("div");
    rotulo.className = "numero";
    rotulo.textContent = `pág. ${numero}`;
    cartao.appendChild(rotulo);

    blocos.forEach((bloco) => {
      const linha = document.createElement("div");
      linha.className = "bloco";
      if (!bloco.editavel) {
        const fixo = document.createElement("div");
        fixo.className = "obs";
        fixo.textContent = `${bloco.rotulo} (automático)`;
        linha.appendChild(fixo);
      } else {
        const selecao = document.createElement("select");
        selecao.setAttribute("aria-label", `Tipo do bloco da página ${numero}`);
        estado.tipos.forEach((tipo) => {
          const opcao = document.createElement("option");
          opcao.value = tipo.nome;
          opcao.textContent = tipo.rotulo;
          opcao.selected = tipo.nome === bloco.tipo;
          selecao.appendChild(opcao);
        });
        selecao.addEventListener("change", () => {
          if (selecao.value === bloco.tipo) delete estado.correcoes[bloco.indice];
          else estado.correcoes[bloco.indice] = selecao.value;
          const tem = Object.keys(estado.correcoes).length > 0;
          $("regerar").classList.toggle("escondido", !tem);
          cartao.classList.toggle("marcada", selecao.value !== bloco.tipo);
        });
        linha.appendChild(selecao);
      }
      if (bloco.observacao) {
        const obs = document.createElement("div");
        obs.className = "obs";
        obs.textContent = bloco.observacao;
        linha.appendChild(obs);
      }
      cartao.appendChild(linha);
    });

    area.appendChild(cartao);
  }
}

$("regerar").addEventListener("click", async () => {
  const botao = $("regerar");
  botao.disabled = true;
  try {
    const resposta = await fetch(`/trabalho/${estado.trabalho}/regerar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correcoes: estado.correcoes }),
    });
    if (!resposta.ok) {
      const corpo = await resposta.json().catch(() => ({}));
      throw new Error(corpo.detail || "não foi possível regerar");
    }
    const { trabalho } = await resposta.json();
    estado.trabalho = trabalho;
    $("resultado").classList.add("escondido");
    $("progresso").classList.remove("escondido");
    $("barra").style.width = "0%";
    acompanhar();
  } catch (erro) {
    alert(erro.message);
  } finally {
    botao.disabled = false;
  }
});
