# Relatório independente — 11.1_origem_do_erro

Data: 2026-09-17

## Escopo

Este relatório audita independentemente a pasta `11.1_origem_do_erro/` por leitura direta dos arquivos `crus/*.json`, usando `casos.csv` apenas como índice da amostra. O objetivo é verificar se a **função de origem atribuída** a cada erro das unidades nº2 e nº10 se sustenta quando o caso é reaberto no trace cru.

Guidance consultado para interpretar a análise:

- `docs/`06-racionais-mineracao-unidades-n2-n10.md` §9;
- `docs/03-procedimento-validacao.md` §1.7;
- `docs/`07-relatorio-mineracao-unidades-n2-n10.md` §6.1.

## Resumo executivo

1. A pasta contém **12 casos**: todos os erros fora da função dominante das unidades e o primeiro caso de cada `via` da função dominante.
2. Dos 12 casos, **7 trazem atribuição positiva** de origem (`get_available_documents`, `validar_quebra_sigilo`, `extrair_evidencias`, `meta_map`) e **5 foram marcados como `não resolvido`**.
3. Na leitura independente do cru, os **7 casos com atribuição positiva conferem** com o código e a trajetória do papel.
4. Nos **5 casos `não resolvido`**, não encontrei no cru evidência forte o bastante para derrubar a cautela do notebook; em todos, a não-atribuição continua defensável.
5. Assim, **não apareceu nenhum caso desta pasta que contradiga a atribuição publicada**. O padrão geral se sustenta: a dominante permanece dominante, e os casos fora dela continuam corretamente separados entre atribuição positiva e não-resolvidos.

## Corpus auditado

Fonte: `casos.csv`.

| contagem | valor |
|---|---:|
| casos totais | 12 |
| `não resolvido` | 5 |
| `get_available_documents` | 3 |
| `validar_quebra_sigilo` | 2 |
| `extrair_evidencias` | 1 |
| `meta_map` | 1 |

Distribuição das vias na amostra:

| via | n |
|---|---:|
| `variável sem origem rastreável` | 3 |
| `em step anterior` | 3 |
| `no mesmo step` | 2 |
| `nó pedido não achado no comando` | 2 |
| `no próprio comando` | 2 |

## Método

Para cada caso, a checagem independente abriu o `ActionStep` alvo (`idx` do `casos.csv`) e, quando necessário, o step imediatamente anterior e o seguinte, observando:

- o código executado no step do erro;
- a mensagem de erro (`error.message`);
- se a variável indexada era produzida pela própria ferramenta no mesmo step, num step anterior ou numa função auxiliar definida pelo agente;
- se havia reatribuição de variável, mudança de nível do objeto ou erro intermediário que justificasse manter o caso como `não resolvido`.

## Resultado por caso

| exec_id | role / idx | atribuição do notebook | leitura no cru | veredito independente |
|---|---|---|---|---|
| `781ae3dc…` | ConversationAgent / 2 | `não resolvido` | o step anterior erra em `docs_resp[0][0]`; o step alvo já usa `docs_resp["result"][0][0]` e quebra depois, dentro de helper/lambda, com `Object hashDocumento has no attribute get`; há reinterpretação do objeto no meio do caminho | **mantém `não resolvido`** |
| `915e77a7…` | ConversationAgent / 2 | `não resolvido` | o passo anterior tenta reconstruir `docs_raw` e falha em `SyntaxError`; o step alvo erra ao indexar colunas de `Empty DataFrame`; a mensagem já não carrega o objeto original | **mantém `não resolvido`** |
| `95344639…` | RespostaBacen / 0 | `extrair_evidencias` / `no mesmo step` | no mesmo step o agente faz `info_evidencias = extrair_evidencias(...)` e depois tenta `info_evidencias["informacoes_evidencias"]`, mas o retorno real traz `dados_evidencias` | **confere** |
| `975b12fd…` | ConversationAgent / 2 | `não resolvido` | o step anterior erra em `docs[0][0]`; o step alvo já reatribui `docs_result = docs['result']`, mas o erro relevante ocorre mais adiante num laço/seleção sem nó inequívoco para rastrear a origem pedida | **mantém `não resolvido`** |
| `b63284df…` | ConversationAgent / 1 | `get_available_documents` / `em step anterior` | o step anterior cria `docs = get_available_documents(...)`; o step alvo itera `docs['result'][0]` e tenta ler `doc['metadado'][0]['nom_docm_juri_mode']` num item cujo schema é `{nomeMetadado, valorMetadado}` | **confere** |
| `cd794f02…` | ConversationAgent / 2 | `meta_map` / `no próprio comando` | o helper `meta_map(doc)` é definido e chamado no próprio comando; o erro `Object hashDocumento has no attribute get` nasce exatamente dentro desse helper, quando o agente já está no nível errado do objeto | **confere** |
| `df4aac6a…` | ConversationAgent / 1 | `não resolvido` | o step alvo reatribui `doc_list = docs['result'][0][0]` e depois quebra ao iterar `doc_list`; o erro efetivo (`Object hashDocumento has no attribute get`) aparece dentro do helper `get_meta`, já depois da mudança de nível | **mantém `não resolvido`** |
| `e6d85e40…` | ConversationAgent / 2 | `não resolvido` | o step anterior erra em `docs[0][0]`; o step alvo muda para `docs_result = docs.get('result')` e volta a quebrar depois, em função auxiliar sobre objeto já reatribuído | **mantém `não resolvido`** |
| `1eed2931…` | ConversationAgent / 1 | `get_available_documents` / `em step anterior` | o step 0 chama `get_available_documents(...)` e imprime `documentos`; o step alvo tenta `for doc in documentos[0]` e a mensagem mostra `Could not index {'result': ...} with '0'` | **confere** |
| `79b2ed7a…` | ConversationAgent / 7 | `get_available_documents` / `no próprio comando` | a própria linha que falha é `get_available_documents(...)[0]`; a origem do objeto indexado está inline no comando | **confere** |
| `d3d64194…` | RespostaBacen / 1 | `validar_quebra_sigilo` / `no mesmo step` | o mesmo comando chama `quebra = validar_quebra_sigilo(...)` e depois monta o JSON final com `quebra["quebra_sigilo"]` | **confere** |
| `69ab8e81…` | RespostaBacen / 3 | `validar_quebra_sigilo` / `em step anterior` | `quebra_obj` já vinha de step anterior; no step alvo o agente monta `final_json` com `quebra_obj["quebra_sigilo"]`; apesar de haver erro paralelo com assunto em `resposta_orgao_regulador`, a origem da variável indexada segue sendo `validar_quebra_sigilo` | **confere** |

## Achados principais

### 1. Os casos com atribuição positiva se sustentam no cru

Os 7 casos com ferramenta/função atribuída pelo notebook permanecem plausíveis quando o fluxo é reaberto diretamente no cru:

- **`get_available_documents`**: confirmado em três casos, dois por variável criada em step anterior e um inline no próprio comando;
- **`validar_quebra_sigilo`**: confirmado em dois casos, um no mesmo step e um em step anterior;
- **`extrair_evidencias`**: confirmado no caso `95344639…`, em que a variável produzida pela tool é imediatamente indexada com a chave errada;
- **`meta_map`**: confirmado no caso `cd794f02…`, em que o acesso que falha está de fato encapsulado na função auxiliar definida pelo agente.

### 2. Os cinco `não resolvido` continuam sendo uma escolha conservadora correta

Nos cinco casos marcados como `não resolvido`, a leitura do cru não mostrou base forte para forçar uma atribuição mais específica sem aumentar o risco de erro.

Os padrões recorrentes são:

- reatribuição de variável entre um step e outro;
- helper/lambda falhando depois de o agente já ter mudado de nível no objeto;
- erro que já não imprime o objeto original (`SyntaxError`, `Empty DataFrame`, `Object hashDocumento has no attribute get`).

Nesses casos, o rótulo `não resolvido` não parece falha do método; parece **medida de cautela metodológica**.

### 3. Nada nesta pasta derruba a leitura agregada do Passo 1

A função dominante das duas unidades não é enfraquecida por nenhum caso reaberto aqui. Pelo contrário:

- os casos exemplares da dominante conferem;
- os casos fora da dominante continuam fora dela por razões compreensíveis;
- os não-resolvidos permanecem não-resolvidos por boa razão, e não por falta óbvia de leitura do cru.

## Conclusões finais

1. A pasta `11.1_origem_do_erro/` sustenta bem a alegação de que o Passo 1 atribui corretamente a origem dos erros **quando ela é rastreável**.
2. Nos casos em que a origem não é rastreável com segurança a partir do comando/erro efetivo, o notebook foi conservador e marcou `não resolvido`; a auditoria independente não encontrou motivo claro para reclassificá-los.
3. O balanço independente desta pasta é, portanto:
   - **7/7 atribuições positivas conferidas**;
   - **5/5 não-resolvidos mantidos como cautela legítima**.
4. Não encontrei, nesta amostra de 12 casos, evidência que exija rever a conclusão publicada para o Passo 1.
