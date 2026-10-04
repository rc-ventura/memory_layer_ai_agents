# Plano atual — o roadmap geral das análises: o que vale, o que está feito, o que vem agora

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](glossario.md).

**Atualizado:** 04/10/2026 · **Branch:** `2026-10-02-consolidacao-unidades` (a partir da `main` com o PR #29,
`dc89992`). O PR #29 (balde invisível) foi auditado e mergeado. A auditoria foi **fechada nas duas bases** em 02/10: as
ressalvas foram resolvidas, o balde invisível ganhou verificação independente (`audit_recompute9`, 0 divergências na
base 1 e na base 2) e saiu o Ajuste 11 (Parte II de `2026-09-trace-law-flow/audit/2026-10-02-auditoria-branch-…md`). Índice do que já foi
auditado: [`2026-09-trace-law-flow/audit/README.md`](2026-09-trace-law-flow/audit/README.md).

**Para que serve:** a **única fonte** do "o que fazer agora", em **qualquer análise**. Tem a fila ativa (§4) e o
backlog geral (§5): as melhorias e o que falta, uma linha por item, com ponteiro para o detalhe. Onde fica o resto:

- o **backlog numerado de cada análise**, com o detalhe dos itens, mora no roadmap dela — hoje
  [`2026-09-trace-law-flow/docs/04-roadmap.md`](2026-09-trace-law-flow/docs/04-roadmap.md). Os números de lá são
  estáveis e citados no projeto todo; aqui eles aparecem como "(roadmap #N)";
- o histórico de cada ajuste e de cada etapa fica no livro-razão ([`pipeline-entre-bases.md`](pipeline-entre-bases.md));
- os números ficam nos relatórios de cada análise.

**Regra de ligação:** quando um item do backlog vira trabalho ativo, ele sobe para a §4 com "(roadmap #N)", e o roadmap
ganha "→ plano-atual 4.x". Quando termina, vai para a §2 com o commit, e é riscado no roadmap.

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
| M1 (resposta final fora do envelope), M2 (ferramenta que concorre com o `final_answer`) | sinal de harness. A ferramenta concorrente do `final_answer` aparece só com a declaração antiga `json_resposta` (dez/2025, nas duas bases). Ela some com `resposta_gerada` (jan/2026), mas são duas janelas de 1.000 execuções: **monitorar, não dar como corrigido** (decisão de 02/10) |
| "o risco à resposta está na plataforma" (o [4]) | **hipótese, não achado**: 0/6 sucessos falsos na leitura da base 2; a falha declarada é uma 3ª categoria (4.1c, S5) |
| M5 (resposta vazia aceita), M6 (narração capturada como código) | achado de harness / plataforma |
| Surto da base 1 (modo) e da base 2 (modelo `gpt-5.6-terra`) | não-memória, achado para a plataforma |
| `U_tipo_retorno`, `U_campo_inexistente` | **continuam memória candidata** — não nascem de falha silenciosa (91–94%, duas bases) |
| `json_invalido` do `busca_obf` (6 e 86) | **dono: o agente** — é o gesto do `U_repr_colado` no canal silencioso (6/6, 86/86); memória **e** sinal de harness: a declaração `textos_decisoes (str)` convida ao `str()`. Testar outra declaração e monitorar na base 3 (decisão de 02/10). Unir os dois canais numa unidade: decidido em 01/10 |
| rótulo do grupo `json_invalido` no `drill_down.py` | **fica "a conferir"** — o grupo é genérico; o `--forma` decide em cada base |
| Base 1, família Protocolo do harness | fechada (5 do managerAgent declarados "não lidos") |

**Decidido e entendido na revisão dos achados da base 2 (02/10, Rafael + Claude, duas rodadas):**

*Decisões:*

- **Ocorrência no balde invisível = a mesma régua do balde visível** (sequência de steps seguidos do mesmo papel com a
  mesma unidade). Ver 4.2b-0.

- **Erro crítico: investigar a chamada que morreu antes de decidir o destino.** Substitui a proposta de "erro crítico →
  sinal de harness direto" (4.6). Motivo: no único caso, o papel foi chamado 4 vezes, e só a última chamada é a
  cascata fatal. É preciso achar o step que a iniciou e decidir pela causa. A leitura do Rafael é que deve ser mais
  memória que sinal de harness, mas isso fica a investigar (o papel do `'DEFAULT'` é hipótese).
- **"Campo inexistente no retorno": destino por base até haver evidência de que é o mesmo erro.** Minerar a base 2. Se
  a essência for a mesma da base 1 (o prompt induz a chave errada), o destino passa a valer para as duas.
- **Alarme de cobertura:** a saída passa a mostrar a concentração — o maior padrão, a taxa sem ele, os meses — para
  separar "ferramenta nova sem regra" de "um incidente" (Etapa 6, roadmap #34).
- **Ferramenta concorrente do `final_answer`:** "monitorar" no lugar de "já corrigido" (tabela acima).
- **Declaração do argumento do `busca_obf`:** memória candidata e sinal de harness ao mesmo tempo (tabela acima).
- **Candidatos a sucesso falso:** examinar **os 24** da base 2, não uma amostra de 6, cruzando a falha da ferramenta, a
  resposta final e o estado final das variáveis (`txt_vrvl_locl`; 4.1c).

*Entendimentos (corrigem ou explicam textos):*

- **Dois caminhos de falha.** Quando a ferramenta falha por dentro, o embrulho dela devolve a falha como texto e o step
  **não** quebra: é a falha silenciosa. Quando o código Python do agente erra (por exemplo, ao tratar esse texto como
  dicionário), há exceção e o step quebra: é o erro visível.
- **Por que a suspeita sobre as memórias de contrato caiu sem a prova perfeita.** A medida conta toda falha silenciosa
  até 3 steps antes no mesmo papel, inclusive as que nada têm a ver com o erro. Então ela conta a mais: é um teto. O
  teto deu 5 de 79 e 3 de 38, e o número real é menor ou igual a isso. A prova perfeita seria o fluxo de dado — a
  variável que recebeu o texto de erro ser a mesma que o erro acessa como dicionário.
- **"Falha declarada" não é família, submecanismo nem unidade.** Ela é um **desfecho** da tarefa depois de uma falha
  real de ferramenta. São quatro desfechos: recuperou (a ferramenta funcionou depois) · não dependia (a resposta não
  precisava do dado, ou veio de outra fonte) · falha declarada (a resposta diz que não conseguiu) · sucesso falso (a
  resposta usa o dado que não veio). Vai numa coluna nova do balde invisível e alimenta o "sucesso em três níveis"
  (4.5).
- **O surto da base 2 é o modelo novo, pelo mecanismo "resposta esvaziada + step vazio aceito".** A causa dentro do
  modelo (raciocínio interno) não é comprovável com o trace. O prompt ambíguo explica a base 1 e o RespostaBacen da
  base 2, não o RoteadorCivel.
- **O "sinal de harness" da família de protocolo só existe nos docs.** No pipeline, a família inteira é uma unidade
  com destino não-memória. Virar regra depende da mineração da família (4.8).
- **O `'DEFAULT'` da calculadora é falha silenciosa de ferramenta (grupo plataforma), não protocolo do harness.** A
  ferramenta devolve um valor sem informação no lugar de um erro com motivo (aviso à plataforma, 4.9). "O agente não
  entende o `'DEFAULT'`" era suposição, sem evidência: virou pergunta a medir no erro crítico.
- **O texto repetido da observação no CalculoCivel (3 de 4)** pertence à investigação do erro crítico, não à da maior
  candidata da base 2.
- **Detectores de comportamento** (retorno ignorado, chamada repetida, ferramenta não chamada): o Rafael retoma depois
  das leituras de artigos pendentes.

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
| **4.2a** — base 2 rodada pelo agente da máquina 2: triagem (479 erros, 8 candidatas, os 6 esperados ✅), `U_repr_colado` visível 18, funil e detectores da §13.7; notebooks não reexecutados inteiros lá | relatório da máquina 2, 02/10 | livro-razão Etapa 10c "Base 2 rodada", §6 |
| **4.1b (base 2)** e **D2** — leitura assistida: 0/6 sucessos falsos; RespostaBacen M1 3, M2 1 (`json_resposta`) | idem | `14` §5, `11` §2.6, `10` §4 M2 |
| `drill_down.py`: stdout em UTF-8 (o `caso` caía no Windows) | (commit do registro da base 2) | — |
| Auditoria de 02/10 fechada (Parte II: contexto → solução → porquê → evidência → verificação) + índice `audit/README.md` | (commit do fechamento) | `audit/` |

| **4.2b / Ajuste 12** — a consolidação: `consolidacao_unidades.ipynb` (§14.x), `REGRAS_INVISIVEL`, as ocorrências dos dois baldes no formato comum, `triagem(..., silenciosas=)`; `U_repr_colado` com os dois canais (base 1: 6 → 12; só ela muda; decisão igual); lição com `json.dumps`; `audit_recompute9` bloco G (0 divergências) | registro de 04/10 | livro-razão Ajuste 12, `09`, `13`, `14` |
| **4.2c** — a triagem (global e por papel) e os gráficos dela saem da esteira para a consolidação (§14.6–14.9); `candidatos_memoria.csv` gravado só lá; `triagem_por_papel(..., silenciosas=)`; `audit_recompute6` lê a parte visível. Muda 1 número: sensibilidade por papel 8 → 7 de 18 | registro de 04/10 | livro-razão Ajuste 12 (complemento), `01` §7, `02` §6, `03` §1.15, `09` |
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
| a seção "Agora" do `04-roadmap.md` | migrada em 02/10: o aberto está no §5 daqui; o roadmap ficou só com o backlog numerado da análise |
| "o [4] da base 1 = 93 sucessos falsos" | teto; só falhas reais: 53/75, ainda teto |
| o [1b] da base 2 "calculado sobre as fotos" | conferido rodando |
| dono do `json_invalido`: "a conferir" / "ler 2–3 casos" | o agente, o gesto do `repr_colado` (duas bases, pelo `--forma`) |
| "o erro do agente se recupera, o de plataforma não" | o `json_invalido` quase sempre se recupera (0/6, **3/86**); argumento do agente 30/41 × 2/6 |
| [4] = 53/75 e 20/116; "o 1º final depois da falha" | **54/75 e 24/116** (Ajuste 11: final no próprio step ou depois, **na mesma chamada**); plataforma 16/19 e **17/22**; conferido nas duas bases |
| "`json_invalido` nunca vira sucesso falso (0/86)" | **3/86** na base 2 — falha e `final_answer` no mesmo bloco |
| `U_repr_colado` na base 2 = 7 erros | **18 em 18 execuções**, só RoteadorCivel (conferido na triagem, 02/10); o 7 era o recorte do Ajuste 2.2 |
| "o risco à resposta está na plataforma" | hipótese: 0/3 na leitura da plataforma, 0/3 no `json_invalido` (falha declarada) |
| "D2: se for M2 com `resposta_gerada`, vira memória por ferramenta" | não é: o único M2 da base 2 tem `json_resposta` (dez/2025); com `resposta_gerada` são M1 |
| triagem da base 2 "não vista depois do 2.2" | vista: 8 candidatas (370/479, 77%); a maior é `U_nome_inventado` (118) |
| "a sobreposição do M1 foi medida avulsa" | `drill_down.py protocolo` [9] (`sobreposicao()`, limiar 0,5 reconstruído) |
| "checagem E da auditoria nº 6 fora de fase" | corrigida (25/33 em out/2025); A–G com 0 divergências |
| regra `'DEFAULT'` do motivo: "só base 2" | `b1 b2` — a mesma calculadora devolve `'DEFAULT'` na base 1 (2×, CalculoCivel) |
| balde invisível "conferido" pela auditoria | era **reexecutado**; conferido de forma independente só desde o `audit_recompute9` |

---

## 4. Próximo, em ordem

Cada item: **contexto · solução · evidência · tipo · status.** Nada começa sem aprovação.

**Ordem sugerida (04/10):** ~~4.2b-0~~, ~~4.2b~~ (Ajuste 12) e ~~4.2c~~ feitos → **4.11** (`U_nome_inventado` na base 2) → 4.1c → S5 → S4 → S3. O 4.10
(parquet) entra antes do intake da base 3. A pendência do 4.2a (reexecutar os notebooks no terminal da máquina 2) vai
na próxima ida lá.

### 4.0 Ressalvas da auditoria de 02/10 — **feito** (`675523b`; §2)

Fechadas A, B, C, D, F e H; G não pede ação; E é o 4.2a. A revisão da auditoria achou mais três coisas. Duas já
estão resolvidas: o **Ajuste 11** e a anotação `'DEFAULT'`. A terceira virou o 4.2b-0. Detalhe e evidência: Parte II
da auditoria.

### 4.1b Conferir os sucessos falsos de plataforma *(base 2 lida em 02/10: 0/6; falta a base 1)*

- **Resultado da base 2 (assistido, 6 casos escolhidos):** plataforma 0/3 (1 não precisava do dado, 2 tiveram outra
  ferramenta); `json_invalido` 0/3, com falha e final no mesmo step e a resposta **declarando a falha**. O [4] é teto
  frouxo. Próximo: a base 1 (3 de plataforma, incluindo o `trigger_worker_execution` do step final) e uma amostra
  **sorteada**, ou direto o 4.1c, que dispensa parte da leitura.

- **Contexto:** o [4] é teto. Plataforma: 16/19 (base 1), 17/22 (base 2, Ajuste 11) terminam em `final_answer` sem a ferramenta ter
  funcionado — o risco à correção da resposta.
- **Solução:** 2–3 casos do grupo plataforma por base (`casos.csv`) → `drill_down.py caso <exec_id> <papel>` → o
  `final_answer` usa um dado que deveria ter vindo da ferramenta? Sai só sim/não e a contagem.
- **Depois do Ajuste 11:** o `casos.csv` das silenciosas tem a coluna `chamada`. Ler o `final_answer` **da mesma
  chamada** da falha, e incluir 1 caso de falha no próprio step final (base 1: `trigger_worker_execution`).
- **Tipo:** leitura; nenhum código.

### 4.1c [4b] — o sucesso falso conferido pelo `txt_vrvl_locl` (roadmap #24) *(proposta; aguarda aprovação; melhoria das falhas silenciosas)*

- **Contexto:** o [4] só olha se **existe** um `final_answer` na mesma chamada sem chamada bem-sucedida da ferramenta no
  meio. Não olha o que a ferramenta devolveu nem o que a resposta usou: por isso é teto, e a confirmação depende da
  leitura assistida (4.1b). O `drill_down.py caso` ainda corta a observação em 400 caracteres e não mostra o
  `action_output` (só com `--json`). Nenhuma medida lê o `txt_vrvl_locl`, o estado final das variáveis do agente por
  papel (`05-schema.md`); hoje só o `tempo` lê, e só o tamanho.
- **Solução:** para cada candidato do [4], um teste determinístico em três partes:
  1. a variável que recebeu o retorno da ferramenta no step da falha (`x = ferramenta(...)`, via AST);
  2. o valor final de `x` no `txt_vrvl_locl[papel]` ainda é `"Error calling tool…"`?
  3. `x`, ou uma variável derivada dela, é usada no código do `final_answer`?

  Os três **sim** contam como sucesso falso **[conferido]**; os casos ambíguos ficam para a leitura. A implementação
  é uma função no `base_pipeline.py`, uma coluna no `casos.csv` das silenciosas e um `[4b]` no `drill_down.py
  silenciosas`, testada na base 1 e depois rodada na máquina 2.
- **Limites:** é o estado **final** (variável sobrescrita, ou papel chamado várias vezes, perde o valor do momento da
  falha); a coluna está presente em ~90% das execuções; tem conteúdo de caso, então só saem contagens e sim/não.
- **Tipo:** medição; não muda número publicado. Reduz o teto do [4] e a dependência de leitura por LLM.

### 4.2a Rodar o balde invisível na base 2 — **prompt entregue ao agente da máquina 2** (passos 1–5 = 4.2a + 4.2b-0 + 4.1b + D2; removido do repo depois de copiado, recuperável em `git show cdd04a1:analysis/maquina2/2026-10-02-prompt-base2.md`) *(**feito** em 02/10, com uma pendência: os dois notebooks não terminaram no editor da máquina 2 e os números saíram da recomputação pelas funções. Reexecutar no terminal — `uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 <notebook>` — para as saídas e figuras embutidas da base 2)*

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

### 4.2d Base 2, rodada 2 — as seis perguntas abertas *(prompt pronto: [`maquina2/2026-10-02-prompt-base2-rodada2.md`](maquina2/2026-10-02-prompt-base2-rodada2.md); aguarda as fotos)*

- **O quê:** reexecutar os dois notebooks no terminal, rodar o `investigacao_achados.py` (colar o print no canal
  visível · nome usado sem ter sido definido · campo inexistente · erro crítico por chamada · desfecho dos 24 candidatos a
  sucesso falso · versões do `busca_obf`) e ler só os casos que a regra não decide, mais uma amostra sorteada.
- **Fecha:** a dúvida sobre os 18 visíveis estarem no `busca_obf`; o que é a maior candidata da base 2; a mineração do
  "campo inexistente"; o papel do `'DEFAULT'` no erro crítico; quantos sucessos falsos existem de fato; o experimento
  natural da declaração do `busca_obf`.

### 4.2b-0 A regra de ocorrência do balde invisível — **decidido (Rafael, 02/10): a mesma régua do balde visível**

- **Contexto:** no visível, ocorrência = cascata × unidade; no invisível, a `ocorrencias.csv` tem uma linha por falha.
  Consolidar sem regra conta o mesmo gesto repetido de jeitos diferentes nos dois canais (auditoria de 02/10, Parte II
  II.3.3).
- **Evidência:** base 1 — 120 falhas em 119 steps e 100 sequências; `json_invalido` 6 = 6 sequências, 0 execuções em
  comum com o `U_repr_colado` visível. **Base 2 (02/10):** 134 falhas em 134 steps e 129 sequências; `json_invalido` 86
  = 86 sequências em 86 execuções, 0 em comum com o visível. Nas duas bases, então, a regra não muda o `json_invalido`.
- **Pendência da base 2 — resolvida (02/10):** o visível da `U_repr_colado` é **18 erros em 18 execuções** (só
  RoteadorCivel: jun 3, jul 10, ago 5), conferido na triagem. O tamanho consolidado é 18 + 86 = **104**, não 93. Com
  as duas bases medidas, a regra de ocorrência (a) ou (b) não muda o canal silencioso. A decisão só pesa nos outros
  grupos (134 steps em 129 sequências na base 2; 119 em 100 na base 1).
- **Decisão (02/10):** ocorrência silenciosa = **sequência de steps consecutivos do mesmo papel com a mesma unidade**,
  exatamente como a cascata do balde visível. A mesma régua nos dois canais é o que permite somar. Entra na
  consolidação (4.2b). Efeito medido: no `json_invalido`, nenhum (6 = 6 e 86 = 86 sequências). Nas silenciosas em
  geral: base 1, 119 steps → 100 sequências; base 2, 134 → 129.
- **Tipo:** decisão de método; entra no 4.2b.


### 4.2b A consolidação — e o `json_invalido` colado entra na `U_repr_colado` (roadmap #26) — **feito** (Ajuste 12, 04/10; base 1 conferida, base 2 no passo 2b do prompt da rodada 2)

- **Contexto:** nas duas bases, as falhas silenciosas do `busca_obf` são o gesto do `repr_colado` — colar o print do
  `puxa_doc_decisao` em vez de passar a variável (6/6, 86/86). **Decidido (Rafael, 01/10): (a)** — uma unidade só, com os
  dois canais.
- **Solução:** `pipeline/consolidacao_unidades.ipynb` + uma função no `base_pipeline.py` que recebe as tabelas de
  ocorrências do visível e do invisível e faz a triagem final, com colunas por canal (visíveis · silenciosas · total).
  Regra do balde invisível, sem nome de ferramenta: `json_invalido` + argumento colado → `U_repr_colado`. A lição ganha
  "converta com `json.dumps`, nunca `str()`". Tokens das silenciosas fora da coluna de tokens da unidade (o custo delas é
  retrabalho, medido no invisível).
- **Esperado:** a decisão da `U_repr_colado` não muda (já é candidata nas duas bases); muda o tamanho — base 1: 6 → 12
  (conferido: sem sequência e sem execução em comum), base 2: 18 → 104 (conferido: sem sequência e sem execução em comum) — e o texto. Na base 1: nenhuma outra unidade se mexe; o notebook da esteira fica idêntico.
- **Evidência:** livro-razão Etapa 10c, "Achado (01/10)".
- **Tipo:** **Ajuste** (muda contagem e texto publicados no `09`).

### 4.2c A triagem e os gráficos de unidade saem da esteira para a consolidação — **feito** (04/10; livro-razão, complemento do Ajuste 12). *Correção do desenho: o 8.5 e o 8.10 ficaram na esteira — o 8.5 é o custo dos erros visíveis e o 8.10 compara papéis, não unidades.*

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

### 4.3 S3 — medir o M6 (narração capturada como código) nas duas bases (roadmap #39) *(aguarda aprovação)*

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

### 4.6 Erro crítico — investigar a chamada que morreu antes do destino *(decidido em 02/10; substitui a proposta de gatilho direto)*

- **Decisão:** erro crítico → investigação obrigatória da **chamada terminal**: achar o step que iniciou a cascata
  dela e decidir o destino pela causa (memória, prompt ou ferramenta). Depende das ferramentas que separam as
  chamadas (4.4).
- **Perguntas abertas do único caso (CalculoCivel, base 2):** o `'DEFAULT'` aparece também nas chamadas 1–3, e elas se
  recuperaram? O pensamento menciona a falha logo depois? A calculadora é chamada de novo? O texto que o modelo
  escreve fora do bloco repete a observação (3 de 4)?
- **Proposta anterior (descartada em 02/10):**
  - sinal de harness → gatilho direto, mesmo com um caso;
  - memória → candidata provisória (não ativa até reaparecer).
- **Evidência:** custo de um crítico (~2,1 M tokens); o risco de memória de caso único (o "índice indisponível" era
  invenção do agente).
- **Tipo:** mudança de método → `10` §5, `03` Frente 3, livro-razão.

### 4.7 D2 — RespostaBacen na base 2 — **feito** (02/10, leitura assistida na máquina 2)

- **Resultado:** M1 em 3 (JSON do negócio ×2, pergunta ao usuário; todos com `resposta_gerada` e o prompt pedindo
  formato), M2 em 1 (dez/2025, com `json_resposta`). O M2 segue a declaração `json_resposta` nas duas bases e sumiu
  com a troca para `resposta_gerada` (jan/2026). Destino: sinal de harness, já corrigido; **não** vira memória
  (`10` §4 M2, `11` §2.6).
- **Pergunta original:** os 4 erros são M2 de novo? Se sim, com a declaração `resposta_gerada` → memória candidata por
  ferramenta (`10` §5).
- **Comandos:** `protocolo --casos RespostaBacen 4`; `grep` da declaração; `metadados_steps.py RespostaBacen`; leitura
  A–D.

### 4.8 Etapa C — mineração da família Protocolo do harness *(depois)*

Regras determinísticas M1–M6 + notebook `mineracao_protocolo_harness.ipynb`. A família se abre nos mecanismos nas
figuras. Usa as fronteiras de chamada (S4).

### 4.10 Ler o trace em parquet — antes do intake da base 3 / extração ~1M *(proposta; aguarda aprovação)*

- **Contexto:** a base 3 vem em **parquet** (Rafael, 02/10). Hoje nada no sistema lê parquet: o pipeline, o
  `drill_down.py` e o `checklist.py` usam `pd.read_csv(TRACE, dtype=str)`; os `audit_recompute1–8` só abrem `.csv.xz`;
  o `audit_recompute9` reconhece `.csv`, `.xz` e `.gz`. O ambiente não tem `pyarrow`.
- **Por que não converter para CSV (só como emergência):** a conversão não trunca, mas pode corromper ou apagar.
  - Colunas aninhadas (struct/list) viram a representação do Python, não JSON. O `json.loads` do `txt_etap_memo` ou
    do `txt_vrvl_locl` falharia, e a execução seria pulada **em silêncio**.
  - Nulo e texto vazio viram a mesma coisa (perde-se, por exemplo, o `content` vazio do M5).
  - Tipos e timestamps mudam de forma (`1.0`, fuso).
  - Na escala de ~1M, o CSV é muitas vezes maior, e o pipeline carrega o trace inteiro na memória.
- **Solução:**
  1. `pyarrow` no `pyproject.toml` (as duas máquinas);
  2. um **leitor único** `ler_trace(caminho, colunas=None)` no `base_pipeline.py`, que decide pelo formato pelo conteúdo do
     arquivo (como o `audit_recompute9`). No parquet, lê só as colunas pedidas e, na escala ~1M, em lotes
     (`iter_batches`);
  3. normalização explícita para o contrato que o código espera: texto em tudo, colunas JSON aninhadas serializadas com
     `json.dumps` (nunca `str()`), nulo continua nulo, data em `AAAA-MM-DD…`;
  4. o `drill_down.py`, o `checklist.py` e os `audit_recompute*` passam a chamá-lo (nos de auditoria, só a abertura do
     arquivo — a lógica independente não muda);
  5. o `checklist.py` (intake) ganha a conferência do formato: tipo de cada coluna, quantos nulos, quantas linhas cujo
     `txt_etap_memo` não parseia (se for > 0, parar).
- **Verificação:** converter o trace da base 1 para parquet (com as colunas JSON como texto **e** como aninhadas) e
  exigir saídas idênticas pelos dois caminhos — `audit_recompute6` e `audit_recompute9` com 0 divergências, CSVs de
  `resultados/` iguais.
- **Tipo:** ferramenta; não muda número. Pré-requisito do intake da base 3 (§5) e da extração ~1M (roadmap #1).

### 4.11 `U_nome_inventado` — a maior candidata da base 2 *(proposta; aguarda aprovação)*

- **Contexto:** na triagem da base 2 (02/10), `U_nome_inventado` é a maior unidade: **118 erros, 112 execuções, 5
  meses, 6 papéis** (na base 1, 5 erros). Ninguém leu nem minerou. É também a 1ª unidade do único erro crítico.
- **Pergunta:** é mesmo nome inventado, ou é (a) uma definição que expirou entre steps (o padrão "def só vale para o
  bloco seguinte" do roadmap #23), (b) a narração executada como código (M6, 4.3), ou (c) um efeito do modelo
  `gpt-5.6-terra` em ago/2026?
- **Solução:** primeiro, contagem determinística na máquina 2: por papel × mês × modelo; quantos são "seguidores" (logo
  depois de outro erro); quantos têm o nome definido com `def` ou atribuição num step anterior do papel (o split do
  roadmap #23); quantos vêm logo depois de um `H_bloco_code`. Depois, a leitura de 3–5 casos, só se as contagens não
  decidirem. Se a unidade se dividir, é **Ajuste**, olhando as duas bases.
- **Tipo:** medição; pode virar Ajuste (mudaria a maior candidata da base 2).

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

## 5. Backlog — melhorias e o que falta (fora da fila do §4)

Uma linha por item; o detalhe está no ponteiro. Sobe para a §4 quando for a vez (regra de ligação, no topo).

**Abertos que vieram do "Agora" do roadmap (02/10):**

- **Relatório de estudo da taxonomia de erros** — aprofundar a genealogia família por família (a Sankey está pronta
  desde 21/09) e o teste de cobertura na extração ~1M. → `schema-e-taxonomia-de-erros.md` §7 · `09` §1.1
- **Refazer as auditorias independentes das pastas de evidência §11** — os `relatorio_independente.md` e os
  meta-relatórios 11.1–11.10 auditaram a amostra de antes de 23/09; não citá-los como verificação da amostra atual. →
  `03-procedimento-validacao.md` §1.12 · `audit/README.md`

**Deste plano (já estavam aqui):**

- Etapa 6 — o alarme de cobertura (o gatilho com 1 caso em mês pequeno; a concentração num padrão). (roadmap #34)
- Resíduo da base 1, os parênteses (roadmap #29); achados laterais do caso `repr_colado` (roadmap #35).
- Intake da base 3 (vem em parquet: depende do 4.10); OBFCivel jul 30 × 180 s; falso negativo do AgenteProcuracoes; escopo de memória em
  `open-questions`.

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
