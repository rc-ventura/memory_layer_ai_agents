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
