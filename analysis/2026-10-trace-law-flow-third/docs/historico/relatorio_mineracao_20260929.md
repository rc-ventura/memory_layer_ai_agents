<!--
Transcrição das fotos do guia `relatorio_mineracao_20260929.md` (máquina 2, `…/third/docs/`), feita em 09/10/2026.
É o guia que acompanha a base minerada de erros e a query `ICTI_crossmemory_query_mineracao_erros`
(ver `query_mineracao_erros.sql` nesta pasta). Não é a documentação atual da base 3 (essa está em `../`).
Texto fiel ao das fotos. Marcas: `[linhas N–M não visíveis na foto]` onde o corte da foto impediu a leitura.
Fotos usadas: IMG_5307 a IMG_5364 da pasta `relatorio_query_mineracao`. Pontos cortados na foto: fim da linha 389 (seção 7), linhas 955–956 (seção 19), 1241–1244 (seção 26) e 1313–1316 (seção 27).
-->

# Guia da Base Minerada de Erros dos Agentes

## 1. Objetivo

Esta base foi construída para apoiar o estudo de erros cometidos pelos agentes durante suas execuções, no contexto do projeto **Cross Memory**.

A tabela original de traces possui uma granularidade de **uma linha por execução de agente** e armazena, no campo `txt_etap_memo`, toda a memória de execução do agente. Esse campo pode ser extremamente grande, contendo tarefas, planejamento, entradas do modelo, código gerado, retornos de ferramentas, erros, observações e demais informações de cada step.

Por esse motivo, trabalhar diretamente com os traces completos é pouco prático para análises em larga escala.

O objetivo da mineração foi transformar essa base bruta em uma base menor, focada especificamente nos momentos em que ocorreram erros, mantendo contexto suficiente para responder perguntas como:

* qual erro ocorreu;
* o que o agente estava tentando fazer;
* qual código produziu o erro;
* o que ocorreu imediatamente antes;
* como o agente reagiu depois;
* se aparentemente conseguiu se recuperar;
* quanto o erro e as tentativas seguintes custaram em tokens e tempo;
* quais tipos de erros são recorrentes e potencialmente ensináveis por memória.

A ideia é que esta base seja a principal entrada para o estudo:

```text
erro
 ↓
sintoma
 ↓
mecanismo
 ↓
padrão recorrente
 ↓
unidade de memória
```

---

# 2. Fonte original

A fonte é:

```text
db_corp_juridico_joogle_sor_01.tbnm9100_exeo_aget
```

O schema relevante da tabela original é:

| Campo                     | Tipo   | Descrição                                          |
| ------------------------- | ------ | -------------------------------------------------- |
| `cod_idef_aget`           | int    | Identificador do tipo/agente                       |
| `cod_idef_exeo`           | string | Identificador da execução                          |
| `cod_idef_stat_exeo_aget` | int    | Status da execução                                 |
| `cod_idef_cvsa_asnc`      | string | Identificador da conversa/fluxo associado          |
| `dat_hor_encm_exeo`       | string | Data/hora de encerramento                          |
| `txt_vrvl_locl`           | string | Estado final das variáveis locais do interpretador |
| `txt_rspa_fina`           | string | Resposta final persistida                          |
| `dat_hor_inio_exeo`       | string | Data/hora de início                                |
| `cod_vers_aget`           | int    | Versão do agente                                   |
| `txt_etap_memo`           | string | Trace/memória completa da execução                 |
| `anomesdia`               | int    | Partição da tabela                                 |

O campo fundamental para este estudo é:

```text
txt_etap_memo
```

Ele é armazenado como `VARCHAR`, mas seu conteúdo corresponde, quando válido, a um JSON com estrutura semelhante a:

```json
{
  "managerAgent": [
    {...},
    {...}
  ],
  "ConversationAgent": [
    {...},
    {...}
  ]
}
```

Ou seja:

```text
execução
  ↓
papel/agente
  ↓
lista de steps
```

---

# 3. Estrutura dos steps

Dentro de cada papel podem existir diferentes classes de step.

As principais observadas são:

### `TaskStep`

Representa a tarefa recebida pelo agente.

Exemplo conceitual:

```json
{
  "task": "...",
  "__class__": "TaskStep"
}
```

---

### `PlanningStep`

Representa etapas explícitas de planejamento geradas por alguns agentes.

---

### `ActionStep`

É a unidade principal deste estudo.

É onde ficam informações como:

```text
step_number
model_output
code_action
observations
tool_calls
error
token_usage
timing
is_final_answer
```

É também onde aparecem os erros estruturados reportados pelo framework.

A base minerada considera apenas os **`ActionStep`** para construção da vizinhança de erro.

---

# 4. O que consideramos um erro

Foram criadas duas categorias diferentes.

## 4.1. `STRUCTURED_ERROR`

É o erro explicitamente registrado pelo framework no campo:

```text
error
```

Normalmente:

```json
"error": {
    "type": "AgentExecutionError",
    "message": "..."
}
```

Quando não houve erro estruturado:

```json
"error": null
```

Esse é o conjunto que deve ser utilizado como **fonte oficial para estatísticas da taxonomia de erros**.

Exemplos de `error_type` encontrados na população incluem:

```text
AgentExecutionError
AgentParsingError
AgentMaxStepsError
```

---

## 4.2. `OBSERVATION_SUSPECT`

Durante a análise foi identificado um segundo comportamento.

Existem casos nos quais:

```text
error = null
```

mas o campo:

```text
observations
```

contém sinais claros de falha, por exemplo:

```text
Input validation error
Code execution failed
InterpreterError
ValidationError
Traceback...
```

Esses casos foram marcados como:

```text
OBSERVATION_SUSPECT
```

Eles **não devem ser misturados automaticamente com os erros estruturados nas estatísticas oficiais**.

A ideia é tratá-los como uma trilha paralela de investigação:

```text
STRUCTURED_ERROR
      ↓
erro confirmado pelo harness
      ↓
taxonomia oficial


OBSERVATION_SUSPECT
      ↓
possível falha não registrada formalmente
      ↓
investigação / descoberta
```

Essa distinção é importante.

---

# 5. Por que extraímos contexto ao redor do erro

Analisar apenas:

```text
error.message
```

mostra principalmente **o sintoma técnico**.

Por exemplo:

```text
Could not index ...
```

Porém, para entender o mecanismo do erro e se ele é útil para Cross Memory, é importante observar a trajetória.

Por isso, para cada erro foram recuperados:

```text
n - 1
n
n + 1
n + 2
```

onde:

```text
n     = ActionStep com erro
n-1   = ActionStep imediatamente anterior
n+1   = próxima ação do agente
n+2   = segunda ação posterior
```

Importante: a vizinhança considera apenas **ActionSteps**.

`TaskStep` e `PlanningStep` não entram no `LAG/LEAD`.

---

# 6. Interpretação da janela

## `n - 1`

Ajuda a entender o estado imediatamente anterior ao erro.

Pode mostrar:

* preparação de variáveis;
* retorno de uma ferramenta;
* estratégia anterior;
* premissas utilizadas pelo agente.

---

## `n`

É o próprio step problemático.

Normalmente contém a maior parte da evidência para classificação inicial:

```text
error_type
error_message
code_action
model_output
observations
tool_name
```

---

## `n + 1`

É particularmente importante.

Frequentemente contém:

* autodiagnóstico do agente;
* primeira tentativa de correção;
* mudança de parâmetros;
* inspeção da saída de uma ferramenta;
* repetição do mesmo erro.

---

## `n + 2`

Foi incluído porque alguns agentes não se recuperam imediatamente.

Uma trajetória real pode ser:

```text
step 3 → erro estruturado
step 4 → tentativa de correção, ainda problemática
step 5 → correção efetiva
```

Analisar apenas `n+1` perderia esse comportamento.

---

# 7. Deduplicação

A tabela fonte possui características de snapshot.

A mesma execução pode aparecer em mais de uma partição.

Na análise realizada, foram observados aproximadamente:

```text
148.966 registros
71.882 execuções únicas
```

com:

```text
~2,07 snapshots por execução em média
```

e casos chegando a múltiplos snapshots da mesma execução.

Por isso, antes de abrir os traces, foi realizada deduplicação por:

```text
cod_idef_exeo
+
cod_idef_aget
```

mantendo a melhor representação disponível da execução.

A ordenação considera principalmente:

1. snapshot mais recente;
2. preferência por execução encerrada;
3. maior tamanho de `txt_etap_memo` em caso de empate.

Foi realizado um teste específico para verificar se o snapshot mais recente escolhido possuía trace menor do que alguma versão anterior.

Resultado:

```text
0 execuções
```

Ou seja, no conjunto analisado não foi encontrado indício de que a deduplicação estivesse selecionando traces truncados em relação a snapshots an[teriores]. [o fim da linha 389 está cortado na foto]

---

# 8. JSONs inválidos

Uma pequena quantidade de registros possui `txt_etap_memo` que não pode ser interpretado como JSON estrito.

Foram observados casos de escapes inválidos como:

```text
\@
\*
\:
```

A incidência, entretanto, foi extremamente baixa.

Em aproximadamente:

```text
238.892 traces
```

foram encontrados apenas:

```text
4 JSONs inválidos
```

Por isso não foi criada rotina de reparo automático.

Esses registros são simplesmente descartados durante o parse utilizando `TRY(...)`.

Essa decisão evita introduzir transformações potencialmente incorretas para resolver um problema residual.

---

# 9. Volume da base minerada

Após:

```text
deduplicação
+
parse do trace
+
seleção de ActionSteps
+
identificação dos erros
```

foram observados:

```text
283.925 ActionSteps
```

na população deduplicada.

Desses:

```text
30.141 = erros estruturados
1.280  = observation suspects
```

Total da base minerada:

```text
31.421 linhas
```

Portanto:

```text
STRUCTURED_ERROR ≈ 95,9%
OBSERVATION_SUSPECT ≈ 4,1%
```

A taxa de erro estruturado por ActionStep na população deduplicada ficou próxima de:

```text
30.141 / 283.925
≈ 10,6%
```

---

# 10. Execuções com erro

Os aproximadamente:

```text
31.421 error steps
```

estão distribuídos em:

```text
20.986 execuções únicas
```

Portanto:

```text
~1,50 error steps por execução problemática
```

A distribuição possui uma cauda significativa.

Existem execuções com:

```text
26 erros
21 erros
20 erros
18 erros
16 erros
...
```

Isso é importante porque múltiplos registros de erro podem representar **uma única cascata de falha**, e não fenômenos independentes.

---

# 11. Campos da base minerada

## 11.1. Identificação da execução

### `cod_idef_exeo`

Identificador da execução original.

É a principal chave para fazer drill-down posteriormente na tabela fonte.

---

### `cod_idef_aget`

Identificador do agente na tabela original.

---

### `papel`

Nome do agente/papel dentro de `txt_etap_memo`.

Exemplos:

```text
managerAgent
ConversationAgent
RoteadorCivel
RespostaBacen
CalculoCivel
...
```

Importante: os valores foram mantidos **como persistidos no trace**.

Não foram corrigidos nomes aparentemente inconsistentes ou históricos.

---

### `cod_idef_stat_exeo_aget`

Status original da execução.

Não deve ser utilizado sozinho como indicador de sucesso ou erro.

---

### `cod_idef_cvsa_asnc`

Identificador da conversa ou fluxo associado.

---

### `cod_vers_aget`

Versão do agente.

Campo especialmente útil para verificar se determinados erros:

* aparecem somente em versões antigas;
* surgiram após alguma mudança;
* desapareceram depois de correções.

---

### `dat_hor_inio_exeo`

Data/hora de início da execução.

---

### `dat_hor_encm_exeo`

Data/hora de encerramento da execução.

---

### `mes_execucao`

Derivado de `dat_hor_inio_exeo`.

Facilita análises temporais.

---

### `anomesdia`

Partição da tabela fonte.

**Não assumir que corresponde à data real da execução.**

Para análise temporal do comportamento do agente, preferir:

```text
dat_hor_inio_exeo
```

---

# 12. Indicadores da execução

### `has_final_locals`

Indica se a execução possuía:

```text
txt_vrvl_locl
```

preenchido.

Valores:

```text
1 = presente
0 = ausente
```

---

### `has_persisted_response`

Indica se:

```text
txt_rspa_fina
```

estava preenchido.

---

### `execution_has_final_step`

Indica se, dentro dos ActionSteps daquele papel, foi encontrado algum:

```text
is_final_answer = true
```

É diferente de `has_persisted_response`.

Esses dois sinais podem divergir e não devem ser tratados como equivalentes.

---

# 13. Classificação do registro

### `error_source`

Pode assumir:

```text
STRUCTURED_ERROR
OBSERVATION_SUSPECT
```

---

### `structured_error`

Indicador binário.

```text
1 = error.type estava preenchido
0 = não
```

---

### `observation_suspect`

Indicador binário para casos sem erro estruturado, mas com forte assinatura de erro em `observations`.

---

# 14. Campos do step com erro — `n`

### `step_number`

Número do ActionStep informado pelo próprio trace.

---

### `step_pos`

Posição original dentro da lista de memória.

Este é o campo utilizado para preservar a ordenação da trajetória.

---

### `error_type`

Tipo de erro reportado pelo framework.

Exemplos:

```text
AgentExecutionError
AgentParsingError
AgentMaxStepsError
```

Para `OBSERVATION_SUSPECT`, normalmente será nulo.

---

### `error_message`

Mensagem estruturada do erro.

É uma das principais entradas para a classificação de:

```text
assinatura
família
mecanismo
```

---

### `tool_name`

Nome da primeira ferramenta registrada no step, quando disponível.

Pode ajudar a identificar concentração de erros por ferramenta.

---

### `tool_calls`

Representação dos `tool_calls` do step.

Foi mantida para permitir investigação mais detalhada sem retornar ao trace bruto em todos os casos.

---

### `error_model_output`

Saída do modelo no step que falhou.

Normalmente contém o pensamento/explicação e o código proposto pelo agente.

É importante para investigar **por que o agente tomou determinada decisão**.

---

### `error_code_action`

Código efetivamente executado naquele ActionStep.

É um dos campos mais importantes para identificar o mecanismo do erro.

---

### `error_observations`

Observação produzida pela execução.

Pode conter:

* retorno de ferramenta;
* log de execução;
* mensagem de validação;
* conteúdo retornado;
* detalhes adicionais do erro.

---

### `error_action_output`

Saída registrada especificamente em `action_output`, quando existente.

---

# 15. Tokens e duração do step com erro

### `input_tokens`

Tokens de entrada no step.

---

### `output_tokens`

Tokens de saída.

---

### `total_tokens`

Total de tokens do step.

---

### `duration_seconds`

Duração do ActionStep.

Esses campos permitem medir não apenas frequência, mas também **custo dos erros**.

---

# 16. Contexto anterior — `n - 1`

Campos:

```text
prev_step_number
prev_model_output
prev_code_action
prev_observations
prev_error_type
prev_error_like
```

Eles representam o ActionStep imediatamente anterior ao erro.

### `prev_error_like`

Permite identificar se o erro atual já faz parte de uma sequência problemática.

Por exemplo:

```text
prev_error_like = 1
```

é um forte indício de que o registro pertence a uma cascata.

---

# 17. Primeira ação posterior — `n + 1`

Campos:

```text
next_step_number
next_model_output
next_code_action
next_observations
next_error_type
next_error_message
next_error_like
next_is_final_answer
next_tool_name
next_input_tokens
next_output_tokens
next_total_tokens
next_duration_seconds
```

Este bloco é especialmente importante para estudar **autorrecuperação**.

### `next_model_output`

Pode conter explicitamente frases semelhantes a:

```text
"O erro ocorreu porque..."
"Vou corrigir..."
"A ferramenta retornou..."
"Vou tentar novamente..."
```

Portanto, ele é uma fonte importante para inferir o diagnóstico feito pelo próprio agente.

---

# 18. Segunda ação posterior — `n + 2`

Campos equivalentes:

```text
next2_step_number
next2_model_output
next2_code_action
next2_observations
next2_error_type
next2_error_message
next2_error_like
next2_is_final_answer
next2_tool_name
next2_input_tokens
next2_output_tokens
next2_total_tokens
next2_duration_seconds
```

Serve para capturar recuperações que exigiram mais de uma tentativa.

---

# 19. Métricas agregadas de custo da janela

### `tokens_error_plus_next_action`

```text
tokens(n) + tokens(n+1)
```

---

### `seconds_error_plus_next_action`

```text
tempo(n) + tempo(n+1)
```

---

### `tokens_error_plus_next_2_actions`

```text
tokens(n) + tokens(n+1) + tokens(n+2)
```

---

### `seconds_error_plus_next_2_actions`

```text
tempo(n) + tempo(n+1) + tempo(n+2)
```

Importante:

esses campos são **custos da janela observada**, não necessariamente "custo de recuperação".

Por isso devem ser interpretados como:

```text
erro + ações seguintes
```

e não automaticamente como:

```text
[linhas 955–956 não visíveis; a linha 956 termina em "tokens desperdiçados"]
```

---

# 20. Completude da janela posterior

### `num_actions_after_error_observed`

Quantidade de ActionSteps posteriores disponíveis dentro da janela minerada.

Pode assumir:

```text
0
1
2
```

---

### `has_full_2_action_window`

Indica se foi possível observar os dois ActionSteps seguintes.

```text
1 = n+1 e n+2 existem
0 = janela incompleta
```

Isso deve ser considerado ao comparar custos.

Exemplo:

```text
50 mil tokens em erro+n+1+n+2
```

não deve ser comparado diretamente com:

```text
30 mil tokens em erro+n+1
```

sem saber que o segundo caso simplesmente não possuía `n+2`.

---

# 21. `recovery_signal`

Foi construída uma heurística para indicar o comportamento observado após o erro.

Importante:

> **Esse campo não é uma verdade semântica sobre recuperação.**

Ele é apenas um sinal operacional baseado na presença ou ausência de novos erros e de `final_answer`.

Os valores possíveis incluem:

### `NO_NEXT_ACTION`

Não existe ActionStep posterior.

---

### `RECOVERED_TO_FINAL_NEXT_ACTION`

O próximo ActionStep:

```text
não apresenta erro_like
+
is_final_answer = true
```

É um dos sinais mais fortes de recuperação rápida.

---

### `RECOVERED_TO_FINAL_WITHIN_2_ACTIONS`

`n+1` ainda apresenta erro, mas `n+2` não e chega ao final.

---

### `POSSIBLE_RECOVERY_NEXT_ACTION`

`n+1` não apresenta erro, mas não é possível afirmar apenas com isso que o problema original foi resolvido.

---

### `POSSIBLE_RECOVERY_WITHIN_2_ACTIONS`

`n+1` apresenta erro e `n+2` não.

---

### `ERROR_CASCADE`

Tanto:

```text
n+1
```

quanto:

```text
n+2
```

também apresentam sinal de erro.

É uma indicação forte de cascata.

---

### `UNKNOWN`

Não foi possível encaixar o comportamento nas regras anteriores.

---

# 22. Limitação do `recovery_signal`

Um step sem `error` não significa necessariamente:

```text
problema solucionado
```

Exemplo:

```text
step 3 → erro
step 4 → não gera error formal, mas continua usando premissa errada
step 5 → falha novamente
```

Por isso o `recovery_signal` deve ser utilizado para:

```text
triagem
agrupamento
seleção de casos
```

e não como ground truth de recuperação.

---

# 23. Unidade atual da base

É fundamental manter clara a granularidade:

> **1 linha da base = 1 ActionStep classificado como erro estruturado ou suspeita de erro.**

Portanto:

```text
1 execução
```

pode aparecer diversas vezes.

Isso ocorre quando a mesma trajetória contém vários erros.

Na base atual:

```text
31.421 linhas
20.986 execuções únicas
```

ou aproximadamente:

```text
1,50 error steps por execução problemática
```

---

# 24. Cascata não é necessariamente um novo fenômeno a cada step

Considere:

```text
step 4 → ERROR
step 5 → ERROR
step 6 → ERROR
step 7 → OK
step 8 → FINAL
```

Na base atual existem:

```text
3 linhas
```

uma para cada ActionStep problemático.

Mas, conceitualmente, isso pode representar:

```text
1 episódio de erro
```

Por isso, a próxima transformação recomendada é construir uma unidade de análise chamada:

```text
error_episode
```

---

# 25. Próxima camada recomendada: `error_episode`

A ideia é agrupar erros consecutivos dentro da mesma:

```text
execução + papel
```

Um novo episódio começaria quando:

```text
error_like = 1
```

e o ActionStep anterior não apresentava erro.

Exemplo:

```text
OK
ERROR   ← início do episódio 1
ERROR
ERROR
OK      ← fim do episódio 1
OK
ERROR   ← início do episódio 2
OK      ← fim do episódio 2
```

Essa execução teria:

```text
2 episódios
4 error steps
```

---

# 26. Campos sugeridos para `error_episode`

Uma futura tabela poderia conter:

```text
cod_idef_exeo
papel
episode_id

first_error_step
last_error_step

num_error_steps
num_structured_errors
num_observation_suspects

first_error_type
last_error_type

first_error_message
last_error_message

first_clean_step_after

recovered
reached_final_answer

tokens_error_steps
tokens_until_first_clean
[linhas 1241–1244 não visíveis na foto]
```

Essa granularidade provavelmente será mais adequada para responder perguntas comportamentais sobre o agente.

---

# 27. Como utilizar esta base no estudo de taxonomia

Para a taxonomia, sugere-se partir principalmente dos registros:

```text
error_source = STRUCTURED_ERROR
```

O pipeline conceitual pode permanecer:

```text
error_type
   ↓
assinatura
   ↓
família
   ↓
submecanismo
   ↓
unidade de memória
```

## `error_type`

Classificação ampla produzida pelo framework.

Exemplo:

```text
AgentExecutionError
```

---

## Assinatura

Sintoma técnico presente principalmente em:

```text
error_message
```

Exemplos:

```text
Could not index
variable is not defined
string literal not closed
invalid syntax
```

---

## Família

Agrupamento de assinaturas tecnicamente relacionadas.

Exemplos estudados anteriormente:

```text
Geração de código
Contrato de retorno da ferramenta
Convenção de chamada
Ambiente / sandbox
[linhas 1313–1316 não visíveis na foto]
```

---

## Mecanismo

Explica **o que o agente fez de errado**, e não apenas o erro que o interpretador reportou.

Por exemplo:

```text
sintoma:
Could not index

mecanismo A:
agente tentou indexar um dict por posição

mecanismo B:
agente tentou acessar uma chave que não existe
```

A distinção geralmente depende de analisar conjuntamente:

```text
error_message
+
error_code_action
+
error_observations
```

---

## Unidade de memória

É a lição reutilizável que poderia evitar o erro no futuro.

Exemplo conceitual:

```text
mecanismo:
agente assumiu nome incorreto de chave no retorno da ferramenta

memória:
"Antes de indexar retorno estruturado de ferramenta,
inspecione ou respeite explicitamente seu contrato."
```

---

# 28. Uso dos steps posteriores na taxonomia

Os campos de `n+1` e `n+2` não servem apenas para medir recovery.

Eles também podem fornecer evidência para descobrir o mecanismo.

O agente frequentemente explicita algo como:

```text
"O retorno possui a chave X e não Y."
```

ou:

```text
"O erro ocorreu porque passei uma lista onde a ferramenta esperava um objeto."
```

Ou seja, o próprio agente pode fornecer o diagnóstico do erro na tentativa seguinte.

Campos especialmente úteis:

```text
next_model_output
next_code_action
next_observations
next_error_message
```

e, quando necessário:

```text
next2_*
```

---

# 29. Uso dos tokens

Uma análise relevante para priorização de memória é combinar:

```text
frequência
+
taxa de recuperação
+
custo
```

Um erro muito frequente, mas corrigido imediatamente com pouco custo, pode ter menor prioridade que um erro menos frequente que:

```text
gera cascatas
+
reenvia contexto grande
+
consome muitos tokens
+
impede final_answer
```

Possíveis métricas:

```text
tokens médios por erro
tokens médios até recuperação
número médio de retries
tempo médio adicional
percentual de cascata
percentual de finalização
```

---

# 30. Drill-down para o trace original

A base minerada foi propositalmente reduzida.

Campos gigantes como:

```text
txt_etap_memo completo
txt_vrvl_locl completo
txt_rspa_fina completo
model_input_messages
```

não foram carregados integralmente.

Quando um caso precisar de investigação aprofundada, utilizar:

```text
cod_idef_exeo
```

para recuperar o trace original.

Isso permite manter a base de estudo relativamente pequena sem perder auditabilidade.

---

# 31. `txt_vrvl_locl`

O campo original:

```text
txt_vrvl_locl
```

é especialmente útil quando é necessário entender o **estado real das variáveis** após a execução.

Por exemplo:

```python
retorno = {
    "vazamento_sigilo": "NAO"
}
```

enquanto o agente tentou:

```python
retorno["quebra_sigilo"]
```

O trace permite ver o erro.

O `txt_vrvl_locl` pode ajudar a confirmar o contrato real armazenado em memória.

Por ser potencialmente muito grande, ele não foi replicado em cada linha da base minerada.

---

# 32. Cuidados importantes

## 32.1. Não tratar cada linha como erro independente

Erros consecutivos podem fazer parte da mesma cascata.

---

## 32.2. Não misturar `OBSERVATION_SUSPECT` com erro confirmado

Para métricas oficiais, utilizar prioritariamente:

```text
structured_error = 1
```

---

## 32.3. Não considerar `recovery_signal` como ground truth

Ele é uma heurística.

---

## 32.4. Não utilizar `anomesdia` como data do comportamento do agente

Preferir:

```text
dat_hor_inio_exeo
```

---

## 32.5. Considerar versão do agente

Um erro histórico pode já ter sido eliminado.

Sempre que possível, analisar:

```text
cod_vers_aget
+
data da execução
```

---

## 32.6. Preservar nomes originais

Os nomes de `papel` foram mantidos conforme persistidos.

Não corrigir silenciosamente nomes históricos ou aparentemente errados antes de entender sua origem.

---

## 32.7. PII

Os traces e observações podem conter informações de clientes.

A base minerada deve seguir as mesmas restrições de segurança e tratamento aplicáveis à base original.

---

# 33. Perguntas que esta base permite responder

A partir desta extração, o estudo pode avançar para perguntas como:

### Frequência

```text
Quais erros mais acontecem?
```

### Concentração

```text
Quais agentes concentram mais erros?
```

### Taxa

```text
Qual percentual dos ActionSteps de cada agente falha?
```

### Recorrência

```text
O mesmo mecanismo ocorre em múltiplas execuções e meses?
```

### Recovery

```text
Quais erros o agente normalmente consegue corrigir sozinho?
```

### Cascata

```text
Quais erros tendem a gerar novos erros?
```

### Custo

```text
Quais tipos de erro consomem mais tokens e tempo?
```

### Evolução

```text
O erro continua existindo nas versões recentes?
```

### Memória

```text
Existe uma lição genérica, estável e reutilizável que evitaria o erro?
```

---

# 34. Critério conceitual para Cross Memory

Nem todo erro deve gerar memória.

Uma boa unidade de memória deve preferencialmente ser:

* recorrente;
* explicável;
* suficientemente geral;
* reutilizável em múltiplas execuções;
* ainda relevante em versões atuais;
* evitável por instrução ou conhecimento;
* não simplesmente falha transitória de infraestrutura.

Exemplos de eventos que provavelmente **não** justificam memória:

```text
timeout eventual
indisponibilidade temporária
falha upstream
erro isolado sem padrão
```

Já erros como:

```text
interpretar incorretamente contrato de ferramenta
usar argumento com convenção errada
acessar chave inexistente
repetir variável de step que falhou
```

podem representar conhecimento ensinável.

---

# 35. Fluxo recomendado de análise

```text
error_steps_context
        |
        ▼
análise exploratória
        |
        ├── frequência
        ├── agentes
        ├── versões
        ├── temporalidade
        ├── tokens
        └── cascatas
        |
        ▼
STRUCTURED_ERROR
        |
        ▼
error_type
        |
        ▼
assinatura
        |
        ▼
família
        |
        ▼
mecanismo
        |
        ▼
error_episode
        |
        ▼
recorrência + recovery + custo
        |
        ▼
candidata a memória?
        |
        ├── sim → Cross Memory
        ├── não → harness / código / ferramenta
        └── fora → infraestrutura / evento eventual
```

---

# 36. Resumo

A base minerada foi criada para substituir a necessidade de manipular traces completos durante a maior parte do estudo.

Ela transforma:

```text
execuções gigantes em JSON
```

em uma coleção estruturada de:

```text
erro
+
contexto anterior
+
duas ações posteriores
+
tokens
+
tempo
+
sinal de recuperação
```

A população atual contém aproximadamente:

```text
283.925 ActionSteps analisados

30.141 erros estruturados
1.280 suspeitas adicionais

31.421 registros minerados

20.986 execuções com pelo menos um registro de erro/suspeita
```

A unidade atual é o **ActionStep problemático**.

A evolução natural é criar uma segunda camada de **episódios de erro**, agrupando erros consecutivos e permitindo estudar melhor:

```text
falha
→ reação
→ tentativa
→ recuperação ou cascata
```

Essa camada deverá aproximar ainda mais a análise técnica dos erros do objetivo central do Cross Memory: identificar **conhecimento recorrente que, se disponibilizado ao agente, pode evitar que o mesmo padrão de falha volte a acontecer**.
