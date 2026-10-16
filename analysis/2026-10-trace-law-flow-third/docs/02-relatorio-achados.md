# Relatório de achados — base 3 (erros com contexto), rodada observada

> Códigos de unidade e siglas: [glossário](../../glossario.md). Cada código aparece junto do nome da lição.

**Data:** 08/10/2026; leituras do painel (§7) de 09/10; figuras refeitas em 15–16/10 (rodada `96958e65`); investigação do nome não definido (§7.8–7.10) de 13/10;
números das seções 1 a 7.7 atualizados em 14/10 para a rodada da extração v2 (Ajuste 18) · **Fonte:**
`base_erros_minerados_full_v2.parquet`, SHA-256 `908aa0052e61517a5727e0f2358b7187023ba12dffd11e0fb946e51f0ed86306` — a
query `ICTI_crossmemory_query_mineracao_erros` sem o corte de texto (as mesmas 31.421 linhas da v1, com o texto
inteiro), execuções iniciadas entre ago/2025 e set/2026.
**Rodada:** `observada_609c947b15295c84` (14/10), estado `concluida_tecnicamente_sem_aprovacao_semantica`, conferida
(46 verificações) — a primeira com o **Ajuste 18** ([livro-razão](../../pipeline-entre-bases.md)): 30.141 erros, 29.392
observáveis, 749 pendentes, 18 unidades, 10 candidatas, 565 no resíduo. Antes, na v1 (texto cortado):
`observada_3f9c2806cac9cd4d` (14/10, Ajuste 17), com 28.338 observáveis e 1.803 pendentes; e `observada_b4fcc7711a9ec8a6`
(09/10; igual à `0d23103afd4fc0f4` de 08/10), com 23.034 e 7.107.
**Por que a análise é assim:** [`01-racionais.md`](01-racionais.md). **Como foi conferido e como reproduzir cada
número:** [`03-procedimento-validacao.md`](03-procedimento-validacao.md).

**Onde está a evidência.** Os arquivos da rodada ficam no ambiente da base 3, em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/observada_609c947b15295c84/` (abaixo, `<rodada>/`). Cada
tabela deste relatório diz de que arquivo vem. Identificadores de execução e texto de caso não saem desse ambiente: os
casos de cada candidata estão em `<rodada>/perfis/<unidade>/casos.csv`.

---

## TL;DR

- **30.141 erros estruturados** em 20.986 execuções. **Em 97,5% (29.392) a regra tem a evidência para decidir**:
  95,6% (28.827) caem numa unidade reconhecida e 565 são resíduo (nenhuma regra reconheceu a causa);
  **2,5% (749) ficam pendentes** porque a janela da query não traz o dado que a regra precisa. Com o texto cortado (v1)
  eram 94% e 6%; antes do Ajuste 17, 76% e 24%.
- **10 candidatas a memória** passam na régua de recorrência (≥3 execuções, ≥2 meses). Juntas somam 17.308 erros e
  **387 milhões de tokens — 65% dos tokens de todos os erros**.
- As três maiores em tokens: **retorno pode chegar como string** (`U_tipo_retorno`, 207 mi),
  **inventário do sandbox** (`U_sandbox`, 70 mi) e **ferramentas só aceitam argumento nomeado** (`U_arg_nomeado`, 52 mi).
  O texto inteiro pôs 1.002 erros a mais no retorno-string (4.317 → 5.319), quase todos do ContestacaoCivel.
- **A taxonomia cobre a base 3:** o resíduo é 565 erros (1,9%), abaixo do alarme de 5%.
- **A maior unidade isolada não é memória:** o agente responder sem bloco de código (`H_bloco_code`, 4.592 erros) —
  protocolo do harness.
- **A maior unidade é um sinal de harness, não memória:** a verificação de existência por `try/except NameError`
  (`U_verificacao_try_nameerror`, 5.764 erros, 5.442 execuções, 112 mi de tokens). O system prompt do ContestacaoCivel
  instrui um padrão que o interpretador do sandbox não suporta; o agente falha no primeiro passo e se corrige no
  seguinte. Eram 5.304 dos 5.818 pendentes do primeiro passo e 460 erros que estavam no estado perdido e no nome
  inventado só pela posição (§7.8–7.10; Ajuste 17).
- **O painel (§7) mostra três padrões:** o custo por erro e a frequência são coisas diferentes (o retorno-string pesa
  pelos dois, o protocolo do harness só pela frequência); dois papéis têm 60% dos erros das candidatas; e agosto de
  2026 concentra 58% dos erros observáveis. **Com o denominador que chegou (pedido A), agosto teve mais execuções e mais
  erro por ActionStep:** 15,7% contra 6,7% em julho (§7.5).

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
| Mensagens de erro limitadas pelo corte | 0 (na v1: 1.009; a maior mensagem tem 833.507 caracteres) |

Fonte: `<rodada>/manifesto.json` (bloco `resumo`) e `cobertura_sintomas.csv`; o comprimento, do
`validacao/inspecionar_parquet.py` ([roadmap](04-roadmap.md) #26).

## 2 · Cobertura: o que as regras conseguem decidir

| Situação | Motivo | Erros | Tokens (mi) |
|---|---|---|---:|
| observável | mensagem de erro inteira basta — inclui a verificação por `try/except NameError` (5.764; Ajuste 17) | 26.441 | 548,3 |
| observável | sinais suficientes para a regra de código mal formado | 2.056 | 23,3 |
| observável | nome não definido com o erro anterior visível na janela | 895 | 16,1 |
| pendente | nome não definido sem passo anterior identificado e sem a assinatura | 514 | 2,2 |
| pendente | timeout sem o prompt e o código que a regra precisa | 215 | 2,3 |
| pendente | histórico insuficiente para separar retorno colado | 15 | 0,3 |
| pendente | numeração ambígua do passo anterior | 5 | 0,3 |
| **Total** | | **30.141** | **592,9** |

Fonte: `<rodada>/cobertura_mecanismos.csv`.

**Leitura.** Em 97,5% dos erros e 99% dos tokens (587,7 mi) a regra tem a evidência para decidir; tirando o resíduo (565 erros), 95,6% caem numa unidade reconhecida. Os pendentes não são resíduo: a regra
existe, faltou o dado ([racionais §3](01-racionais.md#3--pendente-não-é-resíduo)). Com o texto inteiro (Ajuste 18)
saíram da pendência os 1.009 erros de mensagem cortada e os 46 de linha rejeitada sem o código inteiro; o histórico
insuficiente ganhou 1 (14 → 15). O maior pendente agora são os 514 do primeiro passo sem a assinatura — outro mecanismo
(`RoteadorCivel` e `RespostaBacen`, §7.10). Os 215 timeouts seguem pendentes: o código inteiro veio, mas a regra também
pede as ferramentas declaradas no prompt.

## 3 · Triagem: o destino de cada unidade

| Unidade | Lição | Decisão | Erros | Execuções | Meses | Papéis | Tokens (mi) |
|---|---|---|---:|---:|---:|---:|---:|
| `U_tipo_retorno` | Retorno pode chegar como string | candidata | 5.319 | 3.480 | 10 | 17 | 207,0 |
| `U_sandbox` | Inventário do sandbox | candidata | 3.653 | 3.451 | 10 | 16 | 69,6 |
| `U_arg_nomeado` | Ferramentas só aceitam argumento nomeado | candidata | 3.927 | 2.390 | 10 | 11 | 51,6 |
| `U_campo_inexistente` | Campo inexistente no retorno estruturado | candidata | 1.569 | 1.470 | 9 | 9 | 24,2 |
| `U_estado_perdido` | Após passo com erro, o que ele definiria não existe | candidata | 544 | 508 | 10 | 12 | 10,1 |
| `U_texto_solto` | Explicação nunca solta no bloco de código | candidata | 190 | 76 | 9 | 9 | 8,3 |
| `U_repr_colado` | Não colar retorno impresso de volta no código | candidata | 1.588 | 1.547 | 7 | 3 | 6,5 |
| `U_nome_inventado` | Nome usado sem ter sido definido | candidata | 351 | 336 | 10 | 10 | 6,0 |
| `U_texto_literal` | Texto longo nunca dentro de literal de string | candidata | 152 | 140 | 10 | 12 | 3,6 |
| `U_next_gerador` | `next()` sobre expressão geradora falha no sandbox | candidata | 15 | 13 | 6 | 4 | 0,2 |
| `U_verificacao_try_nameerror` | Verificação de existência por try/except NameError | **sinal de harness** | 5.764 | 5.442 | 4 | 2 | 112,0 |
| `C_limite_passos` | Limite de passos atingido | investigar — crítico | 25 | 25 | 9 | 4 | 2,5 |
| `H_bloco_code` | Protocolo do harness (resposta sem bloco de código) | não-memória | 4.592 | 4.030 | 10 | 14 | 34,8 |
| `H_timeout_ferramenta` | Ferramenta excedeu o timeout | não-memória | 1.117 | 1.096 | 1 | 1 | 28,9 |
| `H_infra_llm` | Falha do LLM upstream | não-memória | 19 | 16 | 6 | 4 | 0,5 |
| `U_contrato_dict` | Retorno das ferramentas de documento é dict | recorrência não demonstrada | 2 | 2 | 1 | 1 | 0,0 |
| `X_causa_nao_identificada` | Causa não identificada | revisar — prioridade | 376 | 301 | 9 | 12 | 16,9 |
| `X_sintoma_nao_reconhecido` | Sintoma não reconhecido | revisar — prioridade | 189 | 179 | 9 | 11 | 5,0 |

Fonte: `<rodada>/triagem_visivel_observada.csv`; régua estrita em `triagem_sensibilidade.csv` (as 10 passam também
nela); por papel em `triagem_por_papel.csv`. Os erros somam 29.392 (os observáveis). Execuções se sobrepõem entre
unidades: não somar. Figuras da rodada: `<rodada>/unidades_observadas.png` (tokens por unidade),
`<rodada>/papel_unidade.png` (papel × unidade) e `<rodada>/genealogia_observada.png` (a genealogia completa, com os
pendentes num caminho próprio).

**Leitura.**

- **As 10 candidatas recorrem em quase todo o período.** Oito delas aparecem em 9 ou 10 dos meses. Recorrência aqui é
  medida só nos erros observáveis; a régua estrita (≥5 execuções, ≥3 meses) está em `triagem_sensibilidade.csv`.
- **Três candidatas concentram 75% dos erros das candidatas** (12.899 de 17.308) e **delas vem 85% dos tokens das
  candidatas** (328 de 387 mi). São as três de contrato com o ambiente: o retorno que pode vir como texto, o que existe
  no sandbox e a forma de chamar as ferramentas.
- **Quase toda candidata se concentra em poucos papéis, mesmo quando aparece em muitos.** Pelo mapa papel × unidade
  (`papel_unidade.png`; as colunas somam os totais da triagem): o retorno-string está em 17 papéis, mas 5 deles têm
  5.168 dos 5.319 erros (97%); o argumento nomeado está em 11, mas 1 papel tem 2.613 dos 3.927 erros (67%); o inventário
  do sandbox está em 16, mas 1 papel tem 2.674 dos 3.653 (73%); o campo inexistente está em 9, mas 1 papel tem 1.399 dos
  1.569 (89%); o retorno colado de volta no código está em 3, e 1 papel tem 1.584 dos 1.588 (99,7%). "Aparece em N
  papéis" não quer dizer que a lição vale para N papéis: a decisão entre lição geral e lição de um papel sai de
  `triagem_por_papel.csv`, na mineração de cada candidata. Contagem de erros não é taxa: um papel que roda mais erra
  mais em número absoluto.
- **Reincidência dentro da execução:** a explicação solta no bloco de código tem 190 erros em 76 execuções (2,5 por
  execução); nas demais candidatas a razão fica entre 1,0 e 1,6 erro por execução.
- **O retorno-dict continua com 2 erros, mesmo com a mensagem inteira — e não estava escondido.** Na base 1, o corte
  apagava sobretudo ele (o envelope `{'result': [...]}` indexado com `0`, que termina em `KeyError: 0`). Nas 1.009
  mensagens que a v1 cortava, esse fim aparece 0 vezes (2 na base inteira). Elas são quase todas do ContestacaoCivel
  (847) e terminam em `string indices must be integers`, que, no sandbox, só sai quando o valor indexado é **texto** —
  daí o retorno-string (1.002). **É o retorno da petição inicial chegando como texto JSON:** em 845 de 849 o valor
  começa com `{"` (o que um texto JSON dá; um dict daria `{'`), vem de `get_peticao_inicial_from_pasta` (727) ou
  `ingestao_peticao_inicial` (106), e no passo seguinte o agente desserializa em 93% — mas só 45% ficam sem erro. A
  base 2, com o trace inteiro, mostra o mesmo: 11 casos, todos `{"`, do ContestacaoCivel, da mesma ferramenta
  ([roadmap](04-roadmap.md) #34 e #35).
- **O estado perdido e o nome inventado ficaram menores e mais limpos** (878 → 544 e 477 → 351 erros; 19,8 → 10,1 e
  8,9 → 6,0 mi de tokens): os 460 erros do `try/except NameError` saíram deles (Ajuste 17). Os dois continuam
  passando na régua; o texto inteiro não os mudou.
- Nenhuma destas decisões é memória aprovada: candidata quer dizer "recorrente o suficiente para minerar". O destino
  (memória ou harness) sai da mineração de cada uma ([roadmap](04-roadmap.md)).

## 4 · O que não é memória, mas aparece grande

- **Verificação de existência por `try/except NameError` (`U_verificacao_try_nameerror`): 5.764 erros em 5.442
  execuções, 4 meses, 2 papéis, 112 mi de tokens — a maior unidade em erros e em execuções.** É erro do agente, mas o
  conserto é no ambiente: o system prompt do ContestacaoCivel manda verificar a variável com `except NameError`, e o
  interpretador do sandbox levanta outro erro, que esse `except` não pega. Sinal de harness, destino harness nas bases 2
  e 3 (§7.9–7.10; Ajuste 17); vai para o aviso a quem cuida do harness e para o monitoramento ([roadmap](04-roadmap.md) #1).
- **Resposta sem bloco de código (`H_bloco_code`): 4.592 erros em 4.030 execuções, 10 meses, 14 papéis.** É a maior
  unidade isolada. O agente responde fora do envelope `<code>` que o harness espera — falha de protocolo. Vai para a
  frente do protocolo do harness, como nas bases 1 e 2 ([roadmap](04-roadmap.md) #3).
- **Timeout de ferramenta (`H_timeout_ferramenta`): 1.117 erros, 1 mês, 1 papel, 28,9 mi de tokens.** Concentrado num
  mês e num papel — compatível com um incidente pontual de infraestrutura. É uma observação, a conferir
  ([roadmap](04-roadmap.md) #6).
- **Limite de passos (`C_limite_passos`): 25 execuções que esgotaram os passos.** Não é lição, é o fim de uma cadeia: o
  passo crítico está nos erros anteriores de cada uma ([roadmap](04-roadmap.md) #4).

## 5 · Resíduo: o que a taxonomia não explica

565 erros (376 com causa não identificada, 189 com sintoma não reconhecido) — **1,9% dos erros estruturados**, abaixo
do alarme de cobertura de 5%. Com o texto inteiro, a causa não identificada ganhou 26 erros e o sintoma não reconhecido,
1. Os dois baldes têm padrão recorrente (≥3 execuções, ≥2 meses), por isso estão em "revisar — prioridade": é trabalho
de taxonomia, não de memória ([roadmap](04-roadmap.md) #5). Fonte: `<rodada>/triagem_visivel_observada.csv`.

## 6 · Limitações que afetam a leitura

Medidas no [procedimento §4](03-procedimento-validacao.md#4--limitações-da-extração-v1-medidas). Em resumo: o corte da
mensagem acabou na v2 (Ajuste 18); o denominador chegou (pedido A, `base_contagens.parquet`) e se junta ao parquet sem
diferença, mas as taxas ainda não estão no pipeline nem no painel ([roadmap](04-roadmap.md) #32) — a taxa global é
10,6% dos ActionSteps; as falhas silenciosas não estão no arquivo; ocorrências são condicionais aos vínculos da janela; e
há sinal de que a extração pode ter deixado de fora execuções sem resposta final (99,9% das execuções com erro têm
resposta gravada, contra 11% na base 1).

## 7 · Leituras do painel

Fonte: `<rodada>/painel/painel.md` e as figuras da pasta, rodada `observada_609c947b15295c84` (v2), lidas em 14/10 e
**conferidas contra as tabelas das seções 2 e 3**: os valores por mês somam o total de cada unidade (as 18 linhas); os
erros das candidatas por papel somam 17.308; no mapa papel × unidade, as colunas do ContestacaoCivel e do RoteadorCivel
somam 5.296 e 5.029, os valores da figura de papéis. Contagem de erros não é taxa ([§6](#6--limitações-que-afetam-a-leitura));
as primeiras taxas, do pedido A, estão em §7.5. As leituras da rodada `3f9c…` (v1) estão no histórico do git.

**Figuras refeitas na auditoria dos gráficos (15–16/10, [roadmap](04-roadmap.md) #36 e #40, fechados; geradas e lidas na
rodada `observada_96958e65cb7e615a`, de 16/10):** os números citados abaixo saem das tabelas e não mudam (os totais lidos
nas figuras novas são os da `609c…`; a prova por hash é o #42); mudam as figuras. Dois gráficos saíram da parte 1
por "um insight por gráfico": o de **papéis das candidatas** (a figura citada em §7.4; o total por papel passou para a
margem do mapa papel × unidade) e o de **erros por unidade e mês** (§7.5; virou o painel esquerdo da taxa por unidade e
mês, na parte 2). Entrou o de **unidades por destino e tipo de memória**. Os gráficos por unidade passam a trazer todas
as unidades, cor da família e nenhum destino ([`decisoes.md`](../../decisoes.md), 15/10).

**A figura de destinos** traz a faixa do sinal de harness (a correção de 14/10 em `execucao/figuras_painel.py`, com a
trava que para a figura se uma decisão não tiver faixa) e bate com a triagem: 30.141 erros e 592,9 mi de tokens.

### 7.1 · Os pendentes: o que sobrou depois do Ajuste 18

São 749 erros (2,5%). Pela figura de pendentes, **o RoteadorCivel tem 57% deles**, quase todos do primeiro passo sem a
assinatura (397 dos 514, §7.10); depois vêm o OBFCivel e o RespostaOficios, em que pesa o timeout, e o RespostaBacen, em
que pesa o primeiro passo (89). O ContestacaoCivel, que tinha 59% dos pendentes na v1 por causa da mensagem cortada,
quase saiu da figura. **Por mês**, os erros de cada mês nas contagens (pedido A) menos os observáveis do mesmo mês no
painel dão os pendentes, e fecham em 749: agosto 454, maio 88, julho 75, junho 47, março 35, abril 30, fevereiro 19,
janeiro 1 — o desenho da figura. O que eram os 5.818 do primeiro passo, e como viraram a unidade de sinal de harness:
§7.8–7.10.

### 7.2 · Para onde vão os erros e os tokens

Calculado da triagem (seção 3) e da cobertura (seção 2):

| Destino | Erros | % dos erros | Tokens (mi) | % dos tokens |
|---|---:|---:|---:|---:|
| candidatas a memória | 17.308 | 57% | 387,0 | 65% |
| **sinal de harness** (`U_verificacao_try_nameerror`) | 5.764 | 19% | 112,0 | 19% |
| harness / infra (não-memória) | 5.728 | 19% | 64,2 | 11% |
| pendente (falta dado na extração) | 749 | 2,5% | 5,1 | 0,9% |
| resíduo | 565 | 1,9% | 21,9 | 3,7% |
| crítico e sem recorrência | 27 | 0,1% | 2,5 | 0,4% |

Os erros somam 30.141; os tokens, 592,7 mi (592,9 sem o arredondamento de cada linha). A figura do painel diz o mesmo:
"57% dos erros e 65% dos tokens estão em candidatas a memória".

**Leitura.** Somados, o sinal de harness e a não-memória são **38% dos erros e 30% dos tokens** — o que o ambiente
corrige, não a memória. O sinal de harness custa na média (19,4 mil tokens por erro); a não-memória é frequente e barata.
Com o texto inteiro, as candidatas passaram de 54% para 57% dos erros e de 59% para 65% dos tokens: os pendentes da
mensagem cortada eram, quase todos, retorno-string (+37 mi de tokens nele).

### 7.3 · Frequência e custo por erro são coisas diferentes

Tokens por erro, de `triagem_visivel_observada.csv` (tokens ÷ erros; a média das observáveis é de 20,0 mil, a linha do
gráfico):

| Unidade | Erros | Tokens por erro |
|---|---:|---:|
| `C_limite_passos` | 25 | 100 mil |
| `X_causa_nao_identificada` | 376 | 45 mil |
| `U_texto_solto` | 190 | 44 mil |
| `U_tipo_retorno` | 5.319 | 39 mil |
| `H_timeout_ferramenta` | 1.117 | 26 mil |
| `U_verificacao_try_nameerror` | 5.764 | 19 mil |
| `U_sandbox` | 3.653 | 19 mil |
| `U_estado_perdido` | 544 | 19 mil |
| `U_nome_inventado` | 351 | 17 mil |
| `U_campo_inexistente` | 1.569 | 15 mil |
| `U_arg_nomeado` | 3.927 | 13 mil |
| `H_bloco_code` | 4.592 | 7,6 mil |
| `U_repr_colado` | 1.588 | 4,1 mil |

- **O retorno-string pesa pelos dois lados:** é frequente e cada erro custa o dobro da média (38,9 mil, o título da
  figura). É por isso que lidera em tokens (35%). Os 1.002 erros que voltaram da pendência custam como os demais (37 mi
  em 1.002 erros, cerca de 37 mil cada).
- **A unidade de sinal de harness pesa pela frequência:** é a maior em erros e custa na média; 112 mi de tokens em
  primeiros passos que falham e são refeitos.
- **O estado perdido ficou mais barato** (23 → 19 mil por erro): os 334 erros do `try/except` que saíram dele custavam
  29 mil cada (Ajuste 17).
- **O protocolo do harness e o retorno colado de volta no código pesam só pela frequência:** o erro é barato.
- **Tokens por erro são os do passo com erro, sem a recuperação.** A leitura provável é que o custo reflete o contexto
  acumulado até o erro, e não a gravidade dele; **não confirmada**. A saída é 9,0% dos tokens dos passos com erro e 4,6%
  dos de todos os ActionSteps, mas essa diferença é em boa parte **mistura de papéis** (59% dos tokens de erro são do
  ContestacaoCivel, que gera mais texto; o total é dominado pelo OBFCivel, que gera pouco): dentro de cada papel a
  diferença é bem menor (em revisão, [roadmap](04-roadmap.md) #36); por unidade, falta medir (#13).

### 7.4 · Poucos papéis concentram as candidatas

Erros das candidatas por papel (figura de papéis; os 13 grupos somam os 17.308 erros): `ContestacaoCivel` 5.296,
`RoteadorCivel` 5.029, `RespostaBacen` 2.390, `CalculoTrabalhista` 1.560, `OBFCivel` 1.347, `JoogleAnalytics` 1.191,
`CadastroTrabalhista` 112, `RespostaOficios` 107, `CalculoCivel` 86, `CadastroCivel` 75, `AgenteEstruturador` 30,
`OficiosResposta` 22 e os demais 9 papéis 63.

- **Dois papéis têm 60% dos erros das candidatas** (10.325 de 17.308) e **seis têm 97%** (16.813). São 6 dos 21 papéis
  que têm erro de candidata. **O ContestacaoCivel passou o RoteadorCivel** (4.279 → 5.296): os erros da mensagem
  cortada eram dele, no retorno-string (2.385 erros dele nessa unidade).
- Por candidata, o papel que mais pesa (figura de concentração): campo inexistente, `RespostaBacen` 89%; retorno colado,
  `RoteadorCivel` 100%; argumento nomeado, `RoteadorCivel` 67%; inventário do sandbox, `ContestacaoCivel` 73%;
  **estado perdido, `RoteadorCivel` 60%**, `OBFCivel` 14% e `ContestacaoCivel` 11%; **nome inventado, `RoteadorCivel`
  60%**, `CalculoTrabalhista` 17% e `RespostaBacen` 9%; texto solto, `ContestacaoCivel` 35%, `CalculoTrabalhista` 31% e
  `JoogleAnalytics` 19%; texto longo em literal, `ContestacaoCivel` 36%, `CadastroCivel` 25% e `OBFCivel` 16%; `next()`
  sobre gerador, `CalculoProprios` 60% e `RespostaBacen` 27%; **retorno-string, `ContestacaoCivel` 45%** e `RespostaBacen`
  17% (na v1, 32% e 21%).
- **O Ajuste 17 mudou o retrato de duas candidatas:** sem o `try/except`, o estado perdido e o nome inventado são
  sobretudo do RoteadorCivel. A mineração delas começa por ele.
- **O que isto pede:** a mineração de cada candidata começa por perguntar se a lição vale para todos os agentes ou só
  para o papel que concentra os erros. O número de execuções e de ActionSteps por papel chegou (pedido A); a taxa por
  papel entra com o [roadmap](04-roadmap.md) #32.

### 7.5 · O padrão no tempo: agosto de 2026 concentra mais da metade

Erros observáveis por unidade e mês (os valores de cada linha somam o total da unidade na triagem, conferido nas 18
linhas):

| Unidade | Total | Mês de maior valor | No pico |
|---|---:|---|---:|
| `U_verificacao_try_nameerror` | 5.764 | 2026-08 | 5.667 (jul: 95; fev e mai: 1 cada) |
| `U_tipo_retorno` | 5.319 | 2026-08 | 2.664 (jul: 871) |
| `H_bloco_code` | 4.592 | 2026-08 | 4.153 |
| `U_arg_nomeado` | 3.927 | 2026-07 | 1.810 (ago: 834) |
| `U_sandbox` | 3.653 | 2026-07 | 2.029 (ago: 1.081) |
| `U_repr_colado` | 1.588 | 2026-07 | 687 (primeiro erro em 2026-02; 45 em maio) |
| `U_campo_inexistente` | 1.569 | 2026-05 | 476 (jul: 25; ago: 54) |
| `H_timeout_ferramenta` | 1.117 | 2026-08 | 1.117 (só esse mês) |
| `U_estado_perdido` | 544 | 2026-08 | 424 |
| `U_nome_inventado` | 351 | 2026-08 | 218 |

- **Agosto de 2026 tem 17.031 dos 29.392 erros observáveis (58%)**; julho, 5.838 (20%). O sinal de harness (98% em
  agosto), o protocolo do harness (90%) e o timeout (100%) se concentram nesse mês; o retorno-string tem metade dos
  erros nele.
- **Agosto teve mais execuções e mais erro por ActionStep** (contagens do pedido A, `base_contagens.parquet`, que se
  juntam ao parquet sem diferença; [roadmap](04-roadmap.md) #26): 29.263 execuções contra 24.824 em julho (+18%), e a
  taxa de erro estruturado por ActionStep vai de 6,7% para 15,7%. Sem o `try/except` (5.667 em agosto, 95 em julho),
  10,6% contra 6,6%: o sinal de harness explica parte do salto, não todo. Junho tem a menor taxa do período (4,1%). A
  taxa por unidade e por papel entra com o #32.
- **O retorno colado de volta no código começa tarde:** o primeiro erro é de fevereiro (1), são 45 em maio e 389 em
  junho; o pico é julho (687). O argumento nomeado (1.810) e o inventário do sandbox (2.029) têm o pico em julho e caem em
  agosto (834 e 1.081); o retorno-string e o protocolo do harness têm o pico em agosto.
- **O campo inexistente subiu até maio e caiu a 25 e 54 em julho e agosto.** Pode ter sido corrigido, ou o papel rodou
  menos; a taxa por papel e mês (#32) separa os dois.
- **O estado perdido e o nome inventado ainda têm o pico em agosto** (424 e 218), mesmo sem o `try/except`.
- **O timeout em um mês e um papel segue compatível com incidente pontual**, como na §4; continua em aberto
  ([roadmap](04-roadmap.md) #6).

### 7.6 · O que vem depois do erro

Passo seguinte ao erro, por candidata (figura do painel; percentuais lidos da figura, e o que não é "sem erro" ou
"novo erro" é pequeno e não rotulado). A unidade de sinal de harness não está na figura, que é só das candidatas; o
depois dela está em §7.8 (77% sem erro no passo seguinte).

| Candidata | Passo seguinte sem erro | Novo erro (cascata) | O passo seguinte é a resposta final |
|---|---:|---:|---:|
| `U_texto_solto` | 38% | 62% | 25% |
| `U_tipo_retorno` | 60% | 35% | 24% |
| `U_arg_nomeado` | 63% | 36% | 18% |
| `U_sandbox` | 71% | 28% | 48% |
| `U_texto_literal` | 77% | 23% | 49% |
| `U_nome_inventado` | 85% | 14% | 8% |
| `U_next_gerador` | 87% | 13% | 7% |
| `U_campo_inexistente` | 88% | 11% | 77% |
| `U_estado_perdido` | 89% | 11% | 10% |
| `U_repr_colado` | 96% | ~4% | 4% |

- **A explicação solta no bloco de código é a única em que o agente erra de novo na maioria das vezes** (62%), e cada
  erro dela é dos mais caros (44 mil tokens): é onde uma memória teria mais a ganhar, apesar de ter só 190 erros.
- **No retorno-string, a cascata subiu de 30% para 35%** com os erros que voltaram da pendência: as mensagens longas
  são, mais vezes, seguidas de outro erro.
- **No estado perdido, "o seguinte é a resposta final" caiu de 30% para 10%, e no nome inventado de 15% para 8%**
  (Ajuste 17). Os erros do `try/except` que saíram dessas unidades eram, em boa parte, os que o agente resolvia no passo
  seguinte e entregava — o padrão de §7.9 (tira o `try/except`, chama direto e termina).
- **Sem erro no passo seguinte não é sucesso:** pode ser outro problema que não é erro estruturado. A janela é de um
  passo; o fim da execução não está no arquivo.
- **"O seguinte é a resposta final" tem leitura dupla:** no campo inexistente (77%), no texto longo em literal (49%) e no
  inventário do sandbox (48%) o agente parece resolver e entregar, ou desistir e entregar; a janela não diz qual dos dois.

### 7.7 · O que o painel não mostra

Sem taxas (o denominador chegou, mas ainda não está no pipeline nem no painel: [roadmap](04-roadmap.md) #32), sem os
passos sem erro, sem falhas silenciosas, sem tokens de entrada × saída por unidade, e sem a recuperação além do passo
n+2. Cada ausência está no roadmap (#13, #15, #16, #32) ou no [pedido de dados](05-pedido-queries.md). A figura do
depois do erro não traz a unidade de sinal de harness.

### 7.8 · O nome não definido no primeiro passo (contagens de 13/10)

Duas contagens na máquina 2, sobre a mesma rodada, explicam o maior grupo pendente (os 5.818 de "predecessor não
identificado"). Nas saídas dos scripts, o papel aparece como `ContestacaoCivel`; é o `ContestacaoCivel`. **A causa do
grupo, e uma correção da leitura de mecanismo que estava aqui, estão em [§7.9](#79--a-causa-uma-instrução-do-prompt-que-o-ambiente-de-execução-não-suporta-base-2-1310).**

**1. São todos o primeiro ActionStep do papel** (`pipeline/validacao/contar_predecessor_pendentes.py`; foto IMG_5706).
A regra marcava o motivo para dois casos — não há passo anterior, ou há, sem `step_number`. O leitor do parquet já os
separa: no primeiro, nenhuma coluna `prev_*` vem preenchida (a query calcula o vizinho n-1 sobre todos os ActionSteps,
antes de filtrar os erros); no segundo, o número falta mas os outros campos vêm.

| Medida | Resultado |
|---|---:|
| Nenhum campo do passo anterior preenchido (primeiro ActionStep) | 5.818 |
| Anterior existente sem número | 0 |
| Também `step_number` = 1 e posição na lista (`step_pos`) ≤ 3 | 5.818 |
| `step_pos` = 2 (só a tarefa antes) / = 3 (tarefa e plano antes) | 5.729 / 89 |

Três sinais independentes concordam em todos os casos. Na base 1, onde o trace inteiro permite conferir, "nenhum campo
do anterior" é o primeiro ActionStep em 50 de 50, e a regra `step_number` = 1 e `step_pos` ≤ 3 acerta 1.550 de 1.550, sem
falso positivo, em 5.781 ActionSteps. O `step_number` = 1 sozinho não basta: ele reinicia a cada nova chamada do papel
(1.019 ActionSteps da base 1 com número 1 não eram o primeiro). **Consequência:** esse grupo não precisa de query —
saiu do pedido B ([`05`](05-pedido-queries.md)).

**2. Um erro por execução, poucos nomes, e o padrão da verificação de existência**
(`pipeline/validacao/contar_primeiro_passo_nome.py`; fotos IMG_5707 e IMG_5708).

| Medida | Resultado |
|---|---|
| Execuções distintas | **5.818** — um erro por execução (mínimo, mediana e máximo = 1); as 10 execuções com mais erros têm 0,2% do grupo |
| Nomes distintos (o nome que a mensagem diz não existir) | **27**; o mais frequente = 40,5%, os 3 mais = 90%, os 10 mais = 99,3% |
| Por papel | `ContestacaoCivel` 17 nomes (3 mais = 98,3%); `RoteadorCivel` 5 (o mais frequente = 67,3%); `RespostaBacen` 1 nome em 89 erros |
| Código do passo com erro inteiro (sem corte) | 2.313 (40%); 3.505 cortados ou ausentes |
| …o nome aparece no código / é atribuído no mesmo código / a primeira atribuição vem **depois** do primeiro uso (regex) | 2.313 / 1.824 / **1.815** — **contagem do padrão `try/except NameError`**, não de "ordem errada" (correção em §7.9) |
| Passo seguinte | existe nos 5.818; sem erro em 4.470 (77%), com erro em 1.348 |
| Sinal de recuperação | final na ação seguinte 2.698; possível recuperação na seguinte 1.772; final em até 2 ações 593; cascata 384; possível em até 2 366; desconhecido 5 |
| Tokens do passo com erro | 101,7 mi (≈ 17.500 por erro) |

**Leitura:** não é incidente de poucas execuções — milhares de execuções começam com o mesmo tipo de erro, um só
cada. Não parece nome inventado ao acaso: 27 nomes cobrem tudo. O agente costuma se corrigir no passo seguinte; o custo
é o primeiro passo desperdiçado, multiplicado pelas execuções. **Correção de 13/10:** esta leitura dizia que, nos casos
com código inteiro, o agente "define o nome no próprio código, mas depois de usá-lo". A regra de texto contou como
"atribuição depois do uso" o padrão `try: nome` / `except NameError: nome = ...` (a referência vem no `try`, a atribuição
no `except`). A contagem vale; o mecanismo é o descrito em §7.9.

**3. A base 2, com o trace inteiro, confirma o grupo**
(`2026-09-trace-law-flow-second/scripts/contar_primeiro_passo_nome_base2.py`; fotos IMG_5709 e IMG_5710). A base 2 é o
lote de agosto de 2026 (1.000 execuções, 3.907 ActionSteps, 479 erros estruturados, 129 de nome não definido).

| Medida | Base 2 | Base 3 |
|---|---|---|
| Erros de nome no primeiro ActionStep / depois de passo sem erro / depois de passo com erro | **103** / 15 / 11 | 5.818 / — / — |
| A regra "`step_number` 1 e posição ≤ 3" × primeiro ActionStep real, em todos os ActionSteps | 1.000 de 1.000 e 2.907 de 2.907 (0 erros) | — |
| Um erro por execução | 103 em 103 | 5.818 em 5.818 |
| Execuções do `ContestacaoCivel` em agosto que **começam** com o erro | **97 de 149 (65%)** | sem denominador (pedido A) |
| Execuções do `RoteadorCivel` em agosto que começam com o erro | 6 de 267 (2%) | — |
| Nomes distintos / os 3 mais frequentes | 5 / 92% | 27 / 90% |
| Padrão "referência no `try`, atribuição no `except`" (contado como "atribuição depois do uso", regex) | **97 de 103 (94%)**, código inteiro | 1.815 de 2.313 com código inteiro (78%) |
| Define o nome no código do passo seguinte | 92 de 103 | — |
| O nome aparece no texto da tarefa / no system prompt | **0 / 83** de 103 | — |
| A mesma conversa teve antes uma execução com o mesmo papel | 0 de 103 | — |
| Modelo | `gpt-5.2-2025-12-11` 97; `gpt-5.6-terra-2026-07-09` 6 | sem a coluna |

- **A "maior candidata" da base 2 era este grupo.** Os 118 erros de nome inventado do relatório da base 2 são 103 do
  primeiro passo + 15 nomes inventados de fato; os "101 num papel, num mês e num modelo" são 97 do primeiro passo e 4
  inventados, todos do `ContestacaoCivel` ([`b2 #3`](../../2026-09-trace-law-flow-second/docs/04-roadmap.md)).
- **As hipóteses do [roadmap](04-roadmap.md) #1 se separam:** estado de uma chamada anterior na conversa — não
  sustentada (0); nome vindo da tarefa — não sustentada (0); variável que o harness deveria injetar — não sustentada;
  **instrução do system prompt — sustentada** (§7.9: três casos lidos, e 83 de 103 com o nome no prompt); ligação com o
  modelo — no `ContestacaoCivel` descartada (§7.9, parte F); no `RoteadorCivel`, provável (6 casos).

### 7.9 · A causa: uma instrução do prompt que o ambiente de execução não suporta (base 2, 13/10)

Fontes: a parte F e a parte G do `contar_primeiro_passo_nome_base2.py` (fotos IMG_5712 e IMG_5713) e a leitura de três
casos, feita por Rafael na máquina 2 (fotos IMG_5714 a IMG_5719). Tudo abaixo é contagem ou paráfrase; nenhum
identificador de execução nem número de processo entra neste documento.

**O papel × o modelo (parte F).** No grupo do primeiro passo da base 2, os 97 erros do `ContestacaoCivel` são todos do
`gpt-5.2` e os 6 do `RoteadorCivel` são todos do `gpt-5.6-terra`. Mas **o modelo não explica o `ContestacaoCivel`**: o
mesmo `gpt-5.2` rodou 72 execuções do primeiro passo em julho **sem nenhum erro**, e em agosto 97 de 129 (75%) tiveram o
erro; a variante `gpt-5.2-gs` teve 0 de 20 em agosto. No `RoteadorCivel`, em agosto, o `gpt-4.1` teve 0 erros em 126
execuções e o `gpt-5.6-terra`, 6 em 138 (4%).

**O prompt (parte G).** O hash do trecho do system prompt que atribui os nomes do grupo (o prompt inteiro varia a cada
execução, porque traz o caso) separa duas versões no `ContestacaoCivel`:

| Versão do trecho | Execuções | Com o erro | Meses |
|---|---:|---:|---|
| a antiga (`0618beb504`) | 127 | **0** | 2026-06 a 2026-08 |
| a nova (`7dc18e5e8c`) | 97 | **97 (100%)** | só 2026-08 |

Em agosto, com o mesmo modelo, as 32 execuções que ainda tinham a versão antiga tiveram 0 erros e as 97 com a nova,
97 — **na amostra da base 2** (1.000 registros). Isso não prova que a versão antiga nunca causa o erro: a base 3 tem 95
erros com a mesma assinatura em julho (§7.10), e 0 em 72 execuções é compatível com uma taxa baixa. O prompt do
`RoteadorCivel` não atribui nenhum desses nomes em nenhum mês: ali o erro vem do modelo, não do prompt.

**Os três casos lidos** (`ContestacaoCivel`, agosto de 2026, `gpt-5.2`; casos espalhados no tempo, regra fixa):

| Caso | O primeiro passo | O passo seguinte |
|---|---|---|
| 1 | usa `try: variável` / `except NameError: variável = ...` para várias variáveis; o nome que falta não aparece no trecho do prompt | define direto, sem `try/except`, e termina com a resposta final |
| 2 | o mesmo padrão, para o identificador do processo e para as saídas de quatro ferramentas | abre com um comentário do próprio agente: definição direta, "sem try/except para evitar o erro do interpretador" |
| 3 | o mesmo padrão; **o trecho do prompt ao redor do nome (linhas ≈ 962–976 do prompt) é a instrução** | comenta que faz a chamada direta "para evitar erro de checagem de variável não definida" |

A instrução, em paráfrase (caso 3): antes de chamar uma ferramenta, verificar se a variável de saída já está preenchida
em memória e, se estiver, pular a chamada; não usar `globals()` nem `locals()` (proibidos pelo interpretador); para
checar a existência, usar `try/except NameError`, com um exemplo para a variável da petição inicial; se a variável já
foi definida num passo anterior, apenas referenciá-la.

**O mecanismo.** Em Python comum, um nome inexistente levanta `NameError` e o `except NameError` o captura. O erro da
nossa tabela é um `InterpreterError` ("The variable ... is not defined"), com o `except NameError` escrito no código:
o interpretador do sandbox levanta o seu próprio erro, que o `except NameError` não pega. O passo seguinte passa porque o
agente deixa de verificar e cria a variável direto.

**Reproduzido no interpretador** (`pipeline/validacao/testar_sandbox_try_nameerror.py`, código sintético; smolagents
1.26.0 — a versão da plataforma não é conhecida):

| Forma de verificar se a variável existe | Variável ainda não existe | Já existe (passo anterior) |
|---|---|---|
| `except NameError` (o que o prompt manda) | **falha**, com a mesma mensagem do trace | funciona |
| `except InterpreterError` | **falha**: esse nome não existe dentro do sandbox | — |
| `except Exception` / `except` sem tipo | funciona | funciona |
| `'x' in globals()` | **falha**: `globals()` é proibida | — |
| dicionário de estado injetado pelo harness (`if 'x' not in estado`) | funciona | — |
| chamada direta, sem verificar (o passo seguinte do agente) | funciona | — |

A instrução falha **só quando a variável ainda não existe** — por isso o erro é sempre do primeiro passo e some a partir
do segundo.

**O que muda:**

- **O mecanismo** deixa de ser "nome usado antes de ser definido" e passa a ser "verificação de existência por
  `try/except NameError`, instruída pelo prompt, que o ambiente não suporta". Nome sugerido para a unidade: *verificação
  de existência por `try/except NameError`*. Não é nome inventado (a variável é criada logo abaixo), nem estado perdido
  (não há passo anterior), nem módulo sem import.
- **O destino** proposto é o **harness** (a instrução do prompt ou o interpretador): o agente não tem como saber que a
  instrução falha, e uma memória "não use try/except" contradiria o prompt. Na base 2 a evidência é forte; **na base 3
  fica "em aberto"** até haver evidência dela — a mensagem de erro traz a linha que falhou (começa com `try:` e contém
  `except NameError`), então a assinatura pode ser contada no parquet, sem o prompt (roadmap b3 #1).
- **O custo:** 101,7 mi de tokens na base 3 em passos que falham e são refeitos (≈ 17.500 por erro), todos no primeiro
  passo.
- **O que ainda não sabemos:** se o parágrafo da instrução já existia no prompt de julho. A parte G mostra que a versão do
  trecho que atribui os nomes mudou, e que na amostra só a nova deu o erro; não mostra o parágrafo em si. O diff do prompt (521
  linhas) não foi lido. A próxima medida conta, por versão e mês, se o prompt traz a instrução.
- **Nada mudou no pipeline nem nos números** (continuam 7.107 pendentes, 24%): isto é leitura e proposta, não ajuste.

### 7.10 · A assinatura na base 3: o padrão não é só do primeiro passo (13/10)

`pipeline/validacao/contar_assinatura_try_nameerror.py`; foto IMG_5720. A mensagem de erro traz a linha que falhou
("Code execution failed at line 'try: … except NameError: …' due to: InterpreterError: The variable … is not defined").
O script conta, em cada erro de nome não definido, se a linha tem `try` com `except NameError`; "duvidoso" = a linha
começa com `try:` mas sem `except NameError`. Não precisa do prompt.

| Situação atual do erro (pela posição do passo anterior) | Erros | Com a assinatura | Sem | Duvidoso |
|---|---:|---:|---:|---:|
| Pendente: predecessor não identificado (o primeiro passo) | 5.818 | **5.304 (91%)** | 514 | 0 |
| `U_estado_perdido` | 878 | **334 (38%)** | 543 | 1 |
| `U_nome_inventado` | 477 | **126 (26%)** | 350 | 1 |
| Pendente: numeração ambígua | 5 | 0 | 5 | 0 |
| **Total de erros de nome não definido** | **7.178** | **5.764 (80%)** | 1.412 | 2 |

As somas fecham (5.304 + 334 + 126 = 5.764; 5.818 + 878 + 477 + 5 = 7.178). Com a assinatura: `ContestacaoCivel`
2026-08, 5.667; 2026-07, 95; `RespostaBacen`, 1 em 2026-02 e 1 em 2026-05. Há 12 erros de outro tipo
(`AgentExecutionError`) cuja mensagem também traz `except NameError`. Na base 1, 0 de 10 erros de nome têm a assinatura.

**O que isso mostra**

- **A base 3 tem evidência própria do padrão:** 91% dos 5.818 do primeiro passo. A assinatura prova o padrão, não que o
  prompt o instruiu: isso só foi visto na base 2. O hash do prompt no pedido A fecharia a questão.
- **O padrão acontece depois do primeiro passo.** 460 erros (334 + 126) estão hoje em unidades de memória só porque o
  passo anterior teve erro (estado perdido) ou não teve (nome inventado). A regra atual olha só a posição, e o próprio
  pipeline a rotula `proxy_predecessor_estruturado_nao_prova_namespace`. Foi validada nas bases 1 e 2, onde o padrão
  não existia (0 de 10 na base 1); a base 3 criou um padrão que ela não enxerga.
- **Por que isso importa para a lição.** Cada unidade vira um cartão de memória, escrito e medido a partir dos casos
  dela. O cartão do estado perdido ("redefinir o que o passo anterior criaria") e o do nome inventado ("usar só o que
  foi definido") não previnem um erro que vem de uma instrução do prompt: 38% e 26% dos casos nunca seriam evitados por
  eles, a medida de eficácia sai menor, e um cartão escrito sobre esses casos poderia contradizer o prompt.
- **Os 514 do primeiro passo sem a assinatura** são outro mecanismo. Pelas somas, quase todos devem ser os 397 do
  `RoteadorCivel` (erro com o modelo novo, prompt sem essa instrução) e os 89 do `RespostaBacen`; é dedução, não contagem.
- **Julho já tem 95 erros com a assinatura.** O problema não nasceu em agosto; em agosto ele explodiu. A hipótese de
  que a versão nova do trecho do prompt aumentou a frequência continua aberta.

**Fundamento no método** (`discussion/hipoteses/trace-error-taxonomy-methodology/`, §3.2): o mesmo sintoma pode ter
mecanismos diferentes, e só um sinal local mais fino os separa; quem decide é o eixo do mecanismo. A linha que falhou
é esse sinal. O pipeline já aplica o mesmo gesto ao módulo sem import, decidido antes da posição. Precedente do destino
harness: o `validar_quebra_sigilo` (contradição do prompt com o ambiente, decidida sem LLM) e o `U_campo_inexistente`.

**Aplicado como Ajuste 17 (13/10, decisão do Rafael; [livro-razão](../../pipeline-entre-bases.md)).** A assinatura na
linha que falhou passa antes da posição e leva o erro à unidade `U_verificacao_try_nameerror`, com destino **harness**
nas bases 2 e 3 (sinal de harness). Na base 1 nada muda (498 de 498 na mesma unidade). A simulação na base 3 (foto
IMG_5721) mostrou: mudam 5.764, dos outros 24.377 nenhum muda; pendentes 7.107 (23,6%) → 1.803 (6,0%); estado perdido
878 → 544 e nome inventado 477 → 351, os dois ainda candidatos; a unidade nova com 5.764 erros, 5.442 execuções e 112,0 mi
de tokens. **A rodada nova (`observada_3f9c2806cac9cd4d`, 14/10) confirmou os números da simulação;** as seções 1 a 7.7
estão atualizadas.
