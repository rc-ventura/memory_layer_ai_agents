# Plano atual — o roadmap geral das análises: o que vale, o que está feito, o que vem agora

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](glossario.md).

**Atualizado:** 06/10/2026 (próxima branch: 4.14) · **Base 2 finalizada** (rodada 2, livro-razão Etapa 10d) · **Branch:** `2026-10-02-consolidacao-unidades` (a partir da `main` com o PR #29,
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

**Decidido em 05/10 (Rafael) — o kit de mineração e a primeira investigação ao vivo:**

*Sobre o kit (4.12):*

- **Minerar não é comparar com relatório.** Uma skill de mineração lê as tabelas que o pipeline produziu para a base e
  descreve o que elas mostram; não compara com relatório publicado nem com outra base. A verificação é interna: uma
  **auditoria independente rodando em paralelo** (outro agente, outra implementação, direto do trace), confrontada com
  as tabelas por script, mais as conferências que valem em qualquer base.
- **Nenhuma afirmação sem evidência.** Todo relatório ou dossiê de mineração traz, junto de cada afirmação, o comando
  que reproduz o número, a tabela derivada com o filtro e, nos achados que viram decisão ou parada, os casos crus
  (`exec_id`, o cru, o recorte). O relatório é a análise final: quem o lê não pode precisar ir buscar evidência.
- **Sigilo por script, não por máscara.** O relatório completo, com identificadores, fica no ambiente do trace; a
  versão que sai troca os identificadores por `caso-N` por script (`versao_para_sair.py`) e passa no varredor.
- **Camada de investigação com LLM, depois do determinístico:** o LLM lê uma amostra escolhida por regra, um segundo
  leitor relê às cegas, e a hipótese só vira número como regra contada por script. A decisão é do pesquisador.
- **As skills são genéricas** (sem base, pasta, unidade nem número) e rodam em qualquer agente que leia `SKILL.md`.

*Sobre a investigação dos 7 erros de dez/2025 no RespostaBacen (base 1):*

- **A conclusão de 30/09 fica confirmada** por um método reproduzível (nota em `11` §1.3): a ferramenta de resposta
  final concorre com a resposta do agente; sinal de harness, já corrigido pela plataforma em jan/2026; não é memória.
- **Os três ajustes de método que ela mostrou estão aprovados** (4.13), para aplicar um de cada vez, com verificação
  na base 1 e registro no livro-razão:
  1. o sinal "muitos tokens para pouco texto" passa a considerar o modelo (modelos de raciocínio gastam assim em todo
     step);
  2. o catálogo ganha o desempate: erro logo depois da ferramenta de resposta final **e** reembrulhado no step
     seguinte conta como resposta final fora do lugar;
  3. a regra encontrada vira a primeira regra automática da família: o step anterior chamou uma ferramenta que se
     apresenta como resposta final (reconhecida pela declaração, não pelo nome), e o texto não reaparece na resposta
     final.
- **A regra de criação de notebook específico (revista em 05/10, sem sorteio):** frequência **e** confiança, ou a
  decisão do Rafael. A aprovação final é sempre dele.
  - **Frequência:** a lição está no Pareto das ocorrências das candidatas, ou aparece na maior parte dos meses
    (`valor_da_licao.py`).
  - **Confiança:** dois leitores às cegas (kappa ≥ 0,6), regras contadas (≥ 90% · ≤ 10%) e laudo do validador.
  - **Reconfirmação:** a cada partição nova da base, as regras são reaplicadas sem mudança. Se caírem, a lição volta à
    investigação.
  - **Por quê:** a base 3 é o log inteiro, e as bases 1 e 2 são recortes de 1.000 registros. Frequência sozinha diz
    que vale a pena, não que a regra está certa.
- **O marcador de cada lição (05/10; revisto em 06/10, abaixo):** frequência (Pareto · presença · os dois · não) ×
  confiança → situação e, nas situações com gate, a decisão do Rafael. Sai do painel `valor_da_licao.py` e fica na tabela do funil do `16`.
  - **Base 1, hoje (06/10):** 6 lições em "prioridade de investigação" (a `U_texto_literal` com "poucos casos" na leitura dupla), e a `U_nome_inventado` em "certa, mas rara: monitorar", em monitoramento.
- **O LLM continua depois do notebook:** ele lê a amostra de cada partição nova (a reconfirmação), investiga a sobra
  que a regra não pega e investiga quando a regra cai.
- **O `caso-N` só existe na versão que sai** da máquina do trace. A versão completa guarda os `exec_id`, e o
  `_mapa.csv` volta de um para o outro.
- **Os agentes do kit são disparados da raiz do repositório** (de uma subpasta, ficam parados pedindo permissão para
  o `AGENTS.md`).

**Decidido em 06/10 (Rafael) — a leitura da investigação e o gate, depois do teste na `U_texto_literal` (base 1):**

- **O que o teste mostrou:** uma regra contada acha o mesmo padrão (o relatório final escrito dentro de uma string) em
  132 de 182 erros, mas os dois leitores concordaram em 4 de 8 casos na lição. A lista de lições, escrita antes de ver
  os casos, misturava "o que é o texto" e "o que quebrou a string", e cada leitor respondeu uma. A discordância era da
  lista, não da lição.
- **A leitura passa a ter duas etapas:** primeiro aberta (os dois leitores escrevem a lição e a causa em frase livre),
  depois o **gate da lista** (o Rafael aprova as categorias montadas a partir das frases) e então a leitura fechada às
  cegas, em outros casos, medida por script. Os casos que montam a lista não medem a concordância (divisão por regra
  fixa, sem sorteio).
- **O segundo leitor lê pelo menos 20 casos** (ou todos, se a população é menor). Com menos, a confiança fica "poucos
  casos", e não "passou" ou "falhou".
- **"Os leitores discordam" não é "não há lição".** O painel separa: o padrão existe (regra contada) × a redação da
  lição (os leitores) × várias causas (metade ou mais dos casos em "não há uma lição única").
- **O gate do pesquisador:** nas situações "pronta para notebook", "lição existe, redação em aberto", "várias causas"
  e "certa, mas rara: monitorar", a skill para e traz a lição principal com a cobertura, os leitores lado a lado, o
  resto e as opções. A decisão fica registrada (`registrar_decisao.py`).
- **Dividir a unidade é resultado normal:** a unidade nasce do sintoma, e um sintoma pode ter várias causas. A lição
  pode ser geral com variações por papel (a lição na `description`, os papéis no `scope`).
- **Onde está:** `docs/16` ("A leitura em duas etapas e o gate do pesquisador"), roteiro `candidata` do kit (0.6.0).
- **Monitorar é determinístico:** um registro versionado (`analysis/monitoramento.json`, um só para as pastas de todas
  as bases: linha de base, regras das sub-lições, gatilhos) e o `monitorar.py`, no passo 0 de toda mineração, que para a rodada com alerta. A
  `U_nome_inventado` fica em monitoramento (decisão do Rafael, 06/10), junto com o `U_campo_inexistente` e a
  ferramenta concorrente do `final_answer` (`docs/16` § O monitoramento).
- **A lição do texto longo ainda não vale notebook:** falta a leitura em duas etapas (06/10).

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
| **Base 2 finalizada** (rodada 2, 05/10): as seis perguntas respondidas; consolidação 104 · 104 · 4 · 1 conferida; nenhum sucesso falso confirmado (24/24 declaram a falha); "nome usado sem ter sido definido" concentrado num papel, mês e modelo; o `'DEFAULT'` não mata sozinho; sem experimento natural no `busca_obf` | registro de 05/10 | livro-razão Etapa 10d, `14` §5 |
| **Ajuste 13** — o "campo inexistente" da base 2 também é sinal de harness (38/38 com a chave pedida no prompt); `DESTINO_MINERACAO` aceita várias bases. Base 1 idêntica | registro de 05/10 | livro-razão Ajuste 13 |
| **4.10** — o trace em parquet: leitor único `analysis/leitor_trace.py` (CSV ou um único parquet) no pipeline, `checklist.py` (§0 formato), `drill_down.py` e nos 9 `audit_recompute*` (`--trace`); `pyarrow` no projeto; pandas fixado no texto em Python. Não muda número: base 1 idêntica em CSV, parquet texto e parquet tipado | registro de 05/10 | §4.10, `analysis/README.md` (intake), `audit/README.md` |
| **4.12, etapa 1** — o kit de mineração (`kit-mineracao/`): 3 skills, 3 agentes, 2 prompts e 5 scripts; silenciosas ponta a ponta na base 1 (tudo OK, 0 divergências, CSV = parquet); ponte LLM → regra validada com resposta conhecida (54/54) | registro de 05/10 | §4.12, `kit-mineracao/README.md` |
| **4.12, etapas 2–3 e 0.6.0** — protocolo, investigação e candidatas no kit (5 skills, 4 agentes); Ajustes 14–16; a mineração de candidatas (`docs/16`: parte genérica → funil → parte específica → arquivo final no esquema 0.1; regra de criação de notebook; painel); a leitura em duas etapas, o gate do pesquisador e o monitoramento determinístico (`monitoramento.json`, `monitorar.py`). Validado na base 1; não muda número | `f590038` · `694636b` · `91e9c0a` · `a0fe56c` · `1c36dc2` | §4.12, §4.14, `docs/16`, `kit-mineracao/README.md` |
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

## 3b. Para discutir na próxima branch — o que de fato queremos medir

**Decisão do Rafael (05/10):** os quatro itens abaixo são importantes, mas cada um pode estar medindo outra coisa que não
a que de fato queremos. Por isso nenhum deles é implementado antes de uma discussão própria, item por item, na branch
seguinte. Cada um tem contexto, problema, o que se mediria e por quê — e a pergunta aberta.

### 1. Sucesso falso em dois eixos (detalhe: 4.1c)

- **Contexto:** quando a ferramenta falha calada, o agente pode entregar uma resposta final apoiada num dado que nunca
  chegou — o sucesso falso, que parece sucesso no trace e não deixa rastro.
- **Problema:** a medida de hoje só aponta candidatos (falha real + resposta final, sem a ferramenta ter funcionado no
  meio); não olha o que a resposta usou. Na base 2, 20 lidos e 0 confirmados (24/24 declaram a falha); na base 1, os 54
  candidatos de 75 nunca foram lidos. Ler caso a caso é caro e depende de LLM.
- **O que se mediria:** pelo `txt_vrvl_locl` (o estado final das variáveis do agente por papel), dois eixos — *usou o
  dado que faltou?* (a variável que recebeu o retorno ainda guarda o erro e aparece no código da resposta final) e
  *declarou a falha?* (palavras de falha no texto entregue). Quatro desfechos: repassou o erro · sucesso falso · falha
  declarada · contornou. Limites: é o estado do fim; ~90% das execuções têm a coluna; tem conteúdo de caso (só contagens).
- **Por quê:** se o sucesso falso é raro, o risco das falhas silenciosas é custo (retrabalho), não resposta errada — e o
  destino delas é otimização e aviso à plataforma, não alarme de correção.
- **Pergunta aberta:** "usou a variável" e "palavras de falha" medem o que importa — a resposta estar errada para o
  usuário — ou só a forma do código e do texto?

### 2. Aviso à plataforma (detalhe: 4.9)

- **Contexto:** parte dos achados não é erro do agente: é a plataforma (ferramentas, harness, prompts, escolha de
  modelo) criando a situação em que ele erra. A memória não conserta isso.
- **Problema:** os achados estão espalhados pelo livro-razão e pelos docs, cada um com seu grau de certeza; ninguém da
  plataforma leria lá.
- **O que se produziria:** um texto curto, um item por achado, com evidência, as duas bases e o conserto sugerido (a
  falha devolvida como texto e o `'DEFAULT'`; o passe dict → JSON do `busca_obf`; o prompt que pede um campo com outro
  nome; a resposta vazia aceita; a narração executada; as trocas de modelo sem revalidar).
- **Por quê:** é a terceira saída do método — o sinal de harness — e um entregável concreto; parte desses consertos
  elimina erros na raiz.
- **Pergunta aberta:** para quem, em que formato e com que grau de certeza mínimo um achado entra no aviso?

### 3. Sucesso em três níveis (detalhe: 4.5)

- **Contexto:** o "sucesso" de uma execução mistura três coisas: o Python rodou sem exceção; a ferramenta devolveu
  resultado; a tarefa foi concluída.
- **Problema:** um número publicado pode estar errado por isso — no erro crítico da base 2, a resposta guardada era da
  3ª chamada e a execução morreu na 4ª, e o relatório do protocolo diz "69 de 69 com resposta".
- **O que se mediria:** por execução e papel, os três níveis em separado (sem exceção · ferramenta funcionou · a última
  chamada terminou com resposta final) e quanto o "69/69" muda.
- **Por quê:** a taxa de sucesso é a régua que vai dizer se a memória ajudou; se ela conta como sucesso o que não foi,
  toda comparação antes × depois fica errada.
- **Pergunta aberta:** "concluiu a tarefa" é "terminou com resposta final", ou precisa de algo sobre a qualidade da
  resposta (o que o trace sozinho não dá)?

### 4. Ferramentas que respeitam as chamadas do papel (detalhe: 4.4) e narração executada como código (detalhe: 4.3)

- **Contexto:** um papel pode ser chamado várias vezes na mesma execução (base 1: 491 de 2.252 papéis); a posição dos
  steps junta as chamadas.
- **Problema:** os comandos que investigam o erro crítico e o protocolo misturam as chamadas — e isso já causou uma
  leitura errada ("4 ciclos, 25 erros", quando a cadeia fatal foram 11 erros da 4ª chamada). A medida do sucesso falso
  já foi corrigida (Ajuste 11); as ferramentas de investigação, não.
- **O que se mediria:** (a) os comandos marcam onde cada chamada começa e calculam o caminho da chamada que morreu
  (ferramenta); (b) a tabela dos críticos usa a chamada terminal (Ajuste). Depois, nas duas bases, quantos erros de
  "estado perdido", "texto solto" e "nome usado sem definição" são o harness executando a narração. **Base 2 (relatório
  de 04/10, assistido):** a narração executada existe — 12/12 no CalculoCivel, na execução crítica —, mas numa execução
  só, e no RoteadorCivel 0/5 (contraprova a "vem logo depois de erro de protocolo, logo é narração").
- **Por quê:** todo erro crítico exige investigar a chamada que morreu antes de dar destino (decisão de 02/10); e, se a
  narração executada for frequente, parte das memórias candidatas vira sinal de harness.
- **Pergunta aberta:** com uma execução só na base 2, vale construir a medida agora, ou esperar a base 3 mostrar
  recorrência?

---

## 4. Próximo, em ordem

Cada item: **contexto · solução · evidência · tipo · status.** Nada começa sem aprovação.

**Ordem sugerida (06/10): a próxima branch é o 4.14** (validar o kit na base 2 → a `U_texto_literal` no método novo →
resíduo → erro crítico → apresentação para stakeholders). Antes (05/10): ~~4.2b-0~~, ~~4.2b~~, ~~4.2c~~, ~~4.2a~~, ~~4.2d~~ feitos; base 2 finalizada → **4.11** (`U_nome_inventado` na base 2) → 4.1c → S5 → S4 → S3. ~~4.10~~
(parquet) feito em 05/10. A pendência do 4.2a (reexecutar os notebooks no terminal da máquina 2) vai
na próxima ida lá.

### 4.0 Ressalvas da auditoria de 02/10 — **feito** (`675523b`; §2)

Fechadas A, B, C, D, F e H; G não pede ação; E é o 4.2a. A revisão da auditoria achou mais três coisas. Duas já
estão resolvidas: o **Ajuste 11** e a anotação `'DEFAULT'`. A terceira virou o 4.2b-0. Detalhe e evidência: Parte II
da auditoria.

### 4.1b Conferir os sucessos falsos de plataforma — **base 2 fechada (05/10): nenhum confirmado** (20 lidos; a regra viu 24/24 declarando a falha). *Falta a base 1, que roda aqui.*

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

### 4.1c [4b] — o sucesso falso conferido pelo `txt_vrvl_locl` (roadmap #24) *(**em discussão** — §3b item 1)*

- **Atualização (05/10, rodada 2):** a primeira versão da regra já rodou na base 2, como seção E do
  `investigacao_achados.py`: 24/24 candidatos declaram a falha, 1 "sucesso falso provável" que a leitura derrubou. A
  comparação com a leitura de 04/10 (3 de 18) mostrou o defeito do desenho: as categorias eram exclusivas, e "não
  dependia do dado" e "declarou a falha" valem juntas. **O desfecho passa a ter dois eixos** — *usou o dado que faltou?*
  (estado final + uso no `final_answer`) e *declarou a falha?* (palavras de falha no texto entregue) —, e a função sobe
  para o `base_pipeline.py`, testada na base 1 (onde os casos ainda não foram lidos).

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

### 4.2a Rodar o balde invisível na base 2 — **feito; base 2 finalizada em 05/10** (reexecutar os notebooks no terminal, com cópia íntegra, na próxima ida) — **prompt entregue ao agente da máquina 2** (passos 1–5 = 4.2a + 4.2b-0 + 4.1b + D2; removido do repo depois de copiado, recuperável em `git show cdd04a1:analysis/maquina2/2026-10-02-prompt-base2.md`) *(**feito** em 02/10, com uma pendência: os dois notebooks não terminaram no editor da máquina 2 e os números saíram da recomputação pelas funções. Reexecutar no terminal — `uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 <notebook>` — para as saídas e figuras embutidas da base 2)*

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

### 4.2d Base 2, rodada 2 — as seis perguntas abertas — **feito (05/10; livro-razão Etapa 10d)** *(prompt: [`maquina2/2026-10-02-prompt-base2-rodada2.md`](maquina2/2026-10-02-prompt-base2-rodada2.md))*

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

### 4.3 S3 — medir o M6 (narração capturada como código) nas duas bases (roadmap #39) *(**em discussão** — §3b item 4)*

- **Contexto:** no erro crítico, `U_estado_perdido`, `U_nome_inventado`, `U_texto_solto` e `X_causa_nao_identificada`
  eram o harness executando narração (`10` §4 M6).
- **Solução:** nos erros dessas 4 unidades, contar:
  - `model_output` com mais de um bloco `<code>` ou delimitadores no pensamento;
  - `code_action` que é fragmento de narração.

  Por base, papel e mês, e "logo depois de um `H_bloco_code`".
- **Evidência:** a regex reproduzida em 12 steps (relatório da máquina 2); os 7 `U_texto_solto` depois do incidente de
  out/2025 na base 1.
- **Tipo:** medição. Se for frequente → Ajuste próprio (parte dessas memórias vira sinal de harness).

### 4.4 S4 — ferramentas que respeitam as chamadas do papel *(**em discussão** — §3b item 4)*

- **Contexto:** o `idx` conta as chamadas juntas; o `critico` e a seção 2 do `protocolo --casos` misturaram as
  chamadas e induziram a leitura errada.
- **Solução:**
  - (a) `critico` e `protocolo --casos` marcam as fronteiras (TaskStep) e calculam o caminho da chamada que morreu —
    reusar a contagem de `TaskStep` que o Ajuste 11 pôs em `falhas_silenciosas()` (coluna `chamada`; base 1: 491 de
    2.252 papéis têm mais de uma chamada);
  - (b) `caminho_dos_criticos()` passa a usar a chamada terminal — muda o `criticos.csv` → **Ajuste**, aprovado à parte.
- **Tipo:** (a) ferramenta; (b) ajuste de regra.

### 4.5 S5 — sucesso em três níveis *(**em discussão** — §3b item 3)*

- **Contexto:** o `txt_rspa_fina` guardou a resposta da 3ª chamada numa execução que morreu na 4ª; o `protocolo` [5]
  diz "69/69 com resposta".
- **Solução:** por execução e papel: o Python executou × a ferramenta devolveu resultado (S2) × a tarefa foi concluída
  (a última chamada terminou com `final_answer`). Medir quanto o "69/69" muda.
- **Tipo:** medição; pode corrigir um número publicado.

### 4.6 Erro crítico — investigar a chamada que morreu antes do destino *(decidido em 02/10; substitui a proposta de gatilho direto)*

- **Decisão:** erro crítico → investigação obrigatória da **chamada terminal**: achar o step que iniciou a cascata
  dela e decidir o destino pela causa (memória, prompt ou ferramenta). Depende das ferramentas que separam as
  chamadas (4.4).
- **Respondido na rodada 2 (05/10, Etapa 10d):** o `'DEFAULT'` aparece nas chamadas 1, 2 e 4; as chamadas 1 e 2 se
  recuperaram e terminaram com resposta; na 4ª o pensamento menciona a falha, a calculadora não é chamada de novo e a
  chamada morre (21 steps, 11 erros + o limite, 2,09 M tokens — mais que as outras três somadas). O `'DEFAULT'` é falha
  recorrente da plataforma (vai para o aviso, 4.9), mas não mata sozinho. Em 2 erros da chamada terminal o texto
  repete trechos longos da observação anterior (2.881 e 2.986 caracteres) — hipótese, sem causalidade provada.
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

### 4.10 Ler o trace em parquet — antes do intake da base 3 / extração ~1M — **feito** (05/10; não muda número)

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
- **Feito (05/10):**
  - **Onde ficou o leitor:** em `analysis/leitor_trace.py`, não no `base_pipeline.py`. Os `audit_recompute*`
    não podem importar o pipeline, e assim os dois lados leem pelo mesmo arquivo; o `base_pipeline.py` reexporta o
    `ler_trace`. Há duas interfaces: `ler_trace` (DataFrame, contrato do `read_csv(dtype=str)`) e `abrir_trace`
    (linhas, contrato do `csv.DictReader`, em lotes). Todos os `audit_recompute*` aceitam `--trace`.
  - **Normalização:** texto vazio no nível da coluna vira nulo, como o `read_csv` faz. Data e hora tipadas saem com o
    mesmo texto do CSV, sem os zeros finais da fração.
  - **Achado no caminho:** com o `pyarrow` instalado, o pandas 3 passa a guardar o texto em arrow, e as regex de
    `.str` rodam no RE2 (`\s` não casa o espaço não separável). O `base_pipeline.py` fixa
    `mode.string_storage = "python"`. Na base 1, os dois modos dão o mesmo resultado; a fixação protege as bases
    2 e 3.
  - **Gitignore:** o `.gitignore` não cobria `*.parquet` nem `*.csv.gz`. Agora cobre (PII).
  - **Aninhada na prática:** o JSON da memória da base 1 não vira coluna aninhada (o arrow recusa: tipos mistos no
    mesmo campo). Na prática, a base 3 deve trazê-lo como texto. O caminho aninhado foi testado com dados sintéticos.
- **Verificação (05/10, base 1 convertida em parquet de dois jeitos: tudo texto; tipado, com timestamp, int, coluna
  dicionário e 11 grupos de linhas):**
  - 9/9 `audit_recompute*` com saída byte a byte igual à de antes da mudança, nos três arquivos (CSV, parquet texto,
    parquet tipado); o 6 e o 9 com 0 divergências.
  - Os 5 notebooks, o `checklist.py`, 15 comandos do `drill_down.py`, `metadados_steps.py`,
    `investigacao_achados.py` (removido da `main` depois, no PR #32) e `genealogia_sankey.py` rodaram sem erro nos três.
  - Os 275 arquivos de `resultados/` são iguais nos três; a única diferença é o `_origem.arquivo` dos `crus/`, que
    agora traz o nome do arquivo lido. As saídas das células também são iguais.
  - O checklist sai com código 1 quando uma memória do parquet não parseia (teste com uma linha corrompida).
- **Replicar na máquina 2:**
  1. `uv sync`, que traz o `pyarrow`;
  2. copiar `analysis/leitor_trace.py`;
  3. no `base_pipeline.py`, `checklist.py` e `drill_down.py` da pasta `-second`, as mesmas trocas de leitura;
  4. o `.gitignore`.

### 4.11 `U_nome_inventado` — a maior candidata da base 2 *(proposta; aguarda aprovação)*

- **Como rodar, desde 05/10:** `/rodada-candidata U_nome_inventado` na máquina 2 (skill `mineracao-candidata`; ela está
  em `investigação:candidata` no funil do `16`). O ensaio na base 1, com 5 erros, foi feito em 05/10 (dossiê em
  `resultados/mineracao/U_nome_inventado/`). As hipóteses (a) a (c) abaixo são as hipóteses de causa do roteiro.

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
- **Resultado da contagem (rodada 2, 05/10, [conferido]):** 101 dos 118 erros são **um papel (ContestacaoCivel), um mês
  (ago/2026), um modelo (`gpt-5.2-2025-12-11`)**; 104 no 1º step da chamada; em 107 o nome só é definido depois; só 1
  vem de chamada anterior (não é a definição que expira) e só 1 vem logo depois de resposta sem bloco de código (não é
  narração). **Hipótese:** o grosso é incidente concentrado (modelo/configuração em agosto, como o do protocolo); a
  memória candidata de verdade são os 17 espalhados. **Próximo:** conferir na próxima ida à máquina 2 se o
  ContestacaoCivel já usava esse modelo antes de agosto sem esse erro (o `drill_down.py protocolo` [8] dá papel ×
  modelo × mês) — se for incidente, separar o mês na triagem é **Ajuste**, olhando as duas bases.

### 4.12 Kit de mineração — skills, agentes, prompts e scripts para rodar cada mineração igual em qualquer ambiente — **etapa 1 feita** (05/10; não muda número)

- **Contexto:**
  - O método de cada mineração está escrito, mas desigual: só o protocolo (`12`) e as silenciosas (`15`) têm
    procedimento no formato pré-condições → passos → conferências.
  - Cada rodada numa base era guiada por um prompt escrito à mão (o protótipo: `git show 9ed5bc9`, o prompt da
    rodada 2).
  - O que o determinístico não fecha (as paradas) era lido sem protocolo.
- **Solução** ([o kit](../.claude/skills/mineracao-base/referencias/kit.md), em `.claude/`; até 06/10, na pasta `kit-mineracao/`): um pacote no formato aberto de skill, que roda no
  Claude Code e no Copilot, em três camadas:
  - **determinístico:** a skill da mineração roda o procedimento da análise e confere com o publicado;
  - **investigação:** o LLM lê uma amostra escolhida por regra fixa, um segundo leitor relê às cegas, e a hipótese
    vira regra contada por script;
  - **decisão:** fica com o pesquisador, a partir de um dossiê.

  O kit não tem nome de base, pasta, unidade nem número. A base fica na análise, e o objeto da rodada é argumento da
  chamada.
- **Etapa 1 (05/10):**
  - as skills `mineracao-base` (Passo 0: pasta, base, conferência de versão por manifesto, intake, sigilo,
    relatório), `mineracao-silenciosas` e `mineracao-investigacao` (roteiro das silenciosas: S1 dono, S2 sucesso
    falso, S3 não reconhecido);
  - os agentes `auditor-independente`, `investigador` e `segundo-leitor`;
  - os prompts `rodada-silenciosas` e `investigar`;
  - os scripts `conferir_versao`, `varrer_pii`, `amostrar`, `testar_regra` e `concordancia`, e o `instalar.py`.
- **Verificação (05/10):**
  - o `conferir_versao` dá igual com `TRACE`/`BASE_ID` trocados, com CRLF e com notebooks executados, e acusa uma
    linha a mais;
  - o `varrer_pii` bloqueia identificador de execução, CPF e número de processo, e passa um relatório limpo;
  - a instalação funciona para claude e para copilot, e a reinstalação não apaga o que não é do kit;
  - a rodada das silenciosas na base 1, seguindo a skill, deu todos os números OK contra o `14` e o `audit_recompute9`
    com 0 divergências, igual em CSV e parquet. As paradas abertas foram S3 (9 não reconhecidas) e S2 (54
    candidatos);
  - a ponte foi validada com resposta conhecida: o `testar_regra` reproduz caso a caso a classificação "declara a
    falha" da rodada 2 (54/54, 100%);
  - o `grep` não acha referência específica no kit;
  - **ainda não feito:** a leitura do `investigador` ao vivo. Ela é a primeira rodada de uso, e quem decide quando é o
    Rafael.
- **Revisão do desenho (05/10, Rafael; kit 0.2.0):**
  - **A mineração não compara com relatório nem com outra base.** Ela lê as tabelas que o pipeline produziu para a
    base e descreve o que elas mostram. Os números são o resultado.
  - **A verificação é interna:** o `auditor-independente` roda em paralelo uma segunda implementação. Para isso, o
    `audit_recompute9` passou a aceitar qualquer `--base` e a gravar as medidas com `--json`; a base 1 saiu idêntica,
    com 0 divergências. O `comparar_auditoria.py` confronta as medidas com as tabelas, e somam-se as conferências
    internas.
  - **Exemplo real** ([`exemplo.md`](../.claude/skills/mineracao-base/referencias/exemplo.md)): uma base nova simulada, do zero, em
    parquet, com `BASE_ID = "base3"` e o dado da base 1. O auditor rodou em paralelo como agente; o encontro deu 19
    medidas iguais e 4 conferências internas OK. As paradas abertas foram S3 (9) e S2 (54).
  - **Revisão das peças:** o roteiro S2 passou a usar a coluna `idx_final_depois`, a que existe numa base nova, e o
    `testar_regra.py` ganhou `--onde`.
- **Evidência em todo relatório (05/10, Rafael; kit 0.3.0):**
  - Cada afirmação leva o comando que reproduz o número e a tabela com o filtro. Cada achado que vira decisão ou
    parada leva os casos crus.
  - O `montar_evidencia.py` escolhe os casos por regra, grava o cru e a visão (pelo `drill_down.py evidencia`) e
    escreve o bloco do relatório, com os `exec_id` e o recorte.
  - O relatório completo fica no ambiente. A versão que sai troca os identificadores por `caso-N`, por script
    (`versao_para_sair.py`).
  - Correção no `drill_down.py evidencia`: o papel chamado literalmente `null` era lido como nulo e quebrava a
    gravação. Não muda número.
  - No exemplo, foram 6 pastas de evidência, com todos os trechos conferidos contra o cru.
- **Etapa 2 — protocolo do harness (05/10; kit 0.4.0):**
  - **Skill `mineracao-protocolo`:** passos do `12`, com evidência por achado, a cobertura por papel (`cobertura.py`)
    e a fronteira de chamada.
  - **Roteiro `protocolo`:** P1 é a camada do surto (o fim do prompt); P2 é o mecanismo de cada caso, no catálogo
    M1–M6.
  - **Auditoria `audit_recompute10.py`:** 0 divergências contra o `11` §1; JSON igual em CSV e parquet.
  - **Mudanças no `drill_down.py protocolo`:** passa a gravar `passos.csv`, `versoes.csv` e `modelos.csv`, e as
    colunas `chamada`/`chamadas_do_papel`. A saída impressa ficou igual.
  - **Relação com outros itens:** as colunas cobrem a conferência da fronteira do `12`; o resto do S4 (4.4) e as
    regras determinísticas M1–M6 (4.8) seguem à parte.
- **Etapa 3 — minerar candidatas a memória (05/10; kit 0.5.0).** Desenho decidido com o Rafael, depois de discutir
  as alternativas: a parte genérica, igual para todas as lições, e depois um funil para a parte específica de cada uma.
  Ficaram de fora um notebook por lição, um genérico com tudo dentro e qualquer agrupamento: a família classifica o
  sintoma e não a lição, e o tipo junta causas diferentes.
  - **`mineracao_generica.ipynb`** (G1–G6): nas 11 candidatas da base 1, os 77 números de recorrência são iguais aos do
    `candidatos_memoria.csv`. A limitação está declarada: a ferramenta do G2 é a chamada no step do erro, e não a
    origem do valor (a nº2 tem a origem em `get_available_documents` 91/96, e outra ferramenta é a mais chamada no
    step).
  - **`audit_recompute6 --json --unidade`:** o encontro dá tudo igual nas 11; a saída sem `--json` ficou igual; o JSON
    é o mesmo em CSV e em parquet.
  - **O funil, no `16`:** a nº2 e a nº10 vão para o notebook específico de hoje, que não mudou (arquivos idênticos) e
    é convertido para o esquema. As outras 9 vão para a investigação. Uma lição fora da tabela para a rodada.
  - **O esquema da memória num lugar só:** `analysis/esquema-memoria.json` (0.1, provisório; os campos do `06` §9
    Passo 8, do TRAIL e do AgentDebug). O `validar_memoria.py` aprova a nº2 e a nº10 convertidas e reprova campo
    obrigatório faltando; um campo novo no esquema vira pendência.
  - **O ciclo de vida da parte específica** e **a regra de criação de notebook:** duas bases com as regras sem mudança,
    ou decisão do Rafael. O agente propõe em `propostas/<u>/`, o agente `validador-de-notebook` dá o laudo, e a
    aprovação é do Rafael. Tudo no `16`, com os diagramas Mermaid; a skill traz os mesmos diagramas
    (`referencias/fluxo.md`).
  - **A primeira parte específica por LLM: a `U_nome_inventado` na base 1, com 5 erros.**
    - **Concordância:** dois leitores às cegas, 5/5 na lição e 5/5 na causa.
    - **A unidade junta duas lições,** separáveis por regra contada:
      - (a) usar como variável um nome visto só no texto impresso: 3 casos, "variável não definida";
      - (b) usar uma função definida numa chamada anterior, que o sandbox recusa: 2 casos, "chamada > 1".
    - **Destino:** (a) memória; (b) em aberto. Se o ambiente guarda variáveis e não funções, é sinal de harness.
    - **Arquivo final aprovado no esquema 0.1;** dossiê e `regras.json` em `resultados/mineracao/U_nome_inventado/`.
    - **Recomendação:** rodar na base 2 com as mesmas regras antes de propor a divisão da unidade.
- **Onde o kit mora, desde 06/10 (decisão do Rafael):** no próprio `.claude/`, versionado; a pasta `kit-mineracao/`
  saiu. O Copilot usa cópias geradas pelo `gerar_copilot.py` (git-ignored). Descrição do kit:
  `.claude/skills/mineracao-base/referencias/kit.md`.
- **Feito em 06/10 (0.6.0, `1c36dc2`):** a leitura em duas etapas, o gate do pesquisador e o monitoramento
  determinístico (bloco "Decidido em 06/10", §1; `docs/16`).
- **Próximas etapas:** na próxima branch, **4.14**.
- **Tipo:** ferramenta; não muda número.

### 4.14 Próxima branch (depois do merge da `2026-10-05-base3-parquet-skills`, 06/10) — **a fazer, nesta ordem**

A branch `2026-10-05-base3-parquet-skills` fecha com o parquet, o kit 0.6.0 (5 skills, 4 agentes, 5 prompts), os
Ajustes 14–16 e o monitoramento, validados na base 1. Rodar o kit na base 2 **não** foi condição para fechar: é a
validação do kit, e entra aqui.

1. **Validar o kit na base 2** (máquina de compliance, com o main atualizado; o Rafael roda e traz contagens):
   - **antes:** replicar o que o livro-razão pede para a máquina 2 (parquet, Ajustes 13–16: `base_pipeline.py` com
     `TRACE` e `BASE_ID` restaurados, a esteira, a consolidação) e gerar as cópias do kit para o Copilot
     (`python .claude/skills/mineracao-base/scripts/gerar_copilot.py .`; o kit em si chega com o `.claude/`);
   - **o monitoramento primeiro** (`monitorar.py`). Esperado: a `U_nome_inventado` com alerta (118 erros: régua,
     cresce; frequência provável), com as duas sub-lições contadas pelas regras; o `U_campo_inexistente` com alerta de
     crescimento (38 ≥ 3 × 10); a ferramenta concorrente do `final_answer` sem alerta (só dez/2025);
   - **as skills:** silenciosas, protocolo e candidata (a `U_nome_inventado`, o 4.11, já no método novo de leitura).
     Comparar com o publicado (`14`, `11`, as 8 candidatas, os 118 erros) **aqui, fora do kit** — as skills não
     comparam com relatório.
2. **A `U_texto_literal` na base 1, no método novo:** leitura aberta pelos dois leitores, o gate da lista (com a lição
   geral proposta — "não redigite numa string um texto que já está numa variável" — e os dois eixos "o que é o texto"
   × "o que quebrou a string" como candidatas), leitura fechada em ≥ 20 outros casos. Conferir à parte as duas pontas
   soltas: o papel que responde em JSON (sinal de harness?) e o dicionário mal formado (falso positivo da
   classificação?). Dossiê em `resultados/mineracao/U_texto_literal/`.
3. **Skill de resíduo** (`mineracao-residuo`): antes, o procedimento sai do `03` Frente 3 para um doc próprio, no
   formato do `12`/`15`/`16`; depois a skill, a auditoria independente e o encontro, como nas outras.
4. **Skill de erro crítico** (`mineracao-critico`): antes, o procedimento e o S4 (4.4, 4.6 — a chamada que morreu
   antes do destino).
5. **Skill de apresentação para stakeholders** (nova; formato a decidir: HTML ou slides). Pega o resultado final até
   o momento e o entrega como uma apresentação: os resultados, os racionais e as decisões de negócio e de produto,
   como se tivessem sido apresentados. A decidir antes de construir:
   - o formato (página HTML versionada × deck de slides × os dois) e quem é o público;
   - de onde ela lê: só de documentos já versionados (`plano-atual`, relatórios, `docs/16`, o painel, o
     `monitoramento.json`), nunca do trace — a versão que sai, com o sigilo de sempre (`varrer_pii.py`);
   - a regra da evidência adaptada: cada número com o documento e o commit de onde vem;
   - o que mostra: a genealogia erro → memória, as candidatas e a situação de cada uma, os sinais de harness para a
     plataforma, o que está em monitoramento e as decisões pendentes.

### 4.13 Ajustes do método do protocolo, vindos da investigação de 05/10 — **aprovados (Rafael, 05/10); aplicar um por vez**

- **Contexto:** a primeira investigação ao vivo do kit (os 7 erros de dez/2025 no RespostaBacen, base 1) reproduziu a
  leitura de 30/09 (`11` §1.3) e mostrou dois pontos fracos do método. Os dois leitores os apontaram sem combinar. Ela
  também achou uma regra determinística para o M2.
- **Solução (um ajuste de cada vez, cada um com aprovação):**
  1. **Sinal de M4 por modelo.** Hoje "tokens de saída muito acima do texto" vale como sinal de que o texto é um resto.
     No `o4-mini` (modelo de raciocínio), a mesma razão aparece nos steps sem erro. Proposta: comparar com a linha de
     base do modelo na própria execução, ou descontar os tokens de raciocínio (o `metadados_steps.py` já os mostra).
     ~~Efeito esperado na base 1: o indeterminado do RespostaBacen volta a M2.~~ **Em suspenso (05/10): a medida
     contradiz a premissa.** Não dá para descontar o raciocínio (o trace da base 1 não traz esse detalhe; `10` §4 M4).
     Comparado com a linha de base do próprio agente na mesma execução, os 2 steps de erro do RespostaBacen com o sinal
     entregam 0,08 caractere por token contra 0,66–0,72 nos steps sem erro: **0,11–0,12 do normal do modelo**. Os
     outros 5 ficam 3 a 5 vezes acima do normal, e todos os erros dos outros papéis ficam entre 0,77 e 1,5. A regra
     relativa conserta o limiar fixo (que marcaria todo step do `o4-mini`), mas **mantém o sinal nesses 2 casos**. O
     indeterminado continua indeterminado. Os 2 casos têm o padrão do M4, que o catálogo dá como só da base 2.
     **Feito (05/10, opção (a) do Rafael; livro-razão Ajuste 15):** a regra relativa entrou, e o achado está no `10` §4 M4.
  2. **Desempate M1 × M2 no catálogo (`10` §4)** — **feito (05/10, livro-razão Ajuste 14).** Proposta: o erro logo depois da ferramenta de resposta final e
     reembrulhado no step seguinte conta como M1, porque o M2 exige `final_answer` ausente ou muito tardio. Isso
     registra a convenção que os dois leitores usaram.
  3. **A regra do M2 nas regras determinísticas da família (4.8)** — **feito (05/10, livro-razão Ajuste 16; 5 de 33, todos no RespostaBacen, = a leitura).** A regra é "o step anterior chamou uma ferramenta
     que se apresenta como resposta final, e o texto não reaparece na resposta final". Para valer em qualquer base, a
     ferramenta é reconhecida pela declaração (nome ou descrição que fala em resposta final), não pelo nome
     `resposta_final`. Ela não muda o total da família, só rotula erros com um mecanismo.
- **Evidência:** dossiê de 05/10 (§6 e §7); regra contada com
  `testar_regra.py … --onde role=RespostaBacen --onde "sobreposicao_final<0.5" --campo-passo code --deslocamento -1 --regex 'resposta_final\s*\('`
  → pega certo 5 · a mais 0 · deixa de pegar 0.
- **Tipo:** ajuste de método (1, 2) e regra nova (3), sem mudar número publicado. Cada um passa pelo livro-razão
  antes de entrar.

### 4.9 Aviso à plataforma *(a base 2 fechou em 05/10; **em discussão** — §3b item 2)*

- modo/modelo;
- M5 (resposta vazia aceita);
- M6 (o parser concatena blocos e executa narração);
- **ferramenta devolve falha como texto** (exceção tipada ou resultado estruturado); a calculadora
  `calculo_correcoes_monetarias` devolve `'DEFAULT'` como resultado **nas duas bases**;
- o passe dict → string JSON entre `puxa_doc_decisao` e `busca_obf`: o tipo `(str)` convida ao `str(...)` (aceitar dict, ou
  a declaração pedir `json.dumps`);
- o contrato do prompt que induz o nome errado do campo (`quebra_sigilo` × `vazamento_sigilo` no RespostaBacen) — **nas
  duas bases** (Ajuste 13);
- a troca de modelo sem revalidar o comportamento: o surto de "nome usado sem ter sido definido" no ContestacaoCivel em
  ago/2026 (`gpt-5.2`), a confirmar (4.11), ao lado do `gpt-5.6-terra` no RoteadorCivel;
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
- Intake da base 3 (vem em parquet: o 4.10 está feito); OBFCivel jul 30 × 180 s; falso negativo do AgenteProcuracoes; escopo de memória em
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
