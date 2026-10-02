# Plano atual — o que vale, o que está feito, o que vem agora

**Atualizado:** 02/10/2026 (noite) · **Branch:** `2026-10-02-consolidacao-unidades` (a partir da `main` com o PR #29,
`dc89992`). O PR #29 (balde invisível) foi auditado e mergeado. A auditoria foi **fechada na base 1** em 02/10: as
ressalvas foram resolvidas, o balde invisível ganhou verificação independente (`audit_recompute9`, 0 divergências) e
saiu o Ajuste 11 (Parte II de `2026-09-trace-law-flow/audit/2026-10-02-auditoria-branch-…md`). Índice do que já foi
auditado: [`2026-09-trace-law-flow/audit/README.md`](2026-09-trace-law-flow/audit/README.md).

**Para que serve:** a **única fonte** do "o que fazer agora". O histórico de cada ajuste e de cada etapa continua no
livro-razão ([`pipeline-entre-bases.md`](pipeline-entre-bases.md)); os números, nos relatórios de cada análise. Quando
algo daqui for feito, ele vai para a §2 com o commit, e o detalhe para o livro-razão.

---

## 1. O que vale (decidido)

**Regras de trabalho:**

- **Uma solução por vez.** Eu apresento a solução — contexto, solução, argumento com evidência, tipo da mudança — e
  espero a aprovação. Depois executo, verifico na base 1, commito e digo o que o Rafael roda na máquina 2.
- **Regra nova só olhando as duas bases.** Escrever uma regra com uma base só cria regra específica dela (Ajuste 7; o
  S2b foi escrito assim, com cada palavra-chave anotando a base de origem).
- **Leitura por LLM é "assistida".** Os relatórios feitos com LLM na máquina 2 entram como hipótese; o que foi conferido
  de forma determinística (AST, regex reproduzida, tipo no namespace, contagem) é marcado como **conferido**. Nenhum LLM
  no caminho da classificação.
- **Da máquina 2 só saem** contagens, nomes de papel, ferramenta e modelo, hashes, sim/não, tamanhos, tokens e motivos
  mascarados. Nunca texto de caso nem `exec_id`.

**Decisões de organização:**

- **Cada análise com método próprio ganha o seu conjunto:** notebook + racionais + relatório + procedimento.
  - Família Protocolo do harness → `docs/10-`, `11-`, `12-…-protocolo-harness.md`.
  - **Falhas silenciosas / erro invisível → notebook próprio e docs `13-racionais`, `14-relatorio`,
    `15-procedimento-falhas-silenciosas.md`** (decisão de 01/10). Isso confirma o item 26 do roadmap (22/09) e troca a
    numeração reservada lá (10/11), que colidia com a do protocolo. O notebook da esteira fica só com o erro visível por
    exceção.
- **Três notebooks: visível, invisível, consolidação** (decisão de 01/10). Um funil de detecção único separa os steps
  em dois baldes sem sobreposição — step com exceção → **visível**; sem exceção e com `Error calling tool` no texto →
  **invisível** —, e cada balde é classificado à parte, com regras de entrada próprias (exceção × motivo e forma) e o
  **mesmo catálogo de unidades** (mecanismo → unidade → destino). No fim, os resultados se consolidam.
  - **visível** = o notebook da esteira (não muda);
  - **invisível** = o notebook das falhas silenciosas (docs 13–15);
  - **consolidação** = notebook próprio: junta as tabelas **de ocorrências** dos dois baldes (mesmo formato: `exec_id`,
    papel, `idx`, mês, unidade, canal) e faz a triagem final — recorrência contada sobre a união, nunca somando totais
    (a mesma execução pode ter a unidade nos dois canais). Sem conjunto de docs novo: é a etapa final do método erro →
    memória, documentada no `09`.
- **Código compartilhado:** as funções de medida ficam no `base_pipeline.py` (ou no `analysis/base_utils.py`). O
  notebook e o `drill_down.py` chamam as mesmas.

**Destinos já decididos:**

| Achado | Destino |
|---|---|
| M1 (resposta final fora do envelope), M2 (ferramenta que concorre com o `final_answer`) | sinal de harness |
| M5 (resposta vazia aceita), M6 (narração capturada como código) | achado de harness / plataforma |
| Surto da base 1 (modo) e da base 2 (modelo `gpt-5.6-terra`) | não-memória, achado para a plataforma |
| `U_tipo_retorno`, `U_campo_inexistente` | **continuam memória candidata** — não nascem de falha silenciosa (91–94%, duas bases) |
| `json_invalido` do `busca_obf` (6 e 86) | **dono: o agente** — é o gesto do `U_repr_colado` no canal silencioso (6/6, 86/86); memória **e** aviso à plataforma; unir à unidade é decisão à parte (4.1) |
| rótulo do grupo `json_invalido` no `drill_down.py` | **fica "a conferir"** — o grupo é genérico; o `--forma` decide em cada base |
| Base 1, família Protocolo do harness | fechada (5 do managerAgent declarados "não lidos") |

---

## 2. Feito

| O quê | Commit | Onde está |
|---|---|---|
| Docs da família Protocolo do harness (10/11/12) | `bff1256` | `docs/10-12` |
| `metadados_steps.py` (tokens, finish, campos crus) | `0bd47f1`, `6d0e91c` | `11` §2.3 |
| `drill_down.py critico` | `7c1625d` | `12` |
| **S1** — leitura do erro crítico da base 2 (4 chamadas, M1, **M6**) | `0d71323` | `11` §2.5, `10` §4 |
| **S2** — `falhas_silenciosas()` + `silenciosas` | `78ed696` | livro-razão Etapa 10c |
| `silenciosas --motivos` (mascarado) | `0a69ad0` | idem |
| **S2b** — `motivo_da_falha()`, 6 grupos, regras das duas bases | `41b43b9` | idem |
| Registro das falhas silenciosas (Etapa 10c, item 26, limite no `09`) | `8ddf2c7` | livro-razão, `04`, `09` |
| `silenciosas --forma` (forma do 1º argumento; abre o `str(...)`: colado × montado × variável) | `6123716`, `de5b601` | livro-razão Etapa 10c |
| **4.1** — S2 fechado na base 2: [1b] conferido, [4] por grupo nas duas bases, `json_invalido` = `repr_colado` silencioso | registro de 01/10 | livro-razão Etapa 10c |
| **4.2** — o balde invisível: `falhas_silenciosas.ipynb` (§13.x) + docs 13–15; §7 da esteira migrado inteiro; medidas no `base_pipeline.py` | registro de 01/10 (noite) | livro-razão Etapa 10c, `04` item 26 |
| PR #29 auditado e mergeado; worktree `wt-mineracao` removido; PR #30 (skill `investiga-trace`) fechado sem merge (decisão do Rafael) | `dc89992` · 02/10 | auditoria de 02/10 |
| Auditoria, blueprint das POCs do M1 e diário da semana de 28/09 versionados | `e01238b` | `audit/`, `pocs/`, `research-diary/Out/` |
| **4.0** — ressalvas da auditoria de 02/10: A (checagem E pelo mês da execução; roadmap 36), B (cascata com o `U_estado_perdido`), C (rótulo "chamadas" no `silenciosas`), **D (M1 virou função: `sobreposicao()`, `protocolo` [9])**, F (cabeçalho do livro-razão), H (worktree da auditoria removido) | `675523b` | auditoria de 02/10, Parte II |
| **Ajuste 11** — o [4] conta a falha no próprio step final e respeita a fronteira de chamada; base 1 53/75 → 54/75 | `675523b` | livro-razão §3, `13` §4, `14` §5 |
| `audit_recompute9.py` — verificação independente do balde invisível (0 divergências na base 1; roda na base 2) | `675523b` | `audit/README.md` |
| Auditoria de 02/10 fechada na base 1 (Parte II: contexto → solução → porquê → evidência → verificação) + índice `audit/README.md` | (commit do fechamento) | `audit/` |

---

## 3. O que ficou velho (stale) — e o que vale agora

| Foi dito/registrado | Vale agora |
|---|---|
| "a medida das falhas silenciosas vira uma célula do notebook da esteira" | **notebook separado** (§1) |
| "4 ciclos do mesmo loop desde o idx 20; morte por 25 erros" (CalculoCivel) | 4 chamadas do papel; a morte é da 4ª, com 11 erros (`11` §2.5) |
| "versão 1 / versão 2 do `resposta_final`" | o nome do argumento: `resposta_gerada` / `json_resposta` (o número era ordem de steps) |
| "o `o4-mini` erra mais" | sem base: é o único modelo do papel |
| "catálogo M1–M5" | M1–M6 |
| item 26: docs `10-/11-…-falhas-silenciosas.md` | `13`/`14`/`15` |
| arquivo de plano fora do repo; §5 do livro-razão ("Próximas etapas", 25/09) | **este arquivo** |
| "o [4] da base 1 = 93 sucessos falsos" | teto; só falhas reais: 53/75, ainda teto |
| o [1b] da base 2 "calculado sobre as fotos" | conferido rodando |
| dono do `json_invalido`: "a conferir" / "ler 2–3 casos" | o agente, o gesto do `repr_colado` (duas bases, pelo `--forma`) |
| "o erro do agente se recupera, o de plataforma não" | só o `json_invalido` se recupera (0/6, 0/86); argumento do agente 30/41 × 2/6 |
| [4] base 1 = 53/75; "o 1º final depois da falha" | **54/75** (Ajuste 11: final no próprio step ou depois, **na mesma chamada**); base 2 (20/116) a reconferir |
| "a sobreposição do M1 foi medida avulsa" | `drill_down.py protocolo` [9] (`sobreposicao()`, limiar 0,5 reconstruído) |
| "checagem E da auditoria nº 6 fora de fase" | corrigida (25/33 em out/2025); A–G com 0 divergências |
| regra `'DEFAULT'` do motivo: "só base 2" | `b1 b2` — a mesma calculadora devolve `'DEFAULT'` na base 1 (2×, CalculoCivel) |
| balde invisível "conferido" pela auditoria | era **reexecutado**; conferido de forma independente só desde o `audit_recompute9` |

---

## 4. Próximo, em ordem

Cada item: **contexto · solução · evidência · tipo · status.** Nada começa sem aprovação.

**Ordem sugerida:** **4.2a** (Rafael, máquina 2 — agora com o `audit_recompute9` e o Ajuste 11) → **4.2b-0** (regra
de ocorrência do balde invisível) → 4.2b (Ajuste) → 4.2c → S4(a) → S5 → D2. O 4.1b vai em paralelo, na mesma ida à
máquina 2.

### 4.0 Ressalvas da auditoria de 02/10 — **feito** (`675523b`; §2)

Fechadas A, B, C, D, F e H; G não pede ação; E é o 4.2a. A revisão da auditoria achou mais três coisas. Duas já
estão resolvidas: o **Ajuste 11** e a anotação `'DEFAULT'`. A terceira virou o 4.2b-0. Detalhe e evidência: Parte II
da auditoria.

### 4.1b Conferir os sucessos falsos de plataforma *(Rafael roda; aguarda aprovação)*

- **Contexto:** o [4] é teto. Plataforma: 16/19 (base 1), 16/22 (base 2) terminam em `final_answer` sem a ferramenta ter
  funcionado — o risco à correção da resposta.
- **Solução:** 2–3 casos do grupo plataforma por base (`casos.csv`) → `drill_down.py caso <exec_id> <papel>` → o
  `final_answer` usa um dado que deveria ter vindo da ferramenta? Sai só sim/não e a contagem.
- **Depois do Ajuste 11:** o `casos.csv` das silenciosas tem a coluna `chamada`. Ler o `final_answer` **da mesma
  chamada** da falha, e incluir 1 caso de falha no próprio step final (base 1: `trigger_worker_execution`).
- **Tipo:** leitura; nenhum código.

### 4.2a Rodar o balde invisível na base 2 *(Rafael roda; aguarda aprovação)*

- **Contexto:** o notebook novo rodou na base 1; na base 2 só rodaram os comandos do `drill_down.py`. Faltam o funil por
  step (sobreposição = 0), os detectores da §13.7 e a tabela de ocorrências (entrada da consolidação).
- **Comandos (máquina 2):** copiar para a `-second` `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`), `drill_down.py`,
  `falhas_silenciosas.ipynb`, o notebook da esteira e `audit/scripts/audit_recompute9.py` →
  ```
  uv run jupyter nbconvert --to notebook --execute --inplace falhas_silenciosas.ipynb
  uv run python drill_down.py silenciosas
  uv run python drill_down.py protocolo
  uv run python ../audit/scripts/audit_recompute9.py --base base2 --trace ../data/<trace>.csv.xz \
         --em resultados/erros_mecanismo.csv --fonte base_pipeline.py
  ```
- **Trazer (fotos; só contagens):** (1) a saída inteira do `audit_recompute9` — os blocos A–C e E têm o publicado da
  base 2 como expectativa, e qualquer `DIVERGE` vira item; (2) o **[4] novo** por grupo (bloco D), que substitui o
  20/116 no `14` §5; (3) o bloco F (`json_invalido` em sequências; execuções em comum com o `U_repr_colado` visível) —
  a entrada do 4.2b-0; (4) o `protocolo` [9] (M1 medido na base 2); (5) as §13.1 e §13.7 do notebook. Os números de
  [1]–[3] devem repetir os das fotos de 01/10.
- **Tipo:** confirmação; nenhum código. Fecha a ressalva E da auditoria de 02/10 e o Ajuste 11 na base 2.

### 4.2b-0 A regra de ocorrência do balde invisível *(antes do 4.2b; aguarda os dados do 4.2a)*

- **Contexto:** no visível, ocorrência = cascata × unidade; no invisível, a `ocorrencias.csv` tem uma linha por falha.
  Consolidar sem regra conta o mesmo gesto repetido de jeitos diferentes nos dois canais (auditoria de 02/10, Parte II
  II.3.3).
- **Evidência:** base 1 — 120 falhas em 119 steps e 100 sequências; `json_invalido` 6 = 6 sequências, 0 execuções em
  comum com o `U_repr_colado` visível. Ou seja, "6 → 12" vale com as duas regras. Base 2: a sonda F do 4.2a.
- **Solução (a decidir com os dados das duas bases):** (a) ocorrência silenciosa = sequência de steps consecutivos do
  mesmo papel com a mesma unidade, como no visível; ou (b) uma por falha, declarando a diferença. Recomendo **(a)**: a
  mesma régua nos dois canais é o que permite somar.
- **Tipo:** decisão de método; entra no 4.2b.


### 4.2b A consolidação — e o `json_invalido` colado entra na `U_repr_colado` *(Ajuste; depois do 4.2)*

- **Contexto:** nas duas bases, as falhas silenciosas do `busca_obf` são o gesto do `repr_colado` — colar o print do
  `puxa_doc_decisao` em vez de passar a variável (6/6, 86/86). **Decidido (Rafael, 01/10): (a)** — uma unidade só, com os
  dois canais.
- **Solução:** `pipeline/consolidacao_unidades.ipynb` + uma função no `base_pipeline.py` que recebe as tabelas de
  ocorrências do visível e do invisível e faz a triagem final, com colunas por canal (visíveis · silenciosas · total).
  Regra do balde invisível, sem nome de ferramenta: `json_invalido` + argumento colado → `U_repr_colado`. A lição ganha
  "converta com `json.dumps`, nunca `str()`". Tokens das silenciosas fora da coluna de tokens da unidade (o custo delas é
  retrabalho, medido no invisível).
- **Esperado:** a decisão da `U_repr_colado` não muda (já é candidata nas duas bases); muda o tamanho — base 1: 6 → 12
  (conferido: sem sequência e sem execução em comum), base 2: 7 → até 93 (depende do 4.2b-0) — e o texto. Na base 1: nenhuma outra unidade se mexe; o notebook da esteira fica idêntico.
- **Evidência:** livro-razão Etapa 10c, "Achado (01/10)".
- **Tipo:** **Ajuste** (muda contagem e texto publicados no `09`).

### 4.2c A triagem e os gráficos de unidade saem da esteira para a consolidação *(proposta do Rafael, 01/10; depois do 4.2b)*

- **Contexto:** a esteira ainda faz a triagem das unidades (§9) — uma decisão sobre unidades, que depois do 4.2b depende
  dos dois baldes.
- **Solução (desenho a aprovar quando chegar a vez):**
  - **vai para a consolidação:** a §9 inteira (triagem global e por papel, sensibilidade, `candidatos_memoria.csv`) e os
    gráficos que terminam em unidade ou destino (8.5 tokens por mecanismo aprendível, 8.10 prioridade por critério, a
    Sankey da genealogia do `09`);
  - **fica na esteira:** o que descreve o balde visível — famílias, sintoma, custo, propagação, posição, Lorenz, sucesso
    (8.0–8.4, 8.6–8.9, 8.11, 8.12);
  - numeração nova na consolidação (§14.x); na esteira, a §9 vira ponteiro (número nunca reutilizado);
  - mesmos nomes e caminhos dos arquivos em `resultados/` (o `drill_down.py` e a mineração os leem);
  - docs: o `09` passa a descrever a consolidação como etapa final; `01`/`02` com os links trocados.
- **Tipo:** organização; não muda número. Na máquina 2, a ordem de rodar passa a ser esteira → invisível → consolidação.

### 4.3 S3 — medir o M6 (narração capturada como código) nas duas bases *(aguarda aprovação)*

- **Contexto:** no erro crítico, `U_estado_perdido`, `U_nome_inventado`, `U_texto_solto` e `X_causa_nao_identificada`
  eram o harness executando narração (`10` §4 M6).
- **Solução:** nos erros dessas 4 unidades, contar:
  - `model_output` com mais de um bloco `<code>` ou delimitadores no pensamento;
  - `code_action` que é fragmento de narração.

  Por base, papel e mês, e "logo depois de um `H_bloco_code`".
- **Evidência:** a regex reproduzida em 12 steps (relatório da máquina 2); os 7 `U_texto_solto` depois do incidente de
  out/2025 na base 1.
- **Tipo:** medição. Se for frequente → Ajuste próprio (parte dessas memórias vira sinal de harness).

### 4.4 S4 — ferramentas que respeitam as chamadas do papel *(aguarda aprovação)*

- **Contexto:** o `idx` conta as chamadas juntas; o `critico` e a seção 2 do `protocolo --casos` misturaram as
  chamadas e induziram a leitura errada.
- **Solução:**
  - (a) `critico` e `protocolo --casos` marcam as fronteiras (TaskStep) e calculam o caminho da chamada que morreu —
    reusar a contagem de `TaskStep` que o Ajuste 11 pôs em `falhas_silenciosas()` (coluna `chamada`; base 1: 491 de
    2.252 papéis têm mais de uma chamada);
  - (b) `caminho_dos_criticos()` passa a usar a chamada terminal — muda o `criticos.csv` → **Ajuste**, aprovado à parte.
- **Tipo:** (a) ferramenta; (b) ajuste de regra.

### 4.5 S5 — sucesso em três níveis *(aguarda aprovação)*

- **Contexto:** o `txt_rspa_fina` guardou a resposta da 3ª chamada numa execução que morreu na 4ª; o `protocolo` [5]
  diz "69/69 com resposta".
- **Solução:** por execução e papel: o Python executou × a ferramenta devolveu resultado (S2) × a tarefa foi concluída
  (a última chamada terminou com `final_answer`). Medir quanto o "69/69" muda.
- **Tipo:** medição; pode corrigir um número publicado.

### 4.6 S6 — erro crítico como gatilho de destino *(decisão do Rafael)*

- **Proposta:**
  - sinal de harness → gatilho direto, mesmo com um caso;
  - memória → candidata provisória (não ativa até reaparecer).
- **Evidência:** custo de um crítico (~2,1 M tokens); o risco de memória de caso único (o "índice indisponível" era
  invenção do agente).
- **Tipo:** mudança de método → `10` §5, `03` Frente 3, livro-razão.

### 4.7 D2 — RespostaBacen na base 2 *(aguarda aprovação)*

- **Pergunta:** os 4 erros são M2 de novo? Se sim, com a declaração `resposta_gerada` → memória candidata por
  ferramenta (`10` §5).
- **Comandos:** `protocolo --casos RespostaBacen 4`; `grep` da declaração; `metadados_steps.py RespostaBacen`; leitura
  A–D.

### 4.8 Etapa C — mineração da família Protocolo do harness *(depois)*

Regras determinísticas M1–M6 + notebook `mineracao_protocolo_harness.ipynb`. A família se abre nos mecanismos nas
figuras. Usa as fronteiras de chamada (S4).

### 4.9 Aviso à plataforma *(quando a base 2 fechar)*

- modo/modelo;
- M5 (resposta vazia aceita);
- M6 (o parser concatena blocos e executa narração);
- **ferramenta devolve falha como texto** (exceção tipada ou resultado estruturado); a calculadora
  `calculo_correcoes_monetarias` devolve `'DEFAULT'` como resultado **nas duas bases**;
- o passe dict → string JSON entre `puxa_doc_decisao` e `busca_obf`: o tipo `(str)` convida ao `str(...)` (aceitar dict, ou
  a declaração pedir `json.dumps`);
- "Wrong credentials", APIs, bugs dentro das ferramentas;
- relatório pronto seguido só de `print`.

---

## 5. Fora do plano por enquanto

- Etapa 6 (alarme de cobertura; o gatilho com 1 caso em mês pequeno);
- itens 29 e 35 (o 36 foi fechado em 02/10);
- intake da base 3;
- OBFCivel jul 30 × 180 s;
- falso negativo do AgenteProcuracoes;
- escopo de memória em `open-questions`.
