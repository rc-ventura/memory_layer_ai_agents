# Plano atual — o roadmap geral das análises: o que vale, o que está feito, o que vem agora

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](glossario.md).

**Atualizado:** 06/10/2026 · **Branch:** `2026-10-06-validacao-kit-base2` (o §4.14; a anterior, PR #33, mergeada).
Índice do que já foi auditado: [`2026-09-trace-law-flow/audit/README.md`](2026-09-trace-law-flow/audit/README.md).

**Para que serve:** a **única fonte** do "o que fazer agora", em **qualquer análise**: as decisões em vigor (§1, uma
linha cada, com o link para o porquê), o feito (§2), o que está em discussão (§3), a fila ativa (§4) e o backlog
geral (§5).

**O que não entra aqui:**
- o **porquê** (racional) → os `docs/NN-racionais-*.md` de cada análise;
- os **números** → os relatórios de cada análise;
- o **histórico** de cada ajuste e de cada etapa → o livro-razão ([`pipeline-entre-bases.md`](pipeline-entre-bases.md));
- o **backlog numerado de cada análise**, com o detalhe dos itens → o roadmap dela, hoje
  [`2026-09-trace-law-flow/docs/04-roadmap.md`](2026-09-trace-law-flow/docs/04-roadmap.md). Os números de lá são
  estáveis e citados no projeto todo; aqui eles aparecem como "(roadmap #N)".

O plano antes da limpeza de 06/10, com o detalhe dos itens feitos: `git show f6c86d7:analysis/plano-atual.md`.

**Regra de ligação:** quando um item do backlog vira trabalho ativo, ele sobe para o §4 com "(roadmap #N)", e o roadmap
ganha "→ plano-atual 4.x". Quando termina, vai para o §2 com o commit, sai do §4 e é riscado no roadmap. Os números
4.x nunca são reaproveitados.

---

## 1. O que vale (decidido)

**Regras de trabalho:**
- **Uma solução por vez:** contexto, solução, argumento com evidência e tipo da mudança; espera a aprovação; executa,
  verifica na base 1, commita e diz o que o Rafael roda na máquina 2.
- **Regra nova só olhando as duas bases** (livro-razão, Ajuste 7).
- **Leitura por LLM é `[assistido]`** e vale como hipótese; o determinístico é `[conferido]`. Nenhum LLM no caminho da
  classificação.
- **Da máquina 2 só saem** contagens, nomes de papel, ferramenta e modelo, hashes, sim/não, tamanhos, tokens e motivos
  mascarados. Nunca texto de caso nem `exec_id`.

**Organização:**
- Cada análise com método próprio tem o seu conjunto: notebook + racional + relatório + procedimento (protocolo
  `10`–`12`; falhas silenciosas `13`–`15`; candidatas `06`, `07`, `16`). Onde cada mineração está: §4.14.
- Três notebooks: visível (a esteira), invisível (falhas silenciosas) e consolidação (a triagem final) → `09`, livro-razão
  Ajuste 12.
- As funções de medida ficam no `base_pipeline.py` (ou `analysis/base_utils.py`); o notebook e o `drill_down.py` chamam
  as mesmas.

**Destinos decididos:**

| Achado | Destino | Porquê / onde |
|---|---|---|
| Resposta final fora do envelope (M1), ferramenta que concorre com o `final_answer` (M2) | sinal de harness; a concorrente: **monitorar, não dar como corrigida** (02/10) | `10` §4, `11` §1.3; `analysis/registros/monitoramento.json` |
| "O risco à resposta está na plataforma" ([4]) | hipótese, não achado | `14` §5; 4.1c |
| Resposta vazia aceita (M5), narração executada como código (M6) | achado de harness / plataforma | `10` §4; 4.9 |
| Surtos da base 1 (modo) e da base 2 (modelo) | não-memória; achado para a plataforma | `10`, `11` |
| `U_tipo_retorno`, `U_campo_inexistente` | continuam candidatas: não nascem de falha silenciosa | `13` §8, `14` §4 |
| `U_campo_inexistente` | sinal de harness nas duas bases | livro-razão Ajustes 5 e 13 |
| `json_invalido` do `busca_obf` | dono: o agente (o gesto da `U_repr_colado`); memória **e** sinal de harness; monitorar na base 3 | `13`, `14`; livro-razão Ajuste 12 |
| Família do protocolo, base 1 | fechada | `11` |

**Decisões de método, por data** (o porquê no link):
- **02/10:** ocorrência no balde invisível = a mesma régua do visível (livro-razão Ajuste 12) · erro crítico: investigar
  a chamada que morreu antes de decidir o destino (4.6) · alarme de cobertura mostra a concentração (roadmap #34) ·
  sucesso falso: examinar os 24 candidatos da base 2, em dois eixos (4.1c).
- **05/10, o kit e a investigação:** minerar não é comparar com relatório (a verificação é a auditoria independente em
  paralelo) · nenhuma afirmação sem evidência · sigilo por script (`caso-N`) · a investigação por LLM vem depois do
  determinístico, e o modelo propõe e o script conta · as skills são genéricas → [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md),
  skill `mineracao-base`. Os Ajustes 14–16 do protocolo → livro-razão.
- **05/10, notebook específico:** só com frequência **e** confiança, sem sorteio, reconfirmado a cada partição; a
  aprovação é do Rafael → `16`, `06` §10 peça 6.
- **06/10, a leitura e o gate:** leitura em duas etapas (aberta → gate da lista → fechada em outros casos, ≥ 20) ·
  "os leitores discordam" não é "não há lição" · o gate do pesquisador · dividir a unidade é resultado normal →
  `06` §10, `16`.
- **06/10, monitorar:** determinístico (`analysis/registros/monitoramento.json`, um só para as pastas de todas as bases;
  `monitorar.py` no passo 0 de toda mineração). Em monitoramento: `U_nome_inventado`, `U_campo_inexistente`, a
  ferramenta concorrente do `final_answer` → `16` § O monitoramento.
- **06/10, o kit:** mora no próprio `.claude/`, versionado; cada mineração tem um nome só (`/mineracao-<assunto>`);
  `investigar` e `propor-notebook` são skills de chamada manual; o Copilot lê o mesmo `.claude/`, sem cópia →
  [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md).

---

## 2. Feito

| O quê | Commit | Onde está |
|---|---|---|
| Docs da família Protocolo do harness (`10`/`11`/`12`) | `bff1256` | `docs/10-12` |
| `metadados_steps.py` (tokens, finish, campos crus) | `0bd47f1`, `6d0e91c` | `11` §2.3 |
| `drill_down.py critico` | `7c1625d` | `12` |
| **S1** — leitura do erro crítico da base 2 | `0d71323` | `11` §2.5, `10` §4 |
| **S2** e **S2b** — as falhas silenciosas e o motivo; `silenciosas --motivos` e `--forma` | `78ed696`, `0a69ad0`, `41b43b9`, `8ddf2c7`, `6123716`, `de5b601` | livro-razão Etapa 10c |
| **4.1** — S2 fechado na base 2 | registro de 01/10 | livro-razão Etapa 10c |
| **4.2** — o balde invisível: notebook e docs `13`–`15` | registro de 01/10 | livro-razão Etapa 10c |
| PR #29 auditado e mergeado; PR #30 fechado sem merge | `dc89992` | auditoria de 02/10 |
| Auditoria, blueprint das POCs do M1 e diário da semana de 28/09 | `e01238b` | `audit/`, `pocs/`, `research-diary/` |
| **4.0** — ressalvas da auditoria de 02/10 (A–D, F, H) | `675523b` | auditoria de 02/10, Parte II |
| **Ajuste 11** — o [4] respeita o step final e a fronteira de chamada | `675523b` | livro-razão, `13` §4, `14` §5 |
| `audit_recompute9.py` — verificação independente do balde invisível | `675523b` | `audit/README.md` |
| **4.2a** — base 2 rodada na máquina 2 (pendente: reexecutar os notebooks no terminal → 4.14) | relatório de 02/10 | livro-razão Etapa 10c |
| **4.1b (base 2)** e **4.7 / D2** — leitura assistida; RespostaBacen M1 3, M2 1 | relatório de 02/10 | `14` §5, `11` §2.6, `10` §4 |
| Auditoria de 02/10 fechada (Parte II) e índice `audit/README.md` | commit do fechamento | `audit/` |
| **4.2b-0** — a regra de ocorrência do balde invisível (decisão de 02/10) | — | livro-razão Ajuste 12 |
| **4.2b / Ajuste 12** — a consolidação | registro de 04/10 | livro-razão Ajuste 12, `09`, `13`, `14` |
| **4.2c** — a triagem e os gráficos de unidade vão para a consolidação | registro de 04/10 | livro-razão Ajuste 12 (complemento) |
| **4.2d** — base 2, rodada 2; **base 2 finalizada** | registro de 05/10 | livro-razão Etapa 10d, `14` §5 |
| **Ajuste 13** — o campo inexistente da base 2 também é sinal de harness | registro de 05/10 | livro-razão |
| **4.10** — o trace em parquet (leitor único `analysis/leitor_trace.py`) | `bd3db6b` | `analysis/README.md` (intake) |
| **4.12** — o kit de mineração: silenciosas, protocolo, investigação e candidatas (0.1 → 0.6.0) | `bff9714`, `f590038`, `91e9c0a`, `a0fe56c`, `1c36dc2` | [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md), `16` |
| **4.13 / Ajustes 14–16** — o método do protocolo, vindos da investigação de 05/10 | `694636b` | livro-razão, `10` §4 |
| Monitoramento num registro só para todas as bases; o kit no `.claude/`; cada mineração com um nome só | `e069c26`, `20c97dc`, `fdf9a84`, `1ef5d71` | `16`, `kit.md` |
| O racional das lições de hábito (`06` §10) | `f6c86d7` | `06` §10 |
| Este plano limpo: só plano; a errata foi para o livro-razão (§7) | (este commit) | — |

---

## 3. Em discussão — o que de fato queremos medir

**Decisão do Rafael (05/10):** nenhum destes é implementado antes de uma discussão própria, item por item.

1. **Sucesso falso em dois eixos** (4.1c). *Pergunta:* "usou a variável" e "palavras de falha" medem a resposta estar
   errada para o usuário, ou só a forma do código e do texto?
2. **Aviso à plataforma** (4.9). *Pergunta:* para quem, em que formato e com que grau de certeza mínimo um achado entra?
3. **Sucesso em três níveis** (4.5). *Pergunta:* "concluiu a tarefa" é "terminou com resposta final", ou precisa de algo
   sobre a qualidade da resposta, que o trace sozinho não dá?
4. **Ferramentas que respeitam as chamadas do papel** (4.4) **e narração executada como código** (4.3). *Pergunta:* com
   uma execução só na base 2, vale construir a medida agora, ou esperar a base 3 mostrar recorrência?

---

## 4. Próximo, em ordem

Cada item: **contexto curto · o que fazer · tipo · status.** Nada começa sem aprovação.

**Ordem (06/10):** 4.14 (a próxima branch, que inclui o 4.11) → 4.1b na base 1 → os itens em discussão (§3), na ordem
4.1c → 4.5 → 4.4 → 4.3 → 4.6 → 4.8 → 4.9.

### 4.14 Branch `2026-10-06-validacao-kit-base2` — **a fazer, nesta ordem**

1. **Validar o kit na base 2** (máquina de compliance; o Rafael roda e traz contagens) — **prompt pronto:**
   [`maquina2/2026-10-06-prompt-base2-kit.md`](maquina2/2026-10-06-prompt-base2-kit.md) (06/10; sai do repositório
   depois de copiado, como os anteriores):
   - **antes:** replicar na pasta `-second` o que o livro-razão pede: o parquet (`uv sync`, que traz o `pyarrow`;
     `analysis/leitor_trace.py`; as trocas de leitura no `base_pipeline.py`, `checklist.py` e `drill_down.py`; o
     `.gitignore`) e os Ajustes 13–16, com `TRACE` e `BASE_ID` restaurados; reexecutar os notebooks no terminal (a
     pendência do 4.2a); conferir que o Copilot acha o kit no `.claude/` (`/mineracao-candidata` aparece no `/`) e
     apagar as cópias antigas das skills em `.github/`;
   - **o monitoramento primeiro** (`monitorar.py`). Esperado: a `U_nome_inventado` com alerta (118 erros); o
     `U_campo_inexistente` com alerta de crescimento (38 ≥ 3 × 10); a ferramenta concorrente do `final_answer` sem
     alerta;
   - **as minerações:** silenciosas, protocolo e a candidata `U_nome_inventado` (o 4.11), no método novo de leitura.
     Comparar com o publicado (`14`, `11`, as 8 candidatas, os 118 erros) **aqui, fora do kit**.
2. **A `U_texto_literal` na base 1, no método novo:** leitura aberta, o gate da lista (candidatas: a lição geral "não
   redigite numa string um texto que já está numa variável" e os dois eixos "o que é o texto" × "o que quebrou a
   string"), leitura fechada em ≥ 20 outros casos. Conferir à parte o papel que responde em JSON (sinal de harness?) e
   o dicionário mal formado (falso positivo da classificação?).
3. **Skill de resíduo:** antes, o racional e o procedimento saem do `01` (os dois baldes de resíduo) e do `03` (Frente 3;
   §1.16) para docs próprios; depois a skill, a auditoria independente e o encontro.
4. **Skill de erro crítico:** antes, o racional de método e o procedimento (hoje só existe a decisão: `01`, 4.6).
   Depende do 4.4.
5. **Skill de apresentação para stakeholders** (formato a decidir: HTML ou slides). Mostra os resultados, os racionais e
   as decisões de negócio e de produto. A decidir antes: o formato e o público; que ela leia só documentos versionados,
   nunca o trace, com o `varrer_pii.py`; cada número com o documento e o commit de onde vem; o conteúdo (a genealogia
   erro → memória, as candidatas e a situação de cada uma, os sinais de harness, o monitoramento, as decisões
   pendentes).

**Onde cada mineração está, em documentos:**

| Mineração | Racional | Procedimento | Relatório | Skill |
|---|---|---|---|---|
| Falhas silenciosas | `13` | `15` | `14` | sim |
| Protocolo do harness | `10` | `12` | `11` | sim |
| Candidatas | `06` §9 (fato sobre a ferramenta) e §10 (hábito do agente), com o `09` | `16` | `07` (nº2/nº10); as outras nos dossiês, git-ignored | sim |
| Resíduo | parcial, no `01` | parcial, no `03` (Frente 3, §1.16) | — | não |
| Erro crítico | só a decisão (`01`, 4.6) | — | — | não |

### 4.11 `U_nome_inventado` — a maior candidata da base 2 *(roda no 4.14, passo 1)*

- **Contexto:** 118 erros na base 2 (5 na base 1). A contagem da rodada 2 mostra 101 num papel, num mês e num modelo:
  parece incidente, e os 17 espalhados sustentam a candidatura (livro-razão Etapa 10d). Na base 1, a unidade junta duas
  lições (dossiê em `resultados/mineracao/U_nome_inventado/`).
- **O que fazer:** `/mineracao-candidata U_nome_inventado` na máquina 2, com as regras da base 1 sem mudança; conferir
  se o ContestacaoCivel já usava o mesmo modelo antes de agosto sem o erro (`drill_down.py protocolo` [8]).
- **Tipo:** medição; pode virar Ajuste (separar o mês na triagem, ou dividir a unidade).

### 4.1b Conferir os sucessos falsos de plataforma — **falta a base 1** (a base 2 fechou: nenhum confirmado)

- **O que fazer:** 2–3 casos do grupo plataforma da base 1 (incluindo a falha no próprio step final,
  `trigger_worker_execution`), lendo o `final_answer` **da mesma chamada** da falha. Sai só sim/não e a contagem.
- **Tipo:** leitura; nenhum código. O 4.1c pode dispensar parte dela.

### 4.1c O sucesso falso conferido pelo `txt_vrvl_locl` (roadmap #24) *(em discussão — §3, item 1)*

- **Contexto:** o [4] só aponta candidatos (é teto). A primeira versão da regra, na base 2, mostrou que o desfecho
  precisa de dois eixos: *usou o dado que faltou?* e *declarou a falha?* (livro-razão Etapa 10d).
- **O que fazer:** para cada candidato, um teste determinístico: a variável que recebeu o retorno no step da falha (AST);
  o valor final dela no `txt_vrvl_locl` ainda é o erro?; ela é usada no código do `final_answer`? Uma função no
  `base_pipeline.py`, uma coluna no `casos.csv` das silenciosas e um `[4b]` no `drill_down.py silenciosas`.
- **Limites:** é o estado final; a coluna está em ~90% das execuções; tem conteúdo de caso (só contagens saem).
- **Tipo:** medição; reduz o teto do [4].

### 4.5 S5 — sucesso em três níveis *(em discussão — §3, item 3)*

- **O que fazer:** por execução e papel: o Python executou × a ferramenta devolveu resultado × a última chamada terminou
  com `final_answer`. Medir quanto o "69/69 com resposta" do `11` muda.
- **Tipo:** medição; pode corrigir um número publicado.

### 4.4 S4 — ferramentas que respeitam as chamadas do papel *(em discussão — §3, item 4)*

- **Contexto:** o `idx` junta as chamadas; isso já induziu uma leitura errada no erro crítico.
- **O que fazer:** (a) `critico` e `protocolo --casos` marcam as fronteiras (TaskStep) e calculam o caminho da chamada
  que morreu, reusando a coluna `chamada` do Ajuste 11; (b) `caminho_dos_criticos()` passa a usar a chamada terminal —
  muda o `criticos.csv` → Ajuste, aprovado à parte.
- **Tipo:** (a) ferramenta; (b) ajuste de regra.

### 4.3 S3 — medir a narração executada como código (M6) nas duas bases (roadmap #39) *(em discussão — §3, item 4)*

- **O que fazer:** nos erros de `U_estado_perdido`, `U_nome_inventado`, `U_texto_solto` e `X_causa_nao_identificada`,
  contar `model_output` com mais de um bloco `<code>` e `code_action` que é fragmento de narração, por base, papel e
  mês, e "logo depois de um `H_bloco_code`".
- **Tipo:** medição. Se for frequente → Ajuste (parte dessas memórias vira sinal de harness).

### 4.6 Erro crítico — investigar a chamada que morreu antes do destino *(decidido em 02/10)*

- **O que fazer:** achar o step que iniciou a cascata da chamada terminal e decidir o destino pela causa (memória,
  prompt ou ferramenta). O que a rodada 2 já respondeu está no `11` §2.5 e no livro-razão Etapa 10d.
- **Depende de:** 4.4. **Tipo:** mudança de método → `10` §5, `03` Frente 3, livro-razão; e a skill de erro crítico
  (4.14, passo 4).

### 4.8 Etapa C — as regras determinísticas da família do protocolo *(depois)*

Regras M1–M6 + notebook `mineracao_protocolo_harness.ipynb`; a família se abre nos mecanismos nas figuras. A regra do M2
já entrou (Ajuste 16). Usa as fronteiras de chamada (4.4).

### 4.9 Aviso à plataforma *(em discussão — §3, item 2)*

Os achados que entrariam: o modo e o modelo; a resposta vazia aceita (M5); o parser que executa narração (M6); a
ferramenta que devolve falha como texto, e o `'DEFAULT'` da calculadora nas duas bases; o passe dict → string JSON entre
`puxa_doc_decisao` e `busca_obf`; o prompt que pede um campo com outro nome (Ajuste 13, nas duas bases); a troca de
modelo sem revalidar (o surto do 4.11 e o do RoteadorCivel); credenciais, APIs e bugs dentro das ferramentas; o
relatório pronto seguido só de `print`.

---

## 5. Backlog — melhorias e o que falta (fora da fila do §4)

Uma linha por item; o detalhe está no ponteiro. Sobe para o §4 quando for a vez (regra de ligação, no topo).

**Abertos que vieram do "Agora" do roadmap (02/10):**

- **Relatório de estudo da taxonomia de erros** — aprofundar a genealogia família por família e o teste de cobertura na
  extração ~1M. → `schema-e-taxonomia-de-erros.md` §7 · `09` §1.1
- **Refazer as auditorias independentes das pastas de evidência §11** — não citá-las como verificação da amostra atual.
  → `03-procedimento-validacao.md` §1.12 · `audit/README.md`

**Deste plano:**

- Etapa 6 — o alarme de cobertura (o gatilho com 1 caso em mês pequeno; a concentração num padrão). (roadmap #34)
- Resíduo da base 1, os parênteses (roadmap #29); achados laterais do caso `repr_colado` (roadmap #35).
- Intake da base 3 (vem em parquet; o 4.10 está feito); OBFCivel jul 30 × 180 s; falso negativo do AgenteProcuracoes;
  escopo de memória em `open-questions`.
- Detectores de comportamento (retorno ignorado, chamada repetida, ferramenta não chamada): o Rafael retoma depois das
  leituras de artigos pendentes. → `13` §6
- Racional genérico das candidatas e do monitoramento já escrito (`06` §10); falta o racional próprio do resíduo e do
  erro crítico (4.14, passos 3 e 4).

**Dados e bases:**

- Dataset de erros da base completa (~1M) via query, com o tutor; leitura em parquet e em lotes pelo 4.10. (roadmap #1)
- O que é `anomesdia` e como cada extração escolheu as linhas. (roadmap #27)
- `cod_vers_aget` como dimensão (destrava a curva por maturidade da ferramenta, #14). (roadmap #25, #14)

**Erro invisível — detectores (alimentam o notebook das falhas silenciosas):**

- Groundedness como presença (tokens tipados do `final_answer` × observações) — o erro de maior impacto do TRAIL.
  (roadmap #2)
- Steps sem erro (91,4% nunca olhados), Instruction Non-compliance, Tool-Skip por papel, Reasoning-action mismatch
  determinístico. (roadmap #3, #4, #5, #6)
- Os 9 detectores do TRAIL e os 5 do ToolScan/ToolFailBench; anomalia de ambiente. (roadmap #12, #13, #16)
- `txt_vrvl_locl` — o contrato real na população (o 4.1c é o primeiro uso). (roadmap #24)

**Método e triagem:**

- Eixo de severidade (`impact`) na triagem — decidir o desenho antes. (roadmap #22)
- Terminologia "unidade / candidata"; split do `nome_nao_definido`; resíduo entre bases por mecanismo. (roadmap #21,
  #23, #33)
- Erro estrutural de argumento de ferramenta (AST × assinatura declarada). (roadmap #7)
- Monitor de composição entre bases — para a operação contínua, não agora. (roadmap #38)

**Memória (camada 2):**

- Candidatos de memória de verdade (`description`/`impact`/`correction_guidance` por método); `memory_payload` no
  `unidades_memoria.json`; gold-standard anotado por especialistas. (roadmap #18, #19, #11)

**Custo, evidência e escrita:**

- Custo por chamada de ferramenta; a subida mensal de tokens. (roadmap #8, #9)
- Evidência por análise para §1–§10 do notebook; correção do "CalculoCivel é o pior por %"; de onde vem o schema da nº2;
  PlanningStep. (roadmap #15, #28, #17, #10)
- Promover MAST e ToolScan/ToolFailBench a leitura própria. (roadmap #20)
