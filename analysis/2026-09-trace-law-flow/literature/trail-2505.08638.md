# TRAIL — Trace Reasoning and Agentic Issue Localization

**arXiv:** 2505.08638 (v1 13/05/2025 · v3 23/06/2025, cs.AI) · **Autores:** Darshan Deshpande, Varun Gangal, Hersh Mehta, Jitin Krishnan, Anand Kannappan, Rebecca Qian (Patronus AI) · **Venue:** preprint — o PDF não declara conferência e o metadado do arXiv não traz `journal_ref`; formato ACL (tem *Limitations* e *Ethics Statement*), portanto provável submissão \*ACL, mas **isso é inferência minha, não afirmação do paper** · **Lido:** texto completo + apêndices por subagente (🔎), 2026-09-08

**Dataset:** <https://huggingface.co/datasets/PatronusAI/TRAIL> — licença MIT, mas o repositório está **gated** (`gated: auto`, com cláusula de não-recompartilhamento). Verificado em 2026-09-08: a datasets-server API recusa acesso sem autenticação. Splits: `gaia` (117 exemplos) e `swe_bench` (31). Campos: `trace` (string), `labels` (string).

---

## O que é

Três entregas em um só paper:

1. **Uma taxonomia formal de erros de agentes**, organizada em três áreas — *Reasoning Errors*, *System Execution Errors*, *Planning and Coordination Errors* (Figura 1) — com 20 tipos-folha (+1 balde `Domain Specific Errors` que só aparece no prompt do Apêndice A.11).
2. **TRAIL, um dataset de 148 traces anotados por humanos** — 1.987 spans OpenTelemetry, dos quais **575 (28,9%) exibem ao menos um erro**, totalizando **841 erros anotados**, média de 5,68 erros por trace (mediana 5,0). Traces gerados a partir de GAIA (busca em mundo aberto, agente hierárquico HF OpenDeepResearch com `o3-mini-2025-01-31`) e SWE-Bench Lite (agente **CodeAct** single-agent com interpretador Python sandboxado + biblioteca `gitingest`, backbone `claude-3-7-sonnet-20250219`).
3. **Um benchmark de LLM-as-judge sobre esses traces**: dado o JSON OTel cru, o modelo deve produzir *exaustivamente* todos os erros com `category` + `location` (span id) + `evidence` + `description` + `impact`. O melhor modelo (GEMINI-2.5-PRO) faz **11%** de acurácia conjunta.

Por que é o paper mais próximo do que fizemos: a unidade de análise é o **step/span do trace de execução**, não o resultado final da tarefa. E o split SWE-Bench usa **exatamente a nossa arquitetura** — CodeAgent estilo smolagents, única ferramenta real é o interpretador Python + `final_answer`, com lista branca de imports (o prompt completo está no §A.12.1 e inclui a regra *"You can use imports in your code, but only from the following list of modules: ['asyncio', 'collections', 'csv', 'datetime', 'gitingest', ...]"*). Isso torna o split SWE-Bench o comparável mais honesto para a esteira jurídica.

---

## A taxonomia completa

Definições **verbatim** do Apêndice A.11 (o prompt entregue aos modelos, que é a versão operacional da taxonomia). Frequências lidas da Figura 3a — a soma das barras "Combined" bate exatamente com os 841 erros reportados no texto, o que valida a leitura.

### Reasoning Errors — 590 erros (70,2%)

| Sub-área | Tipo | Definição verbatim | swe_bench | gaia | **Total** | **% de 841** |
|---|---|---|---:|---:|---:|---:|
| Hallucinations | **Language-only** | *(sem glosa no prompt; §3.1: "fabricated or ungrounded statements that conflict with real-world knowledge")* | 12 | 41 | **53** | 6,3% |
| Hallucinations | **Tool-related** | "fabricating tool outputs/capabilities" | 6 | 47 | **53** | 6,3% |
| Information Processing | **Poor Information Retrieval** | "Tried to find information that was not relevant to the task" | 13 | 28 | **41** | 4,9% |
| Information Processing | **Tool Output Misinterpretation** | "Made assumptions about the tool output or used the tool output in an incorrect context" | 1 | 16 | **17** | 2,0% |
| Decision Making | **Incorrect Problem Identification** | "Misunderstood the overall task or the local task" | 9 | 19 | **28** | 3,3% |
| Decision Making | **Tool Selection Errors** | "Used the wrong tool for the task" | 0 | 45 | **45** | 5,4% |
| Output Generation | **Formatting Errors** | "Errors with formatting and execution of code or structuring of output in a specific format" | 72 | 124 | **196** | 23,3% |
| Output Generation | *Formatting Error* (variante singular do rótulo, presente no gráfico) | — | 1 | 0 | **1** | 0,1% |
| Output Generation | **Instruction Non-compliance** | "Failed to perform the task provided and instead did something else" | 91 | 65 | **156** | 18,6% |

### System Execution Errors — 31 erros (3,7%)

| Sub-área | Tipo | Definição verbatim | swe_bench | gaia | **Total** | **% de 841** |
|---|---|---|---:|---:|---:|---:|
| Configuration | **Tool Definition Issues** | "The tool was not defined correctly by the user or contains some errors that make it inconsistent with its description. For example, web search tool was defined as a calculator tool" | 0 | 3 | **3** | 0,4% |
| Configuration | **Environment Setup Errors** | "includes permission problems and inability to access resources or API keys" | 0 | 9 | **9** | 1,1% |
| API Issues | **Rate Limiting** | "Like 429" | — | — | **não aparece na Fig. 3a** | — |
| API Issues | **Authentication Errors** | "Like 401/403" | 0 | 5 | **5** | 0,6% |
| API Issues | **Service Errors** | "Like 500" | 0 | 2 | **2** | 0,2% |
| API Issues | **Resource Not Found** | "Like 404" | 0 | 7 | **7** | 0,8% |
| Resource Management | **Resource Exhaustion** | "includes memory overflow" | 1 | 2 | **3** | 0,4% |
| Resource Management | **Timeout Issues** | "The system took too long to respond" | 0 | 2 | **2** | 0,2% |

> ⚠️ Inconsistência a registrar: **Rate Limiting** existe na taxonomia e aparece como exemplo anotado real na Figura 2 (*"RateLimitError: litellm.RateLimitError: AnthropicException"*, impacto HIGH), mas **não tem barra na Figura 3a**. O paper não explica. Não afirme contagem para essa categoria.

### Planning and Coordination Errors — 220 erros (26,2%)

| Sub-área | Tipo | Definição verbatim | swe_bench | gaia | **Total** | **% de 841** |
|---|---|---|---:|---:|---:|---:|
| Context Management | **Context Handling Failures** | "includes window overflow and state tracking or forgetting important context" | 25 | 19 | **44** | 5,2% |
| Context Management | *Context Handling Failure* (variante singular no gráfico) | — | 0 | 5 | **5** | 0,6% |
| Context Management | **Resource Abuse** | "Called the tool excessively due to memory issues" | 18 | 39 | **57** | 6,8% |
| Task Management | **Goal Deviation** | "The system deviated from the task or the subtask" | 2 | 63 | **65** | 7,7% |
| Task Management | **Task Orchestration** | "includes subtask coordination between agents and progress monitoring" | 5 | 44 | **49** | 5,8% |

### Fora das três áreas

| Tipo | Definição verbatim | Frequência |
|---|---|---|
| **Domain Specific Errors** | "Errors that are specific to the domain of the task" | não aparece na Fig. 3a |

**Contagem de tipos:** 20 tipos-folha nas três áreas + `Domain Specific Errors` = **21**. Se contarmos as duas variantes singular/plural que aparecem como rótulos separados no gráfico (`Formatting Error`, `Context Handling Failure`), o gráfico exibe 21 rótulos. As três áreas se subdividem em 9 sub-áreas: Hallucinations, Information Processing, Decision Making, Output Generation, Configuration, API Issues, Resource Management, Context Management, Task Management.

### Distribuição de impacto (Figura 6)

| Impacto | Erros | % |
|---|---:|---:|
| High | 304 | 36,1% |
| Medium | 363 | 43,2% |
| Low | 174 | 20,7% |

Por sub-área (n / Low / Medium / High) — soma confere com 841:

| Sub-área | n | Low | Medium | High |
|---|---:|---:|---:|---:|
| Hallucinations | 106 | 2 (2%) | 10 (9%) | **94 (89%)** |
| Decision Making | 73 | 2 (3%) | 25 (34%) | **46 (63%)** |
| Task Management | 114 | 3 (3%) | 47 (41%) | **64 (56%)** |
| API Issues | 14 | 1 (7%) | 4 (29%) | 9 (64%) |
| Configuration | 12 | 2 (17%) | 2 (17%) | 8 (67%) |
| Resource Management | 5 | 0 | 1 (20%) | 4 (80%) |
| Context Management | 106 | 2 (2%) | 80 (75%) | 24 (23%) |
| Information Processing | 58 | 6 (10%) | 39 (67%) | 13 (22%) |
| **Output Generation** | **353** | **156 (44%)** | 155 (44%) | 42 (12%) |

Leitura que interessa ao projeto: **a família que a nossa regex enxerga (Output Generation) é a de menor impacto médio** — 12% de HIGH. As famílias de alto impacto (Hallucinations 89% HIGH, Decision Making 63%, Task Management 56%) são justamente as invisíveis a uma classificação por exceção.

---

## Metodologia e schema de anotação

**Quem anotou.** *"We selected four annotators with expertise in software engineering and log debugging to label our agent traces."* Critérios de seleção declarados no Ethics Statement: idade 18+ e expertise em ciência da computação — nada mais. Pagamento: *"We pay annotators a total of $12.66 per trace where each trace takes 30-40 minutes to annotate."*

**Como anotaram.** *"Annotators evaluated each LLM and tool span in sequence, marking span ID, error category, evidence, description, and impact (Low/Medium/High) per our taxonomy, and rated overall traces for instruction adherence, plan optimality, security, and reliability."* Custo temporal: ~30 min/trace GAIA, ~40 min/trace SWE-Bench, +20 min de verificação, **totalizando ≈110–120 minutos por trace**.

**Acordo entre anotadores — leia com cuidado.** O paper afirma acordo alto, mas **não reporta κ de Cohen, Krippendorff, nem qualquer coeficiente formal**. O que ele reporta é *taxa de revisão* em quatro rodadas independentes de verificação por ML researchers, sobre um conjunto separado de 63 traces:

> *"For SWE Bench, 30 traces (444 spans) were reviewed, with 5.63% of spans modified—mainly Resource Abuse (33.33%), Language-only Hallucinations (20.83%), and Tool-related Hallucinations (12.5%). For GAIA, 33 traces (697 spans) were reviewed, with 5.31% revised, primarily Language-only Hallucinations (23.08%), Resource Abuse (19.23%), and Poor Information Retrieval (19.23%). These results indicate high inter-annotator agreement during curation."*

Ao citar, diga **"taxa de revisão de ~5% dos spans em rodadas de verificação"**, não "IAA alto" como se fosse κ. E note quais categorias concentram a revisão: **Resource Abuse e alucinações** — exatamente as categorias subjetivas. Isso é um aviso direto para a nossa própria anotação.

### O schema é reusável no nosso trace? **Sim, com adaptação mínima.**

Schema de saída (Apêndice A.11), por erro:

```json
{
  "category": "<tipo-folha da taxonomia>",
  "location": "<span id>",
  "evidence": "<trecho extraído do trace>",
  "description": "<descrição detalhada do erro>",
  "impact": "HIGH | MEDIUM | LOW"
}
```

Mais 4 notas por trace inteiro, escala Likert 1–5, com rubrica textual completa no §A.7.1: `reliability_score`, `security_score`, `instruction_adherence_score`, `plan_opt_score`, cada uma acompanhada de `*_reasoning`, e um `overall`.

Mapeamento para a nossa estrutura:

| Campo TRAIL | Equivalente na esteira | Nota |
|---|---|---|
| `location` (span id) | `(exec_id, role, step)` | Nosso ActionStep agrega thought+code+observation; um span TRAIL é uma chamada de LLM **ou** uma chamada de ferramenta. Unidades não são idênticas — declarar isso ao comparar densidades. |
| `category` | hoje: `familia` + `assinatura` | Precisa passar a carregar **também** o tipo-folha do TRAIL, para citabilidade. |
| `evidence` | `err_msg` (só para erros com exceção) | Para erros semânticos, a evidência tem de sair de `model_output` / `code_action` / `observations`. **Campo que ainda não temos.** |
| `description` | — | **Não temos.** |
| `impact` | — | **Não temos** e é o que mais falta: sem ele, 223 SyntaxError (baratos, recuperáveis) pesam o mesmo que uma alucinação de número de processo. |
| 4 notas Likert por trace | — | **Não temos.** `instruction_adherence` e `plan_optimality` são baratos de anotar e endereçam justamente o ponto cego. |

**Recomendação concreta:** acrescentar `evidence`, `description` e `impact` a `erros_steps.csv`, e criar um `traces_scores.csv` com as 4 notas Likert por `(exec_id, role)`. A rubrica do §A.7.1 é copiável quase literalmente (só a de *security* precisa ser reescrita para o contexto jurídico: vazamento de PII, acesso indevido a documento de outro processo).

---

## Mapeamento contra o trace da esteira jurídica

**Veredicto geral: o mapeamento frouxo do relatório atual ("nossas famílias mapeiam para *system execution errors* e *reasoning errors*") está ERRADO em um ponto central e deve ser corrigido.** "Geração de código" e "Ambiente & sandbox" **não** são *System Execution Errors* no TRAIL. `System Execution Errors` lá é infraestrutura (config, HTTP, memória, timeout) e vale só 3,7% do dataset. Código malformado é `Formatting Errors`, dentro de **Reasoning → Output Generation**.

| Nossa família | n | Tipo(s) TRAIL correspondente(s) | Área TRAIL | Veredicto |
|---|---:|---|---|---|
| **Geração de código** (258) — SyntaxError 223, resposta em markdown sem `final_answer` 33, IndentationError 2 | 258 | **Formatting Errors** ("Errors with formatting and **execution of code** or structuring of output in a specific format") para os 225 de sintaxe; **Instruction Non-compliance** para os 33 de protocolo | Reasoning → Output Generation | ✅ Corresponde bem, mas **é preciso quebrar a família em duas**: o "markdown puro sem `final_answer`" é não-conformidade com instrução, não erro de formatação. |
| **Suposição sobre dados** (205) — KeyError 98, TypeError 60, ValueError 37, AttributeError 8, JSONDecodeError 2 | 205 | Repartida entre **Tool Output Misinterpretation** ("Made assumptions about the tool output or used the tool output in an incorrect context") e **Tool-related Hallucination** ("fabricating tool outputs/capabilities") | Reasoning → Information Processing / Hallucinations | ⚠️ Corresponde, mas **não é uma categoria única no TRAIL**. Critério de corte sugerido: campo/atributo **inexistente no schema** (`KeyError: 'quebra_sigilo'`, `hashDocumento has no attribute get`) → *Tool-related Hallucination* (o agente inventou uma capacidade/estrutura); campo existente usado no contexto errado (TypeError/ValueError de conversão) → *Tool Output Misinterpretation*. |
| **Ambiente & sandbox** (19) — import não autorizado 11, módulo sem import 6, `openpyxl` ausente 1, operação proibida 1 | 19 | **Environment Setup Errors** ("includes permission problems and inability to access resources or API keys") para `openpyxl`/operação proibida; **Instruction Non-compliance** ou **Formatting Errors** para os 11 imports não autorizados | System Execution → Configuration (parcial) | ⚠️ **Parcialmente**. Os 11 "import não autorizado" são violação de uma regra explícita do system prompt (a esteira tem lista branca, igual à do §A.12.1 do TRAIL) — isso é *Instruction Non-compliance*, não falha de ambiente. Só ~8 são genuinamente System Execution. |
| **Suposição sobre estado** (8) — variável de step anterior que falhou, variável fantasma `Observation` | 8 | **Context Handling Failures** ("includes window overflow and **state tracking** or forgetting important context") | Planning & Coordination → Context Management | ✅ Correspondência exata e limpa. |
| **Infra / LLM upstream** (7) — `AgentGenerationError` 6, HTTP 422 1 | 7 | **Service Errors** ("Like 500") — o 422 é HTTP 4xx sem tipo próprio na taxonomia; o TRAIL só tem 401/403, 404, 429, 500 | System Execution → API Issues | ✅ Corresponde, com a ressalva de que 422 não tem casa exata. |
| **Erros na linha de delegação** (20, transversal) | 20 | **Task Orchestration** ("includes subtask coordination between agents and progress monitoring") | Planning & Coordination → Task Management | ✅ Corresponde — mas é só a ponta com exceção. |
| **Repetição da mesma assinatura em steps consecutivos** (48 pares, 14%) | — | Vizinho de **Resource Abuse**, mas **não é o mesmo conceito**: no TRAIL, Resource Abuse é chamada repetida da ferramenta ("Called the tool excessively"), independentemente de erro. Nossa métrica só conta repetições **de erro**. | Planning & Coordination → Context Management | ⚠️ Renomear no relatório. O achado é nosso e é bom, mas não deve ser vendido como "Resource Abuse do TRAIL" — a versão TRAIL é mais ampla e nós ainda não a medimos. |

**Sem correspondência em nenhuma direção:**

- **Do nosso lado, sem casa no TRAIL:** erros de *domínio jurídico* (prazo errado, tipo de documento errado, cálculo trabalhista incorreto, vazamento de PII entre processos). O único abrigo é o balde `Domain Specific Errors`, que **não tem um único exemplo anotado** no dataset liberado. Este é o gap que a nossa pesquisa pode preencher e citar como contribuição.
- **Do lado do TRAIL, sem detecção nossa:** 9 tipos inteiros — a seção seguinte.

---

## O ponto cego da classificação por exceção de runtime

### 1 · O tamanho do buraco

Classificando cada tipo do TRAIL por **"levanta exceção no runtime Python / retorna status HTTP de erro?"**:

| Bucket | Tipos | Erros | % de 841 |
|---|---|---:|---:|
| **A — Estruturalmente invisível** (por definição não levanta exceção) | Instruction Non-compliance (156), Goal Deviation (65), Resource Abuse (57), Language-only Hallucination (53), Task Orchestration (49), Tool Selection Errors (45), Poor Information Retrieval (41), Incorrect Problem Identification (28), Tool Definition Issues (3) | **497** | **59,1%** |
| **B — Parcialmente visível** (parte das instâncias quebra o código, parte não) | Formatting Errors (196+1), Tool-related Hallucination (53), Context Handling Failures (44+5), Tool Output Misinterpretation (17) | **316** | 37,6% |
| **C — Totalmente visível por exceção/status** | Environment Setup (9), Resource Not Found (7), Authentication (5), Resource Exhaustion (3), Timeout (2), Service Errors (2) | **28** | **3,3%** |

**Resposta direta à pergunta: no mínimo 59% dos erros do dataset TRAIL caem em tipos que a nossa regex não conseguiria pegar de jeito nenhum.** E a fatia que a nossa metodologia captura *integralmente* é de apenas **3,3%**. Todo o resto dos nossos 498 erros vive no bucket B — ou seja, mesmo onde acertamos a categoria, estamos vendo só a fração das instâncias que por acaso quebrou o interpretador.

**Três evidências independentes convergem para o mesmo tamanho de buraco:**

1. **Densidade de erro por step.** TRAIL: 575 de 1.987 spans com erro = **28,9%**. Nós: 498 de 5.781 ActionSteps = **8,6%**. Fator ~3,4×. *(Ressalva: span TRAIL ≠ ActionStep nosso — um ActionStep agrega o que lá são 2+ spans; e os traces do TRAIL têm erro induzido de propósito — ver Ressalvas. A comparação é indicativa, não métrica.)*
2. **Fração de execuções com erro.** TRAIL: 144 de 148 traces (~97%). Nós: 37% das execuções. Fator ~2,6×.
3. **Distribuição por área — o sinal mais nítido:**

| Área TRAIL | TRAIL (841) | Esteira jurídica (498) |
|---|---:|---:|
| Reasoning Errors | 70,2% | 93% (463) |
| **Planning and Coordination** | **26,2%** | **1,6% (8)** |
| System Execution | 3,7% | 5,2% (26) |

**Planning & Coordination é 26% do TRAIL e 1,6% do nosso.** Isso não é porque a esteira planeja bem — é porque *Goal Deviation*, *Task Orchestration*, *Resource Abuse* e *Context Handling* quase nunca levantam `SyntaxError`. É o formato exato do nosso ponto cego, medido.

### 2 · Onde dói mais: impacto

Cruzando a Figura 6b com os buckets acima: das 304 falhas HIGH do TRAIL, ~241 (**79%**) estão em sub-áreas invisíveis à exceção (Context Management 24, Decision Making 46, Hallucinations 94, Information Processing 13, Task Management 64). A nossa família mais visível — Output Generation — é a de **menor** impacto do dataset (12% HIGH, 44% LOW).

Traduzindo para a esteira: **223 `SyntaxError` são baratos e auto-evidentes; uma alucinação de número de processo ou um cálculo trabalhista fora do prazo é cara, é HIGH, e hoje sai do nosso funil sem deixar rastro.**

### 3 · O split que espelha a nossa arquitetura confirma o diagnóstico

O split SWE-Bench do TRAIL usa CodeAct + interpretador Python + `final_answer` + lista branca de imports — a nossa arquitetura. Distribuição dos seus 256 erros:

| Tipo | n | % do split | Nossa regex vê? |
|---|---:|---:|---|
| **Instruction Non-compliance** | **91** | **35,5%** | ❌ (só os 33 de markdown puro) |
| Formatting Errors | 72 (+1) | 28,5% | ✅ parcialmente |
| Context Handling Failures | 25 | 9,8% | ❌ (só 8 de "estado") |
| Resource Abuse | 18 | 7,0% | ❌ |
| Poor Information Retrieval | 13 | 5,1% | ❌ |
| Language-only Hallucination | 12 | 4,7% | ❌ |
| Incorrect Problem Identification | 9 | 3,5% | ❌ |
| Tool-related Hallucination | 6 | 2,3% | ⚠️ parcial |
| Task Orchestration | 5 | 2,0% | ❌ |
| Goal Deviation | 2 | 0,8% | ❌ |
| Resource Exhaustion / Tool Output Misinterpretation | 1 + 1 | 0,8% | ⚠️ |

**No agente arquiteturalmente idêntico ao nosso, o erro nº 1 não é `SyntaxError` — é `Instruction Non-compliance`, com 35,5%.** É o tipo que estamos praticamente cegos para ver.

### 4 · Como passar a ver — análises executáveis sobre os dados que já temos

Ordenadas por (impacto × facilidade). Campos disponíveis: `model_output` (thought), `code_action`, `observations`, `tool_calls`, `model_input_messages`; e por step `exec_id, agente, role, step, dur_s, tok_in/out/tot, err_type, err_msg, is_final, assinatura, familia, em_delegacao`.

| # | Tipo TRAIL cego | Campo | Heurística — determinística, sem LLM salvo onde indicado | Custo | Por que agora |
|---|---|---|---|---|---|
| **1** | **Resource Abuse** (6,8%) | `code_action` de steps **sem erro** | Normalizar (strip de espaços/comentários), hashear e contar repetições exatas/quase-exatas por `(exec_id, role)`; idem para invocações de subagente com o **mesmo** argumento `task=`. É *o mesmo código* que já produziu os 48/354 pares repetidos — basta rodar sobre steps de sucesso. ⚠️ Convenção do TRAIL: *"only mark the last instance of the error in the trace as the location"* | **Trivial** | Reaproveita código pronto; produz uma categoria TRAIL inteira que hoje é zero |
| **2** | **Tool Selection Errors** (5,4%) | `model_output` × `code_action` | Extrair do *thought* o nome do agente/ferramenta que ele **diz** que vai chamar (regex sobre o inventário: `ConversationAgent`, `CalculoCivel`, `RespostaBacen`, `envia_excel_para_usuario`…) e comparar com os nomes efetivamente chamados no código (`ast.parse` → `ast.Call`). Divergência = candidato. **O exemplo canônico da Figura 2 do TRAIL é literalmente isso:** *"The agent's thought said: 'I'll now call search_agent with this detailed task.' However, the 'Code:' generated printed the task through the interpreter instead of calling agent"* | Baixo | Alta precisão, zero LLM, e o paper nos dá o exemplo pronto para citar |
| **3** | **Language-only Hallucination** (6,3%, **89% HIGH**) | `model_output` + payload do `final_answer` vs. `observations` anteriores | *Groundedness* determinística por entidade tipada — o fluxo jurídico favorece isso: extrair via regex número de processo CNJ, CPF/CNPJ, datas, valores monetários, nomes de partes do *thought*/resposta e testar pertinência na concatenação de todas as observações anteriores daquele `(exec_id, role)`. Token tipado que **nunca apareceu** numa observação = alucinação candidata | Baixo–médio | **A análise de maior valor do projeto.** É o erro de maior impacto do TRAIL e é o risco material de uma esteira jurídica |
| **4** | **Instruction Non-compliance** (18,6% geral, **35,5% no split CodeAct**) | `model_input_messages[0]` (system+task) × `code_action` × `final_answer` | Enumerar as regras explícitas do system prompt da esteira (lista branca de imports, "responda só via `final_answer`", limites de tamanho, ferramenta obrigatória para Excel) e escrever **um detector determinístico por regra**. Os 11 "import não autorizado" e os 33 "markdown puro" já são dois desses detectores — faltam os demais. Para o resíduo semântico ("fez outra coisa"), LLM-as-judge **por step**, não pelo trace | Médio | É o erro nº 1 do split arquiteturalmente idêntico ao nosso |
| **5** | **Task Orchestration** (5,8%) | `code_action`, `observations`, `tool_calls` | Montar o **grafo de delegação** (regex `<Agente>(task=...)` no código) e checar: (a) resultado do subagente nunca referenciado depois; (b) mesma subtarefa delegada a dois agentes; (c) `final_answer` do manager ignora o retorno do subagente; (d) subagente falhou e o manager seguiu como se tivesse dado certo. Os nossos 20 erros `em_delegacao` são só o caso (d) *com* exceção | Médio | Somos multi-agente hierárquico; o TRAIL mostra 5,8% aqui e nós reportamos ~0 |
| **6** | **Context Handling Failures** (5,8%) | `tok_in`, `model_input_messages`, `observations` | (a) pressão de janela: steps com `tok_in` no topo da distribuição ou `model_input_messages` truncado; (b) **re-pergunta**: o agente busca informação que já está numa observação anterior do mesmo `(exec_id, role)` — casar a chave da consulta contra observações passadas; (c) retenção de instrução: violação tardia de restrição posta no system prompt. Nossos 8 de "estado" são só o sub-caso que quebrou | Médio | Categoria com **F1 ≈ 0,00 em quase todos os LLMs** — tem de ser determinística, não LLM |
| **7** | **Tool-related Hallucination** (6,3%) | `code_action` | `ast.parse` → coletar todos os nomes chamados; diferença contra o inventário autorizado de ferramentas/agentes. Parte vira `NameError` (já visível), mas o caso de o *thought* **afirmar** uma capacidade/saída que nunca foi chamada, não | Baixo | Reaproveita o parser AST do item 2 |
| **8** | **Poor Information Retrieval** (4,9%) | `observations` | Observações vazias / "nenhum resultado" / zero linhas; ou observação sem sobreposição lexical com a task. Na esteira: consultas que retornam conjunto documental vazio, ou tipo de documento não relacionado ao pedido | Baixo | Barato; F1 do Gemini aqui é 0,50 — categoria "detectável" |
| **9** | **Incorrect Problem Identification** (3,3%) | `model_output` do primeiro step × task | O mais difícil: exige LLM-as-judge sobre (task, primeiro thought). Proxy determinístico específico nosso: `RoteadorCivel` cuja rota escolhida contradiz palavras-chave da task | Alto | Deixar por último |
| **10** | **Goal Deviation** (7,7%) | `model_output` ao longo dos steps | Deriva semântica: similaridade de embedding entre o thought de cada step e o enunciado da task; sinalizar queda monotônica. Proxy barato: execuções com nº de steps acima do p90 do papel **e** sem `final_answer` cedo | Alto | F1 do Gemini é 0,70 aqui — é a categoria onde vale mais usar LLM do que heurística |
| **11** | **Formatting Errors — a metade invisível** | payload do `final_answer` | Validar o payload contra o schema que a esteira espera (string vs. dict, markdown onde se espera JSON). Executa sem erro, entrega errado | Baixo | Fecha o bucket B |

**Sugestão de sequenciamento:** #1, #2, #7 numa rodada (todos são AST/hash, um dia de trabalho, três categorias TRAIL novas); #3 na rodada seguinte, isolada, porque é o achado de maior valor de tese; #4 e #5 depois; #9/#10 só quando houver um pipeline de LLM-as-judge validado.

---

## Viabilidade de automatizar a categorização (o resultado de 11%)

### O que exatamente é 11%

O **11%** do abstract é a *joint accuracy* do GEMINI-2.5-PRO — categoria **e** localização corretas — agregada nos dois splits. A Tabela 1 abre: **GAIA 0,183 e SWE-Bench 0,050**; a conclusão repete "18% em GAIA e 5% em SWE Bench". Decompondo, os números são bem menos catastróficos:

| Métrica (GEMINI-2.5-PRO) | GAIA | SWE-Bench |
|---|---:|---:|
| Category F1 (só a categoria) | 0,389 | 0,148 |
| Location Accuracy (só o span) | 0,462 | 0,817 |
| **Joint** | 0,183 | 0,050 |

O melhor Location Acc do dataset é do GEMINI-2.5-PRO em SWE-Bench: **0,817**. O melhor Category F1 em GAIA é 0,389. **A tarefa que o benchmark mede não é a tarefa que queremos.** Eles pedem: dado o JSON OTel cru de um trace inteiro, produza *exaustivamente* todos os erros, com span id, evidência, descrição e impacto, num único passe.

### Por que os LLMs vão mal — as razões que o paper dá

1. **Comprimento de entrada.** Tabela 2: os traces GAIA vão a **7,50M tokens** (máx., tokenizer gpt-4.1), média 286,85K; SWE-Bench média **616,92K**. Três dos oito modelos nem processam o contexto (marcados `CLE`). E: *"We find all performance metrics to be anti-correlated with input length"* — Pearson −0,379 (localização), −0,291 (joint), −0,296 (categoria).
2. **Horizonte de geração longo.** A saída anotada tem média de 1,11–1,93K tokens e máximo ~5K — fração significativa do teto de saída de vários modelos.
3. **Dados estruturados são difíceis para LLM** (citam Guo et al. 2023; Sui et al. 2024).
4. **Raciocínio ajuda, e ajuda proporcionalmente ao esforço.** Modelos com reasoning batem os sem reasoning em 1,5–8× na joint accuracy; o mesmo `o3` degrada monotonicamente ao baixar o `reasoning.effort` (Cat. F1 0,296 → 0,277 → 0,264; Joint 0,092 → 0,104 → 0,071).
5. **Cauda longa de categorias raras** — reconhecido nas *Limitations*.

### O que isso diz sobre o nosso pipeline — veredicto

**Automatizar é viável, mas não da forma que o benchmark testa.** Quatro decisões de projeto que caem direto do paper:

1. **Separar localização de categorização.** Boa parte do 11% morre na localização. Nós **já temos** a localização de graça — `(exec_id, role, step)` com `err_type`/`err_msg` para o bucket C+B, e os detectores determinísticos da seção anterior para o bucket A. Se a localização é dada, o problema vira classificação, cujo teto medido é ~0,39 F1 macro e bem mais alto nas categorias que importam.
2. **Não mandar o trace inteiro. Mandar um step.** O driver dominante do fracasso é o comprimento de entrada, e a correlação é negativa e forte. O prompt deve conter *task + thought + code + observation* de **um** step (mais, no máximo, a observação anterior) — algo entre 2K e 20K tokens, não 600K. Isso sai da região da curva onde os modelos quebram.
3. **Escolher categorias pela detectabilidade medida, não pelo gosto.** Figura 4, F1 por categoria do GEMINI-2.5-PRO: **automatizáveis** — Goal Deviation 0,70, Tool Output Misinterpretation 0,67, Language-only 0,59, Formatting Errors 0,57, Environment Setup 0,57, Poor Information Retrieval 0,50; **não automatizáveis por LLM** — Tool-related Hallucination 0,00, Context Handling Failures 0,00, Tool Definition Issues 0,00, Task Orchestration 0,08, Tool Selection 0,26. O paper é explícito: *"Among the most challenging categories, Context Handling Failures stand out, as nearly all models score an F1 of 0.00, indicating these errors demand advanced reasoning."* Feliz coincidência: **as categorias em que o LLM falha são justamente as que se detectam bem por estrutura** (hash de código repetido, grafo de delegação, pressão de janela). A arquitetura certa é **híbrida, e a divisão de trabalho é ditada por esses números.**
4. **Usar modelo com reasoning, esforço alto.** É a única alavanca de modelo que o paper mostra funcionando de forma consistente.

**Impacto na tese.** A geração automática de unidades de memória **não depende de resolver TRAIL**. Depende de classificar corretamente um step já localizado, dentro de um vocabulário fechado e específico do domínio, e ainda assim o candidato nº 2 do relatório (*schema real por ferramenta*) é minerável **sem LLM nenhum** — basta agregar os KeyError/AttributeError. O paper é o argumento de que **não se deve** delegar a categorização inteira a um juiz LLM sobre o trace cru; é também o argumento de que a alternativa determinística+focada que já estamos construindo é a resposta certa. Vale citar assim, e não como "LLMs não conseguem analisar traces".

**Custo humano como referência.** ~110–120 min/trace e US$ 12,66/trace, 4 anotadores, 4 rodadas de verificação. Para os nossos 840 traces com memória, anotação humana integral é inviável (~1.700 horas). Isso, e não o 11%, é o argumento econômico para o pipeline híbrido — com uma amostra humana de validação nos moldes deles.

---

## Ressalvas ao citar

1. **Domínio.** GAIA (busca em mundo aberto, perguntas de assistente geral) e SWE-Bench Lite (correção de issues em repositórios GitHub). **Nada jurídico, nada em português, nada em produção, nada sob dado regulado.** Erros de domínio jurídico — prazo, tipo documental, cálculo, vazamento de PII entre processos — não têm tipo próprio na taxonomia; o único abrigo é `Domain Specific Errors`, que **não tem um único exemplo anotado** no dataset. Ao citar TRAIL como validação da nossa taxonomia, diga que ele valida **o método** (anotação por step, taxonomia de três áreas, schema evidence/description/impact), não **o vocabulário completo** para o nosso domínio.
2. **Erros parcialmente induzidos — a ressalva mais importante para comparar distribuições.** No split SWE-Bench: *"To further organically introduce errors into this agent system, we add instructional constraints such as output length limits and force exploration via prompts."* Ou seja, a alta incidência de *Instruction Non-compliance* e *Formatting Errors* é, em parte, **fabricada por desenho experimental**. **A distribuição do TRAIL não é uma taxa-base natural** e não deve ser comparada numericamente com a nossa como se fosse. O que sobrevive à ressalva é o argumento **qualitativo**: as categorias existem, são anotáveis, e são invisíveis a exceções.
3. **Escala e unidade.** 148 traces, 1.987 spans, 841 erros. Nós temos 840 memórias, 5.781 ActionSteps. Um *span* OTel deles ≈ uma chamada de LLM **ou** de ferramenta; um *ActionStep* nosso agrega thought+code+observação. Comparações de densidade (28,9% vs. 8,6%) são indicativas, não métricas.
4. **Anotação sem coeficiente formal de acordo.** Nenhum κ. Só taxa de revisão (~5% dos spans) em 63 traces. Diga isso exatamente.
5. **Só texto.** *Limitations*: *"The TRAIL dataset and taxonomy are primarily focused on text-only inputs and outputs but recent advancements in multimodal agentic systems require careful extension of the taxonomy."* A esteira jurídica processa PDFs e planilhas — território fora do escopo declarado.
6. **Cauda longa reconhecida pelos próprios autores.** *"One additional limitation of TRAIL is the large number of tail categories with very few examples."* Categorias com n=2, n=3 (Timeout, Service Errors, Resource Exhaustion, Tool Definition Issues) e os F1 de 1,00 na Figura 4 sobre esses n minúsculos **não sustentam conclusão nenhuma**.
7. **Inconsistências internas menores, para não sermos pegos.** (a) O texto diz 148 traces; a Tabela 5 lista 118 GAIA + 31 SWE = 149; o HuggingFace publica 117 + 31 = 148. (b) *Rate Limiting* está na taxonomia e aparece como exemplo anotado na Figura 2, mas não tem barra na Figura 3a. (c) O gráfico exibe rótulos singular/plural duplicados (`Formatting Error` n=1, `Context Handling Failure` n=5), sugerindo normalização imperfeita dos rótulos de anotação. Citar contagens do nível de tipo com essa margem.
8. **Versão.** Citar a **v3 (23/06/2025)**. Preprint sem venue declarado — não atribuir conferência.
9. **Acesso ao dataset.** MIT, mas **gated** no HuggingFace, com cláusula de não-recompartilhamento fora de repositório privado/gated. Se formos usar os labels, é preciso aceitar os termos com uma conta — e não podemos redistribuir.

---

## Trechos literais de apoio

**Taxonomia (Apêndice A.11, prompt entregue aos modelos):**
> `|-- Reasoning Errors` / `| |-- Hallucinations` / `| | |-- Language-only` / `| | |-- Tool-related (fabricating tool outputs/capabilities)` / `| |-- Information Processing` / `| | |-- Poor Information Retrieval (Tried to find information that was not relevant to the task)` / `| | |-- Tool Output Misinterpretation (Made assumptions about the tool output or used the tool output in an incorrect context)` / `| |-- Decision Making` / `| | |-- Incorrect Problem Identification (Misunderstood the overall task or the local task)` / `| | |-- Tool Selection Errors (Used the wrong tool for the task)` / `| |-- Output Generation` / `| |-- Formatting Errors (Errors with formatting and execution of code or structuring of output in a specific format)` / `| |-- Instruction Non-compliance (Failed to perform the task provided and instead did something else)`

**Distribuição:**
> "Following the post-annotation review, we found errors in 114 GAIA traces and 30 from SWE Bench. As shown in Figure 3, these errors cover various categories, with most falling under *Output Generation*. Specifically, *Formatting Errors* and *Instruction Non-compliance* make up 353 of 841 total errors—nearly 42%. In contrast, *System Execution Errors* are rare."

**Por que a cauda importa:**
> "Second, although infrequent, errors in categories like API failures can be catastrophic and are critical to detect, as they are often difficult to recover from, unlike errors due to goal deviation or tool misinterpretation. […] While model hallucinations and resource management issues greatly affect agent behavior, about 44% of *Output Generation* errors are low impact. This underscores need for a classification scheme that includes rare but significant error types."

**Arquitetura do split SWE-Bench (≡ à nossa) e indução deliberada de erros:**
> "Parallelly, to explore single-agent planning errors and elicit context handling errors for the SWE-Bench split, we use a CodeAct agent (Wang et al., 2024c) and provide it access to a sandboxed environment, a python interpreter and the gitingest library. We select claude-3-7-sonnet-20250219 as the backbone model due to its strong performance on software engineering tasks. **To further organically introduce errors into this agent system, we add instructional constraints such as output length limits and force exploration via prompts.**"

**Regra da lista branca de imports no system prompt deles (§A.12.1) — igual em espírito à da esteira:**
> "8. You can use imports in your code, but only from the following list of modules: ['asyncio', 'collections', 'csv', 'datetime', 'gitingest', 'io', 'itertools', 'json', 'math', 'os', 'pandas', 'queue', 'random', 're', 'requests', 'stat', 'statistics', 'sys', 'time', 'unicodedata']"

**Anotação:**
> "We selected four annotators with expertise in software engineering and log debugging to label our agent traces. To assess agreement, a separate set of 63 traces was assigned. Results based on these indicate high inter-annotator agreement during curation."

> "Annotators evaluated each LLM and tool span in sequence, marking span ID, error category, evidence, description, and impact (Low/Medium/High) per our taxonomy, and rated overall traces for instruction adherence, plan optimality, security, and reliability."

> "For SWE Bench, 30 traces (444 spans) were reviewed, with 5.63% of spans modified—mainly Resource Abuse (33.33%), Language-only Hallucinations (20.83%), and Tool-related Hallucinations (12.5%)."

> "We pay annotators a total of $12.66 per trace where each trace takes 30-40 minutes to annotate."

**Exemplo canônico de *Tool Selection Error* (Figura 2) — thought diz uma coisa, código faz outra:**
> `"category": "Tool Selection Error"` … `"description": "The agent's thought said: 'I'll now call search_agent with this detailed task.' However, the 'Code:' generated printed the task through the interpreter instead of calling agent"`, `"impact": "MEDIUM"`

**Exemplo canônico de *Instruction Non-compliance* (Figura 2):**
> `"category": "Instruction Non-compliance"` … `"description": "The model didn't submit the final answer as a direct patch but instead provided info about repository"`, `"impact": "HIGH"`

**Exemplo canônico de *Language-only* (Figura 2) — afirmação sem evidência no trace:**
> `"evidence": "Thought: The tree variable doesn't seem to contain file paths as I expected"`, `"description": "The model says \"The tree variable doesn't seem to contain file paths as I expected\", without any evidence or additional exploration"`, `"impact": "HIGH"`

**Convenção de localização para erros repetidos:**
> "In the case of \"Resource Abuse\" error, only mark the last instance of the error in the trace as the location of the error. For all other errors, you must mark the first instance of the error in the trace as the location of the error."

**Dificuldade da tarefa:**
> "Our evaluations reveal that modern long context LLMs perform poorly at trace debugging, with the best GEMINI-2.5-PRO model scoring a mere 11% on TRAIL."

> "We find all performance metrics to be anti-correlated with input length, as detailed in Table 3. This supports the hypothesis that longer input raw traces increase the difficulty of TRAIL for models."

> "Among the most challenging categories, Context Handling Failures stand out, as nearly all models score an F1 of 0.00, indicating these errors demand advanced reasoning. The only exception is CLAUDE-3.7-SONNET, which achieves a relatively better score of 0.18."

**Limitações declaradas:**
> "The TRAIL dataset and taxonomy are primarily focused on text-only inputs and outputs but recent advancements in multimodal agentic systems require careful extension of the taxonomy to handle errors arising from new categories such as multimodal tool use. One additional limitation of TRAIL is the large number of tail categories with very few examples."

---

## Ações decorrentes para o relatório de achados

1. **Corrigir §6** do `02-relatorio-achados.md`: "geração de código" e "ambiente/sandbox" **não** são *System Execution Errors* do TRAIL — são *Reasoning → Output Generation* (Formatting Errors / Instruction Non-compliance). O bucket System Execution do TRAIL vale 3,7%.
2. **Quebrar a família "Geração de código"** em *Formatting Errors* (225 de sintaxe) e *Instruction Non-compliance* (33 de protocolo + 11 de import não autorizado).
3. **Renomear** o achado de repetição consecutiva: é vizinho, mas não idêntico, ao *Resource Abuse* do TRAIL.
4. **Acrescentar uma seção de ponto cego** ao relatório, com o número: ≥59% dos erros do TRAIL são de tipos que a nossa metodologia não detecta, e a nossa fatia integralmente visível é 3,3%.
5. **Adicionar `evidence`, `description`, `impact`** a `erros_steps.csv` e criar `traces_scores.csv` com as 4 notas Likert do §A.7.1.
6. **Rodar as análises #1, #2, #7** (hash de `code_action`, thought×código via AST, inventário de ferramentas) — um dia de trabalho, três categorias TRAIL novas, nenhum LLM.
