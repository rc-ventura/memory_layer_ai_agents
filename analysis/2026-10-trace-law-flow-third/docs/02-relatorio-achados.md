# Relatório de achados — base 3 (erros com contexto), rodada observada

> Códigos de unidade e siglas: [glossário](../../glossario.md). Cada código aparece junto do nome da lição.

**Data:** 08/10/2026, com as leituras do painel (§7) de 09/10/2026 · **Fonte:** `base_erros_minerados_full.parquet` (máquina 2), SHA-256
`7604f77df9fe6127bd7fb9db18337b558b1f2587b0a99621c087b0cf3c2873f1` — saída da query
`ICTI_crossmemory_query_mineracao_erros`, execuções iniciadas entre ago/2025 e set/2026.
**Rodada:** `observada_b4fcc7711a9ec8a6` (09/10), estado `concluida_tecnicamente_sem_aprovacao_semantica`. É a
`observada_0d23103afd4fc0f4` de 08/10 com outro id, porque o código mudou (painel e tabelas novas); as contagens são
as mesmas (30.141 erros, 23.034 observáveis, 7.107 pendentes, 17 unidades, 10 candidatas, 538 no resíduo).
**Por que a análise é assim:** [`01-racionais.md`](01-racionais.md). **Como foi conferido e como reproduzir cada
número:** [`03-procedimento-validacao.md`](03-procedimento-validacao.md).

**Onde está a evidência.** Os arquivos da rodada ficam na máquina 2, em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/observada_b4fcc7711a9ec8a6/` (abaixo, `<rodada>/`). Cada
tabela deste relatório diz de que arquivo vem. Identificadores de execução e texto de caso não saem da máquina 2: os
casos de cada candidata estão em `<rodada>/perfis/<unidade>/casos.csv`.

---

## TL;DR

- **30.141 erros estruturados** em 20.986 execuções. **76% (23.034) caem numa unidade** pelas regras de sempre;
  **24% (7.107) ficam pendentes** porque a janela da query não traz o dado que a regra precisa.
- **10 candidatas a memória** passam na régua de recorrência (≥3 execuções, ≥2 meses). Juntas somam 16.741 erros e
  **362 milhões de tokens — 61% dos tokens de todos os erros**.
- As três maiores em tokens: **retorno pode chegar como string** (`U_tipo_retorno`, 170 mi),
  **inventário do sandbox** (`U_sandbox`, 70 mi) e **ferramentas só aceitam argumento nomeado** (`U_arg_nomeado`, 52 mi).
- **A taxonomia cobre a base 3:** o resíduo é 538 erros (1,8%), abaixo do alarme de 5%.
- **A maior unidade isolada não é memória:** o agente responder sem bloco de código (`H_bloco_code`, 4.592 erros) —
  protocolo do harness.
- **O maior grupo pendente** são 5.818 erros de nome não definido sem passo anterior identificado (102 mi de tokens) —
  vira a primeira investigação ([roadmap](04-roadmap.md) #1). **Eles estão concentrados:** pelo menos 5.708 (98%) são
  de agosto de 2026, e 5.310 (91%) são de um papel num mês só ([§7](#7--leituras-do-painel)).
- **O painel (§7) mostra três padrões:** o custo por erro e a frequência são coisas diferentes (o retorno-string pesa
  pelos dois, o protocolo do harness só pela frequência); dois papéis têm 58% dos erros das candidatas; e agosto de
  2026 concentra quase metade dos erros observáveis — sem denominador, não dá para dizer se foi mais execução ou mais
  erro por execução.

---

## 1 · O que entrou

| Medida | Valor |
|---|---:|
| Linhas do parquet | 31.421 |
| Erros estruturados (a taxonomia oficial) | 30.141 |
| Suspeitas da query (fora da taxonomia) | 1.280 |
| Execuções com erro (execução + agente) | 20.986 |
| Tokens em todos os erros estruturados | 592.858.874 |
| Erros sem tokens ou sem duração | 0 |

Fonte: `<rodada>/manifesto.json` (bloco `resumo`) e `cobertura_sintomas.csv`.

## 2 · Cobertura: o que as regras conseguem decidir

| Situação | Motivo | Erros | Tokens (mi) |
|---|---|---:|---:|
| observável | regra pela mensagem (inteira) | 19.669 | 398,8 |
| observável | sinais suficientes para a regra de código mal formado | 2.010 | 22,2 |
| observável | nome não definido com o erro anterior visível na janela | 1.355 | 28,7 |
| **pendente** | **nome não definido sem passo anterior identificado** | **5.818** | **101,7** |
| pendente | mensagem cortada em 20.000 caracteres | 1.009 | 37,4 |
| pendente | timeout sem o prompt e o código que a regra precisa | 215 | 2,3 |
| pendente | linha rejeitada sem o código inteiro | 46 | 1,1 |
| pendente | histórico insuficiente para separar retorno colado | 14 | 0,3 |
| pendente | numeração ambígua do passo anterior | 5 | 0,3 |
| **Total** | | **30.141** | **592,9** |

Fonte: `<rodada>/cobertura_mecanismos.csv`.

**Leitura.** Três quartos dos erros e três quartos dos tokens (449,7 mi) caem numa unidade. Os pendentes não são
resíduo: a regra existe, faltou o dado ([racionais §3](01-racionais.md#3--pendente-não-é-resíduo)). O corte de 20.000
caracteres responde por 1.009 erros; o teste na base 1 mostra que ele apaga sobretudo o retorno-dict (§4). Onde estão
os pendentes, por papel e mês: [§7](#7--leituras-do-painel).

## 3 · Triagem: o destino de cada unidade

| Unidade | Lição | Decisão | Erros | Execuções | Meses | Papéis | Tokens (mi) |
|---|---|---|---:|---:|---:|---:|---:|
| `U_tipo_retorno` | Retorno pode chegar como string | candidata | 4.317 | 3.042 | 10 | 17 | 169,9 |
| `U_sandbox` | Inventário do sandbox | candidata | 3.653 | 3.451 | 10 | 16 | 69,6 |
| `U_arg_nomeado` | Ferramentas só aceitam argumento nomeado | candidata | 3.927 | 2.390 | 10 | 11 | 51,6 |
| `U_campo_inexistente` | Campo inexistente no retorno estruturado | candidata | 1.566 | 1.468 | 9 | 9 | 24,0 |
| `U_estado_perdido` | Após passo com erro, o que ele definiria não existe | candidata | 878 | 834 | 10 | 12 | 19,8 |
| `U_nome_inventado` | Nome usado sem ter sido definido | candidata | 477 | 461 | 10 | 10 | 8,9 |
| `U_texto_solto` | Explicação nunca solta no bloco de código | candidata | 180 | 68 | 9 | 8 | 8,0 |
| `U_repr_colado` | Não colar retorno impresso de volta no código | candidata | 1.587 | 1.547 | 7 | 3 | 6,4 |
| `U_texto_literal` | Texto longo nunca dentro de literal de string | candidata | 141 | 129 | 10 | 12 | 3,3 |
| `U_next_gerador` | `next()` sobre expressão geradora falha no sandbox | candidata | 15 | 13 | 6 | 4 | 0,2 |
| `C_limite_passos` | Limite de passos atingido | investigar — crítico | 25 | 25 | 9 | 4 | 2,5 |
| `H_bloco_code` | Protocolo do harness (resposta sem bloco de código) | não-memória | 4.592 | 4.030 | 10 | 14 | 34,8 |
| `H_timeout_ferramenta` | Ferramenta excedeu o timeout | não-memória | 1.117 | 1.096 | 1 | 1 | 28,9 |
| `H_infra_llm` | Falha do LLM upstream | não-memória | 19 | 16 | 6 | 4 | 0,5 |
| `U_contrato_dict` | Retorno das ferramentas de documento é dict | recorrência não demonstrada | 2 | 2 | 1 | 1 | 0,0 |
| `X_causa_nao_identificada` | Causa não identificada | revisar — prioridade | 350 | 281 | 9 | 12 | 16,2 |
| `X_sintoma_nao_reconhecido` | Sintoma não reconhecido | revisar — prioridade | 188 | 178 | 9 | 11 | 5,0 |

Fonte: `<rodada>/triagem_visivel_observada.csv`; régua estrita em `triagem_sensibilidade.csv`; por papel em
`triagem_por_papel.csv`. Os erros somam 23.034 (os observáveis). Execuções se sobrepõem entre unidades: não somar.
Figuras da rodada: `<rodada>/unidades_observadas.png` (tokens por unidade), `<rodada>/papel_unidade.png` (papel ×
unidade) e `<rodada>/genealogia_observada.png` (a genealogia completa, com os pendentes num caminho próprio).

**Leitura.**

- **As 10 candidatas recorrem em quase todo o período.** Oito delas aparecem em 9 ou 10 dos meses. Recorrência aqui é
  medida só nos erros observáveis; a régua estrita (≥5 execuções, ≥3 meses) está em `triagem_sensibilidade.csv`.
- **Três candidatas concentram 71% dos erros das candidatas** (11.897 de 16.741) e **delas vem 80% dos tokens das
  candidatas** (291 de 362 mi). São as três de contrato com o ambiente: o retorno que pode vir como texto, o que existe
  no sandbox e a forma de chamar as ferramentas.
- **Quase toda candidata se concentra em poucos papéis, mesmo quando aparece em muitos.** Pelo mapa papel × unidade
  (`papel_unidade.png`; células lidas da figura da rodada, que somam os totais da triagem):
  o retorno-string está em 17 papéis, mas 5 deles têm 4.167 dos 4.317 erros (97%); o argumento nomeado está em 11,
  mas 1 papel tem 2.613 dos 3.927 erros (67%); o inventário do sandbox está em 16, mas 1 papel tem 2.674 dos 3.653
  (73%); o campo inexistente está em 9, mas 1 papel tem 1.398 dos 1.566 (89%); o retorno colado de volta no código
  está em 3, e 1 papel tem 1.583 dos 1.587 (99,7%). "Aparece em N papéis" não quer dizer que a lição vale para N papéis:
  a decisão entre lição geral e lição de um papel sai de `triagem_por_papel.csv`, na mineração de cada candidata.
  Contagem de erros não é taxa: um papel que roda mais erra mais em número absoluto.
- **Reincidência dentro da execução:** a explicação solta no bloco de código tem 180 erros em 68 execuções (2,6 por
  execução); nas demais candidatas a razão fica entre 1,0 e 1,7 erro por execução.
- **O retorno-dict quase some (2 erros) por causa do corte**, não porque deixou de acontecer (§4).
- Nenhuma destas decisões é memória aprovada: candidata quer dizer "recorrente o suficiente para minerar". O destino
  (memória ou harness) sai da mineração de cada uma ([roadmap](04-roadmap.md)).

## 4 · O que não é memória, mas aparece grande

- **Resposta sem bloco de código (`H_bloco_code`): 4.592 erros em 4.030 execuções, 10 meses, 14 papéis.** É a maior
  unidade isolada. O agente responde fora do envelope `<code>` que o harness espera — falha de protocolo. Vai para a
  frente do protocolo do harness, como nas bases 1 e 2 ([roadmap](04-roadmap.md) #3).
- **Timeout de ferramenta (`H_timeout_ferramenta`): 1.117 erros, 1 mês, 1 papel, 28,9 mi de tokens.** Concentrado num
  mês e num papel — compatível com um incidente pontual de infraestrutura. É uma observação, a conferir
  ([roadmap](04-roadmap.md) #6).
- **Limite de passos (`C_limite_passos`): 25 execuções que esgotaram os passos.** Não é lição, é o fim de uma cadeia: o
  passo crítico está nos erros anteriores de cada uma ([roadmap](04-roadmap.md) #4).

## 5 · Resíduo: o que a taxonomia não explica

538 erros (350 com causa não identificada, 188 com sintoma não reconhecido) — **1,8% dos erros estruturados**, abaixo
do alarme de cobertura de 5%. Os dois baldes têm padrão recorrente (≥3 execuções, ≥2 meses), por isso estão em
"revisar — prioridade": é trabalho de taxonomia, não de memória ([roadmap](04-roadmap.md) #5). Fonte:
`<rodada>/triagem_visivel_observada.csv`.

## 6 · Limitações que afetam a leitura

Medidas no [procedimento §4](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Em resumo: sem
denominador não há taxa; a mensagem cortada esconde o retorno-dict; as falhas silenciosas não estão no arquivo;
ocorrências são condicionais aos vínculos da janela; e há sinal de que a extração pode ter deixado de fora execuções
sem resposta final (99,9% das execuções com erro têm resposta gravada, contra 11% na base 1).

## 7 · Leituras do painel

Fonte: `<rodada>/painel/painel.md` e as figuras da pasta, mais as linhas de `consolidacao_pendencias_papel_mes.csv`
fotografadas na máquina 2. Todos os números abaixo foram lidos das fotos de 09/10 e **conferidos contra as tabelas das
seções 2 e 3** (os valores por mês somam o total de cada unidade; os por papel somam 16.741; as linhas dos pendentes
somam 5.817 dos 5.818, a que falta está acima do corte da foto). Contagem de erros não é taxa
([§6](#6--limitações-que-afetam-a-leitura)).

### 7.1 · Os pendentes estão concentrados num papel e num mês

Os 5.818 erros de nome não definido sem passo anterior identificado, pelas linhas do CSV (a soma das linhas lidas é
5.817 erros e 101,7 mi de tokens; falta 1 erro, provavelmente uma linha acima do corte da foto):

| Papel | Mês | Erros | Tokens |
|---|---|---:|---:|
| `ontestacaoCivel` | 2026-08 | 5.310 | 99,6 mi |
| `RoteadorCivel` | 2026-08 | 397 | 1,1 mi |
| `ontestacaoCivel` | 2026-07 | 16 | 0,3 mi |
| `RespostaBacen` | 2026-02 a 2026-06 (5 meses) | 89 | 0,7 mi |
| `AnaliseProcessual` (2026-08), `CalculoCivel` (2026-03), `OBPCivel` (2026-07) | | 5 | 0,03 mi |

- **Um papel e um mês têm 91% do grupo** (5.310 de 5.818); agosto sozinho tem **pelo menos 98%** (5.708). O gráfico
  de pendentes do painel mostra o mesmo: o papel com mais pendentes tem 90% de todos os 7.107.
- **O que isso muda na investigação ([roadmap](04-roadmap.md) #1):** a amostra e a leitura de caso deixam de ser "a
  base inteira" e passam a ser `ontestacaoCivel` em agosto. Isso estreita onde olhar; **não diz a causa**. As quatro
  hipóteses do roadmap seguem em aberto. A contagem que falta é a divisão dos 5.310 entre primeiro ActionStep do papel
  e passo anterior sem número.
- **Não medido:** a divisão dos 1.009 de mensagem cortada por papel e mês (as linhas não foram fotografadas).

### 7.2 · Para onde vão os erros e os tokens

| Destino | % dos erros | % dos tokens |
|---|---:|---:|
| candidatas a memória | 56% | 61% |
| harness / infra (não-memória) | 19% | 11% |
| pendente (falta dado na extração) | 24% | 24% |
| resíduo, crítico e sem recorrência | o restante | o restante |

Conferido com a triagem: os tokens das candidatas são 361,7 mi de 592,9 mi (61%). O harness gasta menos tokens do que
a sua fatia de erros: é frequente e barato.

### 7.3 · Frequência e custo por erro são coisas diferentes

Tokens por erro, de `triagem_visivel_observada.csv` (tokens ÷ erros; a média das observáveis é de 19,5 mil, a linha do
gráfico):

| Unidade | Erros | Tokens por erro |
|---|---:|---:|
| `C_limite_passos` | 25 | 100 mil |
| `X_causa_nao_identificada` | 350 | 46 mil |
| `U_texto_solto` | 180 | 44 mil |
| `U_tipo_retorno` | 4.317 | 39 mil |
| `H_timeout_ferramenta` | 1.117 | 26 mil |
| `U_estado_perdido` | 878 | 23 mil |
| `U_sandbox` | 3.653 | 19 mil |
| `U_campo_inexistente` | 1.566 | 15 mil |
| `U_arg_nomeado` | 3.927 | 13 mil |
| `H_bloco_code` | 4.592 | 7,6 mil |
| `U_repr_colado` | 1.587 | 4,0 mil |

- **O retorno-string pesa pelos dois lados:** é frequente e cada erro custa o dobro da média. É por isso que lidera em
  tokens (29%).
- **O protocolo do harness e o retorno colado de volta no código pesam só pela frequência:** o erro é barato.
- **Tokens por erro são os do passo com erro, sem a recuperação.** O ranking por tokens, sozinho, não ordena o que vale
  minerar. A leitura provável é que o custo reflete o contexto acumulado até o erro, e não a gravidade dele; **não
  confirmada**: depende da divisão entre tokens de entrada e de saída ([roadmap](04-roadmap.md) #13).

### 7.4 · Poucos papéis concentram as candidatas

Erros das candidatas por papel (figura de papéis do painel; os 13 grupos somam os 16.741 erros): `RoteadorCivel` 5.028,
`ontestacaoCivel` 4.739, `RespostaBacen` 2.386, `CalculoTrabalhista` 1.558, `OBFCivel` 1.347, `JoogleAnalytics` 1.190.

- **Dois papéis têm 58% dos erros das candidatas** (9.767 de 16.741) e **seis têm 97%** (16.248). São 6 dos 21 papéis
  que têm erro de candidata.
- Por candidata, o papel que mais pesa (figura de concentração): campo inexistente, `RespostaBacen` 89%; retorno colado,
  `RoteadorCivel` 100%; argumento nomeado, `RoteadorCivel` 67%; inventário do sandbox, `ontestacaoCivel` 73%;
  nome inventado, `RoteadorCivel` 44% e `ontestacaoCivel` 29%; estado perdido, `ontestacaoCivel` 45% e `RoteadorCivel`
  37%; texto solto, `CalculoTrabalhista` 33%, `ontestacaoCivel` 32% e `JoogleAnalytics` 20%; retorno-string,
  `ontestacaoCivel` 32% e `RespostaBacen` 21%, a mais espalhada.
- **O que isto pede:** a mineração de cada candidata começa por perguntar se a lição vale para todos os agentes ou só
  para o papel que concentra os erros. Sem o número de execuções por papel, não se sabe se o papel erra mais ou roda
  mais (pedido A, [`05`](05-pedido-queries.md)).

### 7.5 · O padrão no tempo: agosto de 2026 concentra quase metade

Erros observáveis por unidade e mês (os valores de cada linha somam o total da unidade na triagem, conferido nas 17
linhas):

| Unidade | Total | Mês de maior valor | No pico |
|---|---:|---|---:|
| `H_bloco_code` | 4.592 | 2026-08 | 4.153 |
| `U_tipo_retorno` | 4.317 | 2026-08 | 1.928 |
| `U_arg_nomeado` | 3.927 | 2026-07 | 1.810 (ago: 834) |
| `U_sandbox` | 3.653 | 2026-07 | 2.029 (ago: 1.081) |
| `U_repr_colado` | 1.587 | 2026-07 | 686 (primeiro erro em 2026-02; 45 em maio) |
| `U_campo_inexistente` | 1.566 | 2026-05 | 476 (jul: 24; ago: 52) |
| `H_timeout_ferramenta` | 1.117 | 2026-08 | 1.117 (só esse mês) |
| `U_estado_perdido` | 878 | 2026-08 | 668 |
| `U_nome_inventado` | 477 | 2026-08 | 343 |

- **Agosto de 2026 tem 10.963 dos 23.034 erros observáveis (48%)**, e mais pelo menos 5.708 dos pendentes. Os erros de
  protocolo do harness (90% em agosto) e o timeout (só em agosto) se concentram nesse mês.
- **O retorno colado de volta no código começa tarde:** o primeiro erro é de fevereiro (1), são 45 em maio e 389 em
  junho; o pico é julho (686). O argumento nomeado (1.810) e o inventário do sandbox (2.029) têm o pico em julho e caem em
  agosto (834 e 1.081); o retorno-string e o protocolo do harness têm o pico em agosto.
- **O campo inexistente subiu até maio e caiu a 24 e 52 em julho e agosto.** Pode ter sido corrigido, ou o papel rodou
  menos; sem o denominador, é só uma observação a verificar na mineração dele.
- **O timeout em um mês e um papel segue compatível com incidente pontual**, como na §4; continua em aberto
  ([roadmap](04-roadmap.md) #6).
- **O que não dá para dizer:** se agosto teve mais execuções ou mais erro por execução. Essa é a pergunta que o pedido
  A responde, e a que muda a leitura de metade desta seção.

### 7.6 · O que vem depois do erro

Passo seguinte ao erro, por candidata (figura do painel; percentuais lidos da figura, e o que não é "sem erro" ou
"novo erro" é pequeno e não rotulado):

| Candidata | Passo seguinte sem erro | Novo erro (cascata) | O passo seguinte é a resposta final |
|---|---:|---:|---:|
| `U_texto_solto` | 37% | 63% | 23% |
| `U_arg_nomeado` | 63% | 36% | 18% |
| `U_tipo_retorno` | 64% | 30% | 22% |
| `U_sandbox` | 71% | 28% | 48% |
| `U_texto_literal` | 81% | 19% | 50% |
| `U_estado_perdido` | 85% | 14% | 30% |
| `U_nome_inventado` | 86% | 13% | 15% |
| `U_next_gerador` | 87% | 13% | 7% |
| `U_campo_inexistente` | 88% | 11% | 77% |
| `U_repr_colado` | 96% | ~4% | 4% |

- **A explicação solta no bloco de código é a única em que o agente erra de novo na maioria das vezes** (63%), e cada
  erro dela é dos mais caros (44 mil tokens): é onde uma memória teria mais a ganhar, apesar de ter só 180 erros.
- **Sem erro no passo seguinte não é sucesso:** pode ser outro problema que não é erro estruturado. A janela é de um
  passo; o fim da execução não está no arquivo.
- **"O seguinte é a resposta final" tem leitura dupla:** no campo inexistente (77%), no texto longo em literal (50%) e no
  inventário do sandbox (48%) o agente parece resolver e entregar, ou desistir e entregar; a janela não diz qual dos dois.

### 7.7 · O que o painel não mostra

Sem taxas (denominador), sem os passos sem erro, sem falhas silenciosas, sem tokens de entrada × saída por unidade, e
sem a recuperação além do passo n+2. Cada ausência está no [roadmap](04-roadmap.md) (#13, #15, #16) ou no
[pedido de dados](05-pedido-queries.md).
