# Roadmap — o backlog numerado da base 3

> Códigos e siglas: [glossário](../../glossario.md). O schema deste roadmap (o mesmo de todos) está em
> [`../../plano-atual.md`](../../plano-atual.md); as decisões em vigor, em [`../../decisoes.md`](../../decisoes.md); o que
> atravessa as bases, em [`../../roadmap-transversal.md`](../../roadmap-transversal.md). Os números são estáveis: um
> item feito é marcado `[x]` e desce para "Fechado" com a prova, sem mudar de número. **Os números deste arquivo são da
> base 3**; de fora, cite como `b3 #N` (o "roadmap #N" sem prefixo, nos docs antigos, é o da base 1).

Contexto: [relatório](02-relatorio-achados.md) da rodada `observada_609c947b15295c84` (14/10, a v2, depois do Ajuste 18; na v1, `3f9c…`, `b4fcc77…` e `0d23103…`) e
[limitações medidas](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Atualizado em 14/10/2026
(branch `2026-10-14-base3-roadmap-queries`).

## O plano de adaptação: feito e pendente

O plano era levar a base 3 (só os erros, em parquet) para o método das bases 1 e 2, em Python, com o painel no fim.

| Fase | Situação | O que foi feito / o que ficou |
|---|---|---|
| **0** · Conferir o que já existia | **Feita** | Código e schema do parquet conferidos; o código passou a existir nos dois ambientes |
| **1** · Base do pipeline, verificada na base 1 | **Feita** | A query da base 3 reescrita em Python (`validacao/porta_query_v1.py`) e comparada erro a erro com o pipeline da base 1: 498 erros, 415 na mesma unidade, 83 pendentes, 0 em unidade errada. Sem `analysis/etl/` próprio, sem `base.json`, sem `seguidor` opcional: o modo observado cobre |
| **2** · Rodar a base 3 | **Feita, com um resto** | Rodada oficial `0d23103…` (76% classificados) e, depois do Ajuste 17, `3f9c2806…` (14/10): 94% classificados; na v2 (Ajuste 18), `609c947b…` (14/10): **97,5% classificados**, 10 candidatas, 1 sinal de harness, resíduo 1,9%. O corte de texto acabou com a v2 (#14 fechado) |
| **3** · Depois do erro, custo, versão; suspeitas e protocolo | **Em parte** | Há o gráfico e os perfis do que vem depois do erro, por candidata. **Pendente:** custo da janela completa, unidade por versão → #15; suspeitas e protocolo por papel, mês e versão → #16 |
| **4** · Relatório e pedido de dados | **Feita** | `01` a `05` em `docs/` |
| **5** · Kit e auditoria independente | **Não feita** | → #17 |
| **6** · Painel | **Feita e rodada** | `executar.py painel`, 7 gráficos de leitura; leituras no relatório (#10), refeitas em 14/10 para a rodada `609c…` da v2 (#33). A figura de destinos foi corrigida e bate com a triagem (#27) |
| **7** · Quando a v2 e a agregada chegarem | **Chegaram, conferidas e a v2 rodada** (#26, #31) | A v2 é a v1 sem o corte de texto; as contagens são o pedido A atendido, com a junção exata; rodada `609c…`: 97,5% classificados, 749 pendentes. O relatório foi migrado para ela (#33). **Pendente:** as taxas (#32) e B e C reescritos (#2) |
| **Documentos gerais** (glossário, livro-razão, `analysis/README`, `kit.md`) | **Não feita** | → #18 |
| **Teste de equivalência** `triagem_observada` × `bp.triagem` na suíte | **Só como script** | → #19 |

## Backlog — em ordem de valor

- [ ] **#2** **Fechar os pedidos de dados** ([`05`](05-pedido-queries.md)): **A** (denominadores) **chegou e foi conferido**
  (#26: junção exata chave a chave) — sai do pedido; falta integrá-lo ao pipeline (#32). **B** (complemento dos
  pendentes): **a parte do corte saiu** — na rodada da v2 (#31) os 1.009 de mensagem cortada e os 46 de linha
  rejeitada viraram unidade ou resíduo; ficam os 15 de histórico, os 5 de numeração ambígua e, para os 215 timeouts,
  os nomes das ferramentas declaradas no prompt (o código inteiro já veio). Os 514 do primeiro passo dependem do nome
  do modelo (#29). **C** (ajustes na extração): o agente na partição
  **sai** (uma execução tem um agente só); ficam "Error calling tool", o nome do modelo e o hash do system prompt — mais
  importantes agora que `cod_vers_aget` quase não varia — e o texto ausente como comprimento zero; "todas as
  ferramentas do passo" é para medir antes no `tool_calls` inteiro da v2. **Falta:** reescrever B e C no `05`
  (que ainda descreve A como "a enviar") e levar ao tutor (#11).
- [ ] **#32** **Taxas e relatório único (pedido A integrado)** — **código pronto (14/10), falta rodar na base 3:**
  `executar.py relatorio` gera o painel, as taxas e `<rodada>/relatorio/relatorio.md` (parte 1, os erros; parte 2, as
  taxas). As taxas (`execucao/taxas.py`, `execucao/figuras_taxas.py`) só saem se a junção fonte × contagens conferir
  (7 verificações; se falhar, a parte 2 diz o motivo). Dez gráficos: funil, taxa por mês (com e sem o sinal de harness),
  papel volume × taxa, custo de execução com × sem erro, concentração (Lorenz), custo mensal por execução, entrada ×
  saída (#13 no agregado), taxa por unidade e mês, fatia do orçamento de cada papel por destino, prioridade por
  critério. 182 testes (4 novos em `test_taxas_base3.py`). **Rodado na base 3 em 15/10** (rodada `609c…`): a junção
  passou nas 7 verificações e os números batem com o resumo (283.925 ActionSteps; 30.141 erros, 10,6%; 3.729,3 mi de
  tokens, 592,9 mi em passos com erro). **Falta:** auditar e corrigir os gráficos (#36) e só então reescrever o
  [relatório](02-relatorio-achados.md) §7 com as taxas.
- [ ] **#36** **Auditoria dos 10 gráficos de taxas, um por um** (aberto em 15/10; Rafael audita cada gráfico e
  acrescenta complementações). Conferido em 15/10 por duas vias — os números lidos das imagens cruzados entre si e
  com os totais, e o código de cada figura (`execucao/figuras_taxas.py`, `execucao/taxas.py`). **Os números
  conferem:** somas por mês (283.925 / 30.141 / 71.881); as 10 taxas do gráfico 2 recalculadas das barras; 5 células
  do gráfico 8 = contagem do painel ÷ ActionSteps do mês; fatia × gasto do papel (gráfico 9) = tokens em erro do gráfico
  10 nos 10 papéis, com diferença máxima de 0,4 mi; os 10 papéis somam 589,5 dos 592,9 mi. **O que precisa corrigir:**

  | # | Gráfico | O que a conferência achou | Correção | Auditado |
  |---|---|---|---|---|
  | 1 | Funil | O mesmo rótulo ("com erro estruturado") conta execuções à esquerda (20.442) e passos à direita (30.141), e o título mistura as duas unidades — por isso 20.442 e 30.141 parecem inconsistentes. A barra "com ActionStep" repete "execuções" (71.881). **A limitação escrita está errada para estes dados:** diz que execuções sem ActionStep contam no total, mas toda execução (execução + agente) tem ao menos um passo (as 6 linhas com 0 passos são papéis dentro de execuções que têm outros papéis com passos). Os 28,4% contam só erro estruturado: com as suspeitas (20.986 execuções no parquet de erros) seriam 29,2% | Rótulos "execuções com pelo menos um erro" e "passos com erro"; título "28,4% das execuções têm pelo menos um erro · 10,6% dos passos são erro"; tirar a barra repetida; linhas "1,47 erro por execução com erro" (30.141 ÷ 20.442) e "3,95 passos por execução" (283.925 ÷ 71.881); reescrever a limitação; nota dos 29,2% com as suspeitas | [ ] |
  | 2 | Taxa por mês | **Sem defeito.** As 10 taxas batem. Leitura: sem queda sustentada (16,4% → 4,1% → 15,7%); agosto sem o `try/except` ainda 10,6% × 6,6% em julho; meses antigos com pouca amostra (novembro: 446 passos) | Marcar na figura os meses com menos de 1.000 passos como "amostra pequena" | [ ] |
  | 3 | Papel: volume × taxa | O título cita AnaliseProcessual e AgenteProcuracoes, mas os pontos não têm rótulo (rótulo só nos 10 papéis com mais erros); os dois têm cerca de 50 a 70 passos | Rotular também os papéis citados no título | [ ] |
  | 4 | Custo com × sem erro | **Sem defeito.** 43.774 ÷ 10.074 = 4,3×. É associação, não causa (execução longa erra mais e custa mais) | — (a limitação já está na figura) | [ ] |
  | 5 | Concentração (Lorenz) | **Sem defeito.** 10% mais caras = 64% do gasto; 1% = 21%. A curva começa em 1/n, não em 0 (efeito visual) | Começar a curva em (0, 0) | [ ] |
  | 6 | Custo mensal por execução | O título "de 18.324 (2025-11) a 15.114 (2026-08)" sugere estabilidade; novembro tem 71 execuções. O padrão é ≈ 48 mil (dez–abr) → 10 a 15 mil (jun–ago). **A queda não é aprendizado**: a taxa de erro (gráfico 2) não caiu junto, e as execuções foram de ≈ 1 mil para 25 a 29 mil por mês — provável mudança de mistura de papéis (hipótese, a medir no #37) | Título com o pico e o último mês; mês de amostra pequena fora do título | [ ] |
  | 7 | Entrada × saída | **Leitura errada minha.** O 9,0% × 4,6% é sobretudo **composição**: 59% dos tokens de erro são do ContestacaoCivel (saída ≈ 11–12%) e o total é dominado pelo OBFCivel (≈ 1%). Ponderando papel a papel (valores lidos da figura, aproximados): dentro dos papéis ≈ 1,5 ponto; mistura ≈ 2,9 pontos de 4,4. A frase do relatório §7.3 "a saída pesa o dobro nos passos com erro" estava errada | Título "dentro de cada papel"; acrescentar a conta de composição; reescrever o §7.3 (feito: ressalva já no texto) | [ ] |
  | 8 | Taxa por unidade e mês | **Leitura errada minha.** "O campo inexistente cai de verdade" não se sustenta: o denominador é o mês inteiro (todos os papéis), e o sistema cresceu ≈ 13× de janeiro a julho. Só a **contagem** caiu (234–476 → 25 e 54); se foi correção ou o RespostaBacen rodou menos, só a taxa do próprio papel decide (#37) | Aviso do denominador no título; usar o denominador do papel dominante da unidade, quando houver | [ ] |
  | 9 | Orçamento de cada papel | **Defeito de código.** A `triagem_por_papel.csv` só tem unidades de memória (`mineracao_observada.py:135`); a faixa "harness / infra" nunca é desenhada e `H_bloco_code` e `H_timeout_ferramenta` caem na faixa roxa "resíduo, crítico ou pendente". O total da barra está certo; a divisão por destino, mal rotulada. A legenda fica fora da área visível | Ler `consolidacao_unidade_papel_mes.csv` (todas as unidades observáveis) e separar infra de resíduo; legenda dentro da área; cor do resto distinta da infra | [ ] |
  | 10 | Prioridade por critério | **Sem defeito.** Os dois rankings batem com o gráfico 9; só o ContestacaoCivel é primeiro nos dois | — | [ ] |

  **Também a corrigir (transversais):** (a) números acima de 1.000 mi em bilhões ("3,73 bi", não "3.729,3 mi"), no
  resumo e nos rótulos; (b) o funil dá 20.442 execuções com erro estruturado e o parquet de erros, 20.986: a diferença
  (544) deve ser de execuções só com suspeita — **hipótese**, fechar com uma contagem no `conferir_contagens.py`
  (execuções com suspeita e sem erro estruturado); (c) o nome do papel aparece como `ontestacaoCivel` nos dados
  (já anotado no relatório §7.8; é o ContestacaoCivel). **Complementações pedidas pelo auditor:** (acrescentar aqui,
  uma linha por pedido, com a data).
- [ ] **#37** **Gráfico novo — taxa de erro e custo por papel × mês, com o papel fixo (o baseline da tese).** Resolve de
  uma vez três pontos do #36: a queda do custo mensal (gráfico 6), a queda do campo inexistente (gráfico 8) e a oscilação
  da taxa (gráfico 2) — todos podem ser mudança da mistura de papéis, e só a taxa do próprio papel separa "o sistema errou
  menos" de "entrou um papel que erra menos". **Dados:** as contagens já têm papel e mês. **Gráfico 6 da base 1 que ele
  continua:** §3.6/8.11, o teste da hipótese nula ("o custo cai sozinho, sem memória?"). **Aguarda o sim do Rafael.**
- [ ] **#38** **Unidades por destino e tipo de memória (factual × estratégia)** — o §14.6 do
  `consolidacao_unidades.ipynb` (antes 9.3 da esteira) e o §8.5 ("só o que o agente pode aprender"): uma barra por
  unidade, agrupada pela decisão, com o tipo no rótulo. **Não migrado**; o tipo já existe no pipeline (`bp.UNI[u][1]`),
  falta desenhar. **Também não migrados, só código:** §2.1 (teste do ToolScan) e §2.3 (duração por assinatura; a v2 tem
  `duration_seconds` dos passos com erro). **Não migráveis com a extração atual** (faltam dados, pedido C): sucesso por
  conteúdo (§3.1/8.12), tokens por chamada de ferramenta (§3.3/8.9), posição na trajetória (§4/8.6) e propagação
  (§5/8.2), falhas silenciosas (§7).
- [ ] **#11** **Apresentação ao tutor** com o painel (relatório + gráficos) e o pedido de dados ([`05`](05-pedido-queries.md)):
    o método transfere (com um ajuste, o 17), os erros moram em poucos papéis, a maior unidade é um sinal de harness (o
    `try/except NameError`, 5.764 erros) e o maior problema isolado de protocolo é o `H_bloco_code`, e o que falta para
    as taxas e para os 2,5% pendentes. Depende de #2 e #32.
- [ ] **#28** **Registro de monitoramento do `try/except NameError`** em [`registros/monitoramento.json`](../../registros/monitoramento.json):
  linha de base (base 3: 5.764, com 5.667 em agosto e 95 em julho; base 2: 105), gatilho (qualquer erro com a assinatura
  depois de o prompt ser corrigido, ou num papel novo) e ação. O gatilho em % de execuções espera o denominador (#2).
- [ ] **#29** **Os 514 erros do primeiro passo sem a assinatura** (`RoteadorCivel` 397, `RespostaBacen` 89; 2,2 mi de
  tokens): outro mecanismo; na base 2 os 6 casos do `RoteadorCivel` são do modelo novo e o prompt não tem a instrução.
  Prioridade baixa: depois do nome do modelo (#2).
- [ ] **#18** **Documentos gerais** (a dívida mais concreta): o glossário ganha `STRUCTURED_ERROR`, `OBSERVATION_SUSPECT`,
  "candidata observada", "pendente", "componente" (= a cascata das bases 1 e 2), `recovery_signal` e os estados de
  capacidade; o livro-razão (`pipeline-entre-bases.md`) ganha a etapa da base 3 (o Ajuste 17, de 13/10, já está lá; falta a
  etapa da base 3 em si); o `analysis/README.md`, o intake por formato; o `kit.md`, o que o kit pode e não pode na base 3. Regra do
  repositório: um código novo entra no glossário no mesmo commit. (O `plano-atual.md` não entra: virou o schema dos
  roadmaps — ver o #20, fechado.)
- [ ] **#12** **Piloto de mineração de ponta a ponta: inventário do sandbox** (`U_sandbox`: 3.653 erros, 16 papéis). A lição
    sai da própria mensagem de erro, então fecha só com o parquet. **Antes:** decidir o localizador do arquivo final
    da memória — o [esquema](../../registros/esquema-memoria.json) pede `idx`, que a base 3 não tem; a proposta é aceitar
    `step_ref` com a origem e a fonte.
- [ ] **#7** **Minerar as demais candidatas, uma por vez**, pela ordem de tokens. Cada uma com racionais, relatório e
  procedimento próprios ([procedimento de mineração](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md)),
  destino decidido na base 3. Fecham só com o parquet: argumento nomeado, `next()` sobre gerador. Precisam do
  prompt ou do contrato da ferramenta (pedido C do `05`): retorno pode chegar como string, campo inexistente.
- [ ] **#19** **Teste de equivalência na suíte:** `triagem_observada` × `bp.triagem` sobre a base 1 pela porta da query, fixando
    "mesmas decisões, 0 em unidade errada" como teste e não só como script (`validacao/comparar_base1.py`).
- [ ] **#13** **Conferir tokens de entrada × saída por unidade** — contagem no ambiente da base 3. Confirma (ou não) que o custo
    por erro é o contexto acumulado, a leitura do gráfico frequência × custo. **Já se sabe (14/10, #26):** a saída é
    9,0% dos tokens nos passos com erro e 4,6% em todos os ActionSteps; a v2 traz entrada e saída de cada passo com
    erro, e as contagens trazem as do papel — dá para fazer junto com o #32.
- [ ] **#15** **Depois do erro, completo (e4):** a recuperação em n+1 e n+2 recalculada das colunas (sem usar o
    `recovery_signal` pronto da query); o custo da janela só quando ela está completa (`has_full_2_action_window`); a
    unidade por versão do agente ("aparece ou some"), para o critério "ainda relevante". **A versão não serve (14/10,
    #26):** `cod_vers_aget` vale 1 em 85 linhas de erro e 147 de 71.894 nas contagens; "aparece ou some" fica pelo mês
    (a taxa por unidade e mês do #32) até haver o nome do modelo ou o hash do prompt (pedido C).
- [ ] **#16** **Trilhas paralelas (e5):** as suspeitas da query por padrão × papel × mês (só contagem); o protocolo do harness
    por papel, mês e versão. O que não der na extração vai para o relatório como indisponível.
- [ ] **#17** **Kit e auditoria independente (Fase 5):** o kit chamando o `executar.py` na preparação; o `conferir_versao`
    cobrindo o código novo; as skills consultando a capacidade (a das falhas silenciosas para na base 3 e explica);
    um `audit_recompute` independente da base 3 (só biblioteca padrão e `leitor_trace`) e o encontro com as tabelas.
- [ ] **#3** **Protocolo do harness:** resposta sem bloco de código (`H_bloco_code`, 4.592 erros em 4.030 execuções, 14
  papéis, 10 meses). Racionais, relatório e procedimento próprios, como na base 1.
- [ ] **#4** **Críticos:** as 25 execuções que esgotaram os passos (`C_limite_passos`) — o caminho de erros até o fim de cada uma.
- [ ] **#5** **Resíduos:** os 565 erros de causa ou sintoma não reconhecidos (376 + 189, rodada `609c…`; eram 538 na
  v1) — padrões recorrentes e regra nova, se houver (regra nova só olhando as duas bases).
- [ ] **#6** **Conferir o timeout de ferramenta** (`H_timeout_ferramenta`: 1.117 erros num mês e num papel) — incidente pontual
  ou padrão. O gráfico linha do tempo (item 9) já mostra o mês.

## Fora de escopo / adiado

- **Aviso a quem cuida do harness** sobre o `try/except NameError` (`transversal #7`): decisão de 14/10 de não fazer agora;
  a evidência está em [`02` §7.9–7.10](02-relatorio-achados.md#79--a-causa-uma-instrução-do-prompt-que-o-ambiente-de-execução-não-suporta-base-2-1310).
- **Se o parágrafo da instrução já estava no prompt de julho** (base 2): é do [`b2 #3`](../../2026-09-trace-law-flow-second/docs/04-roadmap.md).

## Fechado

Cada linha: o que foi feito → o commit ou o documento (a prova).

- [x] **#35 · O que são os valores longos que começam com `{` e dão erro de string** (14/10): **o retorno da petição
  inicial chegando como texto JSON**, que o agente indexa como dict. Evidência, nas duas bases que têm o caso:
  - **Base 3** (`validacao/contar_mensagens_longas.py`, nas 849 "Could not index" longas do retorno-string): a aspa
    depois do `{` é `{"` em 845 (4 outros) — no sandbox, `{"` é o que um texto JSON dá; dict e repr Python dão `{'`
    (`testar_sandbox_indexar.py`); a variável indexada vem de `get_peticao_inicial_from_pasta` (727) e
    `ingestao_peticao_inicial` (106) (6 atribuídas em outro passo, 3 de `json.loads`, 2 de `draft_resposta`, 1 de
    `coerce_to_obj`); no passo seguinte o agente desserializa (`json.loads`/`literal_eval`) em 789 (93%), e 382 (45%)
    ficam sem erro.
  - **Base 2, trace completo** (`validacao/indexar_string_trace.py --trace <base 2>`): 78 "Could not index"; 38 com
    erro de string; **11 com valor `{` — todos `{"`, todos do ContestacaoCivel, 10 de `get_peticao_inicial_from_pasta`
    e 1 de `ingestao_peticao_inicial`, 10 desserializam no passo seguinte**; 0 retorno-dict.
  - **Base 1** não tem o caso (0 valores `{` com erro de string; não tem o ContestacaoCivel).
  **Para a mineração do retorno-string (#7):** o grosso da unidade na base 3 é uma ferramenta e um papel; o agente
  quase sempre conserta desserializando, e mais da metade erra de novo — a lição tem um alvo concreto. Os
  identificadores ficam no ambiente de cada base (`--evidencia` no script da base 2; a base 3 conta direto do parquet).

- [x] **#34 · Por que o retorno-dict não voltou na v2** (14/10): **não estava escondido pelo corte.** Evidência:
  (1) a regra do dict casa `KeyError: <número>` no fim da mensagem; nas 1.009 mensagens que a v1 cortava (> 20.000
  caracteres, contadas na v2 por `validacao/contar_mensagens_longas.py`), esse fim aparece **0** vezes, nenhuma o tem
  fora do fim e nenhuma traz os dois padrões juntos; na base inteira, 2 vezes. (2) Pela regra real, 1.002 das 1.009
  vão para o retorno-string (849 por `string indices must be integers`, 151 por objeto sem o atributo, 2 por formato
  inválido), 3 para campo inexistente, 3 sem regra, 1 código mal escrito; 847 são do ContestacaoCivel. (3) No sandbox
  (`validacao/testar_sandbox_indexar.py`, smolagents 1.26.0), um dict indexado nunca dá o erro de string — só texto
  dá; um dict indexado com `0` dá `KeyError: 0`. (4) Na base 1 (trace completo, `validacao/indexar_string_trace.py`):
  88 retorno-dict (81 longos, valor `{'`, a `get_available_documents` onde a origem foi lida) e 37 erros de string —
  valor `[` (9) ou texto (28), **nenhum começando com `{`**; 13 dos 37 desserializam no passo seguinte. **O que não está
  provado:** que os 848 valores longos da base 3 que começam com `{` sejam JSON → #35. (A primeira versão do relatório
  e deste item afirmou "JSON chegando como texto" sem essa evidência; corrigido.)
- [x] **#14 · Contrato da fonte (e0): o corte de texto** (14/10) — perdeu o objeto com a v2: o
  `inspecionar_parquet.py` mostra que nenhuma coluna de texto da v2 tem valores no corte da v1 além de 1 ou 2
  coincidências, e a maior mensagem tem 833.507 caracteres; as 1.009 mensagens que a v1 cortava estão inteiras
  (`conferir_contagens.py`, #26). Quantos "Could not index" perderam o `KeyError` na v1 vira a pergunta do #34.

- [x] **#33 · Relatório na rodada da v2** (14/10): painel da `observada_609c947b15295c84` gerado e lido; [`02`](02-relatorio-achados.md)
  §1–7.7 refeito de uma vez (§7.8–7.10, de 13/10, ficam como estão), conferido contra a triagem e a cobertura: as 18
  linhas por mês somam o total de cada unidade, os papéis somam 17.308, os destinos 30.141, e os pendentes por mês
  (contagens menos observáveis) fecham em 749. Entrou a primeira taxa (agosto 15,7% × julho 6,7%, §7.5). O `03` marca a
  v2 como fonte e as limitações 1, 2 e 6 como resolvida, atendida e sem efeito.

- [x] **#31 · Rodada na v2** (14/10): `observada_609c947b15295c84`, a primeira depois do Ajuste 18, **conferida (46
  verificações**, 10 candidatas, 10 perfis, fonte inalterada). Comparada com a `3f9c…` (v1):

  | Medida | `3f9c…` (v1) | `609c…` (v2) |
  |---|---:|---:|
  | Erros estruturados / suspeitas / tokens | 30.141 / 1.280 / 592,9 mi | iguais |
  | Mensagem limitada | 1.009 | **0** |
  | Observáveis | 28.338 (94,0%) | **29.392 (97,5%)** |
  | Pendentes | 1.803 (6,0%) | **749 (2,5%)** |
  | Resíduo (causa + sintoma) | 538 (1,8%) | 565 (1,9%) |
  | Candidatas | 10 | 10 (as mesmas) |

  **Para onde foram os 1.055 que saíram da pendência** (1.009 de mensagem cortada + 46 de linha rejeitada; o histórico
  insuficiente foi de 14 para 15): retorno-string +1.002 (4.317 → 5.319 erros, 169,9 → 207,0 mi), causa não
  identificada +26, texto em literal +11, explicação solta +10, campo inexistente +3, retorno colado +1, sintoma não
  reconhecido +1. Ficam pendentes 514 (primeiro passo sem a assinatura), 215 (timeout: a regra pede o prompt), 15
  (histórico) e 5 (numeração). As demais unidades não mudam. **O retorno-dict não voltou** (2 erros) → #34. As 10
  candidatas somam 17.308 erros e 387,1 mi de tokens (65% dos tokens dos erros). As somas fecham: 29.392 + 749 =
  30.141; tokens 587,7 + 5,1 = 592,8 mi (arredondamento).

- [x] **#26 · Os dois parquets novos conferidos** (14/10), com `validacao/inspecionar_parquet.py` (schema e agregados)
  e `validacao/conferir_contagens.py` (junção), sem nenhum valor de célula:
  - **`base_erros_minerados_full_v2.parquet` é a v1 sem o corte de texto:** as mesmas 31.421 linhas (30.141 erros +
    1.280 suspeitas, 20.986 execuções) e 69 colunas; nenhuma linha só numa das duas; `error_type` e `total_tokens`
    iguais em todas; a mensagem da v1 é o começo da da v2 em 31.421 de 31.421; as 1.009 mensagens no corte de 20.000
    são mais longas na v2 (a maior tem 833.507 caracteres).
  - **`base_contagens.parquet` é o pedido A:** 71.894 linhas, chave (execução, agente, papel) sem duplicata; 71.882
    execuções; `status_memoria` = OK em 71.893 e `JSON_INVALIDO` em 1 (a linha com quantidades nulas); 6 linhas com 0
    ActionSteps; 15 ActionSteps sem tokens. **Junção exata:** as 20.986 chaves da v2 existem nas contagens, com 0
    diferenças de erros, 0 de suspeitas e 0 casos de tokens dos erros acima dos do papel.
  - **Uma execução tem um agente só** (0 de 20.986 e 0 de 71.882 com mais de um): a limitação 6 não age nesta base.
    **A versão quase não varia** (`cod_vers_aget` = 1 em 85 linhas de erro e em 147 de 71.894 nas contagens).
  - **Globais:** 30.141 erros em 283.925 ActionSteps (10,62%); os erros estruturados gastam 592.858.874 de 3.729.280.264
    tokens (15,90%, o mesmo total da rodada `3f9c…`); 13.135 tokens por ActionStep, 19.670 por ActionStep com erro; a
    saída é 4,55% dos tokens no total e 9,01% nos passos com erro.
  - **Por mês** (soma igual aos totais):

    | Mês | Execuções | ActionSteps | Erros | Erro por ActionStep | ActionSteps por execução | Tokens |
    |---|---:|---:|---:|---:|---:|---:|
    | 2025-11 | 71 | 446 | 32 | 7,2% | 6,28 | 13.088.561 |
    | 2025-12 | 449 | 2.769 | 454 | 16,4% | 6,17 | 72.341.379 |
    | 2026-01 | 997 | 6.611 | 1.086 | 16,4% | 6,63 | 194.793.326 |
    | 2026-02 | 943 | 4.584 | 663 | 14,5% | 4,86 | 111.465.566 |
    | 2026-03 | 883 | 4.452 | 656 | 14,7% | 5,04 | 84.836.441 |
    | 2026-04 | 1.173 | 8.011 | 821 | 10,2% | 6,83 | 131.782.617 |
    | 2026-05 | 2.543 | 14.014 | 1.234 | 8,8% | 5,51 | 203.480.945 |
    | 2026-06 | 10.736 | 43.358 | 1.797 | 4,1% | 4,04 | 370.202.980 |
    | 2026-07 | 24.824 | 88.307 | 5.913 | 6,7% | 3,56 | 890.416.053 |
    | 2026-08 | 29.263 | 111.373 | 17.485 | 15,7% | 3,81 | 1.656.872.396 |

    **Agosto teve mais execuções e mais erro por ActionStep:** 18% mais execuções que julho, mas 2,96 vezes os erros;
    a taxa vai de 6,7% para 15,7%. Sem os erros do `try/except NameError` (5.667 em agosto, 95 em julho), fica 10,6%
    contra 6,6% — o sinal de harness explica parte do salto, não todo. Em agosto, 29.275 linhas para 29.263 execuções:
    12 execuções com dois papéis.

- [x] **#27 · Gerar o painel de novo na máquina 2**, com `execucao/figuras_painel.py` corrigido (14/10): Rafael gerou o painel
  depois da correção (a figura de destinos descartava os 5.764 erros do sinal de harness e agora tem a faixa e uma trava)
  → commit `a4bd5f4`. **Ressalva:** a figura nova ainda não foi fotografada; o que o relatório §7.2 cita sai da triagem
  e da cobertura, não da figura. A foto das barras (30.141 erros, 592,9 mi) fecha a conferência.

- [x] **#1 · Investigar os 5.818 erros de nome não definido sem passo anterior identificado** (13–14/10): os 5.818 são todos o
  primeiro ActionStep do papel, um erro por execução, 98% em agosto; a causa é uma instrução do system prompt do
  ContestacaoCivel (`try/except NameError`) que o interpretador do sandbox não captura — vista no trace inteiro da base 2
  (3 casos lidos), reproduzida no smolagents 1.26.0 e contada na base 3 (5.764 de 7.178 erros de nome); 460 estavam
  em estado perdido e nome inventado só pela posição → [`02` §7.8–7.10](02-relatorio-achados.md#78--o-nome-não-definido-no-primeiro-passo-contagens-de-1310),
  commits `ed06865`, `9fd032b` e `d975621`.
- [x] **#30 · Ajuste 17 aplicado e conferido** (13–14/10): a assinatura na linha que falhou decide antes da posição;
  `U_verificacao_try_nameerror`, destino harness nas bases 2 e 3; base 1 sem mudança (498 de 498); 169 testes; kit 0.7.0;
  pipeline da base 2 replicado (`validar`: 10 de 10 iguais); rodada `observada_3f9c2806cac9cd4d` conferida (46
  verificações), com 28.338 observáveis e 1.803 pendentes, como a simulação → [livro-razão, Ajuste 17](../../pipeline-entre-bases.md),
  commits `d975621`, `0e55110` e `e7c6cc1`; painel lido e §7.1–7.7 refeito → `a4bd5f4`.

- [x] **#10 · Relatório com as leituras do painel** (09/10): [`02` §7](02-relatorio-achados.md#7--leituras-do-painel) — onde estão
  os pendentes, destino de erros e tokens, custo por erro × frequência, concentração por papel, o padrão no tempo e o
  que vem depois do erro; cada número conferido com as tabelas das seções 2 e 3 (os valores por mês e por papel somam
  os totais). Ressalva escrita: sem denominador, não se sabe se agosto teve mais execuções ou mais erro por execução.
- [x] **#9 · Painel novo rodado** (09/10): rodada `observada_b4fcc7711a9ec8a6` na máquina 2; contagens iguais às da
  `0d23103afd4fc0f4` (30.141, 23.034, 7.107, 17 unidades, 10 candidatas, 538 no resíduo) e os 7 gráficos de leitura
  gerados, sem a seção "gráficos não gerados". **Resto:** a suíte lá rodou 162 testes em vez de 164 — dois arquivos de
  teste estão na versão antiga (`test_comandos_third.py` e `test_mineracao_observada_base3.py`); copiar da `main`.
- [x] **#8 · Painel** (08–09/10): `executar.py painel` gera `<rodada>/painel/` com `painel.md` (resumo, cobertura,
  triagem), as figuras da rodada, a figura de cobertura e 7 gráficos de leitura, cada um com pergunta, como ler e
  limitação. Tudo calculado dos CSVs da rodada, com o hash de cada um conferido. Rodado na versão só com as tabelas;
  a versão completa é o item 9.
- [x] **#25 · Documentação da base 3, do zero** (08–09/10): [`01`](01-racionais.md) racionais, [`02`](02-relatorio-achados.md)
  relatório, [`03`](03-procedimento-validacao.md) procedimento e limitações, este roadmap, [`05`](05-pedido-queries.md)
  pedido de dados. Os documentos de análises anteriores (07/10) estão em [`historico/`](historico/README.md).
- [x] **#23 · Teste com resposta conhecida** (08/10): a base 1 pela mesma query da base 3 — 498 de 498 erros com par, 415 na
  mesma unidade, 83 pendentes, 0 em unidade errada. Ver [procedimento §3](03-procedimento-validacao.md#3--teste-com-resposta-conhecida-a-base-1-pela-mesma-query).
- [x] **#24 · Rodada oficial** (08/10): `observada_0d23103afd4fc0f4`, igual à de 07/10; 46 verificações.
- [x] **#22 · Adaptação do pipeline à base 3** (08/10): orquestração só em Python (`executar.py`, sem notebooks), 164 testes,
  validação sem depender de resultados antigos. Ver [procedimento §2](03-procedimento-validacao.md#2--o-que-foi-conferido).
- [x] **#21 · Leitura do parquet** (antigo 4.10 do plano) — leitor único `analysis/leitor_trace.py`, que abre CSV ou um único
  parquet → `bd3db6b`; `analysis/README.md` (intake).
- [x] **#20 · O `plano-atual.md`** — decidido em 09/10: vira o schema dos roadmaps (o mesmo para todas as análises); as
  decisões vão para `decisoes.md`, o que atravessa as bases para `roadmap-transversal.md`, e cada base ganha o seu
  roadmap em checkboxes; a base 2 ganhou pasta → `analysis/plano-atual.md`; `analysis/2026-09-trace-law-flow-second/`.
