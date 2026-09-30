---
name: investiga-trace
description: "Investiga traces crus da esteira jurídica com o drill_down.py do pipeline de análise (Frente 3 do procedimento de validação): lista padrões de resíduo, abre casos concretos (exec_id/role/idx), propõe categorias e rascunha regras de sintoma/causa — sempre apresentando ao Rafael antes de qualquer mudança. Use SEMPRE que a mensagem for 'investiga o resíduo', 'abre o padrão X', 'abre esse padrão', 'drill down nesse caso', 'investiga esse erro', 'quais casos têm esse padrão', 'roda o drill_down', 'abre a execução <exec_id>', 'triagem do resíduo', 'investiga o erro crítico', 'quem gastou os 30s', ou quando o Rafael apontar um exec_id/padrão/assinatura pedindo leitura no cru. NÃO use para: rodar o notebook de análise inteiro (reescreve resultados/), editar regras de classificação em base_pipeline.py sem pedido explícito e aprovação, mineração de unidades de memória (notebook §11 — método próprio), registro no diário (skill diario-campo) ou processar transcrição de reunião (skill checkpoint-reuniao)."
---

# Investiga trace — assistente de drill-down do pipeline de análise

## Papel e fronteira

Esta skill faz o trabalho de **triagem assistida** sobre o trace cru: partir de um achado agregado
(padrão do resíduo, assinatura, mecanismo, unidade) e trazer os **casos concretos** que o sustentam,
com proposta de leitura. O procedimento é o da **Frente 3** de
`analysis/2026-09-trace-law-flow/docs/03-procedimento-validacao.md` — nada aqui é método novo.

Fronteira inegociável:

1. **A classificação canônica é determinística** (`classify()`/`submecanismo()` em `base_pipeline.py`).
   O agente propõe categorias e rascunha regras; **nunca edita `base_pipeline.py`, `drill_down.py` ou
   qualquer script do pipeline** sem pedido explícito do Rafael e aprovação do diff. Decisão de
   triagem (candidata/não-memória/revisar) é sempre do Rafael.
2. **Nunca apresentar número agregado sem apontar o caso concreto** (eixo central do procedimento:
   toda saída desta skill cita `exec_id`/`role`/`idx` do que sustenta a leitura).
3. **PII.** A saída de `drill_down.py` reproduz nomes de clientes e números de processo em claro:
   nunca commitar, nunca redirecionar para arquivo versionado, e **nunca enviar conteúdo do cru para
   LLM externo sem autorização explícita do Rafael** (na máquina de compliance, nada sai da máquina —
   de lá só saem contagens, classes, nomes de papel/ferramenta e esqueletos mascarados).

## Pré-condições

- Rodar **de dentro da pasta `pipeline/`** da base em questão (o `TRACE` é resolvido pelo caminho do
  script, não pelo diretório corrente — mas os CSVs de `resultados/` são lidos do relativo).
- Os comandos `padrao`, `residuo`, `tempo`, `protocolo`, `mecanismo` leem `resultados/erros_mecanismo.csv`
  (gerado pelo notebook). Se não existir: avisar o Rafael e **não rodar o notebook sozinho** (ele
  reescreve `resultados/`).
- Base nova: antes de qualquer investigação, rodar o intake (`python checklist.py`) e ler
  `analysis/README.md` ("Intake checklist — a new trace base").

## Catálogo de comandos (`python drill_down.py <cmd>`)

| Comando | Quando usar |
|---|---|
| `tutorial` | referência guiada; primeiro passo em contexto novo |
| `amostra [n]` | execuções quaisquer, para conferir com os próprios olhos |
| `listar "<assinatura>"` | casos por **sintoma** (mensagem classificada) |
| `mecanismo "<nome>" [n]` | casos por **mecanismo** (mais específico que assinatura); nome errado lista os disponíveis |
| `planos [n]` | execuções com PlanningStep |
| `ferramenta <nome>` | como o system prompt **declara** a ferramenta (assinatura, descrição, retorno) |
| `caso <exec_id> <role>` | trajetória inteira do papel, formato legível; `--json` para o dict completo sem truncar |
| `padrao ["<trecho>"]` | sem args: padrões do resíduo com erros/execuções/meses; com args: casos de um padrão |
| `residuo` | pasta de evidência dos erros sem regra de causa (só contagens na saída) |
| `tempo [<role>] [--mecanismo=a,b]` | quem gastou os 30 s do interpretador (só números e nomes) |
| `protocolo` | "resposta sem bloco de código" por mês/papel, com gatilho |
| `evidencia [<análise>]` / `evidencia <exec_id> <role> <idx> <ferramenta>` | completa pastas de evidência (escreve em `resultados/evidencia/` — git-ignored) |
| `relogios` | as três datas independentes de cada execução (mês real × mês do lote) |

Companheiros: `python checklist.py [outra-base.csv]` (intake/overlap de bases) e
`python genealogia_sankey.py` (regenerar a figura **após** mudança aprovada nas regras).

## Receitas

### R1 — Resíduo: padrão → casos → categoria → regra (Frente 3, passos 1–3)

1. `python drill_down.py padrao` — a lista de padrões com recorrência.
2. `python drill_down.py padrao "<nome exato>"` — os casos (exec_id/role/idx/mês).
3. `python drill_down.py caso <exec_id> <role>` — ler o cru (pensamento, código, observação, erro).
   Ler **o mecanismo, não só a chave**: a máscara junta erros de causas diferentes (item 33 do roadmap).
4. Propor, por grupo: uma **categoria em 3–5 palavras** (limite de passos, timeout, rede/API,
   interpretador/harness, erro do agente, outro) e a qual **de quem é a falha** (agente × plataforma).
5. **Parar e apresentar ao Rafael.** Se ele aprovar a regra: sintoma primeiro (`classify()`), causa
   depois (`submecanismo()`) — e o rascunho da mudança vai para o ciclo de ajuste do
   `analysis/pipeline-entre-bases.md` §2 (evidência → diagnóstico → ajuste testado → réplica → registro),
   sempre com o Rafael executando o commit.

### R2 — Erro crítico ("investigar — crítico")

Ler `resultados/criticos.csv` (uma linha por execução morta): a `primeira unidade` é o ponto de partida;
abrir com `caso` os erros **anteriores** do caminho (`unidades no caminho`) para achar o passo crítico.

### R3 — Tempo esgotado do interpretador

`python drill_down.py tempo [<role>]` — tamanhos em jogo, estrutura do código (laços, chamadas),
o que ia para o `final_answer` e os `final_answer` que deram certo (a régua). Ver Ajuste 9 / Etapa 5b.

### R4 — Base nova

`python checklist.py` antes de tudo (colunas, censo de `error.type`, cruzamento lote × mês real);
`checklist.py <outra-base.csv>` para checar overlap de `exec_id`. Copiar `base_pipeline.py` sem mudar
as regras e ler o balde "Sintoma não reconhecido" como **cobertura**.

## Saída esperada

Sempre: o achado (contagens já existentes nos CSVs não devem ser recalculadas de outra forma) + os
casos que o sustentam (com `exec_id`/`role`/`idx`) + a proposta de leitura separada do fato + o ponto
de decisão explícito ("decisão sua: X ou Y"). O que não puder ser sustentado por caso concreto é
dito como não verificado.
