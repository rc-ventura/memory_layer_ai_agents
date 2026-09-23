# Schema do trace cru — esteira de agentes do fluxo jurídico

**Arquivo:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (14,2 MB comprimido). **git-ignored** — contém PII (nomes
de clientes, nºs de processo, trechos de documentos em claro); ver `.gitignore` da raiz (`*.csv.xz`, `*.csv`) e
o desta pasta. Nunca versionar sem anonimização.

**Cobertura:** 1.000 execuções, out/2025–ago/2026 (lotes de corte nov/2025–ago/2026) · 5.781 `ActionStep` (+ 2.569 `TaskStep` e 46 `PlanningStep`,
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
| 2 | `cod_idef_stat_exeo_aget` | código de status da execução (ver §Status) | dado; **nomes confirmados** pela tabela de status (23/09) — ver §Status |
| 3 | `cod_idef_cvsa_asnc` | id de conversa / fluxo assíncrono | nome **inferido** da abreviação |
| 4 | `dat_hor_encm_exeo` | data/hora de encerramento — **só preenchida para status 3 e 34** | dado |
| 5 | `txt_etap_memo` | JSON das etapas: `model_output` (thought), `code_action`, `observations`, `tool_calls`, `model_input_messages`, e a chamada `final_answer()` | dado |
| 6 | `txt_vrvl_locl` | namespace de variáveis locais do interpretador, por papel — **confirmado por inspeção do conteúdo (18/09)**, ver §`txt_vrvl_locl` abaixo | dado |
| 7 | `txt_rspa_fina` | texto da resposta final (coluna dedicada) — **vazia para status 1** | dado |
| 8 | `dat_hor_inio_exeo` | data/hora de início — **é o relógio da análise**: `mes` = mês desta coluna (ver §Datas) | dado |
| 9 | `cod_vers_aget` | versão do agente | dado |
| 10 | `anomesdia` | AAAAMMDD (int) — **data de corte do lote, não da execução** (ver §Datas); vira `mes_particao` | dado; semântica **inferida** |

⚠️ Nome da coluna 3 é leitura da abreviação, não confirmado com a esteira. A coluna 6 foi confirmada por
inspeção direta do conteúdo em 18/09/2026 (ver §`txt_vrvl_locl` abaixo).

## Datas — `dat_hor_inio_exeo` data a execução; `anomesdia` data o lote (medido em 23/09/2026)

Até 23/09/2026 o pipeline tirava o `mes` de `anomesdia`. Não serve: `anomesdia` tem só **9 valores** nas 1.000
linhas, um por mês e sempre perto do fim dele (`20251130`, `20251231`, …, `20260629`, `20260830`), e o início
da execução é **sempre anterior** a ele — em nenhuma linha a execução começa depois. Nas 840 execuções com
memória, o mês de `anomesdia` só bate com o mês real em **35,8%**; a defasagem mediana é de **46 dias** (máx.
230). É a assinatura de um **corte periódico que acumula tudo o que rodou até ali** — hipótese de trabalho: a
data de corte da democratização da base, feita no fim de cada mês. `dat_hor_inio_exeo` bate com o
`timing.start_time` que o runtime do agente grava em cada step (mesmo mês e mesma semana em 840/840, diferença
máx. 0,26 h) — é a data da execução.

| Coluna derivada (`base_pipeline.carregar_trace`) | Vem de | Uso |
|---|---|---|
| `mes` = `mes_exec` | `dat_hor_inio_exeo` | **toda** análise temporal (triagem, séries por mês) |
| `mes_particao` | `anomesdia` | só proveniência: de qual lote a linha veio (sobreposição entre bases, como uma base foi recortada) |

Consequência para qualquer base nova: um recorte "de um mês" feito por `anomesdia` cobre vários meses de
execução (na base 1, o lote de ago/2026 tem 48 execuções, 5 delas de agosto). `checklist.py` §5 imprime o
cruzamento lote × mês real. Método e evidência: `03-procedimento-validacao.md` §1.12.

## Estrutura de `txt_etap_memo` — os steps (medido em 16/09/2026, direto no trace)

O campo `txt_etap_memo` é o dump da *working memory* estilo **smolagents**: um dict `{papel: [steps]}`, onde a
chave é o papel (`managerAgent`, `ConversationAgent`, agentes de domínio…) e a lista contém os passos na ordem
em que aconteceram. Cada passo tem um discriminador `"__class__"`. **Nada aqui é derivado pelo nosso pipeline
— é o que o sistema persistiu em produção**; o `drill_down.py` apenas formata (`[THOUGHT]`, `[CÓDIGO]`…) o
conteúdo cru destes campos.

**Censo (840 execuções com memória):** `TaskStep` **2.569** · `ActionStep` **5.781** · `PlanningStep` **46**.

**Por que 840 e não 1.000** (medido 19/09, `json.loads` linha a linha): as 160 linhas restantes têm
`txt_etap_memo` **vazio** — 159 são status 1, 1 é status 3. Não é JSON corrompido: **0 falhas de parse**
entre as preenchidas. A execução existe na tabela mas o dump da working memory não veio — "com memória"
no funil do §8.0 quer dizer *campo preenchido*, não "conseguimos ler". Por que o campo vem vazio é
pergunta aberta para a esteira (relacionada a §Status: status 1 também não persiste encerramento nem
resposta final — mas 713 execuções status 1 **têm** memória, então status não determina o vazio).

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

## `txt_vrvl_locl` — o namespace de variáveis locais por papel (confirmado 18/09)

Medido direto do CSV: presente em ~90% das execuções. JSON `{papel: {namespace}}` — o **estado final das
variáveis Python** (`locals()` do executor smolagents) que o agente foi definindo nos `code_action` ao longo
dos steps. Cada namespace mistura:

- **internos do executor**: `__name__` (`"__main__"`), `_print_outputs` (buffer de print),
  `_operations_count` (contador de operações);
- **variáveis do agente**: tudo que foi atribuído step a step — ex. na execução `1be966e7` (`RespostaBacen`):
  `id_reclamacao`, `evidencias`, `info_evidencias`, `reclamacao_texto`, `draft`, `resposta_org`, `quebra`,
  `final_output`.

Não contém steps nem erros — é o que **sobrou de estado** no fim da execução. Utilidade medida: guarda o
**retorno real das ferramentas** como o agente o recebeu — na execução `1be966e7`, a variável `quebra`
contém `{"vazamento_sigilo": "NAO", "justificativa": "..."}`, o campo real do contrato que o prompt induz a
chamar de `quebra_sigilo` (evidência direta da unidade nº10, ver `06-racionais-mineracao-unidades-n2-n10.md`).
Vale baixar junto no dataset de erros como contexto de estado.


## `cod_idef_stat_exeo_aget` (o campo "status")

**Dicionário (tabela `status_execucao_agente.csv`, recebida em 23/09/2026):**

| código | nome | no dicionário desde |
|---|---|---|
| 1 | ativo | sempre |
| 2 | pausado | sempre |
| 3 | encerrado | sempre |
| 34 | validado | fev/2026 |
| 67 | falha | mar/2026 |

A tabela só traduz código → nome; é um dicionário fotografado a cada corte (`anomesdia`, 18 cortes, de set/2025 a
set/2026), não um log por execução. O "desde" é a primeira fotografia em que o código aparece, e não diz quando as
execuções passaram a receber o status. **Correção:** a inferência anterior "34 = erro" estava errada — 34 é
**validado**. O código 67 (**falha**) **não aparece na base 1** (0/1.000); existe no dicionário, e a base 2 pode tê-lo.
O que a tabela **não** diz: por que status 1 (ativo) nunca traz encerramento (o nome sugere "ainda em curso", o que
não explica execuções com `final_answer` no JSON), nem como as 1.000 linhas de cada extração foram escolhidas.

Medido direto do CSV em 2026-09-10 (`lzma.open` + `csv.reader`, `field_size_limit` alto). **Nunca null** —
sempre um de 4 valores na base 1 (1, 2, 3, 34).

| status | execuções | % | tem `dat_hor_encm_exeo`? | tem `txt_rspa_fina`? |
|---|---:|---:|---|---|
| **1** ativo | 872 | 87,2% | não (0/872) | não (0/872) |
| **3** encerrado | 68 | 6,8% | sim (68/68) | sim (63/68) |
| **2** pausado | 51 | 5,1% | não (0/51) | parcial (29/51) |
| **34** validado | 9 | 0,9% | sim (9/9) | sim (9/9) |

Cortes adicionais:

- **status 1 = default dos agentes de maior volume.** `cod_idef_aget` 1 (714 exec) e 2 (100 exec) são 100%
  status 1. Os agentes de domínio (ids 67, 133, 168, 496…) concentram 2/3/34.
- **status 34 só aparece a partir de mar/2026** (0 em out/2025–fev/2026) — possivelmente código adicionado depois.
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

1. ~~O que é cada código?~~ — respondido pela tabela (23/09): 1 ativo, 2 pausado, 3 encerrado, 34 validado, 67 falha.
   Resta: por que "ativo" (1) cobre 87% das execuções, muitas com `final_answer`?
2. Por que status 1 nunca tem `dat_hor_encm_exeo` / `txt_rspa_fina` se houve `final_answer()`? Quem escreve
   essas colunas, e quando?
3. ~~3 e 34: sucesso × erro?~~ — não: 3 = encerrado, 34 = validado (etapa posterior, não erro). Validado por quem e como?
4. status 2 (sem encerramento, resposta parcial) — o que é?
5. status 34 só desde mar/2026 — código novo? o que era antes?
6. O status depende do *tipo* de agente (`cod_idef_aget` 1 e 2 são sempre status 1)?
7. A extração de 1.000 linhas filtra por status?
8. ~~Confirmar os nomes das colunas 3 e 6~~ — coluna 6 (`txt_vrvl_locl`) confirmada por inspeção do conteúdo
   (18/09, ver §`txt_vrvl_locl`). Resta confirmar só a coluna 3 (`cod_idef_cvsa_asnc`).
9. O que é `anomesdia`? A hipótese é a data de corte da democratização da base (§Datas). Como a query de
   extração filtra por ele — um recorte "de agosto" pega o lote de agosto ou as execuções de agosto?

---
Extração e cross-tabs: `lzma.open` + `csv.reader`, 2026-09-10. A semântica dos códigos de status e o nome
da coluna 3 são **inferência** — confirmar com a esteira antes de citar como fato.
