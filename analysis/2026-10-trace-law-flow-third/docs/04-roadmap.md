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
  | 2 | Taxa por mês | **Os números batem** (as 10 taxas recalculadas). **Decisão de 15/10 ([`decisoes.md`](../../decisoes.md)): erro é erro — tirar a linha tracejada "sem o sinal de harness"**: o destino depende da classificação, que muda a cada investigação, e o gráfico de volume ficaria sempre por refazer (a separação por destino mora no gráfico 9 e no #38); sai também `taxa_sem_harness` e `erros_sinal_harness` de `taxas_por_mes.csv` e o uso da tabela da rodada nesta figura. Demais ajustes: (a) o **título destaca o pico** ("2026-01, 16,4%"), mas dezembro tem 16,40% e janeiro 16,43% — empate; a mensagem é a ausência de queda sustentada (16,4% → 4,1% → 15,7%); (b) rótulos de julho (6,7%) e junho (4,1%) colidem com os marcadores; (c) o eixo de volume sem separador de milhar (100000) enquanto as barras usam 111.373; (d) **amostra pequena não está sinalizada**: só vira cinza com menos de 20 execuções, mas novembro tem 446 passos (7,2% ± 2,4 pontos, binomial ingênuo) e dezembro 2.769 (± 1,4); a subida de novembro para dezembro é real, mas jan/fev/mar (16,4; 14,5; 14,7) não se distinguem com folga — e os erros vêm em cascata (até 26 por execução), então a incerteza real é maior que a binomial; (e) a **limitação não diz que a taxa mistura papéis**: a queda de dezembro a junho coincide com o volume ×3 de maio para junho e pode ser mistura (#37). (A leitura "agosto sem o `try/except` ainda 10,6% × 6,6% em julho" sai da figura; fica como texto do relatório, §7.5, ou vai para o gráfico de destinos) | Título "A taxa de erro não cai de forma sustentada: 16,4% (dez/jan) → 4,1% (jun) → 15,7% (ago)"; uma linha só, rotulada em todos os meses sem colisão; separador de milhar no eixo; faixa de incerteza (ou cinza abaixo de 1.000 passos); acrescentar à limitação "a taxa mistura papéis; ver #37" | [ ] |
  | 3 | Papel: volume × taxa | **Coerente com os outros gráficos:** o tamanho das bolhas segue o gasto do gráfico 9 (OBFCivel > ContestacaoCivel > CalculoTrabalhista > RoteadorCivel > RespostaBacen); RoteadorCivel (≈ 150 mil passos a ≈ 5%) e OBFCivel (≈ 65 mil a ≈ 3%) dão ≈ 7,5 mil e ≈ 2,1 mil erros, compatíveis com as candidatas e os pendentes deles. Ajustes: (a) o **título lista três papéis acima do dobro da média, mas dois deles não têm rótulo** (AnaliseProcessual e AgenteProcuracoes, os pontos de ≈ 50 a 70 passos a 25% e 44%); 9 outros pontos também ficam sem nome. **Causa (pergunta do Rafael, 15/10): o título e os rótulos usam regras diferentes** — o título lista todo papel com ≥ 20 execuções e taxa > 2 × 10,6% = 21,2%; os rótulos vão só nos 10 papéis com mais erros **absolutos**, e os dois papéis pequenos têm poucas dezenas de erros. São os dois pontos azuis no alto à esquerda; qual é qual, só o `taxas/taxas_por_papel.csv` diz. Regra da correção: todo papel citado no título leva rótulo; (b) o **título não diz a mensagem do gráfico** — quem erra mais por passo não é quem roda mais (ContestacaoCivel ≈ 38% em ≈ 35 mil passos; RoteadorCivel ≈ 5% em ≈ 150 mil); (c) **a taxa inclui o sinal de harness — e fica assim (decisão de 15/10: erro é erro)**; o ContestacaoCivel erra em ≈ 38% dos passos (≈ 43% dos erros dele são o `try/except`, estimativa lida da figura), e essa separação aparece no gráfico 9, não aqui; (d) a linha "média 10,6%" é a **taxa global** (ponderada pelo volume, dominada pelo RoteadorCivel e pelo OBFCivel), não a média dos papéis; (e) a taxa de cada papel é do **período inteiro** e esconde o mês (o ContestacaoCivel pesa em agosto); (f) os rótulos de JoogleAnalytics e RespostaBacen se sobrepõem; (g) **o tamanho da bolha não está definido (pergunta do Rafael, 15/10):** é a soma dos tokens de **todos** os ActionSteps do papel, com ou sem erro (`tokens_total` das contagens; `figuras_taxas.py:85`), não só dos passos com erro (ex.: OBFCivel 1.222 mi no total e 29,5 mi em erros) — o "Como ler" diz só "gasto total em tokens" e a figura não tem escala de bolha; (h) **a conferir:** os papéis pequenos com taxa alta (AnaliseProcessual, AgenteProcuracoes) aparecem também no gráfico de pendentes, com timeouts — a taxa deles pode ser sobretudo erro que a regra não classifica (hipótese) | Título com a mensagem, calculado dos dados (o papel de maior taxa e o de maior volume, com os dois números); rótulo em todo papel com pelo menos 20 execuções, ou ao menos nos citados no título; "taxa global 10,6%" no lugar de "média"; afastar os rótulos sobrepostos; "Como ler" com "tamanho = gasto total do papel em tokens, em todos os seus ActionSteps (com ou sem erro)" e uma legenda de escala (1 bi, 500 mi, 100 mi); contar a composição dos erros dos papéis pequenos de taxa alta (unidade e pendentes) | [ ] |
  | 4 | Custo com × sem erro | **REDESENHAR (decisão do Rafael, 15/10): o gráfico ficou confuso (mediana, p90 e duas escalas na mesma figura; nem o autor da pesquisa o entendeu) e não será enviado ao tutor como está.** Os números **estão certos** (43.774 ÷ 10.074 = 4,3×; n = 20.442 + 51.439 = 71.881); o que **não está estabelecido** é a leitura "o erro custa 4,3×". Achados da conferência: (a) título causal ("custa"); (b) **provável mistura de papéis, como no gráfico 7 (hipótese)**: a mediana é 4 contra 3 passos (1,3×), os tokens por passo diferem muito entre papéis (ContestacaoCivel ≈ 25 mil, RoteadorCivel ≈ 3 mil); (c) barras ilegíveis (eixo até 500 mil por causa do p90); (d) "sem erro" inclui as execuções só com suspeita; (e) mediana e p90 sem explicação, eixo de passos com decimais (2,5) e escalas independentes não avisadas. **O que o gráfico deve responder (Rafael): "nossos erros custam X× mais tokens e X× mais passos".** **Desenho proposto:** dois painéis simples, cada um com duas barras normalizadas — "execução sem erro = 1×" e "execução com erro = k×" —, um para **tokens por execução** e outro para **ActionSteps por execução**, com **uma estatística só na figura: a mediana** (decisão do Rafael, 15/10: robusta à cauda longa — 1% das execuções leva 21% do gasto; o que ele achou confuso foi o desenho, não a mediana; o "Como ler" a define em palavras: "a execução do meio — metade custa menos, metade custa mais"); a média e o p90 vão para o CSV e são citados no texto se contarem história diferente; título "a execução típica com erro usa k× os tokens e j× os passos da típica sem erro". Antes de fixar o número: calcular **dentro de cada papel** (as contagens têm papel e execução) para saber quanto do k é mistura (#37). **Duas leituras que já saem dos totais, sem mediana:** (1) os erros são **10,6% dos passos e 15,9% dos tokens**; (2) um **passo com erro custa ≈ 19,7 mil tokens e um passo sem erro ≈ 12,4 mil — 1,6×** (global, ainda com mistura de papéis). **Complemento (não migrado do §8.3 da esteira, a confirmar com uma contagem):** "quantas trajetórias terminam num passo com erro" — o `recovery_signal = NO_NEXT_ACTION` da v2 marca o erro que é o último passo do papel | Reescrever `figuras_taxas.custo_execucao` no desenho acima; calcular a mediana (e a média, para o CSV) por papel com e sem erro; "Como ler" em palavras; eixo de passos só com inteiros | [ ] |
  | 5 | Concentração (Lorenz) | **Os números batem** (10% mais caras = 64% do gasto; 1% = 21%). **Reavaliado em 15/10 — a primeira nota ("sem defeito") estava incompleta.** (a) Erro de texto no título: "as 10% execuções mais caras" → "as 10% mais caras das execuções"; (b) **o nome**: a curva soma da mais cara para a mais barata e fica **acima** da diagonal — é uma curva de concentração (Lorenz invertida), não a de Lorenz (que soma da mais barata e fica abaixo); a esteira da base 1 também a chama de Lorenz, então nota no "Como ler" em vez de renomear; (c) o rótulo "1% mais caras" cruza a diagonal tracejada; (d) o rótulo do eixo x não aparece na foto (pode estar cortado; conferir); (e) a limitação não diz que "execução" = execução + agente somando os papéis e que o planejamento não entra; (f) a curva começa em 1/n, não em 0 (efeito visual). **Complemento — o que liga o gráfico à pergunta da pesquisa (contagem direta, sem hipótese):** hoje diz que o custo é concentrado, mas não se as execuções caras são as **com erro** — entre as 10% e as 1% mais caras, que % tem pelo menos um erro estruturado? (as contagens têm execução e erros) | Corrigir o título; nota do nome no "Como ler"; afastar o rótulo da diagonal; começar em (0, 0); limitação completa; escrever nos dois pontos "dessas, X% têm erro"; (opcional) coeficiente de Gini no título | [ ] |
  | 6 | Custo mensal por execução | **Os números batem** (n por mês: 71, 449, 997, 943, 883, 1.173, 2.543, 10.736, 24.824, 29.262 = 71.881). **Correção de uma afirmação minha (15/10):** eu havia escrito que "a queda não é aprendizado: a taxa de erro não caiu junto" — **errado**. Custo e taxa de erro **andaram juntos**: de dez/jan a junho a taxa foi de 16,4% a 4,1% e a mediana por execução de ≈ 48 mil a 10 mil (média de 161–195 mil a 34 mil); de junho a agosto a taxa subiu a 15,7% e o custo subiu (mediana +52%, média +64%). Correlação nos 10 meses: 0,67 (mediana) e 0,45 (média) — n = 10, sugestivo, não prova. Duas leituras, **ambas hipóteses**: o erro encarece a execução, ou uma causa comum (mistura de papéis, mudança de prompt) mexe nos dois. O custo por **passo** caiu de ≈ 29 mil (jan) a ≈ 8,5 mil (jun) enquanto os passos por execução foram de 6,6 a 4,0: a queda é sobretudo de custo por passo. **Para a tese:** o teste do §3.6 da esteira ("se o custo caísse sozinho, bastaria esperar") não é respondido por este gráfico — o custo **caiu** (≈ 80% de janeiro a junho) e **subiu**; ele mostra o que o sistema faz sem memória (oscila com o erro e a mistura), não que o custo não cai. **Leitura do Rafael (15/10), confirmada com os totais:** o que caiu foi a razão tokens por execução, **não o gasto** — de maio para junho as execuções foram de 2.543 a 10.736 (×4,2), a mediana de 29.593 a 9.964 e os **tokens totais subiram 82%** (203 mi → 370 mi; 890 mi em julho; 1,66 bi em agosto); os **erros absolutos também não caíram** (1.086 em jan, 1.797 em jun, 17.485 em ago) — a taxa caiu porque o volume cresceu mais que os erros. **Diluição ou mistura de papéis está mais bem sustentada que aprendizado** (aprendizado apareceria como menos erros num mesmo papel com volume parecido); **continua hipótese** até o #37. "Na casa de 10 mil" vale para junho e julho (9.964 e 11.292); agosto sobe a 15.114 (+34% sobre julho), com a taxa de erro de 4,1% (jun) a 15,7%. Ajustes: (a) título "de 18.324 (2025-11) a 15.114 (2026-08)" sugere estabilidade, e novembro tem 71 execuções; (b) **estatística: a mediana fica (decisão do Rafael, 15/10)**; a média por mês (195 mil em jan, 34 mil em jun, 57 mil em ago) vai para o CSV; (c) eixo sem separador de milhar (60000); (d) não separa mistura de papéis (#37) | Título "pico de 50.672 em abril, 9.964 em junho e 15.114 em agosto"; mediana, como no gráfico 4; separador de milhar; segunda linha com a taxa de erro do mês no mesmo eixo de meses, para ver o par; mistura de papéis no #37 | [ ] |
  | 7 | Entrada × saída | **Os totais batem** (saída 4,6% em todos os passos, 9,0% nos passos com erro; entrada + saída = 3.729 mi). **Leitura errada minha, já corrigida no relatório §7.3:** o 9,0% × 4,6% é sobretudo **composição** — 59% dos tokens de erro são do ContestacaoCivel (saída ≈ 11–12%) e o total é dominado pelo OBFCivel (≈ 1%); ponderando papel a papel (valores lidos da figura, aproximados) a diferença dentro dos papéis é ≈ 1,5 ponto de 4,4, e a mistura ≈ 2,9. Reavaliado em 15/10: (a) **o título usa os valores globais (4,6% e 9,0%), que não são as médias dos 10 papéis desenhados**, e convida a ler "o erro gera o dobro"; (b) **a figura responde a pergunta errada**: o subtítulo pergunta se o custo do erro vem da entrada ou da saída, mas o gráfico mostra a fatia de saída; a resposta direta está nos mesmos dados — **em todos os 10 papéis ≥ 85% dos tokens do passo com erro são de entrada** (a maior saída é a do RespostaBacen, ≈ 14,2%); (c) **"entrada" não prova "contexto acumulado"** (a entrada inclui o prompt do sistema, fixo, e o histórico, que cresce): hipótese até medir, com `step_number` e `input_tokens` dos passos com erro da v2, se a entrada cresce com a posição do passo (#13); (d) dentro de cada papel a diferença é pequena na maioria: em 8 dos 10 a laranja é maior, mas só o OBFCivel (≈ 1,3% → 4,6%) e o RoteadorCivel (≈ 5,1% → 8,6%) têm salto relevante, e o CadastroTrabalhista tem o contrário (≈ 2,6% → 1,6%); (e) os 10 papéis são os de mais tokens **no total**, mas a pergunta é sobre erros — usar os 10 com mais tokens **em erros**; (f) faltam rótulos de valor nas barras e o número de passos com erro de cada papel (poucos erros → laranja instável); (g) **leitura do Rafael (15/10) e o que ela mostra:** OBFCivel (saída ≈ 1,3% → 4,7%, ≈ 3,5×) e RoteadorCivel (≈ 5,1% → 8,6%, ≈ 1,7×) têm relativamente mais geração no passo com erro; ContestacaoCivel e RespostaBacen têm as barras quase iguais (o passo com erro tem a composição do típico). **O que não se sustenta:** (i) "a diferença é os tokens consumidos nos erros" — os tokens do erro são a barra inteira; a diferença é só a fatia de saída (no OBFCivel, 95% do passo com erro ainda é entrada, e os erros são 2,4% do orçamento do papel); (ii) "o custo é de contexto" nos papéis de barras iguais — a entrada domina em todos os papéis (≥ 85%), não só nesses; (iii) "erro de saída" no RoteadorCivel é **hipótese** (algumas unidades são geradoras: resposta sem bloco de código, texto solto, texto longo em literal) — medir a fatia de saída por unidade (#13); (g2) **o leitor não sabe o que são a barra azul e a laranja (pergunta do Rafael, 15/10)**: "entrada" (o que o modelo lê: prompt, histórico, retorno das ferramentas) e "saída" (o que escreve: raciocínio e código) não estão definidas; o comprimento da barra é só a **fração de saída** (não o número de tokens nem de erros); azul = todos os ActionSteps do papel, laranja = só os com erro estruturado, e isso só aparece na legenda, fora da área visível — a figura nova deve trazer as definições no "Como ler" e a legenda dentro; (g3) **a figura induz uma leitura invertida (Rafael, 15/10):** uma fatia de saída alta (≈ 11% no ContestacaoCivel, "≈ 89% de leitura") foi lida como "papel com mais contexto"; é o contrário — fatia de saída alta é papel que **escreve** relativamente mais (o OBFCivel, com ≈ 98,7% de leitura, é o mais "leitor"); o contexto em termos absolutos só aparece em tokens por passo (ContestacaoCivel ≈ 25 mil, OBFCivel ≈ 19 mil, aproximado); e a diferença laranja − azul não é "o erro" nem o custo dele, é quanto a composição do passo que falhou se afasta da do típico; uma diferença grande **aponta onde olhar** (hipóteses: erros geradores — resposta sem bloco de código, texto solto, texto longo em literal; erro cedo no trajeto com pouco contexto; resposta longa rejeitada), não a causa; (h) **a fatia de saída depende de quanto contexto o passo tem** (saída ÷ entrada + saída): os erros do `try/except` são todos do primeiro passo, com pouco contexto, o que eleva a fatia sem o agente gerar mais — **medir tokens absolutos por passo, entrada e saída separadas**; globalmente (aproximado, mistura papéis): passo com erro ≈ 17,9 mil de entrada e ≈ 1,8 mil de saída, passo sem erro ≈ 11,9 mil e ≈ 0,46 mil (≈ 1,5× e ≈ 3,9×) | Título "em todos os papéis, ≥ 85% dos tokens do passo com erro são de entrada" (calculado dos dados); a conta de composição no "Como ler" (dentro dos papéis ≈ 1,5 ponto; mistura ≈ 2,9); papéis ordenados por tokens em erros; rótulo de valor em cada barra e "n passos com erro" por papel; medir a entrada dos passos com erro por posição do passo (#13) antes de afirmar "contexto acumulado"; **trocar a figura por dois painéis em tokens absolutos por passo — entrada e saída —, passo típico × passo com erro, por papel** (as contagens dão os tokens do papel e os passos; a fonte dá os do passo com erro) | [ ] |
  | 8 | Taxa por unidade e mês | **Leitura errada minha.** "O campo inexistente cai de verdade" não se sustenta: o denominador é o mês inteiro (todos os papéis), e o sistema cresceu ≈ 13× de janeiro a julho. Só a **contagem** caiu (234–476 → 25 e 54); se foi correção ou o RespostaBacen rodou menos, só a taxa do próprio papel decide (#37) | Aviso do denominador no título; usar o denominador do papel dominante da unidade, quando houver | [ ] |
  | 9 | Orçamento de cada papel | **Defeito de código.** A `triagem_por_papel.csv` só tem unidades de memória (`mineracao_observada.py:135`); a faixa "harness / infra" nunca é desenhada e `H_bloco_code` e `H_timeout_ferramenta` caem na faixa roxa "resíduo, crítico ou pendente". O total da barra está certo; a divisão por destino, mal rotulada. A legenda fica fora da área visível | Ler `consolidacao_unidade_papel_mes.csv` (todas as unidades observáveis) e separar infra de resíduo; legenda dentro da área; cor do resto distinta da infra | [ ] |
  | 10 | Prioridade por critério | **Sem defeito.** Os dois rankings batem com o gráfico 9; só o ContestacaoCivel é primeiro nos dois | — | [ ] |

  **Princípio (decisão de 15/10, [`decisoes.md`](../../decisoes.md)): nos gráficos de volume, taxa e custo, erro é erro** — sem linha, marcador ou cor por destino; o destino mora no gráfico 9 e no #38. **Também a corrigir (transversais):** (a) números acima de 1.000 mi em bilhões ("3,73 bi", não "3.729,3 mi"), no
  resumo e nos rótulos; (a2) **a base da taxa não está definida nos gráficos** e muda entre eles (pergunta do Rafael,
  15/10): os gráficos 2 e 3 usam % ("a cada 100 passos", implícito no rótulo "% dos ActionSteps") e o 8 usa "por 1.000
  ActionSteps" (escolhido porque as taxas por unidade são pequenas). Regra: a base escrita no eixo e no "Como ler" de
  todo gráfico de taxa ("erros a cada 100 passos (%)"; "erros a cada 1.000 passos do mês") e, se possível, uma base só no
  relatório (% com uma casa a mais no 8) — ou, mantendo 1.000 no 8, a frase "≈ 10 vezes o valor em %"; (b) o funil dá 20.442 execuções com erro estruturado e o parquet de erros, 20.986: a diferença
  (544) deve ser de execuções só com suspeita — **hipótese**, fechar com uma contagem no `conferir_contagens.py`
  (execuções com suspeita e sem erro estruturado); (c) o nome do papel aparece como `ontestacaoCivel` nos dados
  (já anotado no relatório §7.8; é o ContestacaoCivel). **Complementações pedidas pelo auditor:** (acrescentar aqui,
  uma linha por pedido, com a data).
- [ ] **#37** **Gráfico novo — taxa de erro e custo por papel × mês, com o papel fixo (o baseline da tese).** Resolve de
  uma vez três pontos do #36: a queda do custo mensal (gráfico 6), a queda do campo inexistente (gráfico 8) e a oscilação
  da taxa (gráfico 2) — todos podem ser mudança da mistura de papéis, e só a taxa do próprio papel separa "o sistema errou
  menos" de "entrou um papel que erra menos". **Dados:** as contagens já têm papel e mês. **Duas visões baratas, só de contagem, para checar a mistura cedo (proposta de 15/10, a partir da leitura do Rafael do gráfico 6):** (1) **execuções por papel e mês** — mostra quando cada papel entrou em produção e se as ≈ 10 mil execuções de junho são de um papel novo e leve; (2) **a mediana de tokens por execução, por papel e mês** — se a queda da mediana global some com o papel fixo, era mistura. **Gráfico 6 da base 1 que ele
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
