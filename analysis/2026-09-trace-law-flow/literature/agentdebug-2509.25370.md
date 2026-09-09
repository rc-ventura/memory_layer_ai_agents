# AgentDebug — Where LLM Agents Fail and How They can Learn From Failures

**arXiv:** 2509.25370v1 [cs.AI], submetido em 29 Sep 2025 · **Autores:** Kunlun Zhu, Zijia Liu, Bingxuan Li, Muxin Tian (contribuição igual), Yingxuan Yang, Jiaxun Zhang, Pengrui Han, Qipeng Xie, Fuyang Cui, Weijia Zhang, Xiaoteng Ma, Xiaodong Yu, Gowtham Ramesh, Jialian Wu, Zicheng Liu, Pan Lu, James Zou, Jiaxuan You — UIUC, Stanford, AMD, OpenManus, U. Toronto, Likelihood Lab · **Venue:** **nenhum declarado no PDF** — é preprint arXiv v1; não há cabeçalho de conferência nem nota de aceitação. Não citar como paper de conferência. · **Código:** github.com/ulab-uiuc/AgentDebug (MIT) · **Dataset:** AgentErrorBench, link Google Drive no README do repo · **Lido:** ✅ **Rafael leu — 09/09/2026** (discussão dirigida em sessão: taxonomia, 5 módulos, Stages 1–3, definição de erro crítico, re-rollout, o que adotar/não adotar, o âncora custo+reincidência vs. `Eval(τ)`). Antes: texto completo + apêndices A.1–A.6 + código do repositório, por subagente (🔎), 2026-09-08

> Convenção deste arquivo: tudo entre aspas em inglês é **verbatim** do PDF ou do código. Onde escrevo "o paper não trata disso", verifiquei por busca no texto completo. Onde escrevo "inferência minha", é leitura minha, não afirmação dos autores.

---

## O que é

Três contribuições empacotadas:

1. **AgentErrorTaxonomy** — taxonomia modular de modos de falha em 5 módulos (memory, reflection, planning, action, system).
2. **AgentErrorBench** — 200 trajetórias **de falha** anotadas à mão (100 ALFWorld, 50 WebShop, 50 GAIA), rotuladas passo a passo por módulo e tipo de erro, mais a identificação do "erro crítico".
3. **AgentDebug** — framework de 3 estágios que analisa a trajetória, isola o erro-raiz e gera feedback acionável para **re-executar a mesma tarefa** a partir do passo crítico.

A tese central do paper é uma só, e está no box de insight (verbatim):

> "**Key Insight.** Error propagation is the primary bottleneck in LLM agent reliability. Early mistakes rarely remain confined; instead, they cascade into subsequent steps, distorting reasoning, compounding misjudgments, and ultimately derailing the entire trajectory."

O rollout que eles debugam **não é um agente qualquer**: eles impõem uma arquitetura modular no *prompt*, obrigando o modelo a emitir `<memory>`, `<reflection>`, `<plan>` e `<action>` em tags separadas a cada passo (Figuras 17–19). É essa decomposição forçada que torna a atribuição por módulo possível. A ablação 7c confirma que a própria estratégia "Modular" é a que melhor performa (0.38 vs. ReAct 0.26, Reflection 0.32, Memory+ReAct 0.34, Act Only 0.10). **Isso é uma dependência forte e é o primeiro obstáculo para transportar o método para a minha esteira**, que não emite essas tags.

---

## AgentErrorTaxonomy (17 tipos, 5 módulos)

Definições **verbatim** da Tabela 2 (Apêndice A.2) do PDF. Coloco ao lado o nome usado no código (`detector/error_definitions.py`), que às vezes difere, e a definição estendida do código quando ela acrescenta algo.

| Módulo | Tipo (paper, Tab. 2) | Chave no código | Definição verbatim (paper) |
|---|---|---|---|
| Memory | Over-simplification / Incomplete Summary | `over_simplification` | "Summarizes past info too crudely, ignoring details; leads to flawed reasoning." |
| Memory | Hallucination (False Memory) | `hallucination` | "Recalls events or states that never happened, filling missing gaps with fabricated info." |
| Memory | Retrieval Failure | `memory_retrieval_failure` | "Relevant info exists but is not retrieved when needed." |
| Reflection | Progress Misassessment | `progress_misjudge` | "Incorrectly evaluates progress (too optimistic, too pessimistic, or misses completion)." |
| Reflection | Outcome Misinterpretation | `outcome_misinterpretation` | "Executes an action but misreads the immediate result or environment feedback." |
| Reflection | Causal Misattribution | `causal_misattribution` | "Correctly notes failure but blames the wrong cause, misguiding subsequent plans." |
| Reflection | Hallucination | `hallucination` | "Reflects on events/results that never occurred." |
| Planning | Constraint Ignorance | `constraint_ignorance` | "Ignores limits (time, budget, space, etc.) when forming plans." |
| Planning | Impossible Action | `impossible_action` | "Plans a step that is physically/logically impossible given current preconditions." |
| Planning | Inefficient Planning | `inefficient_plan` | "Plan is overly long or illogical; wastes steps and risks hitting limits." |
| Action | Planning–Action Disconnect | `misalignment` | "Chosen actions do not align with the stated plan intent." |
| Action | Format Error | `format_error` | "Produces syntactically invalid actions." |
| Action | Parameter Error | `parameter_error` | "Generates unreasonable or malformed parameters." |
| System | Step Limit Exhaustion | `step_limit` | "Fails due to reaching the maximum step cap despite reasonable behavior." |
| System | Tool Execution Error | `tool_execution_error` | "External tool/API misbehaves or errors, causing downstream failures." |
| System | LLM Limit | `llm_limit` | "Fails due to API/model constraints (e.g., timeouts, token limits)." |
| System | Environment Error | `environment_error` | "Simulator/environment breaks expected rules (bug/crash/network), not agent's fault." |

### Discrepância a registrar: são 17 ou 18?

A Tabela 2 do paper lista **17**. Mas:

- O **código** (`error_definitions.py`) define um 18º tipo, `action / invalid_action` — *"Uses action that does not exist"*, exemplo *"Action is not in the available action list"* — que **não aparece na Tabela 2**.
- Os **diagramas Sankey** das anotações humanas (Figuras 3, 11) contam explicitamente `Invalid Action (2)` no ALFWorld. Ou seja: o tipo foi usado na anotação e sumiu da tabela do apêndice.
- O código define ainda um bucket `others / others` — *"All remaining problems not previously defined or discussed"* — que o prompt de detecção de erro crítico trata como categoria válida ("Others category captures unusual failures not covered by standard error types").
- O README do repo diz "17 error types across 5 modules" mas a tabela do próprio README lista 18.

**Ao citar, dizer "17 tipos (18 no código liberado, que acrescenta `invalid_action`), mais um bucket `others`."** Não repetir "17" sem a ressalva.

### Distribuição observada (Sankey, Figura 3 — combinado GAIA + ALFWorld + WebShop, 200 trajetórias)

| Módulo | n | Tipos |
|---|---|---|
| Plan | 78 | Inefficient Plan 48, Impossible Action 16, Constraint Ignorance 14 |
| Reflection | 39 | Progress Misjudge 20, Outcome Misinterpretation 13, Causal Misattribution 5 |
| Memory | 38 | Over Simplification 22, Hallucination 13, Memory Retrieval Failure 4 |
| Action | 22 | Misalignment 10, Format Error 6, Parameter Error 4, Invalid Action 2 |
| System | 22 | Step Limit 10, Environment Error 7, Tool Execution Error 4, LLM Limit 1 |

**Guardar este número: `Inefficient Plan` sozinho é 48 de ~199 anotações (24%) — o tipo mais frequente do benchmark inteiro. E `Format Error` é 6 (3%).** Na minha esteira a proporção está exatamente invertida. Volto a isso no mapeamento.

Distribuição por passo (mesma figura): Step 1 (18), 2 (28), 3 (17), 4 (31), 5 (14), 6–10 (48), 11–15 (16), 16–20 (2), 21+ (25).

---

## Erro crítico e propagação

### Definição operacional de erro crítico — e uma contradição interna do paper

O paper dá **duas** operacionalizações incompatíveis:

**(a) §3.2, Stage 2 — via contrafactual** (verbatim):

> "**Stage 2: Critical Error Detection via Counterfactuals.** If the trajectory is already successful, no debugging is required. Otherwise, we perform counterfactual testing step by step: at each point, we substitute a corrected action and test whether the rollout would succeed. The critical error is defined as the earliest step whose correction directly prevents the final failure. Unlike superficial mistakes or errors that are later corrected, the critical error is the root cause that truly determines whether the overall trajectory succeeds or fails—capturing both when and why the agent goes irreversibly off track."

**(b) Algorithm 1 — via LLM, sem contrafactual** (verbatim do comentário do pseudocódigo):

> `/* Stage 2: Critical Error Detection via LLM (no rollout/counterfactuals) */`

e o passo é uma única chamada `DetectCriticalErrors(C)` com `t* ← min(T*)` (o passo crítico mais cedo entre os detectados).

**O código liberado implementa (b).** `detector/critical_error_detection.py` faz **uma** chamada de LLM com a trajetória inteira + a análise por passo + a taxonomia, e parseia um JSON. O docstring do arquivo diz literalmente: *"No scoring, no agent feedback - just critical error identification"*. Além disso, a busca contrafactual real ("substituting a corrected action at each step and stopping once the rollout succeeds") aparece no paper como **baseline** chamado *Brute Force* — e esse baseline tem o **pior** desempenho da tabela (12.0% step accuracy vs. 45.0% do AgentDebug).

**Conclusão a registrar:** a *definição* de erro crítico é contrafactual; a *detecção* é um julgamento de LLM contra essa definição, sem rodar contrafactual nenhum. Ao citar, usar a definição (a) como conceito e deixar claro que a implementação é (b). Isso é bom para mim: **eu também não posso rodar contrafactual numa esteira em produção**, e o paper mostra que o proxy por LLM funciona melhor que a busca por força bruta.

Os critérios que o LLM recebe para decidir (verbatim do prompt, Fig. 15):

> "4. An error is critical if:
>    - It represents the ROOT CAUSE that made task success impossible
>    - It caused a cascade of subsequent errors
>    - The trajectory could have succeeded if THIS specific error had not occurred
>    - IMPORTANT: Correcting this specific error would fundamentally change the trajectory toward success
> 5. Focus on causal chains - trace backwards from the failure to find the origin point"

E duas heurísticas de guarda que valem a pena copiar:

> "3. Early exploration steps (steps 1-3) are often normal and should NOT be marked as critical unless there's a clear, fundamental error"
> "6. IMPORTANT: Step 1 only has planning and action modules - no memory or reflection is possible at step 1 since there's no history yet"

(o código tem retry automático que rejeita a resposta se o LLM marcar memory/reflection no passo 1 — regra estrutural, não estatística).

### O achado "mid-trajectory"

Verbatim, §2.2:

> "It shows most failures cluster in mid-trajectory steps (6–15), where early missteps often cascade downstream. Memory and reflection dominate, with retrieval failures, hallucinations, and progress misjudgments leading to flawed planning. Action and system errors occur less frequently but remain critical, as malformed outputs or step-limit exhaustion can immediately terminate trajectories."

E §5.2:

> "Memory and reflection errors are the most common sources of propagation, typically arising in early or mid-trajectory steps (around steps 5–15). Once an agent misremembers a fact or misjudges its progress, subsequent planning becomes systematically distorted, leading to repeated cycles of flawed action selection. Planning errors also contribute heavily, with constraint ignorance or infeasible strategies compounding as the agent attempts to execute them. By contrast, action-level errors are more visible and sometimes recoverable, though malformed outputs or missing parameters can still derail execution. System-level issues such as tool crashes or step-limit exhaustion act as immediate termination points rather than cascades."

**Ressalva importante:** "steps 6–15" é *absoluto*, num regime de trajetórias com step limit de ~30. Isso **não** é transportável direto para a minha esteira (≈5,8 ActionSteps por execução, 5.781/1.000). Preciso normalizar posição — ver seção de análises.

### Como eles medem propagação — resposta curta: **não medem quantitativamente**

Isto é uma lacuna real do paper e vale registrar com clareza, porque abre espaço para contribuição minha:

- A **Figura 8** é a única evidência de propagação: um heatmap de **10 trajetórias** com célula por passo, sombreada em 3 níveis (1/2/3) de "severidade acumulada", com a célula do primeiro erro crítico contornada. Legenda verbatim: *"Illustration of Error Propagation: Darker shading indicating compounding failures and highlighting how initial mistakes amplify downstream breakdowns."* **É ilustração, não métrica.** Não há definição do que faz uma célula ser 1, 2 ou 3; não há n, não há teste, não há taxa.
- O campo `cascading_effects: [{step, impact}]` do JSON de saída é **texto livre gerado por LLM**, não medição.
- Não existe no paper nenhuma métrica do tipo "P(erro em t+1 | erro em t)", "comprimento médio da cascata" ou "fração da trajetória contaminada". **Busquei; não existe.**

**Isso é aplicável ao meu caso de repetição consecutiva (10× o mesmo erro)?** Conceitualmente sim, e o meu dado é **mais forte** que o deles: a repetição de assinatura idêntica em passos consecutivos é uma cascata *mensurável e verificável*, não uma inferência de LLM. Mas atenção: repetição da **mesma** assinatura é um fenômeno diferente do que eles descrevem. Eles descrevem *distorção* (o erro de memória contamina o planejamento seguinte, que produz erros *diferentes*). Eu tenho *reincidência* (o agente recebe a mensagem de erro na observação e comete o **mesmo** erro). O mais próximo no vocabulário deles é `reflection / outcome_misinterpretation` ("Executes an action but misreads the immediate result or environment feedback") combinado com `planning / inefficient_plan` ("Plan is overly long or illogical; wastes steps"), e o exemplo de `Inefficient Plan` da Fig. 23 é justamente um caso de repetição improdutiva ("This resulted in repeated 'Nothing happens' outcomes in subsequent steps"). **Mas o paper não nomeia nem quantifica reincidência de erro idêntico.** Esse é meu espaço.

---

## O loop falha→aprendizado (3 estágios)

### Stage 1 — Fine-grained Analysis com a AET

Para **cada passo** `t` e **cada módulo** `m ∈ {memory, reflection, planning, action}`, uma chamada de LLM independente (`em_t ← MapToAET(st, at, m, EAET)`). Mais uma checagem separada de `system` por passo (no código, `_check_system_errors`, que dispara heuristicamente em step limit e depois pede confirmação ao LLM).

O **Detector Prompt** (Fig. 14) recebe: `task_description`, `environment`, `step_num`, `context` (a mensagem de usuário completa, incluindo histórico), `module_name`, `module_content` (o texto dentro da tag daquele módulo naquele passo), `env_response` (a resposta do ambiente **após** o passo) e as definições de erro **daquele módulo**.

A regra de encadeamento **dentro do passo** é o que faz a atribuição modular funcionar (verbatim):

> "- Evaluation criteria for each module:
>   * Memory: Should correctly summarize/recall from the current step input only
>   * Reflection: Should correctly reflect based on current input + this step's Memory output
>   * Planning: Should plan reasonably based on current input + this step's Memory & Reflection outputs
>   * Action: Should execute correctly based on current input + this step's Planning output
> - Each module builds on previous modules' outputs FROM THE SAME STEP"

Saída, JSON estrito:
```json
{"error_detected": true/false,
 "error_type": "specific_error_type or no_error",
 "evidence": "Quote or description from module content supporting the detection",
 "reasoning": "Explanation of why this is (or isn't) an error based on the definition"}
```
No código isso vira o dataclass `ModuleError(module_name, error_type, error_detected, evidence, reasoning)`, agregado em `StepAnalysis(step, memory_error, reflection_error, planning_error, action_error, step_summary)`.

**Custo:** ~4–5 chamadas de LLM **por passo**. Para uma trajetória de 30 passos, ~150 chamadas antes de sequer começar o Stage 2. O paper **não reporta** esse custo em absoluto.

### Stage 2 — Critical Error Detection

Uma chamada, com o **AgentDebug Prompt** (Fig. 15), recebendo a análise passo a passo inteira + a referência completa da taxonomia + o contexto da iteração de debug. GPT-4.1, `temperature=0`.

**A forma do feedback** — este é o ponto que importa para a tese. É **JSON estruturado**, não texto solto:

```json
{
  "critical_step": <step_number>,
  "critical_module": "<memory|reflection|planning|action|system|others>",
  "error_type": "<specific_error_type_from_definitions>",
  "root_cause": "Concise description of the fundamental problem",
  "evidence": "Specific quote or observation from trajectory supporting this identification",
  "correction_guidance": "Actionable advice for the agent to avoid the same mistake in that step",
  "cascading_effects": [{"step": <step_number>, "impact": "description"}]
}
```
(o código acrescenta `"confidence": 0.0-1.0`; o dataclass é `CriticalError(critical_step, critical_module, error_type, root_cause, evidence, correction_guidance, cascading_effects, confidence)`).

O que chega ao agente é `correction_guidance` + o tipo de erro, e o prompt descreve isso como (verbatim):

> "providing high-priority, iterative follow-up instructions that MUST be followed across all subsequent steps"

e

> "produce an iterative follow-up instruction that will help avoid similar mistakes in future attempts"

Ou seja: **uma diretiva imperativa em linguagem natural, tipada pela taxonomia, ancorada num passo e num módulo, e acompanhada da citação-evidência que a justifica.** Essa forma é diretamente um candidato a unidade de memória.

### Stage 3 — Iterative Debugging com feedback direcionado

```
τ(0) ← τ
for k ← 1 to I:
    τ(k) ← ReRollout(τ(k−1), t*, φ(k−1))   // re-executa a partir de t*, com feedback
    if Eval(τ(k)) = 1: return τ(k)
    φ(k) ← UpdateFeedback(τ(k), φ(k−1))     // refina a orientação se ainda falhar
return Failure
```

Verbatim, §3.2:

> "Once the critical error is identified, the system generates feedback that specifies the error type and provides actionable guidance for refining subsequent actions and plans. The agent then re-executes (re-rolls out) the trajectory under this feedback. If the rollout still fails, the feedback is refined with more specific guidance, and the process repeats up to a fixed budget of attempts."

E, decisivamente (§4.2, Implementation):

> "We implement AGENTDEBUG with up to N = 5 re-rollouts, each beginning precisely at the identified critical step. This design enables the agent to explore alternative continuations directly from the point of failure rather than restarting from the beginning of the trajectory, thereby concentrating computational effort where it is most impactful."

### O feedback é persistido entre tarefas? **Não. E o paper não trata disso.**

- O feedback `φ` **acumula ao longo das ≤5 tentativas da MESMA tarefa** — o prompt tem os campos `Current debug attempt index: {attempt_index}` e `Previously issued follow-up instructions:`. Esse é o único mecanismo de acúmulo descrito.
- **Não há uma única menção**, no paper inteiro, a persistir feedback entre tarefas distintas, a um banco de memória, a uma biblioteca de lições, ou a reuso cross-episódio. Busquei por `persist`, `across task`, `future task`, `memory bank`, `store`, `reuse`, `library`, `accumulat`, `carry over`, `transfer`: a única ocorrência relevante é em Related Work, citando MemGPT como trabalho de terceiros ("persistent memory mechanisms that maintain context across long horizons (Packer et al., 2023)"). **AgentDebug não faz isso.**
- Ao fim da tarefa o algoritmo retorna `τ*` ou `Failure`. Nada é escrito em lugar nenhum. **O feedback é descartado.**

**Achado adicional, do código, que o paper não menciona:** existe em `agentdebug/memory/file_memory.py` uma classe `FileMemory(SimpleMemory)` com persistência em arquivo `memory.md` — append de linhas `[E:<episode>|S:<step>] <content>`, cache das últimas 100 linhas e um `query(query, limit=3)` por **substring literal** (`if query_lower in line.lower()`). Isso *seria* uma memória cross-episódio rudimentar. **Mas:** (i) o paper não a descreve em nenhum lugar; (ii) `rollout.py` não a importa nem a usa (verifiquei por grep: nenhuma referência a `FileMemory` ou `memory.md` no rollout); (iii) a recuperação é substring, não semântica. **Tratar como código morto/exploratório, não como contribuição do paper.** Não citar como "AgentDebug tem memória persistente" — seria fabricação.

**Achado adicional 2:** o repositório público **não contém o Stage 3**. Há `detector/` (Stages 1 e 2) e `agentdebug/rollout/rollout.py` (coleta de trajetória simples, sem injeção de feedback). Não existe loop de re-rollout, não existe `UpdateFeedback`. As pastas `examples/` e `docs/` anunciadas no README **não existem** no repo. Ou seja: **o resultado de manchete (+26% de sucesso) não é reproduzível a partir do código liberado**, na data desta leitura. Registrar isso na ressalva.

---

## Mapeamento contra o trace da esteira jurídica

Contexto do meu trace: 1.000 execuções (nov/2025–ago/2026), 840 com memória preservada, 5.781 ActionSteps, 142,6M tokens, arquitetura CodeAgent estilo smolagents (única ferramenta = `python_interpreter`; delegação a subagentes dentro do código gerado). 498 steps com erro (8,6% dos steps; 37% das execuções). Taxonomia derivada por **regex sobre a mensagem de exceção**.

### Veredicto geral: o mapeamento frouxo **não se sustenta** — mas não porque esteja errado, e sim porque as duas taxonomias medem coisas diferentes

A AgentErrorTaxonomy classifica **a causa cognitiva**, lida no texto que o agente produziu (`<memory>`, `<reflection>`, `<plan>`). A minha classificação atual classifica **o sintoma**, lido na exceção que o Python levantou. As duas só coincidem quando causa e sintoma são a mesma coisa — que é o caso de `format_error` e pouco mais.

Consequência estrutural, e é a crítica mais importante à análise atual:

> **Erros de memory, reflection e planning não levantam exceção.** Um agente que alucina um campo que *existe*, ou que julga ter concluído a tarefa quando não concluiu, ou que planeja um caminho absurdo mas sintaticamente válido, produz um step **sem `err_type`**. No AgentErrorBench, memory + reflection + planning = **155 de ~199 anotações (78%)**. No meu recorte atual, essas três famílias somam praticamente zero por construção. **Meus 498 steps com erro não são "os erros"; são "os erros que crasharam".** O 8,6% é um piso, não uma taxa.

### Mapeamento família a família

**1. Geração de código — 258 (52%): SyntaxError 223, resposta em markdown puro sem chamar `final_answer` 33, IndentationError 2**

→ **Action / Format Error** — "Produces syntactically invalid actions." Correspondência **direta e limpa**. Num CodeAgent a *ação* literalmente É o bloco de código; um `SyntaxError` é exatamente a falha de parse da ação. O exemplo do paper (`click"product"` em vez de `click["product"]`) é a mesma classe.

- Os 33 casos de "markdown puro sem chamar `final_answer`" também são `format_error` (nenhuma ação parseável foi emitida). *Alternativa a considerar caso a caso:* se o `model_output` declara a intenção de responder e o código não emite a chamada, é **Action / Planning–Action Disconnect (misalignment)** — "Chosen actions do not align with the stated plan intent". Distinguir exige ler o `model_output`; tenho o campo.
- `invalid_action` ("Uses action that does not exist") **não se aplica**: meu espaço de ação é aberto, não há lista de ações admissíveis.

⚠️ **Divergência de frequência que precisa ser dita em voz alta:** `Format Error` é **3%** no AgentErrorBench e **52%** no meu trace. Isso não é uma discordância empírica, é uma diferença de arquitetura: ALFWorld/WebShop têm espaço de ação **fechado** (lista de `admissible_actions` no prompt), então errar formato é quase impossível; um CodeAgent tem espaço de ação **aberto** (Python arbitrário), então errar formato é o modo de falha dominante. **Ao citar o paper, nunca comparar as distribuições como se fossem comensuráveis.** O que é comparável é a *taxonomia*, não os *pesos*.

**2. Suposição sobre dados — 205 (41%): KeyError 98 (campo inventado, `'quebra_sigilo'` 7×), TypeError 60, ValueError 37, objeto sem atributo esperado 8, JSONDecodeError 2**

→ **Não corresponde a um módulo. Corresponde a três, e a separação importa.** Esta é a família onde meu mapeamento frouxo mais falha.

| Sub-caso | Módulo/tipo AET | Justificativa |
|---|---|---|
| `KeyError` em campo **inventado** (`'quebra_sigilo'`, nunca observado no payload) | **Memory / Hallucination (False Memory)** | Definição do código: *"Agent 'recalls' events that never happened, object states never observed... fills in missing parts without solid memory basis, generating false memory information"*. O agente afirma uma chave de schema que nunca viu. Match forte. |
| `KeyError` em campo que **foi observado antes** e o agente não recuperou / grafou errado | **Memory / Retrieval Failure** | *"Relevant info exists but is not retrieved when needed."* |
| `AttributeError` (objeto sem atributo esperado) | **Planning / Impossible Action** | *"Plans a step that is physically/logically impossible given current preconditions."* Chamar método inexistente é impossibilidade lógica dada a precondição. |
| `TypeError` / `ValueError` sobre objeto real | **Action / Parameter Error** | *"Generates unreasonable or malformed parameters."* Mas parte pode ser `impossible_action` — depende de o plano já estar errado ou só a passagem de argumento. |
| `JSONDecodeError` | **System / Tool Execution Error** ou **Reflection / Outcome Misinterpretation** | Se a resposta do subagente veio malformada, é system; se veio bem-formada e o agente assumiu JSON onde havia texto, é reflection. |

**Correção metodológica que decorre disso:** a `err_msg` sozinha **não determina o módulo**. Determina o sintoma. O módulo só sai lendo o `model_output` (o "thought") que gerou a ação — que é exatamente o que o Detector Prompt do Stage 1 faz. **Isso é executável no meu dado**, porque tenho `model_output` e `model_input_messages`.

**3. Ambiente & sandbox — 19 (4%): import não autorizado 11, módulo sem import 6, openpyxl ausente 1, operação proibida 1**

→ **Split, e o split é substantivo.** Meu rótulo atual funde uma violação de restrição *do agente* com um defeito *do ambiente*, e o paper separa:

- "import não autorizado" (11) e "operação proibida" (1) → **Planning / Constraint Ignorance** — *"Ignores limits (time, budget, space, etc.) when forming plans."* A lista de imports autorizados do sandbox **é uma restrição declarada no system prompt**. O agente a ignorou. Isso é planejamento, não ambiente.
- "openpyxl ausente" (1) → **System / Environment Error** ou `tool_execution_error` (dependência faltando no runtime).
- "módulo sem import" (6, `NameError`) → fronteira; provavelmente **Planning / Impossible Action** (planeja usar algo cuja precondição não existe) ou `action/parameter_error`.

**Por que o split importa para a tese:** `constraint_ignorance` é **aprendível** — vira uma unidade de memória procedural direta ("os imports autorizados neste sandbox são X, Y, Z"). `environment_error` **não é aprendível** pelo agente — é ticket de infra. Manter os dois na mesma família apaga essa distinção, que é exatamente a distinção que meu mecanismo de memória precisa fazer.

**4. Suposição sobre estado — 8 (2%): variável de step anterior que falhou, variável fantasma do harness (`Observation`)**

→ **Dois tipos, ambos com match forte:**
- variável fantasma (`Observation`, que o agente supõe existir porque o harness a nomeia) → **Memory / Hallucination** — *"Recalls events or states that never happened"*.
- variável de step anterior **que falhou** → **Reflection / Outcome Misinterpretation** — *"Executes an action but misreads the immediate result or environment feedback."* O agente leu um step que crashou como se tivesse tido sucesso. O exemplo canônico da Fig. 26 (`Progress Misjudge`) é exatamente esse padrão em ALFWorld.

⚠️ **Aqui está a evidência mais clara do viés de medição.** Esta é minha **menor** família (8 steps, 2%) e é a **maior** fonte de propagação do paper (memory + reflection = 77/199 = 39%). A diferença é quase certamente artefato: estados alucinados só entram no meu recorte quando por acaso produzem `NameError`. Quando o agente alucina um valor *plausível* de uma variável que *existe*, não há exceção, e o step passa como sucesso. **Esses 8 são a ponta visível.**

**5. Infra / LLM upstream — 7 (1%)**

→ **System / LLM Limit** (*"Fails due to API/model constraints (e.g., timeouts, token limits)"*) + **System / Environment Error**. Match direto, sem ressalva.

### O que existe na AET e está **completamente ausente** do meu recorte

Nenhum destes levanta exceção; nenhum aparece nos meus 498:

| Tipo AET | n no AgentErrorBench | Por que eu não vejo |
|---|---|---|
| `planning / inefficient_plan` | **48 (o mais frequente)** | Plano prolixo/ilógico executa sem erro |
| `memory / over_simplification` | 22 | Resumo pobre do contexto não crasha |
| `reflection / progress_misjudge` | 20 | "Achei que tinha terminado" não crasha — e no meu caso termina com `final_answer` prematuro |
| `planning / constraint_ignorance` | 14 | Só vejo os 12 que batem no sandbox |
| `reflection / outcome_misinterpretation` | 13 | Só vejo os poucos que viram `NameError` |
| `system / step_limit` | 10 | Preciso checar se minha esteira tem step cap; se tiver, é mensurável direto |

**`progress_misjudge` merece atenção especial no meu domínio.** Num fluxo jurídico, "o agente julgou ter concluído e chamou `final_answer` com resposta incompleta" é um modo de falha **caro e invisível** — sai como `status = sucesso` no meu dataset. Tenho `is_final_answer`; posso investigar.

### E o que a AET **não cobre** no meu caso: multiagente

Os 20 erros (4%) na linha de delegação a subagente e toda a estrutura de papéis (managerAgent → ConversationAgent → WorkflowManager → agentes de domínio) **não têm módulo na AET**. Os 5 módulos são **intra-agente**. O paper reconhece explicitamente que multiagente é escopo de outros trabalhos, citando Cemri et al. 2025 ("Why do multi-agent llm systems fail?") e outros em Related Work. **Para a camada de delegação, este paper não me serve; preciso do MAST/Cemri.** (Já tenho `mast.pdf` no diretório de trabalho.)

---

## O que eu NÃO analisei e deveria

Todas executáveis com os campos que já tenho: `exec_id, agente, status, mês, role, step_number, duração, tokens_in/out/total, err_type, err_msg, is_final_answer` + trace cru com `model_output`, `code_action`, `observations`, `tool_calls`, `model_input_messages`.

### A. Posição na trajetória (o que o paper faz e eu não fiz)

1. **Histograma absoluto, nos mesmos buckets do paper** — `1, 2, 3, 4, 5, 6–10, 11–15, 16–20, 21+` — sobre `step_number` dos 498 steps com erro. Isso torna a Figura 3 diretamente comparável.
2. **Posição normalizada.** Para cada trajetória `(exec_id, role)`: `T = max(step_number)`; para cada step com erro, `p = step_number / T ∈ (0,1]`. Distribuição de `p`, global e estratificada por família de erro.
   - ⚠️ **Cuidado com o viés:** `T` é ele próprio consequência da falha (execuções que falham rodam mais passos). Reportar **as duas** versões — absoluta e normalizada — e nunca só a normalizada.
3. **O que esperar.** Com ~5,8 steps/exec, a massa vai estar em `step_number ≤ 5`, e o bucket "6–15" do paper simplesmente não é onde meu dado vive. **A hipótese testável não é "o erro está no meio", é: `SyntaxError` concentra cedo (o agente ainda está formatando a resposta) enquanto `KeyError`/`TypeError` concentram tarde (o agente já buscou dados e está manipulando).** Se isso se confirmar, é um achado próprio e é *melhor* que replicar o do paper, porque separa erro de forma de erro de conteúdo por posição.

### B. Primeiro erro como proxy do erro crítico

Não posso rodar contrafactual (produção, efeitos colaterais reais). Mas o paper mostra que a busca por força bruta é o **pior** detector, e que `t* ← min(T*)` — o mais cedo — é a regra. Então:

1. Para cada `(exec_id, role)`: `first_err_step = min(step_number | err_type not null)`, `first_err_type`, `first_err_module` (após reclassificação — ver D).
2. **Distribuição de `first_err_type` vs. distribuição de `err_type` em todos os steps.** Se diferirem, alguns tipos são **iniciadores** e outros são **seguidores**. Hipótese: `SyntaxError` é iniciador; a cauda de `TypeError`/`ValueError` é seguidora.
3. **`P(status = falha | first_err_type)`** — qual tipo iniciador mais prediz execução falha. Isso é o análogo *observacional* do "erro crítico" e é defensável sem contrafactual.
4. **Comprimento da cascata:** `n_erros_depois = count(steps com erro | step_number > first_err_step)`, por `first_err_type`. Média e distribuição.
5. **Custo da cascata:** `sum(tokens_total | step_number ≥ first_err_step)` vs. `sum(... < first_err_step)`. Isso decompõe o "~3× mais tokens" que já medi em *quanto do excesso vem da cascata* vs. do erro isolado. Métrica nova e diretamente monetizável.

> **Adendo 09/09/2026 — o item 3 é fraco na esteira, e o motivo importa.** `P(status = falha | first_err_type)` foi proposto como o análogo observacional do *critical error* sem contrafactual. Mas o *critical error* do paper é **definido** por `Eval(τ) = fail`, e o AgentErrorBench é **só de trajetórias de falha**. Na esteira o desfecho quase não varia: `0 de 1.550 trajetórias terminam em erro`, 99,3% entregam resposta de conteúdo — restam ~6 não-entregas em 840. Estimar `P(falha | ·)` sobre ~6 casos positivos repete o problema de n pequeno que retirou o achado de duração (`03-procedimento-validacao.md` §1.6, "Falha do LLM interno", n=6). Somado a isso, nem o lado "sucesso" é rótulo firme (status do banco não confiável — `02-relatorio-achados.md` §4 Passo 1; groundedness não medido). **Consequência:** o análogo do "erro que importa" na esteira não é ancorado em falha de tarefa — é ancorado em **custo** (item 5: qual iniciador começa a cascata cara) e em **reincidência** (assinatura que reaparece entre execuções ao longo de 8–9 meses). Os itens 2, 4 e 5 seguem válidos; só o item 3 fica marcado como fraco por construção do dado.

### C. Propagação — onde eu posso ir **além** do paper

O paper não tem métrica de propagação (só a Figura 8 ilustrativa). Então:

1. **Coeficiente de propagação medido.** Sobre todos os pares de steps consecutivos de todas as `(exec_id, role)`:
   `P(erro em k+1 | erro em k)` vs. `P(erro em k+1 | sem erro em k)`.
   A razão entre os dois é uma **taxa de propagação empírica**. É uma linha de pandas e o paper não tem nada equivalente.
2. **Distribuição de comprimento de run de assinatura idêntica.** Já tenho 48/354 pares com repetição consecutiva e recorde de 10. Formalizar: histograma de comprimento de run, por `role` e por `err_type`. Qual papel reincide mais.
3. **Verificar que a mensagem de erro estava mesmo na observação.** Para cada run de repetição, confirmar em `observations[k]` que a mensagem de erro do step `k` chegou ao agente antes do step `k+1`. Isso transforma "o agente reincide" em **"o agente reincide *tendo lido* a mensagem de erro"** — que é uma afirmação muito mais forte e é *o argumento central para memória externa persistente*: o feedback intra-trajetória, sozinho, demonstravelmente não corrige. **Este é o resultado com maior valor de tese em todo o conjunto.**
4. **Cascata heterogênea** (a propagação *do paper*, não a minha reincidência): dos steps com erro que **não** repetem assinatura, o erro em `k+1` é de família diferente do de `k`? Matriz de transição 5×5 entre famílias em steps consecutivos.

### D. Fechar o buraco memory/reflection/planning — a análise que mais falta

Rodar o **Detector Prompt do Stage 1 (Fig. 14)** sobre o meu trace, com as 18 definições do `error_definitions.py`, para classificar **causa** e não sintoma.

Adaptação necessária (o detector do repo faz regex em `<memory>`/`<reflection>`/`<plan>`/`<action>`, que meu CodeAgent não emite):
- `model_output` (o thought) → tratar como **reflection + planning fundidos**. Aceitar que não consigo separar os dois sem um pre-pass, e **declarar essa limitação**.
- `code_action` → **action**.
- `model_input_messages` → **memory**. Aqui minha posição é na verdade **melhor que a do paper**: eles avaliam se o resumo `<memory>` que o agente escreveu está correto; eu tenho o **contexto literal que o agente recebeu**, então posso avaliar diretamente "a informação estava no contexto e o agente não usou" (`memory_retrieval_failure`) vs. "a informação não estava e o agente inventou" (`hallucination`). Isso é uma verificação factual, não um julgamento — e é caro no paper e barato para mim.
- `observations` → `env_response`.

Amostragem: **não rodar nos 5.781 steps** (custo ≈ 4–5 chamadas/step). Amostra estratificada de ~200 steps, sobre-amostrando (a) steps **anteriores** ao `first_err_step` (é lá que os erros de memory/planning silenciosos devem estar) e (b) steps de execuções com `status = sucesso` (para achar `progress_misjudge`). Validar à mão uma sub-amostra e reportar concordância — o paper reporta κ = 0.55 com 10 anotadores; eu preciso de um protocolo mais leve e honesto sobre isso.

### E. Delegação (fora do escopo deste paper, mas o dado está no mesmo lugar)

Para os 20 erros na linha de delegação: comparar `model_output` (qual subagente o thought diz que vai chamar) com `code_action` (qual `XAgent(task=...)` o código chama). Divergência = `action / misalignment`. Não-divergência com erro = `system / tool_execution_error`. **Avisar que a AET não tem módulo para coordenação multiagente** — para isso, MAST.

---

## O que é adotável para memória PERSISTENTE (e o que não é)

### Adotável

**1. O schema do registro de feedback como schema da unidade de memória.** O JSON do Stage 2 já tem quase tudo que uma unidade de memória precisa: um **tipo** (`error_type`, da taxonomia), um **gatilho/evidência** (`evidence`, citação literal do trace), uma **diretiva** (`correction_guidance`, imperativo acionável), e **proveniência** (`critical_step`, `critical_module`) e **escopo do dano** (`cascading_effects`). Isso é muito mais estruturado que "reflexão em texto livre" à la Reflexion, e é o motivo pelo qual esse paper é o mais próximo da tese.

O que **falta** para persistir, e que eu tenho de acrescentar (o paper não fornece):
- **chave de recuperação** — em qual execução futura esta unidade deve ser trazida? Candidatos que tenho: `role`, `agente`, assinatura de tarefa, assinatura de erro.
- **escopo** — vale para todo o `RespostaBacen` ou só para aquele payload?
- **ciclo de vida** — `hit_count`, `last_seen`, `status ∈ {ativa, aposentada}`, para não acumular lixo. Sem isso, memória persistente vira `memory.md` append-only (que é literalmente o que o código morto do repo faz, com busca por substring — um anti-exemplo útil de citar).

**2. O módulo como roteador do TIPO de memória.** Este é o ganho conceitual maior, e é o que substitui meu mapeamento frouxo por snippet:

| Módulo AET do erro-raiz | Tipo de unidade de memória | Exemplo do meu trace |
|---|---|---|
| **memory** (hallucination, retrieval_failure, over_simplification) | **semântica / factual** — asserção sobre o mundo | "O payload de `RespostaBacen` não tem o campo `quebra_sigilo`; o campo equivalente é `<X>`." (os 7 casos) |
| **planning** (constraint_ignorance, impossible_action, inefficient_plan) | **procedural** — regra sobre como agir | "Neste sandbox os imports autorizados são X, Y, Z; não tente `subprocess`." (os 11+1 casos) |
| **reflection** (progress_misjudge, outcome_misinterpretation, causal_misattribution) | **experiencial-procedural** — regra sobre como interpretar a própria execução | "Se a observação do step anterior contém uma exceção, a variável **não** existe; não a reuse — re-derive." (os 8 casos + os 48 pares de reincidência) |
| **action** (format_error, misalignment, parameter_error) | **procedural de formato** — o mais barato de corrigir e o mais frequente no meu caso | "Sempre encerre chamando `final_answer(...)`; markdown puro não é uma ação." (os 33 casos) |
| **system** | **não é memória do agente** — é ticket de infra | openpyxl ausente, timeout upstream |

Repare que essa correspondência é **fundamentada no módulo que PRODUZIU o erro**, não na string da exceção. É a diferença entre o mapeamento frouxo atual e um defensável.

**3. O princípio do "minimal set / earliest critical error" como POLÍTICA DE ESCRITA da memória.** Este é o item mais transferível do paper inteiro e não tem nada a ver com re-rollout. A anotação do benchmark instrui (verbatim):

> "they were tasked with identifying the minimal set of root-cause failures that explain the downstream error cascade, rather than exhaustively flagging all surface mistakes."

E a ablação confirma (verbatim, §1):

> "Ablation studies further confirm that focusing on root-cause errors, rather than attempting to fix every surface-level mistake, is key to efficient debugging and meaningful performance gains."

**Traduzido para a minha política de escrita: não escrever uma unidade de memória por step com erro. Escrever UMA por cascata, na raiz.** Nos meus dados isso é a diferença entre 498 unidades candidatas e ~354 trajetórias `(exec, role)` → provavelmente ~150–250 raízes, e menos ainda após deduplicação por assinatura. Controle de inchaço de memória de graça, com justificativa empírica emprestada.

**4. O Detector Prompt (Fig. 14) como anotador offline.** Verbatim no paper e implementado no repo. Adaptável ao meu trace (ver análise D). É a ferramenta que produz os *candidatos* a unidade de memória a partir do log cru — que é literalmente a tese do projeto: **o log cru É a working memory; extrair e categorizar sinais de erro dele produz os primeiros candidatos a unidades de memória.** Este paper fornece o extrator e o esquema de categorias; não fornece a persistência.

**5. A regra de encadeamento intra-passo** ("Memory → Reflection → Planning → Action, cada um julgado contra a saída do anterior no MESMO passo"). É o que torna a atribuição de módulo bem-posta em vez de arbitrária. Vale copiar mesmo com módulos fundidos.

### Não adotável

**1. O Stage 3 inteiro — re-rollout.** Ele exige três coisas que uma esteira jurídica em produção não tem:
- **resetar o ambiente para o passo `t*`** — meus efeitos colaterais são reais (ofícios expedidos, cálculos entregues, respostas ao Bacen). Não se re-executa um processo do step 7;
- **`Eval(τ)` — um reward automático e imediato.** Nos três benchmarks existe (ALFWorld: `Reward: 10.0; task completed`; WebShop: score do produto; GAIA: resposta-ouro). Na esteira o desfecho é **esparso, atrasado e julgado por humano**;
- **a mesma tarefa ser re-executável** ≤5 vezes.

**Consequência de projeto:** o Stage 3 tem de ser **substituído**, não adaptado. Onde eles fecham o loop *dentro da tarefa* (`ReRollout`), eu fecho *entre execuções*: escreve na memória agora → lê no início da próxima execução do mesmo `role`/classe de tarefa. E o meu sinal de "melhorou" não pode ser `Eval(τ)`; tem de ser medido **cross-execução** — p.ex. **a assinatura de erro `S` para o papel `R` recorreu depois que a unidade de memória foi escrita?** Isso eu consigo medir com o dado que já tenho (`mês`, `role`, `err_msg`), e é uma métrica de RL não-paramétrico legítima: atualiza conteúdo de memória, mede efeito na taxa de recorrência.

**2. O acúmulo de feedback dentro da tarefa (`φ`, `attempt_index`, "Previously issued follow-up instructions").** É intra-tarefa e descartado ao final. É exatamente a peça que eu tenho de construir e que o paper **não** fornece. Não citar AgentDebug como precedente de memória persistente.

**3. A distribuição de frequências da taxonomia.** Específica de ambiente (planning-dominante lá, format-dominante aqui). Só a taxonomia transfere; os pesos não.

**4. `system / step_limit` como tipo de erro relevante** — depende de a minha esteira ter step cap; verificar antes de usar.

**5. Os 5 módulos como cobertura completa** — não cobrem coordenação multiagente, que é 4% dos meus erros e 100% da minha arquitetura de papéis.

---

## Ganho reportado e custo

**Detecção de erro crítico** (AgentErrorBench, 200 trajetórias, GPT-4.1 `temperature=0`). Métricas: `S` = passo exato do primeiro erro crítico; `S+M` = passo + módulo; `ALL` = passo + módulo + tipo.

| Método | ALFWorld S/S+M/ALL | WebShop | GAIA | Média |
|---|---|---|---|---|
| Direct Prompting | 28.0 / 14.0 / 1.0 | 30.0 / 6.0 / 0.0 | 26.0 / 10.0 / 0.0 | 28.0 / 10.0 / 0.3 |
| Brute Force | 10.0 / 5.0 / 0.0 | 8.0 / 0.0 / 0.0 | 18.0 / 8.0 / 0.0 | 12.0 / 4.3 / 0.0 |
| Binary Search | 20.0 / 6.0 / 1.0 | 14.0 / 8.0 / 0.0 | 22.0 / 10.0 / 0.0 | 18.7 / 8.0 / 0.3 |
| **AgentDebug** | **35.0 / 28.0 / 21.0** | **42.0 / 22.0 / 14.0** | **58.0 / 44.0 / 38.0** | **45.0 / 31.3 / 24.3** |

**Ler com atenção o valor absoluto, não só o delta: 45% de acerto de passo e 24% de acerto estrito.** O framework acerta a raiz em **menos de um quarto** dos casos sob a métrica estrita. É melhor que os baselines por muito, mas não é um detector confiável em termos absolutos. **Ao citar, dar os dois números.**

**Sucesso downstream (ALFWorld, sucesso acumulado em 5 tentativas):** GPT-4o-mini 21 → 55; Qwen3-8B 48 → 74; Qwen3-Next-80B 60 → 84. Ganho relativo maior nos modelos menores.

**"Até 26%"** (§4.2, Fig. 6): melhoria em ALFWorld sobre Self-Refine / Best-of-N. Os números absolutos da Figura 6 **não estão no texto** (só no gráfico), então não consigo verificar a base do percentual. Citar como "reportado, base não verificável no texto".

**A comparação é justa?** Os autores afirmam que sim (verbatim):

> "To ensure fairness, the max number of attempts of all baselines is matched to AGENTDEBUG by total token usage, so any observed gains can be attributed to targeted error recovery rather than higher resource allocation."

**Mas:** não há **nenhuma** tabela de custo — nem tokens absolutos, nem $, nem wall-clock. E o custo do detector (Stage 1 = ~4–5 chamadas de LLM **por passo por tentativa**, mais 1 chamada de Stage 2) não é itemizado em lugar nenhum. Para trajetórias de 30 passos, é ≥150 chamadas por rodada de debug. **O pareamento por tokens é uma afirmação, não uma demonstração.**

**O detector depende criticamente do modelo analista** (Fig. 7b): GPT-4.1 42/32 (Step/ALL) vs. Llama-3.3-70B 16/2, GPT-4o-mini 14/2, Qwen3-Next-80B 4/2. **Ordem de magnitude.** O loop só funciona com um modelo forte na posição de analista — custo real do método, não mencionado como limitação.

**⚠️ Inconsistência interna a registrar.** O box "Findings" (§4.2) diz:

> "Its ability to precisely localize root-cause failures (50.0% step accuracy and 42.5% all-correct accuracy)..."

Mas a Tabela 1 reporta **45.0% / 24.3%** e a Figura 7b reporta **42% / 32%**. Os três números não batem. **Citar sempre a Tabela 1** (45.0 / 24.3), que é a fonte primária, e não o box.

---

## AgentErrorBench: anotação e reusabilidade

**Construção** (§2.2, verbatim nos pontos-chave):

- 200 trajetórias curadas: **100 ALFWorld, 50 WebShop, 50 GAIA**, extraídas de "over 500 failed trajectories" coletadas. **São trajetórias de FALHA apenas** — o benchmark não contém trajetórias bem-sucedidas.
- **"Ten expert annotators—graduate students with prior experience in NLP and LLMs agent research—labeled each trajectory using the AgentErrorTaxonomy schema."**
- **"Annotation proceeded at the decision-step level: every action, reflection, or plan was reviewed, and annotators tagged its error type(s) according to the taxonomy."** (note: **tipos no plural** — um passo pode receber mais de um rótulo)
- **"In addition, they were tasked with identifying the minimal set of root-cause failures that explain the downstream error cascade, rather than exhaustively flagging all surface mistakes. This root-cause focus was emphasized through detailed guidelines and calibration examples, refined iteratively over three rounds of pilot annotation."**
- Controle de qualidade: fase de treinamento com feedback dos autores → dupla anotação independente num subconjunto compartilhado → adjudicação coletiva das discordâncias, que gerou esclarecimentos nas definições ("e.g., distinguishing 'retrieval failure' under memory vs. 'constraint ignorance' under planning").
- **"Inter-annotator agreement, measured using Cohen's κ, reached κ = 0.55 across modules, indicating substantial agreement."**

⚠️ **κ = 0.55 não é "substantial".** Na escala de Landis & Koch, 0.41–0.60 é **moderate**; substantial é 0.61–0.80. **É um overclaim dos autores.** Ao citar, dar o valor e a leitura correta. Implicação prática para mim: mesmo com 10 anotadores treinados, guia detalhado e 3 rodadas de piloto, a taxonomia só chega a concordância moderada. **Não devo prometer que classifico meu trace com alta confiabilidade** — e devo reportar concordância própria, mesmo que informal.

**O guia/schema é reusável?**

- **O schema: sim.** Tabela 2 do paper + `detector/error_definitions.py` do repo, que é **mais rico** — traz `definition` **e** `example` concreto para cada um dos 18 tipos. Recomendo usar a versão do código, não a da tabela.
- **O guia de anotação em si: NÃO está publicado.** O paper menciona "detailed guidelines and calibration examples" mas não os inclui; não estão no repositório. Os únicos exemplos calibradores públicos são os **7 casos do Apêndice A.6** (Figs. 20–26: Over Simplification, Impossible Action, Constraint Ignorance, Inefficient Plan, Misalignment, Format Error, Progress Misjudge), com trajetória, evidência e passo crítico — úteis como few-shot.
- **Prompt de anotação publicado que posso adaptar: SIM, dois, verbatim e implementados.**
  - **Figura 14 — Detector Prompt** (`detector/fine_grained_analysis.py`): classificador por passo × módulo, saída JSON `{error_detected, error_type, evidence, reasoning}`. **É este que eu adapto para classificar meu trace automaticamente.**
  - **Figura 15 — AgentDebug Prompt** (`detector/critical_error_detection.py`): identificador de erro crítico, saída JSON com `root_cause` / `correction_guidance` / `cascading_effects`.
- **Dataset:** link Google Drive no README do repo.
- **Adaptação obrigatória para o meu caso:** o extrator de módulos é regex em `<memory>`, `<reflection>`, `<plan>`, `<action>` — tags que meu CodeAgent não emite. Mapeamento proposto na análise **D** acima.

---

## Ressalvas ao citar

1. **Preprint, não publicado.** arXiv 2509.25370v1, 29 Sep 2025. Sem venue. Não citar como conferência.
2. **Domínios são benchmarks sintéticos.** ALFWorld = simulador embodied de texto com **lista fechada de ações admissíveis**; WebShop = e-commerce simulado; GAIA = QA com ferramentas e resposta-ouro. Nenhum é produção, nenhum tem consequência real, nenhum tem stakeholder humano. O próprio paper admite (A.1): *"it remains limited in scale and domain diversity; extending to multimodal environments, longer-horizon tasks, or safety-critical applications (e.g., healthcare, finance) is an important direction for future work."* — **domínio jurídico/financeiro em produção é declarado pelos próprios autores como fora do escopo.**
3. **Reward automático e imediato.** `Eval(τ) = 1` existe nos três ambientes. Não existe na esteira. Todo o Stage 3 repousa nisso.
4. **Espaço de ação fechado vs. aberto.** É a diferença estrutural que explica por que `format_error` é 3% lá e 52% aqui. **Nunca comparar distribuições.**
5. **Horizonte.** Deles: até 30 passos, com `step_limit` como tipo de erro. Meu: ~5,8 ActionSteps/execução. "Mid-trajectory (6–15)" não transfere sem normalização.
6. **Single-agent.** AgentErrorBench é single-agent; os 5 módulos são intra-agente. **Não há módulo para coordenação/delegação.** Para os meus 20 erros de delegação e a arquitetura de papéis, usar MAST/Cemri et al. 2025.
7. **Arquitetura modular imposta por prompt.** O método pressupõe que o agente emita `<memory>/<reflection>/<plan>/<action>` separadamente. A minha esteira não emite. Qualquer replicação minha funde reflection+planning em `model_output` — **declarar essa limitação**.
8. **n = 200 trajetórias, todas de falha, κ = 0.55 (moderate, não substantial), guia de anotação não publicado.**
9. **Números internos inconsistentes:** box "Findings" (50.0/42.5) ≠ Tabela 1 (45.0/24.3) ≠ Fig. 7b (42/32). Usar a Tabela 1.
10. **Taxonomia: 17 na tabela, 18 no código (`invalid_action` some da tabela), + bucket `others`.**
11. **Custo não reportado.** Pareamento de tokens com baselines é afirmado, não demonstrado; nenhuma tabela de custo. Stage 1 custa ~4–5 chamadas de LLM por passo.
12. **Desempenho absoluto modesto:** 24.3% all-correct. Melhor que baseline por muito; longe de confiável.
13. **Dependência forte do modelo analista** (GPT-4.1 32% ALL vs. Qwen3-Next-80B 2%).
14. **Reprodutibilidade:** o repositório público contém apenas os Stages 1 e 2 (`detector/`) e um rollout simples. **Não há código de re-rollout iterativo (Stage 3)**; as pastas `examples/` e `docs/` anunciadas no README não existem. O resultado de +26% não é reproduzível a partir do código liberado (verificado em 2026-09-08).
15. **`FileMemory` / `memory.md` existe no código mas não no paper e não está ligado ao rollout.** Não usar como evidência de que AgentDebug persiste memória.
16. **Contradição do Stage 2:** "via Counterfactuals" (§3.2) vs. "via LLM (no rollout/counterfactuals)" (Algorithm 1). O código implementa a segunda.

---

## Trechos literais de apoio

**Insight central (§2.1, box):**
> "Error propagation is the primary bottleneck in LLM agent reliability. Early mistakes rarely remain confined; instead, they cascade into subsequent steps, distorting reasoning, compounding misjudgments, and ultimately derailing the entire trajectory."

**A intuição do método (§3.2):**
> "The central intuition is that correcting a single root-cause mistake can often flip an otherwise failing trajectory into a successful one."

**Definição de erro crítico (§3.2):**
> "The critical error is defined as the earliest step whose correction directly prevents the final failure. Unlike superficial mistakes or errors that are later corrected, the critical error is the root cause that truly determines whether the overall trajectory succeeds or fails—capturing both when and why the agent goes irreversibly off track."

**Forma e propósito do feedback (§3.2):**
> "Once the critical error is identified, the system generates feedback that specifies the error type and provides actionable guidance for refining subsequent actions and plans. The agent then re-executes (re-rolls out) the trajectory under this feedback. If the rollout still fails, the feedback is refined with more specific guidance, and the process repeats up to a fixed budget of attempts. Grounded in the AgentErrorTaxonomy taxonomy, the feedback is both targeted and forward-looking—resolving the root cause while shaping how the agent approaches future steps."

**O re-rollout parte do passo crítico, não do zero (§4.2):**
> "We implement AGENTDEBUG with up to N = 5 re-rollouts, each beginning precisely at the identified critical step. This design enables the agent to explore alternative continuations directly from the point of failure rather than restarting from the beginning of the trajectory, thereby concentrating computational effort where it is most impactful."

**Acúmulo de feedback é intra-tarefa (prompt, Fig. 15):**
> "DEBUG ITERATION CONTEXT: - Current debug attempt index: {attempt_index} - Previously issued follow-up instructions:"
> "...providing high-priority, iterative follow-up instructions that MUST be followed across all subsequent steps."
> "...produce an iterative follow-up instruction that will help avoid similar mistakes in future attempts."

**Política de "conjunto mínimo" na anotação (§2.2):**
> "they were tasked with identifying the minimal set of root-cause failures that explain the downstream error cascade, rather than exhaustively flagging all surface mistakes."

**A ablação que sustenta essa política (§1):**
> "Ablation studies further confirm that focusing on root-cause errors, rather than attempting to fix every surface-level mistake, is key to efficient debugging and meaningful performance gains."

**Concentração mid-trajectory (§2.2):**
> "It shows most failures cluster in mid-trajectory steps (6–15), where early missteps often cascade downstream. Memory and reflection dominate, with retrieval failures, hallucinations, and progress misjudgments leading to flawed planning."

**Memory e reflection como fontes de propagação; system como terminação (§5.2):**
> "Memory and reflection errors are the most common sources of propagation, typically arising in early or mid-trajectory steps (around steps 5–15). Once an agent misremembers a fact or misjudges its progress, subsequent planning becomes systematically distorted, leading to repeated cycles of flawed action selection. [...] System-level issues such as tool crashes or step-limit exhaustion act as immediate termination points rather than cascades."

**A recomendação de projeto que endossa a minha tese (§5.2) — o trecho mais citável do paper para o projeto:**
> "These findings highlight two important takeaways for designing more reliable agents. First, early detection and correction are critical, since once cascades begin, they are difficult to reverse. Second, mechanisms that strengthen memory retrieval and reflection—such as external memory, progress tracking, or verification prompts—can substantially reduce the risk of propagation."

**Encadeamento intra-passo entre módulos (Detector Prompt, Fig. 14):**
> "* Memory: Should correctly summarize/recall from the current step input only
> * Reflection: Should correctly reflect based on current input + this step's Memory output
> * Planning: Should plan reasonably based on current input + this step's Memory & Reflection outputs
> * Action: Should execute correctly based on current input + this step's Planning output
> - Each module builds on previous modules' outputs FROM THE SAME STEP"

**Critérios de criticidade (AgentDebug Prompt, Fig. 15):**
> "An error is critical if: - It represents the ROOT CAUSE that made task success impossible - It caused a cascade of subsequent errors - The trajectory could have succeeded if THIS specific error had not occurred - IMPORTANT: Correcting this specific error would fundamentally change the trajectory toward success"

**Pareamento de custo com baselines (§4.2):**
> "To ensure fairness, the max number of attempts of all baselines is matched to AGENTDEBUG by total token usage, so any observed gains can be attributed to targeted error recovery rather than higher resource allocation."

**Concordância entre anotadores (§2.2):**
> "Inter-annotator agreement, measured using Cohen's κ, reached κ = 0.55 across modules, indicating substantial agreement."

**Limitações declaradas pelos autores (A.1):**
> "First, while AgentErrorBench covers three representative benchmarks (ALFWorld, GAIA, and WebShop), it remains limited in scale and domain diversity; extending to multimodal environments, longer-horizon tasks, or safety-critical applications (e.g., healthcare, finance) is an important direction for future work. Second, collecting sufficient data to train a dedicated debugging model would be prohibitively expensive in low-resource academic settings, given the costs of large-scale human annotation. To mitigate this, we instead designed a cost-efficient workflow that leverages prompt engineering with existing LLMs, though this approach may still fall short of the performance achievable with a fully trained, specialized model."

**Definições estendidas do código (`detector/error_definitions.py`) mais úteis que as da Tabela 2 — os três que mais me servem:**
> `memory/hallucination`: "Agent 'recalls' events that never happened, object states never observed, or actions never executed, and uses these as basis for reasoning. Agent fills in missing parts without solid memory basis, generating false memory information"
> `planning/constraint_ignorance`: "Planning ignores task constraints, not considering resource limits (time, budget, space) or other relevant restrictions"
> `reflection/outcome_misinterpretation`: "Agent correctly executes an action but incorrectly interprets the direct result or environment feedback from that action"
