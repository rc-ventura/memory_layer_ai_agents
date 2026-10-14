# Roadmap — o backlog numerado da base 3

> Códigos e siglas: [glossário](../../glossario.md). O schema deste roadmap (o mesmo de todos) está em
> [`../../plano-atual.md`](../../plano-atual.md); as decisões em vigor, em [`../../decisoes.md`](../../decisoes.md); o que
> atravessa as bases, em [`../../roadmap-transversal.md`](../../roadmap-transversal.md). Os números são estáveis: um
> item feito é marcado `[x]` e desce para "Fechado" com a prova, sem mudar de número. **Os números deste arquivo são da
> base 3**; de fora, cite como `b3 #N` (o "roadmap #N" sem prefixo, nos docs antigos, é o da base 1).

Contexto: [relatório](02-relatorio-achados.md) da rodada `observada_3f9c2806cac9cd4d` (14/10, depois do Ajuste 17; antes, `b4fcc77…` e `0d23103…`) e
[limitações medidas](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Atualizado em 14/10/2026
(branch `2026-10-09-base3-painel-historico`).

## O plano de adaptação: feito e pendente

O plano era levar a base 3 (só os erros, em parquet) para o método das bases 1 e 2, em Python, com o painel no fim.

| Fase | Situação | O que foi feito / o que ficou |
|---|---|---|
| **0** · Conferir o que já existia | **Feita** | Código e schema do parquet conferidos; o código passou a existir nos dois ambientes |
| **1** · Base do pipeline, verificada na base 1 | **Feita** | A query da base 3 reescrita em Python (`validacao/porta_query_v1.py`) e comparada erro a erro com o pipeline da base 1: 498 erros, 415 na mesma unidade, 83 pendentes, 0 em unidade errada. Sem `analysis/etl/` próprio, sem `base.json`, sem `seguidor` opcional: o modo observado cobre |
| **2** · Rodar a base 3 | **Feita, com um resto** | Rodada oficial `0d23103…` (76% classificados) e, depois do Ajuste 17, `3f9c2806…` (14/10): **94% classificados**, 10 candidatas, 1 sinal de harness, resíduo 1,8%. **Resto:** medir quantos códigos e observações bateram no corte (só o da mensagem foi medido) → #14 |
| **3** · Depois do erro, custo, versão; suspeitas e protocolo | **Em parte** | Há o gráfico e os perfis do que vem depois do erro, por candidata. **Pendente:** custo da janela completa, unidade por versão → #15; suspeitas e protocolo por papel, mês e versão → #16 |
| **4** · Relatório e pedido de dados | **Feita** | `01` a `05` em `docs/` |
| **5** · Kit e auditoria independente | **Não feita** | → #17 |
| **6** · Painel | **Feita e rodada** | `executar.py painel`, 7 gráficos de leitura; leituras no relatório (#10), refeitas em 14/10 para a rodada `3f9c…`. A figura de destinos foi corrigida e o painel gerado de novo (#27) |
| **7** · Quando a v2 e a agregada chegarem | **Aguarda o tutor** | O pedido A está com o tutor; B e C a fechar, com os dois parquets novos → #2 e #26 |
| **Documentos gerais** (glossário, livro-razão, `analysis/README`, `kit.md`) | **Não feita** | → #18 |
| **Teste de equivalência** `triagem_observada` × `bp.triagem` na suíte | **Só como script** | → #19 |

## Backlog — em ordem de valor

- [ ] **#2** **Fechar os pedidos de dados** ([`05`](05-pedido-queries.md)): **A** (denominadores) já está com o tutor e não
  recebe mais colunas; **B** (complemento dos pendentes) ficou só com os 1.289 que a janela não traz — falta decidir se
  leva o nome do modelo e o hash do system prompt; **C** (ajustes na extração) precisa ser revisto com o que 13–14/10
  ensinaram. **Decisões abertas:** (a) o nome do modelo e o hash do system prompt vão no B ou no C? (a base 3 não tem o
  prompt, e a causa do `try/except` só foi provada na base 2); (b) do C, o que sai e o que entra — agente na partição,
  texto ausente como comprimento zero, "Error calling tool", todas as ferramentas do passo; (c) o `05` ainda descreve
  A como "a enviar" e traz modelo e prompt no C, de antes do Ajuste 17. **Falta:** fechar B e C com os parquets de #26,
  atualizar o `05`, levar ao tutor (#11) e, quando A chegar, conferir a junção (soma de erros e suspeitas = 30.141 e
  1.280) e integrar ao pipeline.
- [ ] **#26** **Os dois parquets novos (recebidos em 14/10):** conferir só o schema (nomes de colunas, sem dado) de cada
  um — qual base, qual período, se já são a v2 ou o pedido A — e decidir o que sai de B e C → #2.
- [ ] **#11** **Apresentação ao tutor** com o painel (relatório + gráficos) e o pedido de dados ([`05`](05-pedido-queries.md)):
    o método transfere (com um ajuste, o 17), os erros moram em poucos papéis, a maior unidade é um sinal de harness (o
    `try/except NameError`, 5.764 erros) e o maior problema isolado de protocolo é o `H_bloco_code`, e o que falta para
    as taxas e para os 6% pendentes. Depende de #2 e #26.
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
    por erro é o contexto acumulado, a leitura do gráfico frequência × custo.
- [ ] **#14** **Contrato da fonte completo (e0):** contar quantas mensagens, códigos e observações bateram no corte de tamanho
    (hoje só a mensagem: 1.009) e quantos "Could not index" perderam o `KeyError` do fim — a limitação 1 medida na
    própria base 3, e não só na base 1.
- [ ] **#15** **Depois do erro, completo (e4):** a recuperação em n+1 e n+2 recalculada das colunas (sem usar o
    `recovery_signal` pronto da query); o custo da janela só quando ela está completa (`has_full_2_action_window`); a
    unidade por versão do agente ("aparece ou some"), para o critério "ainda relevante".
- [ ] **#16** **Trilhas paralelas (e5):** as suspeitas da query por padrão × papel × mês (só contagem); o protocolo do harness
    por papel, mês e versão. O que não der na extração vai para o relatório como indisponível.
- [ ] **#17** **Kit e auditoria independente (Fase 5):** o kit chamando o `executar.py` na preparação; o `conferir_versao`
    cobrindo o código novo; as skills consultando a capacidade (a das falhas silenciosas para na base 3 e explica);
    um `audit_recompute` independente da base 3 (só biblioteca padrão e `leitor_trace`) e o encontro com as tabelas.
- [ ] **#3** **Protocolo do harness:** resposta sem bloco de código (`H_bloco_code`, 4.592 erros em 4.030 execuções, 14
  papéis, 10 meses). Racionais, relatório e procedimento próprios, como na base 1.
- [ ] **#4** **Críticos:** as 25 execuções que esgotaram os passos (`C_limite_passos`) — o caminho de erros até o fim de cada uma.
- [ ] **#5** **Resíduos:** os 538 erros de causa ou sintoma não reconhecidos — padrões recorrentes e regra nova, se houver
  (regra nova só olhando as duas bases).
- [ ] **#6** **Conferir o timeout de ferramenta** (`H_timeout_ferramenta`: 1.117 erros num mês e num papel) — incidente pontual
  ou padrão. O gráfico linha do tempo (item 9) já mostra o mês.

## Fora de escopo / adiado

- **Aviso a quem cuida do harness** sobre o `try/except NameError` (`transversal #7`): decisão de 14/10 de não fazer agora;
  a evidência está em [`02` §7.9–7.10](02-relatorio-achados.md#79--a-causa-uma-instrução-do-prompt-que-o-ambiente-de-execução-não-suporta-base-2-1310).
- **Se o parágrafo da instrução já estava no prompt de julho** (base 2): é do [`b2 #3`](../../2026-09-trace-law-flow-second/docs/04-roadmap.md).

## Fechado

Cada linha: o que foi feito → o commit ou o documento (a prova).

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
