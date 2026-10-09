# Roadmap — o backlog numerado da base 3

> Códigos e siglas: [glossário](../../glossario.md). O schema deste roadmap (o mesmo de todos) está em
> [`../../plano-atual.md`](../../plano-atual.md); as decisões em vigor, em [`../../decisoes.md`](../../decisoes.md); o que
> atravessa as bases, em [`../../roadmap-transversal.md`](../../roadmap-transversal.md). Os números são estáveis: um
> item feito é marcado `[x]` e desce para "Fechado" com a prova, sem mudar de número. **Os números deste arquivo são da
> base 3**; de fora, cite como `b3 #N` (o "roadmap #N" sem prefixo, nos docs antigos, é o da base 1).

Contexto: [relatório](02-relatorio-achados.md) da rodada `observada_0d23103afd4fc0f4` e
[limitações medidas](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Atualizado em 09/10/2026
(branch `2026-10-09-roadmaps-schema`).

## O plano de adaptação: feito e pendente

O plano era levar a base 3 (só os erros, em parquet) para o método das bases 1 e 2, em Python, com o painel no fim.

| Fase | Situação | O que foi feito / o que ficou |
|---|---|---|
| **0** · Conferir o que já existia | **Feita** | Código e schema do parquet conferidos; o código passou a existir nos dois ambientes |
| **1** · Base do pipeline, verificada na base 1 | **Feita** | A query da base 3 reescrita em Python (`validacao/porta_query_v1.py`) e comparada erro a erro com o pipeline da base 1: 498 erros, 415 na mesma unidade, 83 pendentes, 0 em unidade errada. Sem `analysis/etl/` próprio, sem `base.json`, sem `seguidor` opcional: o modo observado cobre |
| **2** · Rodar a base 3 | **Feita, com um resto** | Rodada oficial `0d23103…`: 76% classificados, 10 candidatas, resíduo 1,8%. **Resto:** medir quantos códigos e observações bateram no corte (só o da mensagem foi medido) → #14 |
| **3** · Depois do erro, custo, versão; suspeitas e protocolo | **Em parte** | Há o gráfico e os perfis do que vem depois do erro, por candidata. **Pendente:** custo da janela completa, unidade por versão → #15; suspeitas e protocolo por papel, mês e versão → #16 |
| **4** · Relatório e pedido de dados | **Feita** | `01` a `05` em `docs/` |
| **5** · Kit e auditoria independente | **Não feita** | → #17 |
| **6** · Painel | **Feita, falta rodar a versão final** | `executar.py painel`, com 7 gráficos de leitura → #9 |
| **7** · Quando a v2 e a agregada chegarem | **Aguarda o tutor** | O pedido está no [`05`](05-pedido-queries.md) → #2 |
| **Documentos gerais** (glossário, livro-razão, `analysis/README`, `kit.md`) | **Não feita** | → #18 |
| **Teste de equivalência** `triagem_observada` × `bp.triagem` na suíte | **Só como script** | → #19 |

## Backlog — em ordem de valor

- [ ] **#9** **Rodar o painel novo** (`executar.py conferir` e depois `executar.py painel`). Gera a rodada com a tabela dos
  pendentes por papel e mês e os 10 perfis, e os 7 gráficos de leitura (destinos, frequência × custo, concentração por
  papel, papéis, linha do tempo, depois do erro, pendentes). A rodada muda de id (o código mudou); as contagens da
  triagem têm que continuar as mesmas — se mudarem, é erro a investigar antes de seguir.
- [ ] **#10** **Atualizar o relatório com as leituras do painel**, só depois do item 9 e com os números da rodada nova: custo por
    erro × frequência (o ranking por tokens mede o contexto, não a gravidade), dois papéis com mais da metade dos
    erros das candidatas, o protocolo do harness em cerca de 1 de cada 5 execuções com erro, o padrão no tempo
    (timeout num mês só; retorno colado em 7 meses) e o que vem depois do erro. Hoje essas leituras são contas feitas
    a partir das fotos — entram no relatório quando o gráfico da rodada as mostrar.
- [ ] **#11** **Apresentação ao tutor** com o painel (relatório + gráficos) e o pedido de dados ([`05`](05-pedido-queries.md)):
    o método transfere sem regra nova, os erros moram em poucos papéis, o maior problema isolado é de protocolo, e o
    que falta para as taxas e para os 24% pendentes.
- [ ] **#2** **Pedido de dados complementares** — escrito em [`05-pedido-queries.md`](05-pedido-queries.md) (09/10): A
  denominadores (taxas e gráficos de custo da base 1), B complemento dos pendentes (fecha os 24% sem unidade), C
  ajustes na extração. **Falta:** levar ao tutor (item 11) e, quando chegar, conferir a junção e integrar ao pipeline.
- [ ] **#1** **Investigar os 5.818 erros de nome não definido sem passo anterior identificado** (102 mi de tokens, o maior
  grupo pendente). Esse motivo cobre dois casos: não há passo anterior (primeiro ActionStep do papel) ou há, sem
  `step_number` — a proporção na base 3 não foi medida. Primeiro só contagens: os dois casos, `step_number`, papel,
  mês e versão (o gráfico de pendentes do item 9 já mostra papel e mês), se o mesmo nome se repete entre execuções, o
  que o passo seguinte faz. Depois, amostra e leitura (skill `mineracao-investigacao`). Só então decidir a unidade —
  as hipóteses levam a destinos diferentes (estado esperado de uma chamada anterior, variável que o harness deveria
  injetar, nome citado pela tarefa ou pelo prompt, nome inventado). O pedido B do [`05`](05-pedido-queries.md) traz
  as marcas que separam essas hipóteses.
- [ ] **#18** **Documentos gerais** (a dívida mais concreta): o glossário ganha `STRUCTURED_ERROR`, `OBSERVATION_SUSPECT`,
  "candidata observada", "pendente", "componente" (= a cascata das bases 1 e 2), `recovery_signal` e os estados de
  capacidade; o livro-razão (`pipeline-entre-bases.md`) ganha a etapa da base 3 — sem Ajuste novo, porque nenhuma
  regra mudou; o `analysis/README.md`, o intake por formato; o `kit.md`, o que o kit pode e não pode na base 3. Regra do
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

## Fechado

Cada linha: o que foi feito → o commit ou o documento (a prova).

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
