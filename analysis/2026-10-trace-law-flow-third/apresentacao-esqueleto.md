# Esqueleto da apresentação a stakeholders — slides fechados

> Esqueleto aprovado slide a slide; o deck é gerado por `gerar_apresentacao.py` (mesmo diretório), que segue este
> esqueleto. **Roda na máquina da base 3**, depois do relatório da rodada:
>
> ```
> uv sync
> uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py relatorio --rodada <pasta da rodada>
> uv run python analysis/2026-10-trace-law-flow-third/gerar_apresentacao.py --rodada <pasta da rodada> [--figuras <pasta>]
> ```
>
> As figuras vêm da rodada (`relatorio/`, `painel/`, `taxas/`); o painel duplo do slide 5 e a tabela mensal saem de
> `taxas/taxas_por_mes.csv`. Figura que falta vira marcador com o nome esperado; `figuras.md`, ao lado do .pptx, lista o
> que entrou e o que falta. A saída fica em `<rodada>/apresentacao/` (fora do git, como toda saída de rodada). Os
> recortes de trace (slide 2, anexos F, G, H) e os overviews das bases 2 e 3 (anexo B) entram por `--figuras`, já
> anonimizados e varridos.
>
> **Regra do deck:** nenhum número aparece como economia comprovada; candidata ≠ memória validada; cada figura declara
> de qual base veio e em que data.

---

## Slide 1 — Agentes que melhoram com os próprios erros ✅

**Função:** abertura + enquadramento. Mostra o projeto inteiro em 30 segundos e deixa claro que esta apresentação cobre **uma parte**: a evidência empírica da mineração de traces.

**Mensagem principal (uma frase):** "Nossos agentes recomeçam do zero a cada execução; o projeto transforma sinais de desempenho em memória textual controlada — e a mineração de traces é a evidência que sustenta o design."

### Elementos

| Zona | Conteúdo |
|---|---|
| **Eyebrow** | Projeto Nº [ANONIMIZADO] · 07/2026 → 07/2027 · bolsa [PROGRAMA-FOMENTO] |
| **Título** | Agentes que melhoram com os próprios erros |
| **Subtítulo** | título formal do plano: "Mecanismo de atualização de memória para agentes de IA generativa com aprendizado por reforço aplicado a fluxos jurídicos" |
| **Card esquerdo — O problema** | Cada execução recomeça do zero: a lição de hoje não chega à execução de amanhã — o mesmo erro volta, no mesmo papel, meses depois. |
| **Card direito — A proposta (auto-melhora controlada)** | Sinais de desempenho (revisão humana, feedback da área usuária) ajustam **instruções, exemplos e contexto** na memória **textual** do agente. Auditável, versionada, reversível — **sem retreinar o modelo**. |
| **Timeline — Plano de Trabalho** | 5 blocos: **M1** Fundamentação + POCs comparativas (out/26) → **M2** Arquitetura + validação local (dez/26) → **M3** Implementação (mar/27) → **M4** Piloto A/B em produção (mai/27) → **M5** Consolidação + expansão (jul/27) |
| **Faixa de enquadramento (destaque)** | "ESTA APRESENTAÇÃO — a evidência empírica: a mineração dos traces reais produz os sinais de erro/feedback (Subs 1.4–1.5) que fundamentam a arquitetura (M2) e o piloto A/B (M3–M4)." |

### Racional

- **Memória + self-improvement** aparecem na proposta, não só no título: é o conceito central do plano (sinais → ajuste controlado → agente melhor).
- **A timeline** responde "onde você está no projeto?" sem um slide de roadmap separado.
- **A faixa final** resolve o enquadramento: ninguém sai do slide achando que verá o mecanismo pronto ou o piloto.
- **"Sem retreinar o modelo"** pré-arma contra a leitura errada de "aprendizado por reforço" (RL aqui = ajuste por sinais explícitos, não treino de pesos).

### Definição usada no slide

> **Memória textual** = texto curado (regras/instruções, exemplos e contexto operacional) que o agente lê em execuções futuras — não treino, não pesos. Auditável, versionada, reversível. Métodos paramétricos (MEND, fine-tuning) estão fora do escopo de implementação.

### Fontes

`docs/work-plan.md` (macroatividades e prazos) · `docs/sub-activity-map.md` (Subs 1.4–1.5) · `discussion/scope-and-terminology-decisions.md` §§1–2

### Observações de fala

- "Por que não fine-tune?": memória textual é auditável, reversível e atualizável sem pipeline de treino — e é o que a plataforma consegue versionar hoje (argumento de custo do tutor, 28/08).
- "Quando vira produto?": a timeline responde — piloto em M4 (mai/27).

---

## Slide 2 — Anatomia do trace: onde mora o erro e por que ele é esquecido ✅

**Função:** ensinar a máquina antes de medir — o que é uma execução, o que é um passo, como o erro circula no contexto e o que acontece quando a execução termina. Ponte direta para o slide 3 (reincidência).

**Mensagem principal (uma frase):** "Uma execução é uma cadeia de passos; quando um passo erra, a mensagem volta no contexto do passo seguinte — e quando a execução termina, tudo é descartado."

### Layout

```
┌─ UMA EXECUÇÃO DO AGENTE ────────────────────────────────────────┐
│                                                                 │
│ prompt + memória ──► [TaskStep] ──► [PlanningStep] ──►          │
│ [ActionStep] ──► [ActionStep] ──► ... ──► resposta final        │
│                                                                 │
│ ZOOM no ActionStep:                                             │
│ código gerado · pensamento · ferramenta chamada · observação    │
│                                                                 │
│ SE O PASSO ERRA:                                                │
│ exceção ──► a mensagem entra no contexto do próximo passo ──►   │
│ o agente lê o próprio erro e reage ──► segue até a resposta     │
│      ┌─ recorte real (base 1, drill_down) ─┐                    │
│      │ [n]   error: 'dict' has no attr...  │                    │
│      │ [n+1] contexto traz a mensagem ▲    │                    │
│      └─────────────────────────────────────┘                    │
│ ┌───────────────────────────────────────────────┐               │
│ │ execução termina → TODO o contexto descartado  │ ──► slide 3  │
│ └───────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Cadeia** | prompt + memória → TaskStep → PlanningStep → cadeia de ActionSteps → resposta final |
| **Zoom no ActionStep** | código gerado, pensamento, ferramenta chamada, observação — é o único tipo de passo que executa (Task/Planning não têm campo de erro) |
| **O loop do erro** | exceção → mensagem escrita no contexto do próximo passo → o agente **lê o próprio erro** e reage |
| **Recorte real (inset)** | 3–5 linhas de um caso da base 1 via `drill_down.py` — o passo `[n]` com a exceção e o `[n+1]` com a mensagem no contexto — **o mesmo caso do anexo G** (produzir na máquina 2; anonimizado, varredura de PII) |
| **A fronteira** | a execução termina → o contexto inteiro é descartado — é a ponte para o slide 3 |
| **Nota** | "ver o erro" = texto no próximo prompt; "entre execuções" = contexto zerado |

### Observações de fala

- "Onde entra a memória?": o prompt lê a memória no início da execução — a proposta do projeto é atualizar **esse texto** (amarra com o slide 1).
- Fechamento da fala: "guardem a imagem — erro no passo, mensagem no próximo prompt, execução acaba, tudo descartado. O próximo slide mede exatamente isso."

### Fontes

`05-schema.md` (base 1 — tipos de step) · `08-overview-granularidade.png` (base 1 — ActionStep × TaskStep × PlanningStep) · `01-racionais.md` (base 3 — a janela de contexto do erro) · recorte real via `drill_down.py` (mesmo caso do anexo G, máquina 2)

---

## Slide 3 — O agente pode ler o erro e voltar a errar ✅

**Função:** a justificativa empírica. Antes de dados ou método, responder "por que um mecanismo de memória é necessário?" — posicionado **antes** das bases, porque o achado de reincidência é a peça que sustenta a tese do deck.

**Mensagem principal (uma frase):** "O problema não é falta de feedback — é falta de persistência. O agente vê o erro, corrige na hora, e o mesmo erro volta em execuções futuras."

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│ MEMÓRIA PARA AGENTES / EVIDÊNCIA                            │
│ A NECESSIDADE                                               │
│ O agente pode ler o erro e voltar a errar                   │
│                                                             │
│ ┌── FUNIL (base 1) ──┐   ┌── CARD: custo ──┐                │
│ │ 498 erros          │   │ execução c/ erro │                │
│ │  ↓ 430 (86,3%)     │   │ ≈3× mais tokens  │                │
│ │ mensagem chega ao  │   │ (146k vs 48k)    │                │
│ │ passo seguinte     │   │                  │                │
│ │  ↓ 51 (11,9%)      │   ├── CARD: tempo ───┤                │
│ │ repete a MESMA     │   │ mesmo mecanismo  │                │
│ │ assinatura         │   │ em 10/11 meses   │                │
│ └────────────────────┘   └──────────────────┘                │
│                                                             │
│ nota: reincidência = dentro do subconjunto cujo erro chegou │
│ ao contexto; não é taxa de falha geral                      │
└─────────────────────────────────────────────────────────────┘
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Visual principal — funil** | 498 erros → 430 (86,3%) com mensagem no passo seguinte → 51 (11,9%) que repetem a **mesma assinatura** |
| **Card custo** | Execução com erro custa ≈3× mais tokens (mediana 146 mil vs 48 mil na base 1) |
| **Card tempo** | O mecanismo "texto longo em literal" reaparece em 145 execuções, em **10 dos 11 meses** |
| **Nota técnica** | 11,9% é reincidência imediata dentro do subconjunto cuja mensagem chegou ao contexto — não taxa geral de falha |

### De onde vêm os dados

| Número | Valor | Fonte |
|---|---|---|
| Erros na amostra | 498 | `analysis/2026-09-trace-law-flow/docs/02-relatorio-achados.md` §4 |
| Mensagem visível no passo k+1 | **430 (86,3%)** | mesmo doc, §4 — robusto a 3 métodos (84,9–86,3%) |
| Repete a mesma assinatura | **51 (11,9%)** | mesmo doc, §4; por mecanismo: 58 (13,5%) |
| Mecanismo recorrente | 145 execs, **10/11 meses** | mesmo doc, §4 |
| Custo com erro | mediana **146k vs 48k** tokens | mesmo doc, TL;DR + §3.1 |
| Todas se recuperam | 100% `final_answer`; 99,3% com conteúdo | mesmo doc, §3.1 — fala: problema é custo/recorrência, não falha fatal |

### Gráficos — o que existe vs. o que criar

| Visual | Status |
|---|---|
| Funil 498 → 430 → 51 | **Desenhar como formas nativas** (não existe como PNG — é tabela no §4) |
| Custo execução c/ vs s/ erro | **Existe na base 3:** `taxas_custo_execucao.png` — checar na máquina 2; se não houver, usar a mediana da base 1 |
| Faixa de meses (10/11) | Mini-faixa nativa com os meses marcados; ou conferir se há painel "assinatura × mês" na base 1 |

### Observações de fala

- "E se o agente se recupera depois?": recupera — 100% terminam com resposta. O problema é **custo + reincidência**, não crash.
- "O próprio LLM não corrige?": corrige dentro da execução; entre execuções o contexto é descartado — é a diferença entre **recuperação** e **aprendizagem**.
- Título alternativo mais forte (opcional): *"Se o agente vê o erro, por que volta a errar?"*

---

## Slide 4 — Três bases, dois regimes: a amostra explica a causa; o sistema mede a escala ✅

**Função:** inventário honesto das fontes — o stakeholder confia nos números quando sabe de onde vêm e o que cada base não vê.

**Mensagem principal (uma frase):** "As amostras completas provam por que o agente erra; a base 3 mede todos os erros do sistema atual — quanto custam, como o agente reage e se a lição recorre."

### Layout

```
┌─ AMOSTRAS PROFUNDAS ──────┐ ┌─ SISTEMA ATUAL · BASE 3 ★ ────────┐
│ BASE 1  1.000 execs       │ │ dados nov/2025–ago/2026 (10 m.)   │
│         out/25–ago/26     │ │ ┌─ FUNIL da rodada (PNG) ──────┐  │
│         5.781 passos      │ │ │ 71.881 execs → 283.925       │  │
│         498 erros         │ │ │ passos → 30.141 erros        │  │
│ BASE 2  1.000 execs       │ │ │ (20.442 execs com erro)      │  │
│         dez/25–ago/26     │ │ └──────────────────────────────┘  │
│         (9 m.; 88% jun–ago)│ │                                  │
│         3.907 passos      │ │                                   │
│         479 erros         │ │                                   │
│                           │ │ CADA LINHA = um erro + janela:    │
│ trace completo: prompt,   │ │ ┌────┐┌────┐┌────┐┌────┐          │
│ código, trajetória,       │ │ │n−1 ││ n  ││n+1 ││n+2 │          │
│ resposta — a CAUSA do     │ │ └────┘└────┘└────┘└────┘          │
│ erro está no trace        │ │ código · pensamento · ferramenta ·│
│                           │ │ observação · tokens da janela ·   │
│ lacuna: amostras de 1.000 │ │ sinal de recuperação              │
│                           │ │                                   │
└───────────────────────────┘ └───────────────────────────────────┘
O QUE CADA FONTE VÊ (faixa nativa, ✓/✗):
            prompt/   trajetória+   reação ao    população+
            modelo    resposta      erro         taxa real
amostras      ✓           ✓          ✓ completa     ✗ amostra
base 3      ✗           ✗          ✓ até n+2      ✓ 10,6%
rodapé: linha = ActionStep c/ erro · janela só de ActionSteps ·
recovery_signal ≠ sucesso · bases não se somam · só vê erros que
levantaram exceção (silenciosas ficam fora)
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Card amostras** | Bases 1–2 agrupadas: trace completo — a causa do erro está no trace; lacuna: amostras de 1.000 |
| **Card base 3 ★** | **Funil real da rodada** (PNG da máquina 2: 71.881 execs → 283.925 passos → 30.141 erros em 20.442 execs) — a população como figura, não texto; embaixo, **diagrama nativo da janela** `[n−1] [n] [n+1] [n+2]` |
| **Matriz "o que cada fonte vê"** | Faixa nativa ✓/✗: amostras veem prompt/modelo, trajetória e resposta; base 3 vê população, taxa real e reação (até n+2) — substitui os blocos VÊ/RESPONDE/NÃO VÊ |
| **Rodapé técnico** | Linha = ActionStep com erro/suspeita; janela só de ActionSteps; `recovery_signal` ≠ veredicto de sucesso; bases não se somam; só vê erros que levantaram exceção |

### O que a base 3 responde (para a fala)

| Pergunta | Responde? |
|---|---|
| Erro + código + pensamento | Sim |
| O que vinha antes (n−1) | Sim |
| Reação (n+1, n+2) | Sim |
| Recuperação | Parcial — `recovery_signal` é sinal, não ground truth |
| Custo erro + reação | Sim (janela de tokens/tempo) |
| Taxa real | Sim — 10,6% dos passos |
| Concentração papel/mês | Sim |
| Cascatas | Sim (execs com até 26 erros) |
| Prompt/modelo/trajetória | **Não** |
| Sucesso final real | **Não** |
| Após n+2 | **Não** |

### Fontes

`05-relatorio_mineracao_20260929.md` (schema da base minerada) · `02-relatorio-achados.md` §§1–7 · `02-relatorio-base2.md` · funil da parte 2 do painel (`<rodada>/taxas/`, máquina 2)

**Recortes (datas exatas, por `hor_dat_inicio`):** base 1 = out/2025–ago/2026 (11 meses) · base 2 = dez/2025–ago/2026 (9 meses, 88% em jun–ago; "lote de ago/2026" é o nome da extração/`anomesdia`, não o recorte) · base 3 = dados nov/2025–ago/2026 (10 meses; a query cobre execs ago/2025–set/2026)

### Decisões fechadas

- Sem as três imagens de overview no corpo — vão ao anexo ("as três bases lado a lado").
- Card da base 3 destacado como "a fonte de escala"; **funil real da rodada como PNG** no card (buscar na máquina 2; plano B: `taxas_mes.png` aqui e `taxas_papel.png` no slide 5) + diagrama nativo da janela.
- **Sem "falhas silenciosas" no corpo** — o conceito pede explicação que o slide não reusa; fica uma linha de caveat no rodapé técnico.
- **Sem faixa-ponte `try/except`** — o caso volta no slide 7 (destinos, sinal de harness), onde tem contexto para fazer sentido.
- **Matriz ✓/✗ "o que cada fonte vê"** substitui os blocos de texto VÊ/RESPONDE/NÃO VÊ dentro dos cards.

---

## Slide 5 — Escala: o problema é grande — e concentrado o suficiente para ser atacável ✅

**Função:** quantificar o problema na população — volume, taxa e custo — antes de qualquer método. Primeiro slide de achado do deck.

**Mensagem:** "10,6% de todos os passos falham e concentram 15,9% do gasto — e o erro se concentra em poucos papéis e meses, o que torna a memória direcionável."

### Layout

```
┌─ MÉTRICAS (faixa no topo) ────────────────────────────────────┐
│ 30.141 erros · 20.442 execs c/ erro · 592,9 mi tokens em erro │
│ (15,9% dos 3.729,3 mi do sistema)                             │
└───────────────────────────────────────────────────────────────┘
┌─ HERO: painel duplo ──────────┐ ┌─ TABELA (10 linhas) ──────────┐
│ barras: erros absolutos/mês   │ │ mês · passos · erros · taxa   │
│ 1.086 → 1.797 → 17.485        │ │ nov 446 · · 7,2%              │
│ linha: taxa oscila            │ │ jan ···· · 1.086 · 16,4%      │
│ 16,4% → 4,1% → 15,7%          │ │ jun ···· · 1.797 · 4,1%       │
│ (diluição, não melhora)       │ │ ago 111.373 · 17.485 · 15,7%  │
└───────────────────────────────┘ └───────────────────────────────┘
faixa: agosto = 58% dos erros · 2 papéis ≈ 60% das candidatas
rodapé: taxa mistura papéis e prompts — não é causal ·
"erro é erro": inclui o sinal de harness (decisão 15/10)
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Faixa de métricas** | 30.141 erros · 28,4% das execuções com erro (20.442 de 71.881; as 20.986 do parquet contam erro **ou suspeita**) · 592,9 mi tokens em passos com erro (15,9% de 3.729,3 mi) — fatia do gasto, não economia |
| **Figura herói** | **Painel duplo (produzir na máquina 2): erros absolutos por mês (barras) × taxa por mês (linha)** — a taxa oscila com o mix de papéis, mas o erro absoluto cresceu 16× de jan a ago. Variação da `taxas_mes.png`; os dados já existem (`taxas_por_mes.csv` + contagens) |
| **Tabela mês × passos × erros × taxa** | 10 linhas, do `taxas_por_mes.csv` (máquina 2) — a série completa que a figura resume; destaque nas linhas jan / jun / ago |
| **Faixa concentração** | agosto/26 = 58% dos erros observáveis (17.031/29.392) · 2 papéis ≈ 60% das candidatas — a concentração torna a injeção direcionável |
| **Rodapé técnico** | taxa mistura papéis e prompts — não é causal; "erro é erro" (inclui sinal de harness — decisão de 15/10) |

### Observações de fala

- **"Por que a taxa caiu de 16,4% para 4,1% e voltou para 15,7%?"** — a própria figura responde: **os erros absolutos não caíram** (1.086 jan → 1.797 jun → 17.485 ago); a taxa caiu porque o denominador cresceu mais rápido — entraram papéis novos e mais leves (junho: ×4,2 execuções de maio). É diluição por mix, não melhora — e agosto mostra que o erro volta quando o mix muda. A prova definitiva é a taxa por papel fixo (roadmap #37) — um dos dados do pedido. Agosto: o `try/except` explica parte (sem ele: 10,6% × 6,6% jul) — não todo.
- A amarra do slide: **"o problema não se dilui com o crescimento — cresce junto; sem memória, a conta só aumenta."**
- "Essa taxa não é culpa do try/except?": em parte — por isso "erro é erro" na nota; a separação por destino vem no slide 7, depois do método.
- "15,9% é economia?": não — é a **fatia do gasto que está em passos com erro**; o que vira economia é conta do slide 10.

### Fontes

`02-relatorio-achados.md` §§1, 7.4, 7.5 · `04-roadmap.md` #26/#32/#36/#37 · painel duplo erros×taxa (produzir na máquina 2; plano B: `taxas_mes.png` + série de erros no card, ou `taxas_papel.png` com a concentração virando texto)

---

## Slide 6 — O método: dois eixos de leitura — um descreve, outro decide ✅

**Função:** explicar a taxonomia antes dos destinos — os baldes do slide 7 só existem por causa deste roteamento. Antecipar as duas perguntas naturais ("foi regex?" e "por que família e depois ainda mais níveis?").

**Mensagem:** "O sintoma — o que o sistema reclamou — descreve e cataloga; o mecanismo — o que o agente fez de errado — decide a lição. Regras determinísticas sobre o texto, reabíveis no caso cru, sem LLM."

### Layout

```
   ┌────────── EIXO SINTOMA — descreve (censo · proveniência) ──────────┐
   │   classify() lê SÓ a mensagem de erro                              │
   │                                                                   │
   │   30.141 erros ──► assinatura ──► família (censo + catch-all,      │
   │                                   que detecta erro novo)          │
   └────────────────────── NÃO decide nada ───────────────────────────┘

   ┌────────── EIXO MECANISMO — decide ─────────────────────────────────┐
   │   submecanismo() lê a mensagem + a linha de código rejeitada       │
   │   (o "salto de evidência" que o sintoma nunca toca)                │
   │                                                                   │
   │   erros ──► mecanismo ──► unidade ──► triagem ──► destino          │
   │             1:N divide     N:1 funde    3 perguntas:               │
   │             "mesma          "uma frase   é memória?                │
   │              reclamação,    de memória   tem conteúdo              │
   │              causas         previne      único? recorre            │
   │              diferentes"    todas?"      entre execs/meses?"       │
   └───────────────────────────────────────────────────────────────────┘
exemplo: "Could not index" — o classify() vê 1 sintoma; o submecanismo()
separa 3 causas lendo a linha rejeitada (dict como lista · string como
dict · chave inexistente) — 3 consertos diferentes (caso real trabalhado
no anexo H)
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Duas lanes, não uma árvore** | eixo sintoma (describe) paralelo ao eixo mecanismo (decide) — a relação entre eles é muitos-para-muitos, por isso o desenho são duas trilhas, não uma hierarquia |
| **Como é feito** | regras determinísticas **em ordem** sobre o texto da mensagem (+ balde catch-all); o mecanismo lê um sinal a mais: a linha de código rejeitada. Cada erro é reabível no caso cru |
| **Por que família E assinatura** | assinatura → família é N:1 por construção: a família é o censo grosso (o que o sistema mais reclama), a assinatura é a chave fina de busca/proveniência. As duas só descrevem |
| **Por que mecanismo separado** | o mesmo sintoma admite causas com consertos diferentes; só o sinal local mais fino separa — sem ele, uma "lição" misturaria curas contraditórias |
| **Recorte real (inset)** | um erro com as **duas entradas**: a mensagem (o que o sintoma vê) e a linha rejeitada (o que só o mecanismo lê) — mesmo tratamento do inset do slide 2; o trio A/B/C trabalhado completo fica no **anexo H** |
| **Sem LLM** | a taxonomia é a base que valida os achados; um classificador neural seria mais uma afirmação a validar, não fundação. Determinístico = auditável, reproduzível, sem custo por chamada |
| **Literatura como bancada, não como fonte** | a taxonomia nasceu do trace; TRAIL sugeriu os detectores de falha silenciosa e o teste de cobertura; AgentDebug, o princípio "causa-raiz, não sintoma"; o MAST não tinha modo de falha para "o código levantou exceção" — a lacuna que cobrimos |
| **Prova** | cobertura 97,5% (a regra decide em 29.392 dos 30.141); resíduo 1,9%; auditoria independente re-rodou com 0 divergências; régua de candidatura: recorre em ≥3 execuções e ≥2 meses |
| **Gráfico** | `genealogia_observada.png` (rodada real) — o Sankey com as contagens reais por nó/aresta; versão base 1 no anexo A |

### Observações de fala

- **"Foi regex?"** — regras determinísticas sobre o texto e a linha rejeitada, sim — e é de propósito: cada classificação reabre no caso cru, e a mesma regra roda igual em qualquer base (é o que fez a base 2 e a 3 comparáveis à 1).
- **"Por que não pediu a um LLM para classificar?"** — a taxonomia é o instrumento de medida do projeto; medir com um modelo seria caro, não-reprodutível e transformaria a régua em mais uma coisa a validar.
- **"Por que dois eixos em vez de uma árvore?"** — porque a mesma reclamação esconde causas diferentes (1:N) e causas diferentes convergem para a mesma lição (N:1). Árvore é 1:1; aqui é muitos-para-muitos.
- **"De onde saiu a taxonomia?"** — do trace; a literatura testou e deu vocabulário, não entregou categorias prontas.
- **Gancho para a genealogia (caso real):** uma assinatura só — "resposta sem bloco de código" — abriu em seis mecanismos com donos diferentes: a ferramenta `resposta_final` concorrendo com o `final_answer` e o contrato `json_resposta` induzindo o erro (o prompt/contrato induz → sinal de harness); o modelo errando a marca do envelope (→ não-memória, o prompt já ensina); a API entregando fragmento vazio (→ plataforma). É o slide 7 em miniatura: o sintoma não decide o dono, o mecanismo decide.

### Fontes

`09-metodologia-erro-a-memoria.md` (a genealogia, instanciada — o trio A/B/C do "Could not index") · `general-error-taxonomy-methodology.md` (o método, elos E0–E4) · `01-racionais.md` §8 (TRAIL/AgentDebug/MAST/ToolScan como bancada) · `genealogia_observada.png` (rodada, máquina 2)

---

## Slide 7 — Para onde vão os erros: lição do agente × ajuste nosso ✅

**Função:** mostrar o resultado do roteamento — e definir cada destino: o que a memória trata, o que a squad trata, e o que ainda é trabalho da taxonomia.

**Mensagem:** "O roteamento separa a lição do agente do problema do próprio sistema — e o maior erro isolado é nosso, não do agente."

### Layout

```
┌─ HERO: destinos.png (rodada real) ──────────────────────────────┐
│ faixas erros × tokens: candidatas 57%/65% · sinal harness       │
│ 19%/19% · harness/infra 19%/11% · resíduo/pendente/crítico ~5%  │
└─────────────────────────────────────────────────────────────────┘
┌─ O QUE CADA DESTINO É (tábua nativa) ───────────────────────────┐
│ memória     lição que o agente pode aprender → texto na memória │
│             (dono: o projeto — e é degrau 1 de 4, slide 8)      │
│ sinal de    erro DO agente, conserto NO harness da esteira —    │
│ harness     a instrução que demos contradiz o ambiente;         │
│             memória não trata, a squad ajusta o prompt/contrato │
│ harness/    o modelo viola o contrato de saída que o próprio    │
│ infra       prompt ensina, ou a plataforma falha — sem bloco de │
│             código, timeout, falha do LLM upstream; não é       │
│             lição de tarefa: conserto é formato/parser,         │
│             retry/monitoramento (squad)                         │
│ resíduo /   a regra não reconheceu / faltou dado na extração /  │
│ pendente /  a execução morreu — filas de trabalho da taxonomia, │
│ crítico     da query e da investigação                          │
└─────────────────────────────────────────────────────────────────┘
┌─ CALLOUT ───────────────────────────────────────────────────────┐
│ O maior erro isolado (5.764 erros, 112 mi tokens) é um sinal de │
│ harness: o prompt do ContestacaoCivel instrui um try/except que │
│ o sandbox não suporta — o agente segue a instrução e quebra.    │
│ Um ajuste de prompt elimina ~19% dos erros ANTES de qualquer    │
│ piloto de memória.                                              │
└─────────────────────────────────────────────────────────────────┘
rodapé: foto de 14/10, pré-Ajuste 21–23 (a reclassificação do
U_sandbox muda as faixas) · candidata = degrau 1 de 4 (slide 8)
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Figura herói** | `destinos.png` (máquina 2) — faixas por destino em erros × tokens; os tokens mostram que a candidata dói mais por erro (≈22,4 mil/erro vs ≈11,2 mil harness/infra) |
| **Tábua de destinos** | as definições: memória (o projeto trata) · sinal de harness (a squad ajusta o prompt/contrato) · harness/infra (a squad trata com política operacional) · resíduo/pendente/crítico (trabalho da taxonomia, da query e da investigação) |
| **Callout try/except** | o maior erro isolado é defeito nosso com conserto conhecido — retorno mais barato do deck |
| **Apoio** | 3 candidatas concentram 75% dos erros das candidatas e 85% dos tokens delas — as três de contrato com o ambiente |
| **Rodapé técnico** | figura de 14/10 é pré-Ajuste 21–23 (o `U_sandbox` foi reclassificado depois — faixas mudam na próxima rodada); candidata = degrau 1 de 4 |

### Observações de fala

- "Por que sinal de harness não vira memória?" — porque a instrução está errada: escrever memória seria ensinar o agente a desobedecer o próprio prompt. O conserto é na esteira, e a squad pode fazer já.
- "E a diferença para harness/infra?" — no sinal de harness o erro é do agente (ele obedeceu uma instrução ruim); em harness/infra quem falhou foi o protocolo ou a plataforma.
- **"Esse erro 'sem bloco de código' é família ou unidade?"** — os três níveis respondem juntos: família "Protocolo do harness" → assinatura "Resposta sem bloco de código" → unidade `H_bloco_code` (4.592 erros, a maior não-memória). Dentro dela, a investigação da base 1/2 separou seis mecanismos com donos diferentes: a ferramenta `resposta_final` concorrendo com o `final_answer` e o contrato `json_resposta` induzindo (→ sinal de harness, corrigido jan/2026); o modelo errando as marcas do envelope (→ não-memória, o prompt já ensina); a API entregando fragmento (→ plataforma). Transformar esse catálogo em regra determinística é a próxima etapa do método.
- "Candidata já vira memória?": não — é degrau 1 de 4; a governança é o slide 8.

### Fontes

`02-relatorio-achados.md` §3, §7.2, §7.8–7.10 · `04-roadmap.md` #40 (figura de destinos) · destinos.png (máquina 2; foto histórica até a próxima rodada)

---

## Slide 8 — Como uma candidata vira memória: o processo e a escada ✅

**Função:** ensinar o instrumento antes do caso — o pipeline que leva uma unidade candidata até memória pronta para injeção, e a escada de 4 degraus que decide quando ela está pronta. Responde "como chegamos a esses resultados" antes do slide 9 mostrar um.

**Mensagem:** "Cada número do caso sai de um script versionado que roda igual nas três bases — e 'catalogada' é só o degrau 1 de 4; até o degrau 4, a memória é hipótese com evidência."

### Layout

```
┌─ O PIPELINE: de unidade a candidata (detalhe: anexo I) ──────────┐
│                                                                 │
│  TRIAGEM        INVENTÁRIO       INVESTIGAÇÃO     ARQUIVO FINAL │
│  a taxonomia    o script conta   a hipótese tem   o script      │
│  roteia os      o que os erros   de ser testada   monta a       │
│  erros nas      têm em comum     nas bases; a     guidance e    │
│  unidades       → as partes      evidência decide o catálogo    │
│                 com dono         o destino                      │
│                 próprio                                         │
│                                                                 │
│   unidade ──►    partes     ──►   destino por ──►  CANDIDATA    │
│  candidata     com dono           parte          catalogada     │
│                                                                 │
│  auditoria independente mede junto em cada etapa — encontro     │
│  medida a medida (sandbox, 21/10: 77/77 iguais)                 │
└─────────────────────────────────────────────────────────────────┘
┌─ A ESCADA: quando a memória está pronta para injetar (anexo J) ──┐
│                                                                 │
│  1 CANDIDATA   2 CONFERIDA     3 REVISADA      4 VALIDADA       │
│  o erro existe a lição é       a causa é       injetada, reduz  │
│  assim e com   coerente com    mesmo a que     o erro sem       │
│  essa          o ambiente      a regra supõe?  criar outro?     │
│  frequência?   e o prompt?                                    │
│  ─────────     ─────────       ─────────       ─────────        │
│  determiníst.  determinístico  2 leitores às   experimento:     │
│  (a mineração) (5 checagens:   cegas + gate    reprodução +     │
│                 ambiente,      do pesquisador  compensação      │
│                 conflito,          │           antes × depois   │
│                 repete,            ▼                            │
│                 recorrência,   PRONTA PARA     (a POC mínima —  │
│                 1 causa só)    INJETAR          o degrau 4)     │
└─────────────────────────────────────────────────────────────────┘
rodapé: "até o degrau 4, a memória é hipótese com evidência" ·
catalogada prova que o erro existe — não que a memória ensina
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **Pipeline** | as 4 etapas macro do procedimento: triagem (a taxonomia do slide 6 roteia os erros nas unidades) → inventário (o que os erros têm em comum; script específico da unidade) → investigação (a hipótese é testada nas bases; a evidência decide o destino, não o sintoma) → arquivo final (guidance + catálogo `memorias.json`); a auditoria independente roda em paralelo e o encontro confere medida a medida |
| **Escada** | os 4 degraus de `17-validacao-memorias.md`, cada um com a sua pergunta e o seu instrumento: 1 candidata (determinístico) → 2 conferida (5 checagens por script: ambiente, conflito com o prompt, repete o prompt, recorrência, uma causa só) → 3 revisada (leitura de casos, 2 leitores às cegas, concordância medida, gate do pesquisador) → 4 validada (o experimento: reprodução + compensação antes × depois) |
| **Marco de injeção** | depois do degrau 3 (revisada) a memória está pronta para injetar; o degrau 4 é a própria injeção medida — a POC mínima — e só aí "candidata" vira "memória validada" |
| **Rodapé técnico** | cada etapa é script versionado, a mesma regra nas três bases · "catalogada" prova existência, não eficácia · pipeline em detalhe no anexo I, escada no anexo J |

### Observações de fala

- **"Por que inventário antes de destino?"** — não dá para rotear o que não foi contado; é o inventário que revela as partes com donos diferentes (o slide 9 mostra o caso).
- **"A auditoria audita o quê?"** — um script independente recalcula cada medida da mineração; o encontro compara medida a medida (sandbox, 21/10: 77/77 iguais).
- **"Por que 4 degraus e não 'aprovado/reprovado'?"** — porque cada degrau responde uma pergunta diferente com um instrumento diferente: existência ≠ coerência ≠ causa ≠ eficácia.
- **"Quando injeta de verdade?"** — depois do degrau 3, e só na POC mínima controlada (o blueprint das POCs; o pedido é o slide 12).
- **"E se a memória falhar num degrau?"** — volta para o dono certo: falha de ambiente/conflito vira ajuste de prompt (sinal de harness, slide 7); falha de recorrência entra na régua de memória rara; o slide 9 mostra as duas.

### Fontes

`06-procedimento-mineracao-candidatas.md` (o procedimento desta base) · `17-validacao-memorias.md` (a escada e as 5 checagens) · kit de mineração `.claude/skills/mineracao-base/referencias/kit.md` · `registros/memorias.json` + `esquema-memoria.json` · `decisoes.md` 19–20/10 · `pocs/blueprint-m1-pocs-minimos.md` (o degrau 4)

---

## Slide 9 — Caso sandbox: um rótulo, várias causas — e a maior era o nosso prompt ✅ (em fechamento)

**Função:** prova do método num caso real — a unidade que parecia uma lição única abriu, depois do pipeline (slide 8),
em grupos com causas e donos diferentes. Responde "por que não escrever memória direto do rótulo".

**Mensagem:** "'Sandbox' não era uma memória: um rótulo agrupava várias causas — e 69% dele era o nosso prompt."

**Estado:** a unidade ainda não fechou (decisões abertas abaixo); o slide mostra a rodada `99e032ad` (21/10) e diz isso
no rodapé. Substitui a versão de 19/10 (rodada `aedb9b5d`), cuja moral — "A e B igualmente concentrados, destinos
opostos" — caiu quando a maior parte do B (167 de 211, o `get_document_text`) também virou harness (Ajuste 26).

### Layout

```
┌─ A UNIDADE ─────────────────────────────────────────────────────┐
│ U_sandbox · "o agente escreve código com um nome que o sandbox  │
│ recusa" · 3.653 erros em 14/10 · 2ª maior candidata da triagem  │
└─────────────────────────────────────────────────────────────────┘
┌─ ERRO NOSSO → HARNESS ──────┐ ┌─ FICA NO SANDBOX · 1.100 · 17 memórias ─┐
│ 2.518 (69%)                 │ │ C json/re/datetime  423  memória global  │
│ verificação de existência   │ │ E depuração         317  memória global  │
│ (ContestacaoCivel)          │ │ C pd (Joogle)       231  memória do papel│
│   2.217 + 134               │ │ B framework (OBF)    44  memória papel ⚑ │
│ ferramenta citada sem ser   │ │ D fora da lista      40  reforço          │
│ declarada (OBFCivel) 167    │ │ F como verificar     37  em aberto        │
│ + 35 eval por outra regra   │ │ raras                 3  monitoradas      │
└─────────────────────────────┘ └──────────────────────────────────────────┘
┌─ CONCENTRADO NÃO DECIDE ─────┐ ┌─ DEGRAU 2 ─────────────────────────────┐
│ verificação (1 papel) →      │ │ 3 passam: C global, C do Joogle, E —   │
│ harness; pd (231/233 num     │ │ 971 erros, 88% do que ficou · D repete │
│ papel) → memória do papel    │ │ o prompt · ⚑ B do OBFCivel em decisão  │
└──────────────────────────────┘ └────────────────────────────────────────┘
rodapé: em fechamento — rodada 99e032ad (21/10): 9 passos, cobertura 99,6%,
77 medidas iguais · abertos: B do OBFCivel, managerAgent na C global, parte F
```

### De onde vêm os números

| Número | Valor | Fonte |
|---|---|---|
| Trajetória da unidade | 3.653 → 1.436 (Ajuste 21, −2.217) → 1.401 (Ajuste 23, −35) → 1.100 (Ajustes 26 e 27, −167 −134) | dossiê §1, §2b, §2d, §2h item 11 |
| Harness | 2.217 + 134 (verificação) + 167 (`get_document_text`) = 2.518 = 68,9% de 3.653 | idem |
| Partes que ficam | C 423 · C.JoogleAnalytics 231 · C.CalculoTrabalhista 2 · E 317 · B.OBFCivel 44 · B.RespostaBacen 1 · D 40 · F 37 · sem nome 5 = 1.100 | dossiê §2h item 11 |
| Degrau 2 | depois do Ajuste 28, prompt da base 1 | dossiê §2h item 22; `decisoes.md` 21/10 |
| 971 erros, 88% | 423 + 231 + 317 de 1.100 | idem |

O 73% da versão de 19/10 era a primeira leitura (a parte A inteira, 2.667, antes da regra); o slide usa o que a regra
moveu, medido.

### Observações de fala

- **"Por que cada grupo foi para aquele destino?"** — se a instrução veio do prompt, o conserto é no harness; se é do
  agente em qualquer papel, memória global; se depende da lista daquele papel, memória do papel.
- **"A verificação é caso novo?"** — não: é o mesmo defeito do callout do slide 7 por outro sintoma (julho `globals()`,
  agosto `try/except`; anexo L).
- **"O `json` no RoteadorCivel não é o prompt?"** — não: o import funciona no papel e o agente se corrige no passo
  seguinte em 9 de 10 — esquecimento do agente, memória (decisão de 21/10). O que o prompt tem de errado é outra coisa
  (anexo M).
- **"As 17 já são memória injetada?"** — não: catalogadas, degrau 1; três passaram o degrau 2.

### Fontes

`propostas/U_sandbox/dossie_base3.md` §§1, 2b, 2d, 2h (itens 8–22) · `decisoes.md` 19–21/10 · `registros/memorias.json`
(rodada `99e032ad`)

---

## Slide 10 — O custo de não aprender: o erro mora na cauda cara ✅

**Função:** responder "quanto vale mitigar esses erros?" com honestidade — não prometer ROI, mostrar que o custo de não aprender cresce com o sistema, que o erro concentra na cauda que carrega o gasto, e que a régua para decidir se compensa injetar já existe.

**Mensagem:** "O custo de não aprender não é pequeno: o erro cresce junto com o sistema e concentra onde o dinheiro está. Já temos o teto — 13,4% do gasto atacável pelo mesmo loop — e a régua que diz quando a memória compensa; a eficácia é o que o piloto mede."

### Layout

```
┌─ O ERRO ESCALA E CONCENTRA ─────────────────────────────────────┐
│ no tempo:  erros jan 1.086 → ago 17.485 (16×) — sem memória,    │
│            o erro escala junto com o sistema                    │
│ no custo:  execuções com erro por recorte de custo (curva de    │
│            concentração): todas 28% → 10% mais caras 50% →      │
│            1% mais cara 81% (10% = 64% do gasto · 1% = 21%)     │
└─────────────────────────────────────────────────────────────────┘
┌─ O QUE É ATACÁVEL HOJE (em tokens, não R$) ─────────────────────┐
│ 592,9 mi em erros → 387 mi memória + 112 mi harness = 499 mi    │
│ = 13,4% do gasto dentro do mesmo loop de self-improvement       │
│ régua: injetar compensa se memória < eficácia × orçamento       │
│ orçamento máximo: 1.363 t/passo (todas) · 729 (só a maior       │
│ unidade) · com eficácia 25%: ~341                               │
└─────────────────────────────────────────────────────────────────┘
┌─ DUAS SAÍDAS DA MESMA EVIDÊNCIA ────────────────────────────────┐
│ erro NOSSO → ajuste de prompt — barato, já pode fazer           │
│ erro do AGENTE → memória — o piloto mede se compensa            │
└─────────────────────────────────────────────────────────────────┘
rodapé: teto = hipótese — conta o passo que falhou, não a cascata
de recuperação nem a qualidade da resposta entregue · execução
com erro ~4,3× os tokens (parte é mix de papéis, #37) · teto e
split são a foto de 14/10 (pré-Ajuste 21–23 — a reclassificação
do U_sandbox muda a divisão 387/112; o total 13,4% se mantém) ·
série mensal e concentração com a data da própria rodada · as
conclusões são o próximo slide
```

### Elementos

| Elemento | Conteúdo |
|---|---|
| **A curva que não para** | erros absolutos jan → ago (16×) — o mesmo dado do slide 5, agora como argumento de custo: sem aprendizado, o erro escala com o sistema (e mais papéis entrando, mais erros por vir) |
| **A cauda cara** | a curva de concentração medida: 10% das execuções mais caras = 64% do gasto; **50% dessas têm erro vs 28% no total** — o erro está ~1,8× mais presente na cauda que concentra o dinheiro. Descrição, não prova causal (a mesma mistura de papéis do #37 pode explicar parte) — mas consistente com o 1,6× por passo e o ~4,3× por execução: três medidas, mesmo sentido. **Conferido** na figura `taxas_concentracao.png` (foto `IMG_5846`) e no funil (`IMG_5842`: 28,4% = 20.442 de 71.881); no deck a figura da rodada entra ao lado do texto |
| **O atacável** | 387 mi (memória) + 112 mi (sinal de harness) = 499 mi = 13,4% do gasto — o sinal de harness entra porque o loop de self-improvement conserta o erro nosso (prompt) e o do agente (memória). **Pendência:** o split é a foto de 14/10; pós-Ajuste 21–23 a divisão muda (parte do `U_sandbox` virou sinal de harness) e precisa ser atualizada na próxima rodada — o total 499 mi / 13,4% se mantém porque os dois destinos ficam dentro do loop |
| **A régua** | a matemática da decisão pronta: `memória < eficácia × orçamento`; orçamento máximo 1.363 tokens/passo (todas as candidatas, todos os passos) e 729 (só `U_tipo_retorno`); com eficácia 25% cai a ~341 — para dimensionar, não para prometer |
| **O garfo** | a contribuição do projeto: a mesma evidência separa o dono — "corrige o prompt" (barato, já) × "escreva a lição" (o piloto mede) |
| **Rodapé técnico** | teto = hipótese com os 5 descontos do §7 · conta o passo que falhou, não a cascata nem a qualidade do `final_answer` · ~4,3× tem mix de papéis dentro (#37) · datas por bloco: teto e split são a foto de 14/10 (pré-Ajuste 21–23 — o split recalcula; o 13,4% se mantém), série mensal e concentração com a data da própria rodada · sem preço por modelo, não vira R$ |

### Observações de fala

- **"13,4% é pouco?"** — é o que já é atacável pelo loop hoje. E o valor maior não é a economia medida em tokens (pequena se isolada): é que um sistema que não aprende erra na proporção do crescimento — e o erro senta na cauda que carrega o gasto.
- **"50% com erro prova que o erro causa o custo?"** — não sozinho: é associação; parte pode ser mistura de papéis (o papel pesado erra mais). Mas três medidas independentes apontam o mesmo lado: 1,6× por passo, ~4,3× por execução, erro ~2× mais presente na cauda cara.
- **"E o erro que o agente recupera e entrega?"** — custa tokens de recuperação (dentro do 4,3×) e pode custar qualidade de resposta — o `final_answer` ainda não foi medido; é o que a janela completa (#15) e o experimento medem.
- **"Por que não em R$?"** — falta o preço por modelo; medimos em tokens, a unidade que o sistema gasta — com o preço, a conversão é uma multiplicação.
- **"E se a eficácia for baixa?"** — a régua responde antes do piloto: com 25%, o orçamento cai a ~341 tokens/passo — a memória teria de ser curta; com 10%, ~136 — talvez não compense, e saber isso antes é o ponto.

### Fontes

`01-racionais.md` §7 (teto, orçamento, teste de compensação) · `02-relatorio-achados.md` §7.2, §7.5 · `04-roadmap.md` #36–#40 (gráficos 4–6 da parte 2: custo com × sem erro, Lorenz, custo mensal) · `taxas_orcamento_papel.png` e a curva de concentração (máquina 2; correções do #40 registradas)

---

## Slide 11 — O que os números mandam: quatro conclusões ✅

**Função:** condensar a evidência dos slides 5–10 em fato → padrão → implicação → ação; a alavanca do slide 12.

**Mensagem:** "O erro não é periferia: cresce com o sistema, senta no centro do custo, e já sabemos onde mirar o conserto."

| Etiqueta | Conclusão | Evidência (slide) |
|---|---|---|
| FATO | O erro não é periferia: é núcleo do custo | 10,6% dos passos, 15,9% dos tokens; 28,4% → 50% → 81% (5, 10) |
| PADRÃO | Uma parte grande é erro nosso, com conserto conhecido | o maior erro isolado e 69% do sandbox vieram do prompt; o prompt anuncia um ambiente que não é o real (7, 9, anexo M) |
| IMPLICAÇÃO | O que é lição do agente se concentra — e concentração é alavanca | 3 candidatas = 75% dos erros e 85% dos tokens das candidatas; 2 papéis ≈ 60% (5, 7) |
| AÇÃO | O piloto mira memórias e papéis, não a média | as 3 memórias que passaram o degrau 2 (971 erros) + corrigir o prompt em paralelo (9) |

**O que a revisão pediu e foi feito:** as conclusões 1 e 2 (quase redundantes) viraram uma só (FATO); as barras têm
etiqueta fato/padrão/implicação/ação; a conclusão 4 mira memórias e papéis, não "a cauda"; o gradiente tem casa (fotos
`IMG_5842`, `IMG_5846` e a figura da rodada no slide 10).

**Rodapé:** parte do gradiente é mecânica (execução mais longa = mais passos = mais chances de errar) — consistente com
1,6× por passo e ~4,3× por execução, não prova causal.

---

## Slide 12 — O pedido: corrigir o que é nosso, validar a memória antes de implantar ✅

**Mensagem:** "Autorize o piloto controlado e encaminhe os avisos ao harness — a evidência justifica testar, ainda não
justifica prometer."

| Bloco | Conteúdo |
|---|---|
| 01 · Para a squad do harness — já | corrigir a instrução de verificação do ContestacaoCivel · declarar ou renomear o `get_document_text` no OBFCivel · explicar por que a lista de imports do prompt não é a do interpretador (531 de 531) |
| 02 · Para o projeto — o piloto | degrau 3 (leitura de casos) das 3 memórias que passaram o degrau 2 · POC mínima com × sem memória no mesmo recorte: reincidência, tokens, latência, qualidade |
| 03 · Os dados que faltam | prompt e modelo por papel na base 3 · passos sem erro (janela completa) · falhas silenciosas · preço por modelo (R$) |
| Decisão solicitada | autorizar o piloto controlado e encaminhar os três avisos ao time do harness |

Fontes: `17-validacao-memorias.md` · `04-roadmap.md` · `05-pedido-queries.md` · `roadmap-transversal.md` (aviso à
plataforma) · `pocs/blueprint-m1-pocs-minimos.md`

---

## Slide 13 — Referências e onde cada número vive ✅

Como desenhado: a bancada (MAST, TRAIL, AgentDebug, ToolScan/SpecTool + ToolFailBench) e os documentos do projeto por
slide (`02-relatorio-achados.md`, `09-metodologia-erro-a-memoria.md`, `17-validacao-memorias.md`, `dossie_base3.md`,
`registros/memorias.json` — 16 memórias —, `decisoes.md`, `01-racionais.md` §7). Fichamentos em
`analysis/2026-09-trace-law-flow/literature/`.

---

## Anexos ✅

| Anexo | Conteúdo | Figura (nome que o script procura) |
|---|---|---|
| A | Sankey da genealogia da base 1 | `09-genealogia-sankey.png` (repositório) |
| B | As três bases lado a lado | `08-overview-granularidade.png` (repositório) · `overview_base2.png`, `overview_base3.png` (`--figuras`) |
| C | Mapa das figuras — gerado pelo script (o que entrou, o que falta, de onde) | — |
| D | Esquema das três bases (tabela nativa) | — |
| E | O sandbox memória por memória, rodada de 21/10 (tabela nativa) | — |
| F | Uma linha da base 3 com a janela `[n−1] [n] [n+1] [n+2]` | `recorte_base3_janela.png` (`--figuras`; anonimizado, varrido) |
| G | Um erro da base 1: a saída do `drill_down.py` e o trace — o caso do slide 2 | `recorte_base1_drilldown.png`, `recorte_base1_trace.png` (`--figuras`) |
| H | O trio "Could not index" trabalhado | `trio_could_not_index.png` (`--figuras`) |
| I | Os 9 passos da mineração, com o sandbox de 21/10 (tabela nativa) | — |
| J | A escada em detalhe (o degrau 2 pelo interpretador, decisão de 21/10) | — |
| K | Destinos por unidade | `unidades_destino_tipo.png` (rodada) |
| L | Sinal de harness, o exemplo trabalhado (o prompt do ContestacaoCivel) | — |
| M | **Novo:** o prompt anuncia um ambiente que não é o real — 531 de 531 `import json` rodam com o prompt sem `json` na lista (bases 1 e 2); a montagem `executor=` do smolagents que reproduz isso (dossiê §2h, itens 16–21) | — |

Figuras da rodada usadas no corpo: `taxas_funil.png` (4), `genealogia_observada.png` (6), `destinos.png` (7),
`taxas_concentracao.png` (10); `painel_erros_taxa_mes.png` (5) é desenhada pelo script. Recorte do slide 2:
`recorte_slide2.png` (`--figuras`).

---

## Status do esqueleto

| Slide | Tema | Estado |
|---|---|---|
| 1–8 | Projeto, anatomia, necessidade, bases, escala, método, destinos, processo | ✅ fechados (21/10: execuções com erro corrigidas para 20.442 = 28,4% de 71.881) |
| 9 | Caso sandbox | ✅ fechado **em fechamento** — rodada de 21/10; refazer quando a unidade fechar |
| 10 | O custo de não aprender | ✅ fechado — gradiente conferido; a divisão 387/112 continua a foto de 14/10 |
| 11 | Quatro conclusões | ✅ fechado (pontos da revisão aplicados) |
| 12 | Pedido | ✅ fechado |
| 13 | Referências | ✅ fechado |
| Anexos | A–M | ✅ fechados; F, G, H e B (bases 2 e 3) dependem de figuras feitas à mão (`--figuras`) |
