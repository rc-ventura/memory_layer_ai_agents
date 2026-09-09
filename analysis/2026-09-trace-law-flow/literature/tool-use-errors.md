# Taxonomias de erro de tool-use — ToolFailBench (+ ToolScan)

**Papers:**

| Sigla | Referência confirmada no PDF | Status |
|---|---|---|
| **ToolFailBench** | Harsh Soni (UC Berkeley, autor único). *ToolFailBench: Diagnosing Tool-Use Failures in LLM Agents.* arXiv:2607.04686v1 [cs.CL], 6 Jul 2026. Carimbo de rodapé: "Published at ICML 2026 Workshops, 43rd ICML, Seoul, South Korea, 2026". Código anunciado: `github.com/SoHarshh/ToolFailBench` (URL responde HTTP 200). | ✅ **Confirmado** — autoria, ID, data e venue lidos do próprio PDF. Ressalva: é *workshop* do ICML, não main track, e autor único. |
| **ToolScan** | Shirley Kokane, Ming Zhu, Tulika Awalgaonkar, Jianguo Zhang, Akshara Prabhakar, Thai Hoang, Zuxin Liu, Rithesh Murthy, Liangwei Yang, Weiran Yao, Juntao Tan, Zhiwei Liu, Juan Carlos Niebles, Huan Wang, Shelby Heinecke, Caiming Xiong, Silvio Savarese — **Salesforce AI Research**. *ToolScan: A Benchmark for Characterizing Errors in Tool-Use LLMs.* arXiv:2411.13547v2 [cs.SE], 26 Jun 2025. Cabeçalho: "Published at Building Trust Workshop at ICLR 2025". | ✅ **Confirmado** — existe, é real, e os sete tipos batem. **Atenção ao nome:** a v1 do mesmo arXiv ID se chamava **SpecTool**; o próprio ToolFailBench cita esse trabalho como "SpecTool (Kokane et al., 2024)". Ver seção de verificação. |
| *(terciário)* Beyond the Leaderboard | Wael Albayaydh, Rui Zhao, Ivan Flechais (University of Oxford). *Beyond the Leaderboard: A Synthesis of Tool-Use, Planning, and Reasoning Failures in Large Language Model Agents.* arXiv:2607.05775. Pré-print, sem venue. | ✅ Confirmado, usado **só** como corroboração independente da leitura do ToolScan. Não citar para números. |

**Lido:** texto completo por subagente (🔎), 2026-09-08. PDFs baixados via `curl` + `pdftotext` (WebFetch em arxiv.org está bloqueado neste ambiente). Apêndices integrais lidos nos dois papers principais.

---

## ToolFailBench — o que é e a taxonomia

### O que é

Benchmark **diagnóstico** de 1.000 tarefas *single-turn* em cinco domínios profissionais (finanças, medicina, **direito**, cibersegurança, imobiliário), 200 tarefas por domínio: **750 tool-required + 250 control**. Nove ferramentas por domínio.

O mecanismo central são as **"armadilhas paramétricas" (parametric traps)**: o retorno *mock* da ferramenta é deliberadamente ajustado para **contradizer** um valor plausivelmente memorizado no pré-treino. Se o modelo chama a ferramenta e responde com o valor da memória paramétrica em vez do valor retornado, isso é capturado como falha. As *control tasks* fazem o teste inverso: perguntas conceituais, respondíveis direto, para medir se o modelo chama ferramenta desnecessariamente.

Protocolo de inferência em **dois passos**: primeiro o modelo recebe a query com `tool_choice=auto`; se emitir chamada válida, o harness executa o mock e injeta o retorno; depois o modelo escreve a resposta final com `tool_choice=none`. Isso separa a decisão-de-chamar da escrita-da-resposta. `temperature=0`, `max_tokens=1024`, `seed=42` onde suportado.

### A taxonomia (verbatim)

Do §3.2 do paper:

> "For tool-required tasks, a response is **Correct** if the model calls the expected tool and uses the returned data in its final answer. We define three failure modes: **Tool-Skip (TS)**, where the model does not produce a valid executed tool call; **Result-Ignore (RI)**, where the model calls the tool but does not use the returned data; and **Output-Fabrication (OF)**, where the model calls the tool but adds invented structured information not present in the return."
>
> "For control tasks, where no tool is needed, a response is **Correct** if the model answers directly without calling a tool. We label **Unnecessary-Tool-Use (UTU)** when the model calls a tool anyway, and **Wrong-Answer** when the model avoids tool use but answers incorrectly."

Definições operacionais mais detalhadas, do **rubric de juiz** (Apêndice E.5.1) — estas são as que valem para implementar:

> **`tool_skip`** : Model did NOT make a valid, executed tool call. This includes: (a) no tool call at all, (b) a tool call written in plain text inside the answer body (e.g. `"<tool_call>...</tool_call>"`) that was never actually executed by the system, (c) the model refused to answer.
>
> **`result_ignore`** : Model called the correct tool, received the return value, but the final answer does NOT faithfully reflect it. Signs: answer contains memorized/training-data values instead of the tool's values, answer is empty or generic despite having received specific data, answer contradicts the tool return.
>
> **`output_fabrication`** : Model called the correct tool but the answer contains invented structured data (fake JSON, hallucinated table rows, fabricated numbers, named entities not in the tool return) that does not come from the tool's actual return. **Distinguished from result_ignore by the presence of plausible-looking but invented structured output.**
>
> **`unnecessary_tool_use`** : Model called a tool when none was needed.
>
> **`wrong_answer`** : Model correctly refrained from calling a tool, but the factual answer is incorrect.

**Confirmação da pergunta 1:** sim, Tool-Skip / Result-Ignore / Output-Fabrication estão confirmados, e o snippet de busca estava **incompleto** — falta **Unnecessary-Tool-Use** (e, no lado das control tasks, **Wrong-Answer**). São **quatro** modos de falha, não três.

### Métricas

| Métrica | Nome | Conjunto |
|---|---|---|
| TSR | Tool-Skip Rate | Required (750) |
| CTUR | Clean Tool-Use Rate | Required |
| RIR | Result-Ignore Rate | Required |
| OFR | Output-Fabrication Rate | Required |
| UTR | Unnecessary-Tool-Use Rate | Control (250) |
| CTRL-Acc | Control Accuracy | Control |

Propriedade útil: **TSR + CTUR + RIR + OFR = 100%** no conjunto Required — "leaderboard rows are verifiable by addition".

### Resultados (19 modelos headline, rótulo por ensemble)

| Modelo | CTUR | TSR | RIR | OFR | UTR | CTRL-Acc |
|---|---|---|---|---|---|---|
| Grok-4.3 (melhor) | 86.33 | 11.80 | 1.74 | 0.13 | 0.81 | 97.18 |
| Claude-Sonnet-4.5 | 79.28 | 15.64 | 4.41 | 0.67 | 0.00 | 100.00 |
| GPT-5.4-Mini | 79.14 | 14.17 | 5.48 | 1.20 | 0.00 | 97.20 |
| Qwen2.5-72B-Instruct | 79.00 | 18.57 | 2.02 | 0.40 | 0.00 | 98.00 |
| Llama-3.1-70B | 62.58 | 24.23 | 11.17 | 2.02 | **77.73** | **8.91** |
| Llama-3.1-8B (pior) | 47.32 | 20.64 | **30.43** | 1.61 | **98.39** | **0.00** |

Achados que interessam ao seu argumento:

1. **Não está saturado.** O melhor modelo de 2026 ainda falha em 13,67% das tarefas onde a ferramenta é obrigatória.
2. **Scores agregados escondem perfis de falha distintos.** Llama-3.1-70B e Qwen2.5-72B, mesma escala, diferem **89 pontos percentuais** em CTRL-Acc (z = −19,9; p < 10⁻⁸⁰). Os Llama-3.1 formam um padrão **"Always-Call"**: chamam ferramenta em 77–98% das perguntas conceituais.
3. **Efeito de domínio na fidelidade pós-chamada.** RIR mediana (regra, 17 modelos disciplinados): **Finanças 12,24%** vs. **Cibersegurança 0,68%**. Os autores atribuem à competição de *priors* memorizados fortes (preços, P/E). Direito fica no meio. Concordância inter-anotador por domínio: Finance κ=0,51, **Legal κ=0,64**, Medical 0,67, Cyber 0,71, Real estate 0,78.

---

## ToolScan — status da verificação

### Veredicto: **A CITAÇÃO É VERIFICÁVEL. Pode manter no relatório.**

- **Existe.** arXiv **2411.13547**, versão v2 [cs.SE] de 26 Jun 2025.
- **Autores reais:** Shirley Kokane *et al.*, **Salesforce AI Research** (17 autores; inclui Caiming Xiong e Silvio Savarese).
- **Venue real:** *Building Trust Workshop* at **ICLR 2025**. É workshop, não main track — cite assim.
- **Os sete tipos batem** com o que você tinha do snippet, com **um ajuste**: o sétimo não é "hallucinated function names" separado — os sete são IAC, IAV, IAN, IAT, RAC, IFN e **IFE (Invalid Format Error)**, que o snippet não trouxe.

### ⚠️ Duas armadilhas de citação que você precisa saber

**1. O paper mudou de nome entre versões.** A v1 do arXiv 2411.13547 se chamava **SpecTool: A benchmark for characterizing errors in tool-use LLMs**. O próprio ToolFailBench cita a referência assim, na lista de referências:

> "Kokane, S., Zhu, M., Awalgaonkar, T., […] Savarese, S. **SpecTool: A benchmark for characterizing errors in tool-use LLMs.** arXiv preprint arXiv:2411.13547, 2024."

Ou seja: se alguém buscar "SpecTool" e você escreveu "ToolScan", ou vice-versa, é o mesmo trabalho. Recomendo citar como: *Kokane et al. (2024/2025), ToolScan (v2; publicado originalmente como SpecTool), arXiv:2411.13547, Building Trust Workshop @ ICLR 2025*.

**2. O resumo automático de busca web INVENTOU uma taxonomia.** Ao buscar "ToolScan", o sumarizador de resultados de busca devolveu como sendo os sete tipos: *"Tool Hallucination, Argument Hallucination, Invalid Tool Invocation, Partial Tool Execution, Tool Output Hallucination, Invalid Intermediate Reasoning, Re-entrant Error Handling Failures"*. **Nenhum desses sete nomes aparece no paper.** É confabulação do sumarizador. Se essa lista tiver vazado para alguma nota sua, apague. A lista correta está abaixo, transcrita do PDF.

### Os sete padrões de erro (verbatim, §3)

> "we characterize systematic errors generated by LLMs on tool-use tasks into seven critical error types.
>
> • **Insufficient API Calls (IAC)**: Unable to generate sufficient API calls, hence unable to completely fulfill the tasks provided in a query.
> • **Incorrect Argument Value (IAV)**: Generates incorrect argument values. This also includes exclusion of required arguments.
> • **Incorrect Argument Name (IAN)**: Hallucinates argument names.
> • **Incorrect Argument Type (IAT)**: Generates incorrect argument type.
> • **Repeated API Calls (RAC)**: Generates the exact same API Call repeatedly, causing redundant calls.
> • **Incorrect Function Name (IFN)**: Hallucinates function names, not part of the API list.
> • **Invalid Format Error (IFE)**: Generates inappropriate format."

Exemplos concretos dados pelo paper (Tabela 2), que deixam a semântica sem ambiguidade:

| Erro | Ground Truth | Saída do modelo |
|---|---|---|
| **IAV** (GPT-3.5) | `getJokeCategory(category='food', sortby='asc')` | `getJokeCategory(category='workplace', sortby='asc')` |
| **IAC** (GPT-4) | `getMovie(title='Endgame', type='movie')`, `getMovieProvider(region='US')` | `getMovie(title='Endgame', type='movie')` ← só a primeira |
| **IAN** (MLlama) | `getMovieAdv(genre=…, startyear=1970, endyear=2020, minimdb=7)` | `getMovieAdv(genre=…, releasestart=1970, releaseend=2020, imdbrating=7)` |
| **IAT** (xLAM) | `checkDomainAvailability(domain='business.com', availableonly=True)` | `checkDomainAvailability(domain='business.com', availableonly="True")` ← bool virou string |

### Resultados (Tabela 4 — **maior é melhor**: é o % de chamadas SEM o erro)

| Modelo | Success | IAC | RAC | IAV | IFE | IAT | IAN | IFN |
|---|---|---|---|---|---|---|---|---|
| GPT-4-0125-preview | 0.73 | 0.84 | 1.00 | 0.94 | 1.00 | 0.93 | 0.94 | 0.94 |
| xLAM-8x7B | 0.72 | 0.79 | 0.95 | 0.92 | 1.00 | 0.95 | 0.93 | 0.91 |
| GPT-3.5-turbo-1106 | 0.67 | 0.70 | 0.94 | 0.86 | 0.95 | 0.94 | 0.93 | 0.91 |
| Meta-Llama3-8b | 0.27 | 0.58 | 0.40 | 0.42 | 0.71 | 0.49 | 0.42 | 0.64 |
| Mixtral-8x7B-Instruct | 0.10 | 0.11 | 0.12 | 0.11 | 0.10 | 0.15 | 0.12 | 0.20 |

Observações do texto que importam:

- **"We observe that Insufficient API Calls (IAC) is the most common error pattern."** Duas causas dadas: (1) modelos tipo GPT resolvem só parte da query — "If there are multiple questions asked in the same query, GPT ends after answering the first query"; (2) modelos não distinguem APIs parecidas e ignoram restrições.
- **RAC → IAC.** Modelos menores "get stuck in a loop based on their internal belief of solving the query and call the same API multiple times even if they are failing. We also see a co-relation between RAC and IAC."
- **Modelos de código vão bem.** Code-Llama-13B supera vários modelos genéricos maiores; hipótese dos autores: "there may be some inherent similarity between coding-associated tasks and function calls". **Isso é um argumento a favor do paradigma CodeAgent que você usa.**
- **Ablação de formato (§8.1.3):** formato estruturado (JSON/YAML) *piora* IFE, hipótese = inflação de tokens.
- **Ablação de irrelevância (§8.1.1):** ruído irrelevante na query aumenta IFN — o modelo **alucina APIs fictícias** quando confrontado com pedidos fora do escopo das ferramentas.

### 🔑 O achado do ToolScan mais relevante para a sua tese

O framework do ToolScan tem um **mecanismo de feedback** (§5) que intercepta a ação **antes de executar** e devolve ao modelo a informação faltante:

> "- Incorrect Format, please follow the format {}
> - Invalid Action generated, valid actions are {"x", "y", "z"}
> - Invalid Argument for action "a", valid arguments are {'b', 'c'}
> - Invalid Argument type for action "k", its valid type is "bool""

E a ablação §8.1.2 mede o efeito: **"model success rate is higher when model is provided with feedback which helps it to correct itself"**; sem feedback, "the model frequently repeats errors, such as incorrect function names, leading to a significant reduction in its task completion effectiveness. Without guidance, the model struggled to recover from initial mistakes."

Isto é, literalmente, **atualização de memória não-paramétrica**: injetar no contexto o inventário correto de ferramentas/argumentos, derivado do erro observado, e medir ganho de sucesso — sem tocar em pesos. É o antecedente mais próximo do seu mecanismo na literatura de tool-use, e vale citar exatamente nesse enquadramento. Note que o conteúdo injetado é *semântico* (o inventário: nomes válidos, argumentos válidos, tipos válidos) — corresponde à sua unidade de memória semântica. O ToolScan **não** faz o análogo procedural (não injeta "quando X falhar, faça Y"); esse espaço está aberto.

---

## Tradução para o paradigma CodeAgent

### O problema de fundo (leia antes da tabela)

As duas taxonomias assumem uma fronteira que **o seu sistema não tem**: um *schema* de função validado antes da execução. No ToolScan isso é explícito — IFN, IAN, IAT e IFE são **interceptados pelo mecanismo de feedback antes de a ação ser executada**; só depois disso "the action is executed within the corresponding environment".

No CodeAgent estilo smolagents existe **uma** ferramenta registrada, `python_interpreter`. Não há schema no ponto de chamada. Consequência estrutural, em três partes:

1. **As categorias de *entrada* do ToolScan (IAN/IAT/IAV) não somem — mudam de sintoma.** Em vez de falharem na validação, elas ou (a) explodem *dentro* da função com uma exceção Python genérica (`TypeError: got an unexpected keyword argument`), ou (b) passam silenciosamente e corrompem o resultado. Não existe camada que as rotule como erro de argumento. Elas estão **escondidas dentro do seu balde `TypeError = 60`**, misturadas com erros de dados.
2. **Surge uma região de erro que nenhuma das duas taxonomias cobre:** *pós-chamada, pré-resposta, dentro do código*. O ToolScan é todo **pré-execução**; o ToolFailBench é todo sobre a **resposta final**. Mas o CodeAgent tem que **manipular** o retorno em Python — indexar, iterar, acessar atributo. É aí que moram seus `KeyError` 98 e `Object hashDocumento has no attribute get` 8. **Essa lacuna é a sua contribuição, não um defeito da sua análise.** O mais próximo na literatura é a categoria *"output-interpretation errors"* de uma taxonomia de REST-API tools (arXiv:2504.15546) citada pelo *Beyond the Leaderboard* — mas não é o ToolScan.
3. **Portanto a afirmação atual do seu relatório precisa ser corrigida.** Ver o veredicto abaixo.

### ⚠️ Veredicto sobre a afirmação "Suposição sobre dados ≡ erros de argumento do ToolScan"

**Não se sustenta como está escrita. Sustenta-se parcialmente, e a parte que sustenta é uma fatia que você ainda não separou.**

| Seu erro | Nº | Mapeamento honesto |
|---|---|---|
| `KeyError` (campo inventado, ex. `'quebra_sigilo'` 7×) | 98 | **NÃO é erro de argumento.** É suposição sobre o *schema de retorno* da ferramenta. Fora do ToolScan; próximo de "output-interpretation errors" (arXiv:2504.15546) e do espírito pós-chamada do ToolFailBench, mas nenhuma categoria existente encaixa. |
| Objeto sem atributo esperado (lista de strings tratada como lista de dicts) | 8 | Idem — suposição sobre estrutura do retorno. |
| `TypeError` | 60 | **Mistura.** A sub-fatia com mensagem `unexpected keyword argument` **é literalmente IAN**. A sub-fatia `missing N required positional argument` **é literalmente IAV** ("This also includes exclusion of required arguments"). A sub-fatia `not subscriptable` / `unsupported operand` é suposição de dados. **Você precisa quebrar esse balde por padrão de mensagem — é o teste direto da sua afirmação.** |
| `ValueError` 37, `JSONDecodeError` 2 | 39 | Parsing do retorno → suposição sobre formato do retorno, não sobre argumento. |

**Reescrita sugerida da frase do relatório:**

> "A família *Suposição sobre dados* não é o equivalente CodeAgent dos erros de argumento do ToolScan. É majoritariamente uma classe **ausente** das taxonomias baseadas em tool-call estruturado: suposições sobre o **schema do retorno** da ferramenta, que só se manifestam porque no paradigma CodeAgent o modelo precisa *manipular* o retorno em código, e não apenas lê-lo. Os análogos diretos de IAN/IAV do ToolScan existem no trace, mas confinados a uma sub-fatia do balde `TypeError`, que separo em [seção X]. A migração do erro do ponto-de-chamada para o ponto-de-manipulação é, em si, um resultado do paradigma."

E o simétrico, que é ainda mais forte a seu favor:

> "Minha maior família — *Geração de código*, 258 (52%) — mapeia inteira sobre **um único** tipo do ToolScan: **IFE (Invalid Format Error)**. No paradigma de tool-call estruturado, IFE está praticamente resolvido (GPT-4 e xLAM-8x7B marcam **1.00**, isto é, 0% de erro de formato), porque decodificação restrita garante JSON válido. No paradigma CodeAgent ele **ressurge como a categoria dominante**, porque a superfície de saída deixa de ser um objeto com schema e passa a ser uma linguagem de programação inteira. Esse é um custo do paradigma que a literatura de benchmark, ancorada em function-calling estruturado, não mede."

### Tabela: modo de falha → análogo em CodeAgent → detector executável

Legenda de custo: **D** = determinístico (só AST/regex, sem rótulo humano nem LLM); **D+** = determinístico mas precisa das assinaturas reais das ferramentas; **J** = precisa de juiz LLM ou anotação manual.

| Modo (fonte) | Análogo em CodeAgent? | Detector sobre `code_action` / trace | Levanta exceção? | Custo |
|---|---|---|---|---|
| **IFN** — nome de função alucinado *(ToolScan)* | ✅ **Direto e forte** | `ast.parse(code_action)` → coletar todo `ast.Call`; extrair nome (`Name.id`, ou raiz da cadeia `Attribute`). Subtrair: (a) inventário autorizado de tools/subagentes, (b) builtins permitidos pelo sandbox smolagents, (c) nomes ligados localmente **no mesmo bloco** (`Assign`, `FunctionDef`, `Import`, alvos de `for`/`with as`/`except as`, comprehensions). O resto = alucinação. | ✅ Sim — mas como `InterpreterError` / `NameError`, **não** como `SyntaxError`. **Cheque se seu regex tem bucket para esses.** Se não tiver, eles estão hoje mal-classificados. | **D** |
| **IAN** — nome de argumento alucinado *(ToolScan)* | ✅ Direto | Para cada `ast.Call` a uma tool conhecida, coletar `keyword.arg`; comparar com `inspect.signature(tool)`. Atalho sem assinaturas: regex em `err_msg` por `unexpected keyword argument '(\w+)'` — o nome alucinado vem de graça na mensagem. | ✅ Sim, como `TypeError` | **D** (via err_msg) / **D+** (via AST) |
| **IAV** — valor errado / argumento obrigatório omitido *(ToolScan)* | ⚠️ Parcial | Duas metades. **(a) Omissão de obrigatório:** regex em `err_msg` por `missing \d+ required positional argument`. **(b) Valor inventado:** para cada literal string/número passado a uma tool, checar se a substring aparece em `model_input_messages` (a tarefa) ou em qualquer `observations` anterior **da mesma exec_id**. Zero suporte = argumento não-ancorado. | (a) sim; (b) **não** | (a) **D**, (b) **D** |
| **IAT** — tipo de argumento errado *(ToolScan)* | ⚠️ Parcial — **lacuna real do paradigma** | Inferência de tipo sobre nós literais (`ast.Constant` → `type(node.value)`; `List`/`Dict`/`Set` → container) vs. anotação de tipo da tool. Só funciona para literais; argumento vindo de variável exige dataflow. **Sem schema validator, IAT tende a degradar em corrupção silenciosa em vez de erro.** | Às vezes (`TypeError` fundo adentro), muitas vezes **não** | **D+** |
| **RAC** — chamada idêntica repetida *(ToolScan)* | ✅ **Direto e de alto valor** | Normalizar cada nó `ast.Call` (`ast.dump(node)` ou `ast.unparse` + strip) → hash. Agrupar por `exec_id` e contar duplicatas exatas ao longo dos `step_number`. Separar dois regimes: **(i)** repetição após a 1ª ter tido sucesso = redundância pura; **(ii)** repetição após erro = laço de retry (o ToolScan reporta correlação RAC→IAC). Cruzar com `duração` e `tokens` para custo direto. | ❌ **Não** | **D** |
| **IAC** — chamadas insuficientes *(ToolScan)* | ✅ Sim, e é provavelmente seu maior balde silencioso | Sem ground truth é difícil. Proxies: (a) contar itens/perguntas enumerados na tarefa inicial e checar cobertura no `final_answer`; (b) execs que chamam `final_answer` em ≤2 steps com tokens muito abaixo da distribuição do mesmo tipo de tarefa; (c) entidades citadas no pedido que não aparecem em nenhum `code_action` nem na resposta. O ToolScan usou **múltiplas trajetórias válidas anotadas por humanos** (150 queries) — você não tem isso. | ❌ Não | **J** |
| **IFE** — formato inválido *(ToolScan)* | ✅ **Direto — é sua maior família** | Já detectado: `SyntaxError` 223 + `IndentationError` 2 + "resposta em markdown sem chamar `final_answer`" 33 = **258**. Refinamento útil: subclassificar os 223 `SyntaxError` por *causa sintática* (`ast.parse` com captura de `SyntaxError.msg`/`offset`): cerca sem fechar, aspas triplas, f-string, mistura de prosa com código. Cada subclasse é uma unidade de memória procedural distinta. | ✅ Sim | **D** |
| **Tool-Skip** *(ToolFailBench)* | ✅ Sim | Exec que chega em `final_answer` **sem nenhuma chamada a tool/subagente autorizado** em nenhum `code_action` da exec. Variante do caso D.1 do paper: resposta escrita em "estilo-ferramenta" ("Per `<tool>`: …", "Conforme consulta ao sistema…") sem chamada executada — grep no argumento do `final_answer` por frases de atribuição a fonte, cruzado com ausência de chamada. **Em fluxo jurídico isso significa responder de memória paramétrica em vez de consultar o documento.** | ❌ **Não** | **D** |
| **Result-Ignore** *(ToolFailBench)* | ✅ **Direto, e é o melhor detector silencioso do paradigma** | Duas variantes, ambas AST. **(a) Atribuição morta:** o retorno da tool é atribuído (`r = buscar_salario(...)`) e o nome `r` **nunca reaparece** em nenhum `code_action` posterior da mesma exec nem dentro do argumento de `final_answer`. Precisão alta, custo baixo. Variante ainda mais limpa: chamada em *statement position* (`ast.Expr` cujo `value` é `Call`) cujo retorno é simplesmente descartado. **(b) Não-propagação de valor:** extrair tokens estruturados (números, datas, IDs, valores monetários) de `observations` do step *t*; checar interseção com o argumento do `final_answer`. Interseção vazia com observação não-vazia = candidato a RI. | ❌ **Não** | **D** |
| **Output-Fabrication** *(ToolFailBench)* | ✅ Sim — **maior risco no domínio jurídico** | Extrair do argumento de `final_answer` todos os tokens estruturados: números, datas, valores monetários, número de processo (CNJ), CPF/CNPJ, citações de artigo/lei, nomes próprios. Para cada um, procurar suporte na união de todos os `observations` da exec. Sem suporte = candidato a OF. **Falsos positivos previsíveis:** valores *computados* no próprio código (somas, médias, formatações de data). Mitigar rastreando quais literais nasceram de operação aritmética no AST, e/ou passando os sobreviventes por juiz LLM. | ❌ **Não** | **D** (triagem) + **J** (confirmação) |
| **Unnecessary-Tool-Use / Always-Call** *(ToolFailBench)* | ⚠️ Análogo fraco no seu contexto | Sua esteira é dirigida por tarefa, não Q&A aberto, então "chamou sem precisar" é menos aplicável. Variante que **vale** e é barata: chamadas a subagente caro (`ConversationAgent`, `answer_question_using_documents`) cujo resultado é descartado (= detector RI-a) — dá métrica direta de **tokens desperdiçados**. | ❌ Não | **D** |
| **Wrong-Answer** *(ToolFailBench)* | ✅ mas fora de alcance | Exige ground truth do resultado jurídico. Não perseguir agora. | ❌ Não | **J** |

### Ordem de execução recomendada (valor ÷ esforço)

1. **Quebrar `TypeError` (60) e `err_type` por padrão de mensagem.** Zero maquinaria nova, e é o **teste direto** da afirmação do seu relatório. Ao mesmo tempo: **procure explicitamente `NameError` e `InterpreterError` no `err_type`** — se não houver bucket para eles, o IFN está hoje invisível ou mal-alocado.
2. **IFN por AST** (nome chamado ∉ inventário autorizado ∪ locais ∪ builtins). Determinístico, alta precisão, e produz diretamente uma **unidade de memória semântica**: o inventário de ferramentas.
3. **Result-Ignore por atribuição morta.** O detector silencioso de melhor custo-benefício. É a sua primeira medida do ponto cego.
4. **RAC por hash de nó `Call` normalizado, agrupado por `exec_id`.** Determinístico, e converte direto em custo (tokens/latência) — o argumento mais persuasivo para uma **unidade de memória procedural**.
5. **Output-Fabrication por token estruturado sem suporte.** Maior risco do domínio; triagem determinística + confirmação por juiz.
6. **IAV-b: literais de argumento não ancorados no contexto.**
7. **Tool-Skip: exec com `final_answer` e zero chamadas autorizadas.**
8. **Subclassificação dos 223 `SyntaxError` por causa sintática.**
9. **IAT por tipo literal vs. anotação** (precisa das assinaturas).
10. **IAC** — por último, sob amostragem e juiz LLM. É o que exige mais e rende menos por enquanto.

**Nota de implementação:** os detectores 2, 3, 4, 6, 9 exigem uma coisa que você já tem à mão e que é pré-requisito de tudo: **o inventário autorizado** — a lista de nomes que o sandbox realmente injeta nos globals, com assinaturas. Extraia isso primeiro (do código do agente ou do `model_input_messages`, onde o system prompt lista as ferramentas). Sem ele, IFN vira ruído.

---

## O ponto cego: falhas silenciosas (sem exceção)

Esta é a resposta à pergunta 4, e o número é grande.

### No ToolFailBench: **100% das falhas medidas são silenciosas**

Nenhum dos quatro modos — Tool-Skip, Result-Ignore, Output-Fabrication, Unnecessary-Tool-Use — levanta exceção. Todos são falhas de *comportamento*, não de *execução*. O harness executa mocks que sempre retornam com sucesso; a falha está no que o modelo faz com (ou sem) o retorno.

Traduzindo para o seu instrumento: **um classificador por regex de exceção reportaria 0% de erro em todo o ToolFailBench.** Em números do paper, é isso que ficaria invisível:

| Modelo | Falha silenciosa em tarefas tool-required (TSR+RIR+OFR) |
|---|---|
| Grok-4.3 (o melhor de 19) | **13,67%** |
| Claude-Sonnet-4.5 | **20,72%** |
| Qwen2.5-72B | **21,00%** |
| Llama-3.1-8B (o pior) | **52,68%** |
| Média dos 19 headline | **~25%** (100 − CTUR médio 75,02%) |

E, dentro disso, a decomposição importa: **Tool-Skip domina** (11,8%–28,5% em todos os modelos), Result-Ignore é o segundo (0,67%–30,4%, explodindo nos modelos fracos), Output-Fabrication é raro nos modelos fortes (0,13%–2,42%).

### No ToolScan: o tipo **mais comum** também é silencioso

IFN, IAN, IAT e IFE são interceptados pelo mecanismo de feedback antes da execução — no seu sistema, o equivalente são as exceções que você já pega. Mas **IAC e RAC não são detectáveis por validação de forma alguma**: são erros de *suficiência* e de *economia*, não de *validade*.

E o paper diz explicitamente: **"We observe that Insufficient API Calls (IAC) is the most common error pattern."** Nos números da Tabela 4 (lembrando: maior = melhor), IAC é a coluna com os piores scores em quase todos os modelos — GPT-4, o melhor, marca 0,84 (≈16% das chamadas afetadas); GPT-4o-turbo 0,59 (≈41%); Vicuna-13B 0,27; Mixtral-8x7B 0,11. RAC vai de 1,00 (GPT-4, zero) a 0,12 (Mixtral-8x7B, ≈88%).

### O que isso significa para o seu número

Sua taxonomia atual cobre **498 steps com erro (8,6% de 5.781)** — e todos os 498 são *exception-visible*. As duas taxonomias convergem para a mesma conclusão:

> **Os 8,6% devem ser reportados como um piso, não como a taxa de falha.** A literatura sugere que a fatia silenciosa é da mesma ordem de grandeza ou maior — no ToolFailBench, ~25% em média, e ela é *disjunta* da fatia com exceção.

Você **não pode** transportar o número deles para o seu trace (benchmark sintético single-turn ≠ produção multi-turn — ver ressalvas). Mas **pode medir o seu**: os detectores D3 (Result-Ignore por atribuição morta), D4 (RAC por hash) e D7 (Tool-Skip) são **determinísticos, não precisam de rótulo, e rodam direto no `code_action` com `ast`**. Rodar esses três é a maneira mais barata de converter "eu tenho um ponto cego" em "meu ponto cego mede N%".

Argumento de tese que sai daí, e que é forte: **a fatia silenciosa é exatamente a que mais precisa de memória.** Um erro com traceback é auto-corrigível pelo próprio loop do agente — a exceção volta como observação e o modelo tenta de novo. Um Result-Ignore ou um Output-Fabrication **não gera sinal nenhum** dentro da execução; nada no loop o corrige, e ele só é capturável por um observador *fora* da execução que compare steps. Isso justifica precisamente uma camada de memória externa em vez de melhor tratamento de exceção — e o ToolScan §8.1.2 já mostra que injetar o sinal correto no contexto melhora o success rate.

---

## Metodologia e artefatos reusáveis

### ToolFailBench

**Construção.** 1.000 tarefas *single-turn*, 5 domínios × 200 (150 tool-required + 50 control), 9 ferramentas por domínio, retornos *mock* determinísticos. Cada tarefa tool-required guarda **o valor retornado pela ferramenta e o valor provavelmente memorizado**, mais campos estruturados de scoring (as-of dates, status, safety flags, timestamps de protocolo). Ressalva de honestidade dos próprios autores: usam "memorized prior" como *termo de design*, "rather than a claim that the benchmark directly identifies the model's internal source of the value".

**Rotulagem — o desenho de 3 anotadores, que é o artefato metodológico principal:**

1. Um **rule classifier** determinístico, sem LLM. §C.1 verbatim: *"Tool-Skip and Unnecessary-Tool-Use are determined by whether an executed tool call appears in the trace. Result-Ignore is detected when the final answer omits the expected tool-returned value, and Output-Fabrication is detected when the answer contains invented structured information not supported by the mock return."*
2. **Dois juízes LLM com o mesmo rubric mas *overlays* de prompt diferentes** — Qwen3.5-397B-A17B-FP8 com *decision tree*, GLM-4.7-FP8 com *evidence attribution*. Motivo declarado: "reducing the chance that both judges agree only because of one shared prompt framing".
3. **Voto de maioria simples**, empates de três vias resolvidos pelo rule classifier.

**Números de confiabilidade (úteis se você replicar o desenho):** κ de Cohen — regra vs. juiz Qwen 0,649; regra vs. juiz GLM 0,664; **juiz vs. juiz 0,773**; Fleiss κ três vias 0,693. Empates de três vias em apenas **1,5%** dos julgamentos (285/18.900); os dois juízes **sobrepõem** o rótulo da regra em **8,4%**. CTUR média: regra 71,05% vs. ensemble 75,02% — a regra é sistematicamente mais severa porque não tolera paráfrase. κ por modo: Tool-Skip 0,78 / Output-Fabrication 0,60 / Result-Ignore 0,53 / **Unnecessary-Tool-Use 0,23** (com raw agreement 0,84–0,95; atribuem o κ baixo ao efeito de baixa prevalência). Fizeram ainda um **teste de viés same-family** para o juiz Qwen (não encontraram: o juiz Qwen é mais severo com ambos os grupos, gap −5,99 vs. −6,16 p.p.).

**Artefatos reusáveis — e são bons:**

| Artefato | Onde | Reusabilidade para você |
|---|---|---|
| **Base rubric completo do juiz** | Apêndice E.5.1, texto integral | ⭐ **Alta.** Traz definições operacionais dos 5 rótulos, um rubric numérico 0–3 (`tool_selection`, `result_faithfulness`, `answer_correctness`), e uma seção **FORMATTING TOLERANCE** que resolve o falso-positivo mais chato de detector por string (`"$1,001"` vs `"1001"`, arredondamento, unidades reformatadas, paráfrase de chaves JSON). |
| **Overlay decision-tree** (juiz Qwen) | E.5.2, integral | Alta — a árvore T1/T2/T3 é diretamente portável: T1 chamou a tool esperada? T2 tem dado estruturado ausente do retorno? T3 reflete fielmente os valores? |
| **Overlay evidence-attribution** (juiz GLM) | E.5.3, integral | Alta — o esquema EV-1..EV-5 (evidência de chamada / uso fiel / fabricação / memorização / ground truth) força citação de evidência, o que ajuda muito na sua auditoria. |
| **Schema de saída JSON do juiz** | E.5.1 | `{"failure_mode", "confidence": "high\|medium\|low", "tool_selection": N, "result_faithfulness": N, "answer_correctness": N, "reasoning"}` — pronto para usar. |
| **System prompt de domínio (Finanças, integral)** | E.4.1 | Média — vale ler pelo *padrão*, não pelo conteúdo: descrição de tool com assinatura + retorno + "use para" + "**não** use para", regra explícita de "tool return is ground truth", política de fallback/erro/ambiguidade, template de saída obrigatório. É um bom molde para uma unidade de memória semântica por ferramenta. |
| **Template de saída uniforme** | E.3 | Alta — `Per <tool_name>: <valores exatos com unidade>. <campo estruturado>. <1-3 frases limitadas ao que a tool retornou>.` O propósito declarado é dar "a stable surface for checking whether the final answer uses the returned value". **Impor formato de resposta é o que torna o detector de Result-Ignore barato.** Lição de design direta. |
| **Código** | `github.com/SoHarshh/ToolFailBench` (anunciado no abstract; URL responde 200 — não inspecionei o conteúdo) | A verificar. |

### ToolScan

**Construção.** Seed queries de ToolBench e AgentBoard; três aumentações via GPT-4 — *constraint-based* (adiciona argumentos e opções), *sentence-transformation* (reescreve mantendo contexto), *relevant-data* (injeta informação irrelevante em volta das keywords). Geram **600** queries, filtram por viabilidade/validação de restrição/diversidade → **150** finais, sobre 10 ambientes e 30+ tarefas. **Anotação humana com múltiplas trajetórias válidas por query** — é isso que permite medir IAC e IAV, e é exatamente o que você não tem.

**Detecção.** Não é juiz LLM: é um **validador programático pré-execução** (§5), que checa parsing/formato, pertinência ao action space, argumentos válidos e tipos válidos — e devolve feedback estruturado. Modelagem formal como POMDP `<G, S, A, T, O>` emprestada do AgentBoard.

**Métricas.** Para IFN, IAN, IAT, IFE e RAC: `Σ(1 − eᵢ/N)`, onde `eᵢ` = nº de chamadas com o erro na query *i* e `N` = máximo de steps permitidos. Para IAC e IAV, minimizam sobre as trajetórias-verdade: `Σ(1 − min_{g∈Gᵢ} e_{ig}/N)`. **Cuidado ao citar: maior = melhor** (é a fração *sem* erro), e a normalização por `N` deixa a comparação entre modelos sensível ao orçamento de steps.

**Artefatos.** Prompts de aumentação de query nas Tabelas 5–7 e um prompt de execução do benchmark na Tabela 8, todos no Apêndice A. **Não há link de código ou dataset no PDF.** As quatro mensagens de feedback (§5/Figura 2) são o artefato mais reusável e estão transcritas acima.

---

## Ressalvas ao citar

### Sobre o ToolFailBench

1. **Pré-print recentíssimo, autor único, workshop.** arXiv de 6 Jul 2026; ICML 2026 **Workshops**, não main track; um único autor (UC Berkeley). Não ancore afirmação central só nele; use como evidência corroborante e cite o status.
2. **Single-turn — limitação declarada pelos autores.** Verbatim: *"Its single-turn format makes failure modes easier to isolate, but it does not capture multi-turn failures such as tool chaining, recovery from earlier mistakes, or state updates across interactions."* Seu trace tem **5,78 steps por execução em média**, com encadeamento e recuperação. **Os números deles não transferem para o seu regime.**
3. **Retornos *mock*, ambiente sintético e adversarial por construção.** As tarefas são armadilhas paramétricas desenhadas para contradizer priors. Isso infla RI de propósito e não representa o perfil de uma esteira em produção, onde a ferramenta retorna o que retorna.
4. **O domínio "law" deles ≠ o seu.** É pesquisa jurídica em *common law* norte-americano (case law, statutes, regulations, deadlines, jurisdiction tools), single-turn, em inglês. Não é fluxo processual brasileiro, não é multi-agente, não é português, não tem PII real.
5. **Os rótulos dependem de juízes que podem compartilhar cegueira** — admitido: *"the judges may still share blind spots"*. E os dois modos mais interessantes para você são os de κ mais baixo: Result-Ignore 0,53, Unnecessary-Tool-Use 0,23.
6. **Contaminação futura.** Os próprios autores alertam que, pós-release, overlap treino-teste é possível.
7. **Três runs excluídos do headline** por problemas de harness/parser (glm-4-9b, mistral-7b, deepseek-r1-distill-llama-8b) — os 19 do leaderboard não são uma amostra aleatória de 22.

### Sobre o ToolScan

1. **Workshop do ICLR 2025 (Building Trust), não main track.** E o paper mudou de nome entre v1 (SpecTool) e v2 (ToolScan) — cite as duas formas para ser rastreável.
2. **Escala pequena.** 150 queries, 30+ tarefas, 10 ambientes. É um benchmark diagnóstico exploratório, não uma medida de população.
3. **Modelos de safra 2024.** GPT-4-0125-preview, GPT-3.5-turbo-1106, Meta-Llama3-8b, Vicuna-13B-16k, Mixtral, Code-Llama-13B, xLAM. **As taxas absolutas estão desatualizadas para 2026.** Cite a *taxonomia* (que envelhece bem) e os *mecanismos* (RAC→IAC, similaridade de API → IAC, irrelevância → IFN); não cite os números como estado da arte.
4. **Ambientes de consumidor.** Filmes, viagem, esportes, clima, piadas, domínios de mídia. Nada jurídico, nada empresarial, nada de alto risco, nada em português.
5. **Métrica invertida e normalizada por `N`.** Maior = melhor; e a divisão pelo teto de steps torna a comparação entre modelos dependente do orçamento. Leitor desatento inverte o sinal.
6. **Sem artefato público no paper.** Nenhum link de código ou dataset.

### Ressalva de paradigma — vale para as duas, e é a mais importante

7. **As duas taxonomias pressupõem interface de function-calling estruturada com schema e validador.** Seu agente registra **uma** ferramenta, `python_interpreter`; o "tool call" é um nó `ast.Call` dentro de código Python, não um objeto JSON validado. Consequência: **IFN, IAN e IAT são, literalmente, sempre zero no seu sistema pela definição original**, porque não existe lista de API nem schema de argumento a violar no ponto de chamada. Aplicar essas métricas exige **redefinir "API call" como "nó de chamada no AST do `code_action`" e "API list" como "inventário de nomes injetados nos globals do sandbox"**. Essa redefinição é uma **adaptação metodológica sua** e precisa ser declarada como tal no relatório — não como aplicação direta do instrumento deles. É defensável (o ToolScan inclusive nota que modelos de código vão bem em function calling, sugerindo parentesco entre os paradigmas), mas é uma escolha sua e a validade dela não vem emprestada dos papers.
8. **Nenhuma das duas cobre a região onde vive 41% dos seus erros:** pós-chamada, pré-resposta, dentro do código — suposições sobre o *schema do retorno* da ferramenta. O ToolScan é todo pré-execução; o ToolFailBench é todo sobre a resposta final. Trate isso como lacuna a preencher, e diga que é lacuna.
9. **Benchmark ≠ produção.** Retornos mock determinísticos, tarefas curadas, sem PII, sem latência real, sem falha de upstream, sem multi-agente. Seus 8,6% e os ~25% deles **não são comparáveis em nenhuma direção**. Use as taxonomias como *lente*, os números como *ordem de grandeza qualitativa*, e jamais como baseline.
10. **Sobre o *Beyond the Leaderboard* (2607.05775):** é revisão narrativa, não sistemática, sem protocolo pré-registrado, e os autores declaram que **não reproduziram nenhum experimento** — "Table 2 should be read as a compilation of others' reported results rather than an independently verified comparison". Use apenas como confirmação de terceiro independente de que os sete tipos do ToolScan são lidos do mesmo jeito. Nunca como fonte de número.

---

## Trechos literais de apoio

**ToolFailBench — a motivação, que é quase o seu argumento de ponto cego (Abstract):**
> "A model that never calls a needed tool and a model that calls the tool but ignores the result can look similar under final task accuracy."

**ToolFailBench — a taxonomia (§3.2):**
> "We define three failure modes: **Tool-Skip (TS)**, where the model does not produce a valid executed tool call; **Result-Ignore (RI)**, where the model calls the tool but does not use the returned data; and **Output-Fabrication (OF)**, where the model calls the tool but adds invented structured information not present in the return."

**ToolFailBench — a regra determinística (§C.1) — o molde dos seus detectores:**
> "Tool-Skip and Unnecessary-Tool-Use are determined by whether an executed tool call appears in the trace. Result-Ignore is detected when the final answer omits the expected tool-returned value, and Output-Fabrication is detected when the answer contains invented structured information not supported by the mock return."

**ToolFailBench — por que só regra não basta (§5.4):**
> "The rule classifier can mark a faithful answer as a failure when the model uses the correct tool value but does not copy the expected string exactly."

**ToolFailBench — separar formato de saída para facilitar detecção (§E.3):**
> "The uniform format makes outputs easier to compare across models and gives the rule classifier a stable surface for checking whether the final answer uses the returned value."

**ToolFailBench — Tool-Skip disfarçado de sucesso (§D.1) — cheque isso no seu trace:**
> "In several cases, the final answer still followed a tool-style format, using phrases such as 'Per <tool>' and then giving plausible-looking values. We treat these cases as Tool-Skip behavior because the trace does not contain an executed tool call, even if the final answer is written as if a tool had been used."

**ToolFailBench — limitação declarada (§6):**
> "Its single-turn format makes failure modes easier to isolate, but it does not capture multi-turn failures such as tool chaining, recovery from earlier mistakes, or state updates across interactions."

**ToolScan — os sete tipos (§3):** transcritos integralmente na seção "ToolScan" acima.

**ToolScan — fragilidade da chamada (§3):**
> "Note that these tool calls are particularly brittle - even a slight change to an argument, a missing argument, or incorrect tool call can produce drastically different and incorrect results downstream."

**ToolScan — o erro mais comum é silencioso (§8):**
> "We observe that Insufficient API Calls (IAC) is the most common error pattern. […] (1) Models like GPT only solves part of the query. If there are multiple questions asked in the same query, GPT ends after answering the first query. (2) Models are unable to distinguish similar APIs and ignore the given constraints."

**ToolScan — RAC como laço de repetição, e sua correlação com IAC (§8):**
> "They get stuck in a loop based on their internal belief of solving the query and call the same API multiple times even if they are failing. We also see a co-relation between RAC and IAC between these models which suggests that RAC often leads to IAC."

**ToolScan — o mecanismo de feedback (§5/Fig. 2) — o antecedente mais próximo do seu mecanismo de memória:**
> "- Incorrect Format, please follow the format {}
> - Invalid Action generated, valid actions are {"x", "y", "z"}
> - Invalid Argument for action "a", valid arguments are {'b', 'c'}
> - Invalid Argument type for action "k", its valid type is "bool""

**ToolScan — o efeito do feedback (§8.1.2):**
> "In scenarios where the feedback mechanism was absent, the model frequently repeats errors, such as incorrect function names, leading to a significant reduction in its task completion effectiveness. Without guidance, the model struggled to recover from initial mistakes, which compounded its challenges in achieving desired outcomes. Conversely, with the feedback mechanism in place, the model exhibited immediate improvements in subsequent interactions."

**ToolScan — modelos de código vão bem em function calling (§8) — argumento a favor do paradigma CodeAgent:**
> "Another noteworthy observation is the exemplary performance of the Code-Llama-13B model, surpassing many other generically-purposed models. Our hypothesis is that there may be some inherent similarity between coding-associated tasks and function calls."

**ToolScan — irrelevância induz alucinação de API (§8.1.1):**
> "Results indicate that most models produce more errors in Incorrect Function Name (IFN), posing deployment challenges in the real-world scenario. […] the percentage of queries without IFN decreases when irrelevant constraints are introduced in the query."

**ToolFailBench citando o ToolScan pelo nome antigo (Referências) — a prova da mudança de título:**
> "Kokane, S., Zhu, M., Awalgaonkar, T., […] Savarese, S. **SpecTool: A benchmark for characterizing errors in tool-use LLMs.** arXiv preprint arXiv:2411.13547, 2024."

**Beyond the Leaderboard (§4.1) — confirmação independente da leitura dos sete tipos:**
> "ToolScan (Kokane et al., 2024, arXiv:2411.13547; ICLR 2025 Workshop) characterizes LLM tool-use errors into seven recurring types: insufficient API calls, incorrect argument values, incorrect argument names, incorrect argument types, repeated (redundant) API calls, incorrect (hallucinated) function names, and invalid output formatting."

**Beyond the Leaderboard (§4.1) — a categoria que cobre seus KeyError, e que NÃO é do ToolScan:**
> "A parallel taxonomy developed for REST API tool testing groups failures into four categories — tool invocation errors (wrong tool selected, or unproductive recursive invocation), input specification errors (missing or hallucinated parameters), execution errors, and **output-interpretation errors** (pre-print, arXiv:2504.15546, 2025)."

**Beyond the Leaderboard (§4.1) — "functional hallucination", enquadramento útil para o seu IFN:**
> "Related work frames these errors as a distinct class of 'functional hallucination,' separate from the textual confabulation more commonly discussed in LLM hallucination research, because functional hallucinations manifest as structurally plausible but semantically incorrect actions rather than false statements."

**Beyond the Leaderboard (§9) — a ressalva que obriga a não citar números dele:**
> "we rely on the benchmark and error-taxonomy papers' own reported methodology and inter-annotator agreement statistics; we did not independently reproduce any of the underlying experiments."
