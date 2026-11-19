# Procedimento — minerar o resíduo numa base

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`/`X_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Para que serve este documento:** o roteiro para minerar o resíduo de uma base, padrão por padrão, até cada padrão
virar regra, ser descartado com motivo ou ficar em observação. É a decisão **revisar** da triagem
([`03-procedimento-validacao.md`](03-procedimento-validacao.md), Frente 3). O **porquê** de cada passo está em
[`18-racionais-residuo.md`](18-racionais-residuo.md). Os casos de cada base estão em:
- base 1: `03` §1.13;
- base 2: `03` §1.16;
- base 3: [`../../2026-10-trace-law-flow-third/docs/02-relatorio-achados.md`](../../2026-10-trace-law-flow-third/docs/02-relatorio-achados.md) §5.

O kit roda este procedimento pela skill `mineracao-residuo` (as perguntas de leitura de caso estão no roteiro
`residuo` da `mineracao-investigacao`).

**De onde veio o texto (09/11/2026).** Os passos 1 a 8 e os dois casos particulares saíram da Frente 3 do `03` ("O
procedimento do resíduo, passo a passo"), que guarda um ponteiro para cá. Entraram:
- o passo 0 (cruzar com as outras bases pelo mecanismo, `b1 #33`);
- os comandos da base 3;
- o critério de parada por padrão;
- as conferências.

**Regra de ouro (do 03):** nenhum número agregado sem um caso concreto que o sustente, e nenhuma regra nova escrita
olhando uma base só.

## Comandos por base

| O que | Bases 1 e 2 (trace inteiro; de dentro de `pipeline/`) | Base 3 (rodada do `executar.py`; da raiz) |
|---|---|---|
| a tabela de padrões | notebook da esteira 9.2 → `resultados/residuo_padroes.csv`; `drill_down.py residuo` → `evidencia/A5_residuo/casos.csv` | `pipeline/especificas/residuo.py --rodada <id>` → `resultados/mineracao/residuo/{residuo_padroes,casos}.csv` e `resumo.json` |
| os casos de um padrão | `drill_down.py padrao "<trecho do padrão>"` | `montar_evidencia.py <análise> --de mineracao/residuo/casos.csv --onde "padrao=<padrão>"` |
| ler um caso | `drill_down.py caso <exec_id> <role>` (o trace inteiro) | `pipeline/drill_down.py caso <exec_id> <papel> <idx>` (só a janela n-1 … n+2) |
| a auditoria | `audit_recompute6.py` (a classificação inteira) | `audit/scripts/audit_residuo_base3.py` (o padrão, a contagem e a recorrência) + o encontro da skill |

**Na base 3 a régua é contada por erro**, com a execução = (execução, agente), como na triagem dela
(`mineracao_observada._decisao`). O alarme de cobertura não é aplicado lá, porque o universo de elegibilidade é
outro. A tabela traz os dois números; a decisão é a da triagem.

## Pré-condições e o que sai do ambiente

- A rodada é a vigente. Na base 3, o `residuo.py` confere que a fonte e o código são os do manifesto e que a análise
  recalculada tem o identificador da rodada. Se não forem, ele para.
- **Sai do ambiente:** contagens, a classe, o padrão **mascarado**, papel, mês, as três colunas de formato da
  mensagem, e o resultado do encontro. O relatório que sai passa pelo `varrer_pii.py`.
- **Não sai:** `casos.csv` (tem `exec_id`), os crus e o texto dos casos. `resultados/` é git-ignored.

## Passo 0 — Cruzar com as outras bases, pelo mecanismo

Para cada padrão que passa na recorrência ou está no topo de tokens, procure o mesmo padrão na tabela das outras
bases. Se ele aparece lá, **leia um caso de cada base** antes de contar como "o mesmo" (racional §5): a máscara junta
chaves, e o mecanismo pode ser outro. "O mesmo padrão com o mesmo mecanismo em outra base" sobe a prioridade, e a
regra nova é escrita olhando as duas.

## Passo 1 — Listar os casos do padrão

Pelo comando da base (tabela acima). Comece pelos padrões que passam na recorrência. Entre eles, vá pelo maior custo
em tokens e depois pelo número de execuções. Na sintaxe em volume, comece pelo motivo do parser mais frequente.

## Passo 2 — Ler no cru

Leia todos os casos se forem até 10. Se forem mais, leia o 1º de cada mês (ordem `exec_id`, `idx`), a mesma regra das
pastas de evidência (`amostrar.py --regra procedimento`). Na base 3 a leitura vê só a janela do erro (n-1 a n+2); se a
pergunta precisar do prompt ou do resto da execução, registre isso como limite da leitura.

## Passo 3 — Conferir o agrupamento

Os casos são mesmo o mesmo erro? A máscara pode juntar erros que só diferem dentro das aspas, ou separar o mesmo erro
(racional §2). As colunas de formato (`tem_due_to`, `tem_linha_error`, `linha_rejeitada_ok`) dizem se a regra de
parsing viu a mensagem no formato que espera: uma sintaxe com `linha_rejeitada_ok` falso pode estar no resíduo por
falta de formato, não por diagnóstico (Ajuste 1). Se o padrão não for um erro só, anote o motivo, divida-o, e cada
parte volta ao passo 1.

## Passo 4 — De quem é a falha?

- do **agente** (o código que ele escreveu, o jeito que chamou a ferramenta) → passo 5;
- do **harness, da infra ou de um limite do LLM ou do interpretador** (ex.: `AgentMaxStepsError`, o interpretador que
  não suporta algo, o timeout de uma ferramenta) → unidade nova `H_*`, tipo não-memória, e o procedimento de
  não-memória (Frente 3).

## Passo 5 — Já existe uma unidade para essa lição?

- Se existe (a regra só não reconhecia esta mensagem) → **estender a regra** da unidade existente. Ex.: o `Import
  from`, que entrou na regra do sandbox (Ajuste 3).
- Se não existe → **unidade nova**: nome, tipo (factual · ambiente ou experiencial · estratégia) e o conteúdo em uma
  frase.

## Passo 6 — Escrever a regra (é um Ajuste)

A regra é determinística, sem LLM. Ela entra:
- no `submecanismo()` do `base_pipeline.py`. Se o balde era "Sintoma não reconhecido", entra também no `classify()`:
  primeiro a regra de sintoma, depois a de causa;
- em `SUB2UNI` e `UNI`;
- reescrita à parte no `audit/scripts/audit_recompute6.py`.

Antes de escrever, conte a regra na população inteira do resíduo, com o `testar_regra.py` do kit: no trace inteiro,
`--campo-passo error`; na base 3, `--campo-csv mensagem` sobre o `casos.csv`. **Onde ela entra decide o que ela
alcança.** Uma regra posta no fim do `submecanismo()`, logo antes do "causa sem regra", só alcança o que hoje é
resíduo. Uma regra posta antes pode roubar erro de outra unidade, e então tem de ser contada também nos erros das
outras unidades. O passo 7 confere isso. Uma regra que muda número publicado é um **Ajuste**:
1. evidência com os crus;
2. a interpretação fechada com o pesquisador;
3. a proposta de código;
4. a aprovação;
5. só então a mudança.

Na base 3, o `base_pipeline.py` está no hash da rodada: mudá-lo pede uma rodada nova no ambiente da base.

## Passo 7 — Rodar do zero e conferir

Confira quatro coisas:
- os erros do padrão saíram do resíduo;
- nenhum outro erro mudou de unidade sem explicação;
- as candidatas que já existiam não mudaram;
- a auditoria nº 6 continua com 0 divergências.

Na base 3: a rodada nova, o `validacao/comparar_rodadas.py --antes <id> --depois <id>` e o `residuo.py` na rodada
nova. O resíduo tem de cair exatamente pelos erros do padrão.

## Passo 8 — Registrar

Registre em quatro lugares:
- **o livro-razão** ([`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md)): a regra e o porquê
  (gatilho → evidência → mudança → verificação → o que replicar);
- **o doc da base:** os casos e a conferência (`03` Frente 1 nas bases 1 e 2; `02` §5 na base 3);
- **a pasta de evidência** com os crus;
- **o roadmap da base:** o item fechado, com o resíduo antes e depois.

A unidade nova passa pela triagem como qualquer outra: se sair candidata, entra no procedimento de candidata.

## Quando um padrão termina

| Saída | Quando | Onde fica escrito |
|---|---|---|
| **vira regra** | passos 4–7 completos, Ajuste aprovado | livro-razão; a unidade nova ou estendida |
| **descartado com motivo** | o agrupamento era falso e as partes são de uma ocorrência só, ou os casos não têm nada em comum além da classe | `analysis/decisoes.md` (a decisão) e o doc da base (os casos) |
| **fica em observação** | padrão de uma ocorrência só, ou sem impressão digital e sem leitura que o una; ou a causa é conhecida, mas o padrão está abaixo da régua e nenhuma unidade cabe | os erros continuam no resíduo; o motivo em `analysis/decisoes.md`; o padrão volta se reaparecer (na tabela de padrões de toda rodada; o alarme automático no `monitoramento.json` depende do b3 #52) |

**"Em observação" era "cobertura" até 11/11/2026** (decisão do Rafael: o nome vinha do alarme de cobertura e não dizia o que acontece com o erro). O erro em observação **não sai do resíduo e não é esquecido**: continua contado em toda rodada, com o motivo escrito, e volta à fila se passar na régua.

## Dois casos particulares

- **Código Python mal escrito em volume:** o padrão já separa pelo motivo do parser (parêntese, indentação,
  operador). Comece pelo motivo mais frequente.
- **Sintoma não reconhecido:** o passo 6 começa pelo `classify()` (família e assinatura novas) e só depois o
  `submecanismo()`.

## Conferências

- A soma dos padrões é igual aos erros do resíduo, e todo erro do resíduo tem padrão. Na base 3, nenhum pendente
  entra.
- Erros, execuções e meses de cada balde são iguais aos da triagem da rodada. A decisão de cada balde (prioridade ×
  baixa) é igual a "algum padrão passa" na tabela.
- O encontro com a auditoria independente sai com 0 divergências.
