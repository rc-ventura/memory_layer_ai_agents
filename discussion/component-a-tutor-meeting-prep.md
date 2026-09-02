> **Sub-atividade:** 1.6 / 2.2 / 2.3 · **Type:** Preparação de reunião (tutor) — destila [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) (componente A) + a entrada de [26/08/2026](../research-diary/Ago/diario_campo_2026-08-24.md#26082026) + o [reading sprint](reading-sprint-2026-08-24-queue-papers.md) · **Idioma:** português por decisão explícita (override por-arquivo, ver [`README.md`](README.md)) · **Logged:** 27/08/2026

# Componente A (Memory Store) — briefing para a reunião com o tutor

**Estado em 27/08/2026.** Se estiver reabrindo isto mais tarde: os checkboxes da seção 2 são o sinal de obsolescência — cada caixa marcada registra um gap já resolvido (com data + onde ficou). Caixa vazia cujo assunto já tem resposta em outro lugar = este arquivo está desatualizado. Conferir contra `git log --oneline discussion/component-a-tutor-meeting-prep.md`, o doc de arquitetura e [`open-questions.md`](open-questions.md).

## Antes de mais nada — o que é "fechado" aqui

Tudo abaixo é **hipótese de arquitetura**, não decisão. O que está na coluna "fechado" são escolhas que **eu** tomei ao desenhar o componente A, com fundamentação bibliográfica — não coisas que o Luis Felipe já ratificou. Parte do objetivo da reunião é justamente submeter essas escolhas. Elas só viram decisão de fato depois dos POCs mínimos do Sub 1.6 e da comparação implícito-vs-explícito do Sub 1.7.

**Nenhum dos papers citados foi lido por mim ainda** — são 🔎 (um agente sem provider definido leu texto completo via sub-agente e extraiu mecanismo/fórmula) ou 📝 (só verificação bibliográfica). Não apresentar como leitura própria na reunião.

## Como enquadrar (abertura de ~3 min)

O componente A é a **base não-paramétrica** da arquitetura: a store onde todo caso vira registro textual, cross-trial (entre casos, não entre sessões), acessível por qualquer agente via uma tool call MCP. Não é a contribuição da tese — essa está nos componentes D (Commit Gate) e E (Forgetting), que é onde mora a diferenciação contra o Mem0. O A é a fundação sobre a qual D e E operam. O reading sprint confirmou, em nível de mecanismo (não só de tabela de survey), que **nenhum dos 8 papers lidos combina as cinco coisas que o mecanismo precisa** — memória não-paramétrica, sinal de correção externo/humano, atualização em lote controlada, versionamento/rollback, e esquecimento com delete real. Então o A é composto de pedaços de vários (MemoryBank, SAGE, DMF, SSGM), nenhum adotado inteiro.

---

## 1. O que está fechado no desenho (para explicar)

### Papel e fronteira do componente
- **É a 4ª camada de memória**, cross-trial. **Não** substitui nem unifica as três já vivas na plataforma (checkpoints LangGraph do Manager / dump por execução do Small Agent / memória nativa do Hermes) — todas são session/run-scoped; qualquer uma poderia chamar o A pela mesma interface MCP.
- **Fora de escopo por decisão anterior:** fatos de negócio estruturados e mutáveis (ex.: o limiar "grande causa" de R$500k) — já servidos por MCP tools de regra de negócio; escrever isso na memória duplicaria e arriscaria dessincronizar. E compartilhamento de memória entre agentes (os agentes da esteira não conversam entre si — confirmado nas reuniões de 20/08 e 21/08).

### Acesso e escrita
- **Leitura:** `recall_memory` exposta como tool MCP, chamada explicitamente dentro do trace de raciocínio do agente (não injeção silenciosa). Isso torna o design **simultaneamente agnóstico** (qualquer framework — Hermes, LangGraph do Manager, Small Agent — chama sem adotar implementação comum) **e loop-native** no sentido que o achado Hu/Liu §7.2.2 realmente quer dizer.
- **Escrita é incondicional (ADD para todo caso), sem seleção no write-time.** Motivo: *completeness gap* para auditabilidade jurídica — se a escrita dependesse de o agente decidir chamar um `add_memory()`, um caso que o agente não flagueia não deixaria registro nenhum. Inaceitável para auditoria.
- **O trigger da escrita é um evento de sistema, não uma tool do agente:** conclusão de stage do pipeline → publicação em tópico Kafka. **Infra confirmada live:** o agente de cadastro já publica em Kafka ao concluir sua stage (checkpoint 21/08) — o mecanismo já existe, não é pra construir.
- **Só `propose_memory_update` → Commit Gate** (a camada que muda comportamento do agente) precisa ser gated e custosa de disparar. A escrita crua não muda comportamento, então não precisa da mesma cerimônia de transparência que a leitura.

### Estrutura e formato
- **Duas camadas:** episódica (traces crus, **append-only imutável**, source-of-truth) + **strategy layer** derivada (mutável, *replayable* a partir da episódica). Princípio do SSGM (*Reversible Reconciliation*): recupera de drift ou commit ruim por replay do log imutável, não por diffs mantidos à mão. Mesmo layering de duas camadas do Hermes.
- **Conteúdo é texto plano 1D** (string linear) — não grafo. "1D" é a estrutura do conteúdo, não o substrate. Migração futura pra algo mais estruturado (2D/tabular: campos estruturados ao lado do texto livre) não está fechada contra — só não desenhada. Grafo *está* explicitamente decidido contra para v1 (ver §3.3).
- **Taxonomia (Hu/Liu, eixo Functions):** os traces crus são **Case-based Experiential Memory**; a strategy layer derivada é **Strategy-based Experiential Memory** (≈ "instruções" no vocabulário do Sub 3.2). Nenhuma das duas é **Factual Memory** — Factual (fatos de entidade) está fora de escopo, é das MCP tools de regra de negócio. O "semantic fact base" que o survey usa pro output da reflection é linguagem frouxa dele, não a categoria Factual.

### Score de importância e camada de transform
- **Score de importância inicial no write:** princípio do **DMF** — determinístico, combinando 3–4 sinais que os estágios upstream do pipeline **já emitem como output estruturado** (ex.: `is_grande_causa`, keyword de risco flagada, criticidade da stage, confiabilidade da fonte copiloto-vs-sistêmico). **Zero chamada de LLM, zero NLP novo** (o agente de cadastro já extrai os campos; o score só lê). Substitui o `S=1` fixo do MemoryBank como *valor inicial*, que depois decai/reforça normalmente.
- **A camada de transform** (raw→schema: montar o registro, calcular o score, gerar embedding, decidir chunking) **fica dentro do componente A** — não vira componente próprio (resolução de 26/08). Mas como **estágio re-executável sobre o log imutável**: dá pra recalibrar o score ou trocar o modelo de embedding depois por *replay*, sem re-disparar o evento de pipeline nem tocar o registro cru.
- Restrição herdada: o hot path **não carrega chamada generativa de LLM** — `recall_memory` é busca por similaridade de embedding, o ADD só precisa de embedding pra indexar, o score é determinístico. O custo generativo real vive no cold path (componentes C/D), por lote.

### Decay e retrieval (o que está fechado)
- **Decay tem que existir** e ser auditável (esquecimento é o achado central do projeto). *Qual função* ainda é gap — ver §2.
- **Mecânica de retrieval do `recall_memory` (resolvida 25/08 por composição, sem máquina nova):** top-K semântico → filtro do SSGM (`ACL(μ,uid)` + freshness Weibull `w(Δτ) ≥ θfresh` — um item muito similar mas velho pode falhar o gate) → ranking pela fórmula do Generative Agents (`relevância + importância`), reusando o mesmo score DMF-lite já computado na escrita.

---

## 2. O que ainda é gap (para buscar info com o tutor)

Ordenados por quanto destravam. Os cinco primeiros são os do *write-path* (registrados em [`open-questions.md`](open-questions.md)); o sexto é do lado do *read*, mesma família, achado em 26/08. **Marque a caixa quando o gap for resolvido — com data e onde ficou registrado.**

- [ ] **2.1 — O que um "episodic trace" efetivamente contém** — o gap mais upstream, decide os outros quatro. Opção (a): resumo de business-record (campos estruturados + desfecho). Opção (b): trajetória ExpeL/ReAct completa (sequência thought→action→observation). Isso decide o tamanho do registro, que é pré-condição pro chunking. **Pergunta pro tutor:** o payload do evento Kafka de conclusão *já é* o trace (o que o cadastro extrai da petição), ou o transform precisa puxar conteúdo de outro lugar pra montar?
  - **Esquema candidato (SAGE) — hipótese a testar contra o banco de traces do tutor, não decisão.** A STM do SAGE (*case study* TriviaQA, [`../papers/sage-2026.md`](../papers/sage-2026.md)) é campo-estruturada: `task` + *recent trajectory* = `user prompt` + `user instruction` → `assistant initial response` → `checker feedback` → `self-reflection rₜ` → `revised answer` → `rₜ₊₁`; **só os `r` são promovidos para a LTM**. Adaptado ao nosso pipeline per-stage (§2.2): `stage` + (`conteúdo do caso` **separado de** `instrução/playbook da stage`) → `output inicial do agente` → `sinal de crítica` (thumbs-down + correção livre / checker / desfecho — chega **assíncrono**, FK pro Signal Ledger, não campo preenchido no write) → [cold path, comp. C] `reflexão estruturada rₜ` (tipo do erro / causa / sugestão) → `rₜ₊₁`. Mapeamento direto com a §1: **trajetória crua ↔ log episódico** (append-only, completo p/ auditoria); **`r` destilados ↔ strategy layer** (via gate θ1-SAGE / severidade do Update Engine) — o "os `r` viram LTM" do SAGE é o nosso *promote* log→strategy layer. Divergência a registrar: no SAGE o loop é síncrono intra-tarefa; no nosso o sinal é atrasado — a reflexão não roda inline, o registro per-stage é escrito primeiro (incondicional, sem reflexão) e os `r` são derivados depois, quando o sinal chega.
- [ ] **2.2 — Granularidade do trigger** — *per-stage* (cada agente filho: cadastro, subsídios, contestação, publica seu próprio write ao concluir) vs. *per-caso* (um registro no fim). Minha working assumption de 26/08 é **per-stage** (cada publicação Kafka que já existe é um trigger natural, sem custo de infra novo), mas **não tem sign-off**. O worked example do doc de arquitetura descreve um registro por caso — o doc está internamente ambíguo. **Pergunta:** faz sentido um write por stage concluída, ou você espera um registro por caso?
- [ ] **2.3 — Substrate físico** — candidato leading: o Postgres compartilhado que já existe (1 por conta, confirmado live no checkpoint 21/08). Mas isso é inferência encadeada da lógica "evitar nova dependência operacional" (a mesma que descartou git como substrate), não uma decisão tomada sobre este componente. **Pergunta:** posso assumir o Postgres existente como substrate, ou a plataforma tem restrição (multi-tenancy, isolamento, volume)?
- [ ] **2.4 — Categoria de vector storage** — pgvector no Postgres existente vs. vector DB dedicado. Busca vetorial é requisito fechado; o *como* não. Mesma cadeia de inferência do 2.3.
- [ ] **2.5 — Estratégia de chunking** — zero menção no corpus inteiro do projeto. Importa aqui especificamente porque o score `S` e os parâmetros de decay são calculados **por registro**: chunking força decidir se eles se aplicam ao caso inteiro ou por chunk. Downstream do 2.1.
- [ ] **2.6 — ACL / visibilidade cross-domínio** — o `ACL(μ, uid)` da fórmula de retrieval do SSGM é um booleano importado que **nunca foi desempacotado** pro nosso domínio. Questões concretas sem resposta: um agente de um domínio (cível) pode ver traces escritos por um de outro (trabalhista)? Acesso é per-case (só agentes atribuídos ao caso) ou per-domínio/squad? Há dimensão LGPD, já que são casos jurídicos reais, independente do escopo por domínio? **Ganha peso porque a infra de 21/08 confirmou que não há auth centralizada** — o token do usuário é propagado camada a camada (proxy → Manager → MCP) e cada aplicação decide se e como valida. **Essa é a pergunta mais forte pra levar pra ele / pra governança.**

**Gaps de design (não de infra), que quero discutir na reunião:**

- [ ] **2.7 — Função de decay: exponential (MemoryBank) vs. Weibull (SSGM)** — ver §3.7. Trade-off: expressividade vs. nº de parâmetros pra calibrar sem dado.
- [ ] **2.8 — ADD incondicional vs. gate seletivo (SAGE)** — ver §3.1. É o ponto principal que quero debater.
- [ ] **2.9 — Consolidation** — não há mecanismo que faça merge/dedup de traces quase-duplicados nem de entradas redundantes na strategy layer. Hoje redundância só sai pela lógica de staleness do Forgetting. Gap reconhecido no doc de arquitetura (componente G, "não desenhado"). **Pergunta:** redundância na strategy layer vale resolver em v1, ou pode esperar v2?

---

## 3. Trabalhos que fazem diferente (para levantar e discutir)

Para cada escolha de design do componente A, o trabalho que decide de outro jeito — pra na reunião eu poder dizer "pensei assim, mas existe X que faz Y, vamos discutir".

### 3.1 ADD incondicional ↔ gate seletivo STM→LTM com threshold (SAGE) 🔎

- **Minha escolha:** todo caso vira registro, sem seleção no write-time (completeness pra auditoria).
- **SAGE faz diferente** (`MemorySyntax`, Apêndice A.1): retention `R(I,τ) = e^(−τ/S)` checada contra **dois** limiares θ1 > θ2 — `R ≥ θ1` mantém o item em STM; `θ2 ≤ R < θ1` **promove** pra LTM; `R < θ2` **descarta**. O `S(Iₜ) = H(Iₜ)/f(t)` é *entropy-weighted* e sujeito a um teto de capacidade. Ou seja: nem tudo entra na memória de longo prazo — há um portão com threshold e um limite de tamanho.
- **A tensão é real** e o doc de arquitetura marca como aberta: o gate seletivo do SAGE conflita direto com o ADD incondicional que escolhi.
- **Onde os dois podem conviver:** aplicar o gate seletivo do SAGE **não** no log episódico (que por auditoria tem que ser completo), mas na decisão do que é **promovido pra strategy layer** — papel hoje exercido só pelo Update Engine (componente C), em lote, disparado por severidade. Seriam duas portas de promoção com critérios diferentes.
- **Pergunta pro tutor:** o log episódico completo é inegociável pra auditoria (minha suposição), ou há apetite pra um log "quente" menor + arquivo frio? E o gate entropy-weighted do SAGE faz sentido como filtro de entrada da strategy layer?

### 3.2 Escrita disparada por sistema ↔ escrita como decisão do agente via tool call (Hu/Liu §7.2.2; Memento; Mem0)

- **Minha escolha:** evento de pipeline (Kafka), sem tool `add_memory`; o agente não decide escrever.
- **Hu/Liu §7.2.2** (o achado que registrei em 24/08) argumenta o **oposto** pra gestão de memória em geral: integrar construção/evolução/recuperação no loop de decisão via tool calls explícitas, fazendo o agente raciocinar sobre add/update/delete/retrieval, dá comportamento mais coerente, transparente e contextualmente fundamentado.
- **Memento** 🔎: `Write(s,a,r)` explícito dentro do loop, todo caso anexado — mas é *write-only* (sem discard) e o reward é 100% automático (task success binário), sem humano.
- **Mem0** 🔎: decisão ADD/UPDATE/DELETE/NOOP por julgamento de LLM a **cada turno** de conversa.
- **Minha reconciliação** (já no doc): "no loop" vale pra *leitura* — `recall_memory` é tool call explícita, transparência importa pra ler memória. A *escrita crua* não precisa dessa propriedade porque não é uma decisão que muda o comportamento do agente; e fazer ela depender da decisão do agente quebra a completude (o argumento da auditoria). Só `propose_memory_update` → Commit Gate precisa ser gated.
- **Pergunta pro tutor:** concorda que escrita crua ≠ decisão do agente, ou você vê valor em o agente "saber" explicitamente que registrou (a favor da transparência do §7.2.2)?

### 3.3 Texto plano 1D ↔ memória em grafo (Mem0g) / notas linkadas (A-Mem)

- **Minha escolha:** string linear, sem grafo, para v1.
- **Mem0g** 🔎 (variante de grafo do Mem0): estrutura memória como entidades + relações, com um detector de conflito e um resolver que marca relação obsoleta como **inválida em vez de deletar** — um protótipo de exatamente o que os componentes D e E precisam. **Mas** a ablação LoCoMo do próprio Mem0: grafo só ajuda em raciocínio **temporal/relacional** (F1 51,55 vs. 42,02 flat), *piora* levemente em single-hop, e **não dá ganho** em multi-hop. Não é ganho genérico.
- **A-Mem** 📝: notas estilo Zettelkasten com um passo de "memory evolution" que refina/reforça retroativamente notas existentes quando uma nova entra — forma de consolidação diferente (linkar/refinar no lugar, não merge-ou-descarte). Reporta 85–93% menos token vs. MemGPT/MemoryBank/ReadAgent no LoCoMo.
- **Por que fiquei no 1D:** o raciocínio jurídico (cadeia de precedentes, prazo contado a partir de outro evento, hierarquia de recurso) **é** a forma temporal/relacional onde o grafo ajudou — então é motivo real pra reconsiderar em v2, **condicionado ao Sub 1.4** confirmar essa necessidade no fluxo-alvo. Não é v1.
- **Pergunta pro tutor:** o fluxo jurídico-alvo tem navegação multi-hop entre precedentes que justificaria grafo, ou é mais recuperação de caso similar (que texto plano + embedding já resolve)?

### 3.4 Score determinístico DMF-lite ↔ valor fixo (MemoryBank) ↔ julgamento de LLM (Generative Agents; Mem0)

- **Minha escolha:** score determinístico de 3–4 sinais já estruturados do pipeline, zero LLM.
- **MemoryBank** 📝🔎: valor fixo `S = 1`, só muda em recall (`S → S+1`, `Δt → 0`). Simples e auditável (dois inteiros por item), mas o "sinal de importância" é pura frequência de recall — proxy de relevância social, **não** correção jurídica nem severidade de desfecho.
- **Generative Agents** 📝🔎: "poignancy" 1–10 julgada por LLM no momento da criação, com prompt ancorado em vida social ("escovar dentes" vs. "um término"). Precisaria de reancoragem jurídica ("caso extinto", "prazo prescricional perdido").
- **Mem0** 🔎: score/decisão por LLM por item — reintroduz o risco de julgamento auto-referencial que o projeto evita.
- **DMF** 🔎 (a fonte do princípio): score determinístico multi-canal na escrita, zero LLM — **mas** a implementação real são 8 camadas (pipeline NLP spaCy específico de idioma, motor de embedding, camada de projeção de "cartão", etc.) com ~8 pesos (η, κ, λ, δ, ponto médio do sigmoide) **calibrados à mão**, não aprendidos. Portar isso pra português jurídico = construir um adaptador de regras do zero.
- **Minha posição:** princípio do DMF (determinístico, auditável, poucos canais), em escala pequena; pesos são trabalho de calibração do Sub 1.6/1.7.
- **Pergunta pro tutor:** quais sinais estruturados o pipeline de fato já emite hoje que dariam pra compor esse score?

### 3.5 Sem consolidation ↔ ReasoningBank / A-Mem / Mem0 UPDATE / SAGE "Checker"

- **Minha escolha (por omissão):** nada faz merge/dedup; redundância só sai por staleness.
- **ReasoningBank** 📝: nomeia o próprio loop retrieve→construct→**consolidate** — único do corpus a usar o termo pro próprio mecanismo.
- **Mem0 UPDATE** 🔎: merge de um fato novo contra os `s=10` mais similares, via LLM — consolidação de um fato por vez. Candidato a *adaptar* (gated, tipo Commit Gate), não a copiar.
- **A-Mem** 📝: linka/refina no lugar em vez de merge-ou-descarte.
- **SAGE "Checker"** 🔎: ambíguo — consolidação de conteúdo de memória, ou refinamento de política via recompensa que não toca memória? Só uma leitura completa da seção resolve.
- **Status:** gap reconhecido (componente G), nenhum candidato adotado.

### 3.6 Log imutável + camada derivada replayable (SSGM) ↔ append-then-summarize (MemGPT)

- **Minha escolha:** SSGM *Reversible Reconciliation* — recupera de drift/commit ruim por replay do log imutável.
- **MemGPT** 📝: compressão é append-then-summarize, **sem critério homeostático** — a própria nota do repo marca como contraste de cautela, não de arquitetura.
- Aqui não há tensão real — a escolha já está feita; o contraste é "o que **não** fazer".

### 3.7 Decay exponential (MemoryBank) ↔ Weibull (SSGM)

- **MemoryBank** 📝🔎: `R = e^(−Δt/S)` — dois inteiros, fórmula fechada, fácil de explicar num audit trail.
- **SSGM** 🔎: `w(Δτ) = exp(−(Δτ/η)^κ)` — o shape parameter `κ` deixa a curva ser rápida-depois-plana ou lenta-depois-íngreme, ajustável **por classe de memória** (um fato-limiar tipo "grande causa" pode querer curva diferente de um exemplar de desfecho de caso). E a linguagem do SSGM ("pruned before reaching the context window") é mais próxima de deleção real que a de-priorização-só-no-ranking do MemoryBank.
- **Escolha em aberto** — expressividade vs. nº de parâmetros pra calibrar sem dado histórico.

---

## 4. Leituras recomendadas para o componente A

Corte do [`reading-queue.md`](../papers/reading-queue.md) → "Guia de leitura por componente" (seções A e A2). **Status:** 📝 = nota bibliográfica verificada (não lido) · 🔎 = um agente sem provider definido leu texto completo via sub-agente · **nenhum lido por mim ainda**.

| Paper | Status | Tier | Onde focar |
|---|---|---|---|
| **MemoryBank** (arXiv:2305.10250) | 📝🔎 | 1 (#3) | A fórmula `R = e^(−Δt/S)` e a reinforcement em recall (`S → S+1`). Curta. Confirmar que **não há hard-delete** documentado — só de-priorização no ranking. |
| **SSGM** (arXiv:2603.11768) | 🔎 | 1 (#1) | *Reversible Reconciliation* (log imutável + camada derivada replayable — resolve o rollback do Sub 3.4); a fórmula do filtro de retrieval `Ct = {μ ∈ Top-K(qt,Mt-1) \| ACL(μ,uid) ∧ w(Δτμ) ≥ θfresh}`; o decay Weibull. 13 páginas, a mais "carregada de peso" pra defender a arquitetura. |
| **SAGE** (arXiv:2409.00872) | 🔎 | revertido p/ 2 | O gate de promoção STM→LTM (`MemorySyntax`, θ1/θ2, `S(Iₜ)=H(Iₜ)/f(t)` entropy-weighted + capacity cap, Apêndice A.1). É o contraste central da §3.1. Também: confirmar pessoalmente a ressalva de que SAGE reivindica cross-trial mas não isola isso experimentalmente. |
| **DMF** (arXiv:2606.03463) | 🔎 | 2 (#11) | **Só** a seção Survival Score / Calibration, e **só pelo princípio** — não copiar as 8 camadas nem os pesos calibrados à mão. O ponto: score determinístico e auditável combinando poucos canais já estruturados do pipeline, nem valor fixo (MemoryBank) nem LLM (Mem0). |
| **Mem0** (arXiv:2504.19413) | 🔎 | 2 (#9) | O Algoritmo 1 (Apêndice B): ADD/UPDATE/DELETE 100% julgamento de LLM a cada mensagem, **sem decay algum** — forgetting só por contradição lógica, nunca por obsolescência. É o contraponto que sustenta a diferenciação "knowledge as infra". **Provável pergunta do tutor: "por que não usar Mem0 direto?"** — ter resposta pronta. |
| **Generative Agents** (arXiv:2304.03442) | 📝🔎 | 2 (#8) | A fórmula de scoring da memory stream (`relevância + importância + recência`, todos α=1) — rankeia os sobreviventes do filtro do SSGM na mecânica de retrieval. |

**Ordem sugerida (só pro componente A):** MemoryBank (rápido, fundação) → SSGM → SAGE → DMF → Mem0 → Generative Agents.

**Cuidado ao citar:** tudo acima é 🔎 ou 📝. Na reunião, dá pra dizer "o desenho se apoia em SSGM/SAGE/MemoryBank/DMF e há um resumo de texto completo desses" — **não** "eu li X e ele diz Y".

---

## 5. Perguntas objetivas para o tutor (checklist)

1. Log episódico **completo** é inegociável pra auditoria, ou cabe um log quente menor + arquivo frio? (§3.1)
2. Trigger da escrita: **per-stage** (minha suposição) ou **per-caso**? (§2.2)
3. Posso assumir o **Postgres compartilhado existente** como substrate? Restrição de multi-tenancy/isolamento/volume? (§2.3)
4. **ACL / visibilidade cross-domínio:** agente de cível vê trace de trabalhista? Acesso per-case ou per-squad? Dimensão **LGPD**? (§2.6 — a mais importante, dado que não há auth centralizada)
5. Que **sinais estruturados** o pipeline já emite hoje que serviriam pro score de importância determinístico? (§3.4)
6. O fluxo jurídico-alvo tem **navegação multi-hop entre precedentes** (justificaria grafo em v2), ou é recuperação de caso similar? (§3.3)
7. **Consolidation** (dedup na strategy layer): resolver em v1 ou adiar pra v2? (§2.9)
8. O que ele espera que um **"episodic trace"** contenha — resumo de business-record ou trajetória completa? (§2.1)

---

## Links

- Arquitetura completa: [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) — seção A + "Write-path status snapshot for component A"
- Entrada de diário que originou isto: [26/08/2026](../research-diary/Ago/diario_campo_2026-08-24.md#26082026)
- Achados de texto completo dos papers: [`reading-sprint-2026-08-24-queue-papers.md`](reading-sprint-2026-08-24-queue-papers.md)
- Gaps rastreados: [`open-questions.md`](open-questions.md) (itens sobre granularidade do trigger e os cinco gaps de storage-mechanics)
- Infra confirmada: [`../docs/checkpoints/checkpoint-2026-08-21-infra-arquitetura.md`](../docs/checkpoints/checkpoint-2026-08-21-infra-arquitetura.md) · reflexões: [`checkpoint-2026-08-21-infra-reflections.md`](checkpoint-2026-08-21-infra-reflections.md)
