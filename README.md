# Padrão

Ferramentas pessoais. Feitas sob medida, sem anúncio, sem conta, sem ninguém
decidindo por mim como as coisas devem funcionar.

## Projetos

### `um-de-cada-vez/`

Ferramenta de estudo. Um arquivo HTML só — abre no navegador, funciona offline,
guarda tudo no próprio aparelho.

Resolve duas coisas específicas:

1. **Não saber o que estudar hoje.** Abriu, tem um assunto na tela. Só um.
   Decidir gasta energia que era pra ser gasta estudando.
2. **Material espalhado.** Matéria, assunto e resumo no mesmo lugar.

O fluxo de estudo é o método de sempre, só que guiado:

| Passo | O que acontece |
|---|---|
| **Transcrever** | Você digita o resumo. Escrever é o estudo, não é arquivar. |
| **Explicar** | O texto some. Você explica em voz alta, sem olhar. |
| **Avaliar** | Travei / Quase / Mandei bem — define quando o assunto volta. |

A revisão é espaçada: 1, 3, 7, 16, 35, 70 dias. "Travei" volta pro começo,
"Quase" mantém, "Mandei bem" avança.

**Decisões de projeto que não são estéticas:**

- Uma decisão por tela. Lista longa trava, então não tem lista na tela inicial.
- Zero contador de atraso. "Você está 87 revisões atrasado" faz fechar o app e
  não voltar. Atrasado é só o que vem primeiro na fila.
- Sessão com começo e fim visíveis — timer e bolinhas de progresso, finito.
- Sair no meio não perde o que foi escrito.

**Onde os dados ficam:** no navegador daquele aparelho (`localStorage`). Limpar
os dados do navegador apaga tudo. Tem backup em Ajustes — baixa um `.json` que
também serve pra levar os resumos pra outro aparelho.

**Rodar:** abrir `um-de-cada-vez/index.html` no navegador. Não precisa instalar
nada, não tem build, não tem servidor.
