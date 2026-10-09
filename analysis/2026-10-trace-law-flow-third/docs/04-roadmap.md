# Roadmap — o backlog numerado da base 3

> Códigos e siglas: [glossário](../../glossario.md). O que fazer agora, em qualquer análise, fica em
> [`../../plano-atual.md`](../../plano-atual.md); este arquivo é o backlog da base 3. Os números são estáveis: um item
> fechado continua com o número dele.

Contexto: [relatório](02-relatorio-achados.md) da rodada `observada_0d23103afd4fc0f4` e
[limitações medidas](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Atualizado em 09/10/2026.

## Próximos — em ordem de valor

9. **Rodar o painel novo na máquina 2** (`executar.py conferir` e depois `executar.py painel`). Gera a rodada com a
   tabela dos pendentes por papel e mês e os 10 perfis, e os 7 gráficos de leitura (destinos, frequência × custo,
   concentração por papel, papéis, linha do tempo, depois do erro, pendentes). A rodada muda de id (o código mudou);
   as contagens da triagem têm que continuar as mesmas — se mudarem, é erro a investigar antes de seguir.
10. **Atualizar o relatório com as leituras do painel**, só depois do item 9 e com os números da rodada nova: custo por
    erro × frequência (o ranking por tokens mede o contexto, não a gravidade), dois papéis com mais da metade dos
    erros das candidatas, o protocolo do harness em cerca de 1 de cada 5 execuções com erro, o padrão no tempo
    (timeout num mês só; retorno colado em 7 meses) e o que vem depois do erro. Hoje essas leituras são contas feitas
    a partir das fotos — entram no relatório quando o gráfico da rodada as mostrar.
11. **Apresentação ao tutor** com o painel (relatório + gráficos) e o pedido de dados ([`05`](05-pedido-queries.md)):
    o método transfere sem regra nova, os erros moram em poucos papéis, o maior problema isolado é de protocolo, e o
    que falta para as taxas e para os 24% pendentes.
2. **Pedido de dados complementares** — escrito em [`05-pedido-queries.md`](05-pedido-queries.md) (09/10): A
   denominadores (taxas e gráficos de custo da base 1), B complemento dos pendentes (fecha os 24% sem unidade), C
   ajustes na extração. **Falta:** levar ao tutor (item 11) e, quando chegar, conferir a junção e integrar ao pipeline.
1. **Investigar os 5.818 erros de nome não definido sem passo anterior identificado** (102 mi de tokens, o maior
   grupo pendente). Esse motivo cobre dois casos: não há passo anterior (primeiro ActionStep do papel) ou há, sem
   `step_number` — a proporção na base 3 não foi medida. Primeiro só contagens na máquina 2: os dois casos,
   `step_number`, papel, mês e versão (o gráfico de pendentes do item 9 já mostra papel e mês), se o mesmo nome se
   repete entre execuções, o que o passo seguinte faz. Depois, amostra e leitura (skill `mineracao-investigacao`). Só
   então decidir a unidade — as hipóteses levam a destinos diferentes (estado esperado de uma chamada anterior,
   variável que o harness deveria injetar, nome citado pela tarefa ou pelo prompt, nome inventado). O pedido B do
   [`05`](05-pedido-queries.md) traz as marcas que separam essas hipóteses.
12. **Piloto de mineração de ponta a ponta: inventário do sandbox** (`U_sandbox`: 3.653 erros, 16 papéis). A lição
    sai da própria mensagem de erro, então fecha só com o parquet. **Antes:** decidir o localizador do arquivo final
    da memória — o [esquema](../../esquema-memoria.json) pede `idx`, que a base 3 não tem; a proposta é aceitar
    `step_ref` com a origem e a fonte.
7. **Minerar as demais candidatas, uma por vez**, pela ordem de tokens. Cada uma com racionais, relatório e
   procedimento próprios ([procedimento de mineração](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md)),
   destino decidido na base 3. Fecham só com o parquet: argumento nomeado, `next()` sobre gerador. Precisam do
   prompt ou do contrato da ferramenta (pedido C do `05`): retorno pode chegar como string, campo inexistente.
13. **Conferir tokens de entrada × saída por unidade** — contagem na máquina 2. Confirma (ou não) que o custo por
    erro é o contexto acumulado, a leitura do gráfico frequência × custo.
3. **Protocolo do harness:** resposta sem bloco de código (`H_bloco_code`, 4.592 erros em 4.030 execuções, 14
   papéis, 10 meses). Racionais, relatório e procedimento próprios, como na base 1.
4. **Críticos:** as 25 execuções que esgotaram os passos (`C_limite_passos`) — o caminho de erros até o fim de cada uma.
5. **Resíduos:** os 538 erros de causa ou sintoma não reconhecidos — padrões recorrentes e regra nova, se houver
   (regra nova só olhando as duas bases).
6. **Conferir o timeout de ferramenta** (`H_timeout_ferramenta`: 1.117 erros num mês e num papel) — incidente pontual
   ou padrão. O gráfico linha do tempo (item 9) já mostra o mês.

## Fechado

- **8 · Painel** (08–09/10): `executar.py painel` gera `<rodada>/painel/` com `painel.md` (resumo, cobertura,
  triagem), as figuras da rodada, a figura de cobertura e 7 gráficos de leitura, cada um com pergunta, como ler e
  limitação. Tudo calculado dos CSVs da rodada, com o hash de cada um conferido. Rodado na máquina 2 na versão com as
  tabelas (sem os 7 gráficos) — a versão completa é o item 9.
- **Documentação da base 3, do zero** (08–09/10): [`01`](01-racionais.md) racionais, [`02`](02-relatorio-achados.md)
  relatório, [`03`](03-procedimento-validacao.md) procedimento e limitações, este roadmap, [`05`](05-pedido-queries.md)
  pedido de dados. Os documentos de análises anteriores (07/10) estão em [`historico/`](historico/README.md).
- **Teste com resposta conhecida** (08/10): a base 1 pela mesma query da base 3 — 498 de 498 erros com par, 415 na
  mesma unidade, 83 pendentes, 0 em unidade errada. Ver [procedimento §3](03-procedimento-validacao.md#3--teste-com-resposta-conhecida-a-base-1-pela-mesma-query).
- **Rodada oficial** (08/10): `observada_0d23103afd4fc0f4`, igual à de 07/10; 46 verificações na máquina 2.
- **Adaptação do pipeline à base 3** (08/10): código da máquina 2 nas duas máquinas, orquestração só em Python
  (`executar.py`, sem notebooks), 162 testes (164 com o painel), validação sem depender de resultados antigos. Ver
  [procedimento §2](03-procedimento-validacao.md#2--o-que-foi-conferido).
