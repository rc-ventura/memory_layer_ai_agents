<!--
TRANSCRIÇÃO PARCIAL das fotos do guia `relatorio_mineracao_20260929.md` (máquina 2, `…/third/docs/`), feita em 09/10/2026.
É o guia que acompanha a base minerada de erros e a query `ICTI_crossmemory_query_mineracao_erros`.
Não é a documentação atual da base 3 (essa está em `../`).

O QUE ESTÁ AQUI: só as linhas 909 a 1755 do guia (seções 19 a 36), as únicas fotos que carregaram na leitura
(IMG_5337 a IMG_5364 da pasta `relatorio_query_mineracao`). Texto fiel ao das fotos.
O QUE NÃO ESTÁ: as linhas 1 a ~908 (seções 1 a 18: objetivo, fonte, estrutura dos steps, definição de erro, janela,
deduplicação, schema das colunas etc.) — as fotos IMG_5307 a IMG_5336 não carregaram. A query SQL também não foi
transcrita (pasta `query_mineracao`, 31 fotos, e `query-371-373`, 1 foto: nenhuma carregou).
Marcas: `[linhas N–M não visíveis na foto]` onde o corte da foto impediu a leitura.
-->

# Guia da Base Minerada de Erros dos Agentes — transcrição parcial (seções 19 a 36)

[linhas 1–908 não transcritas: fotos não carregaram]

# 19. Métricas agregadas de custo da janela

### `tokens_error_plus_next_action`

[linhas 914–918 não visíveis na foto]

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
