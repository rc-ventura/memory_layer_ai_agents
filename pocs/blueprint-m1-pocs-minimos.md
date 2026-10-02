> **Sub-atividade:** 1.6 / 1.7 (alimenta 1.5 e 2.2) · **Tipo:** Blueprint de construção + plano de experimentos · **Status:** proposta para aprovação · **Data:** 28/09/2026

# Blueprint — POCs de agentes mínimos do Entregável M1

## 0. O que este documento é

Plano executável para a pendência central do **Entregável 1** (Macroatividade 1, prazo formal 30/10/2026; data de trabalho interna 30/11/2026):

- **Sub 1.6** — Construção de agentes mínimos representando abordagens distintas de memória e aprendizado: **(a)** loop de aprendizado fechado nativo, com memória em camadas e conversão automática de sessões em regras/skills reutilizáveis; **(b)** memória transparente, com controle programático explícito do log de execução.
- **Sub 1.7** — Análise comparativa entre aprendizado implícito e um modelo de sinal de feedback explícito (certo/errado), avaliando prós, contras e riscos para o contexto de fluxos jurídicos.
- Contribui para o terceiro item do Entregável 1: *"relatório comparativo entre as abordagens de memória avaliadas, com as respectivas POCs mínimas"*.

Este blueprint **não** é a POC em si nem o relatório comparativo — é a especificação do que construir, em que ordem, e quais experimentos rodar para que o relatório tenha evidência real em vez de opinião.

## 1. Perguntas que as POCs precisam responder

Toda peça construída existe para responder uma pergunta concreta. As fontes são os documentos canônicos do projeto:

| # | Pergunta | Origem |
|---|---|---|
| Q1 | O recall **explícito via tool call** (`recall_memory`, MCP, agnóstico de framework) atinge eficácia comparável à **injeção automática nativa** (Hermes)? | [`knowledge-as-infra-architecture-hypothesis.md`](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis.md) — "What has to happen before this becomes Sub 2.2"; pendente registrada em [`open-questions.md`](../discussion/open-questions.md) |
| Q2 | O **trigger ponderado por severidade** do Update Engine se comporta de forma sensata contra casos reais anotados — ou precisa de recalibração do zero (o "150" do Generative Agents é intransferível)? | mesma seção; [`promotion-policy-log-to-ltm.md`](../discussion/hipoteses/promotion-policy-log-to-ltm.md) |
| Q3 | O check de **qualidade de sinal** do Commit Gate (agreement, erro correlacionado, anti-sycophancy) reduz de verdade o risco que Casper et al. nomeia — ou é teatro de segurança sem diversidade real de raters? | mesma seção; [`thumbs-feedback-reliability.md`](../discussion/teoria/thumbs-feedback-reliability.md) |
| Q4 | Aprendizado **implícito** (conversão sessão→skill automática, sem gate) vs. **explícito** (sinal certo/errado + gate humano): prós, contras e riscos no jurídico | Sub 1.7 do Plano de Trabalho |
| Q5 | O **gate de promoção** log→LTM (filtro determinístico de anomalia, θ, cap) segura o ruído sem perder o caso raro? Qual fração de promoção emerge (meta ~20–30%)? | [`promotion-policy-log-to-ltm.md`](../discussion/hipoteses/promotion-policy-log-to-ltm.md) §"Os componentes da política que faltam definir" |
| Q6 | Os campos para o **score DMF-lite** (`w1..w4`) existem de fato na base de traces real? Quais pesos iniciais? | open-questions ("cinco gaps de storage"); promoção §1 |
| Q7 | A família de erro com destino **harness** (a unidade nº10, `validar_quebra_sigilo`) é corretamente **não** absorvida como memória — falso-positivo de escrita? | [`09-metodologia-erro-a-memoria.md`](../analysis/2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md); Ajuste 5 de [`pipeline-entre-bases.md`](../analysis/pipeline-entre-bases.md) |

Regra do blueprint: **nenhum experimento sem uma dessas perguntas na frente; nenhuma pergunta sem um experimento.**

## 2. As duas POCs (polo a polo)

### POC-A — Loop de aprendizado fechado nativo

- **Stack:** Hermes Agent (Nous Research) — o polo (a) do Plano. Memória em camadas nativa (MEMORY.md/USER.md + arquivo episódico SQLite FTS5 + skill memory), conversão automática sessão→skill, persistência cross-session por padrão.
- **Papel no experimento:** mostrar o que o estado da arte resolve *sozinho* — e onde ele para: sem gate de revisão humana, sem versionamento/rollback, sem hard-delete auditável, sem toque externo de sinal. É o benchmark "native" das Q1/Q4.
- **Referência de desenho:** [`framework-comparison-hermes-smolagents-deepagents.md`](../discussion/hipoteses/framework-comparison-hermes-smolagents-deepagents.md); nota [`papers/hermes-agent.md`](../papers/hermes-agent.md).
- **Pendência de contexto:** a memória Hermes na plataforma real é do [ENGENHEIRO-3] e a reunião com ele **ainda não aconteceu** — a POC-A começa pelo Hermes open source; a reunião fecha o gap "como é na plataforma" (vai para seção de limitações/riscos do relatório comparativo, não bloqueia a POC).

### POC-B — Memória transparente com controle programático explícito

- **Stack:** smolagents (Hugging Face), CodeAgent — o polo (b) do Plano e **o mesmo framework dos traces da esteira** já analisados em `analysis/` (ActionStep/PlanningStep, `agent.memory.steps` — o que permite reusar o vocabulário empírico do projeto). Nata memória: nenhuma automática; o desenvolvedor controla tudo.
- **Papel no experimento:** é o substrato onde se implementa o **esqueleto mínimo do mecanismo do projeto** (knowledge-as-infra, versão POC): log episódico append-only, gate de promoção determinístico, LTM recuperável tipada (`exemplar`/`reflexão`), `recall_memory` como tool explícita chamada dentro do loop do agente, trigger ponderado por severidade, Update Engine produzindo **proposta**, Commit Gate com revisão humana manual, decay `R = e^(−τ/S)` + rebaixamento + hard-delete gated.
- **Recorte de escopo v1-POC (o que fica fora, consciente):** MCP de verdade (a tool `recall_memory` é registrada localmente no harness, mesmo contrato — MCP é decisão de integração do Sub 2.5/2.6, não do teste de conceito); NLI do Commit Gate (na POC a revisão é humana manual sobre a proposta versionada); adapter de STM via opção B (`dump_trajectory()` MCP) — POC usa a **Opção A** (adapter framework-specific lendo `agent.memory.steps`), conforme lean registrado em `open-questions.md`.

## 3. A suite de tarefas (o "jogo" onde os agentes jogam)

As POCs só comparam algo se rodarem **as mesmas tarefas**, com erro injetado de forma controlada. A suite é **sintética** — ferramentas mockadas cujas assinaturas de erro reproduzem as famílias **reais** mineradas na análise da esteira (nunca conteúdo jurídico real — PII rule do `analysis/README.md`).

| Grupo | Família de tarefa | Origem empírica | O que testa |
|---|---|---|---|
| **A — memória-resgatável** | Ferramenta retorna contrato que o agente não compreende; erro recorrente entre execuções, causa-raiz ensinável ("leia `result.docs`, não o dict de topo") | Unidade nº2 minerada (`06-racionais-mineracao-unidades-n2-n10.md` §9); recorrência 11,9%/13,5% por mecanismo | Aprendizado cross-trial (Q4, Q1) |
| **B — sinal de harness** | System prompt declara o mesmo nome de campo para retorno de tool e para o JSON final; o agente conflunde variáveis | Unidade nº10 (43% das respostas com campo regulatório inválido, 9/21, zero exceções) | Destino correto: **não** deve virar memória — detecta falsa aceitação no gate (Q7, Q3) |
| **C — beabá (piso de ruído)** | Casos triviais sem nada a aprender (~90% do volume, premissa do tutor de 28/08) | Premissa do checkpoint 28/08 | Gate de promoção não deve promover (Q5) |
| **D — falha silenciosa** | Tool dá timeout no passo 15 de um plano de 17; constraint do prompt impede retry; agente entrega final_answer pulando a etapa | Achado de 25/09 (diário); roadmap item 26 | Detectores determinísticos sinalizam o que a exceção não vê; do “consciente no thought” à etiqueta certa (Q2/Q7, fronteira com item 26 do roadmap) |

**Regime temporal:** cada grupo roda em N repetições (alvo inicial N≈20–30 execuções por tarefa, em lotes simulados = "meses"), para que a métrica central — **recorrência do mesmo erro entre execuções** — exista de fato. É essa redução de recorrência que as POCs medem (o espelho controlado do achado da esteira: o agente aprende a lição dentro da execução e a perde na próxima — `CalculoCivel`, diário 14/09).

**Critério de acerto/erro (Sub 1.5):** cada tarefa recebe um spec no formato **Task.md** da skill Eval Engineering (tabela de verificação, alternativas aceitas, mudança colateral proibida, caso-realista-que-deve-falhar) — [`eval-engineering-skill-architecture-connections.md`](../discussion/hipoteses/eval-engineering-skill-architecture-connections.md) §2. Esse artefato é em si um pedaço do **documento de especificação preliminar dos sinais de feedback** do Entregável 1.

**Formato de execução da suite — candidato em avaliação: Harbor** (framework de eval de agentes dos criadores do Terminal-Bench; decisão pendente, ver E0/E1). Uma task Harbor é `task.toml` + `instruction.md` + `environment/` (Dockerfile com as tools mockadas) + `tests/` (script que escreve o reward) — estruturalmente o mesmo par spec+verifier que o Task.md pede. O que ele já resolve: orquestração de trials em paralelo (o N≈20–30 do regime temporal), formato de trajetória padronizado (ATIF — sinergia com o pipeline de análise de `analysis/`), dataset versionado/compartilhável (credibilidade do relatório comparativo) e **adapter Hermes nativo** — a POC-A pluga quase de graça. O que fica fora da abstração dele e continua sendo código nosso: a camada de memória entre trials (LTM persiste fora do container efêmero), o Update Engine + Commit Gate rodando **entre** lotes (= "meses"), a instrumentação dentro do loop (chamada de `recall_memory`, mismatch pensamento×código — o verifier só vê o estado final do ambiente) e o adapter `BaseAgent` da POC-B. O grupo D pede controle fino de system prompt e wrapper de tool — só viável porque o adapter é nosso. Alternativa: runner próprio, mais leve (as tools mockadas seriam só funções Python do smolagents), ao custo de reimplementar orquestração de trials e perder o formato padronizado. **Decisão em E0**, com um spike de 1 task Harbor como prova.

## 4. Etapas de construção

Ordem de execução; cada etapa termina num artefato versionado.

| Etapa | Nome | Conteúdo | Saída | Depende de |
|---|---|---|---|---|
| **E0** | Setup e recorte | Branch nova `YYYY-MM-DD-pocs-m1`; dependências (`smolagents`, Hermes Agent, embeddings) via `uv add` — pyproject hoje só tem stack de análise (pandas/numpy/matplotlib/jupyter), POCs precisam grupo de deps separado (ex.: `uv add --optional pocs ...`); decisão de backend de LLM (API vs. modelo local — custo × reprodutibilidade); **decisão do harness da suite: Harbor × runner próprio (§3), com spike de 1 task**; convenção de diretório `pocs/`, estrutura `pocs/2026-09-min-agents/` datada como em `analysis/` | Ambiente rodando um agente smolagents “hello world” com `agent.memory.steps` inspecionável | — |
| **E1** | Suite de tarefas + verifier | Construir os 4 grupos de tarefas (A/B/C/D) com tools mockadas e specs Task.md; verifier determinístico para acerto/erro (antes de qualquer juiz-LLM, conforme princípio da skill). Se E0 decidir Harbor: cada grupo vira tasks no formato `task.toml`/`instruction.md`/`environment/`/`tests/` | `pocs/.../tasks/` + `verifier.py` + relatório de que os 6 fixtures de boundary passam | E0 |
| **E2** | POC-A (Hermes) | Instanciar Hermes mínimo sobre a suite E1; ligar persistência nativa; coletar o que a conversão sessão→skill produz; rodar X rodadas | POC-A executável + log de runs | E1 |
| **E3** | POC-B (smolagents + memória programática) | Agente mínimo + controle explícito: escrita incondicional em log, tool `recall_memory` chamada no loop, gate de promoção, cycle de vida (S inicial, decay, S→S+1, cap/eviction, rebaixamento, hard-delete gated) | POC-B executável | E1 |
| **E4** | Esqueleto do mecanismo (cold path) | Filtro determinístico de anomalia (predicado mínimo: nº tool calls, tamanho do trace, outlier — parametrizado, não calibrado ainda); Update Engine (1ª vs. 2ª reflexão); trigger ponderado por severidade; geração de proposta (nunca commit); Commit Gate manual versionado (arquivo/diff; git history como trilha) | `pocs/.../mechanism/` + um ciclo completo trace→proposta→gate→commit rodado à mão | E3 |
| **E5** | Experimentos (Seção 5) | Rodar EX-1..EX-7, registrar resultados por experimento | `pocs/.../resultados/` + notas | E2, E3, E4 |
| **E6** | Atualização da hipótese de arquitetura | Confrontar Q1–Q7 com os resultados; mover resoluções para `scope-and-terminology-decisions.md` e atualizar `open-questions.md` e os snapshots status da hipótese KaI | Docs de discussion atualizados | E5 |
| **E7** | Relatório comparativo (Sub 1.7) + integração no Entregável 1 | O relatório comparativo entre abordagens com as POCs, prós/contras/riscos no jurídico; liga final com o relatório de revisão bibliográfica e o spec de sinais | Relatório PT (esqueleto na Seção 7) | E6 |

**Sequencia em valor, não em conforto:** E1 antes de E2/E3 (suite primeiro — senão cada POC nasce enviesada pelo que o framework facilita). E4 só faz sentido depois de E3, mas o predicado do filtro e seu instantiate mínimo podem ser escritos em paralelo com E2.

## 5. Experimentos

Cada experimento: pergunta → desenho → medição → critério. Todos na suite E1 compartilhada.

### EX-1 — Recall explícito (tool call no loop) × injeção automática nativa (Q1)

- **Desenho:** mesma família de tarefas (grupo A) em três braços: (i) POC-A Hermes (injeção/conversão nativa), (ii) POC-B com `recall_memory` explícita decidida pelo agente, (iii) baseline sem memória.
- **Medição:** taxa de acerto por rodada em tarefa nova do mesmo domínio após exposure às tarefas anteriores; custo em tokens (recall explícita paga latência/tokens por decidir chamar); quando o agente deixa de chamar a tool quando deveria (miss) e quando chama sem necessidade.
- **Critério:** o explícito fecha ou supera o nativo em acerto, com auditabilidade como contrapartida — senão a premissa MCP agnóstica da arquitetura é rebatida e Q1 vira revisão de hipótese (registrar em E6).

### EX-2 — Redução de recorrência cross-trial (Q4, baseline)

- **Desenho:** grupo A, N repetições da mesma classe de erro em "meses" simulados; medir em qual repetição cada abordagem para de cometer o erro.
- **Medição:** curva erro-por-volta (como a análise mês-a-mês da esteira); paralela direta ao achado 11,9% (mensagem) / 13,5% (mecanismo) de `02-relatorio-achados.md`.
- **Critério:** POC-B + mecanismo reduz recorrência em ≤ n voltas com a lição persistida; POC-A (nativa) serve de referência de velocidade; baseline nunca aprende.

### EX-3 — Trigger ponderado por severidade em lote (Q2)

- **Desenho:** injetar sequências com 1 erro grave isolado, 3 erros graves curtos no tempo, e muitos erros baratos (SyntaxError de bateria dos 223 recuperáveis do TRAIL-esque); rodar o trigger com soma de severidade vs. contagem flat-N.
- **Medição:** delays até disparo nos 3 cenários; casos “100 certos baratos” não devem dispara-lo (anti-stall); 3 graves devem disparar bem antes do flat-N.
- **Critério:** comportamento sensato = dispara cedo em severidade concentrada, não trava em maré boa; se só disparar por contagem, o desenho está degenerado e Q2 pede recalibração (explicitada, pois a escala é nova — não há número portado).

### EX-4 — Qualidade de sinal no Commit Gate (Q3)

- **Desenho:** raters simulados com vieses conhecidos: (i) rater sycophantic (aprova por fluência — Sharma 2023), (ii) rater correlacionado (mesmo avaliador nos 3 erros — Casper), (iii) thumbs assimétrico (👍 vale pouco, 👎 vale muito — prior do tutor 28/08). Gate com: nada, majority vote, agreement+anti-sycophancy check.
- **Medição:** taxa de falsa aceitação e falsa rejeição por configuração; quanto do risco correlacionado o check pega.
- **Critério:** o check precisa reduzir falsa aceitação sob viés correlacionado de forma mensurável — caso contrário é teatro de segurança e Q3 fica respondida “pelo negativo”, o que também é resultado (e alimenta a necessidade de redundância de raters no design produtivo).

### EX-5 — Destino memória × harness (Q7)

- **Desenho:** groups A (memória-resgatável, análogo à unidade nº2) e B (análogo à nº10, prompt-induced field, destino harness) passam pelo pipeline inteiro; a decisão `memória | harness` (o campo `DESTINO_MINERACAO`/`validation.destino` do pipeline de análise) é reimplementada minimamente no esqueleto do mecanismo.
- **Medição:** grupo B é escrito na strategy layer como memória? (falso-positivo grave); grupo A é barrado? (falso-negativo).
- **Critério:** zero escrita de grupo-B como strategy layer; se o mecanismo escrever, a regra de decisão (≥1 caso confirmado chegando ao payload final → harness) precisa entrar no schema da unidade de memória, não em código ad hoc — alinha com o ajuste já feito em 28/09 no `base_pipeline.py` (Ajuste 5).

### EX-6 — Gate de promoção: ruído vs. caso raro (Q5)

- **Desenho:** misturar grupo C (beabá, ~90%) com grupo A e um "caso raro beabá-com-exceção" (volumetria baixa, importância alta — análogo ao `is_grande_causa`); varrer o predicado do filtro determinístico + θ1.
- **Medição:** fração promovida (meta ~20–30%); o caso raro entra? o beabá fica de fora? erro→recuperação sobe com S inicial maior?
- **Critério:** gate segura o beabá sem perder o raro; se subir beabá demais, predicado ficou solto; se derrubar o raro, ficou cego à severidade — os dois falsos são documentados como limites de predicado simples.

### EX-7 — Esquecimento controlado e reversibilidade (apoio a Q4/Q1)

- **Desenho:** memória que fica velha e nunca recallada (a skill de “limiar grande causa” desatualizado do worked example); decay passa θ1→rebaixa; candidate a θ2→gate de delete; replay do log imutável reconstrói a strategy layer após “commit ruim” (rollback via provenance).
- **Medição:** audit trail completo (motivo logado); replay recria o estado pré-commit ruim (Reversible Reconciliation do SSGM).
- **Critério:** demonstra, num cenário mínimo, a combinação cross-trial × forgetting × gate × rollback que a análise do corpus mostrou como interseção vazia ([`cross-trial-vs-forgetting-gap.md`](../discussion/teoria/cross-trial-vs-forgetting-gap.md)) — é o *núcleo empírico* da contribuição do projeto.

*Experimentos EX-3 a EX-6 dependem da calibração de parâmetros (θ1, pesos DMF-lite, predicado do filtro, janela por stage/caso). Tratar calibração como **primeira passada documentada**, não como número final: θ calibrado na POC não calibra a produção — é a *prova de que o procedimento de calibração funciona* e de onde a sensibilidade mora (insumo direto do Sub 2.2/3.6).*

## 6. A matriz pergunta × artefato × entregável

| Artefato | Responde | Entra no Entregável 1 como |
|---|---|---|
| Suite E1 + Task.md files (4 grupos) | Sub 1.5 operacionalizado, Q7 | Documento de **especificação preliminar dos sinais de feedback** (anexa: formato Task.md, critérios de acerto/erro, thumbs assimétrico, agregação e anti-sycophancy) |
| POC-A (Hermes) | Q1, Q4 | “POC mínima — abordagem (a)” do relatório comparativo |
| POC-B (smolagents) + mecanismo mínimo E4 | Q1–Q7 | “POC mínima — abordagem (b)” + embrião validado da arquitetura (input para Sub 2.2/2.3) |
| EX-1..EX-4 | Q1–Q4 | Seção **comparativa** do relatório M1 (prós/contras/riscos implícito × explícito no jurídico) |
| EX-5..EX-7 | Q5–Q7 | Evidência de que o desenho gate/decay/destino se comporta como previsto — ponte declarada para Macroatividade 2 |

## 7. Riscos e dependências abertas

1. **Reunião com [ENGENHEIRO-3] pendente** — POC-A assume o Hermes open source; a variante de plataforma atualiza apenas as notas de integração, não a POC.
2. **Backend de LLM** — decidir em E0 (custo da API vs. reprodutibilidade local). Argumentos registrados para o pós-28/08: tutor descartou fine-tuning por opex GPU; guiar por texto é o caminho — a POC reusa essa lógica.
3. **Campos reais do trace** — Q6/DMF-lite: se os campos do score não existirem na base, POC usa stub determinístico com campos que **existam** (`nº tool calls`, stage, desfecho) e documenta a substituição; confirmar com o tutor/equipe quais campos estruturados o pipeline emite hoje (promotion-policy item 1).
4. **Janela (stage vs. caso)** — o predicado do filtro trabalha com janela "por stage/caso" (consolidação 01/09); a POC testa com stage, que é como os triggers Kafka reais batem.
5. **Leituras pendentes do M1** — MAST e ToolScan ainda 🔎 (relatório mensal de setembro); se informarem detector novo, entra no grupo D da suite como item posterior, sem desbloquear E1–E5.
6. **PII e dados reais** — POCs rodam 100% em tools mockadas; **nenhum** conteúdo de trace real é versionado ou entra em prompt de LLM externo. Traces reais entram apenas como *evidência de projeto* (assinaturas de erro, contagens), nunca como dado da POC — mesma disciplina do `analysis/README.md`.
7. **Escopo do cold path** — o esqueleto E4 implementa o mínimo para alimentar experimentos; NLI-model-choice, rater redundancy real, otimização map-reduce do Engine ficam para Macroatividade 2, e isso é dito explicitamente no relatório (evita inflar o M1 com promessa de coisa pronta).
8. **Harness da suite (Harbor × runner próprio)** — se Harbor (§3): a orquestração "lotes = meses, mecanismo roda entre lotes" é uma camada fina nossa por cima de `harbor run`; a memória mora fora do container, no adapter do agente. Risco de overhead de Docker para tarefas que são puro LLM + mock de tool — mitigado pelo spike de E0. Se runner próprio: reimplementar trials paralelos e logging de trajetória (o que o Harbor daria de graça).

## 8. Critério de "pronto" para as POCs

Adaptado da checklist "complete only when" da skill (conexões §7):

- [ ] Spec (Task.md) casa com o que foi construído; o verifier decide por evidência independente, não por auto-relato do agente
- [ ] Tarefa solucionável a partir do que o agente enxerga (incluindo a memória que ele tem — não adivinhação)
- [ ] Os fixtures de boundary (válido, alternativa válida, errado realista, shortcut, colateral proibido, evidência corrompida) se comportam como o esperado no verifier
- [ ] Pelo menos um run real, ponta a ponta, lido integralmente por Rafael
- [ ] Falhas de ambiente/infra separadas de falhas de agente antes de usar qualquer score (princípio "fix only non-agent failures")
- [ ] Falha silenciosa detectada e etiquetada (não conta como acerto)
- [ ] Resultados entregues com evidência bruta + rastreável (mesmo padrão das pastas de evidência de `analysis/`)

## 9. Próximos passos imediatos (após aprovação deste blueprint)

1. Aprovar/ajustar este blueprint (recorte de escopo v1-POC e a ordem das etapas).
2. Abrir branch `2026-09-29-pocs-m1` (a branch atual `2026-09-28-mineracao-base2` está dedicada à mineração; não misturar).
3. E0 na sequência: decisão de backend de LLM + deps smolagents/Hermes + estrutura `pocs/2026-09-min-agents/`.
4. Registrar no diário (sub-atividade 1.6) e anexar este arquivo ao CLAUDE.md como nova âncora ("Blueprints e POCs").
