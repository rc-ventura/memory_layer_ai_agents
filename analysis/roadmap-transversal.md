# Roadmap — itens que atravessam as bases

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](glossario.md).
> O schema deste roadmap (o mesmo de todos) está em [`plano-atual.md`](plano-atual.md). As decisões em vigor, em [`decisoes.md`](decisoes.md).

**Atualizado:** 09/10/2026 · **Branch:** `2026-10-09-roadmaps-schema`.

**O que entra aqui:** o que não pertence a uma base só — o método, o kit, as skills, as medidas que valem para todas e
o que vai à plataforma. O que é de uma base fica no roadmap dela:
[base 1](2026-09-trace-law-flow/docs/04-roadmap.md) · [base 2](2026-09-trace-law-flow-second/docs/04-roadmap.md) ·
[base 3](2026-10-trace-law-flow-third/docs/04-roadmap.md).

**Numeração:** os números são deste arquivo e estáveis. De fora, cite como `transversal #N` (e `b1 #N`, `b2 #N`,
`b3 #N` para os outros). Até 06/10/2026, estes itens eram o §3, o §4 e parte do §5 do plano atual
(`git show e0335aa:analysis/plano-atual.md`); o de-para está no fim de [`plano-atual.md`](plano-atual.md).

## Backlog

**Em discussão — decisão do Rafael (05/10): nenhum é implementado antes de uma discussão própria, item por item.**

- [ ] **#1 · O sucesso falso conferido pelo `txt_vrvl_locl`** (plano antigo 4.1c; `b1 #24`) — *em discussão.* **Contexto:**
  o [4] só aponta candidatos (é teto). A primeira versão da regra, na base 2, mostrou que o desfecho precisa de dois
  eixos: *usou o dado que faltou?* e *declarou a falha?* (livro-razão Etapa 10d). **Pergunta:** "usou a variável" e
  "palavras de falha" medem a resposta estar errada para o usuário, ou só a forma do código e do texto? **O que fazer:**
  para cada candidato, um teste determinístico: a variável que recebeu o retorno no step da falha (AST); o valor final
  dela no `txt_vrvl_locl` ainda é o erro?; ela é usada no código do `final_answer`? Uma função no `base_pipeline.py`, uma
  coluna no `casos.csv` das silenciosas e um `[4b]` no `drill_down.py silenciosas`. **Limites:** é o estado final; a
  coluna está em ~90% das execuções; tem conteúdo de caso (só contagens saem). **Tipo:** medição; reduz o teto do [4].
  **Base 3:** a coluna não vem na extração atual.
- [ ] **#2 · Sucesso em três níveis** (4.5; S5) — *em discussão.* **Pergunta:** "concluiu a tarefa" é "terminou com
  resposta final", ou precisa de algo sobre a qualidade da resposta, que o trace sozinho não dá? **O que fazer:** por
  execução e papel: o Python executou × a ferramenta devolveu resultado × a última chamada terminou com `final_answer`.
  Medir quanto o "69/69 com resposta" do `11` muda. **Tipo:** medição; pode corrigir um número publicado.
- [ ] **#3 · Ferramentas que respeitam as chamadas do papel** (4.4; S4) — *em discussão.* **Contexto:** o `idx` junta as
  chamadas; isso já induziu uma leitura errada no erro crítico. **Pergunta:** com uma execução só na base 2, vale
  construir a medida agora, ou esperar a base 3 mostrar recorrência? **O que fazer:** (a) `critico` e `protocolo
  --casos` marcam as fronteiras (TaskStep) e calculam o caminho da chamada que morreu, reusando a coluna `chamada` do
  Ajuste 11; (b) `caminho_dos_criticos()` passa a usar a chamada terminal — muda o `criticos.csv` → Ajuste, aprovado à
  parte. **Tipo:** (a) ferramenta; (b) ajuste de regra. **Base 3:** a janela da extração não traz a chamada; o
  `step_number` reinicia nas fronteiras (27 de 27 na base 1) — ver `b3 #14`.
- [ ] **#4 · Narração executada como código (M6) nas duas bases** (4.3; S3; `b1 #39`) — *em discussão* (mesma pergunta
  do #3). **O que fazer:** nos erros de `U_estado_perdido`, `U_nome_inventado`, `U_texto_solto` e
  `X_causa_nao_identificada`, contar `model_output` com mais de um bloco `<code>` e `code_action` que é fragmento de
  narração, por base, papel e mês, e "logo depois de um `H_bloco_code`". **Tipo:** medição. Se for frequente → Ajuste
  (parte dessas memórias vira sinal de harness).
- [ ] **#7 · Aviso à plataforma** (4.9) — *em discussão.* **Pergunta:** para quem, em que formato e com que grau de
  certeza mínimo um achado entra? **Os achados que entrariam:** o modo e o modelo; a resposta vazia aceita (M5); o parser
  que executa narração (M6); a ferramenta que devolve falha como texto, e o `'DEFAULT'` da calculadora nas duas bases; o
  passe dict → string JSON entre `puxa_doc_decisao` e `busca_obf`; o prompt que pede um campo com outro nome (Ajuste 13,
  nas duas bases); a troca de modelo sem revalidar (o surto do `b2 #3` e o do RoteadorCivel); credenciais, APIs e bugs
  dentro das ferramentas; o relatório pronto seguido só de `print`.

**Fila ativa:**

- [ ] **#5 · Erro crítico — investigar a chamada que morreu antes do destino** (4.6; S6; `b1 #39`) — *decidido em 02/10.*
  **O que fazer:** achar o step que iniciou a cascata da chamada terminal e decidir o destino pela causa (memória, prompt
  ou ferramenta). O que a rodada 2 já respondeu está no `11` §2.5 e no livro-razão Etapa 10d. **Depende de:** #3.
  **Tipo:** mudança de método → `10` §5, `03` Frente 3, livro-razão; e a skill de erro crítico (#9).
- [ ] **#6 · Etapa C — as regras determinísticas da família do protocolo** (4.8) — *depois.* Regras M1–M6 + notebook
  `mineracao_protocolo_harness.ipynb`; a família se abre nos mecanismos nas figuras. A regra do M2 já entrou (Ajuste
  16). Usa as fronteiras de chamada (#3).
- [ ] **#8 · Skill de resíduo** (4.14, passo 3). Antes, o racional e o procedimento saem do `01` (os dois baldes de
  resíduo) e do `03` (Frente 3; §1.16) para docs próprios; depois a skill, a auditoria independente e o encontro.
- [ ] **#9 · Skill de erro crítico** (4.14, passo 4). Antes, o racional de método e o procedimento (hoje só existe a
  decisão: `01`, #5). **Depende de:** #3.
- [ ] **#10 · Skill de apresentação para stakeholders** (4.14, passo 5; formato a decidir: HTML ou slides). Mostra os
  resultados, os racionais e as decisões de negócio e de produto. A decidir antes: o formato e o público; que ela leia
  só documentos versionados, nunca o trace, com o `varrer_pii.py`; cada número com o documento e o commit de onde vem;
  o conteúdo (a genealogia erro → memória, as candidatas e a situação de cada uma, os sinais de harness, o
  monitoramento, as decisões pendentes).
- [ ] **#11 · Detectores de comportamento** (retorno ignorado, chamada repetida, ferramenta não chamada) — o Rafael
  retoma depois das leituras de artigos pendentes. → `13` §6
- [ ] **#12 · O escopo de memória em `discussion/open-questions.md`** (veio do §5 do plano antigo, junto com dois itens
  que eram da base 2 e foram para lá em 09/10: OBFCivel jul 30 × 180 s → `b2 #12`; falso negativo do AgenteProcuracoes →
  `b2 #11`). **Antes de mexer:** conferir de que base é.

## Fora de escopo / adiado

- **Monitor de composição entre bases** — para a operação contínua, não agora (`b1 #38`).

## Fechado

Cada linha: o que foi feito → o commit ou o documento (a prova). Itens dos §2 do plano antigo que são do método ou do
kit; os de uma base estão no roadmap dela.

- [x] **#13 · O trace em parquet** (plano antigo 4.10) — leitor único `analysis/leitor_trace.py` → `bd3db6b`;
  `analysis/README.md` (intake).
- [x] **#14 · O kit de mineração** (4.12): silenciosas, protocolo, investigação e candidatas, de 0.1 a 0.6.0 →
  `bff9714`, `f590038`, `91e9c0a`, `a0fe56c`, `1c36dc2`; [`kit.md`](../.claude/skills/mineracao-base/referencias/kit.md),
  `16`.
- [x] **#15 · O método do protocolo, vindo da investigação de 05/10** (4.13; Ajustes 14–16) → `694636b`; livro-razão,
  `10` §4.
- [x] **#16 · Monitoramento num registro só para todas as bases; o kit no `.claude/`; cada mineração com um nome só** →
  `e069c26`, `20c97dc`, `fdf9a84`, `1ef5d71`; `16`, `kit.md`. Em 09/10 os registros foram para `analysis/registros/`
  (`e0335aa`).
- [x] **#17 · O racional das lições de hábito do agente** → `f6c86d7`; `06` §10.
- [x] **#18 · PR #29 auditado e mergeado; PR #30 fechado sem merge** → `dc89992`; auditoria de 02/10.
- [x] **#19 · Auditoria, blueprint das POCs do M1 e diário da semana de 28/09** → `e01238b`; `audit/`, `pocs/`,
  `research-diary/`.
- [x] **#20 · O plano atual limpo: só plano** (857 → 296 linhas; a errata foi para o livro-razão §7) → `4808971`.

## Referência — onde cada mineração está, em documentos

| Mineração | Racional | Procedimento | Relatório | Skill |
|---|---|---|---|---|
| Falhas silenciosas | `13` | `15` | `14` | sim |
| Protocolo do harness | `10` | `12` | `11` | sim |
| Candidatas | `06` §9 (fato sobre a ferramenta) e §10 (hábito do agente), com o `09` | `16` | `07` (nº2/nº10); as outras nos dossiês, git-ignored | sim |
| Resíduo | parcial, no `01` | parcial, no `03` (Frente 3, §1.16) | — | não (#8) |
| Erro crítico | só a decisão (`01`, #5) | — | — | não (#9) |

(Os números `01`…`16` são os docs da [base 1](2026-09-trace-law-flow/docs/).)
