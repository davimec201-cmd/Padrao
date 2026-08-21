# Pendências — o que ainda falta

Atualizado em **21/08/2026**, depois da auditoria de código externa. O conteúdo
clínico continua sendo o da devolutiva do formulário "Decisões clínicas e dados dos
equipamentos", respondido e assinado pelo **Dr. Vinicius Lotto Maeta** em 20/08/2026.

---

## Duas autorizações que agora são do humano

Nenhuma das duas é pendência: são **portões**, e o fluxo do dia a dia não passa por
eles. Ficam aqui porque a pessoa que opera precisa saber que existem.

| Arquivo que o humano cria | Libera | Vale para |
|---|---|---|
| `~/.laudos_oct/PERMITIR_ANYWHERE` | `hands.py --anywhere`, que desliga a guarda de foco e a de retângulo | **um comando** — o arquivo é apagado no uso |
| `~/.laudos_oct/PERMITIR_ASSINATURA` | `laudo_pdf.py --assinar`, o documento final assinado | **um documento** — idem |

```bash
touch ~/.laudos_oct/PERMITIR_ASSINATURA        # macOS / Git Bash
ni $HOME\.laudos_oct\PERMITIR_ASSINATURA      # PowerShell
```

O agente **não** cria esses arquivos: o guardião nega qualquer comando que os toque.
Se ele pedir que você crie um, é porque parou e está pedindo — que é o desenho.

---

## Aberta — uma só

### P1 — Imagens de assinatura

**Bloqueia:** a emissão do **documento final assinado** (`laudo_pdf.py --assinar`).
Não bloqueia a minuta, que sai normalmente e é o fluxo do dia a dia.

Faltam dois arquivos, um por signatário:

| Arquivo | Signatário |
|---|---|
| `~/.laudos_oct/assinaturas/assinatura_cassiano.png` | Dr. Cassiano Ricardo Goulart (Farroupilha) |
| `~/.laudos_oct/assinaturas/assinatura_maeta.png` | Dr Vinícius L Maeta (Nova Prata) |

**Como produzir cada um:**

1. Assinar com caneta preta de ponta grossa (0,7–1,0 mm) em papel branco liso, **sem pauta**.
2. Digitalizar a **600 dpi** em tons de cinza. Escâner de verdade; foto de celular só
   se for bem iluminada e sem sombra.
3. Recortar rente ao traço, aumentar contraste e **remover o fundo** — fundo branco
   vira um retângulo por cima da linha do documento.
4. Salvar **PNG-24 com canal alfa**, largura mínima de **1200 px**. Abaixo disso o
   traço serrilha no tamanho impresso (~50 mm).

**Onde os arquivos ficam, e por quê:** em `~/.laudos_oct/assinaturas/`, **fora do
pacote da skill e fora do controle de versão**. Imagem de assinatura é o ativo mais
sensível deste projeto — quem a tem, assina. Não commite, não coloque em pasta
sincronizada, não mande por e-mail.

**SVG:** vetorizar (Inkscape → Traçar bitmap, ou `potrace`) melhora a nitidez em
qualquer tamanho e pesa poucos KB. O código **prefere `.svg`** quando existe e usa o
`.png` como reserva — mas a renderização de SVG ainda depende da biblioteca `svglib`,
que não está instalada. Enquanto não estiver, forneça o `.png`: se só houver `.svg`,
a emissão do final recusa dizendo isso.

---

## Encerradas em 20/08/2026 — não reabrir

O documento de devolutiva é explícito: estas estão fechadas. Não peça confirmação,
não proponha alternativa, não abra chamado de "conferir com o médico".

| Assunto | Como ficou |
|---|---|
| **Revisão da base científica** | Feita. Registrada em `references/base/REVISAO.json` com revisor, data e hash. A trava continua no código, satisfeita. |
| **Significado das cores** | Verde/branco = dentro. **Amarelo e vermelho = fora**, mesma redação. Não existe "limítrofe". |
| **Modelo dos aparelhos** | Irrelevante — a imagem que ele lauda é sempre a mesma. Não existe campo de equipamento. |
| **Índice de qualidade** | Sem limiar numérico e sem campo. Exame ruim é laudado; frase própria quando for impossível avaliar. |
| **Reserva diagnóstica** | Em todo laudo de nervo, dos dois hospitais. Em nenhum de mácula. |
| **Frase de normalidade da mácula** | "aparentemente dentro da normalidade" nos dois hospitais. |
| **Nascimento em Nova Prata** | Impresso quando houver, em linha própria; a linha some quando não houver. |
| **"área da escavação"** | Corrigido para "relação escavação/papila (área)" em toda a biblioteca. |
| **Conclusão de nervo normal** | **Sem frase aprovada, por decisão.** Sai com CONCLUSÕES em branco e um aviso de que a conclusão é do médico. Não compor substituta. |
| **Frase de exame limitado** | Ficou sem marcação no formulário → **não entra** na biblioteca. Quando for preciso registrar uma limitação, ela vai em `observacoes` **dentro do olho** — na raiz do JSON o campo é recusado, porque de lá ele não era impresso e sumia em silêncio. |
| **Dados dos signatários** | Extraídos dos laudos reais. Um por hospital. |

---

## Preparado, não implementado

**Assinatura digital ICP-Brasil.** Fac-símile em imagem só vale quando o documento é
impresso e conferido. Para laudo que circula em PDF, o padrão é certificado
ICP-Brasil (ou via CFM), que carimba autoria verificável e detecta adulteração.
O PDF é gerado de forma a permitir plugar essa etapa depois. **Não implementar
agora** — decisão do documento de devolutiva, seção 2, Caminho B.

---

## Entregável combinado

O Dr. Maeta registrou que espera receber o conjunto completo — base científica,
modelos de laudo, regras de redação e limites do sistema — em **um único documento**.
Continua valendo como entregável, agora como material de referência e arquivo do
projeto, **não como pré-condição** para operar.
