# Relatório independente — amostra 11.7 (Passo 6)

Data: 2026-09-17

## Escopo

Este relatório foi produzido por leitura direta dos arquivos `crus/*.json` da pasta `11.7_amostra_passo6/`, usando `casos.csv` apenas como índice da amostra. Para o caso `9be7b413… / RespostaBacen`, também foi usado `pipeline/drill_down.py caso` para reconstituir a trajetória completa do papel.

Objetivos desta checagem independente:

1. verificar se, nos 10 casos da amostra, o schema sugerido pelo prompt/contexto coincide ou não com o campo lido pelo agente e com o retorno real da tool;
2. avaliar se, em `validar_quebra_sigilo`, o erro parece alucinação do agente ou conflito entre contrato declarado e retorno real da ferramenta;
3. incluir a checagem do erro de `draft_resposta`/assunto inválido e verificar se ele aparece ou não nos mesmos 10 exemplares.

## Resumo executivo

1. A amostra contém 10 casos: 5 de `U_contrato_dict` com `get_available_documents` e 5 de `U_campo_inexistente` com `validar_quebra_sigilo`.
2. Nos 5 casos de `validar_quebra_sigilo`, o padrão é consistente: o prompt declara um output no formato `{"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}`, mas o retorno real observado no cru vem como `{"vazamento_sigilo": "NAO", "justificativa": ...}`.
3. Portanto, nesses 5 casos, o erro parece decorrer primariamente de **mismatch entre o contrato declarado no prompt e o retorno real da tool**, e não de alucinação livre do agente.
4. Em 4 desses 5 casos, o agente depois corrige e passa a usar `vazamento_sigilo`; no quinto (`21a4fa6c…`) a execução quebra antes de aparecer o step de correção.
5. O erro de `draft_resposta`/assunto inválido **não** é recorrente nos 10 exemplares: ele aparece em **1/10** caso, `9be7b413…`, e não foi encontrado nos outros 9.
6. Nos 5 casos de `get_available_documents`, o problema é diferente: o prompt não especifica um schema concreto de saída, e o agente assume uma estrutura errada (`docs[0]`, `docs["result"][0][0]` etc.). Aqui há subespecificação do contrato e uso incorreto pelo agente, mas não evidência de um schema explícito errado no prompt.

## Corpus auditado

Fonte da amostra: `casos.csv`.

| exec_id | role | idx | unidade | ferramenta |
|---|---|---:|---|---|
| 3f44a68b-c304-eebb-6be1-ad14fa611ee4 | ConversationAgent | 2 | U_contrato_dict | get_available_documents |
| 99ab53e8-d616-5a6f-5f8a-3ce6630cf7b7 | ConversationAgent | 1 | U_contrato_dict | get_available_documents |
| 05a8fe50-3abe-d403-9163-4ac9aa69efdb | ConversationAgent | 1 | U_contrato_dict | get_available_documents |
| cbc5d62d-6ad6-3cb8-bd15-cacc335dc588 | ConversationAgent | 1 | U_contrato_dict | get_available_documents |
| c8627731-e09c-9373-f184-0c91f8e11bd1 | ConversationAgent | 1 | U_contrato_dict | get_available_documents |
| 1be966e7-72d9-4e40-ab15-7c5ade91d430 | RespostaBacen | 6 | U_campo_inexistente | validar_quebra_sigilo |
| d3d64194-ca05-4c53-9041-f398fb723baf | RespostaBacen | 1 | U_campo_inexistente | validar_quebra_sigilo |
| 9be7b413-a0bf-4300-bcfc-8e55c1c143a1 | RespostaBacen | 5 | U_campo_inexistente | validar_quebra_sigilo |
| 8dd410c8-f7d2-4a5d-930b-0d02c376f4b3 | RespostaBacen | 1 | U_campo_inexistente | validar_quebra_sigilo |
| 21a4fa6c-0421-429c-8824-e668bdef11eb | RespostaBacen | 2 | U_campo_inexistente | validar_quebra_sigilo |

## Método resumido

- leitura direta de cada `crus/<exec_id>.json`;
- identificação, no `ActionStep` alvo (`idx` do `casos.csv`), de:
  - bloco de declaração da ferramenta no `model_input_messages[0].content[0].text`;
  - campo efetivamente indexado no `code_action`;
  - objeto efetivamente retornado, quando visível em `observations` e/ou em `error.message`;
- varredura dos `ActionStep` de cada um dos 10 casos atrás de ocorrência de:
  - `Error calling tool 'draft_resposta'`;
  - `Assunto não previsto`.

## Resultado por caso

| exec_id | ferramenta | prompt / contrato observado | o agente leu / assumiu | retorno / erro observado no cru | erro de draft no mesmo caso? | leitura independente |
|---|---|---|---|---|---|---|
| 3f44a68b | get_available_documents | prompt sem schema concreto de saída | `docs["result"][0][0]`, depois iteração como se fosse lista de documentos | `Object hashDocumento has no attribute get` | não | erro de navegação/nível do objeto |
| 99ab53e8 | get_available_documents | prompt sem schema concreto de saída | `docs[0]` | `Could not index {'result': [[...]]}` | não | agente assumiu estrutura não declarada |
| 05a8fe50 | get_available_documents | prompt sem schema concreto de saída | `for doc in docs[0]` | `Could not index {'result': [[...]]}` | não | agente assumiu estrutura não declarada |
| cbc5d62d | get_available_documents | prompt sem schema concreto de saída | `for d in docs[0]` | `Could not index {'result': [[...]]}` | não | agente assumiu estrutura não declarada |
| c8627731 | get_available_documents | prompt sem schema concreto de saída | `for doc in docs[0]` | `Could not index {'result': [[...]]}` | não | agente assumiu estrutura não declarada |
| 1be966e7 | validar_quebra_sigilo | prompt declara `quebra_sigilo` + `motivo` | `quebra["quebra_sigilo"]` | retorno real contém `vazamento_sigilo` + `justificativa` | não | mismatch prompt ↔ tool; agente segue prompt |
| d3d64194 | validar_quebra_sigilo | prompt declara `quebra_sigilo` + `motivo` | `quebra["quebra_sigilo"]` | retorno real contém `vazamento_sigilo` + `justificativa` | não | mismatch prompt ↔ tool; agente segue prompt |
| 9be7b413 | validar_quebra_sigilo | prompt declara `quebra_sigilo` + `motivo` | `valid_quebra["quebra_sigilo"]` | retorno real contém `vazamento_sigilo` + `justificativa` | sim | mismatch prompt ↔ tool; com erro anterior de assunto inválido na mesma execução |
| 8dd410c8 | validar_quebra_sigilo | prompt declara `quebra_sigilo` + `motivo` | `quebra["quebra_sigilo"]` | retorno real contém `vazamento_sigilo` + `justificativa` | não | mismatch prompt ↔ tool; agente segue prompt |
| 21a4fa6c | validar_quebra_sigilo | prompt declara `quebra_sigilo` + `motivo` | `validacao_sigilo["quebra_sigilo"]` | retorno real contém `vazamento_sigilo` + `justificativa` | não | mismatch prompt ↔ tool; quebra já no `if` |

## Achado A — `validar_quebra_sigilo`: o contrato declarado não bate com o retorno real

### A.1. O que o prompt declara

Nos 5 casos de `validar_quebra_sigilo`, a declaração extraída do campo de system prompt é a mesma. A checagem por script encontrou o mesmo bloco em todos os cinco crus; os blocos extraídos são idênticos.

O contrato declarado é:

```python
def validar_quebra_sigilo(reclamacao: string, evidencias: array, resposta: string) -> object:
    ...
    Outputs:
        json com a validação de quebra de sigilo no formato:
        {"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}
```

### A.2. O que o agente faz

Nos 5 casos auditados, o agente usa a chave coerente com esse contrato declarado:

- `quebra["quebra_sigilo"]` (`1be966e7…`, `d3d64194…`, `8dd410c8…`);
- `valid_quebra["quebra_sigilo"]` (`9be7b413…`);
- `validacao_sigilo["quebra_sigilo"]` (`21a4fa6c…`, inclusive dentro de um `if`).

Isto sugere que, nesse grupo de casos, o agente está seguindo o schema que lhe foi apresentado.

### A.3. O que a tool realmente devolve

Nos 5 casos, o objeto explicitado pelo próprio runtime contém as chaves:

```json
{"vazamento_sigilo": "NAO", "justificativa": "..."}
```

Não aparece `quebra_sigilo`; tampouco aparece `motivo`.

### A.4. Interpretação

A divergência não é só em uma chave; é em duas:

- prompt: `quebra_sigilo` / `motivo`
- retorno real: `vazamento_sigilo` / `justificativa`

Assim, a leitura mais parcimoniosa para esta subamostra é:

1. o prompt declara um contrato A;
2. a tool devolve um contrato B;
3. o agente inicialmente segue A;
4. a execução quebra quando tenta indexar uma chave que não existe no retorno real.

Ou seja: **o erro parece ser primariamente de contrato inconsistente prompt ↔ tool**, não de invenção arbitrária do agente.

### A.5. Evidência forte de que o agente estava reagindo ao runtime, não alucinando

No caso `9be7b413…`, após o erro, o passo seguinte muda explicitamente para:

```python
"quebra_sigilo": valid_quebra["vazamento_sigilo"]
```

Isso reforça a leitura de que o agente primeiro acreditou no contrato do prompt e só depois se adaptou ao retorno real observado.

No `21a4fa6c…`, a execução quebra antes de chegar ao passo de correção porque a indexação errada já ocorre na condição `if validacao_sigilo["quebra_sigilo"] == "NÃO":`.

## Achado B — erro de `draft_resposta` / assunto inválido nos 10 casos

### B.1. Resultado da varredura

Foi feita uma varredura pelos 10 casos, procurando as strings:

- `Error calling tool 'draft_resposta'`
- `Assunto não previsto`

Resultado:

- presença em **1/10** caso: `9be7b413…`;
- ausência em **9/10** casos.

### B.2. O que ocorre em `9be7b413…`

Esse caso tem um encadeamento de erros anterior ao `validar_quebra_sigilo`:

1. primeiro, o agente chama `extrair_evidencias` com `assunto="dcr-discorda_de_juros"`, e a tool rejeita porque só aceita `discorda_juros` / `discorda_debito` etc.;
2. depois, mais adiante, o agente chama `draft_resposta` também com `assunto="dcr-discorda_de_juros"`, produzindo novo `Assunto não previsto`;
3. só depois de corrigir o assunto para `discorda_juros` o fluxo anda e chega ao erro de `validar_quebra_sigilo`.

Portanto, neste caso específico há **dois problemas diferentes na mesma execução**:

- um erro anterior de sincronização do nome do assunto (`dcr-discorda_de_juros` vs `discorda_juros`);
- um erro posterior de schema em `validar_quebra_sigilo`.

### B.3. Interpretação

O erro de `draft_resposta` não explica os outros 9 casos da amostra. Ele é um fenômeno local a `9be7b413…`, enquanto o mismatch de `validar_quebra_sigilo` aparece sistematicamente nos 5 casos dessa ferramenta.

Em outras palavras:

- **erro de draft**: contingente, 1/10 na amostra;
- **mismatch `validar_quebra_sigilo`**: estrutural dentro dos 5/5 casos dessa subunidade.

## Achado C — `get_available_documents` é outro tipo de problema

Nos 5 casos de `U_contrato_dict`, não há evidência de que o prompt tenha explicitamente mandado usar um schema errado. O bloco da tool descreve a finalidade da função e os argumentos, mas não fixa uma estrutura concreta de saída equivalente ao que ocorre em `validar_quebra_sigilo`.

Assim, a leitura independente para esses 5 casos é diferente:

- o contrato de saída está subespecificado;
- o agente assume um nível de indexação que não foi estabelecido de forma inequívoca;
- o runtime mostra retorno com chave `result` em vários casos, e o agente tenta acessar `docs[0]` ou itera o nível errado.

Portanto, aqui eu não atribuiria o erro ao mesmo mecanismo de `validar_quebra_sigilo`. O problema parece mais próximo de **schema de saída pouco especificado + suposição errada do agente**.

## Conclusões finais

1. A hipótese de que `validar_quebra_sigilo` instrui o agente para um schema diferente do que a tool realmente devolve está **fortemente sustentada** pelos crus desta amostra.
2. Nos 5/5 casos de `validar_quebra_sigilo`, o agente inicialmente lê `quebra_sigilo` porque o prompt declara esse campo; o retorno real, porém, traz `vazamento_sigilo`.
3. Assim, para esta subamostra, a explicação mais forte é **conflito de contrato prompt ↔ tool**, não simples alucinação.
4. O erro de `draft_resposta`/assunto inválido aparece em apenas 1/10 caso (`9be7b413…`) e não deve ser generalizado para os outros nove.
5. Os 5 casos de `get_available_documents` pertencem a outro padrão: não mostram um schema explicitamente errado no prompt, mas sim uma saída pouco especificada e navegação incorreta do objeto pelo agente.

## Anexo — referências rápidas no cru

### Caso `9be7b413…`

- erro de `extrair_evidencias` com assunto `dcr-discorda_de_juros`: `crus/9be7b413-a0bf-4300-bcfc-8e55c1c143a1.json`, linhas 1079–1103;
- erro de `draft_resposta` / assunto inválido: mesmo arquivo, linhas 1218–1235;
- erro de chave inexistente em `validar_quebra_sigilo`: mesmo arquivo, linhas 1277–1283;
- correção posterior para `vazamento_sigilo`: mesmo arquivo, linhas 1628–1641.

### Caso `21a4fa6c…`

- quebra já na condição `if validacao_sigilo["quebra_sigilo"] == "NÃO":` com retorno real contendo `vazamento_sigilo`: `crus/21a4fa6c-0421-429c-8824-e668bdef11eb.json`, linhas 454–466.

### Caso `99ab53e8…`

- tentativa de usar `docs[0]` apesar do retorno com chave `result`: `crus/99ab53e8-d616-5a6f-5f8a-3ce6630cf7b7.json`, linhas 419–425.
