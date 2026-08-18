# Colocar o diagramador no ar — só pelo tablet

Nenhum passo aqui precisa de computador ou de terminal. São ~15 minutos, e você
faz uma vez só.

---

## 1. Pegar a chave da API (5 min)

A chave é o que permite ao sistema classificar os trechos que você escrever sem
diretiva. **Sem ela o app funciona igual** — só que todo trecho solto vira seção
de texto comum e o relatório avisa.

1. No navegador do tablet, abra **console.anthropic.com** e entre com sua conta.
2. Menu → **API keys** → **Create key**.
3. Dê o nome `diagramador` e toque em **Create**.
4. **Copie a chave agora** (ela só aparece uma vez). Cole em algum lugar seguro
   do tablet — nas Notas, por exemplo. Ela começa com `sk-ant-`.

## 2. Criar o serviço no Render (5 min)

1. Abra **render.com** e entre com a conta do GitHub (a mesma do repositório
   `Padrao`).
2. **New +** → **Blueprint**.
3. Em *Connect a repository*, escolha **Padrao**. Se ele não aparecer, toque em
   *Configure account* e autorize o Render a ver o repositório.
4. O Render lê o arquivo `render.yaml` sozinho e mostra o serviço
   **diagramador-teaformation**. Em *Branch*, deixe `main` (ou escolha a branch
   onde o código está).
5. Ele vai pedir duas variáveis:

   | Variável | O que colocar |
   |---|---|
   | `SENHA_APP` | a senha que **você** vai usar para entrar no app. Invente uma boa; é o que impede qualquer pessoa de abrir |
   | `ANTHROPIC_API_KEY` | a chave `sk-ant-...` do passo 1 |

   `CHAVE_SESSAO` é gerada pelo Render sozinho — não mexa.

6. **Apply**. O primeiro build leva de 5 a 10 minutos (é a imagem Docker com as
   bibliotecas de tipografia). Pode fechar a aba: o build continua.

## 3. Abrir e instalar no tablet (2 min)

1. Quando o painel mostrar **Live**, toque no endereço no topo — algo como
   `https://diagramador-teaformation.onrender.com`.
2. Digite a `SENHA_APP`. Pronto.
3. No Chrome: menu **⋮** → **Adicionar à tela inicial**. No Safari: botão de
   compartilhar → **Adicionar à Tela de Início**. Aí ele abre como aplicativo,
   sem barra de navegador.

---

## Qual plano escolher

O `render.yaml` vem com o plano **Starter**. Vale entender a diferença:

| Plano | Preço | Como se comporta |
|---|---|---|
| **Free** | US$ 0 | Dorme depois de 15 min parado: a primeira geração do dia demora ~1 min a mais, só para acordar. Memória dá conta: um e-book de 20 páginas usa 153 MB e um de 55 usa 219 MB, medidos — o limite é 512 MB |
| **Starter** | ~US$ 7/mês | Não dorme, então não tem espera para acordar. Build mais rápido |

Se você gera e-book de vez em quando, o **Free** resolve. O Starter compra só a
ausência daquele minuto de espera.

Para trocar: no painel do serviço, **Settings** → **Instance Type**. Ou edite
`plan: starter` para `plan: free` no `render.yaml` e faça o commit.

## Trocar a senha depois

Painel do serviço → **Environment** → editar `SENHA_APP` → **Save, rebuild and
deploy**. Todo mundo é desconectado e você entra com a nova.

## Atualizar o app quando o código mudar

Está ligado no automático (`autoDeployTrigger: commit`): todo commit na branch
configurada dispara um deploy novo. Para ver o andamento, painel → **Events**.

## Quando algo der errado

| Sintoma | O que fazer |
|---|---|
| Abre "Falta configurar a senha" | `SENHA_APP` não foi preenchida. Painel → Environment → adicionar → salvar |
| O relatório diz "o classificador não rodou" | `ANTHROPIC_API_KEY` errada, vencida ou sem crédito. O PDF sai igual; o aviso some quando a chave voltar |
| A primeira geração do dia demora muito | Plano Free dormindo. É o comportamento normal dele |
| "Não deu para gerar" com erro estranho | Copie a mensagem: ela diz a linha do markdown. Quase sempre é `:::` sem fechar |
| Build falhou | Painel → **Logs**. Se aparecer `verificar_fontes.py` com FALHA, alguma fonte não foi para o repositório — confira `assets/fontes/` |

## O que fica guardado onde

- **Nada do seu conteúdo é gravado em disco.** Markdown, PDF e miniaturas ficam
  na memória do serviço por até 6 horas e somem quando ele reinicia.
- Baixe o PDF quando terminar. Se o serviço reiniciar, a geração se perde e você
  manda o markdown de novo.
