# Schema do trace cru — esteira de agentes do fluxo jurídico

**Arquivo:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (14,2 MB comprimido). **git-ignored** — contém PII (nomes
de clientes, nºs de processo, trechos de documentos em claro); ver `.gitignore` da raiz (`*.csv.xz`, `*.csv`) e
o desta pasta. Nunca versionar sem anonimização.

**Cobertura:** 1.000 execuções, nov/2025–ago/2026 · 5.781 `ActionStep` (+ 2.569 `TaskStep` e 46 `PlanningStep`,
ver §Estrutura de `txt_etap_memo` abaixo) · 142,6M tokens. **Provável `LIMIT 1000`** na
query de origem — amostra, não população (`04-roadmap.md` item 3).

## Granularidade

1 linha do CSV = **1 execução** de agente. Os steps daquela execução vivem no JSON aninhado da coluna
`txt_etap_memo` (células chegam a dezenas de MB).

## Colunas (11)

| # | Coluna | Conteúdo | Fonte |
|---|---|---|---|
| 0 | `cod_idef_aget` | id numérico do agente (tipo/papel) | dado |
| 1 | `cod_idef_exeo` | id da execução | dado |
| 2 | `cod_idef_stat_exeo_aget` | código de status da execução (ver §Status) | dado; semântica **inferida** |
| 3 | `cod_idef_cvsa_asnc` | id de conversa / fluxo assíncrono | nome **inferido** da abreviação |
| 4 | `dat_hor_encm_exeo` | data/hora de encerramento — **só preenchida para status 3 e 34** | dado |
| 5 | `txt_etap_memo` | JSON das etapas: `model_output` (thought), `code_action`, `observations`, `tool_calls`, `model_input_messages`, e a chamada `final_answer()` | dado |
| 6 | `txt_vrvl_locl` | "variável local" — provável namespace Python persistido entre steps | nome **inferido** |
| 7 | `txt_rspa_fina` | texto da resposta final (coluna dedicada) — **vazia para status 1** | dado |
| 8 | `dat_hor_inio_exeo` | data/hora de início | dado |
| 9 | `cod_vers_aget` | versão do agente | dado |
| 10 | `anomesdia` | AAAAMMDD (int) | dado |

⚠️ Nomes das colunas 3 e 6 são leitura da abreviação, não confirmados com a esteira.

## Estrutura de `txt_etap_memo` — os steps (medido em 16/09/2026, direto no trace)

O campo `txt_etap_memo` é o dump da *working memory* estilo **smolagents**: um dict `{papel: [steps]}`, onde a
chave é o papel (`managerAgent`, `ConversationAgent`, agentes de domínio…) e a lista contém os passos na ordem
em que aconteceram. Cada passo tem um discriminador `"__class__"`. **Nada aqui é derivado pelo nosso pipeline
— é o que o sistema persistiu em produção**; o `drill_down.py` apenas formata (`[THOUGHT]`, `[CÓDIGO]`…) o
conteúdo cru destes campos.

**Censo (840 execuções com memória):** `TaskStep` **2.569** · `ActionStep` **5.781** · `PlanningStep` **46**.

```json
{
  "managerAgent": [
    {"__class__": "TaskStep", "task": "Responda a pergunta: 'PROMPT: ...'", "task_images": null},
    {"__class__": "ActionStep", "step_number": 1, "model_input_messages": [...], "model_output": "Thought: ...",
     "model_output_message": {...}, "code_action": "...", "observations": "...", "error": null, ...},
    {"__class__": "PlanningStep", "plan": "Here are the facts I know and the plan of action...", ...},
    {"__class__": "ActionStep", "step_number": 2, ...}
  ],
  "ConversationAgent": [ ... ]
}
```

### TaskStep — a tarefa recebida

Só carrega o texto da tarefa que abriu a trajetória daquele papel: `task` (str, sempre), `task_images` (null).
Não tem custo/duração — as métricas vivem no `ActionStep`.

### ActionStep — o passo de trabalho (a unidade de toda a análise)

Presença medida campo a campo (n = 5.781):

| Campo | Presença | Tipo | O que é |
|---|---:|---|---|
| `__class__`, `step_number`, `is_final_answer`, `model_input_messages`, `timing` | 100% | str/int/bool/list/dict | sempre presentes |
| `model_output`, `model_output_message` | 99,9% | str/dict | saída crua do LLM: texto ("Thought: ... <code>...") + a mensagem estruturada |
| `code_action` | 99,3% | str | código extraído do bloco `<code>` — dos 39 steps sem ele, 33 são exatamente os `AgentParsingError` (resposta sem bloco de código) |
| `token_usage`, `tool_calls` | 99,9% / 99,3% | dict/list | `{input_tokens, output_tokens, total_tokens}`; calls com `{id, type, function}` estilo OpenAI |
| `observations` | 94,0% | str | o que o interpretador/harness devolveu (logs + último retorno) |
| `action_output` | 56,1% | str | saída do passo — 3.243 steps têm, e 79% deles (2.563) são steps de `is_final_answer` |
| `error` | **8,6% (498)** | dict | **só presente quando o step falhou**: `{"type": ..., "message": ...}` |

Detalhes medidos:

- **`error.type` é nativo do smolagents**, não da nossa `classify()` — e só tem dois valores neste trace:
  `AgentExecutionError` (465, falha *durante* a execução do código) e `AgentParsingError` (33, falha *antes* de
  rodar — é justamente a família "resposta sem bloco de código"). Eixo determinístico a custo zero, ainda pouco
  explorado (`04-roadmap.md` item 10).
- **`model_output` ≠ prefixo "Thought:"** — o campo existe em todo step, mas o *invólucro textual* depende do
  template de prompt do papel (censo em `04-roadmap.md` item 10: 0% `WorkflowManager` · 9,0% `managerAgent` ·
  86,7% `RespostaBacen` · 100% em vários de domínio). Em alguns casos é um JSON `{"thought": ..., "code": ...}`
  no lugar do formato ReAct. Não confundir com o campo `plan` do `PlanningStep`, abaixo.
- **`model_input_messages`** é o contexto exato que o step recebeu: lista de mensagens `{role, content, ...}`,
  começando por `role: "system"` (que **declara as ferramentas** como assinaturas `def nome(...)` — a fonte
  autoritativa do inventário de 90) e depois `role: "user"`/histórico com o echo dos erros anteriores. É este
  campo que torna o achado 86,3% verificável textualmente (`03-procedimento-validacao.md` §1.5). `content` é
  lista de blocos `{"type": "text", "text": ...}`.
- **`timing`** = `{start_time, end_time, duration}` (timestamp real, segundos) em 100% dos steps — matéria-prima
  de span já coletada (ver discussão OTel/Datadog em `literature/trail-2505.08638.md`).
- Exemplo real anonimizável (o caso-vitrine `2a407143…`, step 3): `model_output` começa literalmente com
  `"Thought: Ocorreu um erro porque a resposta anterior não estava dentro de um bloco <code>..."` —
  o autodiagnóstico do agente está gravado no trace, não é inferência.

### PlanningStep — o plano nativo do smolagents (raro: 46 no trace inteiro)

Emitido pelo `planning_interval` do smolagents, num **campo separado** (`plan`) — não é o `"Thought:"` do
`model_output`. Aparece em 3 papéis: `RespostaBacen` (35), `CalculoTrabalhista` (9) e `null` (2 — artefato de
serialização de papel, ver `04-roadmap.md`). Campos (100% dos 46): `plan` (str — abre com
*"Here are the facts I know and the plan of action…"*, template nativo do framework), `model_input_messages`,
`model_output_message` (com `content` = o plano estruturado: "1. Facts survey…"), `timing`, `token_usage`.
**Não tem** `code_action`/`observations`/`error` — planeja, não executa. As versões antigas do pipeline o
descartavam em silêncio; `drill_down.py caso` e o notebook já o incluem (`04-roadmap.md` item 10).


## `cod_idef_stat_exeo_aget` (o campo "status")

Medido direto do CSV em 2026-09-10 (`lzma.open` + `csv.reader`, `field_size_limit` alto). **Nunca null** —
sempre um de 4 valores.

| status | execuções | % | tem `dat_hor_encm_exeo`? | tem `txt_rspa_fina`? |
|---|---:|---:|---|---|
| **1** | 872 | 87,2% | não (0/872) | não (0/872) |
| **3** | 68 | 6,8% | sim (68/68) | sim (63/68) |
| **2** | 51 | 5,1% | não (0/51) | parcial (29/51) |
| **34** | 9 | 0,9% | sim (9/9) | sim (9/9) |

Cortes adicionais:

- **status 1 = default dos agentes de maior volume.** `cod_idef_aget` 1 (714 exec) e 2 (100 exec) são 100%
  status 1. Os agentes de domínio (ids 67, 133, 168, 496…) concentram 2/3/34.
- **status 34 só aparece a partir de abr/2026** (0 em nov–dez/2025) — possivelmente código adicionado depois.
- status 1 domina todos os meses.

### Por que o status não serve como rótulo de sucesso/fracasso

Para os 87% em status 1, a plataforma não persiste nem encerramento nem resposta final — **mesmo o agente
tendo chamado `final_answer()` dentro de `txt_etap_memo`**. As únicas 77 execuções (7,7%) com sinal de "fechou"
estão em status 3/34. Por isso a análise (`02-relatorio-achados.md` §3.1 / §4) construiu um check de sucesso
**por conteúdo** (procura `final_answer` no JSON + duas frases de recusa), não pelo status.

**Precisão:** `01-racionais.md` §4 Passo 1 diz "100% das memórias contêm `final_answer`" — vale para o **JSON
`txt_etap_memo`** (~840 de 1.000). A **coluna `txt_rspa_fina`** é outro campo e está vazia em 87%. São duas
coisas distintas.

## Aberto — perguntas para o time da esteira (`04-roadmap.md` item 3)

1. O que é cada código? status 1 = "em andamento" / "não rastreado até o fim" / "sucesso não persistido"?
2. Por que status 1 nunca tem `dat_hor_encm_exeo` / `txt_rspa_fina` se houve `final_answer()`? Quem escreve
   essas colunas, e quando?
3. 3 e 34 são os "encerrados" — 3 = sucesso, 34 = erro? Outra distinção?
4. status 2 (sem encerramento, resposta parcial) — o que é?
5. status 34 só desde abr/2026 — código novo? o que era antes?
6. O status depende do *tipo* de agente (`cod_idef_aget` 1 e 2 são sempre status 1)?
7. A extração de 1.000 linhas filtra por status?
8. Confirmar os nomes das colunas 3 (`cod_idef_cvsa_asnc`) e 6 (`txt_vrvl_locl`).

---
Extração e cross-tabs: `lzma.open` + `csv.reader`, 2026-09-10. A semântica dos códigos de status e os nomes
das colunas 3/6 são **inferência** — confirmar com a esteira antes de citar como fato.
