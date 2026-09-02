> **Sub-atividade:** 1.6 / 2.2 · **Type:** Nota de desenho — política ainda em aberto, não decidida · **Idioma:** português por decisão explícita (override por-arquivo, ver [`README.md`](README.md)) · **Logged:** 31/08/2026

# Política de promoção: log episódico → LTM recuperável

Consolida o que hoje está fragmentado — os sub-bullets de 27/08 em [`open-questions.md`](open-questions.md), o item de 31/08 ("quem é dono do gate de admissão"), as notas de leitura do SAGE e do MemoryBank, e a seção "Static vs. adaptive" de [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md). Surgiu de várias rodadas de conversa (28–31/08) em que ficou claro que a política de promoção nunca foi escrita como uma coisa só.

## O que "promoção" é — e o que não é

Duas transformações **diferentes** operam sobre o mesmo pool de traces crus:

| | Entrada → Saída | Quem faz | Custo | Isto é a "camada semântica"? |
|---|---|---|---|---|
| **Promoção** | log episódico (texto) → **LTM episódica** (embedado, indexado, recuperável via `recall_memory`) | mecanismo determinístico (gate) | barato, sem LLM generativo | **Não** — continua exemplar episódico (Case-based, Hu/Liu) |
| **Reflexão** | traces (sucesso + falha) → **strategy layer** (heurística destilada) | Update Engine (componente C) | caro, LLM, em lote | **Sim** — é a strategy-based memory |

Esta nota é só sobre a **promoção**. A reflexão e o Commit Gate (check de contradição `∆M ∧ M_core ⊨ ⊥`) são outra coisa, outro caminho (cold path), outra frequência (por lote, não por trace).

Onde a promoção fica no fluxo:

```
trajetória crua  →  log episódico (texto, S calculado no write)  →  relógio de decay começa
                                                                        │
                                              [GATE DE PROMOÇÃO: avalia R contra θ1]   ← esta nota
                                                                        │ passa
                                        Write Transform: embedding + chunking  →  LTM indexada  →  recall_memory
```

## As três camadas e os quatro gatilhos de escrita (added 01/09/2026)

Consolidação que faltava: esta nota trata só da promoção (log→LTM), mas a promoção só faz sentido situada entre as **três camadas** do memory layer e os **quatro eventos de escrita** que as alimentam. O modelo "duas camadas" (log cru episódico + strategy layer) colapsa duas coisas distintas — o log cru e o índice-LTM recuperável — e é exatamente nesse vão que mora o gatilho de "vira memory unit".

### As três camadas

| # | Camada | Conteúdo | Escrita | Recuperável via `recall_memory`? | Taxonomia Hu/Liu |
|---|---|---|---|---|---|
| 1 | **Log episódico** | trajetórias cruas, append-only, imutável, texto puro (sem embedding) | **incondicional** | **não** — serve auditoria jurídica + alimenta o Update Engine (precisa de sucesso *e* falha) | — (substrato) |
| 2 | **LTM episódica recuperável** | os ~20–30% do log que passam no gate, embedados e indexados | **gated** (`R ≥ θ1`) | **sim** | Case-based Experiential |
| 3 | **Strategy layer** | heurística de decisão destilada, derivada/mutável, replayable a partir de (1) | Commit Gate (componente D) | **sim** | Strategy-based Experiential |

O "log episódico é *tudo*" da seção acima continua valendo: a camada 1 guarda cada trajetória; a promoção é 1→2, não 1→(nada). Não há tier STM separado à la SAGE porque a camada 1 já é o holding area completo.

### Os quatro gatilhos de escrita

| Escrita | Gatilho | Quem dispara | Chamada de LLM? | Já é infra viva? |
|---|---|---|---|---|
| evento de pipeline → **trace no log (1)** | conclusão de stage publicada em tópico Kafka | sistema (não é tool do agente) | não | **sim** — cadastro já publica ao concluir ([checkpoint 21/08](../docs/checkpoints/checkpoint-2026-08-21-infra-arquitetura.md)); é o "banco de traces" que o tutor vai fornecer |
| log → **LTM recuperável (2)** | `R = e^(−τ/S) ≥ θ1`, avaliado numa cadência (sweep agendado + bump no recall) | **mecanismo determinístico separado** (lean — ver item 9) | **não** | não — é a política desta nota |
| traces → **proposta de estratégia** | scan em lote agendado (default do tutor) · severidade cumulativa · gatilho humano — com **filtro heurístico determinístico como 1ª etapa** (tamanho do trace, nº de tool calls, distribuição de 👎, outlier vs. distribuição) | Update Engine (componente C) | sim — map-reduce de LLMs, **só nos sobreviventes do filtro** | não |
| proposta → **commit na strategy layer (3)** | chamada `propose_memory_update` | Commit Gate (componente D) | sim (NLI `∆M ∧ M_core ⊨ ⊥`) | não |

### O fluxo, ponta a ponta

```
evento Kafka (fim de stage)
        │  [gatilho: sistema · incondicional · JÁ EXISTE]
        ▼
  trace cru no log episódico (camada 1)   ──────────────┐  (lido cru pelo Update Engine:
        │                                               │   precisa de sucesso E falha)
        │  [gatilho: gate determinístico R ≥ θ1,        │
        │   numa cadência · sem LLM]  ← ESTA NOTA       │
        ▼                                               ▼
  LTM episódica recuperável (camada 2)          filtro heurístico determinístico
  (memory unit episódica, Case-based)           (anomalia / sinal de aprendizado, ~10%)
                                                        │  sobreviventes
                                                        ▼
                                              Update Engine (LLM, map-reduce)
                                                        │  proposta (ExpeL-style)
                                                        ▼
                                              Commit Gate (NLI + qualidade de sinal)
                                                        ▼
                                              strategy layer (camada 3)
                                              (memory unit de estratégia, Strategy-based)
```

### Dois filtros de ruído, não um

O "não pode ser todo evento cru" se resolve em **dois pontos distintos**, ambos determinísticos e sem LLM:

1. **Filtro de volume/relevância = o gate de promoção desta nota** (`R ≥ θ1`). Pergunta: *"vale este trace ser recuperável por um agente depois?"* ~20–30% passam. Protege o espaço de retrieval de index bloat (família *Efficiency* da taxonomia de erros do SSGM).
2. **Filtro de anomalia = 1ª etapa do Update Engine.** Pergunta: *"aconteceu algo aqui que vale destilar numa regra?"* Estimativa do tutor: ~10% dos casos; ~90% "é o beabá, não tem o que aprender". A LLM curadora só roda no que sobra daqui.

São filtros com propósitos diferentes sobre o mesmo pool de traces — um decide o que entra no *retrieval*, o outro o que entra na *reflexão*.

### O que o SSGM contribui aqui — e o que não

O Princípio 1 do SSGM é **trigger-agnostic** por desenho: desacopla "o que dispara a escrita" de "como a escrita é validada", e entrega só o segundo (o Write Validation Gate). A lista de gatilhos que ele cita (decisão RL de ADD, hook de fim-de-subtarefa, timer de N turnos, detecção de erro, reflexão gerada) é catálogo de opções, não recomendação. A definição do nosso gatilho é decisão de projeto — o SSGM não a fornece, só confirma que ela é separada da validação. Ver [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md) → "SSGM's design principles — P1".

## O esqueleto que está decidido

- **Retenção:** `R = e^(−τ/S)` (MemoryBank/SAGE) — `τ` = tempo desde o último acesso, `S` = "força" da memória.
- **`S` inicial:** score determinístico DMF-*lite* no write, combinando campos que os estágios upstream do pipeline **já emitem como output estruturado** — sketch: `w1·is_grande_causa + w2·keyword_de_risco_flagada + w3·criticidade_da_stage + w4·confiabilidade_da_fonte (copiloto vs. sistêmico)`. **Zero chamada de LLM, zero NLP novo.**
- **Reforço:** `S → S+1` a cada recall (spacing effect, MemoryBank).
- **Regra de corte:** `R ≥ θ1` → promove.
- **Volume alvo:** ~20–30% do log (estimativa, não medido).
- **Natureza:** política **estática** por design — regra fixa, auditável, determinística; `θ1` é *calibrado* (Sub 1.6/1.7), não aprendido. Ver [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md) (static vs. adaptive).
- **`θ1` não é portável:** nem da escala de "poignancy" social do SAGE, nem do "150" do Generative Agents — calibração do zero.
- **A nossa versão não tem o tier STM do SAGE.** No SAGE há três faixas (`R ≥ θ1` fica em STM / `θ2 ≤ R < θ1` promove pra LTM / `R < θ2` descarta). Aqui o log episódico é *tudo*, e a promoção é log→índice-LTM — por isso a regra de faixas do SAGE não mapeia direto e virou um limiar só. A banda exata é ponto em aberto (ver abaixo).

## Os componentes da política que faltam definir

Ordenados por quanto destravam. **Nada aqui está decidido.**

### 1. Importância no write (`S` DMF-lite) — quais sinais, quais pesos
Esqueleto existe (a fórmula-sketch acima). Falta: (a) confirmar **que campos estruturados o pipeline de fato emite hoje** — pergunta pro tutor / a checar na base de traces que ele vai fornecer; (b) os pesos `w1..w4` — calibração Sub 1.6/1.7. Sem os campos reais, a fórmula é hipotética.

### 2. Reforço por uso (`S → S+1`) — recall de quê conta?
Se um trace **não está indexado**, ele não é retornado pelo `recall_memory` — então como "ganha" o `+1`? Candidatos: (a) só conta recall de itens **já promovidos** — nesse caso o reforço **mantém** promovido, não promove de início; (b) as leituras do Update Engine sobre o log contam como "recall" — aí um trace muito lido pela reflexão poderia subir. Não decidido. Lean: (a) — o reforço é mecanismo de *permanência*, não de *entrada*.

### 3. Decay temporal — rebaixa ou descarta?
`R` cai com `τ`. Um trace promovido, velho e não usado, cai abaixo de `θ1`. Ele então: (a) é **rebaixado** (sai do índice, volta a ser só log)? (b) é **descartado** (hard-delete)? Liga direto com o item aberto "hard-delete automático vs. gated" do componente E ([`open-questions.md`](open-questions.md)). Lean provável: rebaixamento é automático e barato (sai do índice); hard-delete do **log** é outra decisão, gated.

### 4. Sinal de falha — vai pra LTM recuperável ou só pra reflexão? *(o mais importante)*
Um trace com 👎 ou desfecho adverso (do Signal Ledger): (a) entra na LTM recuperável, pra o agente ver "teve um caso assim que deu errado" (exemplar cautelar); ou (b) **não** entra no espaço de retrieval — só alimenta a reflexão do Update Engine, que destila a lição pra strategy layer. Risco de (a): encher o espaço de retrieval de falhas pode enviesar o agente / degradar o sinal. Risco de (b): perde-se o exemplar concreto negativo, que às vezes ensina mais que a regra abstrata. **Não decidido — e é uma bifurcação real de desenho.** O worked example do doc de arquitetura sugere que o agente recebe "relevant past episodes" (poderia incluir cautelares), mas não crava.

### 5. Cap de capacidade
O índice LTM tem orçamento finito. Quando cheio: evicta o de menor `R` (padrão **Priority Decay** / "forgetting-by-design" — achado da leitura do SSGM, [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md), demonstrado no FiFA benchmark: política de esquecimento *bounded, budget-aware* reduz custo E preserva coerência/privacidade). Não desenhado. Precisa de: tamanho do orçamento, e se a eviction é por `R` puro ou ponderada (ex.: proteger grande causa).

### 6. Redundância / dedup na promoção
50 traces "cadastro simples, sem erro" passam em `θ1` = index bloat sem ganho de sinal (degrada retrieval pro agente). Um check de quase-duplicados no momento da promoção limitaria quantos near-duplicates entram. É o gap de **Consolidation** (componente G, [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md#g-consolidation--an-open-gap-in-evolution-not-yet-a-designed-component-added-25082026)) aplicado à entrada da LTM. DarwinMem ([`../papers/reading-queue.md`](../papers/reading-queue.md) #42) tem um padrão adjacente (poda por *survival value*). Não desenhado.

### 7. Cadência de avaliação do gate
O gate roda: (a) **agendado** (varre o log a cada X)? (b) **on-recall** (reavalia `R` quando o item é acessado)? (c) **os dois** (é o que o SAGE faz — decay contínuo + salto de `S` no recall que pode reempurrar `R` acima de `θ1`)? Não decidido.

### 8. `S` de promoção = `S` de write?
O DMF-lite foi desenhado pra **importância no write** (quanto este caso importa *agora*), não pra **relevância de retrieval ao longo do tempo**. As duas metas podem divergir. Reusar o mesmo `S` é mais simples e coerente com o princípio de não duplicar sinais; um "promotion score" separado é mais fiel ao propósito. Não decidido.

### 9. Dono do gate — mecanismo separado ou o Update Engine?
Item registrado em 31/08 no [`open-questions.md`](open-questions.md). Lean documentado: **mecanismo determinístico separado** (`R ≥ θ1`, sem LLM, no caminho quente/morno), distinto do Update Engine (LLM, lote, cold path). Colar (9) no Update Engine poria uma chamada de LLM no caminho de admissão — granularidade e custo errados. A linguagem "curador" da reunião de 28/08 borrou os dois; precisa de decisão explícita.

## Estratégias de promoção em consideração (added 01/09/2026)

Rodada de conversa de 01/09 (diário [01/09/2026](../research-diary/diario_campo_2026-08-31.md)). **Posição do Rafael (01/09): tem que haver um gate de promoção — "não podemos armazenar ruído" (requisito do tutor, 28/08).** Isso descarta a Estratégia 1 (promover sem filtro) como mecanismo primário do v1. O que fica em aberto não é *se* há gate, mas *qual o critério* dele.

O esqueleto acima assume um critério — `R ≥ θ1` com `S` DMF-lite. Ele depende de dois fatos ainda não verificados: (i) se os campos estruturados pro `S` existem no banco de traces / nos eventos Kafka — **a checar analisando o trace real** (item 1); (ii) `θ1` só calibra com traces anotados (Sub 1.6/1.7). Enquanto isso não fecha, um critério booleano mais simples (Estratégia 2) é o candidato do v1.

### Formato de armazenamento (comum a todas as estratégias)

O que a promoção grava na camada 2 **não é resumo** (resumir é papel da camada 3). É um **envelope estruturado**: conteúdo cru *verbatim* + campos de metadado calculados de forma determinística no write — `case_id`, `stage`, timestamp, `S` inicial, estado de decay (`R`, `τ`, `last_recall_at`), flag de desfecho, nº de tool calls, contagem de 👎, FK pro Signal Ledger, ACL/domínio. Zero LLM. Preserva o exemplar (auditoria, *reversible reconciliation*) e carrega os campos que o retrieval do SSGM (`ACL(μ,uid)`, freshness gate) e o ranking (Generative Agents) precisam.

Bifurcação que isto resolve (levantada 01/09): promover **trace cru puro** vs. **derivado sumarizado por janela**. Resolução proposta: envelope estruturado (cru + campos), **nunca sumarizado** no caminho de promoção.

### Camada 2 tipada — exemplar + reflexão (alternativa, added 01/09/2026)

Rodada de 01/09 (diário). Alternativa ao desenho "camada 2 = só exemplar episódico": a camada 2 recuperável passa a ser **um store só, com entradas tipadas**:

- **`exemplar`** — trace concreto promovido, envelope estruturado (cru *verbatim* + campos), admitido pelo **gate determinístico** (Estratégia 2 / `R ≥ θ1`). É o Case-based Experiential.
- **`reflexão`** — output do **Update Engine** sobre uma janela de traces: o que ele identificou e destilou, gravado direto como **memória semântica** recuperável. Mais perto de Strategy-based, mas em granularidade **local** (por episódio/janela), não a regra transversal da camada 3.

A camada 3 (strategy layer) continua sendo a destilação de **segunda ordem** — reflexão sobre reflexões/traces, com o Commit Gate (D) NLI.

**Ambos os tipos carregam o mesmo ciclo de vida** (confirmado pelo Rafael, 01/09): `S` inicial, decay `R = e^(−τ/S)`, reforço `S→S+1` no recall, cap + eviction. O tipo muda só a *origem* (gate determinístico vs. Update Engine) e o *conteúdo* (cru vs. destilado), não a mecânica de esquecimento.

**Fundamento (papers do repo):**

- **Generative Agents** (Park et al. 2023) — árvore de reflexão: observações → reflexões → reflexões de 2ª ordem, todas no mesmo *memory stream* recuperável. Precedente direto de "exemplar + reflexão num store só, tipados".
- **SAGE** (arXiv:2409.00872) — promove os `r` (self-reflection results) pra LTM, não a trajetória crua.
- **ExpeL** — extração de insights/regras cross-trajectory (a destilação de 2ª ordem → strategy).
- **A-MEM** — notas semânticas que evoluem quando entra nota nova.
- **Learning from Supervision with Semantic and Episodic Memory (2025)** — adaptação reflexiva com as duas memórias.

**Por que tipada e não só-reflexão** (dois custos de ir 100% reflexão, no jurídico):

1. **Perde o raciocínio por precedente** — recuperar o caso concreto parecido e adaptar é como o jurídico raciocina; a reflexão abstrata não substitui o exemplar (ver item 4).
2. **Põe o LLM no caminho de escrita de toda memória recuperável** — hoje a promoção de `exemplar` é determinística, zero LLM, auditável (diferencial vs. Mem0 + requisito de auditoria). Manter o tipo `exemplar` preserva esse caminho; o tipo `reflexão` aceita o LLM porque já é cold path (Update Engine).

**Em aberto:** se o `recall_memory` mistura os dois tipos no mesmo ranking ou o agente pede um tipo ("caso parecido" vs. "lição"); e se o `S` inicial de uma `reflexão` (que nasce curada) deve ser maior que o de um `exemplar`.

### Provenância entre camadas — precondição da reconciliação reversível (added 01/09/2026)

Ponto do Rafael (01/09): pra manter a **Reversible Reconciliation** do SSGM (recuperar de drift ou commit ruim por *replay* do log imutável, não por diffs mantidos à mão — ver [`component-a-tutor-meeting-prep.md`](component-a-tutor-meeting-prep.md)), a cadeia de derivação entre as três camadas tem que ser **explícita e navegável**:

- **Camada 1** — imutável, append-only, IDs estáveis. É a **âncora durável**.
- **Camada 2** — cada entrada guarda `source_trace_ids` → camada 1. `exemplar`: 1:1 (ou 1:N se a janela/caso cobre várias stage-traces). `reflexão`: N:1 (as N traces que o Update Engine analisou).
- **Camada 3** — cada entrada guarda `derived_from` → camada 2 **e** `source_trace_ids` → camada 1 (denormalizado).

**Por que a camada 3 referencia a camada 1 direto, não só via camada 2:** entradas da camada 2 **decaem e são evictadas** (forget-by-disuse + cap). Cadeia só-transitiva (3→2→1) quebra quando a entrada da camada 2 some. A camada 1 nunca é apagada, então o `source_trace_ids` denormalizado na camada 3 é o que garante que a lineage sobrevive.

**Provenância inclui os sinais, não só os traces:** uma `reflexão` / entrada de strategy disparada por um padrão de 👎 ou por um desfecho adverso só é reproduzível por replay se a proveniência guardar **os IDs do Signal Ledger consumidos** junto com os `source_trace_ids`. Replay do log cru sozinho não reconstrói uma strategy acionada por sinal.

**O que destrava:** pegar uma entrada da strategy layer → ver de quais entradas da camada 2 e de quais traces + sinais da camada 1 ela derivou → re-rodar a destilação (score recalibrado, embedding novo, ou depois de um trace ter sido corrigido) e **reconstruir/reajustar a strategy layer** sem manter diffs. Mesmo princípio do "transform re-executável sobre log imutável" (26/08), estendido à camada 3.

### Gate de governança nos dois caminhos de escrita (added 01/09/2026)

Ponto do Rafael (01/09): **os dois writes gerados pelo Update Engine** — a 1ª reflexão (→ camada 2) e a 2ª reflexão / strategy (→ camada 3) — passam por `propose_memory` + gate de governança. É o **Write Validation Gate trigger-agnóstico do SSGM (P1)**: valida a escrita independente do que a disparou (ver §"O que o SSGM contribui aqui").

**Mesma camada de governança, mecanismos diferentes por destino:**

| | Gate da camada 2 (1ª reflexão) | Gate da camada 3 (2ª reflexão / strategy) |
|---|---|---|
| Via | `propose_memory` | `propose_memory` |
| Checa | *grounding* (a reflexão bate com o trace cru que referencia?), dedup (near-duplicate de entrada já existente?), ACL/PII | **Commit Gate (D)** que já existe: NLI `∆M ∧ M_core ⊨ ⊥` + qualidade do sinal |
| Racional | reflexão episódica concreta raramente contradiz o núcleo — o risco dela é alucinação ou duplicata | regra transversal *pode* contradizer o núcleo — o risco dela é inconsistência |

**Assimetria de gatilho 👍/👎:**

- **Filtro determinístico → camada 2** (1ª etapa, antes do Update Engine): usa 👍 **e** 👎 — um 👍 marca um exemplar positivo que vale ser recuperável.
- **Gatilho → camada 3** (passo da strategy): **ponderado pro negativo** — 👎, desfecho adverso, severidade cumulativa, ou **N casos similares acumulados** viram candidatos a regra. Destila-se regra corretiva de falha, não do que já deu certo. Bate com o registro de [31/08](../research-diary/diario_campo_2026-08-31.md): trigger do Update Engine = feedback negativo, não o positivo.
- **Nuance de 31/08 preservada:** o *gatilho* da camada 3 é negativo, mas o Update Engine, quando roda, **lê sucesso E falha** como contexto da reflexão (contraste ExpeL-style). Trigger ≠ input.

### Estratégia 1 — janela sem filtro ("promote-all + forget-by-disuse")

**Status (01/09): descartada como mecanismo primário do v1** — armazenar ruído e contar com o decay pra limpar vai contra o requisito "não armazenar ruído". Mantida aqui como contraste e como possível *piso* opcional (ver "Como compõem").

Pega uma **janela X** de traces (lote por tempo ou por contagem — é gatilho de *quando* rodar o promote+embed, não critério de seleção), promove todos como envelope estruturado, aplica as métricas de decay. Traces que não fazem sentido **decaem e são evictados** pelo cap; isso abre espaço pra próxima janela. Próximo de MemoryBank; respaldo no "forgetting-by-design" do SSGM (esquecimento *é* o filtro).

- **A favor:** nenhum score a calibrar; um mecanismo a menos; degrada de forma graciosa.
- **Contra:** poluição de retrieval na janela de ruído fresco (um exemplar irrelevante servido ao agente jurídico é risco de qualidade, não só ineficiência); decay-como-filtro só limpa se o padrão de recall distinguir sinal de ruído (não testado); passa a depender forte do cap + eviction (item 5, não desenhado); é a resposta "sim, gravamos ruído e ele decai" pra objeção do tutor de 28/08 — tem que ir explícito pra ele.

### Estratégia 2 — promoção dirigida por sinal (eval determinístico)

Em vez de promover a janela inteira, promove só traces com um **aspecto X** detectável de forma determinística. Candidato do Rafael: **erro-seguido-de-recuperação** — o trace registra um erro (tool call com status de erro, retry, guardrail falho, 👎) e *depois* uma conclusão positiva (stage final ok / desfecho favorável / sem 👎 no output final). Alta densidade de aprendizado por trace, contrastivo (o que deu errado × o que consertou). É o mesmo tipo de filtro heurístico determinístico já previsto como 1ª etapa do Update Engine (§"Dois filtros de ruído") — a novidade é **apontá-lo também pro caminho de promoção** (→ camada 2), não só pra reflexão (→ camada 3).

- **A favor:** seleção barata, booleana, sem threshold contínuo a calibrar; sinais estruturais (erro de tool call, retry) provavelmente já existem no banco, ao contrário dos campos DMF-lite; responde à objeção do tutor de forma direta ("analisei o trace e isto vale persistir"); sem poluição — promove uma fatia pequena e caracterizável.
- **Contra:** captura só um tipo de trace útil — perde o exemplar limpo de caso raro (instrutivo sem erro) e o erro-que-continuou-errado (cautelar, ver item 4); "conclusão positiva" costuma ser assíncrona (desfecho vem meses depois) → o eval roda em lote depois, não no write; viés de seleção — a memória recuperável vira um museu de erros-e-correções (pode ser o sinal certo, ou enviesar o agente; ver item 4).

### Como compõem

Com a Estratégia 1 fora como mecanismo primário, a escolha do v1 é sobre **o critério do gate**:

- **(a) filtro booleano por sinal** (Estratégia 2: erro→recuperação, erro de tool call, 👎-seguido-de-correção) — barato, sem calibração, sinais estruturais provavelmente já no banco;
- **(b) score contínuo + limiar** (`S` DMF-lite, `R ≥ θ1`) — depende dos campos existirem e da calibração de `θ1`;
- **(c) os dois:** (a) decide a *admissão*; (b) fornece o `S` inicial (quão grudento) pro ciclo de vida na camada 2.

Lean pro primeiro POC: **(a)**. Migrar pra (c) quando a análise do banco de traces confirmar que os campos do `S` existem. A Estratégia 1 só volta como *piso* opcional se um teste de cobertura mostrar o agente perdendo casos úteis sem sinal de anomalia.

**Decidido (01/09):** o v1 tem um filtro determinístico **antes** do Update Engine (a janela não vai crua pra reflexão). Critério = **(a)**, concretizado pela **família do filtro de anomalia** já definida como 1ª etapa do Update Engine (§"Dois filtros de ruído, não um"): tamanho do trace, nº de tool calls, distribuição de 👎, outlier vs. distribuição. Isso **unifica os dois filtros num só** — o mesmo filtro determinístico serve o caminho de promoção (→ camada 2) e o de reflexão (→ camada 3). O sinal **erro→recuperação** entra como **sub-sinal de prioridade** dentro dele (recebe `S` inicial mais alto), não como o filtro inteiro — um filtro só-erro→recuperação perderia o exemplar limpo de caso raro e o erro-que-continuou-errado (cautelar, item 4). Consequência boa: com o filtro antes do Update Engine, `R ≥ θ1` fica sendo **só a regra de rebaixamento** dentro da camada 2 — a bifurcação entrada-vs-permanência se resolve sozinha.

Falta travar: (i) quais desses sinais existem de fato no banco de traces (bloqueio recorrente — precisa do dado do tutor); (ii) o predicado exato (OR booleano de sinais? limiar de contagem?); (iii) o split imediato (sinais estruturais, disponíveis no write) vs. atrasado (erro→recuperação precisa do desfecho, que é assíncrono).

### Escotilha de escape (comum)

A camada 1 fica **consultável diretamente** (por ID / por query) — não só substrato de auditoria/reflexão. Se a promoção ou o decay derrubaram algo que depois faz falta, o agente ainda desenterra do log cru. É isso que torna o esquecimento agressivo seguro.

### Bifurcação ainda aberta: entrada vs. permanência

A regra `R = e^(−τ/S) ≥ θ1` está fazendo dois trabalhos: decidir **entrada** (log → camada 2) e **permanência/rebaixamento** dentro da camada 2. Mas `τ`-desde-recall e o reforço `S→S+1` só existem *depois* da promoção. Proposta de limpeza: **entrada** = decisão das Estratégias 1/2 (janela ou sinal), não `R`; **`R ≥ θ1`** = só regra de rebaixamento dentro da camada 2. Alinha com o lean do item 2 ("reforço é permanência, não entrada").

## Contrastes — de onde vem cada peça e onde divergimos

| Trabalho | O que faz na promoção | O que a gente pega / muda |
|---|---|---|
| **SAGE** (arXiv:2409.00872) 🔎 | Gate STM→LTM com **duas** faixas θ1>θ2, `S(Iₜ)=H(Iₜ)/f(t)` *entropy-weighted*, cap de capacidade | Pegamos a ideia do gate com threshold + cap; **mudamos** `S` (DMF-lite determinístico, não entropia) e o layering (sem tier STM próprio); a banda exata fica em aberto |
| **MemoryBank** (arXiv:2305.10250) ✅ | `R = e^(−Δt/S)`, `S→S+1` no recall, **só de-prioritiza no ranking, nunca promove nem apaga** | Pegamos a fórmula e o reforço; **adicionamos** a promoção seletiva (que o MemoryBank não tem) e, no componente E, o hard-delete (que ele também não tem) |
| **SSGM** (arXiv:2603.11768) 🔎 | "forgetting-by-design", budget-aware (FiFA / Priority Decay) | Sustenta o cap de capacidade (item 5) como decisão de projeto, não damage control |
| **DarwinMem** (arXiv:2601.22528) 📝 | *Utility-driven Natural Selection* — poda unidades por *survival value* | Padrão adjacente pros itens 5–6 (poda/dedup por utilidade); domínio GUI, não jurídico — pegar o padrão, não a implementação |

## Perguntas objetivas (pro tutor / pra quando a base de traces chegar)

1. Que **campos estruturados** o pipeline emite hoje que serviriam pro `S` DMF-lite? (item 1)
2. A base de traces atual guarda **trajetória completa** ou só desfecho? (pré-condição do chunking, item que já está em [`open-questions.md`](open-questions.md))
3. Um trace de **falha** deve ficar recuperável pelo agente, ou só alimentar a reflexão? (item 4 — decisão de produto tanto quanto técnica)
4. Há um **orçamento** natural pro índice LTM (custo de vetor DB, latência alvo do Sub 3.6)? (item 5)
5. O gate de promoção é peça separada do curador, ou o tutor espera que "o curador" faça tudo? (item 9)

## Como isto vira decisão

- Itens 1, 2, 5: destravam ao **inspecionar a base de traces real** (o tutor vai fornecer).
- Itens 3, 4, 8, 9: decisão de desenho, a fechar **antes do Sub 2.2 travar**.
- Itens 6, 7, e a calibração de `θ1`: **POC do Sub 1.6/1.7** — não dá pra calibrar `θ1` sem rodar contra traces reais anotados.
- A política inteira é **estática** — todos os parâmetros externalizados como config, calibrados à mão no v1 (adaptive calibration é v2 direction, ver [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md)).

## Links

- Fragmentos que esta nota consolida: [`open-questions.md`](open-questions.md) (sub-bullets de 27/08 sobre o SAGE-style promotion gate + item de 31/08 sobre o dono do gate)
- Arquitetura: [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) — componente A (Memory Store + write-path snapshot), E (Forgetting), G (Consolidation)
- Sibling: [`component-a-tutor-meeting-prep.md`](component-a-tutor-meeting-prep.md) — briefing do componente A pro tutor
- Leitura: [`../papers/ssgm-2026.md`](../papers/ssgm-2026.md), [`../papers/memorybank-2023.md`](../papers/memorybank-2023.md), [`../papers/reading-queue.md`](../papers/reading-queue.md) (SAGE #19, DarwinMem #42)
- Diário: [31/08/2026](../research-diary/diario_campo_2026-08-31.md)
