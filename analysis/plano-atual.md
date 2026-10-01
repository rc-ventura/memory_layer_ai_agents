# Plano atual — o que vale, o que está feito, o que vem agora

**Atualizado:** 01/10/2026 · **Branch:** `2026-09-28-mineracao-base2` (PR #29)

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

---

## 4. Próximo, em ordem

Cada item: **contexto · solução · evidência · tipo · status.** Nada começa sem aprovação.

### 4.1 O `json_invalido` do `busca_obf` entra no `U_repr_colado`? *(decisão do Rafael)*

- **Contexto:** nas duas bases, as falhas silenciosas do `busca_obf` são o mesmo gesto do `repr_colado` — colar o print
  do `puxa_doc_decisao` em vez de passar a variável (6/6, 86/86). Na base 2 o canal silencioso é ~12× o visível (86 × 7).
- **Opções:**
  - (a) canal silencioso da `U_repr_colado`: a unidade conta as duas saídas e a lição ganha "converta com `json.dumps`,
    nunca `str()`" → **Ajuste próprio** (muda contagem e texto da unidade, e o `09`);
  - (b) unidade separada, ligada à `U_repr_colado` pelo mecanismo.
- **Evidência:** livro-razão Etapa 10c, "Achado (01/10)".
- **Tipo:** mudança de método.

### 4.1b Conferir os sucessos falsos de plataforma *(Rafael roda; aguarda aprovação)*

- **Contexto:** o [4] é teto. Plataforma: 16/19 (base 1), 16/22 (base 2) terminam em `final_answer` sem a ferramenta ter
  funcionado — o risco à correção da resposta.
- **Solução:** 2–3 casos do grupo plataforma por base (`casos.csv`) → `drill_down.py caso <exec_id> <papel>` → o
  `final_answer` usa um dado que deveria ter vindo da ferramenta? Sai só sim/não e a contagem.
- **Tipo:** leitura; nenhum código.

### 4.2 Criar o conjunto das falhas silenciosas *(proposta; aguarda aprovação)*

- **Contexto:** a análise das falhas silenciosas (Etapa 10c) mora hoje no livro-razão. Pela decisão da §1, ela ganha
  notebook e docs próprios.
- **Solução:**
  - `pipeline/falhas_silenciosas.ipynb` (§13.x), chamando `falhas_silenciosas()` e `motivo_da_falha()`;
  - `docs/13-racionais` (por que a fonte de erros não pode ser só a exceção; o contrato da plataforma; os 6 grupos);
  - `docs/14-relatorio` (base 1 e base 2);
  - `docs/15-procedimento` (comandos, o que sai da máquina 2, como validar regras nas duas bases);
  - o §7 atual do notebook da esteira (Result-Ignore/RAC/Tool-Skip) migra para cá, como o item 26 já previa —
    **ponto de corte a decidir**.
- **Evidência:** item 26 (22/09); Etapa 10c (01/10).
- **Tipo:** organização + documentação; não muda número publicado.

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
  - (a) `critico` e `protocolo --casos` marcam as fronteiras (TaskStep) e calculam o caminho da chamada que morreu;
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
- **ferramenta devolve falha como texto** (exceção tipada ou resultado estruturado);
- o passe dict → string JSON entre `puxa_doc_decisao` e `busca_obf`: o tipo `(str)` convida ao `str(...)` (aceitar dict, ou
  a declaração pedir `json.dumps`);
- "Wrong credentials", APIs, bugs dentro das ferramentas;
- relatório pronto seguido só de `print`.

---

## 5. Fora do plano por enquanto

- Etapa 6 (alarme de cobertura; o gatilho com 1 caso em mês pequeno);
- itens 29, 35, 36;
- intake da base 3;
- OBFCivel jul 30 × 180 s;
- falso negativo do AgenteProcuracoes;
- escopo de memória em `open-questions`;
- merge do PR #29;
- remover o worktree local `wt-mineracao`.
