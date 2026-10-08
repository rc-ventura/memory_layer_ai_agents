# Relatório de achados — base 3 (erros com contexto), rodada observada

> Códigos de unidade e siglas: [glossário](../../glossario.md). Cada código aparece junto do nome da lição.

**Data:** 08/10/2026 · **Fonte:** `base_erros_minerados_full.parquet` (máquina 2), SHA-256
`7604f77df9fe6127bd7fb9db18337b558b1f2587b0a99621c087b0cf3c2873f1` — saída da query
`ICTI_crossmemory_query_mineracao_erros`, execuções iniciadas entre ago/2025 e set/2026.
**Rodada:** `observada_0d23103afd4fc0f4`, estado `concluida_tecnicamente_sem_aprovacao_semantica`.
**Por que a análise é assim:** [`01-racionais.md`](01-racionais.md). **Como foi conferido e como reproduzir cada
número:** [`03-procedimento-validacao.md`](03-procedimento-validacao.md).

**Onde está a evidência.** Os arquivos da rodada ficam na máquina 2, em
`analysis/2026-10-trace-law-flow-third/pipeline/resultados/observada_0d23103afd4fc0f4/` (abaixo, `<rodada>/`). Cada
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
  vira a primeira investigação ([roadmap](04-roadmap.md) #1).

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
caracteres responde por 1.009 erros; o teste na base 1 mostra que ele apaga sobretudo o retorno-dict (§4).

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
- **Espalhamento por papel varia muito.** O retorno-string aparece em 17 papéis; o retorno colado de volta no código,
  com 1.587 erros, em só 3. Uma lição para três papéis e uma lição para todos são entregas diferentes — a mineração
  de cada candidata separa isso (`triagem_por_papel.csv`).
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
