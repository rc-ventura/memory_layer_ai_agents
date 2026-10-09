# Roadmap — o backlog numerado da base 3

> Códigos e siglas: [glossário](../../glossario.md). O que fazer agora, em qualquer análise, fica em
> [`../../plano-atual.md`](../../plano-atual.md); este arquivo é o backlog da base 3. Os números são estáveis: um item
> fechado continua com o número dele.

Contexto: [relatório](02-relatorio-achados.md) da rodada `observada_0d23103afd4fc0f4` e
[limitações medidas](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas).

## Próximos — em ordem de valor

1. **Investigar os 5.818 erros de nome não definido sem passo anterior identificado** (102 mi de tokens, o maior
   grupo pendente). Primeiro só contagens na máquina 2: quantos não têm passo anterior × quantos têm passo anterior sem
   número; `step_number` deles; por papel, mês e versão; se o mesmo nome se repete entre execuções; o que o passo
   seguinte faz. Depois, amostra e leitura (skill `mineracao-investigacao`). Só então decidir a unidade — as
   hipóteses levam a destinos diferentes (estado esperado de uma chamada anterior, variável que o harness deveria
   injetar, nome citado pelo prompt, nome inventado).
2. **Pedido de dados complementares** — descrito em [`05-pedido-queries.md`](05-pedido-queries.md): A denominadores, B complemento dos pendentes (os 24%), C ajustes na extração. Origem:, a partir das 8 limitações medidas
   ([procedimento §4](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas)): mensagem sem corte (ou o
   fim dela), contagens de todos os passos (denominador), falhas silenciosas, partição com o agente, a chamada, o
   filtro de tamanho com `COALESCE`, o modelo e o prompt.
3. **Protocolo do harness:** resposta sem bloco de código (`H_bloco_code`, 4.592 erros, 14 papéis). Racionais,
   relatório e procedimento próprios, como na base 1.
4. **Críticos:** as 25 execuções que esgotaram os passos (`C_limite_passos`) — o caminho de erros até o fim de cada uma.
5. **Resíduos:** os 538 erros de causa ou sintoma não reconhecidos — padrões recorrentes e regra nova, se houver
   (regra nova só olhando as duas bases).
6. **Conferir o timeout de ferramenta** (`H_timeout_ferramenta`: 1.117 erros num mês e num papel) — incidente pontual
   ou padrão.
7. **Minerar as candidatas, uma por vez**, pela ordem de tokens: retorno pode chegar como string, inventário do
   sandbox, argumento nomeado, campo inexistente… Cada uma com racionais, relatório e procedimento próprios
   ([procedimento de mineração](../../2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md)), destino
   decidido na base 3.
8. **Painel:** uma pasta com as figuras da rodada e um MD com as tabelas do relatório, gerados por script a partir da
   rodada (sem números escritos à mão).

## Fechado

- **Adaptação do pipeline à base 3** (08/10): código da máquina 2 nas duas máquinas, orquestração só em Python
  (`executar.py`), 162 testes, 46 verificações, teste com a base 1 sem erro em unidade errada. Ver
  [procedimento §2–3](03-procedimento-validacao.md#2--o-que-foi-conferido).
